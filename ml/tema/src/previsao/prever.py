from pathlib import Path
import joblib
import pandas as pd


#CAMINHOS E CARREGAMENTO DO MODELO
BASE_DIR = Path(__file__).resolve().parents[1]
ARQUIVO_MODELO = BASE_DIR / "models" / "modelo_final.joblib"

if not ARQUIVO_MODELO.exists():
    raise FileNotFoundError(
        f"Modelo não encontrado: {ARQUIVO_MODELO}"
    )

#Carrega o artefato salvo durante o treinamento
artefato = joblib.load(ARQUIVO_MODELO)

modelo = artefato["modelo"]
colunas = artefato["colunas"]


#FUNÇÃO DE PREDIÇÃO
def prever_risco(depression_score: int, anxiety_score: int) -> str:
    """
    Recebe os escores de depressão e ansiedade e retorna
    a classe prevista pelo modelo: Low, Medium ou High.
    """

    # Validação dos valores recebidos
    if not isinstance(depression_score, int) or isinstance(depression_score, bool):
        raise ValueError("depression_score deve ser um número inteiro.")

    if not isinstance(anxiety_score, int) or isinstance(anxiety_score, bool):
        raise ValueError("anxiety_score deve ser um número inteiro.")

    if not 0 <= depression_score <= 30:
        raise ValueError("depression_score deve estar entre 0 e 30.")

    if not 0 <= anxiety_score <= 21:
        raise ValueError("anxiety_score deve estar entre 0 e 21.")

    #Organiza os dados no formato esperado pelo modelo
    entrada = pd.DataFrame(
        [{
            "depression_score": depression_score,
            "anxiety_score": anxiety_score
        }],
        columns=colunas
    )

    #Realiza a previsão
    resultado = modelo.predict(entrada)[0]

    return str(resultado)



# EXECUÇÃO MANUAL PELO TERMINAL
if __name__ == "__main__":

    print("===================================")
    print("       PREVISÃO DE RISCO")
    print("===================================")

    try:
        depression = int(input("Escore de depressão (0 a 30): "))
        anxiety = int(input("Escore de ansiedade (0 a 21): "))

        resultado = prever_risco(depression, anxiety)

        print("\nResultado da previsão:")
        print(f"Classificação: {resultado}")

    except ValueError as erro:
        print(f"\nErro: {erro}")
