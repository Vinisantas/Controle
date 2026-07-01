import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
from dotenv import load_dotenv

# 🔑 carregar variáveis de ambiente
load_dotenv()
TOKEN = os.getenv("TOKEN")
PROJECT_ID = os.getenv("PROJECT_ID")

# =====================================================
# PAGE CONFIG 
# =====================================================
st.set_page_config(
    page_title="Dashboard TI - Movidesk & Asana",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="collapsed"
)

# Atualiza a cada 60 segundos
st_autorefresh(interval=60 * 1000, key="refresh_estoque")

# =====================================================
# CSS 
# =====================================================
st.markdown("""
<style>
/* FUNDO ESCURO */
.stApp {
    background-color: #0f172a;
    color: white;
}

/* TÍTULOS AJUSTADOS PARA TV */
h1 {
    font-size: 42px !important;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 20px !important;
}

h2 {
    font-size: 28px !important;
    margin-top: 25px !important;
    margin-bottom: 15px !important;
    color: white !important;
}

h3 {
    font-size: 22px !important;
    color: white !important;
}

/* CARDS DE MÉTRICAS - TAMANHO OTIMIZADO PARA TV */
.metric-box {
    border-radius: 15px;
    padding: 15px;
    margin: 8px 5px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    color: white;
    font-weight: bold;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.metric-box:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.4);
}

/* CORES DOS CARDS ASANA */
.metric-solicitacao {
    background: linear-gradient(135deg, #8b5cf6, #7c3aed) !important;
    border-bottom: 4px solid #c084fc;
}

.metric-emandamento {
    background: linear-gradient(135deg, #f59e0b, #d97706) !important;
    border-bottom: 4px solid #fbbf24;
}

.metric-concluido {
    background: linear-gradient(135deg, #10b981, #047857) !important;
    border-bottom: 4px solid #34d399;
}

/* CORES DOS CARDS MOVIDESK */
.metric-novo {
    background: linear-gradient(135deg, #ef4444, #dc2626) !important;
    border-bottom: 4px solid #fca5a5;
}

.metric-aberto {
    background: linear-gradient(135deg, #22c55e, #16a34a) !important;
    border-bottom: 4px solid #86efac;
}

.metric-atendimento {
    background: linear-gradient(135deg, #f59e0b, #d97706) !important;
    border-bottom: 4px solid #fbbf24;
}

.metric-fechado {
    background: linear-gradient(135deg, #6b7280, #4b5563) !important;
    border-bottom: 4px solid #9ca3af;
}

/* CORES DOS CARDS DE TEMPO */
.metric-tempo-verde {
    background: linear-gradient(135deg, #10b981, #059669) !important;
    border-bottom: 4px solid #34d399;
}

.metric-tempo-amarelo {
    background: linear-gradient(135deg, #f59e0b, #d97706) !important;
    border-bottom: 4px solid #fbbf24;
}

.metric-tempo-vermelho {
    background: linear-gradient(135deg, #ef4444, #dc2626) !important;
    border-bottom: 4px solid #fca5a5;
}

.metric-value {
    font-size: 48px;
    font-weight: bold;
    margin: 5px 0;
    color: white;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.metric-label {
    font-size: 13px;
    text-transform: uppercase;
    opacity: 0.9;
    color: white;
    letter-spacing: 1px;
}

.metric-sub {
    font-size: 10px;
    margin-top: 5px;
    opacity: 0.8;
}

/* TABELAS MELHORADAS */
.stDataFrame {
    background-color: #1e293b !important;
    border: 1px solid #374151 !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

.stDataFrame thead th {
    background: linear-gradient(135deg, #1e3a8a, #1e40af) !important;
    color: white !important;
    font-weight: bold !important;
    font-size: 13px !important;
    padding: 10px !important;
}

.stDataFrame tbody td {
    background-color: #1e293b !important;
    color: #e2e8f0 !important;
    padding: 8px !important;
    border-bottom: 1px solid #334155 !important;
}

.stDataFrame tbody tr:hover td {
    background-color: #334155 !important;
    transition: background-color 0.2s ease;
}

/* PROGRESS BAR */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important;
}

/* EXPANDER */
.streamlit-expanderHeader {
    background: linear-gradient(135deg, #1e293b, #0f172a) !important;
    color: white !important;
    border-radius: 10px !important;
    font-weight: bold !important;
}

/* FOOTER */
.footer {
    margin-top: 30px;
    padding: 15px;
    text-align: center;
    color: #94a3b8;
    font-size: 11px;
    border-top: 1px solid #334155;
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border-radius: 12px;
}

/* BOTÕES DE DOWNLOAD */
.stDownloadButton button {
    background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 8px 16px !important;
    font-weight: bold !important;
}

.stDownloadButton button:hover {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    transform: translateY(-2px);
    transition: all 0.3s ease;
}

/* DIVIDERS */
hr {
    border-color: #334155 !important;
    margin: 20px 0 !important;
}

/* MÉTRICAS DO STREAMLIT */
[data-testid="stMetricValue"] {
    font-size: 24px !important;
    color: white !important;
}

[data-testid="stMetricLabel"] {
    font-size: 13px !important;
    color: #cbd5e1 !important;
}

/* INFO BOX SEM ALERTA */
.info-normal {
    background: linear-gradient(135deg, #1e293b, #0f172a) !important;
    color: #cbd5e1 !important;
    padding: 10px !important;
    border-radius: 8px !important;
    margin: 10px 0 !important;
    text-align: center !important;
    font-size: 13px !important;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# FUNÇÕES MOVIDESK
# =====================================================
def normalizar_status(status, base):
    status = (status or "").lower()
    base = (base or "").lower()
    if base in ["closed", "resolved"]:
        return "Fechado"
    if any(x in status for x in ["atendimento", "andamento", "análise", "analise", "aguardando"]):
        return "Em atendimento"
    return "Aberto"

def get_risk_level(days_open):
    if days_open > 30:
        return "Alto"
    elif days_open > 20:
        return "Médio"
    else:
        return "Baixo"

def get_urgency_status(days_open, original_urgency):
    if days_open > 40:
        return "Alta"
    elif days_open > 30:
        return "Média"
    else:
        return original_urgency

# =====================================================
# CARREGAR DADOS MOVIDESK
# =====================================================
@st.cache_data(ttl=120)
def carregar_dados_movidesk():
    URL = "https://api.movidesk.com/public/v1/tickets"
    TOKEN_MOVIDESK = "b9991fdc-6754-4153-ac49-4c0116c1b4d1"
    FILTER_QUERY = "(ownerTeam eq 'Estoque TI')"
    SELECT_FIELDS = "id,status,baseStatus,subject,createdDate,clients,urgency,lastActionDate"
    EXPAND = "clients($expand=organization)"
    
    params = {
        "token": TOKEN_MOVIDESK,
        "$select": SELECT_FIELDS,
        "$filter": FILTER_QUERY,
        "$expand": EXPAND,
        "$orderby": "createdDate desc"
    }

    try:
        r = requests.get(URL, params=params, timeout=30)
        if r.status_code != 200:
            st.error(f"❌ Erro API Movidesk: {r.status_code}")
            return pd.DataFrame()

        lista = []
        for t in r.json():
            status = normalizar_status(t.get("status"), t.get("baseStatus"))
            data_criacao = pd.to_datetime(t.get("createdDate"), utc=True)\
                .tz_convert("America/Sao_Paulo")\
                .tz_localize(None)
            data_fechamento_raw = t.get("lastActionDate")
            data_fechamento = pd.NaT
            if data_fechamento_raw:
                data_fechamento = pd.to_datetime(data_fechamento_raw, utc=True)\
                    .tz_convert("America/Sao_Paulo")\
                    .tz_localize(None)

            agora = pd.Timestamp.now()
            dias_aberto = (agora - data_criacao).days
            
            is_new = (agora - data_criacao).total_seconds() < 86400
            
            cliente = t.get("clients")[0] if t.get("clients") else {}
            urgencia_original = t.get("urgency") or "Não definida"
            urgencia = get_urgency_status(dias_aberto, urgencia_original)
            risco = get_risk_level(dias_aberto)
            
            lista.append({
                "ID": t.get("id"),
                "Link": f"https://grupolinsferrao.movidesk.com/Ticket/Edit/{t.get('id')}",
                "Status": status,
                "Assunto": t.get("subject") or "Sem assunto",
                "Solicitante": (cliente.get("businessName") or cliente.get("name", ""))[:30],
                "Urgência": urgencia,
                "Dias": dias_aberto,
                "Risco": risco,
                "Novo": "🆕" if is_new else "",
                "DataCriacao": data_criacao,
                "DataFechamento": data_fechamento,
                "Criado em": data_criacao.strftime('%d/%m/%Y'),
                "Horario": data_criacao.strftime('%H:%M'),
                "Urgência Original": urgencia_original
            })

        return pd.DataFrame(lista)
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar Movidesk: {str(e)}")
        return pd.DataFrame()

# =====================================================
# CARREGAR DADOS ASANA
# =====================================================
@st.cache_data(ttl=120)
def carregar_dados_asana():
    if not PROJECT_ID:
        st.warning("⚠️ PROJECT_ID não configurado no arquivo .env")
        return pd.DataFrame()
    
    url = f"https://app.asana.com/api/1.0/projects/{PROJECT_ID}/tasks"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    params = {
        "opt_fields": ",".join([
            "name",
            "notes",
            "completed",
            "created_at",
            "due_on",
            "assignee.name",
            "created_by.name",
            "memberships.section.name",
            "custom_fields.name",
            "custom_fields.display_value",
            "custom_fields.text_value",
            "custom_fields.enum_value.name",
            "custom_fields.multi_enum_values.name"
        ])
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code != 200:
            st.error(f"❌ Erro na API Asana: {response.status_code}")
            return pd.DataFrame()

        data = response.json()
        
        def get_safe(obj, path):
            try:
                for key in path:
                    obj = obj[key]
                return obj
            except (KeyError, IndexError, TypeError):
                return None

        tasks_list = []
        for task in data.get('data', []):
            custom_data = {}

            for field in task.get('custom_fields', []):
                nome = field.get('name', 'Campo Desconhecido')
                if field.get('text_value'):
                    valor = field.get('text_value')
                elif field.get('enum_value'):
                    valor = field.get('enum_value').get('name')
                elif field.get('multi_enum_values'):
                    valores = field.get('multi_enum_values')
                    valor = ", ".join([v.get('name', '') for v in valores]) if valores else "Não informado"
                else:
                    valor = field.get('display_value', "Não informado")
                custom_data[nome] = valor

            status_real = custom_data.get("Status", "Nova Solicitação")
            separador_real = custom_data.get("Separador ", "Não informado")
            tipo_status = "🆕 Novo" if separador_real in ["Não informado", None, ""] else "📋 Em fluxo"

            tasks_list.append({
                "Título": task.get('name', 'Sem título'),
                "Status": status_real,
                "Separador": separador_real,
                "Tipo": tipo_status,
                "Solicitante": custom_data.get("Nome Solicitante - Suporte Técnico", "Não informado"),
                "Empresa": custom_data.get("empresa", "Não informado"),
                "Lojas": custom_data.get("Lojas", "Não informado"),
                "Tipo_Solicitacao": custom_data.get("Tipo Solicitação", "Não informado"),
                "Chamado": custom_data.get("Chamado", "Não informado"),
                "Responsável": get_safe(task, ['assignee', 'name']) or "Não informado",
                "Seção": get_safe(task, ['memberships', 0, 'section', 'name']) or "Não informado",
            })

        df = pd.DataFrame(tasks_list)
        df.fillna("Não informado", inplace=True)
        return df
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar Asana: {str(e)}")
        return pd.DataFrame()

# =====================================================
# HEADER PRINCIPAL
# =====================================================
st.markdown("# 📊 Dashboard Integrado - TI | Estoque")
st.caption(f"🕐 Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} ")

# =====================================================
# CARREGAR TODOS OS DADOS
# =====================================================
with st.spinner("🔄 Carregando dados..."):
    df_asana = carregar_dados_asana()
    df_movidesk = carregar_dados_movidesk()

# =====================================================
# SEÇÃO 1: TODOS OS KPIs NO TOPO
# =====================================================
st.markdown("---")

# Primeira linha: KPIs do Asana
st.markdown("### 🎯 Solicitações de Equipamento - Asana")

if not df_asana.empty:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        novas_solicitacoes = len(df_asana[df_asana["Tipo"] == "🆕 Novo"])
        st.markdown(f"""
            <div class="metric-box metric-solicitacao">
                <div class="metric-label">📦 NOVAS SOLICITAÇÕES</div>
                <div class="metric-value">{novas_solicitacoes}</div>
                <div class="metric-sub">Aguardando separador</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        em_andamento = len(df_asana[df_asana["Status"] == "Em Andamento"])
        st.markdown(f"""
            <div class="metric-box metric-emandamento">
                <div class="metric-label">⚙️ EM ANDAMENTO</div>
                <div class="metric-value">{em_andamento}</div>
                <div class="metric-sub">Tarefas em execução</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        concluidos = len(df_asana[df_asana["Status"] == "Concluído"])
        st.markdown(f"""
            <div class="metric-box metric-concluido">
                <div class="metric-label">✅ CONCLUÍDOS</div>
                <div class="metric-value">{concluidos}</div>
                <div class="metric-sub">Total entregue</div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div class="info-normal">
            📭 Nenhuma solicitação de equipamento encontrada no Asana
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Segunda linha: KPIs do Movidesk
st.markdown("### 🖥️ Chamados Estoque TI - Movidesk")

if not df_movidesk.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        novos = len(df_movidesk[df_movidesk["Novo"] == "🆕"])
        st.markdown(f"""
        <div class="metric-box metric-novo">
            <div class="metric-label">🆕 NOVOS (24h)</div>
            <div class="metric-value">{novos}</div>
            <div class="metric-sub">Último dia</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        abertos = len(df_movidesk[df_movidesk["Status"] == "Aberto"])
        st.markdown(f"""
        <div class="metric-box metric-aberto">
            <div class="metric-label">📋 ABERTOS</div>
            <div class="metric-value">{abertos}</div>
            <div class="metric-sub">Aguardando atendimento</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        em_atendimento = len(df_movidesk[df_movidesk["Status"] == "Em atendimento"])
        st.markdown(f"""
        <div class="metric-box metric-atendimento">
            <div class="metric-label">⚙️ EM ATENDIMENTO</div>
            <div class="metric-value">{em_atendimento}</div>
            <div class="metric-sub">Em andamento</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        agora_ts = pd.Timestamp.now(tz="America/Sao_Paulo").tz_localize(None)
        inicio_mes_atual = agora_ts.to_period("M").start_time
        inicio_prox_mes = (agora_ts.to_period("M") + 1).start_time
        fechados = len(
            df_movidesk[
                (df_movidesk["Status"] == "Fechado")
                & (df_movidesk["DataFechamento"] >= inicio_mes_atual)
                & (df_movidesk["DataFechamento"] < inicio_prox_mes)
            ]
        )
        st.markdown(f"""
        <div class="metric-box metric-fechado">
            <div class="metric-label">✅ FECHADOS</div>
            <div class="metric-value">{fechados}</div>
            <div class="metric-sub">Neste mês</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Cards de Métricas de Tempo (coloridos)
    st.markdown("#### ⏱️ Métricas de Tempo - Chamados Ativos")
    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    
    chamados_ativos = df_movidesk[df_movidesk["Status"] != "Fechado"]
    
    with col_t1:
        tempo_medio = chamados_ativos["Dias"].mean() if not chamados_ativos.empty else 0
        cor_tempo = "metric-tempo-verde" if tempo_medio <= 15 else "metric-tempo-amarelo" if tempo_medio <= 30 else "metric-tempo-vermelho"
        st.markdown(f"""
            <div class="metric-box {cor_tempo}">
                <div class="metric-label">⏱️ TEMPO MÉDIO</div>
                <div class="metric-value">{tempo_medio:.1f}</div>
                <div class="metric-sub">dias em aberto</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col_t2:
        tempo_maximo = chamados_ativos["Dias"].max() if not chamados_ativos.empty else 0
        cor_max = "metric-tempo-verde" if tempo_maximo <= 30 else "metric-tempo-amarelo" if tempo_maximo <= 40 else "metric-tempo-vermelho"
        st.markdown(f"""
            <div class="metric-box {cor_max}">
                <div class="metric-label">⚠️ TEMPO MÁXIMO</div>
                <div class="metric-value">{tempo_maximo}</div>
                <div class="metric-sub">dias em aberto</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col_t3:
        tickets_criticos = len(chamados_ativos[chamados_ativos["Dias"] > 30])
        cor_critico = "metric-tempo-verde" if tickets_criticos == 0 else "metric-tempo-amarelo" if tickets_criticos <= 3 else "metric-tempo-vermelho"
        st.markdown(f"""
            <div class="metric-box {cor_critico}">
                <div class="metric-label">🔥 +30 DIAS</div>
                <div class="metric-value">{tickets_criticos}</div>
                <div class="metric-sub">chamados críticos</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col_t4:
        tickets_urgentes = len(chamados_ativos[chamados_ativos["Dias"] > 40])
        cor_urgente = "metric-tempo-verde" if tickets_urgentes == 0 else "metric-tempo-vermelho"
        st.markdown(f"""
            <div class="metric-box {cor_urgente}">
                <div class="metric-label">🚨 +40 DIAS</div>
                <div class="metric-value">{tickets_urgentes}</div>
                <div class="metric-sub">prioridade máxima</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Distribuição por tempo
    st.markdown("#### 📊 Distribuição por Tempo de Abertura")
    col_res1, col_res2, col_res3, col_res4 = st.columns(4)
    
    with col_res1:
        ate_7 = len(chamados_ativos[chamados_ativos["Dias"] <= 7])
        st.metric("📅 Até 7 dias", ate_7)
    
    with col_res2:
        ate_30 = len(chamados_ativos[(chamados_ativos["Dias"] > 7) & (chamados_ativos["Dias"] <= 30)])
        st.metric("📅 8-30 dias", ate_30)
    
    with col_res3:
        ate_40 = len(chamados_ativos[(chamados_ativos["Dias"] > 30) & (chamados_ativos["Dias"] <= 40)])
        st.metric("📅 31-40 dias", ate_40)
    
    with col_res4:
        mais_40 = len(chamados_ativos[chamados_ativos["Dias"] > 40])
        st.metric("📅 +40 dias", mais_40)
else:
    st.markdown("""
        <div class="info-normal">
            ⚠️ Nenhum chamado encontrado no Movidesk
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# =====================================================
# SEÇÃO 2: TABELAS DETALHADAS
# =====================================================

# Tabela do Asana
with st.expander("📋 Detalhamento das Solicitações de Equipamento", expanded=True):
    if not df_asana.empty:
        df_asana_ativas = df_asana[df_asana["Status"] != "Concluído"]
        if not df_asana_ativas.empty:
            st.dataframe(
                df_asana_ativas[["Tipo", "Título", "Status", "Separador", "Solicitante", "Empresa", "Tipo_Solicitacao", "Lojas"]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Tipo": st.column_config.Column(width="small"),
                    "Título": st.column_config.Column(width="medium"),
                    "Status": st.column_config.Column(width="small"),
                    "Separador": st.column_config.Column(width="medium"),
                    "Solicitante": st.column_config.Column(width="medium"),
                    "Empresa": st.column_config.Column(width="small"),
                    "Tipo_Solicitacao": st.column_config.Column(width="small"),
                    "lojas": st.column_config.Column(width="small")
                }
            )
            st.markdown(f"""
                <div class="info-normal">
                    📊 {len(df_asana_ativas)} solicitações ativas | {len(df_asana_ativas[df_asana_ativas['Tipo'] == '🆕 Novo'])} aguardando separador
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="info-normal">
                    ✅ Todas as solicitações foram concluídas! 🎉
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="info-normal">
                📭 Nenhuma solicitação de equipamento encontrada
            </div>
        """, unsafe_allow_html=True)



        

# Tabela do Movidesk
with st.expander("📋 Chamados Ativos - Estoque TI", expanded=True):
    if not df_movidesk.empty:
        df_display = df_movidesk[df_movidesk["Status"] != "Fechado"].copy()
        
        if df_display.empty:
            st.markdown("""
                <div class="info-normal">
                    🎉 Todos os chamados estão resolvidos! 🎉
                </div>
            """, unsafe_allow_html=True)
        else:
            # Formatar para exibição
            df_display["Status_icon"] = df_display["Status"].apply(
                lambda x: "🟢 Aberto" if x == "Aberto" else "🟡 Em Atend."
            )
            df_display["Urgência_icon"] = df_display.apply(
                lambda x: "🔥 CRÍTICA" if x["Dias"] > 40 else "⚠️ URGENTE" if x["Dias"] > 30 else "🔴 Alta" if x["Urgência"] == "Alta" else "🟡 Média" if x["Urgência"] == "Média" else "🟢 Baixa",
                axis=1
            )
            df_display["Risco_icon"] = df_display["Dias"].apply(
                lambda x: "🔴 ALTO" if x > 30 else "🟡 Médio" if x > 20 else "🟢 Baixo"
            )
            
            # Ordenar por prioridade
            df_display = df_display.sort_values("Dias", ascending=False)
            
            st.dataframe(
                df_display[["Novo", "ID", "Assunto", "Solicitante", "Status_icon", "Urgência_icon", "Risco_icon", "Dias", "Link"]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Novo": st.column_config.Column(width="small"),
                    "ID": st.column_config.Column(width="small"),
                    "Assunto": st.column_config.Column(width="large"),
                    "Solicitante": st.column_config.Column(width="medium"),
                    "Status_icon": st.column_config.Column(width="small"),
                    "Urgência_icon": st.column_config.Column(width="small"),
                    "Risco_icon": st.column_config.Column(width="small"),
                    "Dias": st.column_config.ProgressColumn(
                        "Dias", format="%d dias", min_value=0, max_value=90, width="small"
                    ),
                    "Link": st.column_config.LinkColumn("Abrir", display_text="🔗", width="small")
                }
            )
    else:
        st.markdown("""
            <div class="info-normal">
                ⚠️ Nenhum chamado encontrado no Movidesk
            </div>
        """, unsafe_allow_html=True)

# =====================================================
# SEÇÃO 3: DOWNLOAD DE RELATÓRIOS
# =====================================================
with st.expander("📥 Download de Relatórios"):
    col_down1, col_down2 = st.columns(2)
    
    with col_down1:
        st.markdown("**📊 Relatório Movidesk**")
        if not df_movidesk.empty:
            csv_movidesk = df_movidesk.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar CSV - Movidesk",
                data=csv_movidesk,
                file_name=f"movidesk_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            # Estatísticas rápidas
            st.markdown("**📈 Estatísticas Rápidas:**")
            st.write(f"- Total de chamados: {len(df_movidesk)}")
            st.write(f"- Chamados ativos: {len(df_movidesk[df_movidesk['Status'] != 'Fechado'])}")
            st.write(f"- Média de dias: {df_movidesk['Dias'].mean():.1f}")
    
    with col_down2:
        st.markdown("**🎯 Relatório Asana**")
        if not df_asana.empty:
            csv_asana = df_asana.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar CSV - Asana",
                data=csv_asana,
                file_name=f"asana_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            # Estatísticas rápidas
            st.markdown("**📈 Estatísticas Rápidas:**")
            st.write(f"- Total de solicitações: {len(df_asana)}")
            st.write(f"- Solicitações ativas: {len(df_asana[df_asana['Status'] != 'Concluído'])}")
            st.write(f"- Aguardando separador: {len(df_asana[df_asana['Tipo'] == '🆕 Novo'])}")

# =====================================================
# SEÇÃO 4: TOP SOLICITANTES
# =====================================================
if not df_movidesk.empty:
    with st.expander("🏆 Top Solicitantes - Ranking"):
        top_solicitantes = df_movidesk[df_movidesk['Status'] != 'Fechado']['Solicitante'].value_counts().head(10)
        if not top_solicitantes.empty:
            st.markdown("**Top 10 solicitantes com chamados ativos:**")
            for i, (solicitante, qtd) in enumerate(top_solicitantes.items(), 1):
                st.markdown(f"{i}. **{solicitante}** - {qtd} chamado(s)")
        else:
            st.markdown("""
                <div class="info-normal">
                    📭 Nenhum chamado ativo no momento
                </div>
            """, unsafe_allow_html=True)

# =====================================================
# LEGENDA DE CORES
# =====================================================
with st.expander("🎨 Guia de Cores e Status"):
    col_leg1, col_leg2, col_leg3 = st.columns(3)
    
    with col_leg1:
        st.markdown("**🎯 Asana - Solicitações**")
        st.markdown("🆕 **Novo** - Aguardando separador")
        st.markdown("🟠 **Em Andamento** - Em execução")
        st.markdown("✅ **Concluído** - Entregue")
        st.markdown("---")
        st.markdown("**🖥️ Movidesk - Status**")
        st.markdown("🟢 **Aberto** - Normal")
        st.markdown("🟡 **Em Atendimento** - Em andamento")
        st.markdown("🔘 **Fechado** - Resolvido")
    
    with col_leg2:
        st.markdown("**🖥️ Movidesk - Urgência**")
        st.markdown("🔥 **CRÍTICA** - +40 dias")
        st.markdown("⚠️ **URGENTE** - +30 dias")
        st.markdown("🔴 **Alta**")
        st.markdown("🟡 **Média**")
        st.markdown("🟢 **Baixa**")
        st.markdown("---")
        st.markdown("**⏱️ Tempo Médio**")
        st.markdown("🟢 **Verde** - ≤ 15 dias")
        st.markdown("🟡 **Amarelo** - 16-30 dias")
        st.markdown("🔴 **Vermelho** - > 30 dias")
    
    with col_leg3:
        st.markdown("**🖥️ Movidesk - Risco**")
        st.markdown("🔴 **ALTO** - +30 dias")
        st.markdown("🟡 **Médio** - 21-30 dias")
        st.markdown("🟢 **Baixo** - Até 20 dias")
        st.markdown("---")
        st.markdown("**📊 Progresso**")
        st.markdown("Barra colorida indica tempo decorrido")
        st.markdown("**💡 Dica:**")
        st.markdown("Passe o mouse nos cards para animação")

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.markdown("""
<div class="footer">
    <strong>📊 Dashboard Integrado - TI | Modo TV 55"</strong><br>
    🎯 Asana: Solicitações de Equipamento | 🖥️ Movidesk: Chamados Estoque TI<br>
    🔥 +40 dias = CRÍTICO | ⚠️ +30 dias = URGENTE | 🕒 Atualização: 60 segundos<br>
    💡 Clique nos links para abrir os chamados | Baixe relatórios na seção de downloads
</div> 
""", unsafe_allow_html=True)

st.caption("🔄 Dashboard atualiza automaticamente a cada 60 segundos | 📦 Novas solicitações em destaque")