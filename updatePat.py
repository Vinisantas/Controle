import pandas as pd
from sqlalchemy import create_engine, inspect
import sqlite3

# Ler tabela
nome_tabela = r"c:\vinícius senior\SRV-APLArquivos$Pompeiateste.xlsx"
df = pd.read_excel(nome_tabela)

# Removendo as linhas em branco
df = df.loc[~df['Unnamed: 0'].isnull()]

# Drop todas as colunas vazias
# df.dropna(how='all', inplace=True, axis=1)

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
    'Unnamed: 37': 'Dep. Acumulado',
    'Unnamed: 38': 'Filial aquisição'
}
# Ler apenas as colunas desejadas
df = pd.read_excel(nome_tabela, usecols=new_column_names.keys())

# Renomear as colunas
df.rename(columns=new_column_names, inplace=True)

# Conectar ao banco de dados SQLite
caminho_db = r"Banco Dados/cadastro_patrimonio.sqlite"
conn = sqlite3.connect(caminho_db)
cursor = conn.cursor()

# Garante que todas as colunas esperadas existam no DataFrame
expected_columns = list(new_column_names.values())
for col in expected_columns:
    if col not in df.columns:
        df[col] = None  # Ou algum outro valor padrão apropriado

# Verificar se a tabela já existe
inspector = inspect(create_engine(f'sqlite:///{caminho_db}'))
tabelas_existentes = inspector.get_table_names()

# Criar tabela se não existir
if "cadastro_patrimonio" not in tabelas_existentes:
    # Create the table with explicit column definitions
    create_table_sql = """
    CREATE TABLE cadastro_patrimonio (
        Plaqueta TEXT,
        "Desc. Bem" TEXT,
        Filial TEXT,
        "Cód. Local" TEXT,
        "Desc. Local" TEXT,
        "Cód. Portador" TEXT,
        Portador TEXT,
        "Data últ. Loc" TEXT,
        "Cód. Fornecedor" TEXT,
        Fornecedor TEXT,
        Documento TEXT,
        "Data aquisição" TEXT,
        "Valor Aquisição" REAL,
        "Cód. Bem" TEXT,
        "Série Fabricação" TEXT,
        Cor TEXT,
        Espécie TEXT,
        "Dep. Acumulado" REAL,
        "Filial aquisição" TEXT
    )
    """
    cursor.execute(create_table_sql)
    conn.commit()

# Iterar pelas linhas do DataFrame
for index, row in df.iterrows():
    # Verificar se a 'Plaqueta' já existe na tabela
    cursor.execute("SELECT COUNT(*) FROM cadastro_patrimonio WHERE Plaqueta = ?", (row['Plaqueta'],))
    count = cursor.fetchone()[0]

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
                "Dep. Acumulado" = ?,
                "Filial aquisição" = ?
            WHERE Plaqueta = ?
        """, (
            row['Desc. Bem'], row['Filial'], row['Cód. Local'], row['Desc. Local'], row['Cód. Portador'],
            row['Portador'], row['Data últ. Loc'], row['Cód. Fornecedor'], row['Fornecedor'],
            row['Documento'], row['Data aquisição'], row['Valor Aquisição'], row['Cód. Bem'],
            row['Série Fabricação'], row['Cor'], row['Espécie'], row['Dep. Acumulado'], row['Filial aquisição'], row['Plaqueta']
        ))
    else:
        # Inserir nova linha
        cursor.execute("""
            INSERT INTO cadastro_patrimonio (
                Plaqueta, "Desc. Bem", Filial, "Cód. Local", "Desc. Local", "Cód. Portador", Portador,
                "Data últ. Loc", "Cód. Fornecedor", Fornecedor, Documento, "Data aquisição",
                "Valor Aquisição", "Cód. Bem", "Série Fabricação", Cor, Espécie, "Dep. Acumulado", "Filial aquisição"
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row['Plaqueta'], row['Desc. Bem'], row['Filial'], row['Cód. Local'], row['Desc. Local'],
            row['Cód. Portador'], row['Portador'], row['Data últ. Loc'], row['Cód. Fornecedor'],
            row['Fornecedor'], row['Documento'], row['Data aquisição'], row['Valor Aquisição'],
            row['Cód. Bem'], row['Série Fabricação'], row['Cor'], row['Espécie'], row['Dep. Acumulado'], row['Filial aquisição']
        ))
    conn.commit()  # Salvar as alterações após cada iteração

conn.close()  # Fechar a conexão após a conclusão