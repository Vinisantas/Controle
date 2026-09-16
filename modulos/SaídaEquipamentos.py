from repositories import patrimonio_repository, saida_repository
from services import exportacao_service, saida_service
import streamlit as st
import pandas as pd


def configurar_tela():
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


def render_saidas():

    configurar_tela()

    saida_repository.inicializar_banco()

    st.title("🚀 Controle de Saída de Equipamentos")

    df_banco = saida_repository.carregar_dados()

    dados = render_formulario_saida()

    if dados["Enviar"]:

        erro = validar_saida(dados)

        if erro:
            st.error(erro)

        else:
            saida_service.registrar_saida(dados)

            st.success("Saída resgistrada com sucesso!")

            st.rerun()
    render_historico_saidas(df_banco)






def render_formulario_saida():
    # =========================================================
    # FORMULÁRIO DE REGISTRO DE SAÍDA
    # =========================================================

    margin_left, center_body, margin_right = st.columns([1, 2.4, 1])

    with center_body:

        st.markdown(
            '<div class="custom-form-container">',
            unsafe_allow_html=True
        )

        st.subheader("🆕 Registrar Saída")
        st.write("")

        # =====================================================
        # LINHA 1 — PATRIMÔNIO / DESCRIÇÃO / QUANTIDADE
        # =====================================================

        c_form_pat, c_form_desc, c_form_qtd = st.columns(
            [1.2, 2, 0.8],
            gap="medium"
        )

        with c_form_pat:

            Sem_Patrimonio = st.checkbox(
                "Item Insumo / Sem Patrimônio ⚠️"
            )

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
                Descricao = patrimonio_repository.buscar_patrimonio(Patrimonio)

        with c_form_desc:

            Descricao_Final = st.text_input(
                "Descrição do Item 📝",
                value=Descricao,
                placeholder="Nome ou descrição do ativo...",
                disabled=Desabilitar_Campos
            )

        with c_form_qtd:

            Qtd = st.number_input(
                "Qtd 🔢",
                min_value=1,
                value=1,
                step=1
            )

        # =====================================================
        # LINHA 2 — MOTIVO / CONDIÇÃO
        # =====================================================

        c_cat1, c_cat2 = st.columns(
            2,
            gap="medium"
        )

        with c_cat1:

            Motivo = st.selectbox(
                "Motivo da Saída 📋",
                options=[
                    "Substituição por Defeito (Incidente)",
                    "Upgrade / Melhoria",
                    "Nova Instalação / Demanda",
                    "Assistência",
                    "Empréstimo Temporário",
                    "Manutenção Preventiva"
                ]
            )

        with c_cat2:

            Status_Equipamento = st.selectbox(
                "Condição do Equipamento 🛡️",
                options=[
                    "Novo (Lacrado)",
                    "Seminovo / Recondicionado",
                    "Usado (Estado de Estoque)",
                    "Danificado / Com Defeito"
                ]
            )

        st.divider()

        # =====================================================
        # LINHA 3 — DESTINO
        # =====================================================

        Tipo_Destino = st.radio(
            "Destino da Saída 📍",
            options=[
                "Loja / Filial",
                "Setor Interno",
                "Assistencia"
            ],
            horizontal=True
        )

        # =====================================================
        # LINHA 4 — DESTINATÁRIO
        # =====================================================

        c_dest1, c_dest2 = st.columns(
            2,
            gap="medium"
        )

        with c_dest1:

            if Tipo_Destino == "Loja / Filial":

                placeholder_destino = "Ex: Filial Centro - Loja 02"
                label_destino = "Identificação da Loja 🏢"

            elif Tipo_Destino == "Setor Interno":

                placeholder_destino = "Ex: Controladoria / Almoxarifado"
                label_destino = "Nome do Setor Interno ⚙️"

            else:

                placeholder_destino = "Ex: Enio (Conserto)"
                label_destino = "Nome do Fornecedor"

            Destinatario_Final = st.text_input(
                label_destino,
                placeholder=placeholder_destino
            )

        with c_dest2:

            if Tipo_Destino == "Setor Interno":

                Usuario_Setor = st.text_input(
                    "Usuário Responsável no Setor 👤",
                    placeholder="Quem vai receber no setor..."
                )

            else:

                Usuario_Setor = ""

        # =====================================================
        # LINHA 5 — DADOS OPERACIONAIS
        # =====================================================

        c_op1, c_op2, c_op3 = st.columns(
            3,
            gap="medium"
        )

        with c_op1:

            Chamado = st.text_input(
                "Chamado / OS 🛠️",
                placeholder="#48220"
            )

        with c_op2:

            Tecnico = st.text_input(
                "Técnico Solicitante 👨‍💻",
                placeholder="Nome do técnico..."
            )

        with c_op3:

            Data = st.date_input(
                "Data de Saída 📅",
                format="DD/MM/YYYY"
            )

        # =====================================================
        # OBSERVAÇÕES
        # =====================================================

        Observacao = st.text_area(
            "Observações / Detalhes do Defeito caso Assistência",
            placeholder=(
                "Caso seja assistência ou substituição, "
                "descreva o problema, defeito relatado "
                "ou detalhes extras aqui..."
            )
        )

        st.write("")

        # =====================================================
        # BOTÃO
        # =====================================================

        submit_button = st.button(
            "🚀 Confirmar Saída do Equipamento",
            use_container_width=True,
            type="primary"
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

    # =========================================================
    # DEVOLVEMOS OS DADOS DO FORMULÁRIO
    # =========================================================

    return {
        "Patrimonio": Patrimonio,
        "Descricao": Descricao_Final,
        "Qtd": int(Qtd),
        "Motivo": Motivo,
        "Status_Equipamento": Status_Equipamento,
        "Tipo_Destino": Tipo_Destino,
        "Destinatario": Destinatario_Final,
        "Usuario_Setor": Usuario_Setor,
        "Chamado": Chamado,
        "Tecnico": Tecnico,
        "Data": Data,
        "Observacao": Observacao,
        "Enviar": submit_button
    }


def render_historico_saidas(df_banco):
    
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
                dados_excel = exportacao_service.converter_para_excel(df_filtrado)
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
                                
                            saida_repository.atualizar_linha_banco(id_registro, nome_coluna, novo_valor)
                            
                    st.toast("Alterações gravadas com sucesso!", icon="💾")
                    st.rerun()
                    
                if mudancas["deleted_rows"]:
                    for index_linha in mudancas["deleted_rows"]:
                        id_registro = int(df_filtrado.iloc[index_linha]["id"])
                        saida_repository.excluir_do_banco(id_registro)
                    st.toast("Registro removido.", icon="🗑️")
                    st.rerun()
            else:
                st.info("Nenhuma movimentação de saída localizada com os filtros selecionados.")








saida_repository.inicializar_banco()


def validar_saida(dados):
        if  dados["Patrimonio"] == "":
                return "O campo Patrimônio é obrigatório."
        
        if dados["Descricao"].strip() == "":
                return "A descrição do item é obrigatória."
        
        if dados["Destinatario"].strip() == "":
                return "Por favor, identifique o local ou pessoa de destino."
        
        if (dados["Tipo_Destino"] == "Setor Interno" and dados["Usuario_Setor"].strip() == ""):
            return "Por favor, digite o Usuário Responsável pelo setor."
        
        return None

