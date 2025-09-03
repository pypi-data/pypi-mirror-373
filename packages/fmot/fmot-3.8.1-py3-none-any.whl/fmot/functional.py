import torch


def cos_arctan(x):
    return (1 + x**2).sqrt()


def cos_tanh_pi(x):
    return torch.cos(torch.pi * torch.tanh(x))


def sin_tanh_pi(x):
    return torch.sin(torch.pi * torch.tanh(x))


def tanh_x_plus_2(x):
    return torch.tanh(x + 2)


def tag(x: torch.Tensor, varname: str) -> torch.Tensor:
    """This operation will ensure that the given variable will be tagged
    with the chosen name when traced to FQIR.

    Arguments:
        x (Tensor): tensor to apply tag to
        varname (str): name given to this tensor

    Example:

    .. code-block :: python

        import torch
        from torch import nn
        import fmot

        class MyModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.lin1 = nn.Linear(32, 32)
                self.lin2 = nn.Linear(32, 32)

            def forward(self, x):
                x = self.lin1(x)
                fmot.tag(x, "lin.1")
                x = torch.relu(x)
                fmot.tag(x, "relu.1")
                x = self.lin2(x)
                fmot.tag(x, "lin.2")
                x = torch.relu(x)
                fmot.tag(x, "relu.2")
                return x

        model = MyModel()
        cmodel = fmot.ConvertedModel(model)
        cmodel.quantize([torch.randn(32, 32) for _ in range(4)])
        graph = cmodel.trace()

        # print out the arithmetic graph:
        print(graph.subgraphs["ARITH"])

    .. code-block ::

        inputs:
            x: fqint16<32>
        parameters:
            %p.6: fqint16<32>
            %p.12: fqint16<32>
            %p.4_tpose: fqint8<32x32>
            %p.10_tpose: fqint8<32x32>
        nodes:
            lin.1: fqint16<32> = addmm(bias=%p.6, x=x, y=%p.4_tpose)
            relu.1: fqint16<32> = relu(lin.1)
            lin.2: fqint16<32> = addmm(bias=%p.12, x=relu.1, y=%p.10_tpose)
            relu.2: fqint16<32> = relu(lin.2)
        outputs:
            relu.2: fqint16<32>

    As we can see, the FQIR variable names match the ones that we gave in the :attr:`fmot.tag` function.

    .. note::

        The same tagging behavior can also be achieved via a modular API, using fmot.nn.TagVarname.

        Example:

        .. code-block:: python

            import torch
            from torch import nn
            import fmot

            class MyModel(nn.Module):
                def __init__(self):
                    super().__init__()
                    self.lin1 = nn.Linear(32, 32)
                    self.tag1 = fmot.nn.TagVarname("lin.1")
                    self.lin2 = nn.Linear(32, 32)
                    self.tag2 = fmot.nn.TagVarname("lin.2")

                def forward(self, x):
                    x = self.lin1(x)
                    self.tag1(x)
                    x = torch.relu(x)
                    x = self.lin2(x)
                    self.tag2(x)
                    x = torch.relu(x)
                    return x


    .. warning::

        If the same name is used multiple times, a number will be appended
        to ensure that named variables are unique in the FQIR graph (incremented in
        topological order).

        Example:

        .. code-block:: python

            model = nn.Sequential(
                nn.Linear(32, 32),
                TagVarname("hello"),
                nn.ReLU(),
                TagVarname("hello"),
                nn.Linear(32, 32),
                TagVarname("hello"))
            cmodel = fmot.ConvertedModel(model)
            cmodel.quantize([torch.randn(8, 32) for _ in range(4)])

            graph = cmodel.trace()
            print(graph.subgraphs["ARITH"])

        .. code-block::

            inputs:
                input: fqint16<32>
            parameters:
                %p.6: fqint16<32>
                %p.12: fqint16<32>
                %p.4_tpose: fqint8<32x32>
                %p.10_tpose: fqint8<32x32>
            nodes:
                hello.0: fqint16<32> = addmm(bias=%p.6, x=input, y=%p.4_tpose)
                hello.1: fqint16<32> = relu(hello.0)
                hello.2: fqint16<32> = addmm(bias=%p.12, x=hello.1, y=%p.10_tpose)
            outputs:
                hello.2: fqint16<32>

    """
    return x


def _apply_varname(x: torch.Tensor, varname: str) -> torch.Tensor:
    """Applies the given name to the tensor in the forward pass.
    This ensures FQIR will represent this tensor with `varname`.

    Arguments:
        x (Tensor): tensor to apply name to
        varname (str): name to give the variable

    Returns:
        Tensor, with a varname tag
    """
    x.varname = varname
    return x
