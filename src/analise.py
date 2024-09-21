import pandas as pd
import numpy as np

class LimpezaDeDados:
    def __init__(self, dados):
        self.dados = dados

    def tratar_dados(self):
        try:
            # Limpar dados numéricos
            colunas_numericas = self.dados.select_dtypes(include=['int64', 'float64']).columns
            self.dados[colunas_numericas] = self.dados[colunas_numericas].fillna(0)

            # Limpar dados de texto
            colunas_texto = self.dados.select_dtypes(include=['object']).columns
            self.dados[colunas_texto] = self.dados[colunas_texto].replace({np.nan: None})

            # Limpar dados de data
            colunas_data = self.dados.select_dtypes(include=['datetime64[ns]']).columns
            self.dados[colunas_data] = self.dados[colunas_data].replace({pd.NaT: pd.to_datetime('1900-01-01')})

            # Remover colunas totalmente vazias
            self.dados = self.dados.dropna(how='all', axis=1)

            # Remover linhas onde a coluna 'ALUNO' está vazia ou contém valores inválidos
            coluna_aluno = 'NOME COMPLETO' if 'NOME COMPLETO' in self.dados.columns else 'ALUNO'
            self.dados = self.dados.dropna(subset=[coluna_aluno])
            self.dados = self.dados[self.dados[coluna_aluno].str.strip() != '']

            # Remover colunas que só têm valores zero
            self.dados = self.dados.loc[:, (self.dados != 0).any(axis=0)]

            return self.dados

        except KeyError as e:
            print(f'Erro ao processar dados: coluna {e} não encontrada.')
        except ValueError as e:
            print(f'Erro ao processar dados: {e}')
        except Exception as e:
            print(f'Erro inesperado ao processar dados: {e}')

    def verificar_pagamentos(self):
        # Identificar colunas relacionadas a pagamentos
        colunas_pagamentos = [col for col in self.dados.columns if "Unnamed" in col]

        # Verificar vencidos
        vencidos = self.dados[self.dados[colunas_pagamentos].apply(lambda x: 'V' in x.values, axis=1)]

        # Verificar pagadores em dia
        em_dia = self.dados[
            self.dados[colunas_pagamentos].apply(lambda x: 'V' not in x.values and 'P' in x.values, axis=1)
        ]

        coluna_aluno = 'NOME COMPLETO' if 'NOME COMPLETO' in self.dados.columns else 'ALUNO'

        return vencidos[[coluna_aluno] + colunas_pagamentos], em_dia[[coluna_aluno]]