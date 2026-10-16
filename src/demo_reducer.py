"""Compara campo acumulado com reducer e campo concorrente sem reducer."""

from __future__ import annotations

import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


class EstadoComReducer(TypedDict, total=False):
    partes: Annotated[list[str], operator.add]


class EstadoSemReducer(TypedDict, total=False):
    valor: str


def _ramo_com_reducer_a(estado: EstadoComReducer) -> dict:
    return {"partes": ["A"]}


def _ramo_com_reducer_b(estado: EstadoComReducer) -> dict:
    return {"partes": ["B"]}


def _ramo_sem_reducer_a(estado: EstadoSemReducer) -> dict:
    return {"valor": "A"}


def _ramo_sem_reducer_b(estado: EstadoSemReducer) -> dict:
    return {"valor": "B"}


def _fim_vazio(estado: dict) -> dict:
    return {}


def demonstrar_com_reducer() -> list[str]:
    grafo = StateGraph(EstadoComReducer)
    grafo.add_node("ramo_a", _ramo_com_reducer_a)
    grafo.add_node("ramo_b", _ramo_com_reducer_b)
    grafo.add_node("fim", _fim_vazio)
    grafo.add_edge(START, "ramo_a")
    grafo.add_edge(START, "ramo_b")
    grafo.add_edge(["ramo_a", "ramo_b"], "fim")
    grafo.add_edge("fim", END)
    return grafo.compile().invoke({"partes": []})["partes"]


def demonstrar_sem_reducer() -> str:
    grafo = StateGraph(EstadoSemReducer)
    grafo.add_node("ramo_a", _ramo_sem_reducer_a)
    grafo.add_node("ramo_b", _ramo_sem_reducer_b)
    grafo.add_node("fim", _fim_vazio)
    grafo.add_edge(START, "ramo_a")
    grafo.add_edge(START, "ramo_b")
    grafo.add_edge(["ramo_a", "ramo_b"], "fim")
    grafo.add_edge("fim", END)
    try:
        resultado = grafo.compile().invoke({"valor": ""})
        return f"resultado sem reducer: {resultado['valor']}"
    except Exception as erro:
        return f"sem reducer, LangGraph rejeitou escrita concorrente: {type(erro).__name__}: {erro}"


def main() -> None:
    print(f"com reducer: {demonstrar_com_reducer()}")
    print(demonstrar_sem_reducer())


if __name__ == "__main__":
    main()
