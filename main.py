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
    #exchanges =  ["gate","kucoin"]
    
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
    worksheet.set_column('C:C', 9, priceFormat)             # Price
    worksheet.set_column('D:D', 9, volumeFormat)            # 24h Volume
    worksheet.set_column('E:F', 10, volumeFormat)           # Base / Quote
    worksheet.set_column('G:G', 13, percentFormat)          # Spread %
    worksheet.set_column('H:I', 9, volumeFormat)            # +/-2%

    worksheet.autofilter('A1:I11')
    worksheet.freeze_panes(1, 0)
        
    writer.save()
    
if __name__ == "__main__":
    run()