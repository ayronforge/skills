---
name: declutter-ui
description: Corta o texto, os enfeites e as animações que sobram numa interface, reescreve o que fica para quem usa o produto e mostra a mudança em prints de antes e depois. Use sempre que pedirem para enxugar, limpar, revisar ou auditar uma tela, o texto ou o movimento dela ("menos é mais", "tem texto demais", "eyebrow", "parece documentação", "parece feito por IA", "animação demais"), ao criar ou revisar uma tela antes de entregar, e quando uma mudança visual precisar de prints de antes e depois, mesmo que ninguém fale em "copy".
---

# Menos texto na UI

A tela conversa com quem usa o produto. Cada palavra serve a essa pessoa naquele momento: mostra onde ela
está, ajuda a decidir ou diz o que acontece quando ela age. Texto que explica a tela para quem a
construiu, para um revisor ou para o modelo que vai editá-la depois é documentação, e documentação não
mora na interface.

Acrescentar é fácil, sobretudo com um agente; tirar exige entender como as pessoas usam a tela, com que
frequência e para decidir o quê. Uma UI de alta qualidade se reconhece pelo que não tem: o título basta,
os rótulos são específicos, a hierarquia vem do tamanho, do peso e do espaço. Esse julgamento vale ao
criar uma tela, não só ao limpar depois. A base é o texto
[Less is more, more or less](https://jakub.kr/writing/less-is-more), de Jakub Krehel.

## O teste

Para cada texto, rótulo, ícone, enfeite ou animação, existente ou que você está prestes a criar:
**se isto sumir, a pessoa perde algo de que precisa para entender, decidir ou agir?**

- **Não perde:** apague, ou não crie.
- **Perde, mas está no lugar errado:** mova para onde a decisão acontece: o rótulo do botão, o lado do
  campo, a mensagem de erro, a confirmação.
- **Perde e está no lugar certo:** mantenha e encurte.

## Sinais de texto escrito para o modelo

| Sinal | Antes | Depois |
| --- | --- | --- |
| Descrição que lista o que vem abaixo | "Conta" + "Seu plano, seu uso e a segurança do seu acesso." | "Conta" |
| Descrição que repete o título | "Segurança" + "Proteja o acesso à sua conta." | "Segurança" |
| Eyebrow ou selo acima do título | "COMPARAÇÃO" acima de "A vs B"; "Erro 404" acima de "Essa página não existe" | Só o título |
| Narração do layout | "Assista ao vídeo ou siga os três passos abaixo." | Nada: a tela já mostra |
| Instrução óbvia | "Clique no nome para ver os detalhes." | Nada: o link parece link |
| Detalhe de implementação | "Quem declara é o arquivo de configuração do repositório." | "Peça ao assistente para adicionar." |
| Título que repete o botão | Card "Criar com este modelo" com botão "Criar com este modelo" | Só o botão |
| Estado vazio com parágrafo | Três frases explicando o recurso | Uma frase com o próximo passo, e o botão |
| Numeração que não é sequência | "01", "02", "03" em cards que não se leem em ordem | Sem número |
| Nome repetido | O nome da seção na navegação, no título e num rótulo acima dele | Uma vez |
| Enfeite como pontuação | Sparkle em tudo que tem IA, ícone em quadrado repetindo o título, glow, mono em texto comum | Sem enfeite |
| Animação em ação frequente | Menu que desliza 300 ms a cada abertura, transição no hover de cada linha | Abre na hora, hover sem transição |

## O que fica

- **Informação que só está ali:** preço, prazo, limite, plano necessário, consequência ("não dá para
  desfazer") e aviso de segurança ("o valor não aparece depois de salvo").
- **Como ler um número:** "cada quadrado é 1% das visitas", "média dos últimos 7 dias".
- **Termo que o público não conhece:** explique, ou melhor, troque por uma palavra comum.
- **Copy que argumenta numa página de venda:** benefício, objeção respondida, prova. Ali, corte só a
  repetição.
- **Identidade visual de que o dono do produto gosta:** ilustração, padrão de fundo, ícones de um guia.
  Nem toda decoração é sobra, e quem decide é ele.
- **Rótulos funcionais em caixa alta:** cabeçalho de tabela, coluna de rodapé, título de menu.

## Como escrever o que fica

- Seja específico: "Pagamento único, no cartão ou no Pix", não "Opções flexíveis de pagamento".
- Use o nome que a pessoa reconhece: ela gerencia avisos, não webhooks.
- Rotule a ação pelo que acontece ("Publicar") e confirme com o resultado ("Publicado").
- No erro, diga o que aconteceu e como resolver, sem pedir desculpas.
- Escreva frases curtas, uma ideia por frase, sem travessão de efeito nem "não é X, é Y".

## Movimento

Quem decide se algo anima é a frequência de uso. Um menu aberto 200 vezes por dia com 300 ms de
animação custa mais de 6 horas por ano de espera.

- **Ação repetida o dia todo** (menu, dropdown, abas, hover em lista, toggle): sem animação, ou tão curta
  que ninguém espera por ela.
- **Mudança rara que orienta** (painel que abre, item que entra na lista): pode animar, curto, para
  mostrar de onde algo veio.
- **Animação para a tela "parecer viva":** tire.
- Respeite `prefers-reduced-motion`. Na dúvida, use a tela dez vezes seguidas; o que cansa sai.

## Como trabalhar

1. **Leia as regras do projeto:** design system, guia de voz, `CLAUDE.md`, `AGENTS.md`. Onde elas
   divergirem desta skill, valem elas, porque foram decididas por quem conhece o produto.
2. **Comece pelos componentes com slot de texto:** cabeçalho de página, seção, estado vazio, diálogo,
   card. Um conserto ali vale para todas as telas que os usam.
3. **Passe o teste em cada elemento de cada tela.** Entre duas soluções, prefira a que tem menos código e
   menos partes; uma boa mudança de UI costuma tirar mais linhas do que pôr.
4. **Procure nos testes cada texto que for apagar:** um teste pode depender dele.
5. **Limpe a sobra da remoção:** margem órfã, `justify-between` com um filho só, import, prop ou campo de
   dados sem uso.
6. **Mostre o antes e o depois ao usuário e espere a avaliação antes do commit.** Corte de copy é decisão
   de produto, e às vezes o que parece enfeite é identidade. Devolva sem discutir o que ele quiser
   manter.
7. **Valide com os checks do projeto:** typecheck, lint, formatação, testes.

## Prints de antes e depois

Os prints e a página de comparação servem para o usuário avaliar a mudança com você, localmente. Ficam
numa pasta temporária, fora do repositório e fora da PR.

1. Antes de editar, fotografe as telas afetadas com `scripts/shots.mjs` em `<pasta>/antes`.
2. Aplique a mudança e fotografe as mesmas telas em `<pasta>/depois`.
3. Rode `scripts/compare.py diff <pasta>` para ver quais pares mudaram de fato.
4. Escreva um `pares.json` com uma frase por par dizendo o que saiu ou entrou e gere a página com
   `scripts/compare.py build`.
5. Passe ao usuário o caminho do `index.html` gerado.

O passo a passo, com o formato dos JSONs, telas que pedem login ou dados e as armadilhas comuns, está em
[`references/prints.md`](references/prints.md). Leia antes de fotografar.
