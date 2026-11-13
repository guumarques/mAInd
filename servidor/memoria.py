"""Memória da conversa, guardada em SQLite (`dados/conversas.db`).

Sobrevive a reinícios do servidor e pode ser apagada pelo usuário. Guarda só o necessário
para o bot lembrar a conversa: texto, quem falou, quando, e a ação/tema decididos.
O que guardar e por quanto tempo se controla por `MAIND_GUARDAR_CONVERSAS` e `apagar_antigas`.
"""
from __future__ import annotations

import sqlite3
import threading
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from servidor.contratos import Mensagem

_ESQUEMA = """
CREATE TABLE IF NOT EXISTS sessoes (
    sessao_id     TEXT PRIMARY KEY,
    criada_em     TEXT NOT NULL,
    atualizada_em TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS mensagens (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    sessao_id TEXT NOT NULL REFERENCES sessoes(sessao_id) ON DELETE CASCADE,
    papel     TEXT NOT NULL CHECK (papel IN ('usuario', 'bot')),
    texto     TEXT NOT NULL,
    acao      TEXT,
    tema      TEXT,
    criada_em TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_mensagens_sessao ON mensagens(sessao_id, id);
"""


def _agora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Memoria:
    def __init__(self, caminho: Path | str, guardar: bool = True):
        self.guardar = guardar
        self._trava = threading.Lock()
        if str(caminho) != ":memory:":
            Path(caminho).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(str(caminho), check_same_thread=False)
        self._db.execute("PRAGMA foreign_keys = ON")
        self._db.executescript(_ESQUEMA)
        self._db.commit()
        # Com MAIND_GUARDAR_CONVERSAS=0 nada é escrito em disco: a conversa vive só na memória do processo.
        self._volatil: dict[str, list[Mensagem]] = {}

    # ------------------------------------------------------------ sessões
    def nova_sessao(self) -> str:
        sessao_id = uuid.uuid4().hex
        if self.guardar:
            with self._trava:
                agora = _agora()
                self._db.execute("INSERT INTO sessoes VALUES (?, ?, ?)", (sessao_id, agora, agora))
                self._db.commit()
        else:
            self._volatil[sessao_id] = []
        return sessao_id

    def existe(self, sessao_id: str) -> bool:
        if not self.guardar:
            return sessao_id in self._volatil
        with self._trava:
            row = self._db.execute("SELECT 1 FROM sessoes WHERE sessao_id = ?", (sessao_id,)).fetchone()
        return row is not None

    def apagar(self, sessao_id: str) -> bool:
        """Apaga a conversa inteira. Devolve False se ela não existia."""
        if not self.guardar:
            return self._volatil.pop(sessao_id, None) is not None
        with self._trava:
            cur = self._db.execute("DELETE FROM sessoes WHERE sessao_id = ?", (sessao_id,))
            self._db.commit()
        return cur.rowcount > 0

    def apagar_antigas(self, dias: int) -> int:
        """Apaga conversas sem atividade há mais de `dias` dias. Devolve quantas apagou."""
        limite = (datetime.now(timezone.utc) - timedelta(days=dias)).isoformat(timespec="seconds")
        with self._trava:
            cur = self._db.execute("DELETE FROM sessoes WHERE atualizada_em < ?", (limite,))
            self._db.commit()
        return cur.rowcount

    # ------------------------------------------------------------ mensagens
    def adicionar(self, sessao_id: str, papel: str, texto: str,
                  acao: str | None = None, tema: str | None = None) -> None:
        if not self.guardar:
            self._volatil.setdefault(sessao_id, []).append(Mensagem(papel, texto))
            return
        with self._trava:
            agora = _agora()
            self._db.execute(
                "INSERT INTO mensagens (sessao_id, papel, texto, acao, tema, criada_em) VALUES (?, ?, ?, ?, ?, ?)",
                (sessao_id, papel, texto, acao, tema, agora),
            )
            self._db.execute("UPDATE sessoes SET atualizada_em = ? WHERE sessao_id = ?", (agora, sessao_id))
            self._db.commit()

    def historico(self, sessao_id: str, limite: int | None = None) -> list[Mensagem]:
        """Mensagens da conversa, da mais antiga para a mais nova (as `limite` últimas)."""
        if not self.guardar:
            msgs = self._volatil.get(sessao_id, [])
            return list(msgs[-limite:] if limite else msgs)
        with self._trava:
            rows = self._db.execute(
                "SELECT papel, texto FROM mensagens WHERE sessao_id = ? ORDER BY id DESC LIMIT ?",
                (sessao_id, limite if limite else -1),
            ).fetchall()
        return [Mensagem(p, t) for p, t in reversed(rows)]

    def fechar(self) -> None:
        self._db.close()
