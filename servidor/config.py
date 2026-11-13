"""Configuração do servidor, lida de variáveis de ambiente (ou do arquivo `.env`).

Veja `.env.example` para a lista completa. Nada aqui deve conter senha ou chave:
chaves ficam só no `.env`, que nunca vai para o GitHub.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
load_dotenv(RAIZ / ".env")

# Perfis prontos para o experimento comparativo. A segurança fica ligada em todos.
PERFIS: dict[str, dict[str, bool]] = {
    "completo":             {"tema": True,  "intencao": True,  "conhecimento": True},
    "so_ia":                {"tema": False, "intencao": False, "conhecimento": False},
    "ia_tema":              {"tema": True,  "intencao": False, "conhecimento": False},
    "ia_tema_conhecimento": {"tema": True,  "intencao": False, "conhecimento": True},
}


def _bool(nome: str, padrao: bool) -> bool:
    v = os.getenv(nome)
    if v is None or v.strip() == "":
        return padrao
    return v.strip().lower() in {"1", "true", "sim", "s", "yes", "on"}


@dataclass
class Config:
    perfil: str = "completo"
    partes: dict[str, bool] = field(default_factory=dict)
    limiar_confianca: float = 0.5
    banco: Path = RAIZ / "dados" / "conversas.db"
    guardar_conversas: bool = True
    historico_max: int = 20            # quantas mensagens anteriores vão para as partes e para a IA
    timeout_ia_s: float = 20.0
    porta: int = 8000

    def ligada(self, parte: str) -> bool:
        return self.partes.get(parte, True)


def carregar() -> Config:
    perfil = os.getenv("MAIND_PERFIL", "completo").strip() or "completo"
    if perfil not in PERFIS:
        raise ValueError(f"MAIND_PERFIL inválido: {perfil!r}. Use um de: {', '.join(PERFIS)}")
    partes = dict(PERFIS[perfil])
    partes["seguranca"] = True
    # Cada parte ainda pode ser forçada individualmente (ex.: MAIND_PARTE_TEMA=0).
    for nome in ("seguranca", "tema", "intencao", "conhecimento"):
        partes[nome] = _bool(f"MAIND_PARTE_{nome.upper()}", partes[nome])

    banco = os.getenv("MAIND_BANCO")
    return Config(
        perfil=perfil,
        partes=partes,
        limiar_confianca=float(os.getenv("MAIND_LIMIAR", "0.5")),
        banco=Path(banco) if banco else RAIZ / "dados" / "conversas.db",
        guardar_conversas=_bool("MAIND_GUARDAR_CONVERSAS", True),
        historico_max=int(os.getenv("MAIND_HISTORICO_MAX", "20")),
        timeout_ia_s=float(os.getenv("MAIND_TIMEOUT_IA_S", "20")),
        porta=int(os.getenv("MAIND_PORTA", "8000")),
    )
