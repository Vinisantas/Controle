"""Indicadores de negócio para assistências técnicas."""

import pandas as pd

def calcular_indicadores(df):
    """Calcula indicadores gerais sem depender da interface Streamlit."""
    if df.empty:
        return {"total": 0, "gasto_total": 0, "gasto_mes": 0, "abertas": 0}

    hoje = pd.Timestamp.today()
    inicio_mes = hoje.to_period("M").start_time
    datas_entrada = pd.to_datetime(df["data_entrada"])
    valores = pd.to_numeric(df["valor_pago"], errors="coerce").fillna(0)
    gasto_mes = valores.loc[datas_entrada >= inicio_mes].sum()

    return {
        "total": len(df),
        "gasto_total": valores.sum(),
        "gasto_mes": gasto_mes,
        "abertas": int((df["status"].astype(str).str.strip().str.casefold() == "em assistência").sum()),
    }
