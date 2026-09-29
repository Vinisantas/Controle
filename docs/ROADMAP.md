# Roadmap — TI Controle

## Visão

O projeto evolui em três frentes integradas:

1. **Gestão** — operação dos ativos;
2. **Dashboards** — acompanhamento operacional;
3. **BI** — análise histórica e executiva.

---

## 1. Gestão de Ativos

### Concluído / validado

- [x] consulta patrimonial;
- [x] saída de equipamentos;
- [x] retorno de equipamentos;
- [x] histórico geral;
- [x] estoque;
- [x] assistências técnicas;
- [x] histórico e custos de assistência;
- [x] Assistente de TI;
- [x] importação incremental do Senior;
- [x] testes de rollback e consistência;
- [x] proteção contra movimentação durante assistência aberta.

### Próximos

- [x] extrair renderização das páginas para modulos/navegacao.py;
- [x] centralizar o despacho da navegação;
- [x] extrair estilos compartilhados para modulos/estilos.py;
- [x] organizar a sidebar por Operação, Acompanhamento e Administração;
- [x] criar página inicial operacional com atalhos somente de navegação;
- [x] extrair login/autenticação para modulos/autenticacao.py;
- [x] impedir autenticação quando APP_USUARIO ou APP_SENHA não estiverem configurados;
- [ ] padronizar tabelas, filtros e estados;
- [ ] registrar usuário/data das alterações;
- [ ] concluir análise anual de assistências;
- [ ] calcular tempo médio em assistência.

---

## 2. Dashboards

### Existente / validado

- [x] Dashboard Estoque;
- [x] Dashboard SUP;
- [x] integração de suporte preparada;
- [x] separação física dos módulos em dashboards/;
- [x] criar Central de Dashboards com atalhos para as visões existentes e limites claros entre Gestão, Dashboards e BI.

### Próximos

- [ ] padronizar filtros e indicadores;
- [ ] dashboard operacional de ativos;
- [ ] visão executiva;
- [ ] consolidar Movidesk e Asana;
- [ ] impedir escrita operacional pelos dashboards.

---

## 3. BI / Dados

### Existente / validado

- [x] ETL Python;
- [x] leitura das fontes SQLite;
- [x] normalização de patrimônio;
- [x] dimensões básicas;
- [x] fato de movimentações;
- [x] snapshot de ativos;
- [x] carga PostgreSQL;
- [x] estrutura preparada para Power BI;
- [x] separação física do ETL em bi/.

### Próximos

- [ ] incluir assistências no modelo analítico;
- [ ] incluir custos e histórico de reparos;
- [ ] estruturar camada RAW/STAGING;
- [ ] integrar Movidesk;
- [ ] integrar Asana;
- [ ] criar validações de qualidade;
- [ ] tornar cargas incrementais;
- [ ] automatizar atualização;
- [ ] consolidar modelo Gold;
- [ ] finalizar modelo semântico e medidas no Power BI.

---

## 4. Arquitetura e segurança

- [ ] remover qualquer credencial fixa do app.py;
- [ ] centralizar configurações;
- [ ] centralizar conexões;
- [ ] reduzir CSS duplicado;
- [ ] criar testes automatizados permanentes;
- [ ] documentar contratos entre Gestão, Dashboards e BI.

---

## Ordem recomendada

**Agora:** organização e navegação da Gestão.

**Depois:** Central de Dashboards.

**Depois:** evolução do ETL/BI com Assistências + Movidesk + Asana.

**Por fim:** automação, Power BI executivo e rotina de atualização.

A regra é evoluir por etapas, preservando os fluxos já testados.
