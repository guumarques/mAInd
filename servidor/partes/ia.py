"""Conversa com a IA · Integrante 4.

VERSÃO PROVISÓRIA: devolve sempre frases fixas, em pedaços, imitando a IA escrevendo.
Substitua `gerar` pela versão real, mantendo o nome, os parâmetros e o formato:

- recebe a conversa até ali (a última mensagem é a da pessoa) e as orientações;
- devolve a resposta em pedaços (`yield`), para ela ir aparecendo aos poucos no site;
- respeita `timeout_s` e, se a IA demorar, falhar ou ficar sem crédito, levanta `FalhaDaIA`.
  O servidor então mostra a mensagem de reserva, em vez de travar.

A chave de acesso da IA vem do `.env` (ex.: `os.getenv("MAIND_IA_CHAVE")`), nunca do código.
"""
import time
from collections.abc import Iterator

from servidor.contratos import Mensagem, Orientacoes

RESPONSAVEL = "Integrante 4"
PROVISORIO = True
DESCRICAO = "frases fixas (provisório)"

_FRASES = {
    "encaminhar": "Obrigado por me contar isso. Parece que você está passando por um momento pesado. "
                  "Separei um conteúdo que pode te ajudar a entender melhor o que está sentindo.",
    "pedir_detalhes": "Quero entender melhor para te ajudar. Pode me contar um pouco mais? "
                      "Por exemplo, há quanto tempo você está assim?",
    "conversa": "Estou aqui para te ouvir. Como você está se sentindo hoje?",
}


def gerar(historico: list[Mensagem], orientacoes: Orientacoes, timeout_s: float) -> Iterator[str]:
    texto = _FRASES.get(orientacoes.acao, _FRASES["conversa"])
    for palavra in texto.split(" "):
        time.sleep(0.02)
        yield palavra + " "
