"""Entrada independente para os dashboards exibidos nas TVs.

Uso:
  /?view=estoque  -> Dashboard de estoque e solicitações
  /?view=suporte  -> Dashboard de suporte técnico

Esta aplicação é somente de visualização; não registra movimentações patrimoniais.
"""
import streamlit as st

from dashboards.estoque import render_estoque
from dashboards.suporte import render_sup

st.set_page_config(
    page_title="VS. | Dashboards TI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

view = str(st.query_params.get("view", "estoque")).strip().lower()

if view in {"estoque", "stock"}:
    render_estoque()
elif view in {"suporte", "support", "sup"}:
    render_sup()
else:
    st.error("Dashboard não reconhecido.")
    st.caption("Use ?view=estoque ou ?view=suporte no endereço.")
