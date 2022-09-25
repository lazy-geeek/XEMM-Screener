def isValidPair(exchangeName, value):
    if exchangeName in ['binance']:
        if value['type'] == 'spot':
            return True
    
    if exchangeName in ['binanceusdm']:
        if value['type'] == 'future':
            return True
        
    if exchangeName in ['bybit']:
        if value['type'] == 'spot' or value['type'] == 'swap':
            return True
    
    #TODO: Check Type -> Dependend on exchange
    
def isActiveMarket(value):
    return value['active'] is True

def tickerHasPrice(type, ticker):
    if type == 'spot':
        if ticker['ask'] is None or ticker['bid'] is None:
            return False
        return float(ticker['ask']) > 0 and float(ticker['bid']) > 0
    else:
        return True

def isUSDpair(quote):
    return 'USD' in quote

def isUSDBasePair(base):
    return 'USD' in base

def isSpotPair(type):
    return type == 'spot'

def orderBookPrice(side, orderBook):
    return orderBook[side][0][0]

def orderBookVolume(side, orderBook, orderBookDepth):
    
    price = 0
    totalVolume = 0
    orderBookLevel = 0
    
    # Calculate volume border price
    borderPrice = orderBook[side][0][0] * (1 + (orderBookDepth / 100))
    
    while price < borderPrice and orderBookLevel < len(orderBook[side]) - 1:
        
        price = orderBook[side][orderBookLevel][0]  # Pair base coin
        quantity = orderBook[side][orderBookLevel][1]  # Pair quote coin
        volume = price * quantity
        totalVolume += volume
                    
        orderBookLevel += 1
        
    return totalVolume
