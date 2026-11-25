from pathlib import Path
import pandas as pd

# CONFIGURAÇÕES
BASE_DIR = Path(__file__).resolve().parents[1]
ARQUIVO_CSV = BASE_DIR / "data" / "raw" / "dataset.csv"

df = pd.read_csv(ARQUIVO_CSV)



#RISCO POR PONTUAÇÃO DE DEPRESSÃO
print("\n========== RISCO POR DEPRESSION SCORE ==========\n")

distribuicao = pd.crosstab(
    df["depression_score"],
    df["mental_health_risk"],
    normalize="index"
) * 100

print(distribuicao.round(1).to_string())



#PRODUTIVIDADE POR PONTUAÇÃO DE DEPRESSÃO
print("\n========== DEPRESSÃO X PRODUTIVIDADE ==========\n")

relacao = df.groupby("depression_score").agg(
    produtividade_media=("productivity_score", "mean"),
    produtividade_minima=("productivity_score", "min"),
    produtividade_maxima=("productivity_score", "max"),
    quantidade=("productivity_score", "count")
)

print(relacao.round(2).to_string())



#RISCO POR COMBINAÇÃO DE DEPRESSÃO E ANSIEDADE
print("\n========== DEPRESSÃO X ANSIEDADE X RISCO ==========\n")

df["faixa_depressao"] = pd.cut(
    df["depression_score"],
    bins=[-1, 10, 20, 30],
    labels=["Baixa", "Moderada", "Alta"]
)

df["faixa_ansiedade"] = pd.cut(
    df["anxiety_score"],
    bins=[-1, 7, 14, 21],
    labels=["Baixa", "Moderada", "Alta"]
)

combinacoes = pd.crosstab(
    [df["faixa_depressao"], df["faixa_ansiedade"]],
    df["mental_health_risk"],
    normalize="index"
) * 100

print(combinacoes.round(1).to_string())


#CORRELAÇÕES ENTRE AS VARIÁVEIS
print("\n========== CORRELAÇÕES COMPLETAS ==========\n")

colunas_numericas = df.select_dtypes(
    include=["number"]
)

correlacoes = colunas_numericas.corr()

print(correlacoes.round(3).to_string())



#INVESTIGAÇÃO DA PRODUTIVIDADE
print("\n========== DEPRESSÃO E PRODUTIVIDADE ==========\n")

df["soma_scores"] = (
    df["depression_score"] +
    df["anxiety_score"]
)

print(
    df.groupby("mental_health_risk")[
        ["depression_score", "anxiety_score",
         "soma_scores", "productivity_score"]
    ].mean().round(2)
)


print("\nInvestigação concluída!")
