# Design e UX — TI Controle

## Direção visual

- corporativo;
- grafite e cinza;
- vermelho discreto para ações e estados importantes;
- contraste suficiente para leitura;
- tabelas neutras e densas;
- poucos efeitos decorativos.

## Hierarquia

O usuário deve perceber rapidamente:

1. onde está;
2. qual ação pode executar;
3. quais informações são importantes;
4. se existe algum alerta.

## Navegação

Organizar a sidebar por contexto:

~~~text
OPERAÇÃO
  Consultar patrimônio
  Registrar saída
  Registrar retorno

ACOMPANHAMENTO
  Histórico
  Estoque
  Suporte

ANÁLISE
  Indicadores
  Relatórios

FERRAMENTAS
  Assistente TI
~~~

## Formulários

Preferir formulários em etapas visuais:

Equipamento → Movimento → Destino → Responsável → Confirmação.

Campos específicos devem aparecer somente quando forem necessários.

## Tabelas

Mostrar primeiro as colunas usadas para decisão. Detalhes secundários devem ficar depois ou em uma ação de consulta.

## CSS

Evitar CSS diferente para cada tela. O config.toml deve definir a base visual e CSS adicional deve ser pequeno e reutilizável.
