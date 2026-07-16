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
                Data DATE,
                Observacao TEXT,
                Baixa_Senior INTEGER DEFAULT 0
            )
        ''')
        
        # Migração automática: Adiciona a coluna Observacao se o banco já existia sem ela
        try:
            cursor.execute("SELECT Observacao FROM saida LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE saida ADD COLUMN Observacao TEXT")
            conn.commit()

        # Migração automática: Adiciona a coluna Baixa_Senior se não existir
        try:
            cursor.execute("SELECT Baixa_Senior FROM saida LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE saida ADD COLUMN Baixa_Senior INTEGER DEFAULT 0")
            conn.commit()
            
        conn.commit()
        conn.close()

    def salvar_no_banco(Patrimonio, Descricao, Qtd, Motivo, Status_Equipamento, Tipo_Destino, Destinatario, Usuario_Setor, Chamado, Tecnico, Data, Observacao):
        # 1. SALVA NO BANCO DE HISTÓRICO DE SAÍDAS (Começa sempre sem baixa na Senior: 0)
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO saida (Patrimonio, Descricao, Qtd, Motivo, Status_Equipamento, Tipo_Destino, Destinatario, Usuario_Setor, Chamado, Tecnico, Data, Observacao, Baixa_Senior)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        ''', (Patrimonio, Descricao, Qtd, Motivo, Status_Equipamento, Tipo_Destino, Destinatario, Usuario_Setor, Chamado, Tecnico, Data.isoformat(), Observacao))
        conn.commit()
        conn.close()

        # 2. ATUALIZA PORTADOR E LOCAL NO CADASTRO DE PATRIMÔNIO (Se houver patrimônio válido)
        if Patrimonio and Patrimonio != "SEM PATRIMÔNIO":
            if os.path.exists(BUSCA_PLAQUETA):
                try:
                    conn_pat = sqlite3.connect(BUSCA_PLAQUETA)
                    cursor_pat = conn_pat.cursor()
                    
                    # Encontra o nome exato da tabela no banco de patrimônios
                    cursor_pat.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tabelas = cursor_pat.fetchall()
                    
                    for tabela in tabelas:
                        nome_tabela = tabela[0]
                        # Atualiza os dados de Portador e Local com base na Plaqueta
                        cursor_pat.execute(f"""
                            UPDATE [{nome_tabela}]
                            SET Portador = ?, "Desc. Local" = ?
                            WHERE RTRIM(LTRIM(REPLACE(Plaqueta, '.0', ''))) = ?
                        """, (Destinatario, Destinatario, Patrimonio))
                        
                    conn_pat.commit()
                    conn_pat.close()
                    # Limpa o cache para atualizar a busca do patrimônio em tempo real!
                    st.cache_data.clear()
                except Exception as e:
                    st.error(f"⚠️ Erro ao atualizar o Portador no cadastro de patrimônio: {e}")

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
        # Convertemos Baixa_Senior para booleano para funcionar perfeitamente no checkbox do Streamlit
        df = pd.read_sql_query("SELECT * FROM saida ORDER BY Data DESC", conn, parse_dates=["Data"])
        df['Baixa_Senior'] = df['Baixa_Senior'].astype(bool)
        conn.close()
        return df

    def converter_para_excel(df):
        output = io.BytesIO()
        df_excel = df.copy()
        if 'id' in df_excel.columns:
            df_excel = df_excel.drop(columns=['id'])
        if 'Data' in df_excel.columns:
            df_excel['Data'] = df_excel['Data'].dt.strftime('%d/%m/%Y')
        if 'Baixa_Senior' in df_excel.columns:
            df_excel['Baixa_Senior'] = df_excel['Baixa_Senior'].apply(lambda x: 'Sim' if x else 'Não')
            
        # Reordena o Excel também para iniciar com Baixa_Senior
        colunas_restantes = [col for col in df_excel.columns if col != 'Baixa_Senior']
        df_excel = df_excel[['Baixa_Senior'] + colunas_restantes]
            
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
                            st.error(f"Erro ao acessar base de patrimônio: {e}")
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
                options=["Novo (Lacrado)", "Seminovo / Recondicionado", "Usado (Estado de Estoque)", "Danificado / Com Defeito"]
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

        # NOVA SEÇÃO: Observações e Defeito
        Observacao = st.text_area(
            "Observações / Detalhes do Defeito (Assistência) 🔍", 
            placeholder="Caso seja assistência ou substituição, descreva o problema, defeito relatado ou detalhes extras aqui..."
        )

        st.write("") 
        submit_button = st.button('🚀 Confirmar Saída do Equipamento', use_container_width=True, type="primary")
        st.markdown('</div>', unsafe_allow_html=True)

        # Validações de Salvamento
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
                salvar_no_banco(
                    Patrimonio, Descricao_Final, int(Qtd), Motivo, Status_Equipamento, 
                    Tipo_Destino, Destinatario_Final, Usuario_Setor, Chamado, Tecnico, Data, Observacao
                )
                st.success("Saída registrada com sucesso!")
                st.rerun()


    # =========================================================
    # 4. TABELA DE HISTÓRICO E CONTROLE DE BAIXAS (Abaixo do Form)
    # =========================================================
    st.write("")
    st.write("")
    
    st.subheader("📋 Histórico & Controle de Baixas")
    
    # Área de Filtros Estratégica (Para você poder filtrar por mês e o que falta baixar)
    with st.expander("🔍 Filtros de Busca Avançados", expanded=True):
        col_filtro_data, col_filtro_patrimonio, col_filtro_baixa = st.columns([1.5, 1.5, 1.5])
        
        with col_filtro_data:
            filtro_mes_ano = st.text_input("Mês/Ano (Ex: 04/2026)", placeholder="MM/AAAA (Deixe em branco para tudo)")
            
        with col_filtro_patrimonio:
            # Opções: Mostrar tudo, Somente com Patrimônio, Somente SEM patrimônio
            filtro_pat = st.selectbox(
                "Filtrar por Tipo de Ativo",
                options=["Todos", "Apenas Com Patrimônio", "Apenas Sem Patrimônio"]
            )
            
        with col_filtro_baixa:
            # Opções: Mostrar tudo, Baixados, Pendentes na Senior
            filtro_baixa = st.selectbox(
                "Status Baixa Senior",
                options=["Todos", "Pendente na Senior ❌", "Baixado na Senior ✅"]
            )
            
        termo_busca = st.text_input(
            label="Buscar por texto", 
            placeholder="🔍 Filtrar por qualquer campo (técnico, destino, descrição...)", 
        )

    # Aplicando os Filtros no DataFrame
    df_filtrado = df_banco.copy()

    # Filtro de Mês/Ano
    if filtro_mes_ano:
        try:
            mes, ano = filtro_mes_ano.split('/')
            df_filtrado = df_filtrado[
                (df_filtrado['Data'].dt.strftime('%m') == mes) & 
                (df_filtrado['Data'].dt.strftime('%Y') == ano)
            ]
        except ValueError:
            st.warning("⚠️ Formato de Mês/Ano inválido. Use MM/AAAA")

    # Filtro de Tipo de Ativo
    if filtro_pat == "Apenas Com Patrimônio":
        df_filtrado = df_filtrado[df_filtrado['Patrimonio'] != "SEM PATRIMÔNIO"]
    elif filtro_pat == "Apenas Sem Patrimônio":
        df_filtrado = df_filtrado[df_filtrado['Patrimonio'] == "SEM PATRIMÔNIO"]

    # Filtro de Status de Baixa Senior
    if filtro_baixa == "Pendente na Senior ❌":
        df_filtrado = df_filtrado[df_filtrado['Baixa_Senior'] == False]
    elif filtro_baixa == "Baixado na Senior ✅":
        df_filtrado = df_filtrado[df_filtrado['Baixa_Senior'] == True]

    # Filtro de Busca Geral por Texto
    if termo_busca:
        df_filtrado = df_filtrado[
            df_filtrado['Patrimonio'].str.contains(termo_busca, case=False, na=False) |
            df_filtrado['Destinatario'].str.contains(termo_busca, case=False, na=False) |
            df_filtrado['Tipo_Destino'].str.contains(termo_busca, case=False, na=False) |
            df_filtrado['Tecnico'].str.contains(termo_busca, case=False, na=False) |
            df_filtrado['Motivo'].str.contains(termo_busca, case=False, na=False) |
            df_filtrado['Descricao'].str.contains(termo_busca, case=False, na=False) |
            df_filtrado['Observacao'].str.contains(termo_busca, case=False, na=False)
        ]

    # Renderização da Tabela de Edição
    if not df_filtrado.empty:
        # ⚡ REORDENAÇÃO FÍSICA DAS COLUNAS: Move 'Baixa_Senior' para a primeira posição
        outras_colunas = [col for col in df_filtrado.columns if col != 'Baixa_Senior']
        df_filtrado = df_filtrado[['Baixa_Senior'] + outras_colunas]

        # Botão Exportar Excel fica logo acima da tabela alinhado à direita
        col_vazia, col_btn_exportar = st.columns([4, 1])
        with col_btn_exportar:
            dados_excel = converter_para_excel(df_filtrado)
            st.download_button(
                label="📥 Exportar Excel",
                data=dados_excel,
                file_name="historico_saidas_ti.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
        df_editado = st.data_editor(
            df_filtrado,
            key="editor_saidas",
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic",
            height=450, 
            column_config={
                "id": None, 
                "Baixa_Senior": st.column_config.CheckboxColumn("✔️ Baixa Senior?", help="Marque se já realizou a baixa desse item na Senior manualmente.", default=False),
                "Patrimonio": st.column_config.TextColumn("🏷️ Patrimônio", required=True),
                "Descricao": st.column_config.TextColumn("📝 Descrição"),
                "Qtd": st.column_config.NumberColumn("🔢 Qtd", format="%d"),
                "Motivo": st.column_config.SelectboxColumn("📋 Motivo Saída", options=["Substituição por Defeito (Incidente)", "Upgrade / Melhoria", "Nova Instalação / Demanda", "Empréstimo Temporário", "Manutenção Preventiva"]),
                "Status_Equipamento": st.column_config.SelectboxColumn("🛡️ Condição", options=["Novo (Lacrado)", "Seminovo / Recondicionado", "Usado (Estado de Estoque)", "Danificado / Com Defeito"]),
                "Tipo_Destino": st.column_config.SelectboxColumn("📍 Tipo Destino", options=["Loja / Filial", "Setor Interno", "Usuário Direto"], required=True),
                "Destinatario": st.column_config.TextColumn("🏢/⚙️/👤 Destino / Local"),
                "Usuario_Setor": st.column_config.TextColumn("👤 Usuário Setor"),
                "Chamado": st.column_config.TextColumn("🛠️ Chamado/OS"),
                "Tecnico": st.column_config.TextColumn("👨‍💻 Técnico"),
                "Data": st.column_config.DateColumn("📅 Data Saída", format="DD/MM/YYYY"),
                "Observacao": st.column_config.TextColumn("🔍 Observações / Defeito")
            }
        )
        
        # Processando Edições na Tabela
        if "editor_saidas" in st.session_state:
            mudancas = st.session_state["editor_saidas"]
            
            if mudancas["edited_rows"]:
                for index_linha, colunas_alteradas in mudancas["edited_rows"].items():
                    # Mapeia o index relativo da tela para o ID correto do Banco usando o DataFrame Filtrado
                    id_registro = int(df_filtrado.iloc[index_linha]["id"])
                    
                    for nome_coluna, novo_valor in colunas_alteradas.items():
                        # Trata tipo de campo Data
                        if nome_coluna == "Data":
                            novo_valor = pd.to_datetime(novo_valor).date().isoformat()
                        
                        # Trata o checkbox da Baixa Senior transformando bool em int (0 ou 1) para salvar no sqlite
                        if nome_coluna == "Baixa_Senior":
                            novo_valor = 1 if novo_valor else 0
                            
                        atualizar_linha_banco(id_registro, nome_coluna, novo_valor)
                        
                st.toast("Alterações gravadas com sucesso!", icon="💾")
                st.rerun()
                
            if mudancas["deleted_rows"]:
                for index_linha in mudancas["deleted_rows"]:
                    id_registro = int(df_filtrado.iloc[index_linha]["id"])
                    excluir_do_banco(id_registro)
                st.toast("Registro removido.", icon="🗑️")
                st.rerun()
    else:
        st.info("Nenhuma movimentação de saída localizada com os filtros selecionados.")