# mAInd · Frontend

Interface do mAInd em HTML, CSS e JavaScript puros (sem build). Segue o design system de `../skill_front.md`.

## Como abrir

Abra `index.html` no navegador (funciona direto do disco). Para o chat usar o modelo treinado, deixe o backend rodando em `http://127.0.0.1:5000` (configurável em `assets/js/config.js`).

Sem backend, o chat entra em **modo demonstração**: um classificador simples de palavras-chave roda no navegador só para a interface poder ser mostrada. A tela avisa quando isso acontece.

## Páginas

| Arquivo | Conteúdo |
|---|---|
| `index.html` | Apresentação, como funciona, temas, pipeline de ML (diagrama da C318) e faixa do CVV |
| `chat.html` | Conversa + painel "Análise do modelo" (probabilidade por tema, limiar de confiança, decisão, pipeline) |
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
  js/api.js        cliente da API + modo demonstração
  js/chat.js       lógica da conversa e do painel
  img/             logo
```

## Contrato da API

```
GET  /api/saude
  -> { "status": "ok", "modelo": { "encoder": "...", "classificador": "...", "limiar_confianca": 0.5 } }

POST /api/mensagem   { "texto": "...", "sessao_id": "opcional" }
  -> {
       "sessao_id": "...",
       "resposta": "texto do mAInd",
       "acao": "encaminhar" | "pedir_detalhes" | "crise",
       "tema": { "id": "ansiedade", "nome": "Ansiedade" } | null,
       "confianca": 0.82,
       "limiar": 0.5,
       "probabilidades": [ { "id": "estresse", "nome": "Estresse", "p": 0.07 }, ... ],
       "latencia_ms": 35
     }
```
