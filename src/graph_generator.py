from random import randint, random, randrange

import numpy as np
import pandas as pd

from src.graph_base import Edge, Graph, Node


class GraphGenerator:
    """
    класса для генерации послойного графа, первый слой всегда состоит из одной вершины (env), во втором слое
    layer_sizes[0] узлов, в след. слое layer_sizes[1] узлов и т.д. после layer_sizes[-1] слоя следует env
    каждый узел имеет по крайнем мере один входной и один выходной поток
    средняя свзяность графа равно average_cohesion, если это возмоно (это может быть невозможно если average_cohesion
    слишком низкая)
    """

    def __init__(self, layer_sizes=[3, 3], average_cohesion: float = None):
        self.graph = Graph(edges={}, nodes={})
        self.layer_sizes = layer_sizes
        self.average_cohesion = average_cohesion

    def build(self):
        """
        построить граф
        """
        layers_len = len(self.layer_sizes)

        nodes = {}
        edges = {}

        self.nodes_by_layers = {}

        # генерируем узлы
        nodes["env"] = Node(id="env", ind=0)
        node_ind = 1
        for layer in range(layers_len):
            self.nodes_by_layers[layer] = []

            for num in range(self.layer_sizes[layer]):
                node_name = f"{layer}:{num}"
                nodes[node_name] = Node(id=node_name, ind=node_ind)
                node_ind += 1
                self.nodes_by_layers[layer].append(node_name)

        # генерируем связи между узлами

        # Идем по узлам, каждый изел должен иметь хотя бы один входящий и хотябы один исходящий поток
        node_idx = 0
        edge_ind = 0
        for node_name, node in nodes.items():
            if node_name == "env":
                continue

            layer, num = node_name.split(":")
            layer = int(layer)

            # если нет ни одного входящего потока, добавляем его
            if not node.edges_in:
                # выбираем случайным образом узел из предыдущего слоя
                prev_layer = layer - 1 if layer > 0 else "env"

                if prev_layer != "env":
                    prev_num = randrange(self.layer_sizes[prev_layer])
                    prev_node_name = f"{prev_layer}:{prev_num}"
                else:
                    prev_node_name = "env"

                node_src = nodes[prev_node_name]
                edge_name = f"{prev_node_name} -> {node_name}"
                edge = Edge(id=edge_name, node_src=node_src, node_dst=node, ind=edge_ind)
                edge_ind += 1
                edges[edge_name] = edge
                node_src.edges_out[edge_name] = edge
                node.edges_in[edge_name] = edge

            # если нет ни одного исходящего потока, добавляем его
            if not node.edges_out:
                # выбираем случайным образом узел из следующего слоя
                next_layer = layer + 1 if layer < len(self.layer_sizes) - 1 else "env"

                if next_layer != "env":
                    next_num = randrange(self.layer_sizes[next_layer])
                    next_node_name = f"{next_layer}:{next_num}"
                else:
                    next_node_name = "env"

                node_dest = nodes[next_node_name]
                edge_name = f"{node_name} -> {next_node_name}"
                edge = Edge(id=edge_name, node_src=node, node_dst=node_dest, ind=edge_ind)
                edge_ind += 1
                edges[edge_name] = edge
                node.edges_out[edge_name] = edge
                node_dest.edges_in[edge_name] = edge

        # Удаляем некоторые потоки для снижения связности
        """edges_to_remove = []
        for edge_name, edge in edges.items():
            if (len(edge.node_src.edges_out) > 1) and (len(edge.node_dst.edges_in) > 1):
                edges_to_remove.append(edge_name)

        # Удаляем лишние потоки
        for edge_name in edges_to_remove:
            edge = edges[edge_name]
            edge.node_dst.edges_in.pop(edge_name, None)
            edge.node_src.edges_out.pop(edge_name, None)
            edges.pop(edge_name, None)
        """
        self.graph = Graph(nodes=nodes, edges=edges)

        return self.graph

    def build_train_item_connectivity_matrix_with_errors(self, ratio=0.2):
        g = self.graph

        mat = np.zeros((len(g.nodes), len(g.nodes)))

        koeffs = np.random.random(len(g.edges))
        mask = [k > (1 - ratio) for k in koeffs]

        errors = {edge.ind: 0 for edge in g.edges.values()}
        for e, m in zip(g.edges.values(), mask):
            i, j = e.node_src.ind, e.node_dst.ind
            mat[i, j] = e.value
            # mat[j, i] = -e.value

            if m:
                k = 0.5 + random()
                mat[i, j] = e.value * k
                # mat[j, i] = - e.value * k
                errors[e.ind] = e.value * (k - 1)

        return mat, errors

    def build_train_dataset(self, ln=10, errors_ratio=0.2, initial_volume=100, to_int=False):
        matrices = []
        errs = []
        for i in range(ln):
            self.fill_with_values(initial_volume=initial_volume)
            m, err = self.build_train_item_connectivity_matrix_with_errors(errors_ratio)
            matrices.append(m)
            errs.append(err)

        if to_int:
            matrices_new = []
            errs_new = []
            for m, e in zip(matrices, errs):
                m = np.int64(m)
                e = np.int64(list(e.values()))
                matrices_new.append(m)
                errs_new.append(e)

            matrices = matrices_new
            errs = errs_new

        matrices = np.array(matrices)
        errs = np.array(errs)

        return matrices, errs

    def fill_with_values(self, initial_volume=100) -> Graph:
        """
        проставить величины потоков для всех ребер графа
        запускается алгоритм волны, начиная с окружающей среды
        """

        init_flow_value = initial_volume / 2 + initial_volume / 2 * random()

        graph = self.graph

        node = graph.nodes["env"]
        koeff = [random() for i in range(len(node.edges_out))]
        sm = sum(koeff)
        for edge, k in zip(node.edges_out.values(), koeff):
            edge.value = init_flow_value * k / sm

        for layer_num in range(len(self.layer_sizes)):
            for node_name in self.nodes_by_layers[layer_num]:
                node = graph.nodes[node_name]
                koeff = [random() for i in range(len(node.edges_out))]
                sm = sum(koeff)
                inp_flow = node.input_flow()

                for edge, k in zip(node.edges_out.values(), koeff):
                    edge.value = inp_flow * k / sm

        return graph  # {edge.id: edge.value for edge in graph.edges.values()}

    def build_pivot_table(self, ln=10, ratio=0.2, initial_env_volume=100) -> pd.DataFrame:
        """
        посторить сводную таблицу для обучения НС
        """

        arr = []
        for a in range(ln):
            g = self.fill_with_values(initial_volume=initial_env_volume)

            # портим заранее определенную долю потоков
            koeffs = np.random.random(len(g.edges))
            mask = [k > (1 - ratio) for k in koeffs]
            diffs = {edge_name + "_diff": 0 for edge_name in g.edges.keys()}
            for edge, m in zip(g.edges.values(), mask):
                if m:
                    k = 0.5 + random()  # (random() * .5 + 1)
                    new_edge_value = edge.value * k
                    diffs[edge.id + "_diff"] = new_edge_value - edge.value
                    edge.value = new_edge_value

            flows = {edge.id: edge.value for edge in g.edges.values()}

            # строим датафрейм дебалансов
            debalancies = {node_name: node.debalance() for node_name, node in g.nodes.items()}  # abs(node.debalance()
            flows.update(debalancies)
            flows.update(diffs)
            arr.append(flows)

        df = pd.DataFrame(arr)

        return df
