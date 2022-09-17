def isSpotPair(value):
    if ':' not in value:
        return True    


def isActiveMarket(value):
    return value['active'] is True


def tickerHasPrice(ticker):
    if ticker['ask'] is None or ticker['bid'] is None:
        return False
    return float(ticker['ask']) > 0 and float(ticker['bid']) > 0
