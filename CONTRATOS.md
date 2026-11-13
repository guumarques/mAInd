# Contratos das partes

Cada parte do mAInd é um arquivo em `servidor/partes/`. Hoje todos têm uma **versão provisória** que finge funcionar, para o chat já rodar de ponta a ponta. A versão real substitui o conteúdo do arquivo **mantendo o nome da função, os parâmetros e o formato de retorno** descritos aqui. Os formatos estão definidos em código em `servidor/contratos.py`.

Na versão real, `PROVISORIO` passa a `False` e `DESCRICAO` descreve o modelo (ela aparece no painel "Análise do modelo" do site). Modelos treinados, dados e notebooks ficam fora de `servidor/` (ex.: `modelos/tema/`, `notebooks/`); o arquivo em `servidor/partes/` só carrega o modelo e responde.

O servidor e o site dependem destes formatos: mudar um contrato exige mudar os dois lados juntos.

## Ordem em que o servidor chama as partes

```
mensagem ─► seguranca.verificar_entrada ─► crise? ─► resposta fixa (CVV 188, SAMU 192)
                     │ não
                     ▼
            intencao.classificar ─► cumprimentar / agradecer / fora_do_tema? ─► acao = "conversa"
                     │ outra
                     ▼
            tema.classificar ─► confiança ≥ limiar? ─► acao = "encaminhar" : "pedir_detalhes"
                     ▼
            conhecimento.buscar   (se "encaminhar", ou se a intenção pede informação/exercício)
                     ▼
            ia.gerar ─► seguranca.revisar_saida (frase a frase) ─► site
```

Se uma parte levantar um erro, a conversa segue sem ela (e com a mensagem de reserva, se for a IA ou a revisão). A falha aparece no painel e no campo `etapas` da resposta.

---

## Segurança · `servidor/partes/seguranca.py`

```python
def verificar_entrada(mensagem: str, historico: list[Mensagem]) -> ResultadoEntrada
# ResultadoEntrada(crise: bool, motivo: str)

def revisar_saida(resposta: str) -> ResultadoSaida
# ResultadoSaida(permitida: bool, motivo: str)
```

- `historico` é a conversa **até antes** desta mensagem, da mais antiga para a mais nova. `Mensagem` tem `papel` (`"usuario"` ou `"bot"`) e `texto`.
- `revisar_saida` é chamada várias vezes por resposta: a cada frase, com **todo o texto acumulado até ali**. A última chamada recebe a resposta completa (é nela que dá para checar o tamanho). Se devolver `permitida=False`, nada mais aparece e o site troca o que já apareceu pela mensagem de reserva.
- Se `revisar_saida` levantar erro, o servidor **barra** a resposta (na dúvida, não mostra).
- Se `verificar_entrada` levantar erro, o servidor usa uma rede mínima de expressões óbvias (`servidor/rede_minima.py`), para uma crise explícita nunca passar.
- A resposta de crise é o texto fixo em `servidor/textos.py`. Troque pelo texto aprovado no protocolo de crise.

## Tema · `servidor/partes/tema.py`

```python
def classificar(mensagem: str, historico: list[Mensagem]) -> ResultadoTema
# ResultadoTema(tema: str, confianca: float, probabilidades: dict[str, float])
```

- `tema` e as chaves de `probabilidades` são ids de `TEMAS` em `servidor/contratos.py`: `estresse`, `depressao`, `bipolaridade`, `personalidade`, `ansiedade`. Se "solidão" entrar no modelo, adicione `"solidao": "Solidão"` em `TEMAS`.
- `probabilidades` tem todos os temas e soma 1. `confianca` é a probabilidade do tema escolhido.
- Precisa responder em menos de 1 segundo. Carregue o modelo uma vez, quando o módulo é importado, e não a cada chamada.
- O limiar de confiança fica em `MAIND_LIMIAR` no `.env` (padrão 0,5). O valor final deve ser escolhido com base nos dados.

## Intenção · `servidor/partes/intencao.py`

```python
def classificar(mensagem: str) -> ResultadoIntencao
# ResultadoIntencao(intencao: str, confianca: float)
```

- Ids possíveis em `INTENCOES` (`servidor/contratos.py`): `cumprimentar`, `desabafar`, `pedir_informacao`, `pedir_exercicio`, `agradecer`, `fora_do_tema`. Intenções novas entram lá.
- `INTENCOES_SEM_TEMA` lista as intenções em que o bot não procura tema. Ajuste junto com as regras de condução.

## Conhecimento · `servidor/partes/conhecimento.py`

```python
def buscar(consulta: str, tema: str | None, k: int = 3) -> list[Trecho]
# Trecho(titulo: str, texto: str, fonte_url: str, tema: str | None)
```

- Devolve até `k` trechos, do mais para o menos relevante. `tema` pode ser `None` (por exemplo, quando a pessoa pede um exercício sem tema claro).
- O site mostra `titulo` e o link `fonte_url` embaixo da resposta. A IA recebe também o `texto`.

## Conversa com a IA · `servidor/partes/ia.py`

```python
def gerar(historico: list[Mensagem], orientacoes: Orientacoes, timeout_s: float) -> Iterator[str]
# Orientacoes(acao: str, tema: str | None, intencao: str | None, trechos: list[Trecho])
```

- `historico` termina com a mensagem atual da pessoa.
- Devolve a resposta em pedaços com `yield`, na ordem. O servidor junta, revisa frase a frase e manda para o site.
- Se a IA demorar mais que `timeout_s`, falhar ou ficar sem crédito, levante `FalhaDaIA` (de `servidor.contratos`). O servidor mostra a mensagem de reserva. O servidor também corta a resposta se ela passar de `timeout_s` no total.
- A chave de acesso vem do `.env` (`os.getenv("MAIND_IA_CHAVE")`). Nunca coloque a chave no código.
- Trocar de IA deve exigir mudança só neste arquivo.

---

## Como testar

```bash
python -m pytest            # testes da plataforma (usam partes falsas, não dependem das reais)
python -m servidor          # liga tudo e abre em http://127.0.0.1:8000
```

No chat, o painel "Análise do modelo" mostra, para cada etapa, se ela é provisória, quanto tempo levou e se falhou. Também dá para mandar mensagens direto pela documentação da API em `http://127.0.0.1:8000/api/docs`.
