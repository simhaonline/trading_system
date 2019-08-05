# Documentation
# Kline interval date parser "1 day ago UTC"  https://dateparser.readthedocs.io/en/latest/
# Python-Binance master document  https://buildmedia.readthedocs.org/media/pdf/python-binance/latest/python-binance.pdf
# Python-Binance quick reference document     https://python-binance.readthedocs.io/en/latest/market_data.html#id6
# More useful information (quick reference)     https://python-binance.readthedocs.io/en/latest/binance.html

from ts_account import Account
from ts_trader import Trader
from ts_strategy import Strategy


pair = 'NEOBTC'
tick_size = "1d"
start = "1 Jan, 2018"
end = "now"


trader = Strategy(pair, tick_size, start, end)
#trader.ohlc(pair, tick_size, start, end)
#trader.rolling_avg()
