# mAInd · Frontend

Interface do mAInd em HTML, CSS e JavaScript puros (sem build). Segue o design system de `../skill_front.md`.

## Como abrir

O jeito normal é ligar o servidor na raiz do repositório (`python -m servidor`) e abrir `http://127.0.0.1:8000`: o próprio servidor entrega o site.

Também dá para abrir `index.html` direto do disco ou por outro servidor estático. Nesse caso o site procura a API em `http://127.0.0.1:8000` (configurável em `assets/js/config.js`).

Sem servidor, o chat entra em **modo demonstração**: um classificador simples de palavras-chave roda no navegador só para a interface poder ser mostrada. A tela avisa quando isso acontece. Com o servidor ligado mas com partes ainda provisórias, a tela também avisa.

## Páginas

| Arquivo | Conteúdo |
|---|---|
| `index.html` | Apresentação, como funciona, temas, fluxo do projeto e faixa do CVV |
| `chat.html` | Conversa + painel "Análise do modelo" (tema, probabilidades, limiar, decisão, etapas com tempo de cada uma) |
| `tema.html?t=<id>` | Página de conteúdo de um tema: `ansiedade`, `depressao`, `estresse`, `bipolaridade`, `personalidade`, `solidao` |

## Estrutura

```
assets/
  css/tokens.css   tokens do design system (cores, tipografia, raios, sombras; tema claro derivado)
  css/app.css      base, componentes e seções da página inicial
  css/chat.css     layout do chat e painel de análise
  js/config.js     URL da API
  js/common.js     cabeçalho, rodapé, tema claro/escuro, ícones, barras de probabilidade
  js/temas.js      conteúdo dos 6 temas
  js/api.js        cliente da API (resposta aos poucos) + modo demonstração
  js/chat.js       lógica da conversa e do painel
  img/             logo
```

## Contrato da API

O servidor fica em `../servidor/`. A documentação interativa das rotas abre em `http://127.0.0.1:8000/api/docs`.

```
GET  /api/saude
  -> { "status": "ok", "perfil": "completo",
       "modelo": { "limiar_confianca": 0.5, "tema": "...", "provisorio": true },
       "partes": { "<etapa>": { "ligada", "provisoria", "responsavel", "descricao" }, ... },
       "guarda_conversas": true }

POST /api/mensagem/stream   { "texto": "...", "sessao_id": "opcional" }      (usada pelo site)
  -> text/event-stream, nesta ordem:
     event: analise     { sessao_id, acao, tema, confianca, limiar, probabilidades, intencao, trechos, perfil }
     event: texto       "pedaço da resposta, já revisado"         (vários)
     event: substituir  "texto que troca tudo o que já apareceu"  (só se a revisão barrar ou a IA falhar)
     event: fim         { resposta, revisao: { permitida, motivo }, latencia_ms, etapas: [...] }
     event: erro        { erro }                                  (falha inesperada no servidor)

POST /api/mensagem          { "texto": "...", "sessao_id": "opcional" }
  -> a mesma informação, inteira, num JSON só (analise + fim):
     {
       "sessao_id": "...",
       "resposta": "texto do mAInd",
       "acao": "encaminhar" | "pedir_detalhes" | "crise" | "conversa",
       "tema": { "id": "ansiedade", "nome": "Ansiedade" } | null,
       "confianca": 0.82,
       "limiar": 0.5,
       "probabilidades": [ { "id": "estresse", "nome": "Estresse", "p": 0.07 }, ... ],
       "intencao": { "id": "desabafar", "nome": "Desabafar", "confianca": 0.9 } | null,
       "trechos": [ { "titulo": "...", "fonte_url": "https://...", "tema": "ansiedade" } ],
       "revisao": { "permitida": true, "motivo": "" },
       "latencia_ms": 35,
       "etapas": [ { "id", "nome", "responsavel", "descricao", "provisoria", "status", "ms", "detalhe" } ]
     }

GET    /api/sessao/{sessao_id}   -> { sessao_id, mensagens: [ { papel, texto } ] }
DELETE /api/sessao/{sessao_id}   -> { apagada: true | false }
```

Erros sempre voltam como `{ "erro": "mensagem em linguagem simples" }`.

Significado de `acao`:

| acao | Quando | O que o site mostra |
|---|---|---|
| `encaminhar` | tema com confiança acima do limiar | cartão do tema + fontes |
| `pedir_detalhes` | confiança abaixo do limiar | etiqueta "confiança baixa" |
| `conversa` | cumprimento, agradecimento, fora do tema, ou perfil sem modelo de tema | só a resposta |
| `crise` | segurança detectou sinal de crise | resposta fixa + botão para ligar 188 |
