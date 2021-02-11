import time

from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

from signals import client


def open_positions():
    positions = client.futures_position_information()
    messages = []
    for position in positions:
        if float(position['positionAmt']) > 0 or float(position['positionAmt']) < 0:
            pnl = (float(position['unRealizedProfit'])/((float(position['positionAmt'])*float(position['markPrice']))/int(position['leverage'])))*100
            message = f'''symbol: {position['symbol']}
positionAmt: {position['positionAmt']} ({position['leverage']}x)
entryPrice: {str(position['entryPrice'])[:10]}
markPrice: {str(position['markPrice'])[:10]}
unRealizedProfit: {str(position['unRealizedProfit'])[:5]} USDT ({str(pnl)[:5]}% ROE)
'''
            messages.append(message)
    return messages


def get_popular_coins():
    opts = Options()
    opts.headless = True
    assert opts.headless
    browser = Firefox(options=opts)
    browser.get('https://www.binance.com/en/markets')
    browser.find_elements_by_xpath("//*[contains(text(), 'Futures Markets')]")[1].click()
    time.sleep(2)
    vol_sort = browser.find_elements_by_xpath("//*[@class='css-1i04fkn']")[6]
    vol_sort.click()
    vol_sort.click()
    rows = browser.find_elements_by_xpath("//*[@class='css-4cffwv']")
    coins = [rows[i].text.split(' ')[0] for i in range(0, 30, 2)]
    return coins


if __name__ == '__main__':
    # print(get_popular_coins())
    print(open_positions())

ex = {'symbol': 'ETHBTC', 'status': 'TRADING', 'baseAsset': 'ETH', 'baseAssetPrecision': 8, 'quoteAsset': 'BTC',
      'quotePrecision': 8, 'quoteAssetPrecision': 8, 'baseCommissionPrecision': 8, 'quoteCommissionPrecision': 8,
      'orderTypes': ['LIMIT', 'LIMIT_MAKER', 'MARKET', 'STOP_LOSS_LIMIT', 'TAKE_PROFIT_LIMIT'], 'icebergAllowed': True,
      'ocoAllowed': True, 'quoteOrderQtyMarketAllowed': True, 'isSpotTradingAllowed': True,
      'isMarginTradingAllowed': True, 'filters': [
        {'filterType': 'PRICE_FILTER', 'minPrice': '0.00000100', 'maxPrice': '100000.00000000',
         'tickSize': '0.00000100'},
        {'filterType': 'PERCENT_PRICE', 'multiplierUp': '5', 'multiplierDown': '0.2', 'avgPriceMins': 5},
        {'filterType': 'LOT_SIZE', 'minQty': '0.00100000', 'maxQty': '100000.00000000', 'stepSize': '0.00100000'},
        {'filterType': 'MIN_NOTIONAL', 'minNotional': '0.00010000', 'applyToMarket': True, 'avgPriceMins': 5},
        {'filterType': 'ICEBERG_PARTS', 'limit': 10},
        {'filterType': 'MARKET_LOT_SIZE', 'minQty': '0.00000000', 'maxQty': '2729.13846842', 'stepSize': '0.00000000'},
        {'filterType': 'MAX_NUM_ORDERS', 'maxNumOrders': 200},
        {'filterType': 'MAX_NUM_ALGO_ORDERS', 'maxNumAlgoOrders': 5}], 'permissions': ['SPOT', 'MARGIN']}
