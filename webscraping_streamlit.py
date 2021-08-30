# WebScraping e Análise de Dados com Python
# Desenvolvido por Lucas Souza Oliveira Mendonça

import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import base64
import numpy as np
import seaborn as sns


@st.cache
# Função para WebScraping
def scrap_data(estado: str) -> dict:
    url = f'https://www.ibge.gov.br/cidades-e-estados/{estado}.html'
    page = requests.get(url)
    bscontent = BeautifulSoup(page.content, 'html.parser')
    classe = bscontent.select('.indicador')

    estado_dict = {
        ind.select('.ind-label')[0].text: ind.select('.ind-value')[0].text
        for ind in classe
    }
    estado_dict['Estado'] = estado

    return estado_dict


# Função para baixar dataframe
def get_table_download_link(df, filename='dataframe', format='csv', msg="Download csv File",
                            header=True, index=True, index_label='index', sep='\t',
                            na_rep='*', decimal='.'):
    csv = df.to_csv(header=header, index=index, index_label=index_label, sep=sep,
                    na_rep=na_rep, decimal=decimal)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.{format}">{msg}</a>'
    return href


# Função para rodar a ferramenta com o streamlit
def scraping_streamlit():
    st.title('Análise de dados dos estados do Brasil')
    st.markdown("""
    Ferramenta simples de WebScraping para análise de dados do IBGE.
    * **Bibliotecas usadas:** pandas, streamlit, beautifulsoup, numpy, seaborn, matplotlib, requests e base64. 
    * **Fonte de dados:** [ibge.gov.br/cidades-e-estados.html](https://www.ibge.gov.br/cidades-e-estados.html)
    """)
    st.header('Tabela de dados')

    estados = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO',
               'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI',
               'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']

    # Aplicar todos os estados na função de WebScraping por meio de list comprehension.
    dados_estados = [scrap_data(estado) for estado in estados]

    # Montar o dataframe e depois tratar os dados.
    df = pd.DataFrame(dados_estados)
    df_tratado = df.copy()
    # Renomeando e reorganizando as colunas para facilitar a nossa vida.
    df_tratado.columns = ['governador', 'capital', 'gentilico', 'area', 'populacao', 'densidade_demografica',
                          'matriculas_escola_fund.', 'idh', 'receitas', 'despesas', 'rendimento_per_capita',
                          'total_veiculos', 'uf']
    df_tratado = df_tratado[['uf', 'governador', 'capital', 'gentilico', 'area', 'populacao',
                             'densidade_demografica', 'matriculas_escola_fund.', 'idh', 'receitas',
                             'despesas', 'rendimento_per_capita', 'total_veiculos']]
    # Removendo textos desnecssários das tabelas.
    df_tratado = df_tratado.replace({
        ' pessoas': '',
        ' matrículas': '',
        '\.': '',
        ',': '.',
        ' km²': '',
        '\[\d+\]': '',
        'R\$.*': '',
        ' veículos': '',
        ' hab/km²': ''
    }, regex=True)

    # Convertendo as colunas numéricas para tipos numéricos.
    colun_num = ['area', 'populacao', 'densidade_demografica', 'matriculas_escola_fund.', 'idh',
                 'receitas', 'despesas', 'rendimento_per_capita', 'total_veiculos']
    df_tratado[colun_num] = df_tratado[colun_num].apply(lambda x: x.str.strip())
    df_tratado[colun_num] = df_tratado[colun_num].apply(pd.to_numeric)

    # Mostrar o dataframe no streamlit.
    st.dataframe(df_tratado)
    # Donwload do dataframe em CSV.
    link_table = get_table_download_link(df_tratado, 'df_estados',
                                         msg='Download dos dados')
    st.markdown(link_table, unsafe_allow_html=True)

    # Botões para gerar análises dos dados
    if st.button('Intercorrelação por Heatmap'):
        corr = df_tratado.corr()
        mask = np.zeros_like(corr)
        mask[np.triu_indices_from(mask)] = True
        with sns.axes_style("white"):
            fig, ax = plt.subplots(figsize=(7, 5))
            ax = sns.heatmap(corr, mask=mask, vmax=1, square=True)
        st.pyplot(fig)
    if st.button('Dispersão - IDH por Rendimento per capita'):
        fig = plt.figure(figsize=(7, 4))
        plt.scatter(df_tratado['rendimento_per_capita'], df_tratado['idh'])
        plt.title('Gráfico de Dispersão - IDH por Rendimento per capita')
        plt.xlabel('Rendimento per capita')
        plt.ylabel('IDH')
        st.pyplot(fig)
    if st.button('Dispersão - IDH por Matriculas no ensino fundamental'):
        fig = plt.figure(figsize=(7, 4))
        plt.scatter(df_tratado['matriculas_escola_fund.'], df_tratado['idh'])
        plt.title('Gráfico de Dispersão - IDH por Matriculas no ensino fundamental')
        plt.xlabel('Matriculas no ensino fundamental')
        plt.ylabel('IDH')
        st.pyplot(fig)


if __name__ == "__main__":
    scraping_streamlit()
