"""Junção das partes: cada mensagem passa pelas 5 etapas, nesta ordem.

  1. segurança na entrada   → se for crise, responde na hora com o texto fixo
  2. entendimento           → intenção (o que a pessoa quer) e tema (sobre o que fala)
  3. conhecimento           → trechos da biblioteca sobre o tema
  4. conversa com a IA      → a resposta, em pedaços
  5. revisão da resposta    → frase a frase, antes de aparecer na tela

`Pipeline.processar` é um gerador de eventos, usado tanto pela rota com resposta aos poucos
(`/api/mensagem/stream`) quanto pela rota com resposta inteira (`/api/mensagem`):

  ("analise", {...})    o que o sistema entendeu (vai para o painel "Análise do modelo")
  ("texto", "...")      um pedaço da resposta, já revisado
  ("substituir", "...") a revisão barrou ou a IA falhou: troque o que foi mostrado por este texto
  ("fim", {...})        resposta final, latência e o registro de cada etapa

Se uma parte falhar, a conversa segue (com a mensagem de reserva, se for preciso) e a falha
fica registrada em `etapas`.
"""
from __future__ import annotations

import logging
import re
import time
from collections.abc import Iterator
from types import ModuleType, SimpleNamespace
from typing import Any

from servidor.config import Config
from servidor.contratos import (INTENCOES, INTENCOES_SEM_TEMA, TEMAS, FalhaDaIA, Mensagem,
                                Orientacoes, ResultadoEntrada, ResultadoIntencao, ResultadoTema, Trecho)
from servidor.memoria import Memoria
from servidor.rede_minima import parece_crise
from servidor.textos import RESPOSTA_CRISE, RESPOSTA_RESERVA

log = logging.getLogger("maind.pipeline")

_FIM_DE_FRASE = re.compile(r"[.!?…:;]+[\"')\]]*\s+|\n+")
_FRASE_MAX = 240          # sem pontuação por muito tempo, revisa assim mesmo para não travar a tela


def partes_padrao() -> SimpleNamespace:
    from servidor.partes import conhecimento, ia, intencao, seguranca, tema
    return SimpleNamespace(seguranca=seguranca, tema=tema, intencao=intencao,
                           conhecimento=conhecimento, ia=ia)


class _Etapas:
    """Registro do que aconteceu em cada etapa, mostrado no painel e usado no experimento."""

    def __init__(self, partes: SimpleNamespace, config: Config):
        self.itens: list[dict[str, Any]] = []
        self._partes, self._config = partes, config

    def registrar(self, id_: str, nome: str, parte: ModuleType | None, status: str,
                  ms: float | None = None, detalhe: str = "", descricao_attr: str = "DESCRICAO") -> None:
        self.itens.append({
            "id": id_,
            "nome": nome,
            "descricao": getattr(parte, descricao_attr, "") if parte else "",
            "provisoria": bool(getattr(parte, "PROVISORIO", False)),
            "status": status,           # ok | falhou | desligada | pulada
            "ms": round(ms, 1) if ms is not None else None,
            "detalhe": detalhe,
        })


def _cronometrar(fn, *args, **kwargs):
    t = time.perf_counter()
    r = fn(*args, **kwargs)
    return r, (time.perf_counter() - t) * 1000


class Pipeline:
    def __init__(self, config: Config, memoria: Memoria, partes: SimpleNamespace | None = None):
        self.config = config
        self.memoria = memoria
        self.partes = partes or partes_padrao()

    # ------------------------------------------------------------ informação para /api/saude
    def descrever(self) -> dict[str, Any]:
        p = self.partes
        def info(parte, ligada, attr="DESCRICAO"):
            return {"ligada": ligada, "provisoria": bool(getattr(parte, "PROVISORIO", False)),
                    "descricao": getattr(parte, attr, "")}
        c = self.config
        return {
            "seguranca_entrada": info(p.seguranca, c.ligada("seguranca"), "DESCRICAO_ENTRADA"),
            "intencao": info(p.intencao, c.ligada("intencao")),
            "tema": info(p.tema, c.ligada("tema")),
            "conhecimento": info(p.conhecimento, c.ligada("conhecimento")),
            "ia": info(p.ia, True),
            "seguranca_saida": info(p.seguranca, c.ligada("seguranca"), "DESCRICAO_SAIDA"),
        }

    # ------------------------------------------------------------ fluxo principal
    def processar(self, texto: str, sessao_id: str | None = None) -> Iterator[tuple[str, Any]]:
        t0 = time.perf_counter()
        c, p = self.config, self.partes
        etapas = _Etapas(p, c)

        if not sessao_id or not self.memoria.existe(sessao_id):
            sessao_id = self.memoria.nova_sessao()
        historico = self.memoria.historico(sessao_id, c.historico_max)
        self.memoria.adicionar(sessao_id, "usuario", texto)

        analise: dict[str, Any] = {
            "sessao_id": sessao_id, "acao": None, "tema": None, "confianca": None,
            "limiar": c.limiar_confianca, "probabilidades": [], "intencao": None,
            "trechos": [], "perfil": c.perfil,
        }

        # ---------------- 1. segurança na entrada
        crise, motivo = self._seguranca_entrada(texto, historico, etapas)
        if crise:
            analise.update(acao="crise", motivo_crise=motivo)
            for id_, nome, parte in (("intencao", "Intenção", p.intencao), ("tema", "Tema", p.tema),
                                     ("conhecimento", "Conhecimento", p.conhecimento), ("ia", "Conversa com a IA", p.ia)):
                etapas.registrar(id_, nome, parte, "pulada", detalhe="crise: resposta fixa")
            etapas.registrar("seguranca_saida", "Revisão da resposta", p.seguranca, "pulada",
                             detalhe="texto fixo aprovado pelo grupo", descricao_attr="DESCRICAO_SAIDA")
            yield "analise", analise
            yield "texto", RESPOSTA_CRISE
            self.memoria.adicionar(sessao_id, "bot", RESPOSTA_CRISE, acao="crise")
            yield "fim", self._fim(RESPOSTA_CRISE, True, "", t0, etapas)
            return

        # ---------------- 2. entendimento: intenção e tema
        intencao = self._intencao(texto, etapas)
        if intencao:
            analise["intencao"] = {"id": intencao.intencao,
                                   "nome": INTENCOES.get(intencao.intencao, intencao.intencao),
                                   "confianca": intencao.confianca}

        sem_tema = intencao is not None and intencao.intencao in INTENCOES_SEM_TEMA
        tema = None
        if sem_tema:
            etapas.registrar("tema", "Tema", p.tema, "pulada", detalhe=f"intenção: {intencao.intencao}")
        else:
            tema = self._tema(texto, historico, etapas)

        if tema is None:
            analise["acao"] = "conversa"
        else:
            analise.update(
                tema={"id": tema.tema, "nome": TEMAS.get(tema.tema, tema.tema)},
                confianca=tema.confianca,
                probabilidades=[{"id": k, "nome": TEMAS.get(k, k), "p": v} for k, v in tema.probabilidades.items()],
                acao="encaminhar" if tema.confianca >= c.limiar_confianca else "pedir_detalhes",
            )

        # ---------------- 3. conhecimento
        trechos: list[Trecho] = []
        if analise["acao"] == "encaminhar" or (intencao and intencao.intencao in {"pedir_informacao", "pedir_exercicio"}):
            trechos = self._conhecimento(texto, tema.tema if tema else None, etapas)
        else:
            etapas.registrar("conhecimento", "Conhecimento", p.conhecimento,
                             "desligada" if not c.ligada("conhecimento") else "pulada",
                             detalhe="" if not c.ligada("conhecimento") else f"ação: {analise['acao']}")
        analise["trechos"] = [{"titulo": t.titulo, "fonte_url": t.fonte_url, "tema": t.tema} for t in trechos]

        yield "analise", analise

        # ---------------- 4 e 5. IA escrevendo + revisão frase a frase
        orient = Orientacoes(acao=analise["acao"], tema=tema.tema if tema else None,
                             intencao=intencao.intencao if intencao else None, trechos=trechos)
        conversa = historico + [Mensagem("usuario", texto)]
        resposta, permitida, motivo_rev = yield from self._escrever(conversa, orient, etapas)

        self.memoria.adicionar(sessao_id, "bot", resposta, acao=analise["acao"],
                               tema=tema.tema if tema else None)
        yield "fim", self._fim(resposta, permitida, motivo_rev, t0, etapas)

    # ------------------------------------------------------------ etapas
    def _seguranca_entrada(self, texto: str, historico: list[Mensagem], etapas: _Etapas) -> tuple[bool, str]:
        seg = self.partes.seguranca
        if not self.config.ligada("seguranca"):
            etapas.registrar("seguranca_entrada", "Segurança na entrada", seg, "desligada",
                             descricao_attr="DESCRICAO_ENTRADA")
            return False, ""
        try:
            r, ms = _cronometrar(seg.verificar_entrada, texto, historico)
            if not isinstance(r, ResultadoEntrada):
                raise TypeError(f"verificar_entrada devolveu {type(r).__name__}, esperado ResultadoEntrada")
            etapas.registrar("seguranca_entrada", "Segurança na entrada", seg, "ok", ms,
                             detalhe="crise" if r.crise else "sem sinal de crise", descricao_attr="DESCRICAO_ENTRADA")
            return r.crise, r.motivo
        except Exception as e:
            # A parte falhou: usa a rede mínima, para uma crise explícita nunca passar.
            log.exception("segurança na entrada falhou")
            crise = parece_crise(texto)
            etapas.registrar("seguranca_entrada", "Segurança na entrada", seg, "falhou",
                             detalhe=f"{type(e).__name__}; rede mínima usada", descricao_attr="DESCRICAO_ENTRADA")
            return crise, "rede mínima (parte de segurança falhou)" if crise else ""

    def _intencao(self, texto: str, etapas: _Etapas) -> ResultadoIntencao | None:
        parte = self.partes.intencao
        if not self.config.ligada("intencao"):
            etapas.registrar("intencao", "Intenção", parte, "desligada")
            return None
        try:
            r, ms = _cronometrar(parte.classificar, texto)
            etapas.registrar("intencao", "Intenção", parte, "ok", ms, detalhe=r.intencao)
            return r
        except Exception as e:
            log.exception("intenção falhou")
            etapas.registrar("intencao", "Intenção", parte, "falhou", detalhe=type(e).__name__)
            return None

    def _tema(self, texto: str, historico: list[Mensagem], etapas: _Etapas) -> ResultadoTema | None:
        parte = self.partes.tema
        if not self.config.ligada("tema"):
            etapas.registrar("tema", "Tema", parte, "desligada")
            return None
        try:
            r, ms = _cronometrar(parte.classificar, texto, historico)
            etapas.registrar("tema", "Tema", parte, "ok", ms, detalhe=f"{r.tema} · {r.confianca:.2f}")
            return r
        except Exception as e:
            log.exception("tema falhou")
            etapas.registrar("tema", "Tema", parte, "falhou", detalhe=type(e).__name__)
            return None

    def _conhecimento(self, texto: str, tema: str | None, etapas: _Etapas) -> list[Trecho]:
        parte = self.partes.conhecimento
        if not self.config.ligada("conhecimento"):
            etapas.registrar("conhecimento", "Conhecimento", parte, "desligada")
            return []
        try:
            r, ms = _cronometrar(parte.buscar, texto, tema)
            etapas.registrar("conhecimento", "Conhecimento", parte, "ok", ms, detalhe=f"{len(r)} trechos")
            return list(r)
        except Exception as e:
            log.exception("conhecimento falhou")
            etapas.registrar("conhecimento", "Conhecimento", parte, "falhou", detalhe=type(e).__name__)
            return []

    def _revisar(self, texto: str) -> tuple[bool, str]:
        if not self.config.ligada("seguranca"):
            return True, ""
        try:
            r = self.partes.seguranca.revisar_saida(texto)
            return r.permitida, r.motivo
        except Exception as e:
            # Na dúvida, não mostra: uma resposta sem revisão pode fazer mal.
            log.exception("revisão da resposta falhou")
            return False, f"revisão falhou ({type(e).__name__})"

    def _escrever(self, conversa: list[Mensagem], orient: Orientacoes, etapas: _Etapas):
        """Gera a resposta com a IA e a revisa frase a frase. Devolve (resposta, permitida, motivo)."""
        p, c = self.partes, self.config
        t_ia = time.perf_counter()
        t_rev = 0.0
        aprovado, buffer = "", ""
        falha_ia: str | None = None
        barrada: str | None = None

        def revisar_e_emitir(trecho: str):
            nonlocal aprovado, barrada, t_rev
            t = time.perf_counter()
            ok, motivo = self._revisar(aprovado + trecho)
            t_rev += (time.perf_counter() - t) * 1000
            if not ok:
                barrada = motivo or "resposta barrada pela revisão"
                return False
            aprovado += trecho
            return True

        try:
            for pedaco in p.ia.gerar(conversa, orient, c.timeout_ia_s):
                if time.perf_counter() - t_ia > c.timeout_ia_s:
                    raise FalhaDaIA("tempo esgotado")
                buffer += pedaco
                while True:
                    m = _FIM_DE_FRASE.search(buffer)
                    if m:
                        corte = m.end()
                    elif len(buffer) > _FRASE_MAX:
                        corte = buffer.rfind(" ", 0, _FRASE_MAX) + 1 or len(buffer)
                    else:
                        break
                    frase, buffer = buffer[:corte], buffer[corte:]
                    if not revisar_e_emitir(frase):
                        break
                    yield "texto", frase
                if barrada:
                    break
            if not barrada and buffer.strip():
                if revisar_e_emitir(buffer):
                    yield "texto", buffer
        except Exception as e:  # FalhaDaIA ou qualquer erro inesperado da parte
            log.warning("IA falhou: %s", e)
            falha_ia = f"{type(e).__name__}: {e}" if str(e) else type(e).__name__

        ms_ia = (time.perf_counter() - t_ia) * 1000 - t_rev
        if falha_ia:
            etapas.registrar("ia", "Conversa com a IA", p.ia, "falhou", ms_ia, detalhe=falha_ia)
        else:
            etapas.registrar("ia", "Conversa com a IA", p.ia, "ok", ms_ia)

        if not c.ligada("seguranca"):
            etapas.registrar("seguranca_saida", "Revisão da resposta", p.seguranca, "desligada",
                             descricao_attr="DESCRICAO_SAIDA")
        else:
            etapas.registrar("seguranca_saida", "Revisão da resposta", p.seguranca,
                             "ok", t_rev, detalhe=f"barrada: {barrada}" if barrada else "aprovada",
                             descricao_attr="DESCRICAO_SAIDA")

        if barrada or falha_ia or not aprovado.strip():
            if aprovado:
                yield "substituir", RESPOSTA_RESERVA
            else:
                yield "texto", RESPOSTA_RESERVA
            motivo = barrada or (f"IA falhou: {falha_ia}" if falha_ia else "IA devolveu resposta vazia")
            return RESPOSTA_RESERVA, not barrada, motivo
        return aprovado.strip(), True, ""

    def _fim(self, resposta: str, permitida: bool, motivo: str, t0: float, etapas: _Etapas) -> dict[str, Any]:
        return {
            "resposta": resposta,
            "revisao": {"permitida": permitida, "motivo": motivo},
            "latencia_ms": round((time.perf_counter() - t0) * 1000),
            "etapas": etapas.itens,
        }

    def responder(self, texto: str, sessao_id: str | None = None) -> dict[str, Any]:
        """Versão com a resposta inteira de uma vez (usada por `/api/mensagem`, testes e experimento)."""
        resultado: dict[str, Any] = {}
        for tipo, dados in self.processar(texto, sessao_id):
            if tipo == "analise":
                resultado.update(dados)
            elif tipo == "fim":
                resultado.update(dados)
        return resultado
