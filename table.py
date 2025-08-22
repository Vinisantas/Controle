import sqlite3

# Conectar ao banco de dados SQLite
caminho_db = r"Banco Dados/cadastro_patrimonio.sqlite"  # Caminho completo para o arquivo .sqlite
conn = sqlite3.connect(caminho_db)
cursor = conn.cursor()

create_table_sql = """
    CREATE TABLE IF NOT EXISTS cadastro_patrimonio (  -- Adicionado IF NOT EXISTS
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

conn.close()
exit()