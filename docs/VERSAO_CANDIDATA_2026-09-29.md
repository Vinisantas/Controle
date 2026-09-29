# Controle de Ativos TI — versão candidata

**Data:** 2026-09-29  
**Projeto:** `Controle Ativos TI - Copia`  
**Base Git no início da preparação:** `8ab4f60`  
**Escopo:** preparação de candidato após regressão integrada.

## Estado validado

- 12/12 telas principais: **PASS**
- 4/4 fluxos de serviço críticos: **PASS**
- `compileall`: **PASS**
- `git diff --check`: **PASS**
- `pip check`: **PASS** — sem dependências quebradas
- Escritas dos testes funcionais: somente em bancos temporários
- Projeto oficial: **não alterado**
- Bancos reais: **não utilizados para escrita nesta etapa**

## Regras críticas confirmadas

1. Equipamento marcado como `SEM CONSERTO` não pode sair do estoque.
2. Patrimônio com assistência aberta não pode registrar saída/retorno incompatível com o fluxo.
3. Após conclusão da assistência, o equipamento pode retornar ao estoque.
4. Saída, retorno e assistência mantêm transações com rollback em falhas.
5. Importação Senior compara por plaqueta, preserva existentes e adiciona somente novos registros.
6. Histórico operacional não deve ser substituído pela carga do Senior.

## Telas da regressão

| Tela | Resultado |
|---|---|
| Visão Geral | PASS |
| Consulta Patrimônio | PASS |
| Saída Equipamentos | PASS |
| Retorno Equipamentos | PASS |
| Assistências | PASS |
| Central de Dashboards | PASS |
| Histórico Geral | PASS |
| Dashboard Estoque | PASS |
| Dashboard Sup | PASS |
| Assistente de TI | PASS |
| Importação Senior | PASS |
| Saídas (Histórico) | PASS |

## Serviços críticos

| Fluxo | Resultado |
|---|---|
| Saída normal | PASS |
| Saída bloqueada por `SEM CONSERTO` | PASS |
| Retorno bloqueado por assistência aberta | PASS |
| Retorno após conclusão da assistência | PASS |

## Integridade técnica

A preparação do candidato não exigiu nova alteração de código. As alterações existentes foram preservadas. A compilação dos módulos principais e a validação das dependências do ambiente passaram sem erro.

## Critérios para não avançar diretamente para produção

- Ainda não tratar este documento como autorização de publicação em produção.
- Não executar o gerador completo do BI contra o PostgreSQL real durante validações.
- Não substituir o banco operacional por uma cópia do Senior.
- Antes de qualquer publicação, executar uma validação operacional controlada com dados e procedimentos definidos.

## Próximo marco

O projeto pode sair do ciclo de correções aleatórias e entrar em **validação candidata controlada**: congelar funcionalmente o comportamento atual, registrar qualquer nova falha reproduzível e somente então alterar código quando houver evidência.


## Validação operacional complementar — 2026-09-29

- Backup de 8 bancos SQLite criado e conferido por SHA-256 em `backups/2026-09-29_candidato/`.
- Ciclo saída → retorno: **PASS**.
- Assistência aberta bloqueia saída e retorno; após conclusão, retorno permitido: **PASS**.
- `SEM CONSERTO` bloqueia saída sem criar histórico: **PASS**.
- Importação Senior incremental preserva existentes e não duplica na reimportação: **PASS**.
- Inicialização Streamlit em cópia isolada e health check HTTP: **PASS**.
- Detalhes: `docs/RELATORIO_VALIDACAO_OPERACIONAL_2026-09-29.md`.
