from pathlib import Path
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    cross_val_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler



#CONFIGURAÇÕES E CAMINHOS
BASE_DIR = Path(__file__).resolve().parents[1]

ARQUIVO_DADOS = BASE_DIR / "data" / "processed" / "dataset_modelo.csv"

PASTA_MODELOS = BASE_DIR / "models"
PASTA_RESULTADOS = BASE_DIR / "results"

ARQUIVO_MODELO = PASTA_MODELOS / "modelo_final.joblib"
ARQUIVO_RESULTADOS = PASTA_RESULTADOS / "resultados_treinamento.csv"
ARQUIVO_RELATORIO = PASTA_RESULTADOS / "relatorio_classificacao.csv"
ARQUIVO_MATRIZ = PASTA_RESULTADOS / "matriz_confusao.csv"

COLUNA_ALVO = "mental_health_risk"

RANDOM_STATE = 42
TEST_SIZE = 0.20
NUM_FOLDS = 5


#CONFIGURAÇÃO DOS EXPERIMENTOS
EXPERIMENTOS = {
    "A - Completo": [
        "age",
        "gender",
        "employment_status",
        "work_environment",
        "mental_health_history",
        "seeks_treatment",
        "stress_level",
        "sleep_hours",
        "physical_activity_days",
        "depression_score",
        "anxiety_score",
        "social_support_score",
    ],

    "B - Depressão e ansiedade": [
        "depression_score",
        "anxiety_score",
    ],

    "C - Sem depressão e ansiedade": [
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
    ],
}



#CARREGAMENTO DOS DADOS
def carregar_dados():
    """Carrega o dataset preparado."""

    if not ARQUIVO_DADOS.exists():
        raise FileNotFoundError(
            f"Dataset não encontrado: {ARQUIVO_DADOS}"
        )

    df = pd.read_csv(ARQUIVO_DADOS)

    if COLUNA_ALVO not in df.columns:
        raise ValueError(
            f"Coluna alvo não encontrada: {COLUNA_ALVO}"
        )

    print("\n========== DATASET ==========")
    print(f"Registros: {len(df)}")
    print(f"Colunas: {len(df.columns)}")

    return df



#DIVISÃO ENTRE TREINO E TESTE
def dividir_dados(df):
    """Realiza divisão estratificada dos dados."""

    X = df.drop(columns=[COLUNA_ALVO])
    y = df[COLUNA_ALVO]

    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    print("\n========== DIVISÃO DOS DADOS ==========")
    print(f"Treinamento: {len(X_treino)} registros")
    print(f"Teste: {len(X_teste)} registros")

    return X_treino, X_teste, y_treino, y_teste



# CONSTRUÇÃO DO PRÉ-PROCESSAMENTO
def criar_preprocessador(colunas, normalizar):
    """Cria o pré-processamento de acordo com as variáveis."""

    colunas_numericas = [
        coluna
        for coluna in colunas
        if coluna in [
            "age",
            "stress_level",
            "sleep_hours",
            "physical_activity_days",
            "depression_score",
            "anxiety_score",
            "social_support_score",
        ]
    ]

    colunas_categoricas = [
        coluna
        for coluna in colunas
        if coluna not in colunas_numericas
    ]

    #Tratamento das variáveis numéricas.
    etapas_numericas = [
        ("imputer", SimpleImputer(strategy="median"))
    ]

    #Regressão Logística se beneficia da normalização.
    if normalizar:
        etapas_numericas.append(
            ("scaler", StandardScaler())
        )

    pipeline_numerico = Pipeline(
        steps=etapas_numericas
    )

    #Tratamento das variáveis categóricas.
    pipeline_categorico = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="most_frequent"),
            ),
            (
                "encoder",
                OneHotEncoder(handle_unknown="ignore"),
            ),
        ]
    )

    transformadores = []

    if colunas_numericas:
        transformadores.append(
            (
                "numericas",
                pipeline_numerico,
                colunas_numericas,
            )
        )

    if colunas_categoricas:
        transformadores.append(
            (
                "categoricas",
                pipeline_categorico,
                colunas_categoricas,
            )
        )

    return ColumnTransformer(
        transformers=transformadores,
        remainder="drop",
    )

#CONSTRUÇÃO DOS MODELOS
def criar_modelo(tipo_modelo, colunas):
    """Cria um pipeline completo de pré-processamento e modelo."""

    if tipo_modelo == "Random Forest":

        classificador = RandomForestClassifier(
            n_estimators=200,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )

        normalizar = False

    elif tipo_modelo == "Regressão Logística":

        classificador = LogisticRegression(
            max_iter=3000,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        )

        normalizar = True

    else:
        raise ValueError(
            f"Modelo desconhecido: {tipo_modelo}"
        )

    preprocessador = criar_preprocessador(
        colunas,
        normalizar,
    )

    return Pipeline(
        steps=[
            ("preprocessamento", preprocessador),
            ("classificador", classificador),
        ]
    )


#COMPARAÇÃO DOS EXPERIMENTOS
def comparar_modelos(X_treino, y_treino):
    """Compara as configurações usando validação cruzada."""

    print("\n========== COMPARAÇÃO DOS MODELOS ==========")

    validacao = StratifiedKFold(
        n_splits=NUM_FOLDS,
        shuffle=True,
        random_state=RANDOM_STATE,
    )

    resultados = []
    melhores_resultados = []

    for nome_experimento, colunas in EXPERIMENTOS.items():

        X_experimento = X_treino[colunas]

        print(f"\nExperimento: {nome_experimento}")
        print(f"Quantidade de variáveis: {len(colunas)}")

        for tipo_modelo in [
            "Random Forest",
            "Regressão Logística",
        ]:

            modelo = criar_modelo(
                tipo_modelo,
                colunas,
            )

            scores = cross_val_score(
                modelo,
                X_experimento,
                y_treino,
                cv=validacao,
                scoring="f1_macro",
                n_jobs=1,
            )

            media = scores.mean()
            desvio = scores.std()

            print(
                f"{tipo_modelo}: "
                f"F1 Macro = {media:.4f} "
                f"(± {desvio:.4f})"
            )

            resultado = {
                "experimento": nome_experimento,
                "modelo": tipo_modelo,
                "quantidade_variaveis": len(colunas),
                "f1_macro_medio": media,
                "f1_macro_desvio": desvio,
            }

            resultados.append(resultado)

            melhores_resultados.append(
                {
                    "resultado": resultado,
                    "colunas": colunas,
                    "tipo_modelo": tipo_modelo,
                }
            )

    resultados = sorted(
        resultados,
        key=lambda item: item["f1_macro_medio"],
        reverse=True,
    )

    melhores_resultados = sorted(
        melhores_resultados,
        key=lambda item: item["resultado"]["f1_macro_medio"],
        reverse=True,
    )

    return resultados, melhores_resultados[0]

#AVALIAÇÃO FINAL
def avaliar_modelo(
    modelo,
    X_teste,
    y_teste,
    nome_experimento,
    tipo_modelo,
):
    """Avalia o modelo escolhido no conjunto de teste."""

    previsoes = modelo.predict(X_teste)

    accuracy = accuracy_score(
        y_teste,
        previsoes,
    )

    f1 = f1_score(
        y_teste,
        previsoes,
        average="macro",
    )

    balanced = balanced_accuracy_score(
        y_teste,
        previsoes,
    )

    print("\n========== AVALIAÇÃO FINAL ==========")
    print(f"Experimento: {nome_experimento}")
    print(f"Modelo: {tipo_modelo}")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"F1 Macro: {f1:.4f}")
    print(f"Balanced Accuracy: {balanced:.4f}")

    print("\nRelatório por classe:")

    relatorio = classification_report(
        y_teste,
        previsoes,
        output_dict=True,
        zero_division=0,
    )

    print(
        classification_report(
            y_teste,
            previsoes,
            zero_division=0,
        )
    )

    classes = modelo.classes_

    matriz = confusion_matrix(
        y_teste,
        previsoes,
        labels=classes,
    )

    return (
        {
            "accuracy": accuracy,
            "f1_macro": f1,
            "balanced_accuracy": balanced,
        },
        pd.DataFrame(relatorio).transpose(),
        pd.DataFrame(
            matriz,
            index=classes,
            columns=classes,
        ),
    )


# SALVAMENTO DOS RESULTADOS
def salvar_resultados(
    resultados,
    modelo,
    nome_experimento,
    tipo_modelo,
    colunas,
    relatorio,
    matriz,
):
    """Salva os resultados e o modelo treinado."""

    PASTA_MODELOS.mkdir(
        parents=True,
        exist_ok=True,
    )

    PASTA_RESULTADOS.mkdir(
        parents=True,
        exist_ok=True,
    )

    pd.DataFrame(resultados).to_csv(
        ARQUIVO_RESULTADOS,
        index=False,
        encoding="utf-8",
    )

    relatorio.to_csv(
        ARQUIVO_RELATORIO,
        encoding="utf-8",
    )

    matriz.to_csv(
        ARQUIVO_MATRIZ,
        encoding="utf-8",
    )

    #Guarda também os nomes das variáveis utilizadas.
    artefato = {
        "modelo": modelo,
        "experimento": nome_experimento,
        "tipo_modelo": tipo_modelo,
        "colunas": colunas,
        "classes": list(modelo.classes_),
    }

    joblib.dump(
        artefato,
        ARQUIVO_MODELO,
    )

    print("\n========== ARQUIVOS SALVOS ==========")
    print(f"Modelo: {ARQUIVO_MODELO}")
    print(f"Resultados: {ARQUIVO_RESULTADOS}")
    print(f"Relatório: {ARQUIVO_RELATORIO}")
    print(f"Matriz: {ARQUIVO_MATRIZ}")



# EXECUÇÃO PRINCIPAL
def main():

    #Carregar dataset.
    df = carregar_dados()

    #Separar treino e teste.
    X_treino, X_teste, y_treino, y_teste = dividir_dados(df)

    #Comparar os seis modelos por validação cruzada.
    resultados, melhor = comparar_modelos(
        X_treino,
        y_treino,
    )

    print("\n========== RANKING DOS MODELOS ==========")

    for posicao, resultado in enumerate(resultados, start=1):
        print(
            f"{posicao}. "
            f"{resultado['experimento']} | "
            f"{resultado['modelo']} | "
            f"F1 Macro: {resultado['f1_macro_medio']:.4f}"
        )

    # 4. Recuperar a melhor configuração.
    melhor_resultado = melhor["resultado"]
    melhores_colunas = melhor["colunas"]
    melhor_tipo = melhor["tipo_modelo"]
    melhor_experimento = melhor_resultado["experimento"]

    print("\n========== MELHOR CONFIGURAÇÃO ==========")
    print(f"Experimento: {melhor_experimento}")
    print(f"Modelo: {melhor_tipo}")
    print(f"Variáveis: {melhores_colunas}")

    #Treinar a melhor configuração com todo o treino.
    modelo_final = criar_modelo(
        melhor_tipo,
        melhores_colunas,
    )

    modelo_final.fit(
        X_treino[melhores_colunas],
        y_treino,
    )

    #Avaliar uma única vez no conjunto de teste.
    metricas, relatorio, matriz = avaliar_modelo(
        modelo_final,
        X_teste[melhores_colunas],
        y_teste,
        melhor_experimento,
        melhor_tipo,
    )

    #Salvar o modelo e os resultados.
    resultados_finais = []

    for resultado in resultados:
        resultados_finais.append(resultado.copy())

    salvar_resultados(
        resultados_finais,
        modelo_final,
        melhor_experimento,
        melhor_tipo,
        melhores_colunas,
        relatorio,
        matriz,
    )


if __name__ == "__main__":
    main()
