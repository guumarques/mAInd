"""Biblioteca de conhecimento.

VERSÃO PROVISÓRIA: devolve sempre os mesmos trechos. Substitua `buscar` pela versão real,
mantendo o nome, os parâmetros e o formato de retorno.
"""
from servidor.contratos import Trecho

PROVISORIO = True
DESCRICAO = "trechos fixos (provisório)"


def buscar(consulta: str, tema: str | None, k: int = 3) -> list[Trecho]:
    """Devolve até `k` trechos úteis, do mais para o menos relevante."""
    trechos = [
        Trecho(
            titulo="O que é ansiedade",
            texto="A ansiedade é uma reação natural do corpo a situações de perigo ou pressão. "
                  "Quando fica intensa e constante, pode atrapalhar a rotina e merece atenção.",
            fonte_url="https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/a/ansiedade",
            tema="ansiedade",
        ),
        Trecho(
            titulo="Quando procurar ajuda",
            texto="Se o sofrimento atrapalha os estudos, o trabalho ou as relações, vale procurar "
                  "um psicólogo ou uma Unidade Básica de Saúde.",
            fonte_url="https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/s/saude-mental",
            tema=None,
        ),
    ]
    return trechos[:k]
