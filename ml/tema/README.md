# Machine Learning — Classificação de Risco em Saúde Mental

## 1. Visão geral

Este módulo faz parte do projeto **mAInd** e tem como objetivo estudar e implementar um modelo de Machine Learning capaz de classificar o risco relacionado à saúde mental em três categorias:

- **Low:** risco baixo.
- **Medium:** risco médio.
- **High:** risco alto.

O desenvolvimento utiliza uma base de dados estruturada e experimentos com diferentes algoritmos de aprendizado de máquina.

O objetivo acadêmico é aplicar técnicas de preparação de dados, análise exploratória, treinamento, avaliação e utilização de modelos de Machine Learning.

**Importante:** o resultado produzido pelo modelo é uma classificação experimental baseada nos dados utilizados no treinamento. Não representa diagnóstico, avaliação clínica ou substituição de acompanhamento profissional.

## 2. Dataset

Foi utilizado o dataset [Mental Health — Kaggle](https://www.kaggle.com/datasets/mahdimashayekhi/mental-health).

A base original possui:

- 10.000 registros.
- 14 colunas.
- Informações demográficas, profissionais e comportamentais.
- Escores relacionados à depressão e ansiedade.
- Uma coluna de classificação de risco (`mental_health_risk`).

### Distribuição das classes

| Classificação | Registros | Percentual |
|---|---:|---:|
| Medium | 5.892 | 58,92% |
| High | 2.369 | 23,69% |
| Low | 1.739 | 17,39% |
| **Total** | **10.000** | **100%** |

A análise inicial identificou que a base não possuía valores ausentes ou registros duplicados.

## 3. Estrutura do projeto

```text
tema/
├── data/
│   ├── raw/
│   │   └── dataset.csv
│   └── processed/
│       └── dataset_modelo.csv
│
├── docs/
│   └── questionario.md
│
├── models/
│   ├── modelo_final.joblib
│   ├── modelo_depressao.joblib
│   └── modelo_ansiedade.joblib
│
├── results/
│   ├── resultados_treinamento.csv
│   ├── relatorio_classificacao.csv
│   ├── matriz_confusao.csv
│   ├── resultados_regressao.csv
│   └── analise_combinacoes_escores.csv
│
├── src/
│   ├── analise/
│   ├── treinamento/
│   └── previsao/
│
└── README.md
```

### Organização dos scripts

**Análise (`src/analise/`)**
- `analise_inicial.py`: análise geral da base de dados.
- `analise_relacoes.py`: investigação das relações entre variáveis.
- `investigar_rotulos.py`: investigação da relação entre os escores e a classificação.
- `verificar_regra_rotulos.py`: verificação das combinações de escores e da consistência dos rótulos.

**Treinamento (`src/treinamento/`)**
- `preparar_dados.py`: tratamento e validação dos dados.
- `experimentos.py`: comparação dos classificadores.
- `treinar_modelo.py`: treinamento e seleção do classificador final.
- `experimentos_regressao.py`: comparação de modelos de regressão.
- `treinar_regressores.py`: treinamento e salvamento dos modelos de regressão.

**Previsão (`src/previsao/`)**
- `prever.py`: classificação a partir dos escores de depressão e ansiedade.
- `prever_completo.py`: fluxo experimental que estima os escores a partir das demais variáveis e realiza a classificação.

## 4. Preparação dos dados

A preparação é realizada pelo script `preparar_dados.py`.

As principais etapas são:

1. Leitura do dataset original.
2. Verificação das colunas esperadas.
3. Padronização de valores categóricos.
4. Conversão de variáveis numéricas.
5. Verificação de valores ausentes.
6. Verificação de valores inválidos e duplicados.
7. Validação das categorias e dos intervalos numéricos.
8. Geração do dataset preparado para os experimentos.

O resultado é salvo em:

`data/processed/dataset_modelo.csv`

Após o processamento, a base manteve os 10.000 registros e não apresentou problemas nas validações realizadas.

## 5. Análise exploratória

Foram realizadas análises para compreender a distribuição dos dados e identificar quais variáveis apresentavam maior relação com a classificação de risco.

Entre os resultados observados:

- Os escores de depressão e ansiedade apresentam forte associação com a classificação.
- As demais variáveis apresentam relações menos expressivas com o resultado.
- A distribuição das classes apresenta desequilíbrio moderado.

Essa investigação orientou os experimentos posteriores, principalmente a comparação entre modelos que utilizavam todas as variáveis e modelos que utilizavam apenas os dois escores.

## 6. Questionário e cálculo dos escores

O projeto possui um questionário documentado em `docs/questionario.md`.

Ele contém perguntas relacionadas ao perfil, à rotina e a aspectos emocionais do respondente.

As perguntas emocionais são divididas em dois grupos:

- Depressão: 10 perguntas.
- Ansiedade: 7 perguntas.

Cada pergunta utiliza uma escala de frequência:

| Resposta | Pontuação |
|---|---:|
| Nunca | 0 |
| Alguns dias | 1 |
| Mais da metade dos dias | 2 |
| Quase todos os dias | 3 |

Os escores são calculados pela soma das respostas:

- `depression_score`: soma das 10 perguntas, com intervalo de 0 a 30.
- `anxiety_score`: soma das 7 perguntas, com intervalo de 0 a 21.

Esses dois valores são utilizados como entradas do classificador final.

## 7. Experimentos de classificação

Foram comparados dois algoritmos:

- Regressão Logística (Logistic Regression).
- Floresta Aleatória (Random Forest).

Os experimentos avaliaram diferentes conjuntos de variáveis para investigar quais informações eram mais relevantes para reproduzir a classificação existente no dataset.

### Resultados dos experimentos

| Conjunto de variáveis | Modelo | Accuracy | F1 Macro | Balanced Accuracy |
|---|---|---:|---:|---:|
| Todas as variáveis | Logistic Regression | 0,9760 | 0,9740 | 0,9864 |
| Todas as variáveis | Random Forest | 0,9650 | 0,9619 | 0,9680 |
| Sem os escores | Logistic Regression | 0,6035 | 0,6077 | 0,6932 |
| Sem os escores | Random Forest | 0,6175 | 0,6104 | 0,6631 |
| Apenas os dois escores | Logistic Regression | 0,9815 | 0,9792 | 0,9895 |
| Apenas os dois escores | Random Forest | 1,0000 | 1,0000 | 1,0000 |

Os resultados demonstraram que os escores de depressão e ansiedade concentram grande parte das informações utilizadas pelo dataset para determinar a classificação.

## 8. Treinamento do modelo final

O treinamento final é realizado por `treinar_modelo.py`.

Foram comparadas três configurações:

- **A — Completa:** utiliza todas as variáveis disponíveis para o treinamento.
- **B — Apenas escores:** utiliza `depression_score` e `anxiety_score`.
- **C — Sem escores:** utiliza as demais variáveis, excluindo os dois escores.

A avaliação utilizou:

- Separação estratificada de 80% para treinamento e 20% para teste.
- Validação cruzada estratificada com 5 divisões.
- F1 Macro como métrica principal de seleção.

### Resultados da validação cruzada

| Configuração | Modelo | F1 Macro médio |
|---|---|---:|
| A — Completa | Random Forest | 0,9516 |
| A — Completa | Logistic Regression | 0,9707 |
| B — Apenas escores | Random Forest | 1,0000 |
| B — Apenas escores | Logistic Regression | 0,9551 |
| C — Sem escores | Random Forest | 0,3248 |
| C — Sem escores | Logistic Regression | 0,3247 |

O modelo selecionado foi o **Random Forest utilizando apenas os escores de depressão e ansiedade**.

### Avaliação final

No conjunto de teste, o modelo apresentou:

| Métrica | Resultado |
|---|---:|
| Accuracy | 1,0000 |
| F1 Macro | 1,0000 |
| Balanced Accuracy | 1,0000 |

O modelo treinado foi salvo em:

`models/modelo_final.joblib`

## 9. Investigação da classificação dos dados

Como o classificador apresentou resultados perfeitos, foi realizada uma investigação adicional para compreender essa característica.

O script `verificar_regra_rotulos.py` agrupou os registros de acordo com os pares de escores de depressão e ansiedade.

Foram encontrados:

- 682 combinações diferentes.
- 682 combinações associadas a uma única classificação.
- Nenhuma combinação associada a classificações diferentes.

Considerando os intervalos inteiros dos escores (0 a 30 para depressão e 0 a 21 para ansiedade), existem exatamente 682 combinações possíveis.

Isso indica que, nesta base, cada combinação de escores determina uma única classificação de risco.

Uma Árvore de Decisão também foi treinada utilizando somente esses dois escores e alcançou 100% de Accuracy no conjunto de teste.

Portanto, os resultados elevados do Random Forest são explicados pela relação determinística existente entre os escores e os rótulos do dataset.

Esse resultado deve ser interpretado como a capacidade de reproduzir as classificações presentes na base, e não como evidência de precisão clínica ou garantia de desempenho em dados reais.

## 10. Experimentos de regressão

Também foi investigada uma abordagem alternativa: utilizar as demais variáveis do questionário para estimar os escores de depressão e ansiedade.

A proposta consistia em:

1. Receber as variáveis demográficas, profissionais e comportamentais.
2. Estimar `depression_score` e `anxiety_score`.
3. Utilizar os escores estimados como entrada do classificador final.

Foram testados:

- Dummy Regressor.
- Regressão Linear.
- Random Forest Regressor.

A avaliação utilizou validação cruzada com 5 divisões e a métrica MAE para seleção.

### Resultados

| Escore | Modelo selecionado | MAE médio na validação cruzada |
|---|---|---:|
| Depressão | Dummy Regressor | 7,7798 |
| Ansiedade | Linear Regression | 5,4724 |

Os resultados demonstraram que as demais variáveis não foram suficientes para estimar os escores com qualidade satisfatória.

Os modelos apresentaram erros relativamente elevados e valores de R² próximos de zero.

Por esse motivo, essa abordagem foi mantida como experimento adicional, não sendo adotada como fluxo principal de previsão.

Os modelos experimentais foram salvos em:

- `models/modelo_depressao.joblib`
- `models/modelo_ansiedade.joblib`

## 11. Utilização do modelo

O script principal de previsão é `prever.py`.

Ele recebe os dois escores calculados a partir do questionário e utiliza o modelo salvo para produzir uma classificação.

### Execução

A partir da pasta `ml/tema`, execute:

```bash
python src/previsao/prever.py
```

O programa solicita:

- Escore de depressão, entre 0 e 30.
- Escore de ansiedade, entre 0 e 21.

Em seguida, apresenta a classificação prevista.

O script `prever_completo.py` permite executar o fluxo experimental com estimativa dos escores a partir das demais variáveis.

## 12. Tecnologias utilizadas

- Python.
- Pandas.
- NumPy.
- Scikit-learn.
- Joblib.

## 13. Considerações finais e limitações

O desenvolvimento permitiu aplicar as principais etapas de um fluxo de Machine Learning, desde a preparação e análise dos dados até o treinamento, avaliação e utilização de modelos.

Os experimentos demonstraram que os escores de depressão e ansiedade são suficientes para reproduzir as classificações presentes no dataset utilizado.

Também foi possível identificar limitações na tentativa de estimar esses escores a partir das demais variáveis, justificando a manutenção dessa abordagem apenas como experimento.

É importante considerar que os resultados dependem diretamente das características e dos rótulos da base utilizada. O desempenho obtido não deve ser interpretado como validação clínica ou garantia de generalização para outras populações e contextos.

O módulo possui finalidade acadêmica e experimental, não devendo ser utilizado isoladamente para diagnóstico ou tomada de decisões clínicas.