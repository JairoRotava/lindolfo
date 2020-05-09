from bovespa.tradingindicator import TradingIndicator
from bovespa.macd import MACD
import yfinance as yf
import pandas as pd
import numpy as np
import mplfinance as mpf
# https://github.com/matplotlib/mplfinance/blob/master/examples/addplot.ipynb

papel_acao = 'PETR4'
ticker = yf.Ticker( papel_acao + '.SA')
# valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
stock_hist = ticker.history(period='3mo')


#my_indicator = TradingIndicator(stock_hist)
#ind = my_indicator.get_indicator(12)
#action = my_indicator.get_action()
#profit = my_indicator.get_performance()

#print(my_indicator._action)
#TradingIndicator.show_graph(my_indicator)

macd = MACD(stock_hist)
macd.get_indicator()
macd.get_action()
macd.get_performance()
MACD.show_graph(macd)

#marcador_venda = my_indicator.get_sell_markers()
#marcador_compra = my_indicator.get_buy_markers()


#apds = [mpf.make_addplot(ind),
#        mpf.make_addplot(marcador_compra, scatter=True, markersize=200, marker='^'),
#        mpf.make_addplot(marcador_venda, scatter=True, markersize=200, marker='v'),
#       ]

#print(marcador_venda)

#mpf.plot(stock_hist, type ='candle', style='charles', mav=(20,50,200), volume=True, show_nontrading=True)
#print(action)
#print('Rendimento: {:.2f}%'.format(profit*100))
#mpf.plot(stock_hist, style='charles', volume=True, addplot=apds)
#mpf.plot(stock_hist, style='charles', volume=True)







