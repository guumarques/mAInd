# Questionário mAInd — Especificação

**Versão:** 1.0

**Objetivo:** coletar informações sobre o perfil, a rotina e o bem-estar emocional do usuário para alimentar o modelo de Machine Learning do mAInd.

---

## 1. Perfil e contexto

### Q01 — Idade
- **Identificador:** `age`
- **Pergunta:** Qual é a sua idade?
- **Tipo:** Numérico
- **Coluna:** `age`
- **Validação:** aceitar números inteiros positivos.

### Q02 — Gênero
- **Identificador:** `gender`
- **Pergunta:** Como você se identifica?
- **Tipo:** Seleção única
- **Alternativas:**
  - Masculino (`Male`)
  - Feminino (`Female`)
  - Não binário (`Non-binary`)
  - Prefiro não informar (`Prefer not to say`)
- **Coluna:** `gender`

### Q03 — Situação profissional
- **Identificador:** `employment_status`
- **Pergunta:** Qual é sua situação profissional atual?
- **Tipo:** Seleção única
- **Alternativas:**
  - Empregado (`Employed`)
  - Estudante (`Student`)
  - Autônomo (`Self-employed`)
  - Desempregado (`Unemployed`)
- **Coluna:** `employment_status`

### Q04 — Ambiente de trabalho ou estudo
- **Identificador:** `work_environment`
- **Pergunta:** Como é seu ambiente de trabalho ou estudo?
- **Tipo:** Seleção única
- **Alternativas:**
  - Presencial (`On-site`)
  - Remoto (`Remote`)
  - Híbrido (`Hybrid`)
- **Coluna:** `work_environment`

### Q05 — Histórico de saúde mental
- **Identificador:** `mental_health_history`
- **Pergunta:** Você já teve algum histórico de dificuldades relacionadas à saúde mental?
- **Tipo:** Seleção única
- **Alternativas:**
  - Sim (`Yes`)
  - Não (`No`)
- **Coluna:** `mental_health_history`

### Q06 — Acompanhamento
- **Identificador:** `seeks_treatment`
- **Pergunta:** Atualmente, você procura algum tipo de acompanhamento relacionado à saúde mental?
- **Tipo:** Seleção única
- **Alternativas:**
  - Sim (`Yes`)
  - Não (`No`)
- **Coluna:** `seeks_treatment`

---

## 2. Hábitos e rotina

### Q07 — Horas de sono
- **Identificador:** `sleep_hours`
- **Pergunta:** Em média, quantas horas você dorme por noite?
- **Tipo:** Numérico
- **Coluna:** `sleep_hours`
- **Validação:** aceitar valores numéricos positivos.

### Q08 — Atividade física
- **Identificador:** `physical_activity_days`
- **Pergunta:** Em quantos dias da semana você pratica alguma atividade física?
- **Tipo:** Seleção única
- **Alternativas:** 0 a 7 dias.
- **Coluna:** `physical_activity_days`

### Q09 — Nível de estresse
- **Identificador:** `stress_level`
- **Pergunta:** Como você classificaria seu nível de estresse atualmente?
- **Tipo:** Escala numérica de 1 a 10.
- **Coluna:** `stress_level`
- **Orientação:** 1 representa o menor nível de estresse e 10 o maior.

### Q10 — Apoio social
- **Identificador:** `social_support_score`
- **Pergunta:** Quanto você sente que pode contar com amigos, familiares ou pessoas próximas?
- **Tipo:** Escala numérica de 0 a 100.
- **Coluna:** `social_support_score`
- **Orientação:** 0 representa ausência de apoio percebido e 100 representa o maior nível de apoio percebido.

---

## 3. Bem-estar emocional

As perguntas desta seção utilizam a mesma escala de frequência.

| Resposta | Valor |
|---|---:|
| Nunca | 0 |
| Em alguns dias | 1 |
| Em mais da metade dos dias | 2 |
| Quase todos os dias | 3 |

### 3.1. Perguntas relacionadas à depressão

| ID | Pergunta | Coluna |
|---|---|---|
| D01 | Você tem sentido pouco interesse ou prazer em realizar atividades? | `depression_score` |
| D02 | Você tem se sentido triste ou desanimado? | `depression_score` |
| D03 | Você tem tido dificuldades para dormir ou dormido mais do que o habitual? | `depression_score` |
| D04 | Você tem sentido cansaço ou falta de energia? | `depression_score` |
| D05 | Você tem percebido alterações no seu apetite? | `depression_score` |
| D06 | Você tem sentido dificuldade para se concentrar? | `depression_score` |
| D07 | Você tem se sentido mal consigo mesmo? | `depression_score` |
| D08 | Você tem tido dificuldade para realizar suas atividades cotidianas? | `depression_score` |
| D09 | Você tem sentido que as coisas perderam o sentido ou a graça? | `depression_score` |
| D10 | Você tem se sentido emocionalmente sobrecarregado? | `depression_score` |

**Cálculo:**

Somar os valores das dez respostas.

`depression_score = D01 + D02 + ... + D10`

- Pontuação mínima: 0.
- Pontuação máxima: 30.

### 3.2. Perguntas relacionadas à ansiedade

| ID | Pergunta | Coluna |
|---|---|---|
| A01 | Você tem se sentido nervoso ou constantemente preocupado? | `anxiety_score` |
| A02 | Você tem tido dificuldade para controlar suas preocupações? | `anxiety_score` |
| A03 | Você tem se preocupado excessivamente com diferentes situações? | `anxiety_score` |
| A04 | Você tem tido dificuldade para relaxar? | `anxiety_score` |
| A05 | Você tem se sentido inquieto ou agitado? | `anxiety_score` |
| A06 | Você tem ficado irritado ou impaciente com facilidade? | `anxiety_score` |
| A07 | Você tem sentido medo de que algo ruim possa acontecer? | `anxiety_score` |

**Cálculo:**

Somar os valores das sete respostas.

`anxiety_score = A01 + A02 + ... + A07`

- Pontuação mínima: 0.
- Pontuação máxima: 21.

---

## 4. Resumo das variáveis

| Variável | Origem |
|---|---|
| `age` | Q01 |
| `gender` | Q02 |
| `employment_status` | Q03 |
| `work_environment` | Q04 |
| `mental_health_history` | Q05 |
| `seeks_treatment` | Q06 |
| `sleep_hours` | Q07 |
| `physical_activity_days` | Q08 |
| `stress_level` | Q09 |
| `social_support_score` | Q10 |
| `depression_score` | Soma de D01 a D10 |
| `anxiety_score` | Soma de A01 a A07 |
| `productivity_score` | Não utilizado inicialmente |
| `mental_health_risk` | Resultado previsto pelo modelo |

---

## 5. Formato esperado para o modelo

Após responder ao questionário, os dados deverão ser organizados em um registro com as seguintes variáveis:

```json
{
  "age": 22,
  "gender": "Male",
  "employment_status": "Student",
  "work_environment": "On-site",
  "mental_health_history": "No",
  "seeks_treatment": "No",
  "sleep_hours": 7.5,
  "physical_activity_days": 3,
  "stress_level": 6,
  "social_support_score": 70,
  "depression_score": 12,
  "anxiety_score": 9
}
```

O exemplo é ilustrativo.

O modelo poderá receber todas essas variáveis ou somente as pontuações de depressão e ansiedade, conforme a configuração escolhida durante o treinamento.

---

## 6. Observações de implementação

1. Os identificadores das perguntas devem ser mantidos entre frontend e backend.
2. As alternativas categóricas devem ser convertidas para os mesmos valores utilizados no dataset.
3. As pontuações emocionais devem ser calculadas pela soma das respostas.
4. `productivity_score` não será solicitado ao usuário nem utilizado inicialmente.
5. `mental_health_risk` é a variável que o modelo deverá prever, portanto não deve ser solicitada no questionário.
6. As respostas devem ser organizadas em um formato único antes de serem encaminhadas ao modelo.

**Fim da especificação.**