"""Remove memórias, checkpoints e logs associados a um cliente."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .grafo import CHECKPOINTER
from .memoria import carregar, salvar


ROOT = Path(__file__).resolve().parents[1]


def remover_dados_cliente(cliente_id: str) -> dict[str, int]:
    memoria = carregar()
    antes = len(memoria["episodios"])
    memoria["episodios"] = [item for item in memoria["episodios"] if item["cliente_id"] != cliente_id]
    episodios = antes - len(memoria["episodios"])
    memoria["preferencias"].pop(cliente_id, None)
    salvar(memoria)

    conversas = {
        item.config.get("configurable", {}).get("thread_id")
        for item in CHECKPOINTER.list(None)
        if item.checkpoint.get("channel_values", {}).get("cliente_id") == cliente_id
    }
    logs_removidos = 0
    for caminho in (ROOT / "logs").glob("*.json"):
        try:
            log = json.loads(caminho.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if log.get("entrada", {}).get("cliente_id") == cliente_id:
            conversa = log.get("entrada", {}).get("conversa_id")
            if conversa:
                conversas.add(conversa)
            caminho.unlink()
            logs_removidos += 1
    for conversa in conversas:
        CHECKPOINTER.delete_thread(conversa)
    return {"episodios_removidos": episodios, "checkpoints_removidos": len(conversas), "logs_removidos": logs_removidos}


def main() -> int:
    analisador = argparse.ArgumentParser(description="Apaga dados locais de um cliente fictício")
    analisador.add_argument("--cliente-id", required=True)
    analisador.add_argument("--confirmar", action="store_true", help="confirma a remoção permanente dos dados locais")
    argumentos = analisador.parse_args()
    if not argumentos.confirmar:
        analisador.error("informe --confirmar para remover memórias, checkpoints e logs")
    print(json.dumps(remover_dados_cliente(argumentos.cliente_id), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
