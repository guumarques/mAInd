from pathlib import Path
import pandas as pd


# CONFIGURAÇÕES E CAMINHOS
BASE_DIR = Path(__file__).resolve().parents[1]

ARQUIVO_ENTRADA = BASE_DIR / "data" / "raw" / "dataset.csv"
PASTA_SAIDA = BASE_DIR / "data" / "processed"
ARQUIVO_SAIDA = PASTA_SAIDA / "dataset_modelo.csv"

# COLUNAS DO DATASET
COLUNAS_ESPERADAS = [
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
    "productivity_score",
    "mental_health_risk",
]

#Variáveis que serão utilizadas inicialmente pelo modelo.
#productivity_score retirada com base nos experimentos.
COLUNAS_MODELO = [
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
    "mental_health_risk",
]

COLUNAS_NUMERICAS = [
    "age",
    "stress_level",
    "sleep_hours",
    "physical_activity_days",
    "depression_score",
    "anxiety_score",
    "social_support_score",
]

CATEGORIAS_VALIDAS = {
    "gender": [
        "Male",
        "Female",
        "Non-binary",
        "Prefer not to say",
    ],
    "employment_status": [
        "Employed",
        "Student",
        "Self-employed",
        "Unemployed",
    ],
    "work_environment": [
        "On-site",
        "Remote",
        "Hybrid",
    ],
    "mental_health_history": [
        "Yes",
        "No",
    ],
    "seeks_treatment": [
        "Yes",
        "No",
    ],
    "mental_health_risk": [
        "Low",
        "Medium",
        "High",
    ],
}


# LEITURA DO DATASET
def carregar_dataset():
    """Carrega o dataset original e verifica sua estrutura."""

    if not ARQUIVO_ENTRADA.exists():
        raise FileNotFoundError(
            f"Dataset não encontrado: {ARQUIVO_ENTRADA}"
        )

    df = pd.read_csv(ARQUIVO_ENTRADA)

    print("\n========== DATASET ORIGINAL ==========")
    print(f"Registros: {df.shape[0]}")
    print(f"Colunas: {df.shape[1]}")

    colunas_faltantes = [
        coluna
        for coluna in COLUNAS_ESPERADAS
        if coluna not in df.columns
    ]

    if colunas_faltantes:
        raise ValueError(
            f"Colunas ausentes no dataset: {colunas_faltantes}"
        )

    return df


# LIMPEZA INICIAL
def limpar_dataset(df):
    """Padroniza espaços e remove registros duplicados."""

    print("\n========== LIMPEZA ==========")

    # Remove espaços extras nas colunas categóricas.
    colunas_categoricas = list(CATEGORIAS_VALIDAS.keys())

    for coluna in colunas_categoricas:
        df[coluna] = df[coluna].astype("string").str.strip()

    # Converte as variáveis numéricas.
    for coluna in COLUNAS_NUMERICAS:
        df[coluna] = pd.to_numeric(
            df[coluna],
            errors="coerce"
        )

    #Verifica valores ausentes ou inválidos.
    valores_ausentes = df[COLUNAS_ESPERADAS].isna().sum()

    print("\nValores ausentes ou inválidos:")
    print(valores_ausentes[valores_ausentes > 0])

    if df[COLUNAS_ESPERADAS].isna().any().any():
        raise ValueError(
            "Existem valores ausentes ou inválidos. "
            "Verifique o dataset antes de continuar."
        )

    #Remove duplicações exatas.
    duplicados = df.duplicated().sum()

    print(f"\nRegistros duplicados encontrados: {duplicados}")

    if duplicados > 0:
        df = df.drop_duplicates().copy()
        print(f"Registros removidos: {duplicados}")

    return df



# VALIDAÇÃO DOS DADOS
def validar_dataset(df):
    """Verifica categorias e intervalos das variáveis."""

    print("\n========== VALIDAÇÃO ==========")

    erros = []

    #Verifica categorias.
    for coluna, categorias in CATEGORIAS_VALIDAS.items():

        valores_encontrados = set(df[coluna].unique())

        valores_invalidos = valores_encontrados - set(categorias)

        if valores_invalidos:
            erros.append(
                f"{coluna}: categorias inválidas "
                f"{valores_invalidos}"
            )

    #Verifica intervalos numéricos.
    limites = {
        "age": (1, None),
        "stress_level": (1, 10),
        "sleep_hours": (0, 24),
        "physical_activity_days": (0, 7),
        "depression_score": (0, 30),
        "anxiety_score": (0, 21),
        "social_support_score": (0, 100),
        "productivity_score": (0, 100),
    }

    for coluna, (minimo, maximo) in limites.items():

        if minimo is not None:
            if (df[coluna] < minimo).any():
                erros.append(
                    f"{coluna}: existem valores abaixo de {minimo}"
                )

        if maximo is not None:
            if (df[coluna] > maximo).any():
                erros.append(
                    f"{coluna}: existem valores acima de {maximo}"
                )

    if erros:
        print("\nProblemas encontrados:")

        for erro in erros:
            print(f"- {erro}")

        raise ValueError(
            "O dataset possui inconsistências. "
            "A preparação foi interrompida."
        )

    print("Todas as verificações foram aprovadas.")


#SELEÇÃO DAS VARIÁVEIS
def selecionar_variaveis(df):
    """Seleciona as variáveis utilizadas inicialmente pelo modelo."""

    print("\n========== SELEÇÃO DE VARIÁVEIS ==========")

    df_modelo = df[COLUNAS_MODELO].copy()

    print("Variáveis utilizadas:")

    for coluna in df_modelo.columns:
        print(f"- {coluna}")

    print("\nVariável removida:")
    print("- productivity_score")

    return df_modelo



#SALVAMENTO DO DATASET PREPARADO
def salvar_dataset(df):
    """Salva o dataset preparado em data/processed."""

    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

    df.to_csv(
        ARQUIVO_SAIDA,
        index=False,
        encoding="utf-8"
    )

    print("\n========== RESULTADO FINAL ==========")
    print(f"Registros: {df.shape[0]}")
    print(f"Variáveis: {df.shape[1]}")
    print(f"Arquivo salvo em: {ARQUIVO_SAIDA}")

    print("\nDistribuição da variável alvo:")

    distribuicao = df["mental_health_risk"].value_counts()

    print(distribuicao)

    print("\nPercentual por classe:")

    print(
        (df["mental_health_risk"].value_counts(normalize=True) * 100)
        .round(2)
    )


#EXECUÇÃO PRINCIPAL
def main():

    # 1. Carrega os dados.
    df = carregar_dataset()

    # 2. Realiza a limpeza inicial.
    df = limpar_dataset(df)

    # 3. Valida os dados.
    validar_dataset(df)

    # 4. Seleciona as variáveis.
    df_modelo = selecionar_variaveis(df)

    # 5. Salva o resultado.
    salvar_dataset(df_modelo)


if __name__ == "__main__":
    main()
