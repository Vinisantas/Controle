import sqlite3
import pandas as pd
import os
from datetime import datetime
import streamlit as st

# ====================================================
# 💾 CARREGAMENTO DE DADOS (Com tratamentos aplicados)
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
        SELECT "Descricao", "Código", "Cód. Depósito", "Filial", "Unidade", "Qtde Estoque", "Custo"
        FROM inventario_adicional
        WHERE "Descricao" <> "" AND "Descricao" IS NOT NULL
        ORDER BY "Custo" DESC;
    """
    df_usoConsumo = pd.read_sql_query(query, conn)
    conn.close()

    # Tratamento rigoroso dos dados numéricos para evitar None
    df_usoConsumo["Qtde Estoque"] = pd.to_numeric(df_usoConsumo["Qtde Estoque"], errors="coerce").fillna(0).astype(int)
    df_usoConsumo["Custo"] = pd.to_numeric(df_usoConsumo["Custo"], errors="coerce").fillna(0.0)
    
    # Cálculo seguro do Total Custo diretamente no Pandas
    df_usoConsumo["Total Custo"] = df_usoConsumo["Qtde Estoque"] * df_usoConsumo["Custo"]
    
    # Garantir strings limpas nas colunas de texto
    for col in ["Descricao", "Código", "Cód. Depósito", "Filial", "Unidade"]:
        if col in df_usoConsumo.columns:
            df_usoConsumo[col] = df_usoConsumo[col].astype(str).replace("nan", "")

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
# 📊 GERENCIAMENTO DE CHECKLIST (INTEGRAÇÃO SÊNIOR CORRIGIDA)
# ====================================================
def processar_baixa_estoque(id_saida, codigo_item, quantidade):
    """
    1. Deduz a quantidade do inventário físico (estoque.sqlite)
    2. Atualiza o status de homologação da baixa sênior no (saida.sqlite)
    """
    db_estoque = 'Banco Dados/estoque.sqlite'
    db_saida = 'Banco Dados/saida.sqlite'
    data_hoje = datetime.now().strftime("%d/%m/%Y %H:%M")

    # --- PASSO 1: Atualizar Estoque Físico ---
    if os.path.exists(db_estoque):
        conn_est = sqlite3.connect(db_estoque)
        try:
            cursor_est = conn_est.cursor()
            cursor_est.execute("""
                UPDATE inventario_adicional 
                SET "Qtde Estoque" = MAX(0, CAST("Qtde Estoque" AS INTEGER) - ?)
                WHERE "Código" = ?
            """, (quantidade, codigo_item))
            conn_est.commit()
        except Exception as e:
            conn_est.rollback()
            st.error(f"Erro ao deduzir do estoque.sqlite: {e}")
            return
        finally:
            conn_est.close()

    # --- PASSO 2: Marcar como Concluído no banco de Saídas ---
    if os.path.exists(db_saida):
        conn_sai = sqlite3.connect(db_saida)
        try:
            cursor_sai = conn_sai.cursor()
            # Atualiza o campo que valida a pendência na query visual
            cursor_sai.execute("""
                UPDATE saida 
                SET Baixa_Senior = ?
                WHERE id = ?
            """, (f"CONCLUIDO EM {data_hoje}", id_saida))
            conn_sai.commit()
            
            st.toast(f"✅ Item {codigo_item} processado no ERP Sênior e estoque físico atualizado!", icon="✔️")
            st.cache_data.clear() # Limpa o cache para recarregar a tabela física com o novo saldo
        except Exception as e:
            conn_sai.rollback()
            st.error(f"Erro ao atualizar pendência no saida.sqlite: {e}")
        finally:
            conn_sai.close()


def render_patrimonio():
    # Estilização CSS Customizada (SaaS Premium Dark - Refinado)
    st.markdown("""
        <style>
        /* Estilo para abas do Streamlit ficarem mais modernas */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: #0B0F19;
            padding: 8px;
            border-radius: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 45px;
            white-space: pre-wrap;
            background-color: #111827;
            border-radius: 8px;
            color: #94A3B8;
            border: 1px solid #1F2937;
            transition: all 0.2s ease-in-out;
        }
        .stTabs [data-baseweb="tab"]:hover {
            color: #FFFFFF;
            background-color: #1F2937;
            border-color: #374151;
        }
        .stTabs [aria-selected="true"] {
            background-color: #10B981 !important;
            color: #FFFFFF !important;
            border-color: #10B981 !important;
            font-weight: bold;
        }

        /* Box de Destaque Verde para o registro selecionado */
        .patrimonio-main-card {
            background: rgba(16, 185, 129, 0.04);
            border: 1px solid rgba(16, 185, 129, 0.15);
            border-left: 5px solid #10B981;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 25px;
        }
        
        /* Grid de Cards de Detalhes Rápidos */
        .metric-grid-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 25px;
        }
        .metric-card {
            background-color: #0E131F;
            border: 1px solid #1E293B;
            border-radius: 10px;
            padding: 16px;
            text-align: left;
            transition: transform 0.2s, border-color 0.2s;
        }
        .metric-card:hover {
            border-color: #334155;
            transform: translateY(-2px);
        }
        .metric-label {
            font-size: 0.75rem;
            color: #94A3B8;
            text-transform: uppercase;
            font-weight: 700;
            letter-spacing: 0.05em;
        }
        .metric-value {
            font-size: 1.3rem;
            font-weight: 700;
            color: #FFFFFF;
            margin-top: 6px;
        }
        .metric-sub {
            font-size: 0.72rem;
            color: #64748B;
            margin-top: 4px;
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
            background-color: #0E131F;
            border: 1px solid #1E293B;
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

    tab_patrimonio, tab_uso_consumo = st.tabs(["🏛️ PATRIMÔNIO ATIVO", "📦 USO E CONSUMO (ESTOQUE)"])

    # ==========================================
    # ABA 1: PATRIMÔNIO ATIVO
    # ==========================================
    with tab_patrimonio:
        df = carregar_dataframe()
        
        st.markdown("### 🔎 Filtro de Pesquisa (Patrimônio)")
        coluna_pesquisa = st.selectbox("Coluna para Pesquisa", ["Plaqueta", "Desc. Bem", "Filial", "Portador"], key="sb_patrimonio")

        filtro = st.text_area(
            f"Consultar {coluna_pesquisa}",
            placeholder="Cole ou digite as plaquetas separadas por linha...",
            height=100,
            key="ta_patrimonio"
        ).strip().upper()

        if filtro:
            if coluna_pesquisa == "Plaqueta":
                lista_plaquetas = [x.strip().zfill(6) for x in filtro.replace("\n", ",").split(",") if x.strip()]
                df_filtrado = df[df["Plaqueta"].isin(lista_plaquetas)]
            else:
                df_filtrado = df[df[coluna_pesquisa].str.contains(filtro, case=False, na=False)]
        else:
            df_filtrado = df

        if len(df_filtrado) == 1:
            ativo = df_filtrado.iloc[0]
            plaqueta_atual = ativo.get('Plaqueta')
            
            historico_real = buscar_historico_saidas(plaqueta_atual)
            esta_na_assistencia = False
            detalhe_assistencia = ""
            qtd_manutencoes = 0
            
            if historico_real:
                for reg in historico_real:
                    dest = str(reg.get('destino', '')).upper()
                    obs = str(reg.get('observacao', '')).upper()
                    if any(termo in dest or termo in obs for termo in ["ASSISTENCIA", "CONSERTO", "MANUTENCAO", "REPARO"]):
                        qtd_manutencoes += 1
                
                ultima_mov = historico_real[0] 
                ultimo_destino = str(ultima_mov.get('destino', '')).upper()
                ultima_obs = str(ultima_mov.get('observacao', '')).upper()
                
                if any(termo in ultimo_destino or termo in ultima_obs for termo in ["ASSISTENCIA", "CONSERTO", "MANUTENCAO", "REPARO"]):
                    esta_na_assistencia = True
                    detalhe_assistencia = f"**Enviado para:** {ultima_mov.get('portador', 'N/A')} em {ultima_mov.get('data_saida', 'N/A')} <br> **Motivo/Obs:** <i>{ultima_mov.get('observacao', 'Sem observações')}</i>"
            
            if esta_na_assistencia:
                st.markdown(f"""
                    <div style="background-color: rgba(239, 68, 68, 0.1); border: 1px solid #EF4444; border-radius: 10px; padding: 15px; margin-bottom: 20px;">
                        <span style="color: #F87171; font-weight: bold; font-size: 1.1rem;">⚠️ ATIVO EM MANUTENÇÃO</span><br>
                        <span style="color: #E2E8F0; font-size: 0.9rem;">{detalhe_assistencia}</span>
                    </div>
                """, unsafe_allow_html=True)
            
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
            
            st.markdown(f"""
                <div class="metric-grid-container">
                    <div class="metric-card">
                        <div class="metric-label">👤 Portador</div>
                        <div class="metric-value">{ativo.get("Portador", "N/A")}</div>
                        <div class="metric-sub">Responsável Atual</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">🏢 Localização</div>
                        <div class="metric-value">{str(ativo.get("Desc. Local", "N/A"))[:22]}</div>
                        <div class="metric-sub">Setor / Departamento</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">📅 Aquisição</div>
                        <div class="metric-value">{ativo.get("Data aquisição", "N/A")}</div>
                        <div class="metric-sub">NF: {ativo.get("Documento")}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">⏳ Idade do Ativo</div>
                        <div class="metric-value">{ativo.get("idade", 0)} anos</div>
                        <div class="metric-sub">Tempo desde a compra</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.write("")
            
            col_esq, col_dir = st.columns([1.8, 1.2], gap="large")
            with col_esq:
                st.markdown("### 🕒 Fluxo de Movimentação Real")
                timeline_html = '<div class="timeline-container">'
                
                if historico_real:
                    for registro in historico_real:
                        dest_reg = str(registro.get('destino', '')).upper()
                        obs_reg = str(registro.get('observacao', '')).upper()
                        is_assist = any(t in dest_reg or t in obs_reg for t in ["ASSISTENCIA", "CONSERTO", "MANUTENCAO", "REPARO"])
                        
                        badge_classe = "badge-saida" if not is_assist else "badge-vazio"
                        emoji_mov = "➡️" if not is_assist else "🔧"
                        titulo_mov = f"Saída para {registro.get('portador', 'N/A')}" if not is_assist else f"Envio para Manutenção ({registro.get('portador', 'N/A')})"
                        
                        timeline_html += f"""
                        <div class="timeline-item">
                            <div class="timeline-badge {badge_classe}">{emoji_mov}</div>
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <b style="font-size:1rem; color:#FFFFFF;">{titulo_mov}</b>
                                <span style="font-size:0.8rem; color:#94A3B8;">📅 {registro.get('data_saida', 'N/A')}</span>
                            </div>
                            <div style="margin-top:8px; font-size:0.85rem; color:#CBD5E1;">
                                Destino: <b>{registro.get('destino', 'N/A')}</b><br>
                                Obs: <i>{registro.get('observacao', 'Sem observações')}</i>
                            </div>
                        </div>
                        """
                else:
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
                    
                fornecedor = ativo.get('Fornecedor')
                fornecedor_str = fornecedor if pd.notnull(fornecedor) and str(fornecedor).strip() != 'None' else 'Não Informado'
                
                # Deixe as aspas triplas e o HTML sem nenhum recuo/espaço na esquerda:
                timeline_html += f"""<div class="timeline-item">
<div class="timeline-badge badge-cadastro">📥</div>
<div style="display:flex; justify-content:space-between; align-items:center;">
<b style="font-size:1rem; color:#FFFFFF;">Cadastro de Aquisição</b>
<span style="font-size:0.8rem; color:#94A3B8;">📅 {ativo.get('Data aquisição')}</span>
</div>
<div style="margin-top:8px; font-size:0.85rem; color:#CBD5E1;">
Adquirido do fornecedor <b>{fornecedor_str}</b>.
</div>
</div>
</div>"""

                st.markdown(timeline_html, unsafe_allow_html=True)
                
            with col_dir:
                st.markdown("### 📋 Ficha Detalhada")
                cor_badge = "#EF4444" if qtd_manutencoes > 2 else ("#F59E0B" if qtd_manutencoes > 0 else "#10B981")
                
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
                        <tr style="border-bottom: 1px solid #1F2937; height:45px;">
                            <td style="color:#94A3B8; font-weight:600;">Histórico de Consertos</td>
                            <td><span style="background-color: {cor_badge}; color: #FFFFFF; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold;">{qtd_manutencoes} manutenções</span></td>
                        </tr>
                    </table>
                """
                st.markdown(detalhes_html, unsafe_allow_html=True)

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
                    hide_index=True,
                    key="editor_patrimonio"
                )
            else:
                st.warning("⚠️ Nenhum registro encontrado.")

# ==================================================
# ABA 2: USO E CONSUMO (ESTOQUE)
# ==================================================
    with tab_uso_consumo:
        df_uc = carregar_dataframeUC()
        
        if df_uc.empty:
            st.warning("⚠️ Nenhum dado de Uso e Consumo encontrado no banco local (`estoque.sqlite`).")
        else:
            # Filtros alinhados no topo usando a largura total
            filtros_col1, filtros_col2 = st.columns([3, 1])
            with filtros_col1:
                busca_uc = st.text_input(
                    "🔍 Pesquisar no Estoque", 
                    placeholder="Busque por descrição de produto ou código...", 
                    key="busca_uc_input",
                    label_visibility="collapsed"
                ).strip()
            
            with filtros_col2:
                depositos_disponiveis = ["Todos Depósitos"] + sorted(list(df_uc["Cód. Depósito"].unique()))
                dep_selecionado = st.selectbox(
                    "Filtrar Depósito", 
                    depositos_disponiveis, 
                    key="sb_dep_uc_input",
                    label_visibility="collapsed"
                )
            
            # Filtragem dos dados
            df_uc_filtrado = df_uc.copy()
            if busca_uc:
                df_uc_filtrado = df_uc_filtrado[
                    df_uc_filtrado["Descricao"].str.contains(busca_uc, case=False, na=False) |
                    df_uc_filtrado["Código"].str.contains(busca_uc, na=False)
                ]
            if dep_selecionado != "Todos Depósitos":
                df_uc_filtrado = df_uc_filtrado[df_uc_filtrado["Cód. Depósito"] == dep_selecionado]
            
            total_pecas = int(df_uc_filtrado["Qtde Estoque"].sum())
            valor_total = df_uc_filtrado["Total Custo"].sum()

            # Métricas distribuídas em 3 colunas iguais de largura total
            met_col1, met_col2, met_col3 = st.columns(3)
            with met_col1:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">📦 Itens Cadastrados</div>
                        <div class="metric-value">{len(df_uc_filtrado)}</div>
                        <div class="metric-sub">Produtos listados</div>
                    </div>
                """, unsafe_allow_html=True)
            with met_col2:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">🔢 Unidades Físicas</div>
                        <div class="metric-value">{total_pecas:,}</div>
                        <div class="metric-sub">Soma total de estoque</div>
                    </div>
                """, unsafe_allow_html=True)
            with met_col3:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">💰 Capital Giro</div>
                        <div class="metric-value" style="color: #10B981;">R$ {valor_total:,.2f}</div>
                        <div class="metric-sub">Custo total investido</div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("### Itens em Estoque")
            
            # Tabela ocupando 100% do container
            st.dataframe(
                df_uc_filtrado,
                column_config={
                    "Descricao": st.column_config.TextColumn("Item / Insumo", width="large"),
                    "Código": st.column_config.TextColumn("Código Senior", width="medium"),
                    "Cód. Depósito": st.column_config.TextColumn("Dep.", width="small"),
                    "Filial": st.column_config.TextColumn("Filial", width="small"),
                    "Unidade": st.column_config.TextColumn("Un.", width="small"),
                    "Qtde Estoque": st.column_config.NumberColumn("Qtd Físico", format="%d", width="small"),
                    "Custo": st.column_config.NumberColumn("Custo Unit.", format="R$ %.2f", width="medium"),
                    "Total Custo": st.column_config.NumberColumn("Custo Total", format="R$ %.2f", width="medium")
                },
                use_container_width=True,
                hide_index=True,
                key="tabela_final_uso_consumo"
            )

# Para renderizar no script principal
if __name__ == "__main__":
    render_patrimonio()