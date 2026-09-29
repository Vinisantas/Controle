
import os
import pandas as pd
import sqlite3

# ============================================================
# ARQUIVO EXCEL DO SENIOR
# ============================================================

nome_tabela = r"c:\vinícius senior\SRV-APLArquivos$Pompeiateste.xlsx"


# ============================================================
# COLUNAS DO RELATÓRIO SENIOR
# ============================================================

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
    'Unnamed: 35': 'ESPECIE',
    'Unnamed: 38': 'Filial aquisição'
}


# ============================================================
# LER EXCEL
# ============================================================

print()
print("=" * 70)
print("📊 ATUALIZAÇÃO DO CADASTRO PATRIMONIAL")
print("=" * 70)

print()
print("📂 Lendo relatório do Senior...")
print(nome_tabela)

# Ler apenas as colunas necessárias
df = pd.read_excel(
    nome_tabela,
    usecols=list(new_column_names.keys())
)

# Renomear colunas
df.rename(
    columns=new_column_names,
    inplace=True
)

# Remover linhas sem plaqueta
df = df[
    df['Plaqueta'].notna()
].copy()

print(
    f"   Registros lidos: {len(df):,}"
)


# ============================================================
# PADRONIZAR PLAQUETA
# ============================================================

df['Plaqueta'] = (
    df['Plaqueta']
    .astype(str)
    .str.strip()
    .str.replace(
        r'\.0$',
        '',
        regex=True
    )
)


# ============================================================
# PADRONIZAR ESPECIE
# ============================================================

df['ESPECIE'] = pd.to_numeric(
    df['ESPECIE'],
    errors='coerce'
)

# Converter 320.0 → 320
df['ESPECIE'] = (
    df['ESPECIE']
    .astype('Int64')
)


# ============================================================
# PADRONIZAR VALOR DE AQUISIÇÃO
# ============================================================

df['Valor Aquisição'] = (
    df['Valor Aquisição']
    .astype(str)
    .str.replace(
        r'[^\d,\.-]',
        '',
        regex=True
    )
    .str.replace(
        ',',
        '.',
        regex=False
    )
    .replace(
        '',
        None
    )
)

df['Valor Aquisição'] = pd.to_numeric(
    df['Valor Aquisição'],
    errors='coerce'
)


# ============================================================
# MOSTRAR ESPÉCIES ENCONTRADAS
# ============================================================

print()
print("🔎 ESPÉCIES ENCONTRADAS NO RELATÓRIO:")

print(
    df['ESPECIE']
    .value_counts(dropna=False)
    .sort_index()
    .to_string()
)


# ============================================================
# PREPARAR BANCO SQLITE
# ============================================================

caminho_db = r"Banco Dados\cadastro_patrimonio.sqlite"

os.makedirs(
    os.path.dirname(caminho_db),
    exist_ok=True
)

with sqlite3.connect(caminho_db) as conn:

    cursor = conn.cursor()

    print()
    print(
        f"🗄️ Banco: {caminho_db}"
    )


    # ========================================================
    # VERIFICAR SE A TABELA EXISTE
    # ========================================================

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name='cadastro_patrimonio'
    """)

    tabela_existe = cursor.fetchone()


    # ========================================================
    # CRIAR TABELA
    # ========================================================

    if not tabela_existe:

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

                ESPECIE INTEGER,

                "Filial aquisição" TEXT
            )
        """)

        conn.commit()

        print(
            "   ✅ Tabela criada"
        )


    # ========================================================
    # TABELA JÁ EXISTE
    # ========================================================

    else:

        cursor.execute(
            "PRAGMA table_info(cadastro_patrimonio)"
        )

        colunas_existentes = [
            coluna[1]
            for coluna in cursor.fetchall()
        ]


        # ----------------------------------------------------
        # ADICIONAR ESPECIE SE NÃO EXISTIR
        # ----------------------------------------------------

        if 'ESPECIE' not in colunas_existentes:

            print()
            print(
                "⚠️ Coluna ESPECIE não existe."
            )

            print(
                "🔧 Adicionando coluna ESPECIE..."
            )

            cursor.execute("""
                ALTER TABLE cadastro_patrimonio
                ADD COLUMN ESPECIE INTEGER
            """)

            conn.commit()

            print(
                "   ✅ ESPECIE adicionada"
            )

        else:

            print(
                "   ✅ Coluna ESPECIE já existe"
            )


        # ----------------------------------------------------
        # GARANTIR PLAQUETA COMO CHAVE ÚNICA
        # ----------------------------------------------------

        cursor.execute(
            "PRAGMA table_info(cadastro_patrimonio)"
        )

        cols = cursor.fetchall()

        pk_cols = [
            c[1]
            for c in cols
            if c[5] == 1
        ]


        if 'Plaqueta' not in pk_cols:

            cursor.execute("""
                SELECT COUNT(*)
                FROM (
                    SELECT Plaqueta
                    FROM cadastro_patrimonio
                    WHERE Plaqueta IS NOT NULL
                    GROUP BY Plaqueta
                    HAVING COUNT(*) > 1
                )
            """)

            dup_count = cursor.fetchone()[0]


            if dup_count > 0:

                raise RuntimeError(
                    f"Existem {dup_count} plaquetas duplicadas "
                    "na tabela."
                )


            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS
                ux_cadastro_patrimonio_plaqueta
                ON cadastro_patrimonio(Plaqueta)
            """)

            conn.commit()

            print(
                "   ✅ Índice UNIQUE em Plaqueta"
            )


    # ========================================================
    # UPSERT
    # ========================================================

    sql = """
        INSERT INTO cadastro_patrimonio (

            Plaqueta,
            "Desc. Bem",
            Filial,
            "Cód. Local",
            "Desc. Local",
            "Cód. Portador",
            Portador,
            "Data últ. Loc",
            "Cód. Fornecedor",
            Fornecedor,
            Documento,
            "Data aquisição",
            "Valor Aquisição",
            "Cód. Bem",
            "Série Fabricação",
            ESPECIE,
            "Filial aquisição"

        )

        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?
        )

        ON CONFLICT(Plaqueta)
        DO UPDATE SET

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

            ESPECIE = excluded.ESPECIE,

            "Filial aquisição" = excluded."Filial aquisição"
    """


    # ========================================================
    # PREPARAR REGISTROS
    # ========================================================

    rows = []

    for _, r in df.iterrows():

        especie = r.get('ESPECIE')

        if pd.isna(especie):
            especie = None
        else:
            especie = int(especie)


        rows.append((

            r.get('Plaqueta'),

            r.get('Desc. Bem'),

            r.get('Filial'),

            r.get('Cód. Local'),

            r.get('Desc. Local'),

            r.get('Cód. Portador'),

            r.get('Portador'),

            r.get('Data últ. Loc'),

            r.get('Cód. Fornecedor'),

            r.get('Fornecedor'),

            r.get('Documento'),

            r.get('Data aquisição'),

            r.get('Valor Aquisição'),

            r.get('Cód. Bem'),

            r.get('Série Fabricação'),

            especie,

            r.get('Filial aquisição')

        ))


    # ========================================================
    # EXECUTAR ATUALIZAÇÃO
    # ========================================================

    try:

        if rows:

            cursor.executemany(
                sql,
                rows
            )

            conn.commit()

            print()
            print(
                f"✅ Registros processados: {len(rows):,}"
            )

        else:

            print(
                "⚠️ Nenhum registro para inserir/atualizar."
            )


    except Exception as e:

        conn.rollback()

        print()
        print(
            "❌ Erro ao inserir/atualizar:"
        )

        print(e)

        raise


    # ========================================================
    # CONFERÊNCIA FINAL
    # ========================================================

    cursor.execute("""
        SELECT
            COUNT(*) AS total,
            COUNT(ESPECIE) AS com_especie
        FROM cadastro_patrimonio
    """)

    total, com_especie = cursor.fetchone()

    print()
    print("=" * 70)
    print("📊 CONFERÊNCIA DO SQLITE")
    print("=" * 70)

    print(
        f"   Total de patrimônios: {total:,}"
    )

    print(
        f"   Com ESPECIE:         {com_especie:,}"
    )

    print(
        f"   Sem ESPECIE:         {total - com_especie:,}"
    )

    print()

print("=" * 70)
print("🎉 ATUALIZAÇÃO CONCLUÍDA!")
print("=" * 70)
