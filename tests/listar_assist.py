import sqlite3
p=r'C:\Users\usuario\controleAtivosTI - Copia\Banco Dados\assistencias.sqlite'
c=sqlite3.connect(p)
print(c.execute('SELECT id,patrimonio,status FROM assistencias ORDER BY id DESC LIMIT 10').fetchall())
c.close()
