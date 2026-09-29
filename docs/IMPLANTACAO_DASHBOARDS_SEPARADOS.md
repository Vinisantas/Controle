# Implantação candidata — Gestão e Dashboards separados

## Objetivo

Manter a Gestão operacional na aplicação atual e executar os dashboards em um segundo contêiner Streamlit, para que os PCs das TVs abram somente a visualização.

## Arquivos desta etapa

- `dashboards_app.py`: entrada independente dos painéis.
- `docker-compose.v2.yml`: definição candidata com dois serviços.
- `requirements.txt`: inclui `streamlit-autorefresh`, usado pelos painéis.

## Endereços planejados no servidor Linux

- Gestão (mantém a porta atual): `http://192.168.201.140:8503`
- Dashboard de estoque: `http://192.168.201.140:8502/?view=estoque`
- Dashboard de suporte: `http://192.168.201.140:8502/?view=suporte`

## Antes de implantar

1. Confirmar no Linux o caminho real da pasta de bancos. O Compose candidato monta `./Banco Dados` em `/app/Banco Dados`, conforme os caminhos usados pelo código. Não iniciar se a pasta do servidor tiver outro nome ou não contiver os bancos corretos.
2. Fazer backup verificável de todos os bancos e do arquivo Compose atual da versão 1.
3. Confirmar que o `.env` existe no diretório de implantação, tem as variáveis necessárias e não será copiado para a imagem nem versionado.
4. Confirmar que as portas 8502 e 8503 estão livres/planejadas e que o acesso fica restrito à rede interna autorizada.
5. Construir e validar os serviços em janela controlada. A atualização do contêiner de Gestão pode causar uma breve interrupção; não executar sem combinar a janela.
6. Testar primeiro o healthcheck, depois o login da Gestão e, por fim, os dois dashboards em navegadores dos PCs das TVs.

## Segurança e operação

O dashboard foi separado da tela de Gestão, mas isso não substitui controles de rede. Os painéis podem exibir dados de chamados e solicitantes; publicar somente na rede interna aprovada e limitar o acesso conforme orientação da TI. O serviço de dashboards não recebe montagem dos bancos operacionais; ele recebe somente a pasta de cache local usada como contingência das integrações.

## Estado desta etapa

Preparação feita na cópia de desenvolvimento no Windows. Nenhum comando foi executado no servidor Linux, nenhum contêiner foi reiniciado e nenhum banco operacional foi alterado. A implantação permanece pendente de validação do caminho dos bancos e de acesso autorizado ao Linux.
