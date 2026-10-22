---
name: testing
description: Regras para escrever, mudar, revisar e apagar testes automatizados em qualquer repositório. Use sempre que a tarefa criar ou editar um arquivo de teste (*.test.*, *.spec.*, test_*.py, *_test.go, suítes e2e), corrigir um bug que pode merecer teste de regressão, revisar um diff que mexe em testes, ou decidir se um comportamento precisa de teste.
---

# Testes

Poucos testes, todos valiosos. Um teste só existe se cumprir as três condições:

- pega um bug sério e plausível;
- verifica comportamento por um contrato estável;
- continua passando quando a implementação é reescrita sem mudar o comportamento.

Na dúvida, não escreva o teste. Quantidade de casos e coverage não são metas.

## Antes de começar

Leia as regras do projeto (`CLAUDE.md`, `AGENTS.md`, guia de contribuição) e alguns testes existentes:
framework, onde as suítes moram, como fakes e dados de teste são montados, como o tempo é controlado. Siga
o que o projeto já faz. Onde as regras dele divergirem desta skill, valem as dele.

## O que merece teste

Bugs com consequência séria:

- segurança e autorização (segredos, redirect aberto, escape de caminho, tokens);
- isolamento entre usuários, contas ou tenants;
- cobrança, quotas e planos;
- perda ou corrupção de dados;
- integrações que publicam, enviam ou movem algo para fora do sistema;
- fluxo central do produto quebrado.

Não merecem teste: textos e copy, analytics e observabilidade, ferramentas internas e CLIs de admin,
otimizações de desempenho e cache, UX secundária.

## O que nunca se testa

- **Implementação.** Nada de ler linhas internas do banco, contar ou ordenar chamadas a fakes, comparar
  objeto inteiro quando só um ou dois campos importam, testar helper interno ou mensagem que não é
  contrato. Se trocar a implementação sem mudar o comportamento quebra o teste, o teste está errado.
- **Bibliotecas e plataforma.** O que quem mantém a dependência já testa não se testa aqui. Se a regra é
  nossa e a biblioteca é só o meio (nossa lista de hosts permitidos, nossa normalização), a regra é
  testada.
- **Garantias de tipo.** O que o compilador, o type checker ou o schema de validação já garantem.
- **Tautologias.** Fixture e expectativa vindas da mesma fonte, constante comparada com ela mesma, fake
  devolvendo o que foi configurado para devolver.

## Onde o teste mora

Na fronteira mais externa que prova o comportamento: requisição HTTP, comando de CLI, mensagem de fila,
job agendado, chamada de API pública do pacote. De preferência com as dependências internas de produção
e um banco real (container, banco em memória do mesmo motor ou banco clonado por teste).

- Teste de função isolada só vale quando:
  - a regra é nossa, densa e com contrato estável (sanitização de path, slug, redação de segredo); ou
  - o código não tem caminho por uma fronteira (script que roda no navegador, runner isolado).
- Teste de UI no navegador (Playwright, Cypress) só para jornada de alto valor que um teste de API não
  cobre.
- Num monorepo, a dependência de teste aponta para baixo como a do código: um teste importa o próprio
  pacote e o que ele declara. Comportamento que precisa de vários pacotes compostos vai para a suíte de
  integração.

## Fakes

- Troque só sistemas externos (pagamento, e-mail, provedor de identidade, DNS, APIs de terceiros), e
  sempre pelo ponto de injeção que o código de produção já usa para encapsulá-los.
- Cada sistema externo tem um único fake, guardado junto do código que o encapsula e reaproveitado por
  todas as suítes.
- Serviços internos rodam com a implementação de produção.
- Tempo, aleatoriedade e IDs vêm de dependências injetáveis controladas pelo teste, não de sleep.
- Evite mocks por monkeypatch ou por módulo (`vi.mock`, `jest.mock`, `unittest.mock.patch`, spies). Se o
  teste só funciona assim, falta um ponto de injeção no código.

## Como escrever

- Um comportamento, um teste. Antes de escrever, procure se já existe.
- Asserte o que o usuário ou o cliente observa: status e corpo da resposta, estado lido pela API, efeito
  externo registrado no fake (cobrança, e-mail, DNS).
- Use teste por tabela só quando cada linha exercita um ramo diferente da regra.
- Escreva no estilo do código de produção do projeto, com as mesmas abstrações e convenções.
- Teste caro (build real, espera real, navegador) precisa de valor proporcional ao custo.

## Checklist

1. Que bug sério e plausível ele pega?
2. Ele continua passando se eu reescrever a implementação sem mudar o comportamento?
3. Está testando código nosso, e não uma biblioteca?
4. Já existe um teste que prova isso?
5. Ele falha se eu reintroduzir o bug? Quebre o código de propósito, rode, veja falhar e desfaça.

Se alguma resposta for ruim, não escreva. Ao mexer num arquivo de teste existente, aplique a mesma régua
e apague o que não passar.

## Como rodar

Descubra os comandos no próprio repositório: scripts do `package.json`, `Makefile`, `justfile`,
`pyproject.toml`, workflows de CI. Suba as dependências que eles pedem (por exemplo `docker compose up`)
e rode primeiro só os testes afetados, depois a suíte que o CI roda. Se o projeto tem teste de mutação,
rode-o quando mexer numa invariante crítica.
