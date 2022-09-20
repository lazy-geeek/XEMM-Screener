import ccxt
import json
import pandas as pd
import time

from functions import *
from pprint import pprint

def run():
    
    print("XEMM Screener")

    with open('config.json', 'r') as f:
        config = json.load(f)
        
    df = pd.DataFrame()
    rows = []
    baseCoins = []
    min24hvolume = 0        
        
    exchanges = config['exchanges']
    min24hvolume = config['min24hvolume']
    
    #exchanges =  ["binance","bybit","ftx","gate","hitbtc","huobi","kucoin","okx"]
    exchanges =  ["gate","kucoin"]
    
    for exchangeName in exchanges:  
        
        try:              

            exchange_class = getattr(ccxt, exchangeName)

            exchange = exchange_class({
                "enableRateLimit": True,
                "options": {'defaultType': 'spot' }            
            })

            print("Exchange:", exchange)

            markets = exchange.load_markets(True)
            tickers = exchange.fetch_tickers()
            
            for pair, value in markets.items():
                quoteVolume = 0
                row = {}
                
                quote = value['quote']
                base = value['base']
                            
                if not (isActiveMarket(value) and isSpotPair(value) and isUSDpair(quote)):
                    continue
                
                if isUSDBasePair(base):
                    continue
                
                ticker = tickers[pair]
                            
                if not tickerHasPrice(ticker):
                    continue    
                
                ######### TODO: Convert nonUSD pairs to USD
                
                ask = ticker['ask']
                bid = ticker['bid']            
                quoteVolume = ticker['quoteVolume'] 
                
                if quoteVolume is None:
                    continue       
                
                if quoteVolume < min24hvolume:
                    continue      
                
                if base not in baseCoins:
                    baseCoins.append(base)      
                
                spread = (ask / bid - 1) * 100
                
                # Calculate Orderbook Volume            
                
                orderbook = exchange.fetch_order_book(pair)
                
                if not (orderbook['asks'] or orderbook['bids']):
                    askVolume = 0
                    bidVolume = 0                
                else:
                    askVolume = orderBookVolume('asks',orderbook)
                    bidVolume = orderBookVolume('bids',orderbook)
                
                # Create row
            
                row['exchange'] = exchangeName
                row['ticker'] = ticker['symbol']
                row['price'] = ticker['last']
                row['volume'] = quoteVolume / 1000
                row['base'] = base
                row['quote'] = quote
                row['spread'] = spread
                row['askVolume'] = askVolume
                row['bidVolume'] = bidVolume
                
                rows.append(row)
                
                
                
        except ccxt.ExchangeError as e:
            pprint(str(e))
            
    df = pd.DataFrame.from_records(rows)
    
    # Remove Base pairs which are only traded on 1 exchange

    for base in baseCoins:
        indexBase = df[ (df['base'] == base) ].index
        if len(indexBase) == 1:
            df.drop(indexBase, inplace=True)  # type: ignore
        
    ######### TODO: Keep only exchanges with highest and lowest spread
    
    ######### TODO: Spread Factor between highest and lowest spread
    
    # Format Numbers

    """
    df['price'] = df['price'].map('{:,.0f}'.format)
    df['volume'] = df['volume'].map('{:,.0f}'.format)
    df['spread'] = df['spread'].map('{:,.0f}'.format)
    df['askVolume'] = df['askVolume'].map('{:,.0f}'.format)
    df['bidVolume'] = df['bidVolume'].map('{:,.0f}'.format)
    """
        
    df.sort_values(['ticker'], inplace=True, ascending=True)
    
    df.rename(columns={ 'exchange': 'Exchange',
                        'ticker': 'Ticker',
                        'price': 'Price',
                        'volume': '24h',
                        'base': 'Base',
                        'quote': 'Quote',
                        'spread': 'Spread %',
                        'askVolume': '+2%',
                        'bidVolume': '-2%'
                            }, inplace=True)
        
    fileName = time.strftime("%Y%m%d-%H%M%S") + ".xlsx"
    
    
    
    ######### TODO: Format Volume to million
    
    ######### TODO: Excel is filterable
    
    ######### TODO: Autoformat Excel
    
    df.to_excel(fileName, index=False)
                
if __name__ == "__main__":
    run()