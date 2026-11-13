# mAInd · bot antigo (legado)

Primeira versão do mAInd, guardada só para a **avaliação comparativa** (bot antigo × bot novo). Não faz parte do sistema novo.

Ela faz 24 perguntas de "sim" ou "não" e, no fim, um KNN (`modelo_knn.pkl`) escolhe um entre 5 rótulos (Normal, Stress, Loneliness, Depression, Anxiety) e responde com uma frase escrita à mão.

- `dataset.csv`: 40.960 linhas, mas só 5 linhas diferentes repetidas. Não serve para treinar.
- `data_to_be_cleansed.csv`: cerca de 6 mil posts do Reddit em inglês, rótulos 0 a 4 (provavelmente 0 estresse, 1 depressão, 2 bipolaridade, 3 personalidade, 4 ansiedade). É o ponto de partida dos dados do modelo de tema.

## Como rodar

```bash
cd legado
python -m venv .venv && .venv/Scripts/activate      # Linux/Mac: source .venv/bin/activate
pip install flask flask-cors numpy scikit-learn==1.5.1
python app.py                                        # http://127.0.0.1:5000
```

Rotas: `POST /mAInd/start` (devolve `user_id` e a primeira pergunta) e `POST /mAInd` com `{ "user_id": "...", "text_mensage": "sim" | "não" }`.

O `requirements.txt` desta pasta é o original e tem várias bibliotecas que o bot não usa.
