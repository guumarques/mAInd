from pathlib import Path
import pandas as pd

# CONFIGURAÇÕES
BASE_DIR = Path(__file__).resolve().parents[1]

ARQUIVO_CSV = BASE_DIR / "data" / "raw" / "dataset.csv"

COLUNA_ALVO = "mental_health_risk"


#IMPORTAÇÃO DOS DADOS
print("\n========== IMPORTAÇÃO DOS DADOS ==========\n")

df = pd.read_csv(ARQUIVO_CSV)

print(f"Quantidade de registros: {df.shape[0]}")
print(f"Quantidade de colunas: {df.shape[1]}")

print("\nPrimeiros registros:")
print(df.head())



#ESTRUTURA E TIPOS DE DADOS
print("\n========== ESTRUTURA ==========\n")

print(df.info())

print("\nTipos de dados:")
print(df.dtypes)


#VALORES AUSENTES
print("\n========== VALORES AUSENTES ==========\n")

valores_ausentes = df.isnull().sum()

print(valores_ausentes)

print(
    "\nTotal de valores ausentes:",
    valores_ausentes.sum()
)



#REGISTROS DUPLICADOS
print("\n========== DUPLICAÇÕES ==========\n")

print("Registros duplicados:", df.duplicated().sum())

#DISTRIBUIÇÃO DA VARIÁVEL ALVO
print("\n========== DISTRIBUIÇÃO DAS CLASSES ==========\n")

if COLUNA_ALVO in df.columns:
    print(df[COLUNA_ALVO].value_counts())

    print("\nDistribuição percentual:")
    print(
        df[COLUNA_ALVO]
        .value_counts(normalize=True)
        .mul(100)
        .round(2)
    )
else:
    print(f"Coluna {COLUNA_ALVO} não encontrada!")


#ANÁLISE DAS VARIÁVEIS NUMÉRICAS
print("\n========== VARIÁVEIS NUMÉRICAS ==========\n")

print(df.describe())



#ANÁLISE DAS VARIÁVEIS CATEGÓRICAS
print("\n========== VARIÁVEIS CATEGÓRICAS ==========\n")

colunas_categoricas = df.select_dtypes(
    include=["object", "category"]
).columns

for coluna in colunas_categoricas:
    print(f"\nColuna: {coluna}")
    print(df[coluna].value_counts(dropna=False))



#VERIFICAÇÃO FINAL
print("\n========== RESUMO FINAL ==========\n")

print("Total de registros:", len(df))
print("Total de colunas:", len(df.columns))
print("Total de duplicados:", df.duplicated().sum())
print("Total de valores ausentes:", df.isnull().sum().sum())

print("\nAnálise inicial concluída!")
