import sqlite3
import pandas as pd
import os
from datetime import datetime
import streamlit as st

# ====================================================
# 💾 CARREGAMENTO DE DADOS (Agora fora de render_patrimonio)
# ====================================================

@st.cache_data()
def carregar_dataframe():  
    caminho_db = 'Banco Dados/cadastro_patrimonio.sqlite'
    if not os.path.exists(caminho_db):
        return pd.DataFrame()
    
    conn = sqlite3.connect(caminho_db)
    query = """
        SELECT * FROM cadastro_patrimonio
        WHERE Plaqueta <> 0 
        ORDER BY Plaqueta DESC;
    """
    df_patrimonio = pd.read_sql_query(query, conn)
    conn.close()
    
    df_patrimonio['Plaqueta'] = df_patrimonio['Plaqueta'].astype(float).astype(int, errors='ignore').apply(
        lambda x: str(x).zfill(6) if pd.notnull(x) else ""
    )
    for col in ['Desc. Bem', 'Filial', 'Desc. Local', 'Portador', 'Fornecedor', 'Documento', 'Cód. Bem', 'Série Fabricação']:
        if col in df_patrimonio.columns:
            df_patrimonio[col] = df_patrimonio[col].astype(str)
    
    data_atual = datetime.now()
    df_patrimonio['Data aquisição'] = pd.to_datetime(df_patrimonio['Data aquisição'], format='%d/%m/%Y', errors='coerce')
    df_patrimonio['idade'] = ((data_atual - df_patrimonio['Data aquisição']).dt.days / 365.25).round(2).fillna(0)
    df_patrimonio['Data aquisição'] = df_patrimonio['Data aquisição'].dt.strftime('%d/%m/%Y')
    df_patrimonio['Documento'] = df_patrimonio['Documento'].apply(lambda x: int(float(x)) if pd.notnull(x) and x != '' and x != 'nan' else 0)
    
    return df_patrimonio

@st.cache_data()
def carregar_dataframeUC():  
    caminho_db = 'Banco Dados/estoque.sqlite'
    if not os.path.exists(caminho_db):
        return pd.DataFrame()
    
    conn = sqlite3.connect(caminho_db)
    query = """
    SELECT "Descricao", "Código", "Cód. Depósito", "Filial", "Unidade", "Qtde Estoque", "Custo", "Total Custo"
    FROM inventario_adicional
    WHERE "Descricao" <> ""
    ORDER BY "Custo" DESC;
    """
    df_usoConsumo = pd.read_sql_query(query, conn)
    conn.close()
    return df_usoConsumo

@st.cache_data()
def carregar_dataFrameBaixas():
    caminho_db = 'Banco Dados/cadastro_baixados.sqlite'
    if not os.path.exists(caminho_db):
        return pd.DataFrame()
        
    conn = sqlite3.connect(caminho_db)
    query = "SELECT * FROM cadastro_baixados WHERE Plaqueta <> 0 ORDER BY Plaqueta DESC;"
    df_patrimonio = pd.read_sql_query(query, conn)
    conn.close()
    return df_patrimonio


# ====================================================
# 🕒 FUNÇÃO DE HISTÓRICO REAL
# ====================================================
def buscar_historico_saidas(plaqueta):
    """Busca registros de saídas salvos pelo SaídaEquipamentos.py para a plaqueta indicada"""
    caminho_db = 'Banco Dados/saidas.sqlite'
    if not os.path.exists(caminho_db):
        return []
    
    try:
        conn = sqlite3.connect(caminho_db)
        query = """
            SELECT data_saida, portador, destino, observacao 
            FROM saidas 
            WHERE plaqueta = ? 
            ORDER BY data_saida DESC;
        """
        df_historico = pd.read_sql_query(query, conn, params=(plaqueta,))
        conn.close()
        return df_historico.to_dict(orient='records')
    except Exception:
        return []


# ====================================================
# 🏛️ RENDERIZAÇÃO DA PÁGINA
# ====================================================
def render_patrimonio():
    # Estilização CSS Customizada (SaaS Premium Dark)
    st.markdown("""
        <style>
        /* Box de Destaque Verde para o registro selecionado */
        .patrimonio-main-card {
            background: rgba(16, 185, 129, 0.05);
            border: 1px solid rgba(16, 185, 129, 0.2);
            border-left: 5px solid #10B981;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 25px;
        }
        
        /* Grid de Cards de Detalhes Rápidos */
        .metric-card {
            background-color: #111827;
            border: 1px solid #1F2937;
            border-radius: 12px;
            padding: 16px;
            text-align: left;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .metric-label {
            font-size: 0.75rem;
            color: #94A3B8;
            text-transform: uppercase;
            font-weight: 600;
        }
        .metric-value {
            font-size: 1.1rem;
            font-weight: 700;
            color: #FFFFFF;
            margin-top: 5px;
        }
        .metric-sub {
            font-size: 0.75rem;
            color: #64748B;
            margin-top: 2px;
        }
        
        /* Layout de Linha do Tempo de Movimentações */
        .timeline-container {
            position: relative;
            padding-left: 30px;
            border-left: 2px dashed #1E293B;
            margin-left: 15px;
            margin-top: 15px;
        }
        .timeline-item {
            position: relative;
            margin-bottom: 25px;
            background-color: #111827;
            border: 1px solid #1F2937;
            padding: 15px;
            border-radius: 10px;
        }
        .timeline-badge {
            position: absolute;
            left: -42px;
            top: 15px;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            color: white;
        }
        .badge-saida { background-color: #EF4444; }
        .badge-cadastro { background-color: #10B981; }
        .badge-vazio { background-color: #4B5563; }
        </style>
    """, unsafe_allow_html=True)

    df = carregar_dataframe()
    
    st.markdown("### 🔎 Filtro de Pesquisa")
    coluna_pesquisa = st.selectbox("Coluna para Pesquisa", ["Plaqueta", "Desc. Bem", "Filial", "Portador"])

    filtro = st.text_area(
        f"Consultar {coluna_pesquisa}",
        placeholder="Cole ou digite as plaquetas separadas por linha...",
        height=100
    ).strip().upper()

    if filtro:
        if coluna_pesquisa == "Plaqueta":
            lista_plaquetas = [x.strip().zfill(6) for x in filtro.replace("\n", ",").split(",") if x.strip()]
            df_filtrado = df[df["Plaqueta"].isin(lista_plaquetas)]
        else:
            df_filtrado = df[df[coluna_pesquisa].str.contains(filtro, case=False, na=False)]
    else:
        df_filtrado = df

    # Exibição de Resultado Único (Ficha Detalhada + Histórico Real de Saídas)
    if len(df_filtrado) == 1:
        ativo = df_filtrado.iloc[0]
        plaqueta_atual = ativo.get('Plaqueta')
        
        # 1. Card de destaque Verde
        st.markdown(f"""
            <div class="patrimonio-main-card">
                <table style="width:100%; border:none; border-collapse:collapse; color:#FFFFFF;">
                    <tr style="border:none;">
                        <td style="width:15%; border:none;"><span style="color:#10B981; font-size:0.8rem; font-weight:bold;">PLAQUETA</span><br><b style="font-size:1.3rem; color:#10B981;">{plaqueta_atual}</b></td>
                        <td style="width:35%; border:none;"><span style="color:#94A3B8; font-size:0.8rem;">DESCRIÇÃO</span><br><b style="font-size:1rem;">{ativo.get('Desc. Bem')}</b></td>
                        <td style="width:20%; border:none;"><span style="color:#94A3B8; font-size:0.8rem;">FILIAL</span><br><b>{ativo.get('Filial')}</b></td>
                        <td style="width:15%; border:none;"><span style="color:#94A3B8; font-size:0.8rem;">CÓDIGO LOCAL</span><br><b>{ativo.get('Cód. Bem', 'N/A')}</b></td>
                    </tr>
                </table>
            </div>
        """, unsafe_allow_html=True)
        
        # 2. Cards Rápidos
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="metric-card"><span class="metric-label">👤 Portador</span><div class="metric-value">{ativo.get("Portador", "N/A")}</div><div class="metric-sub">Responsável Atual</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><span class="metric-label">🏢 Localização</span><div class="metric-value">{str(ativo.get("Desc. Local", "N/A"))[:20]}</div><div class="metric-sub">Setor</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-card"><span class="metric-label">📅 Aquisição</span><div class="metric-value">{ativo.get("Data aquisição", "N/A")}</div><div class="metric-sub">NF: {ativo.get("Documento")}</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="metric-card"><span class="metric-label">⏳ Idade do Ativo</span><div class="metric-value">{ativo.get("idade", 0)} anos</div><div class="metric-sub">Em uso</div></div>', unsafe_allow_html=True)

        st.write("")
        
        col_esq, col_dir = st.columns([1.8, 1.2], gap="large")
        with col_esq:
            st.markdown("### 🕒 Fluxo de Movimentação Real")
            
            # Buscar histórico real vindo do SaídaEquipamentos.py
            historico_real = buscar_historico_saidas(plaqueta_atual)
            
            timeline_html = '<div class="timeline-container">'
            
            if historico_real:
                # Monta a timeline baseando-se nas saídas reais encontradas
                for registro in historico_real:
                    timeline_html += f"""
                        <div class="timeline-item">
                            <div class="timeline-badge badge-saida">➡️</div>
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <b style="font-size:1rem; color:#FFFFFF;">Saída para {registro.get('portador', 'N/A')}</b>
                                <span style="font-size:0.8rem; color:#94A3B8;">📅 {registro.get('data_saida', 'N/A')}</span>
                            </div>
                            <div style="margin-top:8px; font-size:0.85rem; color:#CBD5E1;">
                                Destino: <b>{registro.get('destino', 'N/A')}</b><br>
                                Obs: <i>{registro.get('observacao', 'Sem observações')}</i>
                            </div>
                        </div>
                    """
            else:
                # Caso não tenha histórico de saída gravado ainda
                timeline_html += f"""
                    <div class="timeline-item">
                        <div class="timeline-badge badge-vazio">ℹ️</div>
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <b style="font-size:1rem; color:#FFFFFF;">Sem Saídas Recentes</b>
                        </div>
                        <div style="margin-top:8px; font-size:0.85rem; color:#CBD5E1;">
                            Este equipamento não possui histórico de movimentação externa registrado recentemente.
                        </div>
                    </div>
                """
                
            # Entrada de cadastro fixa no final da timeline (encostado na esquerda)
            timeline_html += f"""
                <div class="timeline-item">
                    <div class="timeline-badge badge-cadastro">📥</div>
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <b style="font-size:1rem; color:#FFFFFF;">Cadastro de Aquisição</b>
                        <span style="font-size:0.8rem; color:#94A3B8;">📅 {ativo.get('Data aquisição')}</span>
                    </div>
                    <div style="margin-top:8px; font-size:0.85rem; color:#CBD5E1;">
                        Adquirido do fornecedor <b>{ativo.get('Fornecedor')}</b>.
                    </div>
                </div>
            </div>
            """
            st.markdown(timeline_html, unsafe_allow_html=True)
            
        with col_dir:
            st.markdown("### 📋 Ficha Detalhada")
            detalhes_html = f"""
                <table style="width:100%; border-collapse:collapse; color:#E2E8F0; font-size:0.9rem;">
                    <tr style="border-bottom: 1px solid #1F2937; height:45px;">
                        <td style="color:#94A3B8; font-weight:600;">Série de Fabricação</td>
                        <td>{ativo.get('Série Fabricação', 'N/A')}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #1F2937; height:45px;">
                        <td style="color:#94A3B8; font-weight:600;">Código do Bem</td>
                        <td>{ativo.get('Cód. Bem', 'N/A')}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #1F2937; height:45px;">
                        <td style="color:#94A3B8; font-weight:600;">Fornecedor Principal</td>
                        <td>{ativo.get('Fornecedor', 'N/A')}</td>
                    </tr>
                </table>
            """
            st.markdown(detalhes_html, unsafe_allow_html=True)

    # Exibição de Múltiplos Resultados (Sua Grade Perfeita de Listagem em Lote)
    else:
        st.markdown("### Listagem de Registros")
        if not df_filtrado.empty:
            df_filtrado_exibir = df_filtrado.copy()
            df_filtrado_exibir['Selecionar'] = False
            disabled_columns = [col for col in df_filtrado_exibir.columns if col != 'Selecionar']
            st.data_editor(
                df_filtrado_exibir,
                column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar", default=False)},
                disabled=disabled_columns,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("⚠️ Nenhum registro encontrado.")