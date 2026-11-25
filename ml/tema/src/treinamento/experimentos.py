from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    f1_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler



#CONFIGURAÇÕES
BASE_DIR = Path(__file__).resolve().parents[1]
ARQUIVO_CSV = BASE_DIR / "data" / "raw" / "dataset.csv"

COLUNA_ALVO = "mental_health_risk"
RANDOM_STATE = 42



#CARREGAMENTO E SEPARAÇÃO DOS DADOS
df = pd.read_csv(ARQUIVO_CSV)

X = df.drop(columns=[COLUNA_ALVO])
y = df[COLUNA_ALVO]

#Separação estratificada para preservar a proporção das classes.
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=RANDOM_STATE,
    stratify=y,
)


#CENÁRIOS DE EXPERIMENTAÇÃO
cenarios = {
    "A - Todas as variáveis": [],

    "B - Sem depression e anxiety": [
        "depression_score",
        "anxiety_score",
    ],

    "C - Sem productivity": [
        "productivity_score",
    ],

    "D - Sem as três suspeitas": [
        "depression_score",
        "anxiety_score",
        "productivity_score",
    ],

    "E - Sem depression": [
        "depression_score",
    ],

    "F - Sem anxiety": [
        "anxiety_score",
    ],

    "H - Apenas depression e anxiety": [
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
        "productivity_score",
    ],
}



#PRÉ-PROCESSAMENTO
def criar_preprocessador(X_dados, escalar=False):
    # Identifica automaticamente os tipos de variáveis.
    numericas = X_dados.select_dtypes(
        include=["number"]
    ).columns.tolist()

    categoricas = X_dados.select_dtypes(
        exclude=["number"]
    ).columns.tolist()

    # Tratamento das variáveis numéricas.
    etapas_numericas = [
        ("imputer", SimpleImputer(strategy="median"))
    ]

    if escalar:
        etapas_numericas.append(
            ("scaler", StandardScaler())
        )

    pipeline_numerico = Pipeline(
        steps=etapas_numericas
    )

    # Tratamento das variáveis categóricas.
    pipeline_categorico = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", pipeline_numerico, numericas),
            ("cat", pipeline_categorico, categoricas),
        ]
    )


#MODELOS
modelos = {
    "Logistic Regression": LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=RANDOM_STATE,
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=200,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    ),
}



# BASELINE
print("\n========== BASELINE ==========")

baseline = DummyClassifier(
    strategy="most_frequent"
)

baseline.fit(X_train, y_train)

pred_baseline = baseline.predict(X_test)

print(
    "Accuracy:",
    round(accuracy_score(y_test, pred_baseline), 4),
)

print(
    "F1 Macro:",
    round(f1_score(y_test, pred_baseline, average="macro"), 4),
)

print(
    "Balanced Accuracy:",
    round(balanced_accuracy_score(y_test, pred_baseline), 4),
)



#EXPERIMENTOS
resultados = []

for nome_cenario, colunas_removidas in cenarios.items():

    print("\n" + "=" * 60)
    print(nome_cenario)
    print("=" * 60)

    X_train_cenario = X_train.drop(
        columns=colunas_removidas
    )

    X_test_cenario = X_test.drop(
        columns=colunas_removidas
    )

    for nome_modelo, modelo in modelos.items():

        escalar = nome_modelo == "Logistic Regression"

        pipeline = Pipeline(
            steps=[
                (
                    "preprocessamento",
                    criar_preprocessador(
                        X_train_cenario,
                        escalar=escalar,
                    ),
                ),
                ("modelo", modelo),
            ]
        )

        # Treinamento.
        pipeline.fit(X_train_cenario, y_train)

        # Previsões.
        previsoes = pipeline.predict(X_test_cenario)

        # Métricas.
        accuracy = accuracy_score(y_test, previsoes)
        f1_macro = f1_score(
            y_test,
            previsoes,
            average="macro",
        )
        balanced = balanced_accuracy_score(
            y_test,
            previsoes,
        )

        resultados.append(
            {
                "cenario": nome_cenario,
                "modelo": nome_modelo,
                "accuracy": accuracy,
                "f1_macro": f1_macro,
                "balanced_accuracy": balanced,
            }
        )

        print(f"\nModelo: {nome_modelo}")
        print(f"Accuracy: {accuracy:.4f}")
        print(f"F1 Macro: {f1_macro:.4f}")
        print(f"Balanced Accuracy: {balanced:.4f}")

        print("\nRelatório de classificação:")
        print(
            classification_report(
                y_test,
                previsoes,
                zero_division=0,
            )
        )



# COMPARAÇÃO FINAL
df_resultados = pd.DataFrame(resultados)

print("\n========== COMPARAÇÃO FINAL ==========")

print(
    df_resultados.sort_values(
        by="f1_macro",
        ascending=False,
    ).to_string(index=False)
)
