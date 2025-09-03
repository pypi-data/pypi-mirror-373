def remove_named_dims(graph, dims=["B", "T", "H", "W"]):
    for x in graph.all_tensors():
        if x.named_dims is not None:
            _remove_dims(x, dims)


def _remove_dims(x, dims=["B", "T", "H", "W"]):
    new_named_dims = []
    new_shape = []
    for dim, size in zip(x.named_dims, x.shape):
        if dim not in dims:
            new_named_dims.append(dim)
            new_shape.append(size)
    x.shape = new_shape
    x.named_dims = new_named_dims
