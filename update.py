import pandas as pd
from sqlalchemy import create_engine, inspect
import sqlite3
import re
from decouple import config

# Variáveis do arquivo .env
caminho_tabela = config('CAMINHO_TABELA')  # Caminho para o arquivo Excel
caminho_db = config('CAMINHO_DB')  # Caminho para o banco de dados SQLite

# Ler tabela
df = pd.read_excel(caminho_tabela)

# Removendo as linhas em branco
df = df.loc[~df['Unnamed: 0'].isnull()]

# Renomear colunas
new_column_names = {
    'Unnamed: 0': 'Plaqueta',
    'Unnamed: 1': 'Desc. Bem',
    'Unnamed: 8': 'Filial',
    'Unnamed: 9': 'Cód. Local',
    'Unnamed: 10': 'Desc. Local',
    'Unnamed: 13': 'Cód. Portador',
    'Unnamed: 15': 'Portador',
    'Unnamed: 17': 'Data últ. Loc',
    'Unnamed: 19': 'Cód. Fornecedor',
    'Unnamed: 21': 'Fornecedor',
    'Unnamed: 25': 'Documento',
    'Unnamed: 27': 'Data aquisição',
    'Unnamed: 28': 'Valor Aquisição',
    'Unnamed: 30': 'Cód. Bem',
    'Unnamed: 32': 'Série Fabricação',
    'Unnamed: 34': 'Cor',
    'Unnamed: 35': 'Espécie',
    'Unnamed: 37': 'Dep. Acumulado'
}
# Ler apenas as colunas desejadas
df = pd.read_excel(caminho_tabela, usecols=new_column_names.keys())

# Renomear as colunas
df.rename(columns=new_column_names, inplace=True)

# Conectar ao banco de dados SQLite
conn = sqlite3.connect(caminho_db)
cursor = conn.cursor()

# Verificar se a tabela já existe
inspector = inspect(create_engine(f'sqlite:///{caminho_db}'))
tabelas_existentes = inspector.get_table_names()

# Criar tabela se não existir
if "cadastro_patrimonio" not in tabelas_existentes:
    df.head(0).to_sql("cadastro_patrimonio", conn, if_exists='replace', index=False)

# Iterar pelas linhas do DataFrame
for index, row in df.iterrows():
    # Limpeza de dados
    for col in df.columns:
        if isinstance(row[col], str):
            row[col] = row[col].strip()  # Remove espaços extras

    # Tratamento específico da coluna valor aquisição.
    valor_aquisicao = str(row['Valor Aquisição']).replace(',', '.')
    valor_aquisicao = re.sub(r'[^\d\.]', '', valor_aquisicao)  # Remove caracteres não numéricos

    try:
        valor_aquisicao = float(valor_aquisicao)
    except ValueError:
        valor_aquisicao = 0

    # Verificar se a 'Plaqueta' já existe na tabela
    cursor.execute("SELECT COUNT(*) FROM cadastro_patrimonio WHERE Plaqueta = ?", (row['Plaqueta'],))
    count = cursor.fetchone()[0]

    try:
        if count > 0:
            # Atualizar a linha existente
            cursor.execute("""
                UPDATE cadastro_patrimonio
                SET
                    "Desc. Bem" = ?,
                    "Filial" = ?,
                    "Cód. Local" = ?,
                    "Desc. Local" = ?,
                    "Cód. Portador" = ?,
                    "Portador" = ?,
                    "Data últ. Loc" = ?,
                    "Cód. Fornecedor" = ?,
                    "Fornecedor" = ?,
                    "Documento" = ?,
                    "Data aquisição" = ?,
                    "Valor Aquisição" = ?,
                    "Cód. Bem" = ?,
                    "Série Fabricação" = ?,
                    "Cor" = ?,
                    "Espécie" = ?,
                    "Dep. Acumulado" = ?
                WHERE "Plaqueta" = ?
            """, (
                row['Desc. Bem'], row['Filial'], row['Cód. Local'], row['Desc. Local'], row['Cód. Portador'],
                row['Portador'], row['Data últ. Loc'], row['Cód. Fornecedor'], row['Fornecedor'],
                row['Documento'], row['Data aquisição'], valor_aquisicao, row['Cód. Bem'],
                row['Série Fabricação'], row['Cor'], row['Espécie'], row['Dep. Acumulado'], row['Plaqueta']
            ))
        else:
            # Inserir nova linha
            cursor.execute("""
                INSERT INTO cadastro_patrimonio (
                    Plaqueta, "Desc. Bem", Filial, "Cód. Local", "Desc. Local", "Cód. Portador", Portador,
                    "Data últ. Loc", "Cód. Fornecedor", Fornecedor, Documento, "Data aquisição",
                    "Valor Aquisição", "Cód. Bem", "Série Fabricação", Cor, Espécie, "Dep. Acumulado"
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['Plaqueta'], row['Desc. Bem'], row['Filial'], row['Cód. Local'], row['Desc. Local'],
                row['Cód. Portador'], row['Portador'], row['Data últ. Loc'], row['Cód. Fornecedor'],
                row['Fornecedor'], row['Documento'], row['Data aquisição'], valor_aquisicao,
                row['Cód. Bem'], row['Série Fabricação'], row['Cor'], row['Espécie'], row['Dep. Acumulado']
            ))
        print(f"Dados inseridos/atualizados: {row}")
    except sqlite3.OperationalError as e:
        print(f"Erro na linha {index}: {e}")
    except Exception as e:
        print(f"Erro inesperado na linha {index}: {e}")

conn.commit()  # Salvar mudanças

print("Processo concluído.")
conn.close()  # Fechar conexão com o banco de dados