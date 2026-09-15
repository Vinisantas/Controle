import sqlite3
import pandas as pd




DB_NAME = "Banco Dados/saida.sqlite"





def inicializar_banco():
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saida (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Patrimonio TEXT,
                Descricao TEXT,
                Qtd INTEGER,
                Motivo TEXT,
                Status_Equipamento TEXT,
                Tipo_Destino TEXT,
                Destinatario TEXT,
                Usuario_Setor TEXT,
                Chamado TEXT,
                Tecnico TEXT,
                Data DATE,
                Observacao TEXT,
                Baixa_Senior INTEGER DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()


def carregar_dados():
    conn = sqlite3.connect(DB_NAME)
    # Convertemos Baixa_Senior para booleano para funcionar perfeitamente no checkbox do Streamlit
    df = pd.read_sql_query("SELECT * FROM saida ORDER BY Data DESC", conn, parse_dates=["Data"])
    df['Baixa_Senior'] = df['Baixa_Senior'].astype(bool)
    conn.close()
    return df


def salvar_no_banco(Patrimonio, Descricao, Qtd, Motivo, Status_Equipamento, Tipo_Destino, Destinatario, Usuario_Setor, Chamado, Tecnico, Data, Observacao):
    # 1. SALVA NO BANCO DE HISTÓRICO DE SAÍDAS (Começa sempre sem baixa na Senior: 0)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO saida (Patrimonio, Descricao, Qtd, Motivo, Status_Equipamento, Tipo_Destino, Destinatario, Usuario_Setor, Chamado, Tecnico, Data, Observacao, Baixa_Senior)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    ''', (Patrimonio, Descricao, Qtd, Motivo, Status_Equipamento, Tipo_Destino, Destinatario, Usuario_Setor, Chamado, Tecnico, Data.isoformat(), Observacao))
    conn.commit()
    conn.close()



def atualizar_linha_banco(id_registro, coluna, novo_valor):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f'UPDATE saida SET {coluna} = ? WHERE id = ?', (novo_valor, id_registro))
    conn.commit()
    conn.close()



def excluir_do_banco(id_registro):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM saida WHERE id = ?', (id_registro,))
    conn.commit()
    conn.close()