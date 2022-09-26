import ccxt
import json
import pandas as pd
import time

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
    screenedExchanges =  ["mexc3"]    
    
    for exchangeName in screenedExchanges:
        
        if not exchangeName in supportedExchanges:
            continue
        
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
                
                spotExchange = exchange_class({
                    "enableRateLimit": True,
                    "options": {'defaultType': 'spot' }           
                })

                spotMarkets = spotExchange.load_markets(True)
                spotTickers = spotExchange.fetch_tickers()
            
            if exchangeName in ["binanceusdm","bybit","ftx","gate","kucoinfutures","mexc3"]:
                
                # Future markets
                
                if exchangeName in ["gate","mexc3"]:
                    futureExchange = exchange_class({
                        "enableRateLimit": True,
                        "options": {'defaultType': 'swap' }           
                    })
                else:                
                    futureExchange = exchange_class({
                        "enableRateLimit": True,
                        "options": {'defaultType': 'future' }           
                    })

                futureMarkets = futureExchange.load_markets(True)
                futureTickers = futureExchange.fetch_tickers()
                
            markets.update(spotMarkets)
            markets.update(futureMarkets)
            tickers.update(spotTickers)
            tickers.update(futureTickers)
            
            print('Number of markets: ', len(markets))
            print('Number of tickers: ', len(tickers))
                        
            for key, value in markets.items():
                quoteVolume = 0
                row = {}
                
                pair = value['symbol']
                quote = value['quote']
                base = value['base']
                
                type = value['type']                
                            
                if not (isActiveMarket(value) and isValidPair(exchangeName, value)):
                    continue
                
                if isUSDBasePair(base):
                    continue
                
                if not pair in tickers.keys():
                    continue                
                
                ticker = tickers[pair]                
                            
                if not tickerHasPrice(type, ticker):
                    continue 
                
                quoteVolume = ticker['quoteVolume'] 
                
                if quoteVolume is None:
                    continue                
                
                if not isUSDpair(quote):
                    pairFound = False                
                    # Find USD pair for base -> Convert quote volume to USD
                    for usdPair, marketValue in markets.items():                
                        if 'USD' in marketValue['quote'] and quote in marketValue['base'] and usdPair in tickers.keys():                 
                            quoteVolume *= tickers[usdPair]['last']
                            pairFound = True
                            break
                    if not pairFound:
                        continue
                            
                
                if quoteVolume < min24hvolume:
                    continue
                
                ######### TODO: Number of trades in the last hour                
                    
                if isSpotPair(type):
                    orderbook = spotExchange.fetch_order_book(pair) # type: ignore
                else:
                    orderbook = futureExchange.fetch_order_book(pair) # type: ignore

                
                ask = orderBookPrice('asks', orderbook)
                bid = orderBookPrice('bids', orderbook)
                
                if (ask == 0 or ask == None or bid == 0 or bid == None):                
                    continue
                
                spread = (ask / bid - 1) * 100
                
                if base not in baseCoins:
                    baseCoins.append(base)      
                            
                ######### TODO: Orderbook volume of swap pairs is too high
                                
                # Calculate Orderbook Volume  
                
                if not (orderbook['asks'] or orderbook['bids']):
                    askVolume = 0
                    bidVolume = 0                
                else:
                    askVolume = orderBookVolume('asks',orderbook,orderBookDepth)
                    bidVolume = orderBookVolume('bids',orderbook,orderBookDepth)
                
                # Create row
            
                row['exchange'] = exchangeName
                row['ticker'] = ticker['symbol']
                row['type'] = type
                row['price'] = ticker['last']
                row['volume'] = quoteVolume / 1000000
                row['base'] = base
                row['quote'] = quote
                row['spread'] = spread
                row['askVolume'] = askVolume
                row['bidVolume'] = bidVolume
                
                rows.append(row)                
        
        except ccxt.ExchangeError as e:
            pprint(str(e))
    
    ######### TODO: Spread Factor between highest and lowest spread
                    
    df = pd.DataFrame.from_records(rows)
    
    # Remove Base pairs which are only traded on 1 exchange
    # TODO Reactivate Code only 1 exchange
    """
    for base in baseCoins:
        indexBase = df[ (df['base'] == base) ].index
        if len(indexBase) == 1:
            df.drop(indexBase, inplace=True)  # type: ignore
    """
    
        
    df.sort_values(['ticker'], inplace=True, ascending=True)
    
    df.rename(columns={ 'exchange': 'Exchange',
                        'ticker': 'Ticker',
                        'type' : 'Type',
                        'price': 'Price',
                        'volume': '24h M',
                        'base': 'Base',
                        'quote': 'Quote',
                        'spread': 'Spread %',
                        'askVolume': '+' + str(orderBookDepth) + '%',
                        'bidVolume': '-' + str(orderBookDepth) + '%'
                            }, inplace=True)
        
    sheetName = 'Order Books'
    fileName = time.strftime("%Y%m%d-%H%M%S") + ".xlsx"
        
    writer = pd.ExcelWriter(fileName,engine='xlsxwriter') # type: ignore
    df.to_excel(writer, sheet_name=sheetName, index=False)
    
    workbook  = writer.book
    worksheet = writer.sheets[sheetName]

    # Add cell formats.
    priceFormat = workbook.add_format({'num_format': '#,##0.00'}) # type: ignore
    volumeFormat = workbook.add_format({'num_format': '#,##0'}) # type: ignore
    percentFormat = workbook.add_format({'num_format': '0.0000'}) # type: ignore

    # Set the column width and format.
    worksheet.set_column('A:A', 13)                         # Exchange
    worksheet.set_column('B:B', 14)                         # Ticker
    worksheet.set_column('D:D', 9, priceFormat)             # Price
    worksheet.set_column('E:E', 9, volumeFormat)            # 24h Volume
    worksheet.set_column('F:G', 10, volumeFormat)           # Base / Quote
    worksheet.set_column('H:H', 13, percentFormat)          # Spread %
    worksheet.set_column('I:J', 9, volumeFormat)            # Orderbook Depth

    worksheet.autofilter('A1:I11')
    worksheet.freeze_panes(1, 0)
        
    workbook.close()    
    
if __name__ == "__main__":
    run()