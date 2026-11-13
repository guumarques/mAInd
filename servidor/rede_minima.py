"""Rede mínima de segurança da plataforma.

Não é o detector do projeto (esse é do Integrante 2, em `partes/seguranca.py`). É só uma lista
de expressões óbvias usada em dois casos: pela versão provisória da segurança, e pelo
servidor se a parte de segurança falhar. Assim, uma crise dita com todas as letras nunca
passa sem resposta, mesmo com a parte real fora do ar.
"""
import re

_CRISE = re.compile(
    r"suic[ií]d|me matar|me mate|tirar (a )?minha (pr[oó]pria )?vida|n[aã]o quero mais viver|"
    r"quero morrer|acabar com (a minha vida|tudo)|me machucar|automutila|me cortar",
    re.IGNORECASE,
)


def parece_crise(texto: str) -> bool:
    return bool(_CRISE.search(texto))
