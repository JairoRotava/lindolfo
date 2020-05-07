#import yfinance as yf
import urllib
import pandas as pd
from datetime import datetime, timedelta
import re
import logging

logger = logging.getLogger(__name__)



# Wrapper para yfinance, que pega dados do Yahoo finance. Olhar lá quais são os nome utilizados, geralmente
# são os mesmo que na bovespa com .SA no final

#def get_value(tickerSymbol):
#    tickerData = yf.Ticker(tickerSymbol)
#    value = tickerData.info['ask']
#    return value

def get_values(ticker, exact=True):
    """
    Pega valores das acoes e opcoes
    Pode retronar mais de uma linha com nomes parecidos

    exact=True: quando true retorna somente ticker exatamente iguais
    """
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

    if not exact:
        return df
    
    df = df.loc[df['Papel']==ticker]
    return df


def process(acao, opcao, filter_type=True, filter_date=None):
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

    df = pd.DataFrame(columns=['acao', 'tipo acao', 'valor acao','opcao', 'tipo_opcao', 'data negociacao', 'valor opcao','strike', 'volume', 'lucro %'])
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


        valor_opcao = row['Último']        
        volume_opcao = float(re.sub('\D','',row['R$']))
        if strike_opcao >= valor_acao:
            lucro = valor_opcao
        else:
            lucro = strike_opcao - valor_acao + valor_opcao
        p_lucro = (lucro / valor_acao) * 100

        #df = pd.DataFrame({'acao':[nome_acao], 'valor acao':[valor_acao], 'opcao':[nome_opcao], 'valor opcao':[valor_opcao],                    'strike':strike_opcao, 'lucro %':p_lucro})
        df.loc[index] = [nome_acao + ' ' + ' '.join(descricao_acao), tipo_acao, valor_acao, nome_opcao + ' ' + ' '.join(descricao_opcao), tipo_opcao, 
            data.strftime('%d/%m'), valor_opcao,strike_opcao, volume_opcao, p_lucro]
 
    return df