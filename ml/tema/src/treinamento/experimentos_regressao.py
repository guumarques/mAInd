
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# ============================================================
# CAMINHOS E CONFIGURAÇÕES
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

ARQUIVO_DADOS = BASE_DIR / "data" / "processed" / "dataset_modelo.csv"
PASTA_RESULTADOS = BASE_DIR / "results"

RANDOM_STATE = 42

# Variáveis utilizadas para estimar os escores.
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

# Variáveis que serão previstas.
TARGETS = [
    "depression_score",
    "anxiety_score",
]


# ============================================================
# CARREGAMENTO E PREPARAÇÃO
# ============================================================

def carregar_dados():
    df = pd.read_csv(ARQUIVO_DADOS)

    colunas_necessarias = FEATURES + TARGETS

    faltantes = [
        coluna for coluna in colunas_necessarias
        if coluna not in df.columns
    ]

    if faltantes:
        raise ValueError(f"Colunas ausentes no dataset: {faltantes}")

    X = df[FEATURES].copy()

    dados = {}

    for target in TARGETS:
        y = pd.to_numeric(df[target], errors="coerce")

        if y.isna().any():
            raise ValueError(f"Valores ausentes ou inválidos em {target}.")

        dados[target] = y

    return X, dados


# ============================================================
# PRÉ-PROCESSAMENTO
# ============================================================

def criar_preprocessador():
    numericas = [
        "age",
        "stress_level",
        "sleep_hours",
        "physical_activity_days",
        "social_support_score",
    ]

    categoricas = [
        "gender",
        "employment_status",
        "work_environment",
        "mental_health_history",
        "seeks_treatment",
    ]

    pipeline_numerico = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    pipeline_categorico = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ])

    return ColumnTransformer([
        ("numericas", pipeline_numerico, numericas),
        ("categoricas", pipeline_categorico, categoricas),
    ])


# ============================================================
# MODELOS
# ============================================================

def criar_modelos():
    return {
        "Dummy Regressor": DummyRegressor(strategy="mean"),

        "Linear Regression": LinearRegression(),

        "Random Forest Regressor": RandomForestRegressor(
            n_estimators=200,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
    }


# ============================================================
# EXPERIMENTAÇÃO
# ============================================================

def executar_experimento(X, y, nome_target):
    print("\n" + "=" * 65)
    print(f"PREVISÃO DE {nome_target.upper()}")
    print("=" * 65)

    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=RANDOM_STATE,
    )

    print(f"Treinamento: {len(X_treino)} registros")
    print(f"Teste: {len(X_teste)} registros")

    cv = KFold(
        n_splits=5,
        shuffle=True,
        random_state=RANDOM_STATE,
    )

    resultados = []
    modelos = criar_modelos()

    melhor_f1 = None
    melhor_pipeline = None
    melhor_nome = None

    for nome, modelo in modelos.items():

        pipeline = Pipeline([
            ("preprocessamento", criar_preprocessador()),
            ("modelo", modelo),
        ])

        # Validação cruzada utilizando R².
        scores_cv = cross_val_score(
            pipeline,
            X_treino,
            y_treino,
            cv=cv,
            scoring="r2",
            n_jobs=-1,
        )

        # Treinamento e avaliação no conjunto de teste.
        pipeline.fit(X_treino, y_treino)

        previsoes = pipeline.predict(X_teste)

        mae = mean_absolute_error(y_teste, previsoes)

        rmse = np.sqrt(
            mean_squared_error(y_teste, previsoes)
        )

        r2 = r2_score(y_teste, previsoes)

        r2_cv = scores_cv.mean()

        resultados.append({
            "target": nome_target,
            "modelo": nome,
            "r2_cv": r2_cv,
            "desvio_cv": scores_cv.std(),
            "mae": mae,
            "rmse": rmse,
            "r2_teste": r2,
        })

        print(f"\nModelo: {nome}")
        print(f"R² CV: {r2_cv:.4f} ± {scores_cv.std():.4f}")
        print(f"MAE: {mae:.4f}")
        print(f"RMSE: {rmse:.4f}")
        print(f"R² teste: {r2:.4f}")

        if melhor_f1 is None or r2_cv > melhor_f1:
            melhor_f1 = r2_cv
            melhor_pipeline = pipeline
            melhor_nome = nome

    print("\n" + "-" * 65)
    print(f"Melhor modelo para {nome_target}: {melhor_nome}")
    print(f"R² médio na validação cruzada: {melhor_f1:.4f}")

    return resultados, melhor_nome


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

def main():
    print("=" * 65)
    print("EXPERIMENTOS DE REGRESSÃO")
    print("=" * 65)

    X, dados = carregar_dados()

    print(f"\nTotal de registros: {len(X)}")
    print(f"Variáveis de entrada: {len(FEATURES)}")

    todos_resultados = []

    for target in TARGETS:
        resultados, melhor_modelo = executar_experimento(
            X,
            dados[target],
            target,
        )

        todos_resultados.extend(resultados)

    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)

    df_resultados = pd.DataFrame(todos_resultados)

    arquivo_saida = (
        PASTA_RESULTADOS / "resultados_regressao.csv"
    )

    df_resultados.to_csv(
        arquivo_saida,
        index=False,
    )

    print("\n" + "=" * 65)
    print("RESUMO DOS EXPERIMENTOS")
    print("=" * 65)

    print(
        df_resultados.sort_values(
            ["target", "r2_cv"],
            ascending=[True, False],
        ).to_string(index=False)
    )

    print(f"\nResultados salvos em: {arquivo_saida}")


if __name__ == "__main__":
    main()
