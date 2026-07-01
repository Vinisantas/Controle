import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime
import base64
from pathlib import Path
from streamlit_autorefresh import st_autorefresh


TOKEN = "b9991fdc-6754-4153-ac49-4c0116c1b4d1"
ALERTA_INTERVALO_SEGUNDOS = int(os.getenv("ALERTA_INTERVALO_SEGUNDOS", "60"))
URL = "https://api.movidesk.com/public/v1/tickets"
FILTER_QUERY = "(ownerTeam eq 'Suporte Técnico')"
SELECT_FIELDS = "id,status,baseStatus,subject,createdDate,clients,urgency,lastActionDate,owner"
EXPAND = "clients($expand=organization),owner"

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================
st.set_page_config(
    page_title="Movidesk TI",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="collapsed"
)

# Atualiza a cada 30 segundos
st_autorefresh(interval=15 * 1000, key="refresh_sup")

# =====================================================
# CSS PARA SUAVIZAR O REFRESH E MANTER A COR DE FUNDO
# =====================================================
st.markdown("""
<style>
/* Remove o escurecimento durante o reload */
html, body {
    background-color: #0f172a !important;
    margin: 0;
    padding: 0;
}

div.stApp > header {
    background-color: transparent !important;
}
div[data-testid="stDecoration"] {
    display: none !important;
}
div.stSpinner {
    display: none !important;
}
div[data-testid="stStatusWidget"] {
    display: none !important;
}
* {
    transition: none !important;
}
.stApp {
    background-color: #0f172a !important;
    opacity: 1 !important;
}

/* Demais estilos */
h1, h2, h3 {
    color: white !important;
}
.metric-box {
    border-radius: 30px;
    padding: 20px;
    margin: 5px;
    text-align: center;
    box-shadow: 0 8px 12px rgba(0,0,0,0.3);
    color: white;
    font-weight: bold;
}
.metric-box.metric-novo {
    background: linear-gradient(315deg, #3b82f6 0%, #2563eb 74%) !important;
}
.metric-box.metric-atendimento {
    background: linear-gradient(315deg, #b06500 0%, #5A321A 74%) !important;
}
.metric-box.metric-resolvidos {
    background: linear-gradient(315deg, #10b981 0%, #059669 74%) !important;
}
.metric-box.metric-fechado {
    background: linear-gradient(315deg, rgb(28.2%,30.1%,31.3%)) !important;
}
.metric-box.metric-aguardando {
    background: linear-gradient(315deg, #f59e0b 0%, #d97706 74%) !important;
}
.metric-value {
    font-size: 90px;
    font-weight: bold;
    margin: 5px 0;
    color: white;
}
.metric-label {
    font-size: 15px;
    text-transform: uppercase;
    opacity: 0.9;
    color: white;
}
.alert-box {
    background: linear-gradient(315deg, #ef4444 0%, #dc2626 74%) !important;
    color: white !important;
    padding: 25px !important;
    border-radius: 12px !important;
    margin: 20px 0 !important;
    border: 3px solid #991b1b !important;
    box-shadow: 0 8px 25px rgba(239, 68, 68, 0.5) !important;
    text-align: center !important;
    animation: alert-pulse 2s infinite !important;
    font-weight: bold !important;
    font-size: 30px !important;
}
@keyframes alert-pulse {
    0% { transform: scale(1); box-shadow: 0 8px 25px rgba(239,68,68,0.5); }
    50% { transform: scale(1.02); box-shadow: 0 12px 35px rgba(239,68,68,0.7); }
    100% { transform: scale(1); box-shadow: 0 8px 25px rgba(239,68,68,0.5); }
}
.stDataFrame {
    background-color: #1e293b !important;
    border: 1px solid #374151 !important;
    border-radius: 10px !important;
}
.stDataFrame thead th {
    background-color: #1e3a8a !important;
    color: white !important;
    font-weight: bold !important;
    border-bottom: 2px solid #3b82f6 !important;
}
.stDataFrame tbody td {
    background-color: #1e293b !important;
    color: white !important;
    border-bottom: 1px solid #374151 !important;
}
.stDataFrame tr:hover td {
    background-color: #2d3748 !important;
}
.footer {
    margin-top: 20px;
    padding: 15px;
    text-align: center;
    color: #9ca3af;
    font-size: 12px;
    border-top: 1px solid #374151;
    background-color: #1e293b;
    border-radius: 8px;
}
div[data-testid="stMetricValue"], 
div[data-testid="stMetricLabel"],
div[data-testid="column"] {
    background-color: transparent !important;
}
span {
    color: inherit !important;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# FUNÇÕES AUXILIARES
# =====================================================
def classificar_status(status, baseStatus, owner):
    """Classifica o ticket com prioridade: fechado > cancelado > em atendimento > novo"""
    status_lower = (status or "").lower()
    base_lower = (baseStatus or "").lower()
    
    if "cancel" in status_lower:
        return "Cancelado"
    if base_lower in ["closed", "resolved"]:
        return "Fechado"
    if "aguardando" in status_lower:
        return "Aguardando"
    # Movidesk pode retornar status em PT-BR ("Novo") e/ou baseStatus "New"
    if "novo" in status_lower or base_lower == "new" or status_lower in ["open", "new"]:
        return "Novo"
    if owner:
        return "Em atendimento"
    return "Desconhecido"

def get_risk_level(days_open):
    if days_open > 30:
        return "Alto"
    elif days_open > 20:
        return "Médio"
    return "Baixo"

def get_urgency_status(days_open, original_urgency):
    if days_open > 40:
        return "Alta"
    elif days_open > 30:
        return "Média"
    return original_urgency

def tocar_alarme():
    if not st.session_state.get("som_liberado", False):
        return

    # Caminho absoluto seguro
    BASE_DIR = Path(__file__).resolve().parent
    audio_path = BASE_DIR / "audio" / "alerta3.mp3"

    if not audio_path.exists():
        st.error(f"❌ Arquivo não encontrado: {audio_path}")
        return

    with open(audio_path, "rb") as f:
        audio_bytes = f.read()
        b64 = base64.b64encode(audio_bytes).decode()

    st.components.v1.html(f"""
        <audio autoplay>
            <source src="data:audio/wav;base64,{b64}" type="audio/wav">
        </audio>
    """, height=0)

# =====================================================
# CARREGAMENTO DE DADOS (CACHE REDUZIDO)
# =====================================================
@st.cache_data(ttl=15, show_spinner=False)
def carregar_dados():
    params = {
        "token": TOKEN,
        "$select": SELECT_FIELDS,
        "$filter": FILTER_QUERY,
        "$expand": EXPAND,
        "$orderby": "createdDate desc"
    }
    try:
        r = requests.get(URL, params=params, timeout=30)
        if r.status_code != 200:
            st.error(f"Erro API: {r.status_code}")
            return pd.DataFrame()
        data = r.json()
        registros = []
        for ticket in data:
            # Ignora cancelados na fonte
            if (ticket.get("status") or "").lower() == "canceled":
                continue

            owner = ticket.get("owner")
            tecnico = owner.get("businessName") if owner else None

            status = classificar_status(
                ticket.get("status"),
                ticket.get("baseStatus"),
                owner
            )

            data_criacao = pd.to_datetime(ticket.get("createdDate"), utc=True)
            data_criacao = data_criacao.tz_convert("America/Sao_Paulo").tz_localize(None)
            data_fechamento_raw = ticket.get("lastActionDate")
            data_fechamento = pd.NaT
            if data_fechamento_raw:
                data_fechamento = pd.to_datetime(data_fechamento_raw, utc=True)
                data_fechamento = data_fechamento.tz_convert("America/Sao_Paulo").tz_localize(None)
            agora = pd.Timestamp.now()
            dias_aberto = (agora - data_criacao).days
            is_new_24h = (agora - data_criacao).total_seconds() < 86400

            cliente = ticket.get("clients", [{}])[0]
            solicitante = cliente.get("businessName") or cliente.get("name", "Sem nome")

            urgencia_original = ticket.get("urgency") or "Não definida"
            urgencia = get_urgency_status(dias_aberto, urgencia_original)
            risco = get_risk_level(dias_aberto)

            registros.append({
                "ID": ticket.get("id"),
                "Link": f"https://grupolinsferrao.movidesk.com/Ticket/Edit/{ticket.get('id')}",
                "Status": status,
                "Assunto": ticket.get("subject") or "Sem assunto",
                "Solicitante": solicitante[:30],
                "Urgência": urgencia,
                "Dias": dias_aberto,
                "Risco": risco,
                "Técnico": tecnico if tecnico else "Sem técnico",
                "Novo_24h": is_new_24h,
                "DataCriacao": data_criacao,
                "DataFechamento": data_fechamento,
                "Criado em": data_criacao.strftime('%d/%m/%Y %H:%M'),
                "Urgência Original": urgencia_original
            })
        return pd.DataFrame(registros)
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

# =====================================================
# INTERFACE PRINCIPAL
# =====================================================
st.markdown("# 📊 Dashboard Movidesk - SUPORTE TI")
st.markdown(f"*Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}*")


# Carrega dados
df = carregar_dados()

if df.empty:
    st.warning("⚠️ Nenhum chamado encontrado.")
    st.stop()

# =====================================================
# INDICADORES (KPIs)
# =====================================================
st.markdown("### 📈 Status")

novos = len(df[(df["Status"] == "Novo") & (df["Técnico"] == "Sem técnico")])
em_atendimento = len(df[df["Status"] == "Em atendimento"])
aguardando = len(df[df["Status"] == "Aguardando"])

agora_ts = pd.Timestamp.now(tz="America/Sao_Paulo").tz_localize(None)
inicio_mes_atual = agora_ts.to_period("M").start_time
inicio_prox_mes = (agora_ts.to_period("M") + 1).start_time

limite_24h = agora_ts - pd.Timedelta(hours=24)
resolvidos_24h = len(
    df[
        (df["Status"] == "Fechado")
        & (df["DataFechamento"] >= limite_24h)
        & (df["DataFechamento"] <= agora_ts)
    ]
)
fechados = len(
    df[
        (df["Status"] == "Fechado")
        & (df["DataFechamento"] >= inicio_mes_atual)
        & (df["DataFechamento"] < inicio_prox_mes)
    ]
)

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown(f"""
    <div class="metric-box metric-novo">
        <div class="metric-label">Novos (sem técnico)</div>
        <div class="metric-value">{novos}</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="metric-box metric-aguardando">
        <div class="metric-label">Aguardando</div>
        <div class="metric-value">{aguardando}</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="metric-box metric-atendimento">
        <div class="metric-label">Em Atendimento</div>
        <div class="metric-value">{em_atendimento}</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
    <div class="metric-box metric-resolvidos">
        <div class="metric-label">Resolvidos (últ. 24h)</div>
        <div class="metric-value">{resolvidos_24h}</div>
    </div>
    """, unsafe_allow_html=True)
with col5:
    st.markdown(f"""
    <div class="metric-box metric-fechado">
        <div class="metric-label">Total Fechados</div>
        <div class="metric-value">{fechados}</div>
    </div>
    """, unsafe_allow_html=True)


with st.expander("ℹ️ Detalhes dos KPIs"):
    st.markdown("""
    - **Novos (sem técnico):** Tickets com status "Novo" que ainda não foram atribuídos a um técnico.  
    - **Em Atendimento:** Tickets que estão atualmente sendo atendidos por um técnico.  
    - **Resolvidos (últ. 24h):** Tickets que foram fechados nas últimas 24 horas.  
    - **Total Fechados:** Total de tickets com status "Fechado", considerando o mês atual.
    """)

# =====================================================
# ALERTA SONORO PROFISSIONAL — VIA KPI
# =====================================================

if "ultimo_kpi_novos" not in st.session_state:
    st.session_state.ultimo_kpi_novos = novos

# Se aumentou em relação ao último valor, toca o alarme
if novos > st.session_state.ultimo_kpi_novos:
    tocar_alarme()

# Atualiza histórico
if "ultimo_alerta_novos_at" not in st.session_state:
    st.session_state.ultimo_alerta_novos_at = None

if novos > 0 and st.session_state.get("som_liberado", False):
    agora_alerta = datetime.now()
    ultimo_alerta = st.session_state.ultimo_alerta_novos_at
    if (
        ultimo_alerta is None
        or (agora_alerta - ultimo_alerta).total_seconds() >= ALERTA_INTERVALO_SEGUNDOS
    ):
        tocar_alarme()
        st.session_state.ultimo_alerta_novos_at = agora_alerta
else:
    st.session_state.ultimo_alerta_novos_at = None

st.session_state.ultimo_kpi_novos = novos

# Alerta visual: total de chamados criados nas últimas 24h (independente de técnico)
alerta_20dias = len(df[(~df["Status"].isin(["Fechado", "Cancelado"])) & (df["Dias"] > 20 )])
if alerta_20dias > 0:
    st.markdown(f"""
    <div class="alert-box">
        {alerta_20dias} CHAMADO(S) ABERTO(S) COM MAIS DE 20 DIAS
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("✅ Nenhum chamado com mais de 20 dias aberto.")

st.markdown("---")

# =====================================================
# TABELA PRINCIPAL (CHAMADOS ATIVOS)
# =====================================================
st.markdown("###  Chamados Ativos (Em aberto / Em atendimento)")

# Filtra apenas os que não são fechados, cancelados!
df_display = df[~df["Status"].isin(["Fechado", "Cancelado"])].copy()

if df_display.empty:
    st.info(" Todos os chamados estão resolvidos.")
else:
    def format_status(s):
        if s == "Novo":
            return "🆕 Novo"
        elif s == "Em atendimento":
            return "🟡 Em Atend."
        elif s == "Aguardando":
            return "🔵 Aguardando"
        elif s == "Aberto":
            return "🟢 Aberto"
        else:
            return s
        

    def format_urgency(row):
        if row["Dias"] > 40:
            return "🔥 +40 dias"
        if row["Dias"] > 30:
            return "⚠️ +30 dias"
        if row["Urgência"] == "Alta":
            return "🔴 Alta"
        if row["Urgência"] == "Média":
            return "🟡 Média"
        if row["Urgência"] == "Baixa":
            return "🟢 Baixa"
        return "⚪ " + row["Urgência"]
    

    df_display["Status"] = df_display["Status"].apply(format_status)
    df_display["Urgência"] = df_display.apply(format_urgency, axis=1)
    ordem_risco = {"Alto": 0, "Médio": 1, "Baixo": 2}
    df_display["_ordem_risco"] = df_display["Risco"].map(ordem_risco)
    df_display = df_display.sort_values(by=["Dias", "_ordem_risco"], ascending=[False, True])
    df_display.drop("_ordem_risco", axis=1, inplace=True)

    df_table = df_display[[
        "Técnico", "ID", "Assunto", "Solicitante",
        "Status", "Urgência", "Risco", "Dias", "Link"
    ]].rename(columns={
        "ID": "Ticket",
        "Dias": "Dias Abertos",
        "Link": "Ação"
    })

    st.dataframe(
        df_table,
        use_container_width=True,
        height=500,
        hide_index=True,
        column_config={
            "Técnico": st.column_config.Column(width="medium"),
            "Ticket": st.column_config.Column(width="small"),
            "Assunto": st.column_config.Column(width="large"),
            "Solicitante": st.column_config.Column(width="medium"),
            "Status": st.column_config.Column(width="small"),
            "Urgência": st.column_config.Column(width="small"),
            "Risco": st.column_config.Column(width="small"),
            "Dias Abertos": st.column_config.ProgressColumn(
                "Dias",
                format="%d dias",
                min_value=0,
                max_value=90,
                width="medium"
            ),
            "Ação": st.column_config.LinkColumn(
                "Abrir",
                display_text="🔗 Abrir",
                width="small"
            )
        }
    )

# =====================================================
# RESUMO POR TEMPO
# =====================================================
st.markdown("---")
st.markdown("### 📊 Resumo por Tempo (Abertos + Em atendimento)")

ativos = df[~df["Status"].isin(["Fechado", "Cancelado", "Novo"])]
ate_10 = len(ativos[ativos["Dias"] <= 10])
ate_20 = len(ativos[(ativos["Dias"] > 10) & (ativos["Dias"] <= 20)])
ate_30 = len(ativos[(ativos["Dias"] > 20) & (ativos["Dias"] <= 30)])
mais_40 = len(ativos[ativos["Dias"] > 40])

col_r1, col_r2, col_r3, col_r4 = st.columns(4)
col_r1.metric("Até 10 dias", ate_10)
col_r2.metric("11-20 dias", ate_20)
col_r3.metric("21-30 dias", ate_30)
col_r4.metric("+40 dias", mais_40)

# =====================================================
# LEGENDA E RODAPÉ
# =====================================================
with st.expander("🎨 Legenda de Cores"):
    st.markdown("""
    **Status:**  
    🔵 Aberto - Aguardando atendimento (sem técnico)  
    🟡 Em Atendimento - Em andamento  

    **Urgência:**  
    🔴 Alta - Crítico  
    🟡 Média - Atenção  
    🟢 Baixa - Normal  
    🔥 +40 dias - Urgência forçada ALTA  
    ⚠️ +30 dias - Urgência forçada MÉDIA  

    **Risco:**  
    🔴 Alto - +30 dias  
    🟡 Médio - 21-30 dias  
    🟢 Baixo - Até 20 dias  
    """)

st.markdown("---")
st.markdown("""
<div class="footer">
    📊 Dashboard Movidesk - Suporte TI | 
    🔴 +40 dias = Urgência ALTA | 
    ⚠️ +30 dias = Risco ALTO | 
    ⚡ Atualização a cada 15 segundos (sem flash)
</div> 
""", unsafe_allow_html=True)

# Controle de som
if "som_liberado" not in st.session_state:
    st.session_state.som_liberado = False

col_som1, col_som2 = st.columns([1, 5])
with col_som1:
    if st.button("🔊 Ativar/Desativar Som"):
        st.session_state.som_liberado = not st.session_state.som_liberado
        status = "ativados" if st.session_state.som_liberado else "desativados"
        st.success(f"Alertas sonoros {status}!")
with col_som2:
    if st.session_state.som_liberado:
        st.markdown("🔔 **Som ativo**")
    else:
        st.markdown("🔇 **Som desativado**")

# Botão de teste (opcional)
if st.button("🔊 TESTAR ALARME"):
    tocar_alarme()
