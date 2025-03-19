import pandas as pd
from sqlalchemy import create_engine
import sqlite3
import re

# Função utilitária para tratar valores deflacionados e conversões
def tratar_valor(valor):
    if isinstance(valor, str):
        valor = valor.replace(',', '.')
        valor = re.sub(r'[^\d\.]', '', valor)
    try:
        return float(valor)
    except ValueError:
        return 0.0

# Função para criar ou conectar ao banco SQLite
def conectar_banco(caminho_db):
    engine = create_engine(f'sqlite:///{caminho_db}')
    conn = sqlite3.connect(caminho_db)
    return conn, engine

# Função para excluir a tabela inventario_adicional, se existir
def excluir_tabela_adicional(cursor):
    cursor.execute("DROP TABLE IF EXISTS inventario_adicional")

# Função para criar a tabela inventario_adicional com as colunas na ordem correta
def criar_tabela_adicional(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario_adicional (
            "Código" TEXT,
            "Descricao" TEXT,
            "Cód. Depósito" REAL,
            "Filial" TEXT,
            "Unidade" TEXT,
            "Qtde Estoque" REAL,
            "Custo" REAL,
            "Total Custo" REAL,
            UNIQUE("Código", "Descricao", "Cód. Depósito", "Filial")
        )
    """)

# Função principal para processar e carregar os dados
def processar_dados(nome_tabela, caminho_db):
    # Ler dados do Excel
    df = pd.read_excel(nome_tabela)

    # Remover linhas vazias
    df = df.dropna(how='all')

    # Renomear colunas
    new_column_names = {
        'Filial': 'Filial',
        'Cód. Depósito': 'Cód. Depósito',
        'Código': 'Código',
        'Descrição': 'Descricao',
        'Unidade': 'Unidade',
        'Custo': 'Custo',
        'Estoque': 'Estoque',
        'Total Custo': 'Total Custo',
    }
    df.rename(columns=new_column_names, inplace=True)

    # Tratar a coluna 'Cód. Depósito'
    df['Cód. Depósito'] = df['Cód. Depósito'].astype(str).str.strip().str.replace('.', '').str.replace(',', '.').astype(float)

    # Conectar ao banco
    conn, engine = conectar_banco(caminho_db)
    cursor = conn.cursor()

    # Excluir tabela inventario_adicional, se existir
    excluir_tabela_adicional(cursor)
    conn.commit()

    # Criar tabela inventario_adicional
    criar_tabela_adicional(cursor)
    conn.commit()

    # Contadores para monitoramento
    total_linhas = len(df)
    inseridos_adicional = 0
    nao_inseridos = []

    # Iterar pelas linhas do DataFrame
    for index, row in df.iterrows():
        # Tratar valores
        codigo = row['Código']
        descricao = row['Descricao'].strip()
        cod_deposito = row['Cód. Depósito']
        filial = row['Filial']
        unidade = row['Unidade']
        estoque = tratar_valor(row['Estoque'])
        custo = tratar_valor(row['Custo'])
        total_custo = tratar_valor(row['Total Custo'])

        try:
            # Inserir dados na tabela inventario_adicional
            cursor.execute("""
                INSERT OR IGNORE INTO inventario_adicional (
                    "Código",
                    "Descricao",
                    "Cód. Depósito",
                    "Filial",
                    "Unidade",
                    "Qtde Estoque",
                    "Custo",
                    "Total Custo"
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (codigo, descricao, cod_deposito, filial, unidade, estoque, custo, total_custo))

            if cursor.rowcount > 0:
                inseridos_adicional += 1
                print(f"Registro inserido em inventario_adicional: Código={codigo}, Descricao={descricao}, Cód. Depósito={cod_deposito}, Filial={filial}")
            else:
                nao_inseridos.append((codigo, descricao, cod_deposito, filial))

        except sqlite3.Error as e:
            print(f"Erro ao inserir registro na linha {index}: {e}")
            nao_inseridos.append((codigo, descricao, cod_deposito, filial))

    # Salvar alterações e fechar conexão
    conn.commit()
    conn.close()

    # Resumo do processo
    print("Processo concluído!")
    print(f"Total de linhas no arquivo: {total_linhas}")
    print(f"Registros inseridos na tabela inventario_adicional: {inseridos_adicional}")
    if nao_inseridos:
        print("Registros que não foram inseridos:")
        for item in nao_inseridos:
            print(f" - Código={item[0]}, Descricao={item[1]}, Cód. Depósito={item[2]}, Filial={item[3]}")

# Caminhos do arquivo e banco
nome_tabela = r"c:\vinícius senior\UsoConsumo.xlsx"
caminho_db = r"C:\Users\usuario\OneDrive\Desktop\App\Controle\Banco Dados\estoque.sqlite"

# Executar o processo
processar_dados(nome_tabela, caminho_db)