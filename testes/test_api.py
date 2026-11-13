"""Rotas HTTP: formato das respostas, resposta aos poucos, apagar conversa e erros."""
import json


def ler_sse(resposta_bruta: str) -> list[tuple[str, object]]:
    eventos = []
    for bloco in resposta_bruta.strip().split("\n\n"):
        linhas = dict(l.split(": ", 1) for l in bloco.splitlines())
        eventos.append((linhas["event"], json.loads(linhas["data"])))
    return eventos


def test_saude(cliente):
    r = cliente.get("/api/saude").json()
    assert r["status"] == "ok"
    assert r["modelo"]["limiar_confianca"] == 0.5
    assert set(r["partes"]) == {"seguranca_entrada", "intencao", "tema", "conhecimento", "ia", "seguranca_saida"}


def test_mensagem_no_formato_que_o_site_espera(cliente):
    r = cliente.post("/api/mensagem", json={"texto": "ando muito ansioso"}).json()
    for campo in ("sessao_id", "resposta", "acao", "tema", "confianca", "limiar", "probabilidades", "latencia_ms"):
        assert campo in r
    assert {"id", "nome", "p"} <= set(r["probabilidades"][0])


def test_stream(cliente, falsas):
    with cliente.stream("POST", "/api/mensagem/stream", json={"texto": "ando muito ansioso"}) as s:
        assert s.headers["content-type"].startswith("text/event-stream")
        evs = ler_sse(s.read().decode())
    assert evs[0][0] == "analise" and evs[-1][0] == "fim"
    assert "".join(d for t, d in evs if t == "texto").strip() == falsas.resposta_ia


def test_apagar_conversa(cliente):
    sessao = cliente.post("/api/mensagem", json={"texto": "oi"}).json()["sessao_id"]
    assert len(cliente.get(f"/api/sessao/{sessao}").json()["mensagens"]) == 2
    assert cliente.delete(f"/api/sessao/{sessao}").json() == {"apagada": True}
    assert cliente.get(f"/api/sessao/{sessao}").status_code == 404


def test_mensagem_vazia_tem_erro_compreensivel(cliente):
    r = cliente.post("/api/mensagem", json={"texto": "   "})
    assert r.status_code == 422
    assert r.json() == {"erro": "Escreva alguma coisa antes de enviar."}


def test_mensagem_longa_demais(cliente):
    r = cliente.post("/api/mensagem", json={"texto": "a" * 2001})
    assert r.status_code == 422 and "longa demais" in r.json()["erro"]


def test_site_e_servido(cliente):
    assert cliente.get("/").status_code == 200
    assert cliente.get("/chat.html").status_code == 200
