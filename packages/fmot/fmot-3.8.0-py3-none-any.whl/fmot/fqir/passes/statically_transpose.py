from fmot import fqir
from collections import defaultdict
import numpy as np
from fmot.fqir.passes.helpers import replace_tensor_in_graph


def static_transposes(graph: fqir.GraphProto):
    arith = graph.subgraphs["ARITH"]

    _static_transposes(arith)

    for node in arith.nodes:
        if node.subgraph is not None:
            _static_transposes(node.subgraph)


def _static_transposes(graph: fqir.GraphProto):
    params2tposes = defaultdict(list)
    tpose2constructor = {}

    # find mapping between params and their transposes
    for node in graph.nodes:
        if node.opname == "transpose":
            x = node.inputs["x"]
            y = node.outputs[0]

            if x in graph.parameters:
                params2tposes[x].append(y)
                tpose2constructor[y] = node

    # statically perform transpose
    removed = set()
    for matrix, consumers in params2tposes.items():
        new_matrix = fqir.TensorProto(
            name=f"{matrix.name}_tpose",
            dtype=matrix.dtype,
            shape=[matrix.shape[1], matrix.shape[0]],
            avg_sparsity=matrix.avg_sparsity,
            value=matrix.value.T,
            quanta=matrix.quanta,
            density_per_element=matrix.density_per_element,
            named_dims=None,
        )
        graph.add_parameter(new_matrix)

        # dereference old transposed matrices
        for consumer in consumers:
            for node in graph.nodes:
                for k, v in node.inputs.items():
                    if v == consumer:
                        node.inputs[k] = new_matrix

            # remove transpose node
            constructor = tpose2constructor[consumer]
            if constructor not in removed:
                graph.nodes.remove(tpose2constructor[consumer])
            removed.add(constructor)

    # print(params2tposes)
    return graph


if __name__ == "__main__":
    import torch
    from torch import nn
    import fmot
    from fmot.fqir.passes.cleanup import remove_unused_params

    class MyModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.stack = nn.Sequential(nn.Linear(32, 64), nn.ReLU(), nn.Linear(64, 32))

        def forward(self, x):
            x = self.stack(x)
            x = self.stack(x)
            return x

    model = MyModel()
    model = fmot.ConvertedModel(model)
    model.quantize([torch.randn(8, 32) for _ in range(4)])
    graph = model.trace()

    print(graph.subgraphs["ARITH"])
    print()
    graph = static_transposes(graph)
    remove_unused_params(graph)
    print()
    print(graph.subgraphs["ARITH"])

    x = np.random.randn(32)
    print(graph.run(x))
