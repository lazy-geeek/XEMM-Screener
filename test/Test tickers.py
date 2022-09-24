import ccxt
import json
import pandas as pd
import time
import os
import sys

# Append parent directory to import path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from functions import *
from pprint import pprint

supportedExchanges = ["binance","binanceusdm","bybit","ftx","gate","mexc3","kucoin","kucoinfutures"]

def run():
    
    print("XEMM Screener")

    with open('config.json', 'r') as f:
        config = json.load(f)
        
    df = pd.DataFrame()
    rows = []
    baseCoins = []
    min24hvolume = 0        
        
    screenedExchanges = config['screenedExchanges']
    min24hvolume = config['min24hvolume']
    orderBookDepth = config['orderBookDepth']
    
    #exchanges =  ["binance","binanceusdm","bybit","ftx","gate","mexc3","kucoin","kucoinfutures"]
    screenedExchanges =  ["binanceusdm"]
    
    for exchangeName in screenedExchanges:
        
    
        #if not exchangeName in supportedExchanges:
        #    continue
        
        print("Exchange:", exchangeName)
        
        markets = {}    
        tickers = {}
        spotMarkets = {}
        spotTickers = {}
        futureMarkets = {}
        futureTickers = {}
        
        try:              

            exchange_class = getattr(ccxt, exchangeName)
                        
            if exchangeName in ["binance","bybit","ftx","gate","mexc3","kucoin"]:
                
                # Spot markets
                
                exchange = exchange_class({
                    "enableRateLimit": True,
                    "options": {'defaultType': 'spot' }           
                })

                spotMarkets = exchange.load_markets(True)
                spotTickers = exchange.fetch_tickers()
            
            if exchangeName in ["binanceusdm","bybit","gate","kucoinfutures"]:
                
                # Future markets
                
                exchange = exchange_class({
                    "enableRateLimit": True,
                    "options": {'defaultType': 'future' }           
                })

                futureMarkets = exchange.load_markets(True)
                futureTickers = exchange.fetch_tickers()
                
            markets.update(spotMarkets)
            markets.update(futureMarkets)
            tickers.update(spotTickers)
            tickers.update(futureTickers)
            
            orderbook = exchange.fetch_order_book('BTC/USDT')
            pprint(orderbook)
            
            """
            print('Number of markets: ', len(markets))
            print('Number of tickers: ', len(tickers))
            
            for key, value in markets.items():
                print(value['symbol'], value['type'])
                        
            for key, value in tickers.items():
                print(key)
                        
            
            for key, value in markets.items():
                quoteVolume = 0
                row = {}
                
                pair = value['symbol']
                quote = value['quote']
                base = value['base']
                
                type = value['type']
                
                
                
                print(pair, isActiveMarket(value), isValidPair(exchangeName, value))
                
                            
                if not (isActiveMarket(value) and isValidPair(exchange, value)):
                    continue                
                
                if isUSDBasePair(base):
                    continue
                
                
                
                if not pair in tickers.keys():
                    continue
                
                ticker = tickers[pair]
                            
                if not tickerHasPrice(ticker):
                    continue    
             
                pprint(ticker)
                
                """
               
        except ccxt.ExchangeError as e:
            pprint(str(e))

if __name__ == "__main__":
    run()