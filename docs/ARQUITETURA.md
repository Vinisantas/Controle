# Arquitetura — TI Controle

## Objetivo

Manter o sistema simples, compreensível e seguro, separando operação, acompanhamento e análise de dados.

## Camadas

```text
Gestão de Ativos
      ↓
Services
      ↓
Repositories
      ↓
SQLite / APIs

Dashboards
      ↓
Fontes operacionais e integrações
      ↓
Visualização

BI
      ↓
ETL / modelo analítico
      ↓
PostgreSQL / Power BI
```

## Organização atual

```text
app.py                 # entrada e composição da Gestão
modulos/               # telas operacionais, autenticação, estilos e navegação
services/              # regras de negócio
repositories/          # persistência
dashboards/            # dashboards operacionais
bi/                    # ETL e modelo analítico
Banco Dados/           # fontes SQLite
config/                # configuração compartilhada
ferramentas/           # manutenção e históricos técnicos
tests/                 # testes e diagnósticos
docs/                  # documentação
```

## Responsabilidades

### Gestão

A Gestão registra e consulta a operação: patrimônio, saídas, retornos, estoque, assistências, importação Senior e histórico.

As telas não devem concentrar regras de negócio nem SQL. Elas chamam services e repositories.

### Dashboards

Dashboards apresentam indicadores operacionais e de suporte. Eles não devem criar ou alterar movimentações patrimoniais.

### BI

A camada BI lê as fontes operacionais e integrações, transforma os dados e publica o modelo analítico para PostgreSQL/Power BI.

O BI analítico é consumido no Power BI Desktop. O PostgreSQL é acessado separadamente pelo IP da máquina Linux; a Gestão em Streamlit não deve abrir conexão com esse banco nem executar o ETL. O BI não deve ser executado diretamente pela interface da Gestão.

## Regras

- Uma regra de negócio deve existir em um único lugar.
- SQL de persistência deve ficar em repositories quando aplicável.
- Integrações externas devem ficar isoladas de telas.
- Bancos SQLite existentes não devem ser renomeados ou excluídos sem validação.
- Mudanças arquiteturais devem ser testadas antes de seguir para o projeto oficial.

## Próxima evolução

1. reduzir responsabilidades do app.py;
2. centralizar a navegação da Gestão;
3. concluir a separação funcional dos dashboards;
4. evoluir o ETL em bi/ para assistências e integrações;
5. centralizar conexões e configurações compartilhadas;
6. automatizar a atualização do modelo analítico.

A migração é incremental e preserva as funcionalidades já testadas.
