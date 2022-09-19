def isSpotPair(value):
    if value['type'] == 'spot':
        return True
    
    if ':' not in value['symbol']:
        return True    

def isActiveMarket(value):
    return value['active'] is True


def tickerHasPrice(ticker):
    if ticker['ask'] is None or ticker['bid'] is None:
        return False
    return float(ticker['ask']) > 0 and float(ticker['bid']) > 0

def isUSDpair(quote):
    return 'USD' in quote

def isUSDBasePair(base):
    return 'USD' in base