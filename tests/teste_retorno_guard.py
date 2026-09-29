import tempfile, shutil, sqlite3, sys, datetime
from pathlib import Path
root = Path(r'C:\Users\usuario\controleAtivosTI - Copia')
td = Path(tempfile.mkdtemp(prefix='retorno_guard_'))
(td / 'Banco Dados').mkdir()
for name in ['cadastro_patrimonio.sqlite', 'retorno.sqlite', 'assistencias.sqlite']:
    shutil.copy2(root / 'Banco Dados' / name, td / 'Banco Dados' / name)
sys.path.insert(0, str(root))
import services.retorno_service as rs
rs.DB_ASSISTENCIAS = td / 'Banco Dados' / 'assistencias.sqlite'
conn = sqlite3.connect(td / 'Banco Dados' / 'assistencias.sqlite')
row = conn.execute("SELECT id FROM assistencias WHERE patrimonio='113046' ORDER BY id DESC LIMIT 1").fetchone()
assert row
assist_id = row[0]
conn.execute("UPDATE assistencias SET status='Em assistência' WHERE id=?", (assist_id,))
conn.commit()
conn.close()
blocked = False
try:
    rs.registrar_retorno('113046', 'VENTILADOR TESTE', '10', 'RET-GUARD-001', 'NF-001', datetime.date.today(), str(td/'Banco Dados/retorno.sqlite'), str(td/'Banco Dados/cadastro_patrimonio.sqlite'))
except ValueError as exc:
    print('BLOCKED:', exc)
    blocked = 'assistencia aberta' in str(exc).lower()
assert blocked
conn = sqlite3.connect(td / 'Banco Dados' / 'assistencias.sqlite')
conn.execute("UPDATE assistencias SET status='Concluída' WHERE id=?", (assist_id,))
conn.commit()
conn.close()
rs.registrar_retorno('113046', 'VENTILADOR TESTE', '10', 'RET-GUARD-002', 'NF-002', datetime.date.today(), str(td/'Banco Dados/retorno.sqlite'), str(td/'Banco Dados/cadastro_patrimonio.sqlite'))
conn = sqlite3.connect(td / 'Banco Dados' / 'retorno.sqlite')
n = conn.execute("SELECT COUNT(*) FROM retorno WHERE Chamado='RET-GUARD-002'").fetchone()[0]
conn.close()
print('SUCCESS_AFTER_CONCLUSAO:', n)
assert n == 1
print('RETORNO_GUARD_TEST_PASS')
