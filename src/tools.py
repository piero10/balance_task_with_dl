import pandas as pd

from src.graph_base import Graph, Node, Edge


def build_sunkey_links(graph: Graph, remove_env_node=True):
    links = []
    for edge in graph.edges.values():
        #if remove_env_node and (edge.node_src.id == 'env' or edge.node_dst.id == 'env'):
        #    continue

        if edge.node_src.id :
            links.append(
                {
                    'Source': edge.node_src.id,
                    'Target': edge.node_dst.id if edge.node_dst.id != 'env' else '_env',
                    'Value': edge.value
                }
            )

    return pd.DataFrame(links)

