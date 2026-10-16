"""Interface de linha de comando para o agente síncrono."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

from .contratos import EntradaAgente
from .grafo import executar, saida_validada
from .tools import ApiTools


def main() -> int:
    load_dotenv(ROOT / ".env")
    os.environ.setdefault("LANGGRAPH_STRICT_MSGPACK", "true")
    parser = argparse.ArgumentParser(description="Agente de recomendação e agendamento AgendeAkiAI")
    parser.add_argument("--cliente-id", required=True)
    parser.add_argument("--conversa-id", default="conversa-local")
    parser.add_argument("--message", default="")
    parser.add_argument("--retomar", choices=("aprovar", "rejeitar"))
    parser.add_argument("--editar-opcao-id", default="")
    args = parser.parse_args()
    ferramentas = ApiTools(os.getenv("API_BASE_URL") or "http://127.0.0.1:8765", "token-mock", args.cliente_id)
    if args.retomar or args.editar_opcao_id:
        decisao = {"acao": "editar", "opcao_id": args.editar_opcao_id} if args.editar_opcao_id else args.retomar == "aprovar"
        estado = executar(EntradaAgente(texto="retomada", cliente_id=args.cliente_id, conversa_id=args.conversa_id), ferramentas, decisao)
    else:
        entrada = EntradaAgente(texto=args.message, cliente_id=args.cliente_id, conversa_id=args.conversa_id)
        estado = executar(entrada, ferramentas)
    print(json.dumps(saida_validada(estado), ensure_ascii=False, indent=2))
    print(f"[thread_id={args.conversa_id}; motivo={estado.get('motivo_terminacao', 'aguardando_aprovacao')}; passos={estado.get('passos', 0)}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
