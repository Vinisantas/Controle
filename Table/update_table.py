import os
import pandas as pd
import sqlite3

# Ler tabela
nome_tabela = r"c:\vinícius senior\SRV-APLArquivos$Pompeiateste23.xlsx"

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
    'Unnamed: 38': 'Filial aquisição'
}

# Ler apenas as colunas desejadas e limpar linhas vazias
df = pd.read_excel(nome_tabela, usecols=list(new_column_names.keys()))
df.rename(columns=new_column_names, inplace=True)
df = df[df['Plaqueta'].notna()]  # remover linhas sem plaqueta
print(f"Linhas lidas (com Plaqueta): {len(df)}")
df['Valor Aquisição'] = (
    df['Valor Aquisição']
    .astype(str)
    .str.replace(r'[^\d,\.-]', '', regex=True)  # remover símbolos
    .str.replace(',', '.', regex=False)
    .replace('', None)
)
df['Valor Aquisição'] = pd.to_numeric(df['Valor Aquisição'], errors='coerce')

# Preparar banco
caminho_db = r"Banco Dados\cadastro_patrimonio.sqlite"
os.makedirs(os.path.dirname(caminho_db), exist_ok=True)

with sqlite3.connect(caminho_db) as conn:
    cursor = conn.cursor()
    print(f"Conectando ao DB: {caminho_db}")

    # Se tabela ainda não existe, cria normalmente
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cadastro_patrimonio'")
    if not cursor.fetchone():
        cursor.execute("""
        CREATE TABLE cadastro_patrimonio (
            Plaqueta TEXT PRIMARY KEY,
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
            "Filial aquisição" TEXT
        )
        """)
        conn.commit()
        print("Tabela 'cadastro_patrimonio' criada.")
    else:
        # tabela existe: verificar se Plaqueta é PK/UNIQUE; se não for, criar índice UNIQUE (se não houver duplicatas)
        cursor.execute("PRAGMA table_info(cadastro_patrimonio)")
        cols = cursor.fetchall()
        pk_cols = [c[1] for c in cols if c[5] == 1]  # c[5] é flag PK
        if 'Plaqueta' not in pk_cols:
            cursor.execute("""
                SELECT COUNT(*) FROM (
                    SELECT Plaqueta FROM cadastro_patrimonio
                    WHERE Plaqueta IS NOT NULL
                    GROUP BY Plaqueta
                    HAVING COUNT(*) > 1
                )
            """)
            dup_count = cursor.fetchone()[0]
            if dup_count > 0:
                raise RuntimeError(f"Existem {dup_count} plaquetas duplicadas na tabela. Remova duplicatas ou recrie a tabela antes de usar ON CONFLICT.")
            # sem duplicatas: criar índice UNIQUE para poder usar ON CONFLICT(Plaqueta)
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_cadastro_patrimonio_plaqueta ON cadastro_patrimonio(Plaqueta)")
            conn.commit()
            print("Índice UNIQUE em 'Plaqueta' criado.")
    # Usar upsert bulk para melhor performance
    sql = """
    INSERT INTO cadastro_patrimonio (
        Plaqueta, "Desc. Bem", Filial, "Cód. Local", "Desc. Local", "Cód. Portador", Portador,
        "Data últ. Loc", "Cód. Fornecedor", Fornecedor, Documento, "Data aquisição",
        "Valor Aquisição", "Cód. Bem", "Série Fabricação", "Filial aquisição"
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(Plaqueta) DO UPDATE SET
        "Desc. Bem" = excluded."Desc. Bem",
        Filial = excluded.Filial,
        "Cód. Local" = excluded."Cód. Local",
        "Desc. Local" = excluded."Desc. Local",
        "Cód. Portador" = excluded."Cód. Portador",
        Portador = excluded.Portador,
        "Data últ. Loc" = excluded."Data últ. Loc",
        "Cód. Fornecedor" = excluded."Cód. Fornecedor",
        Fornecedor = excluded.Fornecedor,
        Documento = excluded.Documento,
        "Data aquisição" = excluded."Data aquisição",
        "Valor Aquisição" = excluded."Valor Aquisição",
        "Cód. Bem" = excluded."Cód. Bem",
        "Série Fabricação" = excluded."Série Fabricação",
        "Filial aquisição" = excluded."Filial aquisição"
    """
    rows = []
    for _, r in df.iterrows():
        rows.append((
            r.get('Plaqueta'), r.get('Desc. Bem'), r.get('Filial'), r.get('Cód. Local'), r.get('Desc. Local'),
            r.get('Cód. Portador'), r.get('Portador'), r.get('Data últ. Loc'), r.get('Cód. Fornecedor'),
            r.get('Fornecedor'), r.get('Documento'), r.get('Data aquisição'), r.get('Valor Aquisição'),
            r.get('Cód. Bem'), r.get('Série Fabricação'), r.get('Filial aquisição')
        ))
    try:
        if rows:
            cursor.executemany(sql, rows)
            conn.commit()
            print(f"Registros processados: {len(rows)}")
        else:
            print("Nenhum registro para inserir/atualizar.")
    except Exception as e:
        conn.rollback()
        print("Erro ao inserir/atualizar:", e)
        raise