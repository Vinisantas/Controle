import streamlit as st
from modulos.consulta_patrimonio import render_patrimonio, carregar_dataframeUC, carregar_dataFrameBaixas
from modulos.Histórico_Geral import render_historico
from modulos.SaídaEquipamentos import render_saidas
from modulos.RetornoEquipamentos import render_retornos
from modulos.sup_dash import render_sup
from modulos.estoque_dash import render_estoque

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Controle de Ativos TI",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. INICIALIZAÇÃO DO ESTADO DE LOGIN E NAVEGAÇÃO
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "menu_atual" not in st.session_state:
    st.session_state["menu_atual"] = "🔍 Consulta Patrimônio"

# 3. FUNÇÃO DE LOGIN
def realizar_login(usuario, senha):
    USUARIO_CORRETO = "admin"
    SENHA_CORRETA = "admin123"
    
    if usuario == USUARIO_CORRETO and senha == SENHA_CORRETA:
        st.session_state.autenticado = True
        st.success("Login realizado com sucesso!")
        st.rerun()
    else:
        st.error("Usuário ou senha incorretos.")

# 4. FLUXO DE TELAS
if not st.session_state.autenticado:
    # --- TELA DE LOGIN ---
    st.markdown("""
        <style>
        .stApp { background-color: #0B0F19; color: #F8FAFC; }
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

    _, col_login, _ = st.columns([1.2, 1.5, 1.2])
    with col_login:
        st.write("\n" * 4)
        st.markdown("""
            <div style="text-align: center; margin-bottom: 20px;">
                <h1 style="font-size: 2.2rem; color: #FFFFFF; margin-bottom: 5px;">🔐 TI CONTROLE</h1>
                <p style="color: #94A3B8; font-size: 1rem;">VPS Tech - Gestão Patrimonial</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("form_login"):
            usuario_input = st.text_input("Usuário", placeholder="Digite seu usuário")
            senha_input = st.text_input("Senha", type="password", placeholder="Digite sua senha")
            botao_entrar = st.form_submit_button("Entrar no Sistema", use_container_width=True)
            
            if botao_entrar:
                realizar_login(usuario_input, senha_input)

else:
    # --- TELA DO SISTEMA (SaaS Dark) ---
    st.markdown("""
        <style>
        .stApp { background-color: #0B0F19; color: #F8FAFC; }
        [data-testid="stSidebar"] { background-color: #0F1322 !important; border-right: 1px solid #1E293B; }
        .sidebar-header { padding: 15px 0px; border-bottom: 1px solid #1E293B; margin-bottom: 20px; text-align: center; }
        .sidebar-title { font-size: 1.3rem; font-weight: 800; color: #FFFFFF; display: flex; align-items: center; justify-content: center; gap: 10px; }
        .sidebar-subtitle { font-size: 0.8rem; color: #94A3B8; display: block; margin-top: 5px; }
        .sidebar-section-title { font-size: 0.75rem; font-weight: 700; color: #64748B; text-transform: uppercase; margin-top: 15px; margin-bottom: 10px; letter-spacing: 0.05em; }
        .user-badge { background-color: #111827; border: 1px solid #1E293B; border-radius: 8px; padding: 10px; margin-bottom: 15px; text-align: center; }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("""
            <div class="sidebar-header">
                <span class="sidebar-title">🖥️ TI CONTROLE</span>
                <span class="sidebar-subtitle">Gestão de Equipamentos</span>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="user-badge">
                <span style="font-size: 0.75rem; color: #94A3B8; display: block;">USUÁRIO ATIVO</span>
                <span style="font-weight: bold; color: #10B981;">🟢 admin</span>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<p class="sidebar-section-title">Navegação Principal</p>', unsafe_allow_html=True)
        
        # Páginas disponíveis no menu
        paginas_disponiveis = [
            "🔍 Consulta Patrimônio",
            "📦 Uso & Consumo",
            "📊 Dashboard Estoque",
            "🕒 Histórico Geral",
            "➡️ Saída Equipamentos",
            "↩️ Retorno Equipamentos",
            "📈 Dashboard Sup",
            "🗑️ Saídas (Histórico)"
        ]
        
        for pagina in paginas_disponiveis:
            is_active = st.session_state['menu_atual'] == pagina
            if st.button(
                pagina, 
                use_container_width=True, 
                type="primary" if is_active else "secondary"
            ):
                st.session_state['menu_atual'] = pagina
                st.rerun()
            
        st.write("---")
        
        if st.button("🚪 Sair do Sistema", use_container_width=True):
            st.session_state.autenticado = False
            st.rerun()

        st.caption("VPS Ativos v1.1.0")

    # 5. DIRECIONAMENTO E RENDERIZAÇÃO DAS PÁGINAS
    opcao = st.session_state['menu_atual']

    if opcao == "🔍 Consulta Patrimônio":
        st.title("Consulta Patrimônio")
        st.caption("Gerencie e rastreie os ativos de TI em tempo real")
        st.divider()
        render_patrimonio()

    elif opcao == "📦 Uso & Consumo":
        st.title("Consulta Uso e Consumo")
        st.caption("Gerencie os insumos adicionais de TI")
        st.divider()
        df = carregar_dataframeUC()
        if not df.empty:
            st.markdown("### 🔎 Consulta de Descrição")
            filtro = st.text_input("Digite o termo do insumo").strip().upper()
            df_filtrado = df[df['Descricao'].str.contains(filtro, case=False)] if filtro else df
            st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
        else:
            st.warning("Banco de Uso e Consumo não disponível ou vazio.")

    elif opcao == "🗑️ Saídas (Histórico)":
        st.title("Consulta Baixados")
        st.caption("Ativos desativados e baixados do inventário")
        st.divider()
        df = carregar_dataFrameBaixas()
        if not df.empty:
            st.markdown("### 🔎 Consulta de Baixados")
            filtro = st.text_input("Consultar Plaqueta ou Descrição").strip().upper()
            df_filtrado = df[df['Plaqueta'].str.contains(filtro, case=False) | df['Desc. Bem'].str.contains(filtro, case=False)] if filtro else df
            st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
        else:
            st.warning("Banco de Baixados não disponível ou vazio.")

    # --- RENDERIZAÇÃO DAS FUNÇÕES DOS OUTROS MÓDULOS ---
    elif opcao == "📊 Dashboard Estoque":
        render_estoque()

    elif opcao == "🕒 Histórico Geral":
        render_historico()

    elif opcao == "➡️ Saída Equipamentos":
        render_saidas()

    elif opcao == "↩️ Retorno Equipamentos":
        render_retornos()

    elif opcao == "📈 Dashboard Sup":
        render_sup()