"""Tema da conversa · Integrante 1.

VERSÃO PROVISÓRIA: devolve sempre o mesmo resultado. Substitua `classificar` pela versão
real (o modelo treinado), mantendo o nome, os parâmetros e o formato de retorno.
A versão real deve responder em menos de 1 segundo.
"""
from servidor.contratos import Mensagem, ResultadoTema

RESPONSAVEL = "Integrante 1"
PROVISORIO = True
DESCRICAO = "resultado fixo (provisório)"


def classificar(mensagem: str, historico: list[Mensagem]) -> ResultadoTema:
    probabilidades = {
        "estresse": 0.10,
        "depressao": 0.10,
        "bipolaridade": 0.05,
        "personalidade": 0.05,
        "ansiedade": 0.70,
    }
    return ResultadoTema(tema="ansiedade", confianca=0.70, probabilidades=probabilidades)
