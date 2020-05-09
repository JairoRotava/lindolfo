import pandas as pd
import numpy as np
import mplfinance as mpf
from bovespa.tradingindicator import TradingIndicator

class MACD(TradingIndicator):
    
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
