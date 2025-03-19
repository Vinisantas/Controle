
import streamlit as st
import pandas as pd
import locale
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
import sqlite3

# Configurações da página
st.set_page_config(layout="wide", page_title="Controle")

# Seleção da página
escolha = st.sidebar.selectbox("Escolha uma página", ["Consulta Patrimonio"])

# Função para carregar o DataFrame
@st.cache_data()
def carregar_dataframe():  
    # Configurar a conexão com o banco de dados SQLite cadastro_patrimonio.sqlite
    caminho_db = 'cadastro_patrimonio.sqlite'
    conn = sqlite3.connect(caminho_db)

    query = """
        SELECT Plaqueta, "Desc. Bem", Filial,
        "Desc. Local", Portador, "Data últ. Loc", Fornecedor,
        Documento, "Data Aquisição", "Valor Aquisição",
        "Cód. Bem", "Série Fabricação"
        FROM 
            cadastro_patrimonio
        WHERE 
            Plaqueta <> 0 
            
        ORDER BY 
            Plaqueta DESC;
    """

    # Ler dados diretamente para um DataFrame do pandas
    df_patrimonio = pd.read_sql_query(query, conn)
    
    # Fechar a conexão
    conn.close()
    
    # Converter as colunas para os tipos apropriados
    df_patrimonio['Plaqueta'] = df_patrimonio['Plaqueta'].astype(float).astype(int, errors='ignore').apply(lambda x: str(x).zfill(6) if pd.notnull(x) else "")
    df_patrimonio['Desc. Bem'] = df_patrimonio['Desc. Bem'].astype(str)
    df_patrimonio['Filial'] = df_patrimonio['Filial'].astype(str)
    df_patrimonio['Desc. Local'] = df_patrimonio['Desc. Local'].astype(str)
    df_patrimonio['Portador'] = df_patrimonio['Portador'].astype(str)
    df_patrimonio['Fornecedor'] = df_patrimonio['Fornecedor'].astype(str)
    df_patrimonio['Documento'] = df_patrimonio['Documento'].astype(str)
    df_patrimonio['Cód. Bem'] = df_patrimonio['Cód. Bem'].astype(str)
    df_patrimonio['Série Fabricação'] = df_patrimonio['Série Fabricação'].astype(str)
    
    # Data atual
    data_atual = datetime.now()

    # Converter a coluna para datetime, se ainda não tiver sido feito
    df_patrimonio['Data aquisição'] = pd.to_datetime(df_patrimonio['Data aquisição'], format='%d/%m/%Y')

    # Calcular a idade em anos
    df_patrimonio['idade'] = (data_atual - df_patrimonio['Data aquisição']).dt.days / 365.25
    df_patrimonio['idade'] = df_patrimonio['idade'].round(2)

    # Substituir valores NaN em 'idade' por zero
    df_patrimonio['idade'] = df_patrimonio['idade'].fillna(0 )
    # Converter a coluna para datetime, se ainda não tiver sido feito
    df_patrimonio['Data aquisição'] = df_patrimonio['Data aquisição'].dt.strftime('%d/%m/%Y')
    
    # Converter a coluna 'Documento' para float e depois para int, lidando com valores nulos
    df_patrimonio['Documento'] = df_patrimonio['Documento'].apply(lambda x: int(float(x)) if pd.notnull(x) and x != '' else 0)

    return df_patrimonio

# Função para formatar valores em moeda local
def format_currency(value):
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        return locale.currency(value, grouping=True)
    except locale.Error as e:
        st.error(f"Erro ao configurar locale: {e}")
        return value

#pagina 1 
if escolha == "Consulta Patrimonio":
    st.title("Consulta Patrimonio")
    
    # # Forçar atualização dos dados
    # if st.button('Atualizar Dados'):
    #     st.cache_data.clear()  # Limpar o cache
    #     st.write("Cache limpo, dados serão recarregados.")
    
    # Carregar o dataframe
    df = carregar_dataframe()
        
    # Quebra de linha
    st.header(" ")
   
    # Campos consultas
    filtro = st.text_input("Consultar Plaqueta ou Descrição")
    filtro = filtro.strip().upper()
    idade_min, idade_max = st.slider('Selecionar faixa de idade', min_value=int(df['idade'].min()), max_value=int(df['idade'].max()), value=(int(df['idade'].min()), int(df['idade'].max())))
    df['Selecionar'] = False
    # Desabilitar a edição de todas as colunas, exceto a última
    disabled_columns = df.columns[:-1].tolist()    
    if filtro or idade_min or idade_max:
        df_filtrado = df[(df['Plaqueta'].str.contains(filtro, case=False) | df['Desc. Bem'].str.contains(filtro, case=False)) & 
                        (df['idade'] >= idade_min) & 
                        (df['idade'] <= idade_max)]
        
        if not df_filtrado.empty:
            st.data_editor(df_filtrado, column_config={"Selecionar": st.column_config.CheckboxColumn(
                "Selecionar",
                default=True
            )},  disabled=disabled_columns ,use_container_width=True, hide_index=True)
        else:
            st.header("Produto não encontrado!")
    else:
        st.text("Por favor, insira um filtro ou intervalo de idade.")


# # Página 2
# if escolha == "Dashboard descarte":
#     # Função para ler o arquivo excel
#     def load_excel(file_path, sheet_name="Grupo"):
#         if Path(file_path).exists():
#             return pd.read_excel(file_path, sheet_name=sheet_name)
#         else:
#             st.error(f"Arquivo {file_path} não encontrado!")
#             return None

#     # Função para plotar gráfico de pizza
#     def plot_pie_chart(data, labels):
#         fig, ax = plt.subplots()
#         ax.pie(data, labels=labels, autopct='%1.1f%%', startangle=140)
#         return fig

#     # Função para plotar gráfico de barras
#     def plot_bar_chart(df_pompeia, df_gang):
#         merged_df = pd.merge(df_pompeia, df_gang, on='Categoria', suffixes=('_pompeia', '_gang'))
#         y = range(len(merged_df))
        
#         fig, ax = plt.subplots(figsize=(10, 14))
#         ax.barh(y, merged_df['Quantidade_pompeia'], color='orange', alpha=0.6, label='Pompeia')
#         ax.barh(y, merged_df['Quantidade_gang'], color='blue', alpha=0.6, left=merged_df['Quantidade_pompeia'], label='Gang')
        
#         ax.set_yticks(y)
#         ax.set_yticklabels(merged_df['Categoria'])
#         ax.set_xlabel('Quantidade')
#         ax.legend()

#         for i in y:
#             ax.text(merged_df['Quantidade_pompeia'][i] / 2, i, str(merged_df['Quantidade_pompeia'][i]), va='center', ha='center', color='white')
#             ax.text(merged_df['Quantidade_pompeia'][i] + merged_df['Quantidade_gang'][i] / 2, i, str(merged_df['Quantidade_gang'][i]), va='center', ha='center', color='white')

#         return fig

#     # CSS customizado
#     st.markdown("""
#         <style>
#         .big-font {
#             font-size:25px !important;
#             text-align: center;
#         }
#         </style>
#     """, unsafe_allow_html=True)

#     # Caminho do arquivo Excel
#     path_excel = r"C:\Users\usuario\Downloads\Relatório Descarte.xlsx"
#     df = load_excel(path_excel)  # Utilizando a função load_excel

#     if df is not None:
#         df['DEFEITO'] = df['DEFEITO'].fillna("NÃO CLASSIFICADOS")
#         df['Filial'] = df['Filial'].apply(int)
#         df['Marca'] = df['Filial'].apply(lambda x: 'Pompeia' if 1 <= x <= 1000 else 'Gang')
#         df['Data aquisição'] = pd.to_datetime(df['Data aquisição'],format='%d/%m/%Y') 
#         df['Data aquisição'] = pd.to_datetime(df['Data aquisição']).dt.strftime('%d/%m/%Y')
#         df = df.fillna(0)
#         # Data atual
#         data_atual = datetime.now()
#         # Converter a coluna para datetime
#         df['Data aquisição'] = pd.to_datetime(df['Data aquisição'], format='%d/%m/%Y')
        
#         # Calcular a idade em anos
#         df['idade'] = (data_atual - df['Data aquisição']).dt.days / 365.25

#         # Arredondar a idade para duas casas decimais
#         df['idade'] = df['idade'].round(0).astype(int)

#         # Converter a coluna portador para garantir a serelização do dataframe
#         df['Portador'] = df['Portador'].astype(str)
#         df['Fornecedor'] = df['Fornecedor'].astype(str)
#         df['TECNICO'] = df['TECNICO'].astype(str)


#         df = df.sort_values(by=['idade'])


#         total_itens = df['Filial'].count()
#         valor_total = df['Valor Aquisição'].sum().round(2)
#         valor_total_formatado = format_currency(valor_total)
        
#         valor_total_pompeia = df[df['Marca'] == 'Pompeia']['Valor Aquisição'].sum()
#         valor_total_pompeia_formatado = format_currency(valor_total_pompeia)
        
#         valor_total_gang = df[df['Marca'] == 'Gang']['Valor Aquisição'].sum()
#         valor_total_gang_formatado = format_currency(valor_total_gang)
        
#         st.title("Relatório de descarte")
#         col1, col2, col3 = st.columns(3)
        
#         col1.metric('Valor total acumulado', valor_total_formatado)
#         col2.metric('Valor total acumulado Pompeia', valor_total_pompeia_formatado, valor_total_pompeia.round(2))
#         col3.metric('Valor total acumulado Gang', valor_total_gang_formatado, valor_total_gang.round(2), delta_color="inverse")

#         col9, col10, col11 = st.columns(3)
#         st.header("",divider='red')

#         col9.metric('Total Itens', df['Categoria'].count())
#         col10.metric("Idade média dos itens Grupo",df['idade'].mean().round().astype(int))

#         valor_medio_aquisicao = df['Valor Aquisição'].mean().round(2)
#         valor_medio_aquisicao = locale.currency(valor_medio_aquisicao, grouping=True)
#         col11.metric("Valor médio aquisição Grupo",valor_medio_aquisicao)

#         col6, col7, col8 = st.columns(3)


#         # Usando Markdown para adicionar quebra de linha
#         st.markdown("\n")
#         st.markdown("\n")
        
#         # Pagina 01 
#         col4, col5 = st.columns(2)

#         classificar = df.groupby('Marca').size().reset_index(name='Quantidade')
#         col4.markdown('<p class="big-font">Distribuição por Marca</p>', unsafe_allow_html=True)
#         fig_pizza = plot_pie_chart(classificar['Quantidade'], classificar['Marca'])
#         col4.pyplot(fig_pizza)
        
#         df_pompeia = df[df['Marca'] == 'Pompeia'].groupby(['Categoria']).size().reset_index(name='Quantidade')
#         df_gang = df[df['Marca'] == 'Gang'].groupby(['Categoria']).size().reset_index(name='Quantidade')
        
#         col5.markdown('<p class="big-font">Comparação de Quantidades por Categoria</p>', unsafe_allow_html=True)
#         fig_barras = plot_bar_chart(df_pompeia, df_gang)
#         col5.pyplot(fig_barras)

#         st.title("Levantamento de descarte")

#         st.header("Itens para Descarte", divider='red')
#         # Obter os itens únicos da coluna 'Categoria'
#         itens_para_descarte = df['Categoria'].unique()
#         # Ordenar os itens
#         itens_para_descarte = sorted(itens_para_descarte)

#         # Criar quatro colunas
#         col1, col2, col3, col4 = st.columns(4)

#         # Distribuir os itens nas colunas
#         colunas = [col1, col2, col3, col4]
#         for i, item in enumerate(itens_para_descarte):
#             colunas[i % 4].text(item)

#         st.header("Tempo de uso (anos)", divider='red')
#         # Supondo que df seja o seu DataFrame
#         idades_unicas = df['idade'].unique()
#         col1, col2, col3, col4 = st.columns(4)

#         # Distribuir os itens nas colunas
#         colunas = [col1, col2, col3, col4]
#         for i, idade in enumerate(idades_unicas):
#             colunas[i % 4].text(idade)

#         # Adicionando a barra de pesquisa
#         search_term = st.text_input("Pesquisar por Descrição", "")
#         # Filtrando o DataFrame com base no texto de pesquisa
#         filtered_df = df[df['Desc. Bem'].str.contains(search_term, case=False)]
#         # Verificar se há resultados


#         if len(filtered_df) > 0:
#             st.title("Resultado da Pesquisa")
#             # Calculate the minimum and maximum values of the 'idade' column
#             min_idade = min(df['idade'])
#             max_idade = max(df['idade'])

#             # Display the DataFrame with background gradient
#             st.dataframe(filtered_df.style.background_gradient(axis=0, cmap='RdYlGn',
#                                     vmin=min_idade, vmax=max_idade, gmap=df['idade']),hide_index=True)
#         else:
#             st.title("Nenhum resultado encontrado")

    
#     else:
#         st.error("DataFrame não foi carregado corretamente.")




