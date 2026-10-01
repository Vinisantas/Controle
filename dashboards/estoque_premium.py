import streamlit as st
import pandas as pd
import requests
import os
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from dotenv import load_dotenv

# Carrega as credenciais do .env localizado na raiz do projeto.
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
TOKEN = os.getenv("ASANA_TOKEN")
PROJECT_ID = os.getenv("ASANA_PROJECT_ID")

# =====================================================
# CONFIGURAÇÃO DE CAMINHOS PARA BACKUP LOCAL (FALLBACK)
# =====================================================
BACKUP_DIR = "cache_backup"
os.makedirs(BACKUP_DIR, exist_ok=True)

PATH_BACKUP_MOVIDESK = os.path.join(BACKUP_DIR, "backup_movidesk.parquet")
PATH_TS_MOVIDESK = os.path.join(BACKUP_DIR, "timestamp_movidesk.txt")

PATH_BACKUP_ASANA = os.path.join(BACKUP_DIR, "backup_asana.parquet")
PATH_TS_ASANA = os.path.join(BACKUP_DIR, "timestamp_asana.txt")


# =====================================================
# FUNÇÕES DE SUPORTE AO BACKUP
# =====================================================
def salvar_backup_local(df: pd.DataFrame, path_dados: str, path_ts: str):
    """Salva os dados tratados em formato Parquet e atualiza o timestamp do backup."""
    try:
        df.to_parquet(path_dados, index=False)
        with open(path_ts, "w") as f:
            f.write(str(time.time()))
    except Exception as e:
        st.warning(f"Não foi possível salvar o backup local em {path_dados}: {e}")

def obter_tempo_ultimo_backup(path_ts: str) -> float:
    """Retorna o timestamp do último backup bem-sucedido."""
    if os.path.exists(path_ts):
        try:
            with open(path_ts, "r") as f:
                return float(f.read().strip())
        except ValueError:
            pass
    return 0.0


# =====================================================
# RENDERIZAÇÃO DO STATUS DA CONEXÃO NA SIDEBAR
# =====================================================
def renderizar_status_conexoes(status_movidesk: str, status_asana: str):
    """Renderiza na barra lateral o estado de conexão de cada serviço."""
    st.sidebar.markdown("## 🔌 Status das Integrações")
    st.sidebar.markdown("---")

    # --- STATUS MOVIDESK ---
    st.sidebar.markdown("### 🖥️ Movidesk (Chamados)")
    ts_movid = obter_tempo_ultimo_backup(PATH_TS_MOVIDESK)

    if status_movidesk == "ONLINE":
        st.sidebar.markdown("🟢 **Online** (Tempo Real)")
        st.sidebar.caption("Sincronizado com a API com sucesso.")
    elif status_movidesk == "FALLBACK" and ts_movid > 0:
        minutos = int((time.time() - ts_movid) // 60)
        if minutos < 5:
            st.sidebar.markdown("🟡 **Instabilidade detectada**")
            st.sidebar.caption(f"Exibindo cache de {minutos} min atrás.")
        else:
            st.sidebar.markdown("🟠 **Modo Contingência**")
            st.sidebar.error(f"Sem conexão há {minutos} min. Exibindo dados de cache.")
    else:
        st.sidebar.markdown("🔴 **Desconectado**")
        st.sidebar.error("Sem conexão e sem backup local disponível.")

    st.sidebar.markdown("---")

    # --- STATUS ASANA ---
    st.sidebar.markdown("### 🎯 Asana (Solicitações)")
    ts_asana = obter_tempo_ultimo_backup(PATH_TS_ASANA)

    if status_asana == "ONLINE":
        st.sidebar.markdown("🟢 **Online** (Tempo Real)")
        st.sidebar.caption("Sincronizado com a API com sucesso.")
    elif status_asana == "FALLBACK" and ts_asana > 0:
        minutos = int((time.time() - ts_asana) // 60)
        if minutos < 5:
            st.sidebar.markdown("🟡 **Instabilidade detectada**")
            st.sidebar.caption(f"Exibindo cache de {minutos} min atrás.")
        else:
            st.sidebar.markdown("🟠 **Modo Contingência**")
            st.sidebar.error(f"Sem conexão há {minutos} min. Exibindo dados de cache.")
    else:
        st.sidebar.markdown("🔴 **Desconectado**")
        st.sidebar.error("Sem conexão e sem backup local disponível.")


# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================
def render_estoque():
    # Atualiza o dashboard automaticamente a cada 60 segundos
    st_autorefresh(interval=60 * 1000, key="refresh_estoque")

    # =====================================================
    # CSS PERSONALIZADO (OTIMIZADO PARA TV/MODO ESCURO)
    # =====================================================
    st.markdown("""
    <style>
    /* FUNDO ESCURO */
    .stApp {
        background: radial-gradient(circle at 12% 0%, rgba(164,38,48,.12), transparent 28%), #070C10 !important;
        color: #F4F6F7 !important;
    }
    .block-container {
        max-width: 1500px !important;
        padding: 34px 42px 44px !important;
    }
    [data-testid="stHeader"] { background: transparent !important; }
    hr { border-color: #243038 !important; opacity: .7; }
    .stCaption, small { color: #829099 !important; }

    /* TÍTULOS */
    h1 {
        font-size: 36px !important;
        background: none;
        -webkit-background-clip: text;
        -webkit-text-fill-color: #F5F7F8;
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

    /* KPI CARDS — visual premium com hierarquia e acentos por categoria */
    .metric-box {
        position: relative;
        isolation: isolate;
        min-height: 142px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        overflow: hidden;
        border-radius: 17px;
        padding: 21px 22px 19px;
        margin: 8px 3px 12px;
        text-align: center;
        background: linear-gradient(145deg, var(--metric-bg, #26343D) 0%, var(--metric-bg-deep, #1A252C) 100%) !important;
        border: 1px solid var(--metric-border, #3A4A54) !important;
        box-shadow: 0 8px 22px rgba(0,0,0,.18), inset 0 1px 0 rgba(255,255,255,.035);
        color: #F5F7F8;
        font-weight: 600;
        transition: transform .22s ease, border-color .22s ease, box-shadow .22s ease;
    }
    .metric-box::before {
        content: none;
        display: none;
    }
    .metric-box::after {
        content: none;
        display: none;
    }
    .metric-box:hover {
        transform: translateY(-3px);
        border-color: var(--metric-border, #46515A) !important;
        box-shadow: 0 13px 28px rgba(0,0,0,.28), inset 0 1px 0 rgba(255,255,255,.045);
    }
    .metric-solicitacao, .metric-novo {
        --metric-accent: #8BC4D7;
        --metric-bg: #244653;
        --metric-bg-deep: #1B3540;
        --metric-border: #416777;
    }
    .metric-emandamento, .metric-atendimento {
        --metric-accent: #C0B3EF;
        --metric-bg: #40375B;
        --metric-bg-deep: #302943;
        --metric-border: #5A5276;
    }
    .metric-concluido, .metric-tempo-verde {
        --metric-accent: #8BD8B5;
        --metric-bg: #254B3C;
        --metric-bg-deep: #1C392E;
        --metric-border: #3D6C59;
    }
    .metric-aberto {
        --metric-accent: #E6C581;
        --metric-bg: #55462B;
        --metric-bg-deep: #403520;
        --metric-border: #6C5A3D;
    }
    .metric-fechado {
        --metric-accent: #B7C8C1;
        --metric-bg: #35423E;
        --metric-bg-deep: #29332F;
        --metric-border: #53635C;
    }
    .metric-tempo-amarelo {
        --metric-accent: #F0C779;
        --metric-bg: #57452A;
        --metric-bg-deep: #40331F;
        --metric-border: #80663D;
    }
    .metric-tempo-vermelho {
        --metric-accent: #F09AA1;
        --metric-bg: #542E34;
        --metric-bg-deep: #3F2227;
        --metric-border: #81434A;
    }
    .metric-value {
        order: 2;
        font-size: 43px;
        line-height: 1;
        font-weight: 760;
        letter-spacing: -1.5px;
        margin: 13px 0 8px;
        color: #F7F8FA;
        text-shadow: none;
        font-variant-numeric: tabular-nums;
    }
    .metric-label {
        order: 1;
        font-size: 10px;
        line-height: 1.4;
        text-transform: uppercase;
        font-weight: 750;
        opacity: 1;
        color: #C4CDD3;
        letter-spacing: 1.05px;
    }
    .metric-sub {
        order: 3;
        font-size: 11px;
        line-height: 1.4;
        margin-top: 0;
        color: #8F9DA7;
        opacity: 1;
    }

    /* Hierarquia das seções e acabamento geral */
    h1 {
        letter-spacing: -1.2px;
        font-weight: 780 !important;
    }
    h3 {
        font-size: 19px !important;
        letter-spacing: -.25px;
        padding: 0 0 10px 2px;
        border-bottom: 1px solid #25323A;
        margin-bottom: 16px !important;
    }
    h4 {
        font-size: 15px !important;
        color: #C5CED4 !important;
        letter-spacing: .2px;
        margin-top: 10px !important;
    }


    /* TABELAS */
    .stDataFrame {
        background-color: #06151C !important;
        border: 1px solid #22343C !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }

    .stDataFrame thead th {
        background: linear-gradient(135deg, #8F1820, #8F1820) !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 13px !important;
        padding: 10px !important;
    }

    .stDataFrame tbody td {
        background-color: #06151C !important;
        color: #E7EAED !important;
        padding: 8px !important;
        border-bottom: 1px solid #18272E !important;
    }

    /* FOOTER */
    .footer {
        margin-top: 30px;
        padding: 18px;
        text-align: center;
        color: #AAB7BE;
        font-size: 11px;
        border-top: 1px solid #18272E;
        background: linear-gradient(135deg, #06151C, #00080D);
        border-radius: 12px;
    }

    /* INFO BOX */
    .info-normal {
        background: linear-gradient(135deg, #06151C, #00080D) !important;
        color: #D5D9DC !important;
        padding: 10px !important;
        border-radius: 8px !important;
        margin: 10px 0 !important;
        text-align: center !important;
        font-size: 13px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # =====================================================
    # TRATAMENTO E NORMALIZAÇÃO DO MOVIDESK
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
    # CARREGAR DADOS MOVIDESK (RESILIENTE COM PARQUET REAL)
    # =====================================================
    @st.cache_data(ttl=120)
    def carregar_dados_movidesk_resiliente():
        URL = "https://api.movidesk.com/public/v1/tickets"
        TOKEN_MOVIDESK = os.getenv("MOVIDESK_TOKEN")
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
            # 1. Faz a requisição na API com timeout seguro
            r = requests.get(URL, params=params, timeout=15)
            if r.status_code != 200:
                raise Exception(f"Código HTTP {r.status_code}")

            # 2. Transforma a resposta da API em DataFrame tratado
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

            df_api = pd.DataFrame(lista)

            # 3. Salva o DataFrame tratado na máquina se tudo deu certo
            salvar_backup_local(df_api, PATH_BACKUP_MOVIDESK, PATH_TS_MOVIDESK)
            return df_api.copy(), "ONLINE"

        except Exception as e:
            # Fallback de Contingência: Se a API falhar, busca o backup local Parquet
            if os.path.exists(PATH_BACKUP_MOVIDESK):
                try:
                    df_backup = pd.read_parquet(PATH_BACKUP_MOVIDESK)
                    # Certificar que as colunas de data recuperadas continuam como datetime
                    if "DataCriacao" in df_backup.columns:
                        df_backup["DataCriacao"] = pd.to_datetime(df_backup["DataCriacao"])
                    if "DataFechamento" in df_backup.columns:
                        df_backup["DataFechamento"] = pd.to_datetime(df_backup["DataFechamento"])
                    return df_backup.copy(), "FALLBACK"
                except Exception:
                    pass
            return pd.DataFrame(), "OFFLINE"


    # =====================================================
    # CARREGAR DADOS ASANA (RESILIENTE COM PARQUET REAL)
    # =====================================================
    @st.cache_data(ttl=120)
    def carregar_dados_asana_resiliente():
        if not PROJECT_ID:
            return pd.DataFrame(), "OFFLINE"

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
            # 1. Requisição à API do Asana
            response = requests.get(url, headers=headers, params=params, timeout=15)
            if response.status_code != 200:
                raise Exception(f"Código HTTP {response.status_code}")

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

            df_api = pd.DataFrame(tasks_list)
            df_api.fillna("Não informado", inplace=True)

            # 2. Salva localmente se obteve sucesso
            salvar_backup_local(df_api, PATH_BACKUP_ASANA, PATH_TS_ASANA)
            return df_api.copy(), "ONLINE"

        except Exception:
            # Fallback de Contingência: Se falhar, busca o backup Parquet
            if os.path.exists(PATH_BACKUP_ASANA):
                try:
                    df_backup = pd.read_parquet(PATH_BACKUP_ASANA)
                    return df_backup.copy(), "FALLBACK"
                except Exception:
                    pass
            return pd.DataFrame(), "OFFLINE"


    # =====================================================
    # PROCESSAMENTO E EXIBIÇÃO DO DASHBOARD
    # =====================================================
    st.markdown("# 📊 Dashboard Integrado - TI | Estoque")
    st.caption(f"🕐 Última atualização local: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    # Carregar dados usando funções resilientes com fallback
    with st.spinner("🔄 Atualizando painéis e conexões..."):
        df_asana, status_asana = carregar_dados_asana_resiliente()
        df_movidesk, status_movidesk = carregar_dados_movidesk_resiliente()

    # Renderiza indicadores de rede na barra lateral (Sidebar)
    renderizar_status_conexoes(status_movidesk, status_asana)

    # =====================================================
    # SEÇÃO 1: TODOS OS KPIs NO TOPO
    # =====================================================
    st.markdown("---")

    # KPIs do Asana
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

    # KPIs do Movidesk
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
            agora_ts = pd.Timestamp.now()
            inicio_mes_atual = agora_ts.to_period("M").start_time
            fechados = len(
                df_movidesk[
                    (df_movidesk["Status"] == "Fechado")
                    & (df_movidesk["DataFechamento"] >= inicio_mes_atual)
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

        # Cards de Métricas de Tempo
        st.markdown("#### ⏱️ Métricas de Tempo - Chamados Ativos")
        col_t1, col_t2, col_t3, col_t4 = st.columns(4)

        chamados_ativos = df_movidesk[df_movidesk["Status"] != "Fechado"] if not df_movidesk.empty else pd.DataFrame()

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
            tickets_criticos = len(chamados_ativos[chamados_ativos["Dias"] > 30]) if not chamados_ativos.empty else 0
            cor_critico = "metric-tempo-verde" if tickets_criticos == 0 else "metric-tempo-amarelo" if tickets_criticos <= 3 else "metric-tempo-vermelho"
            st.markdown(f"""
                <div class="metric-box {cor_critico}">
                    <div class="metric-label">🔥 +30 DIAS</div>
                    <div class="metric-value">{tickets_criticos}</div>
                    <div class="metric-sub">chamados críticos</div>
                </div>
            """, unsafe_allow_html=True)

        with col_t4:
            tickets_urgentes = len(chamados_ativos[chamados_ativos["Dias"] > 40]) if not chamados_ativos.empty else 0
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
            ate_7 = len(chamados_ativos[chamados_ativos["Dias"] <= 7]) if not chamados_ativos.empty else 0
            st.metric("📅 Até 7 dias", ate_7)

        with col_res2:
            ate_30 = len(chamados_ativos[(chamados_ativos["Dias"] > 7) & (chamados_ativos["Dias"] <= 30)]) if not chamados_ativos.empty else 0
            st.metric("📅 8-30 dias", ate_30)

        with col_res3:
            ate_40 = len(chamados_ativos[(chamados_ativos["Dias"] > 30) & (chamados_ativos["Dias"] <= 40)]) if not chamados_ativos.empty else 0
            st.metric("📅 31-40 dias", ate_40)

        with col_res4:
            mais_40 = len(chamados_ativos[chamados_ativos["Dias"] > 40]) if not chamados_ativos.empty else 0
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
                        "Lojas": st.column_config.Column(width="small")
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
                # Formatar ícones informativos
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

                # Ordenar por criticidade
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
                    ⚠️ Nenhum chamado em aberto no Movidesk
                </div>
            """, unsafe_allow_html=True)

    # =====================================================
    # SEÇÃO 3: DOWNLOAD DE RELATÓRIOS
    # =====================================================
    with st.expander("📥 Download de Relatórios"):
        col_down1, col_down2 = st.columns(2)

        with col_down1:
            st.markdown("**📊 Dados do Movidesk**")
            if not df_movidesk.empty:
                csv_movidesk = df_movidesk.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Baixar CSV - Movidesk",
                    data=csv_movidesk,
                    file_name=f"movidesk_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        with col_down2:
            st.markdown("**🎯 Dados do Asana**")
            if not df_asana.empty:
                csv_asana = df_asana.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Baixar CSV - Asana",
                    data=csv_asana,
                    file_name=f"asana_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

    # =====================================================
    # SEÇÃO 4: GUIA DE CORES E STATUS
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

        with col_leg3:
            st.markdown("**⏱️ Tempo de Resolução**")
            st.markdown("🟢 **Seguro** - Menos de 15 dias")
            st.markdown("🟡 **Atenção** - 15 a 30 dias")
            st.markdown("🔴 **Grave** - Mais de 30 dias")

    # =====================================================
    # FOOTER
    # =====================================================
    st.markdown("""
        <div class="footer">
            💻 Painel Integrado TI - Gestão de Estoque • Desenvolvido para exibição contínua
        </div>
    """, unsafe_allow_html=True)


# Inicializador Principal do Streamlit
if __name__ == "__main__":
    st.set_page_config(
        page_title="Dashboard TI - Estoque",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"  # Força a exibição da barra lateral com os status
    )
    render_estoque()