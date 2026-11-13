"""Situações principais da conversa: normal, crise, mensagem curta, falha da IA e revisão."""
from servidor.memoria import Memoria
from servidor.pipeline import Pipeline
from servidor.textos import RESPOSTA_CRISE, RESPOSTA_RESERVA
from testes.conftest import montar_config


def eventos(pipeline, texto, sessao_id=None):
    return list(pipeline.processar(texto, sessao_id))


# ---------------------------------------------------------------- conversa normal
def test_conversa_normal_encaminha_com_tema_e_trechos(pipeline, falsas):
    r = pipeline.responder("ando muito ansioso com as provas")
    assert r["acao"] == "encaminhar"
    assert r["tema"] == {"id": "ansiedade", "nome": "Ansiedade"}
    assert r["resposta"] == falsas.resposta_ia
    assert r["trechos"][0]["fonte_url"] == "https://exemplo.org"
    assert falsas.chamadas == ["seguranca_entrada", "intencao", "tema", "conhecimento", "ia"]
    assert {e["id"] for e in r["etapas"]} == {"seguranca_entrada", "intencao", "tema",
                                              "conhecimento", "ia", "seguranca_saida"}


def test_ordem_dos_eventos(pipeline):
    tipos = [t for t, _ in eventos(pipeline, "ando muito ansioso")]
    assert tipos[0] == "analise" and tipos[-1] == "fim"
    assert set(tipos[1:-1]) == {"texto"}


def test_confianca_baixa_pede_detalhes_sem_buscar_conteudo(pipeline, falsas):
    falsas.confianca = 0.3
    r = pipeline.responder("não sei, tô estranho")
    assert r["acao"] == "pedir_detalhes"
    assert "conhecimento" not in falsas.chamadas
    assert falsas.orientacoes_recebidas[0].acao == "pedir_detalhes"


def test_memoria_lembra_a_conversa(pipeline, falsas):
    r1 = pipeline.responder("primeira mensagem")
    pipeline.responder("segunda mensagem", r1["sessao_id"])
    # o tema recebe a conversa até ali, sem a mensagem atual
    assert [m.texto for m in falsas.historicos_recebidos[1]] == ["primeira mensagem", falsas.resposta_ia]


def test_memoria_sobrevive_a_reinicio(tmp_path, falsas):
    banco = tmp_path / "persistente.db"
    p1 = Pipeline(montar_config(tmp_path), Memoria(banco), falsas.ns())
    sessao = p1.responder("oi, tudo bem?")["sessao_id"]
    p1.memoria.fechar()
    p2 = Pipeline(montar_config(tmp_path), Memoria(banco), falsas.ns())
    assert len(p2.memoria.historico(sessao)) == 2


def test_sessao_desconhecida_vira_sessao_nova(pipeline):
    r = pipeline.responder("olá", "nao-existe")
    assert r["sessao_id"] != "nao-existe"


# ---------------------------------------------------------------- crise
def test_crise_responde_texto_fixo_sem_chamar_ia(pipeline, falsas):
    r = pipeline.responder("eu quero me matar")
    assert r["acao"] == "crise"
    assert r["resposta"] == RESPOSTA_CRISE
    assert "188" in r["resposta"]
    assert falsas.chamadas == ["seguranca_entrada"]


def test_se_a_seguranca_quebrar_a_rede_minima_pega_crise_explicita(pipeline, falsas):
    def quebrada(msg, hist):
        raise RuntimeError("bug")
    pipeline.partes.seguranca.verificar_entrada = quebrada
    r = pipeline.responder("não quero mais viver")
    assert r["acao"] == "crise"
    assert next(e for e in r["etapas"] if e["id"] == "seguranca_entrada")["status"] == "falhou"


# ---------------------------------------------------------------- mensagem curta / sem tema
def test_cumprimento_nao_classifica_tema(pipeline, falsas):
    falsas.intencao_id = "cumprimentar"
    r = pipeline.responder("oi")
    assert r["acao"] == "conversa"
    assert r["tema"] is None and r["probabilidades"] == []
    assert "tema" not in falsas.chamadas


def test_pedido_de_exercicio_busca_conteudo(pipeline, falsas):
    falsas.intencao_id = "pedir_exercicio"
    falsas.confianca = 0.2
    pipeline.responder("me ensina um exercício de respiração?")
    assert "conhecimento" in falsas.chamadas


# ---------------------------------------------------------------- falha da IA
def test_ia_falha_antes_de_escrever_usa_reserva(pipeline, falsas):
    falsas.ia_falha_apos = 0
    evs = eventos(pipeline, "ando ansioso")
    textos = [d for t, d in evs if t == "texto"]
    assert textos == [RESPOSTA_RESERVA]
    fim = evs[-1][1]
    assert fim["resposta"] == RESPOSTA_RESERVA
    assert next(e for e in fim["etapas"] if e["id"] == "ia")["status"] == "falhou"


def test_ia_falha_no_meio_substitui_o_que_apareceu(pipeline, falsas):
    falsas.ia_falha_apos = 8      # depois da primeira frase
    evs = eventos(pipeline, "ando ansioso")
    tipos = [t for t, _ in evs]
    assert "texto" in tipos and "substituir" in tipos
    assert evs[-1][1]["resposta"] == RESPOSTA_RESERVA


def test_ia_que_trava_estoura_o_tempo(tmp_path, falsas):
    import time
    def lenta(historico, orientacoes, timeout_s):
        for _ in range(100):
            time.sleep(0.02)
            yield "palavra "
    p = Pipeline(montar_config(tmp_path, timeout_ia_s=0.1), Memoria(tmp_path / "t.db"), falsas.ns())
    p.partes.ia.gerar = lenta
    assert p.responder("oi")["resposta"] == RESPOSTA_RESERVA


# ---------------------------------------------------------------- revisão da resposta
def test_revisao_barra_e_nada_proibido_aparece(pipeline, falsas):
    falsas.resposta_ia = "Entendo você. Tome 50mg de remédio X. Vai passar."
    falsas.barrar_se_contiver = "remédio"
    evs = eventos(pipeline, "ando ansioso")
    mostrados = "".join(d for t, d in evs if t == "texto")
    assert "remédio" not in mostrados
    assert ("substituir", RESPOSTA_RESERVA) in evs
    assert evs[-1][1]["revisao"]["permitida"] is False


def test_revisao_recebe_texto_acumulado_e_resposta_completa(pipeline, falsas):
    pipeline.responder("ando ansioso")
    assert falsas.revisoes[-1].strip() == falsas.resposta_ia
    assert len(falsas.revisoes) >= 2


def test_revisao_que_quebra_bloqueia_a_resposta(pipeline, falsas):
    def quebrada(resp):
        raise RuntimeError("bug")
    pipeline.partes.seguranca.revisar_saida = quebrada
    assert pipeline.responder("ando ansioso")["resposta"] == RESPOSTA_RESERVA


# ---------------------------------------------------------------- perfis do experimento
def test_perfil_so_ia_nao_chama_tema_nem_conhecimento(tmp_path, falsas):
    p = Pipeline(montar_config(tmp_path, "so_ia"), Memoria(tmp_path / "t.db"), falsas.ns())
    r = p.responder("ando muito ansioso")
    assert r["acao"] == "conversa"
    assert falsas.chamadas == ["seguranca_entrada", "ia"]


def test_perfil_ia_tema_nao_busca_conteudo(tmp_path, falsas):
    p = Pipeline(montar_config(tmp_path, "ia_tema"), Memoria(tmp_path / "t.db"), falsas.ns())
    r = p.responder("ando muito ansioso")
    assert r["acao"] == "encaminhar" and r["trechos"] == []
    assert "conhecimento" not in falsas.chamadas


def test_crise_continua_detectada_no_perfil_so_ia(tmp_path, falsas):
    p = Pipeline(montar_config(tmp_path, "so_ia"), Memoria(tmp_path / "t.db"), falsas.ns())
    assert p.responder("vou me matar")["acao"] == "crise"


# ---------------------------------------------------------------- privacidade
def test_sem_guardar_conversas_nada_vai_para_o_disco(tmp_path, falsas):
    banco = tmp_path / "nao_guardar.db"
    p = Pipeline(montar_config(tmp_path), Memoria(banco, guardar=False), falsas.ns())
    r = p.responder("primeira")
    p.responder("segunda", r["sessao_id"])
    assert len(p.memoria.historico(r["sessao_id"])) == 4
    import sqlite3
    assert sqlite3.connect(banco).execute("SELECT COUNT(*) FROM mensagens").fetchone()[0] == 0
