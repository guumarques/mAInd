"""Liga o mAInd: `python -m servidor` (API + site em http://127.0.0.1:8000)."""
import logging

import uvicorn

from servidor.app import criar_app
from servidor.config import carregar


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    config = carregar()
    provisorias = [n for n, p in criar_app(config).state.pipeline.descrever().items() if p["provisoria"]]
    print(f"\n  mAInd · perfil '{config.perfil}' · http://127.0.0.1:{config.porta}")
    if provisorias:
        print(f"  partes ainda provisórias: {', '.join(provisorias)}")
    print()
    uvicorn.run("servidor.app:criar_app", factory=True, host="127.0.0.1", port=config.porta)


if __name__ == "__main__":
    main()
