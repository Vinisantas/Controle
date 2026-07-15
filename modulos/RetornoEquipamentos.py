import sqlite3
import streamlit as st
import pandas as pd
import os
import io

def render_retornos():
    # Customização CSS para o formulário grafite premium e textos claros
    st.markdown("""
        <style>
        .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
        h1 { font-weight: 800; letter-spacing: -0.05em; color: #0F172A; }
        h3 { font-weight: 600; letter-spacing: -0.03em; color: #1E293B; }
        
        /* Container do Formulário Grafite com bordas arredondadas e suavizadas */
        .custom-form-container { 
            background-color: #1E293B !important; 
            border-radius: 12px !important; 
            border: none !important;
            padding: 25px !important;
            color: #F8FAFC !important;
        }
        /* Estilização dos rótulos dos campos dentro do container escuro */
        .custom-form-container label p {
            color: #F8FAFC !important;
            font-weight: 500 !important;
        }
        /* Estilização dos títulos internos */
        .custom-form-container h3 {
            color: #FFFFFF !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Garante que a pasta existe
    if not os.path.exists("Banco Dados"):
        os.makedirs("Banco Dados")

    DB_NAME = "Banco Dados/retorno.sqlite"
    BUSCA_PLAQUETA = "Banco Dados/cadastro_patrimonio.sqlite"

    def inicializar_banco():
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS retorno (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Patrimonio TEXT,
                Descricao TEXT,
                Loja TEXT,
                Chamado TEXT,
                Notafiscal TEXT,
                Data DATE
            )
        ''')
        conn.commit()
        conn.close()

    # FUNÇÃO ADICIONADA: Busca descrição no banco de cadastros por plaqueta/patrimônio
    def buscar_descricao_por_patrimonio(codigo):
        if not os.path.exists(BUSCA_PLAQUETA):
            return ""
        try:
            conn = sqlite3.connect(BUSCA_PLAQUETA)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tabelas = cursor.fetchall()
            if not tabelas:
                conn.close()
                return ""
                
            tabela_nome = tabelas[0][0] # Pega a primeira tabela existente
            
            # Busca dinâmica que tenta mapear pela plaqueta digitada (case-insensitive)
            query = f"SELECT * FROM {tabela_nome} LIMIT 1"
            df_temp = pd.read_sql_query(query, conn)
            colunas = [c.lower() for c in df_temp.columns]
            
            col_chave = 'Plaqueta' if 'Plaqueta' in colunas else ('patrimonio' if 'patrimonio' in colunas else df_temp.columns[0])
            col_valor = 'descricao' if 'descricao' in colunas else ('nome' if 'nome' in colunas else df_temp.columns[1])

            cursor.execute(f"SELECT {col_valor} FROM {tabela_nome} WHERE UPPER({col_chave}) = ?", (codigo.upper(),))
            resultado = cursor.fetchone()
            conn.close()
            
            if resultado:
                return resultado[0]
        except Exception as e:
            st.error(f"Erro ao acessar banco de plaquetas: {e}")
        return ""

    def salvar_no_banco(Patrimonio, Descricao, Loja, Chamado, Notafiscal, Data):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO retorno (Patrimonio, Descricao, Loja, Chamado, Notafiscal, Data)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (Patrimonio, Descricao, Loja, Chamado, Notafiscal, Data.isoformat()))
        conn.commit()
        conn.close()



    def atualizar_linha_banco(id_registro, coluna, novo_valor):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(f'UPDATE retorno SET {coluna} = ? WHERE id = ?', (novo_valor, id_registro))
        conn.commit()
        conn.close()

    def excluir_do_banco(id_registro):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM retorno WHERE id = ?', (id_registro,))
        conn.commit()
        conn.close()

    def carregar_dados():
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query("SELECT * FROM retorno ORDER BY Data DESC", conn, parse_dates=["Data"])
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
            df_excel.to_excel(writer, index=False, sheet_name='Retornos')
        return output.getvalue()

    # Inicializa banco de dados
    inicializar_banco()

    # 2. CABEÇALHO PRINCIPAL DA APLICAÇÃO
    st.title(" Retorno de Equipamentos")
    st.markdown("Retornos de equipamentos de lojas e setores.")
    st.divider()

    # Carrega os dados para o painel
    df_banco = carregar_dados()

    # 3. DISPOSIÇÃO DO LAYOUT PRINCIPAL
    col_form, col_tabela = st.columns([1, 2.5], gap="large")

    with col_form:
        # Mantém o design escuro customizado
        st.markdown('<div class="custom-form-container">', unsafe_allow_html=True)
        st.subheader("🆕 Registrar Entrada")
        st.write("") 

        # 1. Opção para itens sem patrimônio de fábrica ou não catalogados
        Sem_Patrimonio = st.checkbox("Item sem Patrimônio / Não Catalogado ⚠️")
        
        # Inicialização das variáveis que vão abastecer os campos
        Patrimonio = "SEM PATRIMÔNIO"
        Descricao = ""
        Loja_Sugerida = ""
        Desabilitar_Campos = False

        # 2. FLUXO COM PATRIMÔNIO: Ativa a busca automática e puxa os dados do banco
        if not Sem_Patrimonio:
            Patrimonio_Input = st.text_input(
                "Patrimônio 🏷️", 
                placeholder="Digite a plaqueta e mude de campo",
                key="txt_patrimonio"
            )
            Patrimonio = Patrimonio_Input.strip()
            Desabilitar_Campos = True  # Bloqueia a descrição por segurança para ativos oficiais
            
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
                                # Tratamento para floats e strings do banco de dados de patrimônios
                                df_cadastro['Plaqueta_Limpa'] = df_cadastro['Plaqueta'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
                                resultado = df_cadastro[df_cadastro['Plaqueta_Limpa'] == Patrimonio]
                                
                                if not resultado.empty:
                                    Descricao = str(resultado['Desc. Bem'].iloc[0]).strip()
                                    
                                    # --- CORREÇÃO DO FORMATO INTEIRO (REMOÇÃO DO .0) ---
                                    # Se o usuário digitou um número puro, força o patrimônio final a salvar como inteiro limpo
                                    if Patrimonio.isdigit():
                                        Patrimonio = str(int(float(Patrimonio)))
                                    
                                    # Tenta buscar a coluna 'Loja' ou 'Filial' se ela existir no seu banco de cadastros
                                    col_loja_banco = next((c for c in df_cadastro.columns if c.lower() in ['loja', 'filial', 'unidade']), None)
                                    if col_loja_banco:
                                        valor_loja_bruto = resultado[col_loja_banco].iloc[0]
                                        
                                        # Se a loja também vier com .0 por erro de importação, limpa ela aqui
                                        if pd.api.types.is_number(valor_loja_bruto) or str(valor_loja_bruto).endswith('.0'):
                                            Loja_Sugerida = str(int(float(valor_loja_bruto))).strip()
                                        else:
                                            Loja_Sugerida = str(valor_loja_bruto).strip()
                                    
                                    achou = True
                                    break
                        conn.close()
                        
                        if not achou:
                            st.error(f"❌ Plaqueta '{Patrimonio}' não localizada no cadastro.")
                            Descricao = ""
                            Loja_Sugerida = ""
                        else:
                            st.toast("🔍 Dados do ativo carregados!", icon="✅")
                            
                    except Exception as e:
                        st.error(f"Erro ao processar busca: {e}")

        # 3. FLUXO SEM PATRIMÔNIO: Libera tudo para o usuário escrever o que quiser
        else:
            Desabilitar_Campos = False # Permite editar a descrição livremente

        # 4. Exibição dos Campos de Texto baseados no fluxo selecionado
        
        # Descrição: Bloqueada se for ativo com patrimônio válido, aberta se for item sem patrimônio
        Descricao_Final = st.text_input(
            "Descrição do Item 📝", 
            value=Descricao, 
            placeholder="Digite a descrição se o item não tiver patrimônio...",
            disabled=Desabilitar_Campos
        )
        
        # Loja de Origem: Sempre EDITÁVEL, mas pré-preenchida se o banco trouxer a informação
        Loja_Final = st.text_input(
            "Loja de Origem 🏢", 
            value=Loja_Sugerida,
            placeholder="Ex: Filial Centro (Você pode alterar este campo)"
        )
        
        # Campos operacionais complementares
        c_form1, c_form2 = st.columns(2)
        with c_form1:
            Chamado = st.text_input("Chamado 🛠️", placeholder="#45091")
        with c_form2:
            Notafiscal = st.text_input("Nota Fiscal 📄", placeholder="NF-7731")
            
        Data = st.date_input("Data de Retorno 📅", format="DD/MM/YYYY")

        st.write("") 
        submit_button = st.button('💾 Confirmar Recebimento', use_container_width=True, type="primary")
        st.markdown('</div>', unsafe_allow_html=True)

        # 5. Validação de Salvamento Dinâmica
        if submit_button:
            if not Sem_Patrimonio and Patrimonio == "":
                st.error("O campo Patrimônio é obrigatório quando a opção 'Sem Patrimônio' está desmarcada.")
            elif Descricao_Final.strip() == "":
                st.error("A descrição do item é obrigatória para realizar o recebimento.")
            elif Loja_Final.strip() == "":
                st.error("Por favor, informe ou confirme a Loja de Origem.")
            else:
                # Grava no banco com o patrimônio convertido em texto de número inteiro puro
                salvar_no_banco(Patrimonio, Descricao_Final, Loja_Final, Chamado, Notafiscal, Data)
                st.success("Equipamento registrado com sucesso!")
                st.rerun()

    with col_tabela:
        col_titulo_tab, col_busca, col_btn_exportar = st.columns([1.5, 1.5, 1])
        
        with col_titulo_tab:
            st.subheader("📋 Histórico Operacional")
            
        with col_busca:
            termo_busca = st.text_input(
                label="Buscar", 
                placeholder="🔍 Buscar por Loja ou Patrimônio...", 
                label_visibility="collapsed"
            )
            
        if termo_busca:
            df_banco = df_banco[
                df_banco['Patrimonio'].str.contains(termo_busca, case=False, na=False) |
                df_banco['Loja'].str.contains(termo_busca, case=False, na=False) |
                df_banco['Descricao'].str.contains(termo_busca, case=False, na=False)
            ]
        
        if not df_banco.empty:
            with col_btn_exportar:
                dados_excel = converter_para_excel(df_banco)
                st.download_button(
                    label="📥 Exportar Excel",
                    data=dados_excel,
                    file_name="relatorio_retornos.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                
            st.caption("✨ *Tabela interativa: Dê duplo clique em qualquer célula para corrigir valores diretamente.*")
            
            df_editado = st.data_editor(
                df_banco,
                key="editor_retornos",
                hide_index=True,
                use_container_width=True,
                num_rows="dynamic",
                height=480, 
                column_config={
                    "id": None, 
                    "Patrimonio": st.column_config.TextColumn("🏷️ Patrimônio", required=True),
                    "Descricao": st.column_config.TextColumn("📝 Descrição do Equipamento"),
                    "Loja": st.column_config.TextColumn("🏢 Loja"),
                    "Chamado": st.column_config.TextColumn("🛠️ Chamado ID"),
                    "Notafiscal": st.column_config.TextColumn("📄 Nota Fiscal"),
                    "Data": st.column_config.DateColumn("📅 Data de Entrada", format="DD/MM/YYYY")
                }
            )
            
            if "editor_retornos" in st.session_state:
                mudancas = st.session_state["editor_retornos"]
                
                if mudancas["edited_rows"]:
                    for index_linha, colunas_alteradas in mudancas["edited_rows"].items():
                        id_registro = int(df_banco.iloc[index_linha]["id"])
                        for nome_coluna, novo_valor in colunas_alteradas.items():
                            if nome_coluna == "Data":
                                novo_valor = pd.to_datetime(novo_valor).date().isoformat()
                            atualizar_linha_banco(id_registro, nome_coluna, novo_valor)
                    st.toast("Alteração salva com sucesso!", icon="💾")
                    st.rerun()
                    
                if mudancas["deleted_rows"]:
                    for index_linha in mudancas["deleted_rows"]:
                        id_registro = int(df_banco.iloc[index_linha]["id"])
                        excluir_do_banco(id_registro)
                    st.toast("Registro removido permanentemente.", icon="🗑️")
                    st.rerun()
        else:
            st.info("Nenhum registro correspondente encontrado para exibição.")