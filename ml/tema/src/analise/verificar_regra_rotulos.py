
from pathlib import Path

import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.metrics import accuracy_score, classification_report


# ============================================================
# CAMINHOS E CONFIGURAÇÕES
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = BASE_DIR / "data" / "processed" / "dataset_modelo.csv"

RANDOM_STATE = 42


# ============================================================
# CARREGAMENTO DOS DADOS
# ============================================================

df = pd.read_csv(DATA_PATH)

FEATURES = [
    "depression_score",
    "anxiety_score",
]

TARGET = "mental_health_risk"

X = df[FEATURES]
y = df[TARGET]

print("\n========== DADOS ==========")
print("Registros:", len(df))
print("Classes:", y.value_counts().to_dict())


# ============================================================
# 1. INVESTIGAÇÃO DAS COMBINAÇÕES
# ============================================================

print("\n========== COMBINAÇÕES DOS ESCORES ==========")

combinacoes = (
    df.groupby(FEATURES)[TARGET]
    .agg(
        quantidade="count",
        classes_diferentes="nunique",
        classificacoes=lambda valores: valores.value_counts().to_dict(),
    )
    .reset_index()
)

total_combinacoes = len(combinacoes)

combinacoes_deterministicas = combinacoes[
    combinacoes["classes_diferentes"] == 1
]

combinacoes_ambiguas = combinacoes[
    combinacoes["classes_diferentes"] > 1
]

print("Combinações encontradas:", total_combinacoes)
print(
    "Combinações com uma única classificação:",
    len(combinacoes_deterministicas),
)
print(
    "Combinações com classificações diferentes:",
    len(combinacoes_ambiguas),
)

if len(combinacoes_ambiguas) > 0:
    print("\nExemplos de combinações ambíguas:")
    print(combinacoes_ambiguas.head(20).to_string(index=False))

else:
    print("\nTodas as combinações produzem uma única classificação.")

taxa_deterministica = (
    combinacoes_deterministicas["quantidade"].sum() / len(df)
)

print(
    f"\nPercentual de registros em combinações determinísticas: "
    f"{taxa_deterministica * 100:.2f}%"
)


# ============================================================
# 2. TREINAMENTO DE UMA ÁRVORE SIMPLES
# ============================================================

print("\n========== ÁRVORE DE DECISÃO ==========")

X_treino, X_teste, y_treino, y_teste = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=RANDOM_STATE,
    stratify=y,
)

arvore = DecisionTreeClassifier(
    random_state=RANDOM_STATE,
    max_depth=None,
)

arvore.fit(X_treino, y_treino)

previsoes = arvore.predict(X_teste)

accuracy = accuracy_score(y_teste, previsoes)

print(f"Accuracy: {accuracy:.4f}")

print("\nRelatório de classificação:")
print(classification_report(y_teste, previsoes, zero_division=0))


# ============================================================
# 3. REGRAS APRENDIDAS PELA ÁRVORE
# ============================================================

print("\n========== REGRAS APRENDIDAS ==========")

regras = export_text(
    arvore,
    feature_names=FEATURES,
)

print(regras)


# ============================================================
# 4. ANÁLISE DA COMPLEXIDADE
# ============================================================

print("\n========== COMPLEXIDADE DA ÁRVORE ==========")

print("Profundidade:", arvore.get_depth())
print("Quantidade de folhas:", arvore.get_n_leaves())
print("Quantidade de nós:", arvore.tree_.node_count)


# ============================================================
# 5. COMPARAÇÃO COM UMA ÁRVORE LIMITADA
# ============================================================

print("\n========== ÁRVORE COM PROFUNDIDADE LIMITADA ==========")

for profundidade in [1, 2, 3, 4, 5]:
    modelo = DecisionTreeClassifier(
        max_depth=profundidade,
        random_state=RANDOM_STATE,
    )

    modelo.fit(X_treino, y_treino)

    predicoes = modelo.predict(X_teste)

    resultado = accuracy_score(y_teste, predicoes)

    print(
        f"Profundidade {profundidade}: "
        f"Accuracy = {resultado:.4f}"
    )


# ============================================================
# 6. SALVAR TABELA DE COMBINAÇÕES
# ============================================================

RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

CAMINHO_RESULTADO = (
    RESULTS_DIR / "analise_combinacoes_escores.csv"
)

combinacoes.to_csv(
    CAMINHO_RESULTADO,
    index=False,
)

print("\nTabela salva em:", CAMINHO_RESULTADO)
print("\nInvestigação concluída.")
