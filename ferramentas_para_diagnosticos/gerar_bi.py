import sqlite3
from pathlib import Path
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values


# ============================================================
# CONFIGURAÇÃO
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
PASTA_BANCO = BASE_DIR / "Banco Dados"

# ------------------------------------------------------------
# SQLITE - FONTES DA APLICAÇÃO
# ------------------------------------------------------------

DB_PATRIMONIO = PASTA_BANCO / "cadastro_patrimonio.sqlite"
DB_ESTOQUE = PASTA_BANCO / "estoque.sqlite"
DB_BAIXADOS = PASTA_BANCO / "cadastro_baixados.sqlite"
DB_SAIDA = PASTA_BANCO / "saida.sqlite"
DB_RETORNO = PASTA_BANCO / "retorno.sqlite"


# ============================================================
# POSTGRESQL
# ============================================================

PG_HOST = "192.168.201.140"
PG_PORT = 5432

PG_USER = "postgres"
PG_PASSWORD = "COLOQUE_SUA_SENHA_AQUI"

PG_DATABASE = "controle_ativos_ti"


# ============================================================
# CONEXÃO SQLITE
# ============================================================

def ler_tabela(caminho, tabela):

    conn = sqlite3.connect(caminho)

    try:

        df = pd.read_sql_query(
            f'SELECT * FROM "{tabela}"',
            conn
        )

    finally:

        conn.close()

    return df


# ============================================================
# INFORMAÇÕES
# ============================================================

def mostrar_info(nome, df):

    print(
        f"   {nome:<35} {len(df):>10,} registros"
    )


# ============================================================
# CARREGAR PATRIMÔNIO
# ============================================================

def carregar_patrimonio():

    print()
    print("=" * 70)
    print("📦 PATRIMÔNIO")
    print("=" * 70)

    df = ler_tabela(
        DB_PATRIMONIO,
        "cadastro_patrimonio"
    )

    mostrar_info(
        "Cadastro Patrimonial",
        df
    )

    return df


# ============================================================
# CARREGAR ESTOQUE
# ============================================================

def carregar_estoque():

    print()
    print("=" * 70)
    print("📦 ESTOQUE")
    print("=" * 70)

    tabelas = [
        "estoque",
        "cadastro_patrimonio",
        "inventario_adicional",
        "pendencias_baixa"
    ]

    dados = {}

    for tabela in tabelas:

        try:

            df = ler_tabela(
                DB_ESTOQUE,
                tabela
            )

            dados[tabela] = df

            mostrar_info(
                tabela,
                df
            )

        except Exception as e:

            print(
                f"   ⚠️ {tabela}: {e}"
            )

            dados[tabela] = pd.DataFrame()

    return dados


# ============================================================
# CARREGAR BAIXADOS
# ============================================================

def carregar_baixados():

    print()
    print("=" * 70)
    print("🗑️ PATRIMÔNIOS BAIXADOS")
    print("=" * 70)

    df = ler_tabela(
        DB_BAIXADOS,
        "cadastro_baixados"
    )

    mostrar_info(
        "Patrimônios baixados",
        df
    )

    return df


# ============================================================
# CARREGAR SAÍDAS
# ============================================================

def carregar_saidas():

    print()
    print("=" * 70)
    print("📤 SAÍDAS")
    print("=" * 70)

    df = ler_tabela(
        DB_SAIDA,
        "saida"
    )

    mostrar_info(
        "Saídas",
        df
    )

    return df


# ============================================================
# CARREGAR RETORNOS
# ============================================================

def carregar_retornos():

    print()
    print("=" * 70)
    print("📥 RETORNOS")
    print("=" * 70)

    df = ler_tabela(
        DB_RETORNO,
        "retorno"
    )

    mostrar_info(
        "Retornos",
        df
    )

    return df


# ============================================================
# NORMALIZAR PLAQUETA
# ============================================================

def normalizar_plaqueta(valor):

    if pd.isna(valor):

        return None

    valor = str(valor).strip()

    if valor.lower() in [
        "",
        "nan",
        "none",
        "null",
        "sem patrimônio",
        "sem patrimonio"
    ]:

        return None

    if valor.endswith(".0"):

        valor = valor[:-2]

    return valor


# ============================================================
# PADRONIZAR PATRIMÔNIO
# ============================================================

def padronizar_patrimonio(df):

    df = df.copy()

    if "Plaqueta" in df.columns:

        df["Plaqueta"] = (
            df["Plaqueta"]
            .apply(normalizar_plaqueta)
        )

    if "Cód. Bem" in df.columns:

        df["Cód. Bem"] = (
            df["Cód. Bem"]
            .astype(str)
            .str.replace(
                r"\.0$",
                "",
                regex=True
            )
            .str.strip()
        )

    if "Valor Aquisição" in df.columns:

        df["Valor Aquisição"] = pd.to_numeric(
            df["Valor Aquisição"],
            errors="coerce"
        )

    return df


# ============================================================
# PADRONIZAR BAIXADOS
# ============================================================

def padronizar_baixados(df):

    df = df.copy()

    if "Plaqueta" in df.columns:

        df["Plaqueta"] = (
            df["Plaqueta"]
            .apply(normalizar_plaqueta)
        )

    if "Cód. Bem" in df.columns:

        df["Cód. Bem"] = (
            df["Cód. Bem"]
            .astype(str)
            .str.replace(
                r"\.0$",
                "",
                regex=True
            )
            .str.strip()
        )

    if "Valor Aquisição" in df.columns:

        df["Valor Aquisição"] = pd.to_numeric(
            df["Valor Aquisição"],
            errors="coerce"
        )

    if "Dep. Acumulado" in df.columns:

        df["Dep. Acumulado"] = pd.to_numeric(
            df["Dep. Acumulado"],
            errors="coerce"
        )

    return df


# ============================================================
# PADRONIZAR SAÍDAS
# ============================================================

def padronizar_saidas(df):

    df = df.copy()

    if "Patrimonio" in df.columns:

        df["Patrimonio"] = (
            df["Patrimonio"]
            .apply(normalizar_plaqueta)
        )

    if "Qtd" in df.columns:

        df["Qtd"] = pd.to_numeric(
            df["Qtd"],
            errors="coerce"
        ).fillna(0).astype(int)

    if "Baixa_Senior" in df.columns:

        df["Baixa_Senior"] = pd.to_numeric(
            df["Baixa_Senior"],
            errors="coerce"
        ).fillna(0).astype(int)

    if "Data" in df.columns:

        df["Data"] = pd.to_datetime(
            df["Data"],
            errors="coerce"
        )

    return df


# ============================================================
# PADRONIZAR RETORNOS
# ============================================================

def padronizar_retornos(df):

    df = df.copy()

    if "Patrimonio" in df.columns:

        df["Patrimonio"] = (
            df["Patrimonio"]
            .apply(normalizar_plaqueta)
        )

    if "Data" in df.columns:

        df["Data"] = pd.to_datetime(
            df["Data"],
            errors="coerce"
        )

    return df


# ============================================================
# CLASSIFICAR TIPO DE ATIVO
# ============================================================

def classificar_tipo_ativo(descricao):

    if pd.isna(descricao):

        return "USO_CONSUMO"

    texto = str(descricao).upper()

    palavras_patrimoniais = [
        "COMPUTADOR",
        "NOTEBOOK",
        "MONITOR",
        "IMPRESSORA",
        "NOBREAK",
        "NO-BREAK",
        "CAMERA",
        "CÂMERA",
        "ACCESS POINT",
        "AP UBIQUITI",
        "SERVIDOR"
    ]

    for palavra in palavras_patrimoniais:

        if palavra in texto:

            return "PATRIMONIAL"

    return "USO_CONSUMO"


# ============================================================
# CRIAR FATO DE MOVIMENTAÇÃO
# ============================================================

def criar_movimentacoes(
    df_saida,
    df_retorno
):

    colunas = [

        "ID_MOVIMENTACAO",
        "Plaqueta_Normalizada",
        "Tipo_Movimentacao",
        "Data",
        "Descricao",
        "Quantidade",
        "Motivo",
        "Status_Equipamento",
        "Tipo_Destino",
        "Destinatario",
        "Usuario_Setor",
        "Chamado",
        "Tecnico",
        "NotaFiscal",
        "Baixa_Senior",
        "Observacao",
        "Tipo_Ativo"

    ]

    lista = []

    # --------------------------------------------------------
    # SAÍDAS
    # --------------------------------------------------------

    if not df_saida.empty:

        for _, row in df_saida.iterrows():

            patrimonio = normalizar_plaqueta(
                row.get("Patrimonio")
            )

            descricao = row.get(
                "Descricao"
            )

            lista.append({

                "ID_MOVIMENTACAO":
                    f"S-{row.get('id')}",

                "Plaqueta_Normalizada":
                    patrimonio,

                "Tipo_Movimentacao":
                    "Saída",

                "Data":
                    row.get("Data"),

                "Descricao":
                    descricao,

                "Quantidade":
                    row.get("Qtd", 1),

                "Motivo":
                    row.get("Motivo"),

                "Status_Equipamento":
                    row.get(
                        "Status_Equipamento"
                    ),

                "Tipo_Destino":
                    row.get("Tipo_Destino"),

                "Destinatario":
                    row.get("Destinatario"),

                "Usuario_Setor":
                    row.get("Usuario_Setor"),

                "Chamado":
                    row.get("Chamado"),

                "Tecnico":
                    row.get("Tecnico"),

                "NotaFiscal":
                    None,

                "Baixa_Senior":
                    row.get(
                        "Baixa_Senior",
                        0
                    ),

                "Observacao":
                    row.get("Observacao"),

                "Tipo_Ativo":
                    classificar_tipo_ativo(
                        descricao
                    )

            })

    # --------------------------------------------------------
    # RETORNOS
    # --------------------------------------------------------

    if not df_retorno.empty:

        for _, row in df_retorno.iterrows():

            patrimonio = normalizar_plaqueta(
                row.get("Patrimonio")
            )

            descricao = row.get(
                "Descricao"
            )

            lista.append({

                "ID_MOVIMENTACAO":
                    f"R-{row.get('id')}",

                "Plaqueta_Normalizada":
                    patrimonio,

                "Tipo_Movimentacao":
                    "Retorno",

                "Data":
                    row.get("Data"),

                "Descricao":
                    descricao,

                "Quantidade":
                    1,

                "Motivo":
                    "Retorno",

                "Status_Equipamento":
                    None,

                "Tipo_Destino":
                    row.get("Loja"),

                "Destinatario":
                    None,

                "Usuario_Setor":
                    None,

                "Chamado":
                    row.get("Chamado"),

                "Tecnico":
                    None,

                "NotaFiscal":
                    row.get("Notafiscal"),

                "Baixa_Senior":
                    0,

                "Observacao":
                    None,

                "Tipo_Ativo":
                    classificar_tipo_ativo(
                        descricao
                    )

            })

    if not lista:

        return pd.DataFrame(
            columns=colunas
        )

    return pd.DataFrame(
        lista,
        columns=colunas
    )


# ============================================================
# CRIAR DIMENSÃO EQUIPAMENTO
# ============================================================

def criar_dim_equipamento(
    df_patrimonio,
    df_saida,
    df_retorno,
    df_baixados
):

    df = df_patrimonio.copy()

    # --------------------------------------------------------
    # PLAQUETA
    # --------------------------------------------------------

    df["Plaqueta_Normalizada"] = (
        df["Plaqueta"]
        .apply(normalizar_plaqueta)
    )

    # --------------------------------------------------------
    # TIPO DE ATIVO
    # --------------------------------------------------------

    df["Tipo_Ativo"] = (
        df["Desc. Bem"]
        .apply(classificar_tipo_ativo)
    )

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    df["Status_Atual"] = "DISPONÍVEL"

    # --------------------------------------------------------
    # PATRIMÔNIOS QUE SAÍRAM
    # --------------------------------------------------------

    if not df_saida.empty:

        saidas = set(
            df_saida[
                "Patrimonio"
            ]
            .dropna()
            .apply(normalizar_plaqueta)
        )

        df.loc[
            df["Plaqueta_Normalizada"].isin(
                saidas
            ),
            "Status_Atual"
        ] = "FORA"

    # --------------------------------------------------------
    # RETORNOS
    # --------------------------------------------------------

    if not df_retorno.empty:

        retornos = set(
            df_retorno[
                "Patrimonio"
            ]
            .dropna()
            .apply(normalizar_plaqueta)
        )

        df.loc[
            df["Plaqueta_Normalizada"].isin(
                retornos
            ),
            "Status_Atual"
        ] = "DISPONÍVEL"

    # --------------------------------------------------------
    # BAIXADOS
    # --------------------------------------------------------

    if not df_baixados.empty:

        baixados = set(
            df_baixados[
                "Plaqueta"
            ]
            .dropna()
            .apply(normalizar_plaqueta)
        )

        df.loc[
            df["Plaqueta_Normalizada"].isin(
                baixados
            ),
            "Status_Atual"
        ] = "BAIXADO"

    return df


# ============================================================
# CRIAR DIMENSÃO DATA
# ============================================================

def criar_dim_data(
    df_saida,
    df_retorno
):

    datas = []

    if not df_saida.empty:

        datas.extend(
            df_saida["Data"]
            .dropna()
            .tolist()
        )

    if not df_retorno.empty:

        datas.extend(
            df_retorno["Data"]
            .dropna()
            .tolist()
        )

    if not datas:

        return pd.DataFrame()

    inicio = min(datas)
    fim = max(datas)

    calendario = pd.DataFrame({

        "Data":
            pd.date_range(
                inicio,
                fim,
                freq="D"
            )

    })

    calendario["Ano"] = (
        calendario["Data"].dt.year
    )

    calendario["Mes"] = (
        calendario["Data"].dt.month
    )

    calendario["Nome_Mes"] = (
        calendario["Data"]
        .dt.month_name()
    )

    calendario["Trimestre"] = (
        "T"
        + calendario["Data"]
        .dt.quarter.astype(str)
    )

    calendario["Dia"] = (
        calendario["Data"].dt.day
    )

    calendario["Dia_Semana"] = (
        calendario["Data"]
        .dt.dayofweek + 1
    )

    return calendario


# ============================================================
# CONECTAR POSTGRES
# ============================================================

def conectar_postgres(
    database=PG_DATABASE
):

    return psycopg2.connect(

        host=PG_HOST,

        port=PG_PORT,

        user=PG_USER,

        password=PG_PASSWORD,

        database=database

    )


# ============================================================
# CRIAR BANCO POSTGRES
# ============================================================

def criar_banco_postgres():

    print()
    print("=" * 70)
    print("🐘 VERIFICANDO POSTGRESQL")
    print("=" * 70)

    conn = psycopg2.connect(

        host=PG_HOST,

        port=PG_PORT,

        user=PG_USER,

        password=PG_PASSWORD,

        database="postgres"

    )

    conn.autocommit = True

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 1
        FROM pg_database
        WHERE datname = %s
        """,
        (PG_DATABASE,)
    )

    existe = cursor.fetchone()

    if existe:

        print(
            f"   ✅ Banco {PG_DATABASE} já existe"
        )

    else:

        cursor.execute(
            f'CREATE DATABASE "{PG_DATABASE}"'
        )

        print(
            f"   ✅ Banco {PG_DATABASE} criado"
        )

    cursor.close()
    conn.close()


# ============================================================
# CRIAR ESTRUTURA ANALÍTICA
# ============================================================

def criar_estrutura_postgres():

    conn = conectar_postgres()

    cursor = conn.cursor()

    print()
    print("🏗️ CRIANDO ESTRUTURA ANALÍTICA...")

    # --------------------------------------------------------
    # DIM DATA
    # --------------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS dim_data (

            Data DATE PRIMARY KEY,

            Ano INTEGER,

            Mes INTEGER,

            Nome_Mes TEXT,

            Trimestre TEXT,

            Dia INTEGER,

            Dia_Semana INTEGER

        )
        """
    )

    # --------------------------------------------------------
    # DIM EQUIPAMENTO
    # --------------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS dim_equipamento (

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

            "Valor Aquisição" NUMERIC,

            "Cód. Bem" TEXT,

            "Série Fabricação" TEXT,

            "Filial aquisição" TEXT,

            Plaqueta_Normalizada TEXT,

            Tipo_Ativo TEXT,

            Status_Atual TEXT

        )
        """
    )

    # --------------------------------------------------------
    # FATO MOVIMENTAÇÃO
    # --------------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS fato_movimentacao (

            ID_MOVIMENTACAO TEXT PRIMARY KEY,

            Plaqueta_Normalizada TEXT,

            Tipo_Movimentacao TEXT,

            Data TIMESTAMP,

            Descricao TEXT,

            Quantidade INTEGER,

            Motivo TEXT,

            Status_Equipamento TEXT,

            Tipo_Destino TEXT,

            Destinatario TEXT,

            Usuario_Setor TEXT,

            Chamado TEXT,

            Tecnico TEXT,

            NotaFiscal TEXT,

            Baixa_Senior INTEGER,

            Observacao TEXT,

            Tipo_Ativo TEXT

        )
        """
    )

    conn.commit()

    cursor.close()
    conn.close()

    print("   ✅ dim_data")
    print("   ✅ dim_equipamento")
    print("   ✅ fato_movimentacao")


# ============================================================
# SINCRONIZAR DIM DATA
# ============================================================

def sincronizar_dim_data(df):

    if df.empty:

        return

    conn = conectar_postgres()
    cursor = conn.cursor()

    registros = []

    for _, row in df.iterrows():

        data = row["Data"]

        if pd.isna(data):

            continue

        registros.append((

            data.date(),

            int(row["Ano"]),

            int(row["Mes"]),

            row["Nome_Mes"],

            row["Trimestre"],

            int(row["Dia"]),

            int(row["Dia_Semana"])

        ))

    sql = """

        INSERT INTO dim_data (

            Data,
            Ano,
            Mes,
            Nome_Mes,
            Trimestre,
            Dia,
            Dia_Semana

        )

        VALUES %s

        ON CONFLICT (Data)

        DO UPDATE SET

            Ano = EXCLUDED.Ano,

            Mes = EXCLUDED.Mes,

            Nome_Mes = EXCLUDED.Nome_Mes,

            Trimestre = EXCLUDED.Trimestre,

            Dia = EXCLUDED.Dia,

            Dia_Semana = EXCLUDED.Dia_Semana

    """

    execute_values(
        cursor,
        sql,
        registros
    )

    conn.commit()

    cursor.close()
    conn.close()

    print(
        f"   ✅ dim_data: {len(registros):,}"
    )


# ============================================================
# SINCRONIZAR DIM EQUIPAMENTO
# ============================================================

def sincronizar_dim_equipamento(df):

    if df.empty:

        return

    conn = conectar_postgres()
    cursor = conn.cursor()

    colunas = [

        "Plaqueta",
        "Desc. Bem",
        "Filial",
        "Cód. Local",
        "Desc. Local",
        "Cód. Portador",
        "Portador",
        "Data últ. Loc",
        "Cód. Fornecedor",
        "Fornecedor",
        "Documento",
        "Data aquisição",
        "Valor Aquisição",
        "Cód. Bem",
        "Série Fabricação",
        "Filial aquisição",
        "Plaqueta_Normalizada",
        "Tipo_Ativo",
        "Status_Atual"

    ]

    registros = []

    for _, row in df.iterrows():

        plaqueta = row.get(
            "Plaqueta_Normalizada"
        )

        if not plaqueta:

            continue

        valores = []

        for coluna in colunas:

            valor = row.get(
                coluna
            )

            if pd.isna(valor):

                valor = None

            valores.append(valor)

        registros.append(
            tuple(valores)
        )

    placeholders = ",".join(
        ["%s"] * len(colunas)
    )

    atualizacoes = ",".join(

        f'"{col}" = EXCLUDED."{col}"'

        for col in colunas
        if col != "Plaqueta"

    )

    sql = f"""

        INSERT INTO dim_equipamento (

            {",".join(f'"{c}"' for c in colunas)}

        )

        VALUES ({placeholders})

        ON CONFLICT (Plaqueta)

        DO UPDATE SET

            {atualizacoes}

    """

    cursor.executemany(
        sql,
        registros
    )

    conn.commit()

    cursor.close()
    conn.close()

    print(
        f"   ✅ dim_equipamento: {len(registros):,}"
    )


# ============================================================
# SINCRONIZAR FATO MOVIMENTAÇÃO
# ============================================================

def sincronizar_movimentacoes(df):

    if df.empty:

        return

    conn = conectar_postgres()
    cursor = conn.cursor()

    colunas = list(
        df.columns
    )

    registros = []

    for _, row in df.iterrows():

        valores = []

        for coluna in colunas:

            valor = row[coluna]

            if pd.isna(valor):

                valor = None

            elif isinstance(
                valor,
                pd.Timestamp
            ):

                valor = valor.to_pydatetime()

            valores.append(valor)

        registros.append(
            tuple(valores)
        )

    placeholders = ",".join(
        ["%s"] * len(colunas)
    )

    atualizacoes = ",".join(

        f'"{col}" = EXCLUDED."{col}"'

        for col in colunas
        if col != "ID_MOVIMENTACAO"

    )

    sql = f"""

        INSERT INTO fato_movimentacao (

            {",".join(f'"{c}"' for c in colunas)}

        )

        VALUES ({placeholders})

        ON CONFLICT (ID_MOVIMENTACAO)

        DO UPDATE SET

            {atualizacoes}

    """

    cursor.executemany(
        sql,
        registros
    )

    conn.commit()

    cursor.close()
    conn.close()

    print(
        f"   ✅ fato_movimentacao: {len(registros):,}"
    )


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

def main():

    print()
    print("=" * 70)
    print("🚀 CONTROLE DE ATIVOS TI")
    print("   SINCRONIZAÇÃO SQLITE → POSTGRESQL")
    print("=" * 70)

    # --------------------------------------------------------
    # VERIFICAR SQLITE
    # --------------------------------------------------------

    print()
    print("🔎 VERIFICANDO BANCOS SQLITE...")

    arquivos = [

        DB_PATRIMONIO,
        DB_ESTOQUE,
        DB_BAIXADOS,
        DB_SAIDA,
        DB_RETORNO

    ]

    for arquivo in arquivos:

        if arquivo.exists():

            print(
                f"   ✅ {arquivo.name}"
            )

        else:

            print(
                f"   ❌ {arquivo.name} NÃO ENCONTRADO"
            )

            return

    # --------------------------------------------------------
    # POSTGRES
    # --------------------------------------------------------

    try:

        criar_banco_postgres()

        criar_estrutura_postgres()

    except Exception as e:

        print()
        print("❌ ERRO NO POSTGRESQL")
        print(e)

        return

    # --------------------------------------------------------
    # CARREGAR
    # --------------------------------------------------------

    df_patrimonio = (
        carregar_patrimonio()
    )

    estoque = (
        carregar_estoque()
    )

    df_baixados = (
        carregar_baixados()
    )

    df_saida = (
        carregar_saidas()
    )

    df_retorno = (
        carregar_retornos()
    )

    # --------------------------------------------------------
    # PADRONIZAR
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("🔧 PADRONIZANDO DADOS")
    print("=" * 70)

    df_patrimonio = (
        padronizar_patrimonio(
            df_patrimonio
        )
    )

    df_baixados = (
        padronizar_baixados(
            df_baixados
        )
    )

    df_saida = (
        padronizar_saidas(
            df_saida
        )
    )

    df_retorno = (
        padronizar_retornos(
            df_retorno
        )
    )

    print("   ✅ Patrimônio")
    print("   ✅ Baixados")
    print("   ✅ Saídas")
    print("   ✅ Retornos")

    # --------------------------------------------------------
    # MOVIMENTAÇÕES
    # --------------------------------------------------------

    print()
    print("🔄 CRIANDO MOVIMENTAÇÕES...")

    df_movimentacoes = (
        criar_movimentacoes(
            df_saida,
            df_retorno
        )
    )

    print(
        f"   ✅ {len(df_movimentacoes):,} movimentações"
    )

    # --------------------------------------------------------
    # DIM EQUIPAMENTO
    # --------------------------------------------------------

    print()
    print("📦 CRIANDO DIMENSÃO EQUIPAMENTO...")

    df_equipamento = (
        criar_dim_equipamento(
            df_patrimonio,
            df_saida,
            df_retorno,
            df_baixados
        )
    )

    print(
        f"   ✅ {len(df_equipamento):,} equipamentos"
    )

    # --------------------------------------------------------
    # CALENDÁRIO
    # --------------------------------------------------------

    print()
    print("📅 CRIANDO CALENDÁRIO...")

    df_data = criar_dim_data(
        df_saida,
        df_retorno
    )

    print(
        f"   ✅ {len(df_data):,} datas"
    )

    # --------------------------------------------------------
    # SINCRONIZAR
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("🐘 SINCRONIZANDO POSTGRESQL")
    print("=" * 70)

    try:

        sincronizar_dim_data(
            df_data
        )

        sincronizar_dim_equipamento(
            df_equipamento
        )

        sincronizar_movimentacoes(
            df_movimentacoes
        )

    except Exception as e:

        print()
        print("❌ ERRO DURANTE SINCRONIZAÇÃO")
        print(e)

        return

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("📊 STATUS ATUAL")
    print("=" * 70)

    print(
        df_equipamento[
            "Status_Atual"
        ]
        .value_counts()
        .to_string()
    )

    print()
    print("=" * 70)
    print("🎉 SINCRONIZAÇÃO CONCLUÍDA!")
    print("=" * 70)

    print()
    print("PostgreSQL:")
    print(
        f"   Host: {PG_HOST}"
    )

    print(
        f"   Banco: {PG_DATABASE}"
    )

    print(
        f"   Porta: {PG_PORT}"
    )

    print()
    print("Tabelas:")

    print(
        f"   dim_equipamento: "
        f"{len(df_equipamento):,}"
    )

    print(
        f"   fato_movimentacao: "
        f"{len(df_movimentacoes):,}"
    )

    print(
        f"   dim_data: "
        f"{len(df_data):,}"
    )

    print()
    print("💡 O Power BI poderá consultar")
    print("   diretamente o PostgreSQL.")


# ============================================================
# INICIAR
# ============================================================

if __name__ == "__main__":

    main()