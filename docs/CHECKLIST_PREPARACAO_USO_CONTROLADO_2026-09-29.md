# Checklist final — preparação para uso controlado

**Data:** 2026-09-29  
**Projeto:** `Controle Ativos TI - Copia`  
**Decisão:** candidato funcional; uso controlado condicionado aos itens pendentes abaixo.

## Verificações concluídas

- [x] Regressão anterior: 12/12 telas PASS.
- [x] Fluxos de dados: 18/18 PASS em bancos temporários.
- [x] Inicialização do Streamlit: health check `200 / ok` em cópia isolada.
- [x] Backup de 8 bancos SQLite com hashes SHA-256 conferidos.
- [x] `.env` está listado nas regras de exclusão do Git.
- [x] Autenticação usa `APP_USUARIO` e `APP_SENHA` do ambiente, sem credencial fixa no fluxo de login.
- [x] Corrigida a última linha inválida/ilegível de `requirements.txt`; incluído `python-dotenv==1.0.1`, usado por `app.py`.
- [x] Adicionada exclusão de `backups/` e arquivos SQLite temporários de WAL/SHM ao `.gitignore`.
- [x] README atualizado para descrever a configuração de autenticação atual.

## Itens que ainda exigem confirmação do responsável

- [ ] Confirmar que `.env` contém usuário e senha fortes, sem exibir ou enviar esses valores.
- [ ] Confirmar que o sistema só está acessível a pessoas autorizadas e, se for uso em rede, restringir firewall/rede e não expor diretamente à internet.
- [ ] Definir quem pode registrar saídas, retornos, excluir/editar assistências e importar dados do Senior.
- [ ] Testar a restauração do backup em uma pasta de recuperação separada antes de qualquer incidente real.
- [ ] Fazer uma validação assistida com o responsável operacional antes de substituir qualquer rotina atual.
- [ ] Se houver dados pessoais ou de colaboradores nos bancos, confirmar acesso mínimo necessário e política interna de retenção.

## Procedimento de recuperação — não sobrescrever os bancos atuais diretamente

1. Interrompa o Streamlit antes de recuperar arquivos, para evitar gravações simultâneas.
2. Copie a pasta `backups/2026-09-29_candidato/` para uma pasta de recuperação separada.
3. Confira o `MANIFESTO_SHA256.txt` e valide os hashes das cópias recuperadas.
4. Abra a recuperação em uma cópia separada do projeto e confira cadastro, históricos e assistências.
5. Só após aprovação do responsável, planeje a troca dos bancos com backup adicional do estado imediatamente anterior.
6. Nunca restaure o banco de teste sobre o projeto oficial nem misture snapshots do Senior com o histórico operacional.

## Correções desta revisão

- `requirements.txt`: removida uma linha corrompida e substituída pela dependência `python-dotenv==1.0.1`.
- `.gitignore`: adicionadas exclusões para backups locais e arquivos SQLite WAL/SHM.
- `README.md`: documentação da autenticação alinhada ao código atual.

Nenhum banco de dados foi alterado nesta revisão. Nenhum valor de `.env` foi exibido ou incluído nos relatórios.
