# Importação Senior

## Objetivo

Separar a informação cadastral exportada do Senior do histórico operacional do TI Controle.

O Excel baixado é uma fonte externa e deve ser preservado como snapshot.

## Fluxo

```text
Senior
  ↓
Excel
  ↓
Importação Senior
  ↓
senior_raw.sqlite / GERAL
  ↓
Comparação
  ↓
Sincronização controlada
  ↓
Cadastro operacional
```

## Regra principal

Uma nova exportação do Senior não deve apagar saídas, retornos, assistências ou outros eventos registrados pelo TI Controle.

O registro que não aparecer no novo Excel também não é automaticamente considerado baixa.## O que foi implementado

A tela `📥 Importação Senior` permite:

- selecionar o Excel exportado;
- padronizar as plaquetas;
- visualizar uma prévia;
- comparar novos, existentes e ausentes;
- guardar o snapshot como GERAL/RAW;
- consultar o histórico de importações.

A etapa de armazenamento não altera `cadastro_patrimonio.sqlite`.

## Próxima etapa

A sincronização deverá ser uma operação separada e explícita, com prévia das alterações antes da confirmação.

Campos vindos do Senior devem ser tratados como dados de origem externa. Campos operacionais do TI Controle devem permanecer sob controle do sistema.

Exemplo:

| Informação | Origem |
|---|---|
| Descrição | Senior |
| Fornecedor | Senior |
| Data aquisição | Senior |
| Última saída | TI Controle |
| Última assistência | TI Controle |
| Custo de assistência | TI Controle |
| Histórico de movimentações | TI Controle |
## Evolução planejada

### Fase 1 — Segurança da carga

Snapshot bruto, histórico de importações e comparação sem alteração automática.

### Fase 2 — Sincronização controlada

Tela mostra exatamente quais campos serão atualizados antes da confirmação.

### Fase 3 — Auditoria

Registrar quem importou, quando importou, arquivo utilizado e resultado da sincronização.

### Fase 4 — BI

Usar o cadastro consolidado e as tabelas de eventos para gerar indicadores de estoque, movimentação, assistência e custo.

## Princípio de arquitetura

**Senior = fonte cadastral externa**  
**TI Controle = operação e histórico**  
**Power BI = análise**
