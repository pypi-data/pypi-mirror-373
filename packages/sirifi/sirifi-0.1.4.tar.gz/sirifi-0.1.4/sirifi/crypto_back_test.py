from binance.client import Client
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from itertools import product
import requests
import time


class Sirifi_C_Backtester:
    def __init__(self, symbol: str, intervals=None, days: int = 30,
                 fee: float = 0.001, slippage_pct: float = 0.0005):
        """
        symbol: trading pair symbol like 'BTCUSDC'
        intervals: list of intervals to test e.g. ['5m','15m','1h','4h']
        days: how many days of historical data to fetch
        fee: trading fee percentage (e.g. 0.001 for 0.1%)
        slippage_pct: slippage percentage on entry/exit prices
        """
        if intervals is None:
            intervals = ['15m', '1h', '4h']

        assert isinstance(symbol, str) and symbol.endswith("USDC"), "Symbol must be a valid USDC pair string"
        assert all(i in ['1m','3m','5m','15m','30m','1h','2h','4h','6h','8h','12h','1d'] for i in intervals), \
            "Intervals must be valid Binance intervals"
        assert days > 0, "Days must be positive"
        assert 0 <= fee <= 0.01, "Fee must be small float (0 <= fee <= 0.01)"
        assert 0 <= slippage_pct <= 0.01, "Slippage must be small float (0 <= slippage_pct <= 0.01)"

        self.symbol = symbol  # Trading symbol like BTCUSDC
        self.intervals = intervals  # List of intervals to optimize over
        self.days = days  # Historical days to fetch
        self.fee = fee  # Trading fee per trade (fraction)
        self.slippage_pct = slippage_pct  # Slippage fraction applied to entry/exit

        self.client = Client()  # Binance Client instance
        self.best_result = None
        self.best_interval = None
        self.best_result_df = None

    def _fetch_data(self, interval):
        # Fetch historical klines for symbol and interval
        start_time = (datetime.utcnow() - timedelta(days=self.days)).strftime('%d %b %Y %H:%M:%S')
        klines = self.client.get_historical_klines(self.symbol, interval, start_time)
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base', 'taker_buy_quote', 'ignore'
        ])
        df = df[['timestamp', 'open', 'high', 'low', 'close']]
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        for col in ['open', 'high', 'low', 'close']:
            df[col] = df[col].astype(float)
        df['Returns'] = df['close'].pct_change()
        return df.dropna()

    def _compute_indicators(self, df, fast, slow, signal, rsi_period):
        # MACD calculation: difference of fast and slow EMA of close price
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()

        # RSI calculation: relative strength index over rsi_period
        delta = df['close'].diff()
        gain = delta.clip(lower=0).rolling(window=rsi_period).mean()
        loss = -delta.clip(upper=0).rolling(window=rsi_period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        df['MACD'] = macd
        df['Signal'] = signal_line
        df['RSI'] = rsi
        return df.dropna()

    def _apply_strategy(self, df, rsi_oversold, rsi_overbought, stop_loss_pct, take_profit_pct):
        position = 0
        entry_price = 0
        returns = []

        for i in range(1, len(df)):
            price = df['close'].iloc[i]
            prev_price = df['close'].iloc[i - 1]
            macd_val = df['MACD'].iloc[i]
            signal_val = df['Signal'].iloc[i]
            rsi_val = df['RSI'].iloc[i]

            ret = 0

            if position == 0:
                # Entry condition: MACD crosses above signal and RSI below oversold threshold
                if macd_val > signal_val and rsi_val < rsi_oversold:
                    position = 1
                    entry_price = price * (1 + self.slippage_pct)  # account for slippage on entry
                    ret -= self.fee  # pay trading fee
            elif position == 1:
                # Calculate profit/loss
                pl = (price - entry_price) / entry_price

                # Exit conditions: stop loss or take profit reached
                if pl <= -stop_loss_pct or pl >= take_profit_pct:
                    exit_price = price * (1 - self.slippage_pct)  # slippage on exit
                    trade_return = (exit_price - entry_price) / entry_price
                    trade_return -= self.fee  # pay fee on exit
                    ret += trade_return
                    position = 0
                    entry_price = 0
                else:
                    # Hold position: accumulate return from price movement
                    ret += (price - prev_price) / prev_price

            returns.append(ret)

        df = df.iloc[1:].copy()
        df['Strategy_Returns'] = returns
        df['Cumulative'] = (1 + df['Strategy_Returns']).cumprod()

        total_return = df['Cumulative'].iloc[-1] - 1
        max_drawdown = (df['Cumulative'] / df['Cumulative'].cummax() - 1).min()
        std = df['Strategy_Returns'].std()
        sharpe = df['Strategy_Returns'].mean() / std * np.sqrt(24 * 365) if std > 0 else np.nan  # annualized Sharpe
        trades = (df['Strategy_Returns'] != 0).sum()
        buy_hold_return = df['close'].iloc[-1] / df['close'].iloc[0] - 1

        metrics = {
            'Total Return': total_return,
            'Max Drawdown': max_drawdown,
            'Sharpe Ratio': sharpe,
            'Buy & Hold Return': buy_hold_return,
            'Trades': trades
        }

        return metrics, df

    def _optimize(self):
        # Parameter ranges with some wider range for thorough search
        fast_vals = [8, 12, 16, 20]         # Short-term EMA
        slow_vals = [26, 35, 50]            # Long-term EMA
        signal_vals = [6, 9, 12]            # Signal line EMA
        rsi_periods = [10, 14, 20]          # RSI lookback period
        rsi_oversold_vals = [25, 30, 35]    # Buy threshold
        rsi_overbought_vals = [60, 65, 70]  # Sell threshold (not used in MACD logic here)
        stop_loss_vals = [0.01, 0.02, 0.03] # Stop-loss % per trade
        take_profit_vals = [0.03, 0.05, 0.07] # Take-profit % per trade

        best_result = None
        best_df = None
        best_sharpe = -np.inf
        best_interval = None

        for interval in self.intervals:
            try:
                df_raw = self._fetch_data(interval)
            except Exception as e:
                print(f"Error fetching data for {self.symbol} interval {interval}: {e}")
                continue

            # Iterate all parameter combinations
            for params in product(fast_vals, slow_vals, signal_vals, rsi_periods,
                                  rsi_oversold_vals, rsi_overbought_vals,
                                  stop_loss_vals, take_profit_vals):
                fast, slow, signal, rsi_p, rsi_oversold, rsi_overbought, sl, tp = params
                if fast >= slow or rsi_oversold >= rsi_overbought:
                    continue
                try:
                    df = self._compute_indicators(df_raw.copy(), fast, slow, signal, rsi_p)
                    metrics, result_df = self._apply_strategy(df, rsi_oversold, rsi_overbought, sl, tp)
                    if metrics['Sharpe Ratio'] > best_sharpe:
                        best_sharpe = metrics['Sharpe Ratio']
                        best_result = {
                            'Symbol': self.symbol,
                            'Interval': interval,
                            'MACD Fast': fast,
                            'MACD Slow': slow,
                            'MACD Signal': signal,
                            'RSI Period': rsi_p,
                            'RSI Oversold': rsi_oversold,
                            'RSI Overbought': rsi_overbought,
                            'Stop Loss %': sl,
                            'Take Profit %': tp,
                            **metrics
                        }
                        best_df = result_df
                        best_interval = interval
                except Exception:
                    continue

        self.best_result = best_result
        self.best_interval = best_interval
        self.best_result_df = best_df
        return best_result, best_df




##############################################################################################################
import pandas as pd
import numpy as np
import requests
from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET
from datetime import datetime
import time


class Sirifi_C_TradingBot:
    def __init__(self, symbol: str, interval: str, params: dict,
                 api_key: str = None, api_secret: str = None,
                 fee: float = 0.001, slippage_pct: float = 0.0005,
                 enable_telegram: bool = False,
                 telegram_token: str = None, telegram_chat_id: str = None,
                 max_budget: float = 100.0,
                 dry_run: bool = True):
        """
        :param symbol: Trading pair like 'BTCUSDC'
        :param interval: Binance interval like '1h', '15m'
        :param params: Strategy parameters (dict)
        :param api_key: Binance API Key
        :param api_secret: Binance Secret Key
        :param fee: Trading fee (e.g., 0.001 for 0.1%)
        :param slippage_pct: Slippage percent (e.g., 0.0005 = 0.05%)
        :param enable_telegram: Enable Telegram alerts
        :param telegram_token: Telegram bot token
        :param telegram_chat_id: Telegram chat ID
        :param max_budget: Max USDC/USDT to spend per trade (entry)
        :param dry_run: If True, no real orders will be placed
        """
        assert symbol.endswith(('USDC', 'USDT')), "Only USDC or USDT pairs are supported"
        self.symbol = symbol
        self.interval = interval
        self.params = params
        self.fee = fee
        self.slippage_pct = slippage_pct

        self.client = Client(api_key, api_secret)
        self.enable_telegram = enable_telegram
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id

        self.position = 0  # 0 = no position, 1 = holding
        self.entry_price = None
        self.max_budget = max_budget
        self.dry_run = dry_run

        self.start_date = datetime.now()
        self.initial_capital = None

    def interval_to_seconds(self):
        """
        Converts Binance interval string like '1h', '15m' into seconds.
        """
        unit = self.interval[-1]
        amount = int(self.interval[:-1])
        if unit == 'm':
            return amount * 60
        elif unit == 'h':
            return amount * 3600
        elif unit == 'd':
            return amount * 86400
        else:
            # default to 1 hour if unknown
            return 3600

    def fetch_ohlcv(self, lookback: int = 100):
        klines = self.client.get_klines(symbol=self.symbol, interval=self.interval, limit=lookback)
        df = pd.DataFrame(klines, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base', 'taker_buy_quote', 'ignore'
        ])
        df['close'] = df['close'].astype(float)
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df.set_index('open_time', inplace=True)
        return df

    def compute_indicators(self, df):
        # MACD calculation
        ema_fast = df['close'].ewm(span=self.params['macd_fast'], adjust=False).mean()
        ema_slow = df['close'].ewm(span=self.params['macd_slow'], adjust=False).mean()
        macd = ema_fast - ema_slow
        signal = macd.ewm(span=self.params['macd_signal'], adjust=False).mean()

        # RSI calculation
        delta = df['close'].diff()
        gain = delta.clip(lower=0).rolling(window=self.params['rsi_period']).mean()
        loss = -delta.clip(upper=0).rolling(window=self.params['rsi_period']).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        df['MACD'] = macd
        df['Signal'] = signal
        df['RSI'] = rsi
        return df.dropna()

    def notify(self, message: str):
        if not self.enable_telegram:
            print("[Telegram Disabled] " + message)
            return
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {
            'chat_id': self.telegram_chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }
        try:
            response = requests.post(url, data=payload)
            if response.status_code != 200:
                print(f"Telegram error: {response.text}")
        except Exception as e:
            print(f"Failed to send Telegram message: {e}")

    def get_balance(self, asset: str) -> float:
        balances = self.client.get_account()['balances']
        for b in balances:
            if b['asset'] == asset:
                return float(b['free'])
        return 0.0

    def place_order(self, side: str, quantity: float):
        if self.dry_run:
            self.notify(f"[DRY RUN] Would place {side} order for {quantity} {self.symbol.replace('USDC', '').replace('USDT', '')}")
            return {"status": "dry_run", "side": side, "quantity": quantity}

        try:
            order = self.client.create_order(
                symbol=self.symbol,
                side=side,
                type=ORDER_TYPE_MARKET,
                quantity=quantity
            )
            return order
        except Exception as e:
            self.notify(f"⚠️ Order error: {e}")
            return None

    def get_price(self) -> float:
        ticker = self.client.get_symbol_ticker(symbol=self.symbol)
        return float(ticker['price'])

    def get_portfolio_value(self) -> float:
        quote_asset = 'USDC' if 'USDC' in self.symbol else 'USDT'
        base_asset = self.symbol.replace(quote_asset, '')
        usdc = self.get_balance(quote_asset)
        coin = self.get_balance(base_asset)
        coin_price = self.get_price()
        return usdc + coin * coin_price

    def get_status_report(self):
        port_val = self.get_portfolio_value()

        if self.initial_capital is None:
            self.initial_capital = port_val

        pnl = ((port_val - self.initial_capital) / self.initial_capital) * 100 if self.initial_capital else 0
        base_asset = self.symbol.replace('USDC', '').replace('USDT', '')
        quote_asset = 'USDC' if 'USDC' in self.symbol else 'USDT'
        base_qty = self.get_balance(base_asset)
        quote_qty = self.get_balance(quote_asset)

        status = "📈 BUY (Holding)" if self.position == 1 else "⏸️ HOLD (No Position)"

        msg = (
            f"📊 *Bot Status Report*\n\n"
            f"🕒 *Start Date:* {self.start_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"💰 *Initial Capital:* {self.initial_capital:.2f} {quote_asset}\n"
            f"📈 *Current Portfolio:* {port_val:.2f} {quote_asset}\n"
            f"📊 *PnL:* {pnl:.2f}%\n"
            f"📌 *Position:* {status}\n"
            f"🔹 *{base_asset} Balance:* {base_qty:.5f}\n"
            f"🔹 *{quote_asset} Balance:* {quote_qty:.2f}\n"
        )

        print("\n===== 📊 BOT STATUS REPORT =====")
        print(msg.replace("*", ""))
        print("================================\n")

        if self.enable_telegram:
            self.notify(msg)

    def _sell(self, price, reason):
        base_asset = self.symbol.replace('USDC', '').replace('USDT', '')
        qty = round(self.get_balance(base_asset), 5)
        if qty > 0:
            order = self.place_order(SIDE_SELL, qty)
            if order:
                self.position = 0
                self.entry_price = None
                port_val = self.get_portfolio_value()
                self.notify(f"{reason} - Sold {qty} {self.symbol} at approx {price:.4f}\n"
                            f"Portfolio value: ${port_val:.2f}")

    def run_loop(self):
        sleep_sec = self.interval_to_seconds()
        self.notify(f"🤖 Started trading bot on {self.symbol} with interval {self.interval} ({sleep_sec} seconds)")
        while True:
            try:
                # Fetch data and indicators
                df = self.fetch_ohlcv()
                df = self.compute_indicators(df)
                macd = df['MACD'].iloc[-1]
                signal = df['Signal'].iloc[-1]
                rsi = df['RSI'].iloc[-1]
                close = df['close'].iloc[-1]

                # Initialize capital at first run
                if self.initial_capital is None:
                    self.initial_capital = self.get_portfolio_value()

                print(f"{self.symbol} - MACD: {macd:.4f}, Signal: {signal:.4f}, RSI: {rsi:.2f}, Price: {close:.4f}")

                base_asset = self.symbol.replace('USDC', '').replace('USDT', '')
                quote_asset = 'USDC' if 'USDC' in self.symbol else 'USDT'

                # Entry logic
                if self.position == 0:
                    if macd > signal and rsi < self.params['rsi_oversold']:
                        usdc = self.get_balance(quote_asset)
                        amount = min(self.max_budget, usdc)
                        qty = round(amount / close, 5)

                        # Check Binance min notional (skip if too low)
                        min_notional = self.get_min_notional()
                        if qty * close < min_notional:
                            self.notify(f"❌ Trade skipped: Notional value {qty * close:.2f} below min {min_notional}")
                        elif qty > 0:
                            order = self.place_order(SIDE_BUY, qty)
                            if order:
                                self.position = 1
                                self.entry_price = close * (1 + self.slippage_pct)
                                port_val = self.get_portfolio_value()
                                self.notify(f"✅ Bought {qty} {self.symbol} at approx {self.entry_price:.4f}\n"
                                            f"Portfolio value: ${port_val:.2f}")
                else:
                    # Exit logic (stop loss / take profit)
                    pnl = (close - self.entry_price) / self.entry_price
                    if pnl <= -self.params['stop_loss']:
                        self._sell(close, reason="🛑 Stop Loss")
                    elif pnl >= self.params['take_profit']:
                        self._sell(close, reason="🎯 Take Profit")

                # Send status report every cycle
                self.get_status_report()

            except Exception as e:
                self.notify(f"⚠️ Error: {e}")

            time.sleep(sleep_sec)

    def get_min_notional(self):
        """Get minimum notional value for the symbol from exchange info."""
        try:
            exchange_info = self.client.get_exchange_info()
            for symbol_info in exchange_info['symbols']:
                if symbol_info['symbol'] == self.symbol:
                    for filt in symbol_info['filters']:
                        if filt['filterType'] == 'MIN_NOTIONAL':
                            return float(filt['minNotional'])
            return 10  # default fallback
        except Exception as e:
            self.notify(f"⚠️ Failed to fetch min notional: {e}")
            return 10



