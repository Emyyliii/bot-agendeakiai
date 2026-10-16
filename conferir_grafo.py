"""Mostra nós e arestas do grafo importado pelo agente."""

from src.grafo import GRAFO


def main() -> None:
    estrutura = GRAFO.get_graph()
    print("Nós:")
    for nome in sorted(estrutura.nodes):
        print(f"- {nome}")
    print("Arestas:")
    for aresta in sorted(estrutura.edges, key=lambda item: (item.source, item.target)):
        marca = " [condicional]" if aresta.conditional else ""
        print(f"- {aresta.source} -> {aresta.target}{marca}")


if __name__ == "__main__":
    main()
