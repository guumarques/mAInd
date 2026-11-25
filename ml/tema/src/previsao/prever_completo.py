
from pathlib import Path

import joblib
import pandas as pd


# ============================================================
# CAMINHOS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]
MODELS_DIR = BASE_DIR / "models"

CAMINHO_DEPRESSAO = MODELS_DIR / "modelo_depressao.joblib"
CAMINHO_ANSIEDADE = MODELS_DIR / "modelo_ansiedade.joblib"
CAMINHO_CLASSIFICADOR = MODELS_DIR / "modelo_final.joblib"


# ============================================================
# FUNÇÕES DE ENTRADA
# ============================================================

def solicitar_inteiro(mensagem, minimo, maximo):
    while True:
        try:
            valor = int(input(mensagem))

            if minimo <= valor <= maximo:
                return valor

            print(f"Informe um valor entre {minimo} e {maximo}.")

        except ValueError:
            print("Digite um número inteiro válido.")


def solicitar_decimal(mensagem, minimo, maximo):
    while True:
        try:
            valor = float(input(mensagem).replace(",", "."))

            if minimo <= valor <= maximo:
                return valor

            print(f"Informe um valor entre {minimo} e {maximo}.")

        except ValueError:
            print("Digite um número válido.")


def solicitar_opcao(mensagem, opcoes):
    print(f"\n{mensagem}")

    for indice, opcao in enumerate(opcoes, start=1):
        print(f"{indice} - {opcao}")

    while True:
        escolha = solicitar_inteiro(
            "Escolha uma opção: ",
            1,
            len(opcoes),
        )

        return opcoes[escolha - 1]


# ============================================================
# COLETA DAS RESPOSTAS
# ============================================================

def coletar_respostas():
    print("\n========== QUESTIONÁRIO ==========")

    dados = {}

    # Perfil
    dados["age"] = solicitar_inteiro(
        "Idade: ", 1, 120
    )

    dados["gender"] = solicitar_opcao(
        "Gênero:",
        ["Male", "Female", "Non-binary", "Prefer not to say"],
    )

    dados["employment_status"] = solicitar_opcao(
        "Situação profissional:",
        ["Employed", "Student", "Self-employed", "Unemployed"],
    )

    dados["work_environment"] = solicitar_opcao(
        "Ambiente de trabalho:",
        ["On-site", "Remote", "Hybrid"],
    )

    dados["mental_health_history"] = solicitar_opcao(
        "Possui histórico de problemas de saúde mental?",
        ["Yes", "No"],
    )

    dados["seeks_treatment"] = solicitar_opcao(
        "Está buscando tratamento?",
        ["Yes", "No"],
    )

    # Hábitos e rotina
    dados["stress_level"] = solicitar_inteiro(
        "Nível de estresse (1 a 10): ", 1, 10
    )

    dados["sleep_hours"] = solicitar_decimal(
        "Horas de sono por dia (0 a 24): ", 0, 24
    )

    dados["physical_activity_days"] = solicitar_inteiro(
        "Dias de atividade física por semana (0 a 7): ", 0, 7
    )

    dados["social_support_score"] = solicitar_decimal(
        "Pontuação de suporte social (0 a 100): ", 0, 100
    )

    return pd.DataFrame([dados])


# ============================================================
# PREDIÇÃO
# ============================================================

def prever():
    # Carrega os três modelos.
    regressor_depressao = joblib.load(CAMINHO_DEPRESSAO)
    regressor_ansiedade = joblib.load(CAMINHO_ANSIEDADE)
    classificador = joblib.load(CAMINHO_CLASSIFICADOR)

    # Coleta os dados do usuário.
    dados = coletar_respostas()

    # Estima os escores.
    previsao_depressao = regressor_depressao["modelo"].predict(dados)[0]
    previsao_ansiedade = regressor_ansiedade["modelo"].predict(dados)[0]

    # Ajusta os valores aos intervalos válidos.
    score_depressao = round(max(0, min(30, previsao_depressao)))
    score_ansiedade = round(max(0, min(21, previsao_ansiedade)))

    # Prepara os escores para o classificador existente.
    dados_classificacao = pd.DataFrame([{
        "depression_score": score_depressao,
        "anxiety_score": score_ansiedade,
    }])

    # Classifica o risco.
    resultado = classificador["modelo"].predict(dados_classificacao)[0]

    # Exibe os resultados.
    print("\n========== RESULTADO ==========")

    print(f"Escore estimado de depressão: {score_depressao}/30")
    print(f"Escore estimado de ansiedade: {score_ansiedade}/21")

    print(f"\nClassificação de risco: {resultado}")

    print("\nEsta é uma estimativa baseada no modelo,")
    print("não um diagnóstico clínico.")


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

if __name__ == "__main__":
    prever()
