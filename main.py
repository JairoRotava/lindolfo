import yfinance as yf
import bovespa
import pandas
import matplotlib. pyplot as plt 
from datetime import datetime, timedelta

# https://pypi.org/project/yfinance/
# https://aroussi.com/post/python-yahoo-finance
# https://tradologics.com/

#define the ticker symbol
#tickerSymbol = 'PETR4.SA'


#print(bovespa.get_value('PETR4.SA'))
#print(bovespa.get_value('BBAS3.SA'))
#print(bovespa.get_value('VALE3.SA'))

# get stock info
#petro = yf.Ticker('PETR4.SA')
#petro = yf.Ticker('ITUB4.SA')
# valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
#hist = petro.history(period='3mo')

#ax = plt.gca()
#hist.plot(y=['Close', 'High', 'Low', 'Close'], ax=ax)
#hist.plot(secondary_y=True, y='Volume', ax=ax)
#plt.show()

#print(hist)

acao = 'BBDC4'
opcoes = 'BBDCF'
data_vencimento_opcoes = '2020/16/01'
data_negociacao = datetime.today() - timedelta(days=1)

acao = bovespa.get_values(acao)
opcao = bovespa.get_values(opcoes, exact=False)

avaliacao= bovespa.process(acao, opcao, filter_date = data_negociacao)
ordenado = avaliacao.sort_values('lucro %', ascending=False)

print(ordenado[:10])

#print('Acao:\n', valor_acao)
# Separar ticker, descricao, data, valor
#
# print('Opcao:\n', valor_opcao)
# Separar ticker, descricao, valor vencimento, data vencimento, valor opcao
#print('Acao {}, opcao {}'.format(valor_acao,valor_opcao))

# Merge do valor da acao e opcoes.
# Calcular ganho anual, e oque mais?

