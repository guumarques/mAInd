"""Segurança da conversa · Integrante 2.

VERSÃO PROVISÓRIA. Substitua o corpo das duas funções pela versão real, mantendo
os nomes, os parâmetros e o formato de retorno (ver `CONTRATOS.md`).
"""
from servidor.contratos import Mensagem, ResultadoEntrada, ResultadoSaida
from servidor.rede_minima import parece_crise

RESPONSAVEL = "Integrante 2"
PROVISORIO = True
DESCRICAO_ENTRADA = "lista fixa de expressões de risco (provisória)"
DESCRICAO_SAIDA = "aprova tudo (provisória)"


def verificar_entrada(mensagem: str, historico: list[Mensagem]) -> ResultadoEntrada:
    """A mensagem da pessoa indica crise?"""
    if parece_crise(mensagem):
        return ResultadoEntrada(crise=True, motivo="expressão de risco explícita")
    return ResultadoEntrada(crise=False)


def revisar_saida(resposta: str) -> ResultadoSaida:
    """A resposta escrita pela IA pode ser mostrada?

    O servidor chama esta função várias vezes durante a escrita, sempre com o texto
    acumulado até ali (frase a frase), e uma última vez com a resposta completa.
    """
    return ResultadoSaida(permitida=True)
