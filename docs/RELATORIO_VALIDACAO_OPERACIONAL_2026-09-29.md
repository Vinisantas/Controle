# Relatório de validação operacional — 2026-09-29

**Projeto:** `Controle Ativos TI - Copia`  
**Base Git:** `8ab4f60`  
**Escopo:** backup verificável, ciclo de movimentação, assistência, proteção `SEM CONSERTO`, importação incremental Senior e smoke test de inicialização.

## Segurança dos dados

- **PASS:** backup de 8 arquivos SQLite em `backups/2026-09-29_candidato/`.
- **PASS:** tamanho e SHA-256 de cada cópia conferidos com a origem.
- **PASS:** operações de escrita dos testes ocorreram apenas em bancos temporários descartáveis.
- **PASS:** o teste de inicialização foi executado em uma cópia isolada do projeto; processo encerrado e cópia temporária removida.
- **PASS:** projeto oficial não foi aberto para alteração.

## Fluxos funcionais (bancos temporários)

| Teste | Resultado | Evidência |
|---|---|---|
| Patrimônio de teste encontrado | PASS | Plaqueta selecionada na cópia descartável |
| Saída registrada | PASS | Contagem do histórico aumentou em 1 |
| Cadastro atualizado para filial 10 | PASS | `Filial = 10` |
| Retorno registrado | PASS | Contagem do histórico aumentou em 1 |
| Retorno restaura estoque | PASS | `Filial = 1000`, `Portador = ESTOQUE TI` |
| Abertura de assistência sincroniza fornecedor | PASS | `Filial = 1000`, portador do fornecedor de teste |
| Saída durante assistência aberta | PASS | Operação bloqueada; exceção esperada |
| Retorno durante assistência aberta | PASS | Operação bloqueada; exceção esperada |
| Conclusão da assistência | PASS | Cadastro sincronizado para `ESTOQUE TI` |
| Retorno após conclusão | PASS | Operação permitida e histórico incrementado |
| Saída de equipamento `SEM CONSERTO` | PASS | Operação bloqueada |
| Nenhum histórico criado pelo bloqueio | PASS | Contagem de saídas permaneceu igual |
| Snapshot Senior salvo | PASS | 2 linhas no snapshot de teste |
| Somente ativo novo inserido | PASS | 1 inserção |
| Ativo existente não duplicado | PASS | Contagem permaneceu 1 |
| Descrição manual preservada | PASS | Valor manual permaneceu inalterado |
| Ativo novo disponível no cadastro | PASS | Plaqueta sintética encontrada |
| Reimportação não duplica | PASS | Segunda inserção retornou 0 |

**Resultado dos fluxos:** 18/18 PASS.

## Inicialização

- **PASS:** Streamlit iniciou em cópia isolada do projeto.
- **PASS:** endpoint local `/_stcore/health` respondeu `200` com `ok`.
- **PASS:** processo de teste foi encerrado.
- **PASS:** diretório temporário foi removido.

## Ocorrências durante os testes

1. A primeira execução do teste de ciclo acusou uma falha na asserção de filial. A inspeção do banco temporário confirmou que a aplicação havia atualizado corretamente para `Filial = 10`; o teste estava indexando incorretamente o valor retornado pela consulta. A asserção foi corrigida e o ciclo passou. **Não foi identificada falha de aplicação.**
2. A primeira tentativa de limpeza do banco temporário encontrou arquivos ainda abertos pelo próprio processo de teste. Após o encerramento do processo, os diretórios temporários foram removidos. Nenhum arquivo do projeto ou banco operacional foi alterado por isso.

## Arquivos alterados nesta etapa

- Criado `docs/RELATORIO_VALIDACAO_OPERACIONAL_2026-09-29.md`.
- Atualizado `docs/VERSAO_CANDIDATA_2026-09-29.md` com o resultado operacional.
- Criado backup em `backups/2026-09-29_candidato/` com 8 bancos SQLite e `MANIFESTO_SHA256.txt`.
- Nenhum arquivo de código da aplicação foi alterado nesta etapa.

## Resultado final

**PASS — candidato validado funcionalmente em ambiente temporário e inicialização confirmada em cópia isolada.** Isso não equivale, por si só, à autorização para substituir o ambiente operacional ou publicar em produção.
