"""Confere pausa e retomada do checkpoint em processos separados."""

from __future__ import annotations

import subprocess
import sys
import time
import os
import socket
from pathlib import Path
from urllib import request

from .grafo import CHECKPOINTER

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    with socket.socket() as tomada:
        tomada.bind(("127.0.0.1", 0))
        porta = tomada.getsockname()[1]
    endereco_api = f"http://127.0.0.1:{porta}"
    ambiente = os.environ.copy()
    ambiente["API_BASE_URL"] = endereco_api
    api = subprocess.Popen([sys.executable, "-m", "src.mock_api", "--port", str(porta)], cwd=ROOT, env=ambiente, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    conversa = ""
    try:
        for _ in range(50):
            try:
                with request.urlopen(f"{endereco_api}/saude", timeout=0.2):
                    break
            except OSError:
                if api.poll() is not None:
                    print("FALHOU: a API mock terminou antes de ficar pronta")
                    return 1
                time.sleep(0.1)
        conversa = f"verificacao-retomada-{time.time_ns()}"
        base = [sys.executable, "-m", "src.main", "--cliente-id", "cliente-001", "--conversa-id", conversa]
        inicio = subprocess.run(base + ["--message", "Quero penteado clássico no Centro até R$ 150. Confirmo."], cwd=ROOT, env=ambiente, capture_output=True, text=True)
        if inicio.returncode or "motivo=aguardando_aprovacao" not in inicio.stdout:
            print(f"FALHOU ao pausar: {inicio.stderr or inicio.stdout}")
            return 1
        retomada = subprocess.run(base + ["--retomar", "aprovar"], cwd=ROOT, env=ambiente, capture_output=True, text=True)
        if retomada.returncode or "Agendamento agd-001 confirmado" not in retomada.stdout:
            print(f"FALHOU ao retomar em novo processo: {retomada.stderr or retomada.stdout}")
            return 1
        print("PASSOU: o processo inicial pausou; outro processo retomou o mesmo thread_id e concluiu a reserva mock.")
        return 0
    finally:
        api.terminate()
        api.wait(timeout=5)
        if conversa:
            CHECKPOINTER.delete_thread(conversa)


if __name__ == "__main__":
    raise SystemExit(main())
