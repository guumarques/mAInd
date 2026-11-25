
from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# ============================================================
# CAMINHOS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = BASE_DIR / "data" / "processed" / "dataset_modelo.csv"
MODELS_DIR = BASE_DIR / "models"

MODELS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# VARIÁVEIS
# ============================================================

FEATURES = [
    "age",
    "gender",
    "employment_status",
    "work_environment",
    "mental_health_history",
    "seeks_treatment",
    "stress_level",
    "sleep_hours",
    "physical_activity_days",
    "social_support_score",
]

TARGETS = {
    "depressao": "depression_score",
    "ansiedade": "anxiety_score",
}

NUMERIC_FEATURES = [
    "age",
    "stress_level",
    "sleep_hours",
    "physical_activity_days",
    "social_support_score",
]

CATEGORICAL_FEATURES = [
    "gender",
    "employment_status",
    "work_environment",
    "mental_health_history",
    "seeks_treatment",
]


# ============================================================
# PRÉ-PROCESSAMENTO
# ============================================================

def criar_preprocessador():
    numerico = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    categorico = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ])

    return ColumnTransformer([
        ("numerico", numerico, NUMERIC_FEATURES),
        ("categorico", categorico, CATEGORICAL_FEATURES),
    ])


# ============================================================
# MODELOS CANDIDATOS
# ============================================================

def criar_modelos():
    return {
        "DummyRegressor": DummyRegressor(strategy="mean"),

        "LinearRegression": LinearRegression(),

        "RandomForestRegressor": RandomForestRegressor(
            n_estimators=200,
            random_state=42,
            n_jobs=-1,
        ),
    }


# ============================================================
# TREINAMENTO E SELEÇÃO
# ============================================================

def treinar_regressor(df, nome, target):
    X = df[FEATURES]
    y = df[target]

    validacao = KFold(
        n_splits=5,
        shuffle=True,
        random_state=42,
    )

    resultados = []

    print("\n" + "=" * 60)
    print(f"REGRESSÃO: {target}")
    print("=" * 60)

    for nome_modelo, modelo in criar_modelos().items():

        pipeline = Pipeline([
            ("preprocessamento", criar_preprocessador()),
            ("modelo", modelo),
        ])

        scores = cross_val_score(
            pipeline,
            X,
            y,
            cv=validacao,
            scoring="neg_mean_absolute_error",
            n_jobs=1,
        )

        mae_medio = -scores.mean()

        resultados.append({
            "nome": nome_modelo,
            "mae": mae_medio,
            "pipeline": pipeline,
        })

        print(f"{nome_modelo}: MAE = {mae_medio:.4f}")

    # Seleciona o modelo com menor MAE na validação cruzada.
    melhor = min(resultados, key=lambda resultado: resultado["mae"])

    # Treina o modelo selecionado com todos os dados.
    melhor_pipeline = melhor["pipeline"]
    melhor_pipeline.fit(X, y)

    # Avaliação no próprio conjunto de treinamento.
    # É apenas uma referência, não uma medida de generalização.
    previsoes = melhor_pipeline.predict(X)

    print("\nModelo selecionado:", melhor["nome"])
    print(f"MAE no conjunto completo: {mean_absolute_error(y, previsoes):.4f}")
    print(f"RMSE no conjunto completo: {mean_squared_error(y, previsoes) ** 0.5:.4f}")
    print(f"R² no conjunto completo: {r2_score(y, previsoes):.4f}")

    # Salva o pipeline e seus metadados.
    caminho = MODELS_DIR / f"modelo_{nome}.joblib"

    joblib.dump({
        "modelo": melhor_pipeline,
        "nome_modelo": melhor["nome"],
        "features": FEATURES,
        "target": target,
    }, caminho)

    print("Modelo salvo em:", caminho)

    return melhor["nome"], melhor["mae"]


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

def main():
    df = pd.read_csv(DATA_PATH)

    # Verifica se todas as colunas necessárias existem.
    colunas_necessarias = FEATURES + list(TARGETS.values())
    faltantes = [
        coluna for coluna in colunas_necessarias
        if coluna not in df.columns
    ]

    if faltantes:
        raise ValueError(f"Colunas ausentes no dataset: {faltantes}")

    print("Registros disponíveis:", len(df))

    for nome, target in TARGETS.items():
        treinar_regressor(df, nome, target)

    print("\nTreinamento dos regressores concluído.")


if __name__ == "__main__":
    main()
