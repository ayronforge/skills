# Prints de antes e depois

Os scripts ficam em `scripts/`, ao lado do `SKILL.md`. Rode-os a partir da raiz do projeto.

- `shots.mjs` precisa de `playwright` ou `@playwright/test` instalado no projeto.
- `compare.py` precisa do Pillow. Se `python3 -c "import PIL"` falhar, rode `pip install pillow`.

Use uma pasta temporária fora do repositório, com `antes/` e `depois/`. Cada print tem o mesmo nome nos
dois lados; é pelo nome que o comparador junta os pares.

## 1. Antes

Fotografe o código atual, antes de editar: depois da mudança não há como recuperar a tela antiga. Se já
editou, rode `git stash`, fotografe e rode `git stash pop`.

Suba o servidor de desenvolvimento e descreva os prints num JSON, partindo de
`scripts/shots.example.json`:

```json
{
  "baseUrl": "http://localhost:3000",
  "colorScheme": "dark",
  "hide": ["[data-cookie-banner]"],
  "unstick": true,
  "shots": [
    { "name": "home-topo", "path": "/", "target": "top" },
    { "name": "home-planos", "path": "/", "target": "section[aria-labelledby=planos]" },
    { "name": "conta", "path": "/conta", "target": "full" }
  ]
}
```

Depois rode:

```sh
node <skill>/scripts/shots.mjs shots.json <pasta>/antes
```

### Campos do JSON

| Campo | Para que serve |
| --- | --- |
| `target` | `top` fotografa a primeira tela; `full`, a página inteira; um seletor CSS, só aquele trecho. |
| `hide` | Esconde o que cobre o conteúdo: banner de cookies, barra de ferramentas de dev, widget de chat. |
| `unstick` | Solta header e barras fixas, que senão aparecem por cima do recorte. |
| `css` | CSS extra, por exemplo para revelar elementos que só aparecem ao rolar. |
| `localStorage` | Chaves gravadas antes de cada página: tema salvo, consentimento já aceito. |
| `storageState` | Sessão salva, para telas com login (abaixo). |
| `viewport`, `locale`, `blockThirdParty`, `settleMs` | Ajustes opcionais, com padrões no exemplo. |

Para o seletor, use um que sobreviva à mudança, como `section[aria-labelledby=...]` ou um `id`. Classes
de estilo mudam, e o print do depois falharia.

Se a página tem modo claro e escuro e a mudança mexe em cor, fotografe os dois, com dois JSONs.

O script rola a página para carregar o conteúdo preguiçoso, espera as fontes e zera as animações. Por
isso o print não mostra movimento: quando a mudança é numa animação, descreva o antes e o depois na frase
do par.

### Variáveis de ambiente

| Variável | Quando usar |
| --- | --- |
| `SHOTS_CHROMIUM` | A versão do Playwright não acha o navegador sozinha. Aponte para um Chromium já instalado. |
| `PLAYWRIGHT_MODULE` | O Playwright não está na raiz do projeto. Aponte para o pacote. |

## Telas que pedem login ou dados

- **Com login:**
  1. Gere um `storageState` com o login do próprio projeto: um passo do setup de e2e, um script com
     `context.storageState({ path })` ou `npx playwright codegen --save-storage=auth.json <url>`.
  2. Ponha o caminho em `"storageState"`.
  3. Não commite esse arquivo: ele carrega a sessão.
- **Com dados** (contas, planos, registros): use o harness de e2e do projeto, que já sabe montar esses
  cenários.
  1. Escreva uma spec temporária com os fixtures existentes.
  2. Salve os prints com `page.screenshot({ path })` ou `locator.screenshot({ path })`.
  3. Rode só essa spec e apague-a antes do commit.
- **Build do antes:** se o harness compila o app, recompile entre o antes e o depois. Um build
  reaproveitado fotografa o código velho dos dois lados.
- **Tela fora de alcance:** quando ela depende de serviço externo ou de um processo que não termina no
  ambiente de teste, deixe sem print e diga isso na entrega.

## 2. Depois

Aplique a mudança e rode os mesmos comandos com `<pasta>/depois`. O servidor de desenvolvimento recarrega
sozinho; o harness de e2e precisa recompilar.

## 3. Comparar

```sh
python3 -I <skill>/scripts/compare.py diff <pasta>
```

Cada par sai marcado como `IGUAL`, `MUDOU`, `TAMANHO` ou `SÓ-UM-LADO`.

- Deixe os pares `IGUAL` fora da página.
- Deixe fora também diferenças pequenas onde nada deveria mudar, como pulso de animação, cursor ou
  relógio.
- Um `MUDOU` numa tela que você não queria tocar é sinal de que algo vazou. Investigue.
- Abra alguns prints do depois e olhe com atenção: é ali que aparecem a margem órfã e o alinhamento
  quebrado.

## 4. Página de comparação

Escreva um `pares.json`:

```json
{
  "title": "Menos texto, antes e depois",
  "intro": "Cada par mostra a mesma tela antes e depois. Clique num print para abrir em tamanho real.",
  "missing": "Sem print: a etapa de pagamento, que depende do provedor externo.",
  "groups": { "site": "Site", "app": "Aplicativo" },
  "items": [
    { "group": "app", "name": "conta", "title": "Conta", "note": "Sai a descrição do cabeçalho, que listava as seções da página." }
  ]
}
```

O `note` diz em uma frase o que saiu ou entrou, com o texto entre aspas quando for o caso. É lendo essas
frases que o usuário decide o que volta, então seja preciso.

Depois rode:

```sh
python3 -I <skill>/scripts/compare.py build <pasta> pares.json
```

Isso gera `<pasta>/pagina/index.html`, com as imagens ao lado (em WebP, ou PNG quando passam de 16.383 px).

- **Mostrar:** passe ao usuário o caminho do `index.html` ou abra a página pela ferramenta do ambiente que
  mostra arquivos locais. Espere a avaliação antes do commit.
- **Corte devolvido:** desfaça no código, refaça só os prints daquele par, ajuste o `note` e gere a
  página de novo.
