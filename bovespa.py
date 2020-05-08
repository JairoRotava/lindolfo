#import yfinance as yf
import urllib
import pandas as pd
from datetime import datetime, timedelta
import re
import logging
import yfinance as yf
import bovespa
import mplfinance as mpf
import ipywidgets as widgets

logger = logging.getLogger(__name__)



# Wrapper para yfinance, que pega dados do Yahoo finance. Olhar lá quais são os nome utilizados, geralmente
# são os mesmo que na bovespa com .SA no final

#def get_value(tickerSymbol):
#    tickerData = yf.Ticker(tickerSymbol)
#    value = tickerData.info['ask']
#    return value

def get_values(tickers, exact=True):
    """
    Pega valores das acoes e opcoes
    Pode retronar mais de uma linha com nomes parecidos

    exact=True: quando true retorna somente ticker exatamente iguais
    """

    if isinstance(tickers, str):
        tickers = [tickers]

    df_out = pd.DataFrame()
    if isinstance(tickers, list):
        for ticker in tickers:
            url = "http://www.tradergrafico.com/ajuda/ajuda.asp?pesq=" + ticker
            fp = urllib.request.urlopen(url)
            mybytes = fp.read()
            mystr = mybytes.decode('iso-8859-1')
            fp.close()

            start_string = '<h3>Cota&ccedil;&otilde;es</h3>'
            start = mystr.rfind(start_string)
            start = start + len(start_string)
            end_string = '</TABLE>'
            end = mystr.rfind(end_string) + len(end_string)
            table = mystr[start:end]

            df = pd.read_html(table, header=0, decimal=',', thousands='.')[0]

            # Pega somente papel exatamente com mesmo nome
            if exact:
                df = df.loc[df['Papel']==ticker]
            
            # Retorna qualquer coisa parecida
            df_out = pd.concat([df_out, df], axis=0)
            
    return df_out


def process(acao, opcao, expiration_lookup_table, filter_type=True, filter_date=None):
    """
    processa acao e opcao e verificando data, tipo e calcula o lucro
    """
    def find_type(description):
        if any('PN'==s for s in description):
            return('PN')
        elif any('ON'==s for s in description):
            return('ON')
        else:
            return('')

    nome_acao = acao.iloc[0]['Papel']
    valor_acao = acao.iloc[0]['Último']
    descricao_acao = acao.iloc[0]['Descrição'].split()
    tipo_acao = find_type(descricao_acao)
    #descricao_acao[1]

    df = pd.DataFrame(columns=['acao', 'tipo acao', 'valor acao','opcao', 'tipo_opcao', 'data negociacao', 
        'valor opcao','strike', 'data expiracao', 'volume', 'lucro %', 'lucro aa'])
    for index, row in opcao.iterrows():
        nome_opcao = row['Papel']
        descricao_opcao = row['Descrição'].split()
        strike_opcao = float(descricao_opcao[-1].replace(',','.'))
        tipo_opcao = find_type(descricao_opcao)

        # Ignora opcoes de tipos diferentes (PN e ON)
        # TODO: Muito sujeito a dar pau isso aqui
        if tipo_acao != tipo_opcao:
            logger.debug('Ignorando opcao {} {} devido tipo diferente'.format(nome_opcao,' '.join(descricao_opcao)))
            continue

        # Descarta opcoes de dias antigos
        data_hora = row['Data']
        data = datetime.strptime(data_hora,  "%d/%m\xa0%H:%M")
        #now = datetime.now()
        now = filter_date
        if filter_date is not None:
            if data.month != now.month or data.day != now.day:
                logger.debug('Ignorando opcao {} {} devido data antiga'.format(nome_opcao,' '.join(descricao_opcao)))
                continue

        data_expiracao = option_expiration(nome_opcao, expiration_lookup_table)
        valor_opcao = row['Último']        
        volume_opcao = float(re.sub('\D','',row['R$']))
        if strike_opcao >= valor_acao:
            lucro = valor_opcao
        else:
            lucro = strike_opcao - valor_acao + valor_opcao
        
        delta_days = data_expiracao.date() - datetime.today().date()
        delta_days = delta_days.days
        p_lucro = (lucro / valor_acao) * 100

        lucro_aa = p_lucro * 365/delta_days

        #df = pd.DataFrame({'acao':[nome_acao], 'valor acao':[valor_acao], 'opcao':[nome_opcao], 'valor opcao':[valor_opcao],                    'strike':strike_opcao, 'lucro %':p_lucro})
        df.loc[index] = [nome_acao + ' ' + ' '.join(descricao_acao), tipo_acao, valor_acao, nome_opcao + ' ' + ' '.join(descricao_opcao), tipo_opcao, 
            data.strftime('%d/%m'), valor_opcao, strike_opcao, data_expiracao.strftime('%d/%m'), volume_opcao, p_lucro, lucro_aa]
 
    return df


def option_expiration(option, expiration_lookup_table):
    for c in reversed(option):
        if c.isdigit():
            continue
        return(expiration_lookup_table[c])

def show_all(papel_acao, papel_opcao, tabela_vencimento_opcao):
    hoje = datetime.today()
    data_negociacao = hoje
    acao = get_values(papel_acao)
    opcao = get_values(papel_opcao, exact=False)
    aval_opcoes = process(acao, opcao, tabela_vencimento_opcao, filter_date = data_negociacao)
    opcoes_ordenadas_lucro = aval_opcoes.sort_values('lucro aa', ascending=False)
    ticker = yf.Ticker( papel_acao + '.SA')
    hist = ticker.history(period='3mo')
    intraday = ticker.history(period='1d', interval='5m')

    widget1 = widgets.Output()
    widget2 = widgets.Output()
    widget3 = widgets.Output()

    with widget1:
        mpf.plot(hist, type ='candle', style='charles', mav=(3,6,9), volume=True)
    with widget2:
        display(opcoes_ordenadas_lucro[:10])
    with widget3:
        # Pega ultimas 10 leituras
        display(intraday.tail(10)[::-1])

    # Coloca grafico lado a lado com ultimas cotacoes
    view = widgets.HBox([widget1, widget3])
    view_all = widgets.VBox([view, widget2])
    return view_all