"""Experimento comparativo: o que cada parte acrescenta ao bot.

Passa as mesmas conversas por 3 versões do sistema (a segurança fica ligada em todas):
  so_ia                 só a IA
  ia_tema               IA + modelo de tema
  ia_tema_conhecimento  IA + modelo de tema + biblioteca de conhecimento

Mede, por versão: segurança (lista de mensagens difíceis), velocidade e custo. Também gera a
planilha cega para as notas de qualidade (amostra de conversas, respostas embaralhadas).

Uso (na raiz do repositório):
  python -m experimento.rodar
  python -m experimento.rodar --conversas experimento/conversas.json --seguranca experimento/seguranca.json --amostra 10

Formatos de entrada: ver `experimento/README.md`. Saídas em `experimento/resultados/<data-hora>/`.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import statistics
import time
from datetime import datetime
from pathlib import Path

from servidor.config import PERFIS, RAIZ, Config
from servidor.memoria import Memoria
from servidor.pipeline import Pipeline, partes_padrao

VERSOES = ["so_ia", "ia_tema", "ia_tema_conhecimento"]
PASTA = RAIZ / "experimento"


def montar_pipeline(perfil: str, limiar: float) -> Pipeline:
    config = Config(perfil=perfil, partes=dict(PERFIS[perfil], seguranca=True), limiar_confianca=limiar)
    return Pipeline(config, Memoria(":memory:", guardar=False), partes_padrao())


def custo_da_ia(pipeline: Pipeline) -> float | None:
    """Se a parte da IA souber o custo da última chamada (função opcional), registra."""
    fn = getattr(pipeline.partes.ia, "custo_ultima_chamada", None)
    try:
        return float(fn()) if fn else None
    except Exception:
        return None


def rodar_conversas(conversas: list[dict], limiar: float) -> list[dict]:
    linhas = []
    for versao in VERSOES:
        p = montar_pipeline(versao, limiar)
        for conv in conversas:
            sessao = None
            for i, msg in enumerate(conv["mensagens"], 1):
                t = time.perf_counter()
                r = p.responder(msg, sessao)
                sessao = r["sessao_id"]
                linhas.append({
                    "versao": versao, "conversa": conv["id"], "tema_esperado": conv.get("tema_esperado", ""),
                    "turno": i, "mensagem": msg, "resposta": r["resposta"], "acao": r["acao"],
                    "tema": (r["tema"] or {}).get("id", ""), "confianca": r["confianca"],
                    "trechos": len(r["trechos"]), "latencia_ms": round((time.perf_counter() - t) * 1000),
                    "custo": custo_da_ia(p),
                    "falhas": ";".join(e["id"] for e in r["etapas"] if e["status"] == "falhou"),
                })
    return linhas


def rodar_seguranca(casos: list[dict], limiar: float) -> list[dict]:
    """Cada caso: {id, mensagem, esperado: "crise" | "nao_crise", categoria?}."""
    linhas = []
    for versao in VERSOES:
        p = montar_pipeline(versao, limiar)
        for caso in casos:
            r = p.responder(caso["mensagem"])
            detectou = r["acao"] == "crise"
            linhas.append({
                "versao": versao, "id": caso["id"], "categoria": caso.get("categoria", ""),
                "mensagem": caso["mensagem"], "esperado": caso["esperado"],
                "detectou_crise": detectou, "acertou": detectou == (caso["esperado"] == "crise"),
                "revisao_barrou": not r["revisao"]["permitida"], "resposta": r["resposta"],
            })
    return linhas


def resumir(conv: list[dict], seg: list[dict]) -> list[dict]:
    resumo = []
    for v in VERSOES:
        c = [l for l in conv if l["versao"] == v]
        s = [l for l in seg if l["versao"] == v]
        crises = [l for l in s if l["esperado"] == "crise"]
        nao = [l for l in s if l["esperado"] != "crise"]
        lat = [l["latencia_ms"] for l in c]
        custos = [l["custo"] for l in c if l["custo"] is not None]
        tema_ok = [l for l in c if l["tema_esperado"] and l["turno"] == 1]
        resumo.append({
            "versao": v,
            "recall_crise": f"{sum(l['detectou_crise'] for l in crises)}/{len(crises)}" if crises else "-",
            "alarmes_falsos": f"{sum(l['detectou_crise'] for l in nao)}/{len(nao)}" if nao else "-",
            "latencia_mediana_ms": round(statistics.median(lat)) if lat else "-",
            "latencia_p90_ms": round(sorted(lat)[int(0.9 * (len(lat) - 1))]) if lat else "-",
            "custo_total": round(sum(custos), 4) if custos else "-",
            "acerto_tema_1o_turno": (f"{sum(l['tema'] == l['tema_esperado'] for l in tema_ok)}/{len(tema_ok)}"
                                     if tema_ok and v != "so_ia" else "-"),
            "respostas_com_fonte": f"{sum(l['trechos'] > 0 for l in c)}/{len(c)}" if c else "-",
            "falhas": sum(bool(l["falhas"]) for l in c),
        })
    return resumo


def planilha_cega(conv: list[dict], amostra: int, semente: int) -> tuple[list[dict], list[dict]]:
    """Amostra de conversas; cada resposta ganha um código e as versões ficam embaralhadas."""
    rng = random.Random(semente)
    ids = sorted({l["conversa"] for l in conv})
    escolhidas = rng.sample(ids, min(amostra, len(ids)))
    itens, chave = [], []
    for cid in escolhidas:
        blocos = []
        for v in VERSOES:
            turnos = [l for l in conv if l["versao"] == v and l["conversa"] == cid]
            dialogo = "\n".join(f"Pessoa: {l['mensagem']}\nmAInd: {l['resposta']}" for l in turnos)
            blocos.append((v, dialogo))
        rng.shuffle(blocos)
        for v, dialogo in blocos:
            codigo = f"R{len(itens) + 1:03d}"
            itens.append({"codigo": codigo, "conversa": cid, "dialogo": dialogo,
                          "naturalidade": "", "empatia": "", "utilidade": "", "seguranca": "",
                          "adequacao_ao_tema": "", "avaliador": ""})
            chave.append({"codigo": codigo, "versao": v})
    return itens, chave


def salvar_csv(caminho: Path, linhas: list[dict]) -> None:
    if not linhas:
        return
    with caminho.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0]))
        w.writeheader()
        w.writerows(linhas)


def tabela_md(linhas: list[dict]) -> str:
    cab = list(linhas[0])
    out = ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
    out += ["| " + " | ".join(str(l[c]) for c in cab) + " |" for l in linhas]
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--conversas", type=Path, default=PASTA / "conversas_exemplo.json")
    ap.add_argument("--seguranca", type=Path, default=PASTA / "seguranca_exemplo.json")
    ap.add_argument("--amostra", type=int, default=10, help="conversas na planilha cega de notas")
    ap.add_argument("--limiar", type=float, default=0.5)
    ap.add_argument("--semente", type=int, default=42)
    args = ap.parse_args()

    conversas = json.loads(args.conversas.read_text(encoding="utf-8"))
    casos = json.loads(args.seguranca.read_text(encoding="utf-8"))
    print(f"{len(conversas)} conversas · {len(casos)} casos de segurança · {len(VERSOES)} versões")

    conv = rodar_conversas(conversas, args.limiar)
    seg = rodar_seguranca(casos, args.limiar)
    resumo = resumir(conv, seg)
    itens, chave = planilha_cega(conv, args.amostra, args.semente)

    saida = PASTA / "resultados" / datetime.now().strftime("%Y-%m-%d_%H%M%S")
    saida.mkdir(parents=True, exist_ok=True)
    salvar_csv(saida / "conversas.csv", conv)
    salvar_csv(saida / "seguranca.csv", seg)
    salvar_csv(saida / "resumo.csv", resumo)
    salvar_csv(saida / "planilha_notas_cega.csv", itens)
    salvar_csv(saida / "chave_da_planilha_NAO_ABRIR_ANTES_DAS_NOTAS.csv", chave)
    provisorias = [n for n, p in montar_pipeline("completo", args.limiar).descrever().items() if p["provisoria"]]
    aviso = f"\n> Atenção: partes provisórias nesta rodada: {', '.join(provisorias)}.\n" if provisorias else ""
    (saida / "resumo.md").write_text(
        f"# Experimento comparativo · {saida.name}\n{aviso}\n{tabela_md(resumo)}\n", encoding="utf-8")

    print(aviso)
    print(tabela_md(resumo))
    print(f"\nResultados em {saida}")


if __name__ == "__main__":
    main()
