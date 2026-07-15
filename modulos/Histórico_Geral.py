import sqlite3
import streamlit as st
import pandas as pd
import os
from datetime import datetime

def render_historico():
    # Estilização visual premium para cards de histórico e status
    st.markdown("""
        <style>
        .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
        h1 { font-weight: 800; letter-spacing: -0.05em; color: #0F172A; }
        
        /* Box de Alerta da Base */
        .status-box {
            padding: 15px 20px;
            border-radius: 12px;
            color: #FFFFFF;
            font-weight: 600;
            margin-bottom: 25px;
        }
        .auto-updated {
            background: linear-gradient(135deg, #059669 0%, #047857 100%);
            border: 1px solid #34D399;
        }
        .conforme {
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            border: 1px solid #334155;
        }
        
        /* Card do Paradeiro Atual do Equipamento */
        .paradeiro-card {
            background-color: #1E293B;
            border: 1px solid #475569;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }
        
        /* Novo Card do Histórico de Passagem */
        .card-passagem {
            background-color: #1E293B;
            border-radius: 10px;
            border: 1px solid #334155;
            padding: 18px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .badge-tipo {
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: bold;
            text-transform: uppercase;
            display: inline-block;
            margin-bottom: 10px;
        }
        .badge-entrada { background-color: #065F46; color: #34D399; }
        .badge-saida { background-color: #7F1D1D; color: #F87171; }
        
        .grid-passagem {
            display: grid;
            grid-template-columns: 1.2fr 1fr 1fr;
            gap: 15px;
            margin-top: 10px;
            font-size: 0.9rem;
        }
        .info-block {
            background-color: #0F172A;
            padding: 10px;
            border-radius: 6px;
            border: 1px solid #1E293B;
        }
        .info-label {
            font-size: 0.75rem;
            color: #94A3B8;
            text-transform: uppercase;
            font-weight: bold;
            display: block;
            margin-bottom: 3px;
        }
        </style>
    """, unsafe_allow_html=True)

    DB_CADASTRO = "Banco Dados/cadastro_patrimonio.sqlite"
    DB_RETORNO = "Banco Dados/retorno.sqlite"
    DB_SAIDA = "Banco Dados/saida.sqlite"

    # --- FUNÇÕES DE BANCO DE DADOS ---

    def buscar_dados_cadastro(plaqueta):
        if not os.path.exists(DB_CADASTRO):
            return None, None
        
        plaqueta_limpa = str(plaqueta).strip().replace(".0", "")
        conn = sqlite3.connect(DB_CADASTRO)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tabelas = [t[0] for t in cursor.fetchall()]
            
            for tabela in tabelas:
                df = pd.read_sql_query(f"SELECT * FROM [{tabela}]", conn)
                df.columns = [c.strip() for c in df.columns]
                
                if "Plaqueta" in df.columns:
                    df['Plaqueta_Busca'] = df['Plaqueta'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
                    resultado = df[df['Plaqueta_Busca'] == plaqueta_limpa]
                    if not resultado.empty:
                        conn.close()
                        return resultado.iloc[0].to_dict(), tabela
            conn.close()
        except Exception as e:
            st.error(f"Erro ao acessar cadastro: {e}")
        return None, None

    def buscar_movimentacoes_ativo(plaqueta):
        plaqueta_limpa = str(plaqueta).strip()
        movimentacoes = []
        
        # 1. Buscar nas Saídas
        if os.path.exists(DB_SAIDA):
            try:
                conn = sqlite3.connect(DB_SAIDA)
                df = pd.read_sql_query("SELECT * FROM saida", conn, parse_dates=["Data"])
                conn.close()
                if not df.empty:
                    df['Patrimonio'] = df['Patrimonio'].astype(str).str.strip()
                    filtro = df[df['Patrimonio'] == plaqueta_limpa]
                    for _, row in filtro.iterrows():
                        movimentacoes.append({
                            "Data": row["Data"],
                            "Tipo": "SAIDA",
                            "Origem_Destino": row["Destinatario"],
                            "Tipo_Destino": row["Tipo_Destino"] if "Tipo_Destino" in row else "Loja / Filial",
                            "Motivo": row["Motivo"],
                            "Condicao": row["Status_Equipamento"],
                            "Chamado": row["Chamado"],
                            "Responsavel": row["Tecnico"] if "Tecnico" in row else "Não Informado"
                        })
            except:
                pass
                
        # 2. Buscar nos Retornos
        if os.path.exists(DB_RETORNO):
            try:
                conn = sqlite3.connect(DB_RETORNO)
                df = pd.read_sql_query("SELECT * FROM retorno", conn, parse_dates=["Data"])
                conn.close()
                if not df.empty:
                    df['Patrimonio'] = df['Patrimonio'].astype(str).str.strip()
                    filtro = df[df['Patrimonio'] == plaqueta_limpa]
                    for _, row in filtro.iterrows():
                        movimentacoes.append({
                            "Data": row["Data"],
                            "Tipo": "RETORNO",
                            "Origem_Destino": "ESTOQUE TI / FILIAL 1000",
                            "Origem_Fisica": row["Loja"] if "Loja" in row else "Desconhecido",
                            "Tipo_Destino": "Loja / Filial",
                            "Motivo": "Retornado para Manutenção / Triagem",
                            "Condicao": "Pendente de Análise",
                            "Chamado": row["Chamado"] if "Chamado" in row else "N/A",
                            "Responsavel": "Estoque TI"
                        })
            except:
                pass
                
        movimentacoes.sort(key=lambda x: x["Data"], reverse=True)
        return list(movimentacoes)

    def extrair_numero_filial(texto):
        import re
        numeros = re.findall(r'\d+', str(texto))
        if numeros:
            return int(numeros[0])
        return 1000

    def aplicar_atualizacao_banco_oficial(plaqueta, tabela_nome, nova_filial, nova_desc_local):
        try:
            conn = sqlite3.connect(DB_CADASTRO)
            cursor = conn.cursor()
            plaqueta_limpa = str(plaqueta).strip()
            data_atual = datetime.now().strftime('%d/%m/%Y')
            
            query = f"""
                UPDATE [{tabela_nome}] 
                SET [Filial] = ?, [Desc. Local] = ?, [Data últ. Loc] = ?
                WHERE CAST(Plaqueta AS TEXT) = ? 
                OR CAST(Plaqueta AS TEXT) = ?
            """
            cursor.execute(query, (float(nova_filial), nova_desc_local, data_atual, plaqueta_limpa, f"{plaqueta_limpa}.0"))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Erro ao persistir na base: {e}")
            return False


    # --- INTERFACE ---

    st.title("🔍 Rastreabilidade de TI & Ciclo de Vida")
    st.markdown("Busque e rastreie o fluxo físico real e a conformidade contábil do imobilizado.")
    st.divider()

    col_margem_l, col_busca, col_margem_r = st.columns([1, 2, 1])
    with col_busca:
        plaqueta_busca = st.text_input(
            "Digite o Número do Patrimônio / Plaqueta para Rastreamento 🏷️", 
            placeholder="Ex: 81940"
        ).strip()

    if plaqueta_busca:
        dados_ativo, tabela_origem = buscar_dados_cadastro(plaqueta_busca)
        
        if dados_ativo:
            # Pega dados contábeis atuais
            filial_contabil = int(float(dados_ativo.get('Filial', 1000)))
            local_contabil = str(dados_ativo.get('Desc. Local', 'NÃO INFORMADO')).strip()
            
            # Busca passagens físicas da TI
            historico = buscar_movimentacoes_ativo(plaqueta_busca)
            
            # Calcula onde o item deve estar hoje baseado na última movimentação física
            if historico:
                ultimo_evento = historico[0]
                if ultimo_evento["Tipo"] == "RETORNO":
                    filial_calculada = 1000
                    local_calculado = "ESTOQUE TI / MANUTENÇÃO"
                else:
                    if ultimo_evento["Tipo_Destino"] == "Setor Interno":
                        filial_calculada = 1000
                        local_calculado = str(ultimo_evento["Origem_Destino"]).upper()
                    else:
                        filial_calculada = extrair_numero_filial(ultimo_evento["Origem_Destino"])
                        local_calculado = "LOJA GERAL"
            else:
                filial_calculada = filial_contabil
                local_calculado = local_contabil

            # Valida divergência e executa AUTO-GRAVAÇÃO NA BASE
            base_foi_atualizada = False
            divergencia = (filial_contabil != filial_calculada) or (local_contabil.upper() != local_calculado.upper())
            
            if divergencia:
                if aplicar_atualizacao_banco_oficial(plaqueta_busca, tabela_origem, filial_calculada, local_calculado):
                    base_foi_atualizada = True
                    filial_contabil = filial_calculada
                    local_contabil = local_calculado

            # Feedbacks visuais de atualização
            if base_foi_atualizada:
                st.markdown(f"""
                    <div class="status-box auto-updated">
                        <span style="font-size: 1.15rem; display: block;">⚡ BASE OFICIAL SINCRONIZADA EM TEMPO REAL!</span>
                        <span style="font-size: 0.9rem; font-weight: normal; opacity: 0.95;">
                            Detectamos alteração física. O arquivo <b>cadastro_patrimonio.sqlite</b> foi atualizado para: <b>Filial {filial_calculada} - {local_calculado}</b>.
                        </span>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div class="status-box conforme">
                        <span style="font-size: 1.1rem; display: block;">🟢 STATUS: LOCALIZAÇÃO SINCRONIZADA</span>
                        <span style="font-size: 0.85rem; font-weight: normal; opacity: 0.8;">
                            A base do imobilizado reflete exatamente a última movimentação física realizada pela TI.
                        </span>
                    </div>
                """, unsafe_allow_html=True)

            # 1. CARD DE LOCALIZAÇÃO ATUAL
            st.subheader("📍 Localização Física Atual do Equipamento")
            
            cor_destaque = "#10B981" if filial_contabil == 1000 else "#6366F1"
            tipo_local_rotulo = "Estoque Central de TI" if filial_contabil == 1000 else f"Operando na Loja"
            
            st.markdown(f"""
                <div class="paradeiro-card" style="border-top: 5px solid {cor_destaque};">
                    <span style="color: #94A3B8; font-size: 0.85rem; font-weight: bold; text-transform: uppercase;">Paradeiro Confirmado</span>
                    <h2 style="color: {cor_destaque}; font-weight: 800; margin: 10px 0;">FILIAL {filial_contabil}</h2>
                    <p style="font-size: 1.1rem; margin: 5px 0; color: #F8FAFC;"><b>Setor/Descrição:</b> {local_contabil}</p>
                    <span style="background-color: #334155; color: #F1F5F9; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold;">
                        {tipo_local_rotulo}
                    </span>
                </div>
            """, unsafe_allow_html=True)

            # Detalhes Técnicos e Histórico Lado a Lado
            col_detalhes, col_historico_fisico = st.columns([1, 2.2], gap="large")

            # 2. FICHA TÉCNICA
            with col_detalhes:
                st.subheader("📋 Ficha do Ativo imobilizado")
                with st.container(border=True):
                    st.write(f"**Descrição do Bem:**")
                    st.markdown(f"<p style='color: #94A3B8; font-size: 0.95rem; line-height: 1.4;'>{dados_ativo.get('Desc. Bem', 'N/A')}</p>", unsafe_allow_html=True)
                    st.divider()
                    st.write(f"**Data da Última Sincronização:** {dados_ativo.get('Data últ. Loc', 'N/A')}")
                    st.write(f"**Fornecedor:** {dados_ativo.get('Fornecedor', 'N/A')}")
                    if "Portador" in dados_ativo and dados_ativo["Portador"] != "None":
                        st.write(f"**Responsável Atual (Portador):** {dados_ativo.get('Portador')}")

    # 3. HISTÓRICO VISUAL DETALHADO (Componentes Nativos à Prova de Falhas)
            with col_historico_fisico:
                st.subheader("🔄 Histórico de Passagens e Movimentações")
                
                if historico:
                    for idx, item in enumerate(historico):
                        is_entrada = item["Tipo"] == "RETORNO"
                        
                        # Definição das cores e rótulo do status
                        status_cor = "green" if is_entrada else "red"
                        titulo_operacao = "📥 RETORNO AO ESTOQUE" if is_entrada else "📤 ENVIO PARA UNIDADE"
                        
                        # Trata a exibição amigável do fluxo físico
                        if is_entrada:
                            origem = item.get('Origem_Fisica')
                            origem_str = f"Filial {int(float(origem))}" if isinstance(origem, (int, float)) or (isinstance(origem, str) and origem.replace('.0', '').isdigit()) else f"Filial {origem}"
                            fluxo_origem_destino = f"⬅️ {origem_str}"
                        else:
                            fluxo_origem_destino = f"➡️ {item['Origem_Destino']}"

                        chamado_exibido = item['Chamado'] if item['Chamado'] and str(item['Chamado']).strip() != "" and str(item['Chamado']).lower() != "none" else "N/A"
                        data_formatada = item['Data'].strftime('%d/%m/%Y')

                        # Criamos um container nativo do Streamlit para agrupar visualmente o Card
                        with st.container(border=True):
                            # Cabeçalho do Card (Status e Data)
                            col_status, col_data = st.columns([2, 1])
                            with col_status:
                                st.markdown(f":{status_cor}[**{titulo_operacao}**]")
                            with col_data:
                                st.markdown(f"<p style='text-align: right; color: #94A3B8; font-size: 0.85rem;'>📅 {data_formatada}</p>", unsafe_allow_html=True)
                            
                            # Fluxo Físico em destaque
                            st.markdown(f"### {fluxo_origem_destino}")
                            st.divider()
                            
                            # Grid de Informações usando as colunas nativas do Streamlit (Sem Divs quebrando!)
                            col_motivo, col_condicao, col_tecnico = st.columns(3)
                            
                            with col_motivo:
                                st.caption("MOTIVO DO FLUXO")
                                st.markdown(f"**{item['Motivo']}**")
                                
                            with col_condicao:
                                st.caption("CONDIÇÃO DO ITEM")
                                st.markdown(f"**{item['Condicao']}**")
                                
                            with col_tecnico:
                                st.caption("SUPORTE / TI")
                                st.markdown(f"👤 {item['Responsavel']}")
                                st.markdown(f"🎫 Chamado: **{chamado_exibido}**")
                else:
                    st.info("Nenhuma movimentação de TI (saídas ou retornos) foi registrada para este patrimônio.")