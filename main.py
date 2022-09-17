import ccxt
from pprint import pprint
import json
from functions import *

def run():

    print("XEMM Screener")

    with open('config.json', 'r') as f:
        config = json.load(f)
        
    exchanges = config['exchanges']
    min24hvolume = config['min24hvolume']
        
    pprint(exchanges)
    
    for exchangeName in exchanges:   
        
        allPairs = []  

        exchange_class = getattr(ccxt, exchangeName)

        exchange = exchange_class({
            "enableRateLimit": True,
            "options": {'defaultType': 'spot' }            
        })

        print("Exchange:", exchange)

        markets = exchange.load_markets(True)
        
        for pair, value in markets.items():
            if isActiveMarket(value) and isSpotPair(value):
                allPairs.append(pair)

        tickers = exchange.fetch_tickers()

        """
        for pair in allPairs:
            if not tickerHasPrice(tickers[pair]):
                allPairs.remove(pair)
        """
            
        # ######### TODO: Check market volume        

        print(tickers[allPairs[0]]['symbol'])

                
if __name__ == "__main__":
    run()