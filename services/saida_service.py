

from repositories import saida_repository , patrimonio_repository


def registrar_saida(dados):

    saida_repository.salvar_no_banco(
        dados["Patrimonio"],
        dados["Descricao"],
        dados["Qtd"],
        dados["Motivo"],
        dados["Status_Equipamento"],
        dados["Tipo_Destino"],
        dados["Destinatario"],
        dados["Usuario_Setor"],
        dados["Chamado"],
        dados["Tecnico"],
        dados["Data"],
        dados["Observacao"]
    )

    if dados["Tipo_Destino"] == "Loja / Filial":
        patrimonio_repository.atualiza_filial(dados["Patrimonio"],dados["Destinatario"])
    elif dados["Tipo_Destino"] == "Setor Interno":
            patrimonio_repository.atualiza_filial(dados["Patrimonio"],dados["Destinatario"])
            patrimonio_repository.atualiza_portador(dados["Patrimonio"], dados["Usuario_Setor"])
    elif dados["Tipo_Destino"] == "Assistencia":
            patrimonio_repository.atualiza_fornecedor(dados["Patrimonio"], dados["Destinatario"])


