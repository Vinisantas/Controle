import sqlite3

# Conectar ao banco de dados
conn = sqlite3.connect("cadastro_patrimonio.sqlite")

# Listar as tabelas existentes
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# Exibir as tabelas
print("Tabelas no banco de dados:")
for table in tables:
    print(table[0])

# Fechar a conexão
conn.close()
