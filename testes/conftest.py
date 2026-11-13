"""Peças comuns dos testes: partes falsas, controláveis, no lugar das partes reais."""
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from servidor.app import criar_app
from servidor.config import PERFIS, Config
from servidor.contratos import (FalhaDaIA, ResultadoEntrada, ResultadoIntencao, ResultadoSaida,
                                ResultadoTema, Trecho)
from servidor.memoria import Memoria
from servidor.pipeline import Pipeline


class Falsas:
    """Partes falsas. Cada teste muda o que precisa (ex.: `falsas.confianca = 0.2`)."""

    def __init__(self):
        self.intencao_id = "desabafar"
        self.confianca = 0.8
        self.resposta_ia = "Que bom que você me contou. Isso parece pesado. Estou aqui com você."
        self.ia_falha_apos: int | None = None      # levanta FalhaDaIA depois de N pedaços
        self.barrar_se_contiver: str | None = None
        self.chamadas: list[str] = []
        self.historicos_recebidos: list[list] = []
        self.orientacoes_recebidas = []
        self.revisoes: list[str] = []

    def ns(self) -> SimpleNamespace:
        f = self

        class seguranca:
            PROVISORIO = False
            @staticmethod
            def verificar_entrada(msg, hist):
                f.chamadas.append("seguranca_entrada")
                return ResultadoEntrada(crise="me matar" in msg.lower(), motivo="teste")
            @staticmethod
            def revisar_saida(resp):
                f.revisoes.append(resp)
                if f.barrar_se_contiver and f.barrar_se_contiver in resp:
                    return ResultadoSaida(False, "contém termo proibido")
                return ResultadoSaida(True)

        class tema:
            @staticmethod
            def classificar(msg, hist):
                f.chamadas.append("tema")
                f.historicos_recebidos.append(list(hist))
                resto = (1 - f.confianca) / 4
                probs = {t: resto for t in ("estresse", "depressao", "bipolaridade", "personalidade")}
                probs["ansiedade"] = f.confianca
                return ResultadoTema("ansiedade", f.confianca, probs)

        class intencao:
            @staticmethod
            def classificar(msg):
                f.chamadas.append("intencao")
                return ResultadoIntencao(f.intencao_id, 0.9)

        class conhecimento:
            @staticmethod
            def buscar(consulta, tema, k=3):
                f.chamadas.append("conhecimento")
                return [Trecho("Ansiedade", "texto", "https://exemplo.org", "ansiedade")]

        class ia:
            @staticmethod
            def gerar(historico, orientacoes, timeout_s):
                f.chamadas.append("ia")
                f.orientacoes_recebidas.append(orientacoes)
                for i, palavra in enumerate(f.resposta_ia.split(" ")):
                    if f.ia_falha_apos is not None and i >= f.ia_falha_apos:
                        raise FalhaDaIA("sem crédito")
                    yield palavra + " "

        return SimpleNamespace(seguranca=seguranca, tema=tema, intencao=intencao,
                               conhecimento=conhecimento, ia=ia)


def montar_config(tmp_path, perfil="completo", **extra) -> Config:
    partes = dict(PERFIS[perfil], seguranca=True)
    return Config(perfil=perfil, partes=partes, banco=tmp_path / "teste.db", **extra)


@pytest.fixture
def falsas():
    return Falsas()


@pytest.fixture
def pipeline(tmp_path, falsas):
    return Pipeline(montar_config(tmp_path), Memoria(tmp_path / "teste.db"), falsas.ns())


@pytest.fixture
def cliente(tmp_path, falsas):
    return TestClient(criar_app(montar_config(tmp_path), falsas.ns()))
