# Relatório de teste de segurança — 2026-09-29

**Projeto:** Controle de Ativos TI - Copia  
**Escopo:** verificações estáticas, configuração local e teste de restauração isolada.  
**Segurança operacional:** nenhum banco original foi alterado; nenhum valor de credencial foi exibido.

## Resultado

- **37 verificações PASS**
- **0 verificações FAIL**
- **1 alerta de melhoria**
- O resultado não equivale a um teste de invasão (pentest) nem comprova segurança para exposição pública.

## Verificações executadas

- Manifesto contém os 8 bancos esperados.
- SHA-256 dos 8 arquivos de backup confere com o manifesto.
- Os 8 bancos foram copiados para uma pasta temporária de recuperação, separados dos bancos do projeto.
- SHA-256 das 8 cópias restauradas confere.
- `PRAGMA integrity_check` retornou `ok` nos 8 bancos.
- A pasta temporária de restauração foi removida após os testes.
- Git ignora `.env`, `backups/`, `*.sqlite-wal` e `*.sqlite-shm`.
- `.env` não está versionado; as variáveis `APP_USUARIO` e `APP_SENHA` existem e não estão vazias. Os valores não foram lidos para saída nem registrados.
- O fluxo do app condiciona a interface principal ao estado autenticado.
- `requirements.txt` não contém caractere de substituição e declara `python-dotenv==1.0.1`.

## Alerta e riscos residuais

1. **Tentativas de login:** não foi identificada limitação explícita de tentativas, atraso progressivo ou bloqueio temporário no módulo de autenticação. Recomenda-se adicionar proteção contra força bruta se o sistema for usado por outras pessoas ou em rede.
2. **Permissões:** a autenticação atual usa um usuário e senha compartilhados por configuração; não foi identificada autorização por perfil/ação. Defina quem pode registrar saídas, retornos, alterar assistências e importar dados.
3. **Rede e transporte:** esta verificação não confirmou as regras de firewall, o endereço de escuta real nem a presença de HTTPS/TLS. Não exponha o Streamlit diretamente à internet; restrinja-o à máquina/rede autorizada e use acesso seguro se houver acesso remoto.
4. **Credenciais:** foi verificado apenas que as variáveis existem e não estão vazias. A força da senha não foi avaliada e o valor não foi exibido.
5. **HTML/CSS:** o app usa `unsafe_allow_html=True) para estilos e marcação visual. Não injete conteúdo não confiável nessas chamadas; mantenha os textos HTML estáticos ou devidamente sanitizados.

## Conclusão

O backup passou no teste de integridade e restauração isolada, e as regras básicas para não versionar credenciais e backups passaram. O candidato pode seguir para **uso controlado e supervisionado**, condicionado à confirmação das restrições de rede e das permissões operacionais. Não considerar aprovado para exposição pública até tratar ou aceitar formalmente os riscos residuais.

## Limites

Não foram realizados testes de invasão, varredura de dependências/CVEs, avaliação de firewall, teste de HTTPS, revisão completa de autorização por função ou validação da força da senha. Nenhum banco real foi modificado.
