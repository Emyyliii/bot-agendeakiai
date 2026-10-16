"""Confere logs, contrato de saída e limites de escrita dos cenários."""

from __future__ import annotations

import json
from pathlib import Path

from .contratos import SaidaAgente


ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / "logs"
CASOS = [
    "01-caso-simples.json", "02-divergencia.json", "03-registro-inexistente.json",
    "04-sem-acao-principal.json", "05-fora-do-corpus.json", "06-aprovacao-editada.json",
    "07-incompleta.json", "08-ambigua.json", "09-fora-escopo.json", "10-aprovacao-expirada.json",
]


def _leitura(arquivo: str) -> dict:
    return json.loads((LOGS / arquivo).read_text(encoding="utf-8"))


def _escritas(log: dict) -> list[dict]:
    return [evento for evento in log.get("eventos", []) if evento.get("ferramenta") == "confirmar_agendamento"]


def _verificar() -> list[str]:
    falhas = []
    dados = {}
    for arquivo in CASOS:
        caminho = LOGS / arquivo
        if not caminho.exists():
            falhas.append(f"log ausente: {arquivo}")
            continue
        log = _leitura(arquivo)
        dados[arquivo] = log
        try:
            SaidaAgente.model_validate(log["saida_validada"])
        except Exception as erro:
            falhas.append(f"saída inválida em {arquivo}: {erro}")
        if not log.get("executado_em") or not log.get("commit_base") or not log.get("impressao_do_codigo"):
            falhas.append(f"metadados de execução incompletos: {arquivo}")

    for arquivo in ("02-divergencia.json", "03-registro-inexistente.json", "04-sem-acao-principal.json", "05-fora-do-corpus.json", "07-incompleta.json", "08-ambigua.json", "09-fora-escopo.json", "10-aprovacao-expirada.json"):
        if arquivo in dados and _escritas(dados[arquivo]):
            falhas.append(f"escrita indevida em {arquivo}")
    if "01-caso-simples.json" in dados and len(_escritas(dados["01-caso-simples.json"])) != 1:
        falhas.append("o caminho feliz precisa de uma escrita aprovada")
    if "03-registro-inexistente.json" in dados and not any(e.get("resultado", {}).get("erro", {}).get("codigo") == "CLIENTE_NAO_ENCONTRADO" for e in dados["03-registro-inexistente.json"]["eventos"]):
        falhas.append("o caso de cliente inexistente não registrou o erro esperado")
    if "05-fora-do-corpus.json" in dados and dados["05-fora-do-corpus.json"]["saida_validada"]["suficiente"]:
        falhas.append("a pergunta fora do corpus precisa de suficiência negativa")
    if "06-aprovacao-editada.json" in dados:
        log = dados["06-aprovacao-editada.json"]
        if not log.get("pausa_humana") or log.get("repeticao_idempotente", {}).get("segunda_chamada", {}).get("ja_existia") is not True:
            falhas.append("o caso editado precisa demonstrar pausa e repetição idempotente")
        elif log["repeticao_idempotente"].get("agendamentos_unicos") != 1:
            falhas.append("a repetição criou mais de um agendamento")
    if "10-aprovacao-expirada.json" in dados and not any(e.get("motivo") == "aprovacao_expirada" for e in dados["10-aprovacao-expirada.json"]["eventos"]):
        falhas.append("o caso expirado não foi rejeitado pelo prazo")
    return falhas


def main() -> int:
    falhas = _verificar()
    if falhas:
        for falha in falhas:
            print(f"FALHOU: {falha}")
        return 1
    print(f"PASSOU: {len(CASOS)} logs válidos; contrato Pydantic conferido; zero escrita sem aprovação; repetição idempotente e expiração conferidas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
