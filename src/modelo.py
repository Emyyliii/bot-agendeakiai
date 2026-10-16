"""Chamada opcional ao Mistral para redigir a resposta final."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from .contratos import SaidaAgente


ROOT = Path(__file__).resolve().parents[1]
MAX_CUSTO_USD = 0.01
MAX_TOKENS_TOTAIS = 4000


def responder_com_mistral(texto: str, resposta_base: str, fontes: list[str], suficiente: bool) -> tuple[dict[str, Any], dict[str, int]]:
    load_dotenv(ROOT / ".env")
    chave = os.getenv("OPENAI_API_KEY", "")
    if not chave:
        raise ValueError("Defina OPENAI_API_KEY no .env para usar o modo Mistral.")
    prompt = (ROOT / "src" / "prompts" / "agente-v1.txt").read_text(encoding="utf-8")
    pedido = json.dumps({"pedido": texto, "resposta_verificada": resposta_base, "fontes": fontes, "suficiente": suficiente}, ensure_ascii=False)
    # Cada token consome pelo menos um byte; os bytes dão um teto conservador antes da chamada.
    entrada_estimada = len(prompt.encode("utf-8")) + len(pedido.encode("utf-8")) + 100
    entrada_usd = os.getenv("LLM_CUSTO_USD_POR_MILHAO_ENTRADA", "")
    saida_usd = os.getenv("LLM_CUSTO_USD_POR_MILHAO_SAIDA", "")
    if not entrada_usd or not saida_usd:
        raise ValueError("Informe os custos atuais por milhão de tokens antes de habilitar o modo Mistral.")
    taxa_entrada = float(entrada_usd)
    taxa_saida = float(saida_usd)
    custo_estimado = (entrada_estimada * taxa_entrada + 400 * taxa_saida) / 1_000_000
    if entrada_estimada + 400 > MAX_TOKENS_TOTAIS or custo_estimado > MAX_CUSTO_USD:
        raise ValueError("A chamada Mistral excederia o limite local de tokens ou de US$ 0,01.")
    cliente = OpenAI(base_url=os.getenv("LLM_BASE_URL") or "https://api.mistral.ai/v1", api_key=chave, timeout=10)
    resposta = cliente.chat.completions.create(
        model=os.getenv("LLM_MODELO") or "mistral-small-2603",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": pedido},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
        max_tokens=400,
    )
    conteudo = resposta.choices[0].message.content or "{}"
    objeto = SaidaAgente.model_validate(json.loads(conteudo)).model_dump()
    uso = resposta.usage
    tokens_entrada = uso.prompt_tokens if uso else 0
    tokens_saida = uso.completion_tokens if uso else 0
    custo_usd = (tokens_entrada * taxa_entrada + tokens_saida * taxa_saida) / 1_000_000
    return objeto, {"tokens_entrada": tokens_entrada, "tokens_saida": tokens_saida, "custo_usd": custo_usd}
