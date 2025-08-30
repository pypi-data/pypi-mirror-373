import torch
from torch import nn, Tensor
from typing import Union
from itertools import zip_longest
from fmot.qat.annotated_tensors import copy_annotations


class RecursiveStateHandler(nn.Module):
    """Stub -- the QAT version is more fleshed out"""

    def forward(self, x):
        return x

    def observe(self, x):
        pass


class Loop(nn.Module):
    """Static FOR loop with a Sequencer-like interface.

    Arguments:
        n_iter (int): number of iterations for the loop
        n_recurse (int): number of recursive state variables. Their initial values will be passed
            in to .forward() inside of x_recursed_init
        slice_blocksizes (list[int]): for each sliced input, this is the slice size for each. Should
            have length equal to the number of independent sliced inputs
        slice_reversed (list[bool], optional): if any of the sliced inputs need to be sliced in reverse order,
            use this list to indicate which one. Default is `False`, indicating that all sliced variables will
            be indexed in the forward order.
        concat_reversed (list[bool], optional): similar to slice_reversed, if any of the concatenated outputs
            need to be concatenated in reverse order, use this list to indicate which ones. Default `False`.
        dim (int, optional): which dimension of the inputs corresponds to the feature dimension that will be
            iterated over. Note that this is not the sequence dimension.
    """

    def __init__(
        self,
        n_iter: int,
        n_recurse: int,
        slice_blocksizes: list[int],
        slice_reversed: Union[bool, list[bool]] = False,
        concat_reversed: Union[bool, list[bool]] = False,
        dim: int = -1,
    ):
        super().__init__()
        self.n_iter = n_iter
        self.n_recurse = n_recurse
        self.slice_blocksizes = slice_blocksizes
        if isinstance(slice_reversed, bool):
            slice_reversed = [slice_reversed] * len(self.slice_blocksizes)
        self.slice_reversed = slice_reversed
        if isinstance(concat_reversed, bool):
            concat_reversed = [concat_reversed]
        self.concat_reversed = concat_reversed
        self.dim = dim

        self.tracing = False

        self.state_handlers: list[RecursiveStateHandler] = nn.ModuleList()
        for i in range(self.n_recurse):
            self.state_handlers.append(RecursiveStateHandler())

    @torch.jit.export
    def step(
        self, x_sliced: list[Tensor], x_recursed: list[Tensor], x_scope: list[Tensor]
    ) -> tuple[list[Tensor], list[Tensor], list[Tensor]]:
        """
        Args:
            x_sliced (list[Tensor]): list of sliced inputs for the current iteration,
                of same length as `self.slice_blocksizes`
            x_recursed (list[Tensor]): list of the current values of each of the recursed variables,
                of same length as `self.n_recursed`
            x_scope (list[Tensor]): list of globally scoped activations (these will be the same at each
                iteration of the loop)

        Returns: tuple[list[Tensor], list[Tensor], list[Tensor]]
            - x_recursed (list[Tensor]): updated values for each of the recursed variables
            - y_concat_i (list[Tensor]): outputs to be concatenated
            - y_final (list[Tensor]): outputs for which only the final value will be returned from the Loop
        """
        raise NotImplementedError()

    @torch.jit.ignore
    def forward(
        self,
        x_to_slice: list[Tensor],
        x_recursed_init: list[Tensor],
        x_scope: list[Tensor],
    ) -> list[Tensor]:
        """
        Call the loop on the given inputs.

        Arguments:
            x_to_slice (list[Tensor]): inputs to slice
            x_recursed_init (list[Tensor]): initial value for each of the recursed variables
            x_scope (list[Tensor]): inputs that need to be in the loop-body's scope, but
                are not sliced and are unchanging during the loop iteration

        Returns:
            list[Tensor]: concatenated outputs first, followed by "final" outputs
        """
        assert len(x_to_slice) == len(
            self.slice_blocksizes
        ), f"{len(x_to_slice)=} {len(self.slice_blocksizes)=}"

        x_slices = [
            torch.split(x, blocksize, self.dim)
            for x, blocksize in zip(x_to_slice, self.slice_blocksizes)
        ]
        x_slices = [
            slices[::-1] if reversed else slices
            for slices, reversed in zip(x_slices, self.slice_reversed)
        ]
        y_concat: list[list[Tensor]] = []

        converted = False
        all_inputs = x_to_slice + x_recursed_init + x_scope
        if any(hasattr(x, "quantized") for x in all_inputs):
            converted = True

        x_recursed = self._initialize_recursive_state(x_recursed_init)

        for i in range(self.n_iter):
            x_sliced_i = [slices[i] for slices in x_slices]
            if converted:
                x_sliced_i = [
                    copy_annotations(x, x_s) for x, x_s in zip(x_to_slice, x_sliced_i)
                ]
            x_recursed, y_concat_i, y_final = self.step(x_sliced_i, x_recursed, x_scope)

            for j, y_c in enumerate(y_concat_i):
                if i == 0:
                    y_concat.append([y_c])
                else:
                    y_concat[j].append(y_c)

            for x, state_handler in zip(x_recursed, self.state_handlers):
                state_handler.observe(x)

        if len(self.concat_reversed) != len(y_concat):
            if len(self.concat_reversed) == 1:
                self.concat_reversed = self.concat_reversed * len(y_concat)

        y_concat_proc = []
        for i, y in enumerate(y_concat):
            if self.concat_reversed[i]:
                y = y[::-1]
            y_cat = torch.cat(y, dim=self.dim)
            if hasattr(y[0], "quantized"):
                y_cat = copy_annotations(y[0], y_cat)
            y_concat_proc.append(y_cat)

        return y_concat_proc + y_final

    def _initialize_recursive_state(self, x_recursed_init: list[Tensor]):
        x_recursed = [
            state_handler(x)
            for x, state_handler in zip(x_recursed_init, self.state_handlers)
        ]

        return x_recursed

    def _forward_trace(
        self,
        x_to_slice: list[Tensor],
        x_recursed_init: list[Tensor],
        x_scope: list[Tensor],
        slice_protos: list,
    ) -> tuple[list[Tensor], list[Tensor], list[Tensor]]:
        assert len(x_to_slice) == len(
            self.slice_blocksizes
        ), f"{len(x_to_slice)=} {len(self.slice_blocksizes)=}"
        assert len(x_to_slice) == len(slice_protos)

        x_slices = [
            torch.split(x, blocksize, self.dim)
            for x, blocksize in zip(x_to_slice, self.slice_blocksizes)
        ]
        x_slices = [
            slices[::-1] if reversed else slices
            for slices, reversed in zip(x_slices, self.slice_reversed)
        ]

        y_concat = []

        x_recursed = x_recursed_init

        # only iterate a single time when tracing
        x_sliced_i = [slices[0] for slices in x_slices]
        x_sliced_i = [
            copy_annotations(x, x_s) for x, x_s in zip(x_to_slice, x_sliced_i)
        ]
        for x_slice, proto in zip(x_sliced_i, slice_protos):
            x_slice.proto = proto

        y_recursed, y_concat, y_final = self.step(x_sliced_i, x_recursed, x_scope)

        return y_recursed, y_concat, y_final
