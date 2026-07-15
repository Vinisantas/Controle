import sqlite3
import streamlit as st
import pandas as pd
import os
import io

def render_saidas():
    # Customização CSS para centralização e tom premium
    st.markdown("""
        <style>
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        h1 { font-weight: 800; letter-spacing: -0.05em; color: #0F172A; }
        
        /* Centralização e largura controlada do formulário */
        .custom-form-container { 
            background-color: #1E293B !important; 
            border-radius: 16px !important; 
            border: 1px solid #334155 !important;
            padding: 30px !important;
            color: #F8FAFC !important;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
        }
        
        /* Estilização interna */
        .custom-form-container label p {
            color: #94A3B8 !important;
            font-weight: 600 !important;
            font-size: 0.85rem !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .custom-form-container h3 {
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Garante que a pasta existe
    if not os.path.exists("Banco Dados"):
        os.makedirs("Banco Dados")

    DB_NAME = "Banco Dados/saida.sqlite"
    BUSCA_PLAQUETA = "Banco Dados/cadastro_patrimonio.sqlite"

    def inicializar_banco():
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saida (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Patrimonio TEXT,
                Descricao TEXT,
                Qtd INTEGER,
                Motivo TEXT,
                Status_Equipamento TEXT,
                Tipo_Destino TEXT,
                Destinatario TEXT,
                Usuario_Setor TEXT,
                Chamado TEXT,
                Tecnico TEXT,
                Data DATE
            )
        ''')
        conn.commit()
        conn.close()

    def salvar_no_banco(Patrimonio, Descricao, Qtd, Motivo, Status_Equipamento, Tipo_Destino, Destinatario, Usuario_Setor, Chamado, Tecnico, Data):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO saida (Patrimonio, Descricao, Qtd, Motivo, Status_Equipamento, Tipo_Destino, Destinatario, Usuario_Setor, Chamado, Tecnico, Data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (Patrimonio, Descricao, Qtd, Motivo, Status_Equipamento, Tipo_Destino, Destinatario, Usuario_Setor, Chamado, Tecnico, Data.isoformat()))
        conn.commit()
        conn.close()

    def atualizar_linha_banco(id_registro, coluna, novo_valor):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(f'UPDATE saida SET {coluna} = ? WHERE id = ?', (novo_valor, id_registro))
        conn.commit()
        conn.close()

    def excluir_do_banco(id_registro):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM saida WHERE id = ?', (id_registro,))
        conn.commit()
        conn.close()

    def carregar_dados():
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query("SELECT * FROM saida ORDER BY Data DESC", conn, parse_dates=["Data"])
        conn.close()
        return df

    def converter_para_excel(df):
        output = io.BytesIO()
        df_excel = df.copy()
        if 'id' in df_excel.columns:
            df_excel = df_excel.drop(columns=['id'])
        if 'Data' in df_excel.columns:
            df_excel['Data'] = df_excel['Data'].dt.strftime('%d/%m/%Y')
            
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_excel.to_excel(writer, index=False, sheet_name='Saidas')
        return output.getvalue()

    inicializar_banco()

    # Header Minimalista
    st.title("🚀 Controle de Saída de Equipamentos")
    st.markdown("Gerenciamento centralizado de movimentações e envio de ativos de TI.")
    st.divider()

    df_banco = carregar_dados()

    # =========================================================
    # 3. LAYOUT CENTRALIZADO DO FORMULÁRIO (Usa colunas de margem)
    # =========================================================
    margin_left, center_body, margin_right = st.columns([1, 2.4, 1])

    with center_body:
        st.markdown('<div class="custom-form-container">', unsafe_allow_html=True)
        st.subheader("🆕 Registrar Saída")
        st.write("") 

        # Linha 1: Patrimônio e Opção de Insumo
        c_form_pat, c_form_desc, c_form_qtd = st.columns([1.2, 2, 0.8], gap="medium")
        
        with c_form_pat:
            Sem_Patrimonio = st.checkbox("Item Insumo / Sem Patrimônio ⚠️")
            Patrimonio = "SEM PATRIMÔNIO"
            Descricao = ""
            Desabilitar_Campos = False

            if not Sem_Patrimonio:
                Patrimonio_Input = st.text_input(
                    "Patrimônio 🏷️", 
                    placeholder="Plaqueta...",
                    key="txt_patrimonio"
                )
                Patrimonio = Patrimonio_Input.strip()
                Desabilitar_Campos = True
                
                if Patrimonio:
                    if os.path.exists(BUSCA_PLAQUETA):
                        try:
                            conn = sqlite3.connect(BUSCA_PLAQUETA)
                            cursor = conn.cursor()
                            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                            tabelas = [t for t in cursor.fetchall()]
                            
                            achou = False
                            for tabela in tabelas:
                                nome_real_tabela = tabela[0]
                                df_cadastro = pd.read_sql_query(f"SELECT * FROM [{nome_real_tabela}]", conn)
                                df_cadastro.columns = [c.strip() for c in df_cadastro.columns]
                                
                                if "Plaqueta" in df_cadastro.columns and "Desc. Bem" in df_cadastro.columns:
                                    df_cadastro['Plaqueta_Limpa'] = df_cadastro['Plaqueta'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
                                    resultado = df_cadastro[df_cadastro['Plaqueta_Limpa'] == Patrimonio]
                                    
                                    if not resultado.empty:
                                        Descricao = str(resultado['Desc. Bem'].iloc[0]).strip()
                                        if Patrimonio.isdigit():
                                            Patrimonio = str(int(float(Patrimonio)))
                                        achou = True
                                        break
                            conn.close()
                            
                            if not achou:
                                st.error(f"❌ Plaqueta '{Patrimonio}' não localizada.")
                                Descricao = ""
                            else:
                                st.toast("🔍 Dados do ativo carregados!", icon="✅")
                        except Exception as e:
                            st.error(f"Erro ao processar busca: {e}")
            else:
                Desabilitar_Campos = False

        with c_form_desc:
            Descricao_Final = st.text_input(
                "Descrição do Item 📝", 
                value=Descricao, 
                placeholder="Nome ou descrição do ativo...",
                disabled=Desabilitar_Campos
            )
            
        with c_form_qtd:
            Qtd = st.number_input("Qtd 🔢", min_value=1, value=1, step=1)

        # Linha 2: Categorização técnica da Saída (Motivo e Estado do item)
        c_cat1, c_cat2 = st.columns(2, gap="medium")
        with c_cat1:
            Motivo = st.selectbox(
                "Motivo da Saída 📋",
                options=["Substituição por Defeito (Incidente)", "Upgrade / Melhoria", "Nova Instalação / Demanda", "Empréstimo Temporário", "Manutenção Preventiva"]
            )
        with c_cat2:
            Status_Equipamento = st.selectbox(
                "Condição do Equipamento 🛡️",
                options=["Novo (Lacrado)", "Seminovo / Recondicionado", "Usado (Estado de Estoque)"]
            )

        st.divider()

        # Linha 3: Tipo de Destino
        Tipo_Destino = st.radio(
            "Destino da Saída 📍",
            options=["Loja / Filial", "Setor Interno", "Usuário Direto"],
            horizontal=True
        )

        # Linha 4: Campos Dinâmicos de Destino
        c_dest1, c_dest2 = st.columns(2, gap="medium")
        
        with c_dest1:
            if Tipo_Destino == "Loja / Filial":
                placeholder_destino = "Ex: Filial Centro - Loja 02"
                label_destino = "Identificação da Loja 🏢"
            elif Tipo_Destino == "Setor Interno":
                placeholder_destino = "Ex: Controladoria / Almoxarifado"
                label_destino = "Nome do Setor Interno ⚙️"
            else:
                placeholder_destino = "Ex: João Silva (Técnico)"
                label_destino = "Nome do Usuário Final 👤"
                
            Destinatario_Final = st.text_input(label_destino, placeholder=placeholder_destino)

        with c_dest2:
            if Tipo_Destino == "Setor Interno":
                Usuario_Setor = st.text_input("Usuário Responsável no Setor 👤", placeholder="Quem vai receber no setor...")
            else:
                Usuario_Setor = ""

        # Linha 5: Dados Operacionais
        c_op1, c_op2, c_op3 = st.columns(3, gap="medium")
        with c_op1:
            Chamado = st.text_input("Chamado / OS 🛠️", placeholder="#48220")
        with c_op2:
            Tecnico = st.text_input("Técnico Solicitante 👨‍💻", placeholder="Nome do técnico...")
        with c_op3:
            Data = st.date_input("Data de Saída 📅", format="DD/MM/YYYY")

        st.write("") 
        submit_button = st.button('🚀 Confirmar Saída do Equipamento', use_container_width=True, type="primary")
        st.markdown('</div>', unsafe_allow_html=True)

        # Valitações de Salvamento
        if submit_button:
            if not Sem_Patrimonio and Patrimonio == "":
                st.error("O campo Patrimônio é obrigatório.")
            elif Descricao_Final.strip() == "":
                st.error("A descrição do item é obrigatória.")
            elif Destinatario_Final.strip() == "":
                st.error(f"Por favor, identifique o local ou pessoa em '{label_destino}'.")
            elif Tipo_Destino == "Setor Interno" and Usuario_Setor.strip() == "":
                st.error("Por favor, digite o Usuário Responsável pelo setor.")
            else:
                salvar_no_banco(Patrimonio, Descricao_Final, int(Qtd), Motivo, Status_Equipamento, Tipo_Destino, Destinatario_Final, Usuario_Setor, Chamado, Tecnico, Data)
                st.success("Saída registrada com sucesso!")
                st.rerun()


    # =========================================================
    # 4. TABELA DE HISTÓRICO COMPLETA (Abaixo do Form)
    # =========================================================
    st.write("")
    st.write("")
    col_titulo_tab, col_busca, col_btn_exportar = st.columns([2, 1.5, 0.8])

    with col_titulo_tab:
        st.subheader("📋 Histórico de Movimentações")
        
    with col_busca:
        termo_busca = st.text_input(
            label="Buscar", 
            placeholder="🔍 Filtrar histórico geral...", 
            label_visibility="collapsed"
        )
        
    if termo_busca:
        df_banco = df_banco[
            df_banco['Patrimonio'].str.contains(termo_busca, case=False, na=False) |
            df_banco['Destinatario'].str.contains(termo_busca, case=False, na=False) |
            df_banco['Tipo_Destino'].str.contains(termo_busca, case=False, na=False) |
            df_banco['Tecnico'].str.contains(termo_busca, case=False, na=False) |
            df_banco['Motivo'].str.contains(termo_busca, case=False, na=False) |
            df_banco['Descricao'].str.contains(termo_busca, case=False, na=False)
        ]

    if not df_banco.empty:
        with col_btn_exportar:
            dados_excel = converter_para_excel(df_banco)
            st.download_button(
                label="📥 Exportar Excel",
                data=dados_excel,
                file_name="historico_saidas_ti.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
        df_editado = st.data_editor(
            df_banco,
            key="editor_saidas",
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic",
            height=450, 
            column_config={
                "id": None, 
                "Patrimonio": st.column_config.TextColumn("🏷️ Patrimônio", required=True),
                "Descricao": st.column_config.TextColumn("📝 Descrição"),
                "Qtd": st.column_config.NumberColumn("🔢 Qtd", format="%d"),
                "Motivo": st.column_config.SelectboxColumn("📋 Motivo Saída", options=["Substituição por Defeito (Incidente)", "Upgrade / Melhoria", "Nova Instalação / Demanda", "Empréstimo Temporário", "Manutenção Preventiva"]),
                "Status_Equipamento": st.column_config.SelectboxColumn("🛡️ Condição", options=["Novo (Lacrado)", "Seminovo / Recondicionado", "Usado (Estado de Estoque)"]),
                "Tipo_Destino": st.column_config.SelectboxColumn("📍 Tipo Destino", options=["Loja / Filial", "Setor Interno", "Usuário Direto"], required=True),
                "Destinatario": st.column_config.TextColumn("🏢/⚙️/👤 Destino / Local"),
                "Usuario_Setor": st.column_config.TextColumn("👤 Usuário Setor"),
                "Chamado": st.column_config.TextColumn("🛠️ Chamado/OS"),
                "Tecnico": st.column_config.TextColumn("👨‍💻 Técnico"),
                "Data": st.column_config.DateColumn("📅 Data Saída", format="DD/MM/YYYY")
            }
        )
        
        if "editor_saidas" in st.session_state:
            mudancas = st.session_state["editor_saidas"]
            if mudancas["edited_rows"]:
                for index_linha, colunas_alteradas in mudancas["edited_rows"].items():
                    id_registro = int(df_banco.iloc[index_linha]["id"])
                    for nome_coluna, novo_valor in colunas_alteradas.items():
                        if nome_coluna == "Data":
                            novo_valor = pd.to_datetime(novo_valor).date().isoformat()
                        atualizar_linha_banco(id_registro, nome_coluna, novo_valor)
                st.toast("Alterações gravadas com sucesso!", icon="💾")
                st.rerun()
                
            if mudancas["deleted_rows"]:
                for index_linha in mudancas["deleted_rows"]:
                    id_registro = int(df_banco.iloc[index_linha]["id"])
                    excluir_do_banco(id_registro)
                st.toast("Registro removido.", icon="🗑️")
                st.rerun()
    else:
        st.info("Nenhuma movimentação de saída localizada no banco de dados.")