from pathlib import Path
import pandas as pd

#CONFIGURAÇÕES
BASE_DIR = Path(__file__).resolve().parents[1]
ARQUIVO_CSV = BASE_DIR / "data" / "raw" / "dataset.csv"

COLUNA_ALVO = "mental_health_risk"

df = pd.read_csv(ARQUIVO_CSV)

#ESTATÍSTICAS POR CATEGORIA DE RISCO
print("\n========== MÉDIAS POR CATEGORIA DE RISCO ==========\n")

colunas_numericas = df.select_dtypes(
    include=["number"]
).columns

print(
    df.groupby(COLUNA_ALVO)[colunas_numericas]
    .mean()
    .round(2)
    .T
)


#DISTRIBUIÇÃO DAS VARIÁVEIS CATEGÓRICAS
print("\n========== VARIÁVEIS CATEGÓRICAS POR RISCO ==========\n")

colunas_categoricas = df.select_dtypes(
    include=["str", "object", "category"]
).columns.drop(COLUNA_ALVO, errors="ignore")

for coluna in colunas_categoricas:
    print(f"\n--- {coluna} ---")

    distribuicao = pd.crosstab(
        df[coluna],
        df[COLUNA_ALVO],
        normalize="columns"
    ) * 100

    print(distribuicao.round(2))


#CORRELAÇÃO ENTRE VARIÁVEIS NUMÉRICAS
print("\n========== CORRELAÇÃO NUMÉRICA ==========\n")

correlacao = df[colunas_numericas].corr()

print(correlacao.round(2))


#DISTRIBUIÇÃO DOS SCORES POR RISCO
print("\n========== SCORES PSICOLÓGICOS ==========\n")

scores = [
    "stress_level",
    "depression_score",
    "anxiety_score",
    "social_support_score",
    "productivity_score"
]

for coluna in scores:
    print(f"\n--- {coluna} ---")

    print(
        df.groupby(COLUNA_ALVO)[coluna]
        .agg(["min", "mean", "median", "max"])
        .round(2)
    )


#VALORES ÚNICOS DAS VARIÁVEIS
print("\n========== VALORES ÚNICOS ==========\n")

for coluna in df.columns:
    print(f"{coluna}: {df[coluna].nunique()} valores distintos")


print("\nAnálise de relações concluída!")
