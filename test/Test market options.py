from traceback import print_exc
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
    
    #exchanges =  ["binance","binanceusdm","bybit","ftx","gate","hitbtc","mexc","huobi","kucoin","okx"]
    exchanges =  ["mexc3"]
    
    for exchangeName in exchanges:  
        
        try:              

            exchange_class = getattr(ccxt, exchangeName)

            exchange = exchange_class({
                "enableRateLimit": True,
                "options": {'defaultType': 'future' }           
                
            })

            print("Exchange:", exchange)

            markets = exchange.load_markets(True)
            tickers = exchange.fetch_tickers()
            
            
            for pair, value in markets.items():
                text = value['symbol'] + ' ' + value['type']
                print(text)
            
                
            print(len(markets))
                
        except ccxt.ExchangeError as e:
            pprint(str(e))
            
    
if __name__ == "__main__":
    run()