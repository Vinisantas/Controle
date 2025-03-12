from pathlib import Path
import sqlite3

# Definir o caminho do banco de dados
caminho = 'cadastro_patrimonio.sqlite'

# Verificar se o arquivo existe antes de tentar conectar
if not Path(caminho).exists():
    print("Arquivo de banco de dados não encontrado.")
else:
    # Conectar ao banco de dados se o arquivo existir
    conn = sqlite3.connect(caminho)
    print("Conexão estabelecida com sucesso.")
    # Fechar a conexão
    conn.close()
