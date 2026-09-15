import sqlite3
import pandas as pd

DB_NAME = "Banco Dados/cadastro_patrimonio.sqlite"


def buscar_patrimonio(patrimonio):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
    """)

    tabelas = cursor.fetchall()

    for tabela in tabelas:
        nome_tabela = tabela[0]

        try:
            df = pd.read_sql_query(
                f'SELECT * FROM "{nome_tabela}"',
                conn
            )

            if "Plaqueta" not in df.columns:
                continue

            df["Plaqueta_Normalizada"] = (
                df["Plaqueta"]
                .astype(str)
                .str.replace(".0", "", regex=False)
                .str.strip()
            )

            resultado = df[
                df["Plaqueta_Normalizada"] == str(patrimonio).strip()
            ]

            if not resultado.empty:
                descricao = resultado.iloc[0].get("Desc. Bem", "")

                conn.close()

                return str(descricao).strip()

        except Exception:
            continue

    conn.close()
    return None

def atualiza_portador(Patrimonio, novo_portador):
    conn_pat = sqlite3.connect(DB_NAME)
    cursor_pat = conn_pat.cursor()
    # Atualiza os dados de Portador com base na Plaqueta
    cursor_pat.execute(f"""
        UPDATE [{"cadastro_patrimonio"}]
        SET Portador = ?
        WHERE RTRIM(LTRIM(REPLACE(Plaqueta, '.0', ''))) = ?
    """, (novo_portador, Patrimonio))
    
    conn_pat.commit()
    conn_pat.close()


def atualiza_filial(Patrimonio, nova_filial):
    conn_pat = sqlite3.connect(DB_NAME)
    cursor_pat = conn_pat.cursor()
    # Atualiza os dados da filial com base na Plaqueta
    cursor_pat.execute(f"""
        UPDATE [{"cadastro_patrimonio"}]
        SET Filial = ?
        WHERE RTRIM(LTRIM(REPLACE(Plaqueta, '.0', ''))) = ?
    """, (nova_filial, Patrimonio))
    
    conn_pat.commit()
    conn_pat.close()

def atualiza_fornecedor(Patrimonio,fornecedor):
    conn_pat = sqlite3.connect(DB_NAME)
    cursor_pat = conn_pat.cursor()
    # Atualiza os dados de Portador e filial com base na Plaqueta
    cursor_pat.execute(f"""
        UPDATE [{"cadastro_patrimonio"}]
        SET Portador = ?, Filial = "1000"
        WHERE RTRIM(LTRIM(REPLACE(Plaqueta, '.0', ''))) = ?
    """, (fornecedor, Patrimonio))
    
    conn_pat.commit()
    conn_pat.close()
