"""Smoke tests das telas Streamlit na cópia de teste, sem enviar formulários."""
from pathlib import Path
import sys
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
APP = ROOT / "app.py"
PAGINAS = [
    "🏠 Visão Geral",
    "📊 Central de Dashboards",
    "🔍 Consulta Patrimônio",
    "➡️ Saída Equipamentos",
    "↩️ Retorno Equipamentos",
    "🕒 Histórico Geral",
    "📊 Dashboard Estoque",
    "📈 Dashboard Sup",
    "🤖 Assistente de TI",
    "🛠️ Assistências",
    "📥 Importação Senior",
    "🗑️ Saídas (Histórico)",
]

for pagina in PAGINAS:
    teste = AppTest.from_file(str(APP), default_timeout=45)
    teste.session_state["autenticado"] = True
    teste.session_state["menu_atual"] = pagina
    teste.run()
    erros = list(teste.exception)
    if erros:
        detalhes = " | ".join(str(erro.message) for erro in erros)
        raise AssertionError(f"TELA COM ERRO [{pagina}]: {detalhes}")
    print(f"TELA_PASS: {pagina}")

print(f"TELAS_STREAMLIT_PASS: {len(PAGINAS)}")
