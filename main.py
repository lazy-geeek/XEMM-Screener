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
    min24hvolume = 0        
        
    exchanges = config['exchanges']
    min24hvolume = config['min24hvolume']
    
    #exchanges =  ["ascendex","binance","bybit","ftx","gate","hitbtc","huobi","kucoin","okx"]
    
    for exchangeName in exchanges:                

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
            
            ######### TODO: Skip Base USD pairs
            
            ######### TODO: Skip Base pairs which are only traded on 1 exchange
            
            if not (isActiveMarket(value) and isSpotPair(value) and isUSDpair(quote)):
                continue
            
            if not tickerHasPrice(tickers[pair]):
                continue    
            
            ######### TODO: Convert nonUSD pairs to USD
            
            ticker = tickers[pair]
            quoteVolume = ticker['quoteVolume']    
            
            if quoteVolume is None:
                continue       
            
            if quoteVolume < min24hvolume:
                continue                    

            #print(tickers[allPairs[0]]['symbol'])
            
            ######### TODO: Calculate Spread
            
            ######### TODO: Calculate Orderbook Volume
            
            # Create row
        
            row['Exchange'] = exchangeName
            row['Ticker'] = ticker['symbol']
            row['Price'] = ticker['last']
            row['24h'] = quoteVolume
            row['Base'] = base
            row['Quote'] = quote
            
            rows.append(row)
            
    df = pd.DataFrame.from_records(rows)
    
    df.sort_values(['Ticker'], inplace=True, ascending=True)
        
    fileName = time.strftime("%Y%m%d-%H%M%S") + ".xlsx"
    
    ######### TODO: Format Price Decimals
    
    ######### TODO: Format Volume to million
    
    ######### TODO: Excel is filterable
    
    ######### TODO: Autoformat Excel
    
    df.to_excel(fileName, index=False)
                
if __name__ == "__main__":
    run()