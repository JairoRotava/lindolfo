import pandas as pd
import numpy as np
import mplfinance as mpf

class TradingIndicator(object):
    def __init__(self, history):
        self._stock = None
        self.set_stock(history)
        self._indicator = None
        self._action = None
        self._performance = None
    
    def get_stock(self):
        return self._stock

    def set_stock(self, history):
        self._stock = history
    
    def get_indicator(self, window_size=5):
        """
        A implementacao do indicador deve ser feita aqui
        """
        self._indicator = pd.DataFrame(self._stock['Close'].rolling(window_size).mean())
        return self._indicator

    def get_action(self):
        """
        Implementacao do algoritmo de tomada de descicao baseado nesse indicador
        """
        index = []
        action = []
        last_action = 'sell'
        for i, row in self._indicator.iterrows():
            # Buy
            if row[0] < 14.0 and last_action == 'sell':
                index.append(i)
                #action.append(['buy', self._stock.loc[i]['Close']])
                action.append(['buy'] + self._stock.loc[i].values.tolist())
                last_action = 'buy'
            # Sell
            elif row[0] > 17.0 and last_action == 'buy':
                index.append(i)
                #action.append(['sell', self._stock.loc[i]['Close']])
                action.append(['sell'] + self._stock.loc[i].values.tolist())
                last_action = 'sell'

        headers = ['Action'] + self._stock.columns.tolist()
        self._action = pd.DataFrame(action, index=index, columns=headers)
        return self._action

    def get_sell_markers(self):
        sell = self._action.loc[self._action['Action']=='sell']
        lenght = len(self._stock.index)
        markers = np.full(lenght, np.nan)
        for index, values in sell.iterrows():
            n = self._stock.index.get_loc(index)
            markers[n] = self._stock.loc[index]['High'] * 1.1
        return markers

    def get_buy_markers(self):
        sell = self._action.loc[self._action['Action']=='buy']
        lenght = len(self._stock.index)
        markers = np.full(lenght, np.nan)
        for index, values in sell.iterrows():
            n = self._stock.index.get_loc(index)
            markers[n] = self._stock.loc[index]['Low'] * 0.9
        return markers

    def get_performance(self):
        # Calcula ganho financeiro seguindo essa estrategia
        profit = 0
        sell_value = 0
        buy_value = 0
        last_action = 'sell'
        for i, row in self._action.iterrows():
            act = row['Action']
            if act == 'buy' and last_action == 'sell':
                buy_value = self._stock.loc[i]['Close']
                last_action = 'buy'
            elif act == 'sell' and last_action == 'buy':
                sell_value = self._stock.loc[i]['Close']
                last_action = 'sell'
                profit += (sell_value - buy_value)/buy_value
            
        if last_action == 'buy':
            sell_value = self._stock.iloc[-1]['Close']
            profit += (sell_value - buy_value)/buy_value
        return profit
    
    @staticmethod
    def show_graph(my_indicator):
        #my_indicator.get_indicator()
        #action = my_indicator.get_action()
        #profit = my_indicator.get_performance()
        
        #print('Rendimento: {:.2f}%'.format(profit*100))
        
        marcador_venda = my_indicator.get_sell_markers()
        marcador_compra = my_indicator.get_buy_markers()
        apds = [mpf.make_addplot(my_indicator._indicator),
                mpf.make_addplot(marcador_compra, scatter=True, markersize=200, marker='^'),
                mpf.make_addplot(marcador_venda, scatter=True, markersize=200, marker='v'),
            ]
        mpf.plot(my_indicator._stock, style='charles', volume=True, addplot=apds)
