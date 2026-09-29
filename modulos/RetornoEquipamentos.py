import streamlit as st
import pandas as pd
import io
import streamlit.components.v1 as components
from services import retorno_service
from repositories import retorno_repository

def render_retornos():
    # Customização CSS para o formulário grafite premium e textos claros
    st.markdown("""
        <style>
        .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
        h1 { font-weight: 800; letter-spacing: -0.05em; color: #FFFFFF !important; }
        h3 { font-weight: 600; letter-spacing: -0.03em; color: #FFFFFF !important; }
        
        /* Container do Formulário Grafite com bordas arredondadas e suavizadas */
        .custom-form-container { 
            background-color: #06151C !important;
            border-radius: 12px !important; 
            border: none !important;
            padding: 25px !important;
            color: #F1F3F5 !important;
        }
        /* Estilização dos rótulos dos campos dentro do container escuro */
        .custom-form-container label p {
            color: #F1F3F5 !important;
            font-weight: 500 !important;
        }
        /* Estilização dos títulos internos */
        .custom-form-container h3 {
            color: #FFFFFF !important;
        }
        </style>
    """, unsafe_allow_html=True)
    DB_NAME = "Banco Dados/retorno.sqlite"
    BUSCA_PLAQUETA = "Banco Dados/cadastro_patrimonio.sqlite"

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

    # Inicializa e consulta o banco pela camada de repositório
    retorno_repository.inicializar_banco()

    # 2. CABEÇALHO PRINCIPAL DA APLICAÇÃO
    st.title(" Retorno de Equipamentos")
    st.markdown("Retornos de equipamentos de lojas e setores.")
    st.divider()

    # Carrega os dados para o painel
    df_banco = retorno_repository.carregar_dados()

    # 3. DISPOSIÇÃO DO LAYOUT PRINCIPAL
    _, center_body, _ = st.columns([0.5, 4, 0.5], gap="large")

    with center_body:
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
                try:
                    dados_patrimonio = retorno_repository.buscar_dados_patrimonio(Patrimonio)
                    if not dados_patrimonio:
                        st.error(f"❌ Plaqueta '{Patrimonio}' não localizada no cadastro.")
                    else:
                        Descricao = dados_patrimonio["descricao"]
                        Loja_Sugerida = dados_patrimonio["loja"]
                        st.toast("🔍 Dados do ativo carregados!", icon="✅")
                except sqlite3.Error as e:
                    st.error(f"Erro ao processar busca no cadastro: {e}")

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
                try:
                    retorno_service.registrar_retorno(Patrimonio, Descricao_Final, Loja_Final, Chamado, Notafiscal, Data, db_retorno=DB_NAME, db_cadastro=BUSCA_PLAQUETA)
                    st.cache_data.clear()
                except Exception as e:
                    st.error(str(e))
                else:
                    st.success("Equipamento registrado com sucesso!")
                    st.rerun()

    with center_body:
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
                
            st.caption("🔒 Histórico somente para consulta. Para corrigir uma movimentação, registre uma movimentação compensatória para preservar a rastreabilidade.")
            
            st.data_editor(
                df_banco,
                key="editor_retornos_v2",
                hide_index=True,
                use_container_width=True,
                num_rows="fixed",
                disabled=list(df_banco.columns),
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
            
        else:
            st.info("Nenhum registro correspondente encontrado para exibição.")
            # COLE ISSO NA ÚLTIMA LINHA DO SEU ARQUIVO DO FORMULÁRIO (NÃO ALTERA NADA DO SEU CÓDIGO)
    components.html(
                """
            <link rel="stylesheet" href="https://jsdelivr.net">
            <style>
            .simple-keyboard { position: fixed; bottom: 10px; left: 5%; width: 90%; max-width: 1000px; z-index: 99999; background: #E7EAED; box-shadow: 0px 4px 15px rgba(0,0,0,0.3); }
            .hg-button { height: 50px !important; font-size: 18px !important; }
            </style>
            <div class="simple-keyboard"></div>
            <script src="https://jsdelivr.net"></script>
            <script>
            const Keyboard = window.SimpleKeyboard.default;
            let activeInput = null;
            const myKeyboard = new Keyboard({
                onChange: input => { if(activeInput) { activeInput.value = input; activeInput.dispatchEvent(new Event("input", { bubbles: true })); } },
                layout: { default: ["q w e r t y u i o p", "a s d f g h j k l ç", "{shift} z x c v b n m {backspace}", "{space}"], shift: ["Q W E R T Y U I O P", "A S D F G H J K L Ç", "{shift} Z X C V B N M {backspace}", "{space}"] }
            });
            parent.document.querySelectorAll("input[type=text], textarea").forEach(input => {
                input.addEventListener("focus", e => { activeInput = e.target; myKeyboard.setInput(e.target.value); });
            });
            </script>
            """,
                height=0,
                width=0,
            )

            


