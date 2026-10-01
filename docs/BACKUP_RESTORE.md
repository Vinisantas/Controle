# Backup e recuperação de bancos

## Objetivo

Proteger os dados operacionais do Controle de Ativos TI e o modelo analítico
PostgreSQL. O backup deve ser validado e a restauração precisa ser testada.

## O que o script salva

- Todos os arquivos `.sqlite`, `.sqlite3` e `.db` de `Banco Dados/`.
- O banco PostgreSQL `controle_bi`, via `pg_dump` executado no container
  `meu-postgres`.
- Um `manifest.json` com horário, tamanho, SHA-256 e resultado de integridade
  de cada arquivo SQLite.

Cada execução cria uma pasta em `backups/AAAA-MM-DD_HH-MM-SS/`.
O backup só é marcado como concluído se todas as cópias SQLite passarem em
`PRAGMA integrity_check` e o `pg_dump` terminar com sucesso.

## Primeiro backup manual

Execute no host Linux, não dentro do container:

```bash
cd "$HOME/Área de trabalho/Controle"
python3 ferramentas/backup_bancos.py
```

O comando precisa terminar com código de saída zero e mostrar
`BACKUP_SUCCESS`. Confira o manifesto e os arquivos criados:

```bash
find backups -maxdepth 2 -type f -printf '%p (%s bytes)\n'
cat backups/*/manifest.json
```

Se aparecer `BACKUP_FAILED`, não agende a rotina ainda. Leia o erro; o
diretório com `FAILED.json` é preservado para diagnóstico.

## Agendamento diário

Só configure depois de executar e conferir o primeiro backup manual. Abra o
crontab do usuário Linux que administra o projeto:

```bash
crontab -e
```

Adicione uma linha (ajuste o caminho se o projeto estiver em outro local):

```cron
30 2 * * * cd "$HOME/Área de trabalho/Controle" && /usr/bin/python3 ferramentas/backup_bancos.py >> "$HOME/backup-controle.log" 2>&1
```

Isso agenda a rotina diariamente às 02:30. O script mantém 14 dias de backups
concluídos e só remove pastas antigas com `manifest.json` de sucesso. Backups
incompletos não são apagados automaticamente.

Confira a execução e o espaço disponível:

```bash
tail -n 80 "$HOME/backup-controle.log"
df -h "$HOME/Área de trabalho/Controle"
```

## Teste de restauração

Um backup só é confiável quando sabemos restaurá-lo. Faça o teste em uma pasta
separada ou ambiente de teste, nunca sobre os bancos usados pela aplicação.

- SQLite: restaure um arquivo para outro nome/local e confira com
  `sqlite3 arquivo_teste.sqlite 'PRAGMA integrity_check;'`.
- PostgreSQL: liste o conteúdo do dump com
  `docker exec -i meu-postgres pg_restore --list < caminho/controle_bi.dump`.
- Para uma restauração real do PostgreSQL, crie um banco de teste vazio e use
  `pg_restore` apontando para esse banco. Não restaure sobre `controle_bi`
  sem plano de recuperação e autorização explícita.

## Limite importante

A pasta `backups/` fica no mesmo disco do projeto. Isso protege contra exclusão
acidental e alguns problemas lógicos, mas não contra falha ou perda do disco,
roubo ou incidente que afete a máquina inteira. Copie backups concluídos para
outro disco ou armazenamento remoto com acesso restrito. Não envie bancos
operacionais para o GitHub.

O script não substitui monitoramento: confira regularmente o log, o espaço em
disco e faça testes de restauração periódicos.
