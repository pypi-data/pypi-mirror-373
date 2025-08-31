import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from binance.client import Client
from concurrent.futures import ThreadPoolExecutor, as_completed


class Sirifi_C_ValueInvest:
    def __init__(self, api_key, api_secret, quote_asset='USDC', timeframe='1d', max_symbols=50, threads=10, history_days=90):
        self.client = Client(api_key, api_secret)
        self.quote_asset = quote_asset
        self.timeframe = timeframe
        self.max_symbols = max_symbols
        self.threads = threads
        self.history_days = history_days
        self.timeframe_map = {
            '30m': timedelta(minutes=30),
            '1h': timedelta(hours=1),
            '1d': timedelta(days=1),
        }

    def get_start_time_ms(self):
        delta = self.timeframe_map[self.timeframe]
        return int((datetime.utcnow() - delta).timestamp() * 1000)

    def fetch_all_symbols(self):
        info = self.client.get_exchange_info()
        return [
            s['symbol'] for s in info['symbols']
            if s['quoteAsset'] == self.quote_asset and s['status'] == 'TRADING'
        ][:self.max_symbols]

    def fetch_price_and_market_cap(self, symbol):
        try:
            ticker = self.client.get_ticker(symbol=symbol)
            price = float(ticker.get('lastPrice', 0))
            quote_volume = float(ticker.get('quoteVolume', 0))
            market_cap = quote_volume / 0.05  # Approximate
            return price, float(ticker.get('priceChangePercent', 0)), market_cap
        except:
            return 0.0, 0.0, 0.0

    def fetch_agg_trades(self, symbol, start_time, end_time):
        trades = []
        while True:
            try:
                batch = self.client.get_aggregate_trades(
                    symbol=symbol,
                    startTime=start_time,
                    endTime=end_time,
                    limit=1000
                )
                if not batch:
                    break
                trades.extend(batch)
                last_trade_time = batch[-1]['T']
                if last_trade_time >= end_time:
                    break
                start_time = last_trade_time + 1
                time.sleep(0.05)
            except:
                break
        return trades

    def calculate_historical_metrics(self, symbol):
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=self.history_days)
            klines = self.client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1DAY,
                                                       start_time.strftime("%d %b %Y %H:%M:%S"),
                                                       end_time.strftime("%d %b %Y %H:%M:%S"))

            df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume',
                                               'close_time', 'quote_asset_volume', 'num_trades',
                                               'taker_buy_base', 'taker_buy_quote', 'ignore'])
            df['close'] = df['close'].astype(float)
            df['returns'] = df['close'].pct_change()

            # CAGR
            cagr = (df['close'].iloc[-1] / df['close'].iloc[0]) ** (365 / len(df)) - 1

            # Sharpe
            sharpe = df['returns'].mean() / df['returns'].std() * np.sqrt(365) if df['returns'].std() != 0 else 0

            # Max Drawdown
            cumulative = (1 + df['returns']).cumprod()
            drawdown = cumulative / cumulative.cummax() - 1
            max_drawdown = drawdown.min()

            return round(cagr, 4), round(sharpe, 4), round(max_drawdown, 4)

        except Exception as e:
            print(f"[!] Historical data error for {symbol}: {e}")
            return 0.0, 0.0, 0.0

    def process_symbol(self, symbol, start_time, end_time):
        trades = self.fetch_agg_trades(symbol, start_time, end_time)
        if not trades:
            return None

        total_buy = 0
        total_sell = 0
        for trade in trades:
            value = float(trade['p']) * float(trade['q'])
            if trade['m']:
                total_sell += value
            else:
                total_buy += value

        total_volume = total_buy + total_sell
        net_flow_pct = (total_buy - total_sell) / total_volume if total_volume > 0 else 0
        price, price_change_pct, market_cap = self.fetch_price_and_market_cap(symbol)

        cagr, sharpe, max_dd = self.calculate_historical_metrics(symbol)

        return {
            'symbol': symbol,
            'price': round(price, 4),
            'price_change_pct': price_change_pct,
            'total_volume': round(total_volume, 2),
            'net_flow_pct': round(net_flow_pct, 4),
            'market_cap': round(market_cap, 2),
            'cagr': cagr,
            'sharpe': sharpe,
            'max_drawdown': max_dd
        }

    def analyze(self):
        symbols = self.fetch_all_symbols()
        start_time = self.get_start_time_ms()
        end_time = int(datetime.utcnow().timestamp() * 1000)
        print(f"Analyzing {len(symbols)} symbols with historical data...")

        results = []
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(self.process_symbol, symbol, start_time, end_time): symbol for symbol in symbols}
            for future in as_completed(futures):
                data = future.result()
                if data:
                    results.append(data)

        df = pd.DataFrame(results)
        if not df.empty:
            df['volume_yield'] = df['total_volume'] / df['market_cap']
            df['value_score'] = (
                (1 - df['price_change_pct'].rank(pct=True)) * 1.5 +  # Contrarian
                df['net_flow_pct'].rank(pct=True) * 1.0 +
                df['volume_yield'].rank(pct=True) * 1.0 +
                df['cagr'].rank(pct=True) * 2.0 +
                df['sharpe'].rank(pct=True) * 1.5 +
                (1 - df['max_drawdown'].rank(pct=True)) * 1.0  # Lower is better
            )
            df['rank'] = df['value_score'].rank(ascending=False).astype(int)
            df = df.sort_values(by='rank')

        return df[['rank', 'symbol', 'price', 'price_change_pct', 'net_flow_pct', 'total_volume',
                   'market_cap', 'volume_yield', 'cagr', 'sharpe', 'max_drawdown', 'value_score']].reset_index(drop=True)
