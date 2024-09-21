import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk


def mostrar_aniversariantes():
    from src.main import carregar_planilhas

    caminho_arquivo = '../assets/dados/data_base.xlsx'

    planilha = ['ESTUDANTES']
    planilhas_carregadas = carregar_planilhas(caminho_arquivo, planilha)

    # Recupera os dados da planilha ESTUDANTES
    df_estudantes = planilhas_carregadas.get('ESTUDANTES')

    if df_estudantes is not None:
        # Filtrar colunas
        df_aniversariantes = df_estudantes[['NOME COMPLETO', 'DIA', 'MÊS']].dropna()

        # Converter a coluna MÊS para números inteiros
        df_aniversariantes['MÊS'] = df_aniversariantes['MÊS'].astype(int)
        df_aniversariantes['DIA'] = df_aniversariantes['DIA'].astype(int)

        # Ordenar por mês e dia
        df_aniversariantes = df_aniversariantes.sort_values(by=['MÊS', 'DIA'])

        # Criar uma nova janela para mostrar os aniversariantes
        janela_aniversariantes = tk.Toplevel()
        janela_aniversariantes.title("Aniversariantes")
        janela_aniversariantes.geometry("400x600")

        # Criar um canvas e uma scrollbar
        canvas = tk.Canvas(janela_aniversariantes)
        scrollbar = tk.Scrollbar(janela_aniversariantes, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Criar um frame dentro do canvas
        frame = tk.Frame(canvas)

        # Adicionar o frame ao canvas
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Atualizar a região de rolagem do canvas
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        frame.bind("<Configure>", on_frame_configure)

        # Agrupar por mês
        meses = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
            7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }

        for mes, alunos in df_aniversariantes.groupby('MÊS'):
            # Adicionar rótulo do mês
            label_mes = tk.Label(frame, text=meses.get(mes, "Mês Desconhecido"), font=("Helvetica", 12, "bold"))
            label_mes.pack(padx=10, pady=5)

            # Adicionar alunos do mês
            for _, row in alunos.iterrows():
                aluno_texto = f"Dia {int(row['DIA'])}: {row['NOME COMPLETO']}"
                label_aluno = tk.Label(frame, text=aluno_texto, font=("Helvetica", 10))
                label_aluno.pack(padx=10, pady=2)

    else:
        # Caso a planilha estudantes não esteja carregada
        janela_erro = tk.Toplevel()
        janela_erro.title("Erro")
        label_erro = tk.Label(janela_erro, text="Planilha 'ESTUDANTES' não carregada!", font=("Helvetica", 12, "bold"))
        label_erro.pack(padx=20, pady=20)



def visualizar_comparacao(pagadores_em_dia, inadimplentes, nao_classificados):
    # janela principal
    root = tk.Tk()
    root.title("Comparação de Alunos")
    root.geometry("1100x600")

    # frame principal
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # canvas e uma barra de rolagem
    canvas = tk.Canvas(main_frame)
    scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Botão aniversariantes
    btn_frame = ttk.Frame(root)  # Frame para o botão
    btn_frame.pack(side=tk.TOP, anchor='ne', padx=30, pady=30)

    btn_aniversariantes = ttk.Button(btn_frame, text="Aniversariantes", command=mostrar_aniversariantes, width=20, style='TButton')

    btn_aniversariantes.pack()

    # Configuração do estilo do botão
    style = ttk.Style()
    style.configure('TButton', font=('Helvetica', 16))

    # Quantidade de cada categoria
    categorias = {
        "Alunos em Dia": len(pagadores_em_dia),
        "Inadimplentes": len(inadimplentes),
        "Não Classificados": len(nao_classificados)
    }

    # gráfico de pizza
    fig_pizza, ax_pizza = plt.subplots(figsize=(6.5, 5))
    labels = categorias.keys()
    sizes = categorias.values()
    colors = ['#4CAF50', '#F44336', '#FFC107']
    ax_pizza.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    ax_pizza.set_title('Comparação de Alunos')

    # gráfico de barras
    fig_bar, ax_bar = plt.subplots(figsize=(12, 6))
    bar_width = 0.35
    index = range(len(set([aula for (_, aula) in pagadores_em_dia] + [aula for (_, aula) in inadimplentes])))

    # Contabilizando os inadimplentes e pagantes por aula
    aulas_inadimplentes = {}
    aulas_pagantes = {}

    for (_, aula), _ in inadimplentes.items():
        aulas_inadimplentes[aula] = aulas_inadimplentes.get(aula, 0) + 1

    for _, aula in pagadores_em_dia:
        aulas_pagantes[aula] = aulas_pagantes.get(aula, 0) + 1

    todas_aulas = set(aulas_inadimplentes.keys()).union(aulas_pagantes.keys())
    aulas_nomes = sorted(list(todas_aulas))

    qtd_inadimplentes = [aulas_inadimplentes.get(aula, 0) for aula in aulas_nomes]
    qtd_pagantes = [aulas_pagantes.get(aula, 0) for aula in aulas_nomes]

    ax_bar.barh([i - bar_width / 2 for i in index], qtd_inadimplentes, bar_width, label='Inadimplentes',
                color='#F44336')
    ax_bar.barh([i + bar_width / 2 for i in index], qtd_pagantes, bar_width, label='Alunos em Dia', color='#4CAF50')

    ax_bar.set_xlabel('Quantidade de Alunos')
    ax_bar.set_ylabel('Aulas de Dança')
    ax_bar.set_title('Comparação de Alunos Inadimplentes e Alunos Pagadores por Aula')
    ax_bar.set_yticks(index)
    ax_bar.set_yticklabels(aulas_nomes)
    ax_bar.legend()

    # grid para posicionar os gráficos lado a lado
    scrollable_frame.grid_columnconfigure(0, weight=1)
    scrollable_frame.grid_columnconfigure(1, weight=1)

    # Embutir o gráfico de pizza no Tkinter
    canvas_pizza = FigureCanvasTkAgg(fig_pizza, master=scrollable_frame)
    canvas_pizza.draw()
    canvas_pizza.get_tk_widget().grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

    # Embutir o gráfico de barras no Tkinter
    canvas_bar = FigureCanvasTkAgg(fig_bar, master=scrollable_frame)
    canvas_bar.draw()
    canvas_bar.get_tk_widget().grid(row=0, column=1, padx=(10, 30), pady=10, sticky='nsew')

    # Adicionar as listas abaixo dos gráficos em colunas lado a lado
    ttk.Label(scrollable_frame, text="Alunos Inadimplentes", font=("Helvetica", 12, "bold")).grid(row=1, column=0,
                                                                                                  padx=10, pady=10,
                                                                                                  sticky='nsew')
    ttk.Label(scrollable_frame, text="Alunos com Pagamento em Dia", font=("Helvetica", 12, "bold")).grid(row=1,
                                                                                                         column=1,
                                                                                                         padx=10,
                                                                                                         pady=10,
                                                                                                         sticky='nsew')

    # Mostrar alunos inadimplentes
    inadimplentes_texto = "\n".join(
        [f"Nome: {aluno}, Aula: {aula}, Dívidas: {inadimplentes[(aluno, aula)]}" for (aluno, aula) in
         inadimplentes.keys()])
    ttk.Label(scrollable_frame, text=inadimplentes_texto).grid(row=2, column=0, padx=10, pady=10, sticky='nsew')

    # Mostrar alunos com pagamento em dia
    pagadores_texto = "\n".join([f"Nome: {aluno}, Aula: {aula}" for aluno, aula in pagadores_em_dia])
    ttk.Label(scrollable_frame, text=pagadores_texto).grid(row=2, column=1, padx=10, pady=10, sticky='nsew')

    # Mostrar alunos não classificados abaixo dos inadimplentes
    ttk.Label(scrollable_frame, text="Alunos Não Classificados", font=("Helvetica", 12, "bold")).grid(row=3, column=0,
                                                                                                      padx=10, pady=10,
                                                                                                      sticky='nsew')
    nao_classificados_texto = "\n".join([f"Nome: {aluno}, Aula: {aula}" for aluno, aula in nao_classificados])
    ttk.Label(scrollable_frame, text=nao_classificados_texto).grid(row=4, column=0, padx=10, pady=10, sticky='nsew')

    # Iniciar a interface
    root.mainloop()

