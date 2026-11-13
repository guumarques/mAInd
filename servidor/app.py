"""API do mAInd (FastAPI). Também serve o site da pasta `frontend/`.

Rotas (detalhes em `frontend/README.md`):
  GET    /api/saude                 status do servidor e de cada parte
  POST   /api/mensagem              resposta inteira, em JSON
  POST   /api/mensagem/stream       resposta aos poucos (Server-Sent Events)
  GET    /api/sessao/{sessao_id}    mensagens guardadas da conversa
  DELETE /api/sessao/{sessao_id}    apaga a conversa
"""
from __future__ import annotations

import json
import logging
from types import SimpleNamespace

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from servidor import config as cfg
from servidor.memoria import Memoria
from servidor.pipeline import Pipeline

log = logging.getLogger("maind")

TEXTO_MAX = 2000


class EntradaMensagem(BaseModel):
    texto: str = Field(..., max_length=TEXTO_MAX)
    sessao_id: str | None = Field(None, max_length=64)

    @field_validator("texto")
    @classmethod
    def nao_vazio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("a mensagem está vazia")
        return v


def _sse(evento: str, dados) -> str:
    return f"event: {evento}\ndata: {json.dumps(dados, ensure_ascii=False)}\n\n"


def criar_app(config: cfg.Config | None = None, partes: SimpleNamespace | None = None) -> FastAPI:
    config = config or cfg.carregar()
    memoria = Memoria(config.banco, guardar=config.guardar_conversas)
    pipeline = Pipeline(config, memoria, partes)

    app = FastAPI(title="mAInd", docs_url="/api/docs", openapi_url="/api/openapi.json")
    app.state.config, app.state.memoria, app.state.pipeline = config, memoria, pipeline
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

    # ---------------------------------------------------------------- erros compreensíveis
    @app.exception_handler(RequestValidationError)
    async def erro_validacao(request: Request, exc: RequestValidationError):
        erros = exc.errors()
        campo = erros[0]["loc"][-1] if erros else ""
        if campo == "texto" and erros[0].get("type") == "string_too_long":
            msg = f"A mensagem é longa demais. Tente resumir em até {TEXTO_MAX} caracteres."
        elif campo == "texto":
            msg = "Escreva alguma coisa antes de enviar."
        else:
            msg = "Não entendi o pedido enviado ao servidor."
        return JSONResponse(status_code=422, content={"erro": msg})

    @app.exception_handler(Exception)
    async def erro_geral(request: Request, exc: Exception):
        log.exception("erro inesperado")
        return JSONResponse(status_code=500, content={
            "erro": "Algo deu errado do nosso lado. Tente de novo em instantes. "
                    "Se precisar conversar com alguém agora, o CVV atende 24h pelo 188."})

    # ---------------------------------------------------------------- rotas
    @app.get("/api/saude")
    def saude():
        partes = pipeline.descrever()
        return {
            "status": "ok",
            "perfil": config.perfil,
            "modelo": {
                "limiar_confianca": config.limiar_confianca,
                "tema": partes["tema"]["descricao"],
                "provisorio": any(p["provisoria"] for p in partes.values()),
            },
            "partes": partes,
            "guarda_conversas": config.guardar_conversas,
        }

    @app.post("/api/mensagem")
    def mensagem(entrada: EntradaMensagem):
        return pipeline.responder(entrada.texto, entrada.sessao_id)

    @app.post("/api/mensagem/stream")
    def mensagem_stream(entrada: EntradaMensagem):
        def eventos():
            try:
                for tipo, dados in pipeline.processar(entrada.texto, entrada.sessao_id):
                    yield _sse(tipo, dados)
            except Exception:
                log.exception("erro durante a resposta")
                yield _sse("erro", {"erro": "Algo deu errado no meio da resposta. Pode tentar de novo?"})
        return StreamingResponse(eventos(), media_type="text/event-stream",
                                 headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    @app.get("/api/sessao/{sessao_id}")
    def ver_sessao(sessao_id: str):
        if not memoria.existe(sessao_id):
            return JSONResponse(status_code=404, content={"erro": "Conversa não encontrada."})
        return {"sessao_id": sessao_id,
                "mensagens": [{"papel": m.papel, "texto": m.texto} for m in memoria.historico(sessao_id)]}

    @app.delete("/api/sessao/{sessao_id}")
    def apagar_sessao(sessao_id: str):
        apagada = memoria.apagar(sessao_id)
        return {"apagada": apagada}

    # ---------------------------------------------------------------- site
    app.mount("/", StaticFiles(directory=cfg.RAIZ / "frontend", html=True), name="site")
    return app
