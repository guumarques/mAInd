"""Formatos que cada parte do mAInd recebe e devolve.

Cada parte fica em `servidor/partes/<parte>.py` e respeita estes formatos. Enquanto a
versão real não chega, cada arquivo tem uma versão provisória que finge funcionar.
A explicação completa está em `CONTRATOS.md`, na raiz do repositório.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Papel = Literal["usuario", "bot"]


@dataclass
class Mensagem:
    """Uma mensagem da conversa, como fica guardada na memória."""
    papel: Papel
    texto: str


# ---------------------------------------------------------------- segurança
@dataclass
class ResultadoEntrada:
    """A mensagem da pessoa indica crise?"""
    crise: bool
    motivo: str = ""


@dataclass
class ResultadoSaida:
    """A resposta escrita pela IA pode ser mostrada?"""
    permitida: bool
    motivo: str = ""


# ---------------------------------------------------------------- tema
@dataclass
class ResultadoTema:
    """Tema mais provável, a confiança do modelo e a chance de cada tema.

    `tema` é um dos ids de `TEMAS`; `probabilidades` tem uma entrada por tema e soma 1.
    """
    tema: str
    confianca: float
    probabilidades: dict[str, float]


# ---------------------------------------------------------------- intenção
@dataclass
class ResultadoIntencao:
    """O que a pessoa quer naquele momento. `intencao` é um dos ids de `INTENCOES`."""
    intencao: str
    confianca: float


# ---------------------------------------------------------------- conhecimento
@dataclass
class Trecho:
    """Um trecho da biblioteca de conhecimento."""
    titulo: str
    texto: str
    fonte_url: str
    tema: str | None = None


# ---------------------------------------------------------------- conversa com a IA
@dataclass
class Orientacoes:
    """O que a IA recebe além da conversa para escrever a resposta."""
    acao: str                      # "encaminhar" | "pedir_detalhes" | "conversa"
    tema: str | None = None
    intencao: str | None = None
    trechos: list[Trecho] = field(default_factory=list)


class FalhaDaIA(Exception):
    """A IA demorou, falhou ou ficou sem crédito. O servidor responde com a mensagem de reserva."""


# ---------------------------------------------------------------- vocabulário comum
TEMAS: dict[str, str] = {
    "estresse": "Estresse",
    "depressao": "Depressão",
    "bipolaridade": "Bipolaridade",
    "personalidade": "Personalidade",
    "ansiedade": "Ansiedade",
}

INTENCOES: dict[str, str] = {
    "cumprimentar": "Cumprimentar",
    "desabafar": "Desabafar",
    "pedir_informacao": "Pedir informação",
    "pedir_exercicio": "Pedir exercício",
    "agradecer": "Agradecer",
    "fora_do_tema": "Fora do tema",
}

# Intenções em que o bot só conversa, sem procurar tema nem conteúdo.
INTENCOES_SEM_TEMA = {"cumprimentar", "agradecer", "fora_do_tema"}
