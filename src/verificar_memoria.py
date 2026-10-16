"""Exercita a remoção integral usando um identificador temporário."""

from __future__ import annotations

import json
from pathlib import Path

from langgraph.checkpoint.base import empty_checkpoint

from .esquecer import remover_dados_cliente
from .grafo import CHECKPOINTER
from .memoria import carregar, registrar


ROOT = Path(__file__).resolve().parents[1]
CLIENTE_TESTE = "verificacao-remocao-local"
CONVERSA_TESTE = "verificacao-remocao-thread"
LOG_TESTE = ROOT / "logs" / "verificacao-remocao-local.json"


def main() -> int:
    registrar(CLIENTE_TESTE, "Prefiro clássico")
    registrar(CLIENTE_TESTE, "Prefiro moderno")
    if carregar()["preferencias"][CLIENTE_TESTE]["estilo"]["valor"] != "moderno":
        print("FALHOU: a preferência explícita mais recente não venceu")
        return 1
    LOG_TESTE.write_text(json.dumps({"entrada": {"cliente_id": CLIENTE_TESTE, "conversa_id": CONVERSA_TESTE}}), encoding="utf-8")
    checkpoint = empty_checkpoint()
    checkpoint["channel_values"] = {"cliente_id": CLIENTE_TESTE}
    configuracao = {"configurable": {"thread_id": CONVERSA_TESTE, "checkpoint_ns": ""}}
    CHECKPOINTER.put(configuracao, checkpoint, {"source": "input", "step": 1, "writes": {"cliente_id": CLIENTE_TESTE}}, {})

    contagem = remover_dados_cliente(CLIENTE_TESTE)
    restante = carregar()
    checkpoint_restante = any(item.config.get("configurable", {}).get("thread_id") == CONVERSA_TESTE for item in CHECKPOINTER.list(None))
    log_restante = LOG_TESTE.exists()
    cliente_restante = any(item.get("cliente_id") == CLIENTE_TESTE for item in restante["episodios"]) or CLIENTE_TESTE in restante["preferencias"]
    if checkpoint_restante or log_restante or cliente_restante:
        print("FALHOU: ainda há dados associados ao cliente temporário")
        return 1
    print(f"PASSOU: memória, preferências, checkpoint e log removidos: {contagem}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
