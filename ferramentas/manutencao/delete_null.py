import sqlite3
conn = sqlite3.connect("Banco Dados/cadastro_patrimonio.sqlite")
c = conn.cursor()
c.execute("DELETE  FROM cadastro_patrimonio WHERE Plaqueta IS NULL")
conn.commit()
print(c.execute("DELETE  FROM cadastro_patrimonio WHERE Plaqueta IS NULL").fetchall())

conn.close()