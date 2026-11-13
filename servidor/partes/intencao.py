"""Intenção da mensagem · Integrante 4.

VERSÃO PROVISÓRIA: devolve sempre "desabafar". Substitua `classificar` pela versão real,
mantendo o nome, os parâmetros e o formato de retorno. Os ids possíveis estão em
`servidor.contratos.INTENCOES` (se o grupo criar intenções novas, adicione lá).
"""
from servidor.contratos import ResultadoIntencao

RESPONSAVEL = "Integrante 4"
PROVISORIO = True
DESCRICAO = "sempre 'desabafar' (provisório)"


def classificar(mensagem: str) -> ResultadoIntencao:
    return ResultadoIntencao(intencao="desabafar", confianca=1.0)
