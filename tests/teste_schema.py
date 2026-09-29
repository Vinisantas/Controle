import sqlite3
c=sqlite3.connect(r'C:\Users\usuario\controleAtivosTI - Copia\Banco Dados\cadastro_patrimonio.sqlite')
print(c.execute('PRAGMA table_info(cadastro_patrimonio)').fetchall())
c.close()
