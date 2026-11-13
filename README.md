# mAInd

Chatbot de acolhimento para pessoas passando por ansiedade, depressão, estresse e outros sofrimentos. Conversa como um amigo, ajuda a pessoa a entender o que sente e mostra caminhos de apoio. **Não faz diagnóstico e não substitui um profissional.** Em emergência: CVV 188 · SAMU 192.

Projeto da disciplina C318 (Fundamentos de Machine Learning, Inatel).

## Como ligar

Precisa de Python 3.11 ou mais novo.

```bash
python -m venv .venv
.venv\Scripts\activate             # Windows
# source .venv/bin/activate        # Linux / Mac
pip install -r requirements.txt
copy .env.example .env             # Linux / Mac: cp .env.example .env  (depois preencha as chaves)

python -m servidor
```

Abra **http://127.0.0.1:8000**. O mesmo comando liga a API e o site. A documentação das rotas fica em http://127.0.0.1:8000/api/docs.

Para rodar os testes: `python -m pytest`.

## Como funciona

Cada mensagem passa por 5 etapas, nesta ordem:

```
 mensagem ─► 1. SEGURANÇA ─► 2. ENTENDIMENTO ─► 3. CONHECIMENTO ─► 4. CONVERSA ─► 5. REVISÃO ─► site
             crise? resposta   tema e intenção    trechos da         a IA escreve    frase a frase,
             fixa na hora                         biblioteca                         antes de aparecer
```

Cada etapa é uma parte separada, num arquivo em `servidor/partes/`. Enquanto a versão real não chega, cada parte tem uma versão provisória, e o site avisa quais ainda são provisórias. O que cada parte recebe e devolve está em [`CONTRATOS.md`](CONTRATOS.md).

## Pastas

```
servidor/            API (FastAPI), memória da conversa e junção das partes
  partes/            uma parte por arquivo: seguranca, tema, intencao,
                     conhecimento, ia
  contratos.py       formatos que cada parte recebe e devolve
  pipeline.py        ordem das etapas, tratamento de falhas, revisão frase a frase
  memoria.py         conversas em SQLite (dados/conversas.db), apagáveis pelo usuário
  textos.py          textos fixos (resposta de crise e de reserva), nunca gerados pela IA
frontend/            o site (HTML/CSS/JS puros)                                  · ver frontend/README.md
experimento/         experimento comparativo das 3 versões                       · ver experimento/README.md
testes/              testes automáticos da plataforma
dados/               banco de conversas local (não vai para o GitHub)
legado/              bot antigo (questionário de 24 perguntas), guardado para a comparação
```

O treino dos modelos (notebooks, dados, modelos salvos) fica fora de `servidor/`, por exemplo em `modelos/<parte>/` e `notebooks/`. O arquivo em `servidor/partes/` só carrega o modelo e responde.

## Configuração

Tudo pelo arquivo `.env` (modelo em [`.env.example`](.env.example)). O `.env` guarda chaves de acesso e **nunca vai para o GitHub**. Os principais itens:

| Variável | Para quê |
|---|---|
| `MAIND_PERFIL` | quais partes ficam ligadas: `completo`, `so_ia`, `ia_tema`, `ia_tema_conhecimento` |
| `MAIND_PARTE_<NOME>` | liga ou desliga uma parte específica (`1`/`0`) |
| `MAIND_LIMIAR` | confiança mínima para o bot seguir com o tema |
| `MAIND_GUARDAR_CONVERSAS` | `0` para não gravar nada em disco |
| `MAIND_IA_CHAVE` | chave da IA que escreve as respostas |

## Privacidade

As conversas ficam só no computador onde o servidor roda (`dados/conversas.db`), e o botão "Apagar conversa" do chat as remove. Com `MAIND_GUARDAR_CONVERSAS=0`, nada é gravado.
