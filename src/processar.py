import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import time

inicio = time.time()

# carregar o arquivo
caminho_arquivo = 'c:/Users/Lipe&Gra/.vscode/Projetos/BIG_DATA/assets/dados/db1.xlsx'

# planilhas relevantes
planilhas_relevantes = {
    'ESTUDANTES': None,
    'Forró': None, 'Baby Class A': None, 'Baby Class B': None, 'Ballet Infantil A': None, 
    'Ballet Infantil B': None, 'Ballet Juvenil': None, 'Ballet Adulto': None, 'Jazz Adulto': None, 
    'JazzFunk A': None, 'JazzFunk B': None, 'KPOP A': None, 'KPOP B': None, 'KPOP C': None, 
    'KPOP D': None, 'Ritmos': None, 'Forró II': None, 'Teatro Adulto': None, 
    'Stiletto III': None, 'Dança do Ventre': None
}

# Carregar cada planilha e armazenar no dicionário
for planilha in planilhas_relevantes.keys():
    try:
        planilhas_relevantes[planilha] = pd.read_excel(caminho_arquivo, sheet_name=planilha, skiprows=1, index_col=None, na_values=['NA'])
        print(f'Planilha {planilha} carregada com sucesso!')
    except Exception as e:
        print(f'Erro ao carregar a planilha {planilha}: {e}')

class LimpezaDeDados:

    def __init__(self, dados):
        self.dados = dados
  
    def tratar_dados(self):
        try:
            # Tratar colunas numéricas
            colunas_numericas = self.dados.select_dtypes(include=['int64', 'float64']).columns
            self.dados[colunas_numericas] = self.dados[colunas_numericas].fillna(0)
      
            # Tratar colunas de texto
            colunas_texto = self.dados.select_dtypes(include=['object']).columns
            self.dados[colunas_texto] = self.dados[colunas_texto].replace({np.nan: None}) 

            # Tratar colunas de datas
            colunas_data = self.dados.select_dtypes(include=['datetime64[ns]']).columns
            self.dados[colunas_data] = self.dados[colunas_data].replace({pd.NaT: pd.to_datetime('1900-01-01')})

            # Remover colunas vazias
            self.dados = self.dados.dropna(how='all', axis=1)
            self.dados = self.dados.loc[:, (self.dados != 0).any(axis=0)]

            return self.dados

        except KeyError as e:
            print(f'Erro ao processar dados: coluna {e} não encontrada.')
        except ValueError as e:
            print(f'Erro ao processar dados: {e}')
        except Exception as e:
            print(f'Erro inesperado ao processar dados: {e}')


# Função para aplicar a limpeza de dados em uma planilha
def processar_planilha(planilha, df):
    if df is not None:
        try:
            limpeza = LimpezaDeDados(df)
            return planilha, limpeza.tratar_dados()
        except Exception as e:
            print(f'Erro ao processar a planilha {planilha}: {e}')
            return planilha, None
    return planilha, None

# Utilizar ThreadPoolExecutor para paralelizar o processamento das planilhas
with ThreadPoolExecutor() as executor:
    resultados = list(executor.map(lambda p: processar_planilha(p[0], p[1]), planilhas_relevantes.items()))

# Atualizar o dicionário com os dados tratados
planilhas_relevantes = dict(resultados)

# Printar as primeiras linhas de todos os DataFrames tratados
for planilha, df in planilhas_relevantes.items():
    if df is not None:
        print(f'\nPlanilha {planilha}:')
        print(df.head())


fim = time.time()
tempo_total= fim - inicio
print(f'\nTempo total de execução: {tempo_total:.2f} segundos')
