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
    orderBookDepth = config['orderBookDepth']
    
    #exchanges =  ["binance","bybit","ftx","gate","hitbtc","huobi","kucoin","okx"]
    exchanges =  ["gate"]
    
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
            
            pair = '1INCH/ETH'
            quoteVolume = 0
            row = {}
                
            quote = 'ETH'
            base = '1INCH'
                
            ticker = tickers[pair]
                            
            if not isUSDpair(quote):                
                # Find USD pair for base
                for usdPair, marketValue in markets.items():                
                    if 'USD' in marketValue['quote'] and quote in marketValue['base']:                 
                        print(usdPair)
                        
                        print(tickers[usdPair]['last'])
                        break
                
        except ccxt.ExchangeError as e:
            pprint(str(e))
            
    
if __name__ == "__main__":
    run()