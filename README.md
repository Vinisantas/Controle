# TI Controle

Sistema interno para gestão e rastreabilidade de ativos de TI.

## Objetivo

Centralizar consulta patrimonial, saídas, retornos, estoque, histórico e indicadores de suporte.

O projeto usa Streamlit na interface e mantém uma separação inicial entre telas, serviços e repositórios.

## Estado atual

- Interface: Streamlit
- Linguagem: Python
- Dados locais: SQLite
- Integrações: suporte a Movidesk/Asana conforme módulos configurados
- Dashboards operacionais: Streamlit
- BI analítico: Power BI Desktop
- Banco analítico: PostgreSQL na máquina Linux, acessado separadamente pelo IP dessa máquina
- Ambiente da Gestão: Windows + ambiente virtual Python

## Estrutura

~~~text
app.py                 # ponto de entrada
modulos/               # telas operacionais da Gestão
services/              # regras de negócio/orquestração
repositories/          # acesso aos bancos e dados
dashboards/             # dashboards operacionais
bi/                    # ETL e modelo analítico
Banco Dados/           # bancos SQLite locais
config/                # configuração compartilhada
database/              # camada de conexão futura
docs/                  # documentação técnica e de produto
ferramentas/           # manutenção e históricos técnicos
tests/                 # testes e diagnósticos
~~~

## Fluxo recomendado

~~~text
Tela Streamlit
     ↓
Service
     ↓
Repository
     ↓
Banco / integração
~~~

A tela deve cuidar principalmente de apresentação e entrada de dados. Regras de negócio devem ficar nos services e acesso persistente nos repositories.
## Principais módulos

### Operação

- Consulta de patrimônio
- Registro de saída de equipamento
- Registro de retorno
- Histórico de movimentações
- Consulta de patrimônio baixado
- Importação segura do Senior
- Controle de assistências e custos

### Acompanhamento

- Dashboard de estoque
- Dashboard de suporte
- Assistente de TI

## Convenções

Novas funções devem preferencialmente usar nomes em português, claros e verbos no infinitivo:

- carregar_saidas()
- buscar_patrimonio()
- registrar_saida()
- atualizar_filial()
- renderizar_historico()

Evite nomes genéricos como carregar_dados() quando o domínio puder ser explicitado.

## Banco de dados

Os arquivos SQLite estão em Banco Dados/.

Não mover, renomear ou excluir bancos existentes sem validar primeiro quais módulos os utilizam.

## Segurança

Credenciais, tokens e chaves devem ficar fora do código-fonte e fora do Git. O arquivo .env é ignorado pelo repositório.

A autenticação lê `APP_USUARIO` e `APP_SENHA` do arquivo `.env` local (não versionado). Antes de disponibilizar o sistema a outras pessoas, configure credenciais fortes e individuais, restrinja o acesso à máquina/rede e valide o processo de troca e recuperação de senha. Não compartilhe nem versione o `.env`.

## Design

A identidade visual definida para o sistema é corporativa, com grafite/cinza, alto contraste e vermelho discreto como destaque. A documentação visual está em docs/DESIGN.md.

## Próximos passos

Consulte docs/ROADMAP.md para a sequência de evolução sem reescrever o projeto inteiro.
## Execução local

No PowerShell, a partir da pasta do projeto:

~~~powershell
.\venv\Scripts\Activate.ps1
streamlit run app.py
~~~

## Regra importante para manutenção

Antes de alterar uma funcionalidade existente:

1. identificar a tela que chama a funcionalidade;
2. identificar o service responsável;
3. identificar o repository/banco envolvido;
4. fazer a menor alteração possível;
5. executar a tela afetada e validar o fluxo completo.

## Documentação

- docs/ARQUITETURA.md — organização e responsabilidades
- docs/DESIGN.md — identidade visual e UX
- docs/ROADMAP.md — melhorias planejadas e ordem de execução
