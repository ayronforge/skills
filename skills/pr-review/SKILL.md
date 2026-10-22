---
name: pr-review
description: Criteria for reviewing a pull request and for addressing review comments in any repository. Use whenever the task is to review a PR, branch or diff, to triage or answer review comments (human or bot, including Claude Code Review, Copilot, CodeRabbit), to fix findings raised on a PR, or to decide whether a reported issue deserves a change at all — even if the user just pastes a comment or a PR link and says "resolve isso" or "dá uma olhada".
---

# Revisão de PR

Uma revisão existe para impedir que um cliente real tenha um problema real. Tudo o que não serve a isso
custa tempo de quem revisa, de quem implementa e de quem lê o código depois. Por isso a régua é alta:
poucos apontamentos, todos com consequência, e cada correção ataca a causa.

A mesma régua vale nos dois papéis:

- **Revisando:** só aponte o que passa pela triagem abaixo.
- **Atendendo comentários:** passe cada comentário pela mesma triagem antes de mudar código. Comentário
  não é ordem; é uma alegação a verificar.

## Triagem: todo apontamento precisa de um caso de uso real

Antes de apontar ou corrigir, escreva para si mesmo, em uma frase, o caminho concreto:

> Um cliente que faz **X** (ação real do produto: se cadastrar, pagar, publicar, importar dados, chamar
> a API…) chega em **Y** (estado ou entrada que ele de fato produz) e vê **Z** (erro, dado errado,
> cobrança errada, vazamento, serviço fora do ar).

Se não dá para escrever essa frase com X e Y plausíveis, não há apontamento. "Pode acontecer se…",
"em tese…" e "por segurança…" sem um X real não contam.

Depois pese o custo: o código que a correção adiciona contra o que ela evita. Correção grande para dano
pequeno ou raríssimo fica de fora.

## O que fica de fora

- **Nitpicks.** Nome, ordem de imports, estilo, preferência pessoal, "poderia ser mais idiomático". Lint
  e formatter já cuidam do que importa aqui; o resto é gosto.
- **Overengineering.** Abstração para um caso só, parâmetro configurável que ninguém configura, camada
  "para quando precisar", generalização especulativa.
- **Programação defensiva.** `try/catch` que engole erro, checagem de `null` para valor que o tipo ou o
  schema de validação já garantem, fallback para estado que o sistema não produz, validação repetida da
  mesma entrada em camadas internas. Dado validado na fronteira é confiável dentro dela.
- **Cenários improváveis.** Corrida que exige timing que o produto não gera, entrada que nenhum
  cliente ou integração envia, falha simultânea de vários sistemas, volume ordens de grandeza acima do
  real.
- **Gambiarras.** Flag para pular um caso, `if` especial para o input que quebrou, retry para esconder
  erro determinístico, `as`/`!` para calar o TypeScript, sleep, cópia de lógica em vez de corrigir a
  origem.

Fora da régua não é o mesmo que proibido: se o autor quer, ele faz. A revisão só não pede.

## O que entra

Problemas que um cliente sente ou que quebram uma garantia do sistema:

- segurança e autorização; isolamento entre usuários, contas ou tenants;
- cobrança, quotas e planos;
- perda ou corrupção de dados;
- deploy, infraestrutura e integrações externas;
- fluxo central do produto quebrado ou regressão de comportamento;
- violação com consequência de uma regra do projeto (`CLAUDE.md`, `AGENTS.md`, guia de contribuição,
  ADR), por exemplo estado global compartilhado entre requisições ou texto de usuário indo para um modelo
  sem proteção contra prompt injection.

## Corrigir a invariante, não o sintoma

Quando um problema é real, a pergunta é: **qual garantia deveria tornar esse estado impossível, e por que
ela não vale?** Corrija ali.

- Estado inválido aparece → torne-o irrepresentável (tipo, schema de validação, constraint no
  banco) ou impeça na fronteira que o cria, em vez de checar em cada leitor.
- Dois lugares divergem → uma fonte de verdade, não sincronização.
- Ordem de operações quebra algo → transação, idempotência ou a ordem certa, não retry.
- Erro aparece → trate onde há decisão a tomar; não capture para "não quebrar".

Sinal de remendo: a correção só faz sentido para o input do bug, adiciona um caso especial, ou o próximo
bug parecido exigiria outro remendo igual. Se for assim, suba até a causa. Se a causa estiver fora do
escopo do PR, diga isso e proponha o caminho em vez de remendar.

## Revisando um PR

1. Entenda a intenção do PR (descrição, issue, commits) e o fluxo de cliente que ele toca.
2. Leia o diff com o código ao redor; um bug costuma estar no que o diff assume sobre quem o chama.
3. Para cada suspeita, faça a triagem. Confirme lendo o caminho real (chamadores, schema, constraint),
   não pela aparência da linha.
4. Reporte só o que sobreviveu, do mais grave ao menos grave. Para cada um:
   - o cenário de cliente (a frase X → Y → Z);
   - a causa, apontando a invariante que falta;
   - a correção na causa, em poucas linhas.
5. Se nada sobreviveu, diga que o PR está bom. Revisão sem apontamentos é um resultado válido; não
   invente achados para parecer rigorosa.

## Atendendo comentários de revisão

Para cada comentário:

1. Faça a triagem. Leia o código para confirmar se o cenário existe, mesmo que o comentário pareça
   óbvio ou venha com severidade alta.
2. Decida e aja:
   - **Real e no escopo** → corrija na causa. Uma correção pode resolver vários comentários; nesse caso
     responda cada um apontando para ela.
   - **Real, mas fora do escopo ou grande** → responda com a proposta e deixe a decisão com o autor.
   - **Não passa na triagem** → não mude código. Responda curto e com o motivo concreto.
3. Nunca implemente a versão defensiva só para encerrar a thread. Uma resposta clara custa menos que
   código que ninguém precisa.

Respostas de recusa são uma ou duas frases, sem tom de desculpa, com o fato que decide:

- "`userId` vem do schema da rota, que já exige UUID; esse estado não chega aqui."
- "Só o cron chama isso, uma vez por minuto; não há concorrência entre execuções."
- "Correção exigiria X para um caso que nenhum cliente produz; fica como está."

## Testes

A mesma régua vale para testes. Peça teste de regressão só para bug sério e plausível, e que ele
verifique comportamento por uma fronteira estável (requisição, comando, API pública), não detalhe de
implementação. Num PR que mexe em testes, teste que não pegaria um bug sério é apontamento: sai.
