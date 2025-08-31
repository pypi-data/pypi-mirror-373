from binance.client import Client
from newsapi import NewsApiClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class Sirifi_C_SentimentAnalyzer:
    def __init__(self, binance_api_key, binance_api_secret, newsapi_key, 
                 quote_asset='USDC', max_symbols=100, threads=5):
        self.binance_client = Client(binance_api_key, binance_api_secret)
        self.newsapi = NewsApiClient(api_key=newsapi_key)
        self.analyzer = SentimentIntensityAnalyzer()
        self.quote_asset = quote_asset
        self.max_symbols = max_symbols
        self.threads = threads
        
        # Will hold symbol-to-fullname mapping
        self.symbol_name_map = {}

    def fetch_symbols_and_names(self):
        info = self.binance_client.get_exchange_info()
        symbols = []
        for s in info['symbols']:
            if s['quoteAsset'] == self.quote_asset and s['status'] == 'TRADING':
                symbols.append(s['symbol'])
                self.symbol_name_map[s['symbol']] = s['baseAsset']
        return symbols[:self.max_symbols]

    def get_sentiment_for_news(self, query):
        """
        Fetch news articles for the query, and compute aggregate sentiment.
        Returns dict with average positive, negative, neutral, compound, and total articles.
        """
        try:
            all_articles = []
            # Fetch up to 100 articles in multiple pages (NewsAPI allows max 100 per request)
            for page in range(1, 3):  # try two pages max to limit requests
                response = self.newsapi.get_everything(
                    q=query,
                    language='en',
                    sort_by='relevancy',
                    page_size=50,
                    page=page
                )
                if 'articles' not in response or not response['articles']:
                    break
                all_articles.extend(response['articles'])
                if len(response['articles']) < 50:
                    break
                time.sleep(1)  # be polite to API rate limits
            
            if not all_articles:
                return None
            
            # Aggregate sentiment scores
            pos, neg, neu, comp = 0, 0, 0, 0
            for article in all_articles:
                text = (article.get('title') or '') + ' ' + (article.get('description') or '')
                vs = self.analyzer.polarity_scores(text)
                pos += vs['pos']
                neg += vs['neg']
                neu += vs['neu']
                comp += vs['compound']
            
            count = len(all_articles)
            return {
                'positive': pos / count,
                'negative': neg / count,
                'neutral': neu / count,
                'compound': comp / count,
                'total_articles': count
            }
        except Exception as e:
            print(f"[!] NewsAPI error for query '{query}': {e}")
            return None

    def fetch_price(self, symbol):
        try:
            ticker = self.binance_client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except:
            return None

    def analyze_single_crypto(self, symbol):
        """
        Runs sentiment for both symbol and full coin name, merges results,
        and gets current price.
        """
        full_name = self.symbol_name_map.get(symbol, '')
        # Query both symbol and full name
        sentiment_symbol = self.get_sentiment_for_news(symbol)
        sentiment_name = self.get_sentiment_for_news(full_name)

        # Combine sentiment scores if both available
        def combine_sentiments(a, b):
            if a and b:
                return {
                    k: (a[k] + b[k]) / 2 for k in a.keys()
                }
            return a or b

        combined_sentiment = combine_sentiments(sentiment_symbol, sentiment_name)
        if combined_sentiment is None:
            return None

        price = self.fetch_price(symbol)
        if price is None:
            return None

        # Calculate ranking score: weighted compound + positive/negative ratio
        pos_neg_ratio = combined_sentiment['positive'] / (combined_sentiment['negative'] + 1e-6)
        ranking_score = 0.6 * combined_sentiment['compound'] + 0.4 * pos_neg_ratio

        return {
            'symbol': symbol,
            'name': full_name,
            'price': round(price, 6),
            'positive': round(combined_sentiment['positive'], 4),
            'negative': round(combined_sentiment['negative'], 4),
            'neutral': round(combined_sentiment['neutral'], 4),
            'compound': round(combined_sentiment['compound'], 4),
            'total_articles': combined_sentiment['total_articles'],
            'pos_neg_ratio': round(pos_neg_ratio, 4),
            'ranking_score': round(ranking_score, 4)
        }

    def analyze_all(self):
        symbols = self.fetch_symbols_and_names()
        print(f"Analyzing {len(symbols)} cryptos for sentiment...")

        results = []
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(self.analyze_single_crypto, sym): sym for sym in symbols}
            for i, future in enumerate(as_completed(futures), 1):
                sym = futures[future]
                try:
                    res = future.result()
                    if res:
                        results.append(res)
                except Exception as e:
                    print(f"[!] Error processing {sym}: {e}")
                print(f"[{i}/{len(symbols)}] Processed {sym}")

        df = pd.DataFrame(results)
        if not df.empty:
            df.sort_values('ranking_score', ascending=False, inplace=True)
            df.reset_index(drop=True, inplace=True)
            df.index += 1  # Start index at 1 for ranking display
            df.rename_axis('Rank', inplace=True)
        return df


