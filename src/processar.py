from analise import LimpezaDeDados

def processar_planilha(planilha, df):
    if df is not None:
        try:
            coluna_aluno = "NOME COMPLETO" if planilha == "ESTUDANTES" else "ALUNO"

            if coluna_aluno not in df.columns:
                raise KeyError(f"A coluna '{coluna_aluno}' não foi encontrada na planilha {planilha}")

            limpeza = LimpezaDeDados(df)
            df_limpo = limpeza.tratar_dados()
            vencidos, em_dia = limpeza.verificar_pagamentos()
            return planilha, df_limpo, vencidos, em_dia
        except Exception as e:
            print(f'Erro ao processar a planilha {planilha}: {e}')
            return planilha, None, None, None
    return planilha, None, None, None