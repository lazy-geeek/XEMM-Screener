import ccxt
from pprint import pprint
import json
from functions import *

def run():

    print("XEMM Screener")

    with open('config.json', 'r') as f:
        config = json.load(f)
        
    min24hvolume = 0    
        
    exchanges = config['exchanges']
    min24hvolume = config['min24hvolume']
        
    #exchanges =  ["ascendex","binance","bybit","ftx","gate","hitbtc","huobi","kucoin","okx"]
    
    exchanges =  ["huobi"]
    
    for exchangeName in exchanges:
                
        rows = []        

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
            
            if not tickerHasPrice(tickers[pair]):
                continue    
            
            ######### TODO: Convert to USD
            
            ticker = tickers[pair]
            quoteVolume = ticker['quoteVolume']           
            
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
            
            ######### TODO: Create pandas dataframe
            
            
                
if __name__ == "__main__":
    run()