import time
from visualizar import visualizar_comparacao
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from processar import processar_planilha
import warnings

def carregar_planilhas(caminho_arquivo, planilhas):
    planilhas_carregadas = {}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # Ignorar os avisos temporariamente
        for planilha in planilhas:
            if planilha != 'SORTEIO':  # Ignorar a planilha sorteio
                try:
                    planilhas_carregadas[planilha] = pd.read_excel(caminho_arquivo, sheet_name=planilha, skiprows=1,
                                                                   index_col=None, na_values=['NA'])
                    print(f'Planilha {planilha} carregada com sucesso!')
                except Exception as e:
                    print(f'Erro ao carregar a planilha {planilha}: {e}')
                    planilhas_carregadas[planilha] = None
    return planilhas_carregadas


def main():
    inicio = time.time()

    caminho_arquivo = '../assets/dados/data_base.xlsx'

    planilhas_relevantes = [
        'ESTUDANTES', 'Forró', 'Baby Class A', 'Baby Class B', 'Ballet Infantil A', 'Ballet Infantil B',
        'Ballet Juvenil', 'Ballet Adulto', 'Jazz Adulto', 'JazzFunk A', 'JazzFunk B', 'KPOP A', 'KPOP B',
        'KPOP C', 'KPOP D', 'Ritmos', 'Forró II', 'Teatro Adulto', 'Stiletto III', 'Dança do Ventre'
    ]

    planilhas_carregadas = carregar_planilhas(caminho_arquivo, planilhas_relevantes)

    inadimplentes = {}
    pagadores_em_dia = []
    nao_classificados = []
    total_alunos = 0
    alunos_por_planilha = {}

    with ThreadPoolExecutor(max_workers=36) as executor:
        resultados = list(executor.map(lambda p: processar_planilha(p[0], p[1]), planilhas_carregadas.items()))

    for planilha, df_limpo, vencidos, em_dia in resultados:
        if df_limpo is not None:
            if planilha != 'ESTUDANTES':
                num_alunos = len(df_limpo)
                alunos_por_planilha[planilha] = num_alunos
                total_alunos += num_alunos

                if vencidos is not None and not vencidos.empty:
                    for index, row in vencidos.iterrows():
                        nome_aluno = row.get('NOME COMPLETO', row.get('ALUNO'))
                        key = (nome_aluno, planilha)
                        colunas_vencidos = [col for col in vencidos.columns if "Unnamed" in col and row[col] == 'V']

                        inadimplentes[key] = inadimplentes.get(key, 0) + len(colunas_vencidos)

                if em_dia is not None and not em_dia.empty:
                    for index, row in em_dia.iterrows():
                        nome_aluno = row.get('NOME COMPLETO', row.get('ALUNO'))
                        pagadores_em_dia.append((nome_aluno, planilha))

                # Alunos não classificados
                colunas_vencidos = [col for col in df_limpo.columns if "Unnamed" in col]
                nao_classificados_df = df_limpo[~df_limpo[colunas_vencidos].apply(lambda x: x.isin(['P', 'V']).any(), axis=1)]
                if not nao_classificados_df.empty:
                    for index, row in nao_classificados_df.iterrows():
                        nome_aluno = row.get('NOME COMPLETO', row.get('ALUNO'))
                        nao_classificados.append((nome_aluno, planilha))

    # Impressão dos resultados finais
    print("\nQuantidade de alunos por planilha:")
    for planilha, quantidade in alunos_por_planilha.items():
        print(f'{planilha}: {quantidade} alunos')

    print(f'\nTotal de alunos (excluindo ESTUDANTES): {total_alunos}')

    print("\nTotal de alunos inadimplentes:", len(inadimplentes))
    print("Alunos inadimplentes:")
    for aluno, aula in inadimplentes.keys():
        print(f'Nome: {aluno}, Aula: {aula}, Total de dívidas: {inadimplentes[(aluno, aula)]}')

    print("\nTotal de alunos com pagamento em dia:", len(pagadores_em_dia))
    print("Alunos com pagamento em dia:")
    for aluno, aula in pagadores_em_dia:
        print(f'Nome: {aluno}, Aula: {aula}')

    print("\nTotal de alunos não classificados:", len(nao_classificados))
    print("Alunos não classificados:")
    for aluno, aula in nao_classificados:
        print(f'Nome: {aluno}, Aula: {aula}')

    fim = time.time()
    tempo_total = fim - inicio
    print(f'\nTempo total de execução: {tempo_total:.2f} segundos')

    # Chama a função de visualização
    visualizar_comparacao(pagadores_em_dia, inadimplentes, nao_classificados)

if __name__ == "__main__":
    main()