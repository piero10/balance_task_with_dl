from src.graph_generator import GraphGenerator
from src.tools import build_sunkey_links

if __name__ == "__main__":
    gg = GraphGenerator([2, 2])
    gg.build()

    graph = gg.fill_with_values(100)
    gg.build_train_dataset(ln=2, errors_ratio=0.2, to_int=True)

    df = gg.build_pivot_table(10)

    # print(df.head())

    sunkey_diagram_links = build_sunkey_links(graph)

    # строим свертку
    # считаем максимальный ранг графа
    rank = 0
    for node in graph.nodes.values():
        rank = max(rank, len(node.edges_in), len(node.edges_out))

    # for node in graph.nodes.values():
