import torch
import math
import warnings
from torch import Tensor, nn
from typing import List, Tuple, Optional
from torch.jit import Final
from fmot.qat import annotated_tensors as anno
from fmot.qat.control import cache_parameters, decache_parameters


def unbind(x, dim):
    y = torch.unbind(x, dim)
    if not hasattr(x, "annotated"):
        return y
    else:
        unbind_x = []
        for yy in y:
            z = anno.copy_annotations(x, yy)
            try:
                dimensions = list(x.dimensions)
                dimensions.pop(dim)
                anno.set_dim_annotations(dimensions, z)
            except:
                warnings.warn(
                    "Input dimensions are missing: "
                    + "dimension information has not been propagated correctly"
                )
            unbind_x.append(z)
        return unbind_x


def cat(x, dim):
    x0 = x[0]
    y = torch.cat(x, dim)
    if not hasattr(x[0], "annotated"):
        return y
    else:
        return anno.copy_annotations(x0, y)


def stack(x, dim):
    x0 = x[0]
    y = torch.stack(x, dim)
    if not hasattr(x[0], "annotated"):
        return y
    else:
        z = anno.copy_annotations(x0, y)
        try:
            if dim < 0:
                insert_dim = len(x0.dimensions) + dim + 1
            else:
                insert_dim = dim
            z.dimensions.insert(insert_dim, "T")
        except:
            warnings.warn(
                "Input dimensions are missing: "
                + "dimension information has not been propagated correctly"
            )
        return z


def chunk(x, chunks, dim):
    y = torch.chunk(x, chunks, dim)
    if not hasattr(x, "annotated"):
        return y
    else:
        return [anno.copy_annotations(x, yy) for yy in y]


class StateInitializer(nn.Module):
    def __init__(self, state_shapes, batch_dim):
        super().__init__()
        self.state_shapes = state_shapes
        self.batch_dim = batch_dim

        self.p_inherit = 0
        self._n_state = None

    @torch.jit.ignore
    def store_state(self, state: List[Tensor]):
        for i, x in enumerate(state):
            self.register_buffer(f"_prev_state_{i}", x.detach(), persistent=False)
        self._n_state = len(state)

    @torch.jit.ignore
    def inherit_state(self, batch_size: int, p_inherit: float) -> List[Tensor]:
        state = []
        mask = None

        for i in range(self._n_state):
            x_prev = getattr(self, f"_prev_state_{i}", None)
            if x_prev is None:
                return None
            else:
                # transpose x_prev to put batch_dim first
                if self.batch_dim != 0:
                    x_prev = x_prev.transpose(0, self.batch_dim)

                batch_size_prev = x_prev.shape[0]

                if mask is None:
                    # create an inheritance mask (only on the first state-variable)
                    mask = (
                        torch.rand(batch_size_prev, device=x_prev.device) >= p_inherit
                    )
                    # broadcast mask to x_prev's shape
                    mask = mask.unsqueeze(-1)
                    x_prev = torch.masked_fill(x_prev, mask, 0)

                # trim / pad to new batch size
                if batch_size_prev > batch_size:
                    x_prev = x_prev[:batch_size]
                elif batch_size_prev < batch_size:
                    zeros = torch.zeros(
                        (batch_size - batch_size_prev, x_prev.shape[1]),
                        device=x_prev.device,
                    )
                    x_prev = torch.cat([x_prev, zeros], 0)

                # don't undo the transpose -- we want batch-dim to be first!

                state.append(x_prev)

        return state

    @torch.jit.ignore
    def forward(self, x) -> List[Tensor]:
        batch_size = x.shape[self.batch_dim]
        if self.p_inherit > 0 and self._n_state is not None:
            state = self.inherit_state(batch_size, self.p_inherit)
            if state is not None:
                return state
        return [
            torch.zeros(batch_size, *shape, device=x.device)
            for shape in self.state_shapes
        ]

    @torch.jit.ignore
    def observe_state(self, state):
        pass

    @torch.jit.ignore
    def quantize_state(self, state):
        return state


class Sequencer(nn.Module):
    state: Final[Optional[List[Tensor]]]

    def __init__(self, state_shapes, batch_dim=0, seq_dim=1, return_hidden_state=True):
        super().__init__()
        self.seq_dim = seq_dim
        self.batch_dim = batch_dim
        self.state_initializer = StateInitializer(state_shapes, batch_dim)
        self.state_shapes = state_shapes
        self._streaming = False
        self.return_hidden_state = return_hidden_state
        self.state = None
        self.is_mimo = False

    @torch.jit.ignore
    def get_init_state(self, x) -> List[Tensor]:
        return self.state_initializer(x)

    def forward(
        self, x: Tensor, state: Optional[List[Tensor]] = None
    ) -> Tuple[Tensor, List[Tensor]]:
        if self._streaming:
            return self._forward_streaming_internal_state(x)
        else:
            if state is None:
                state = self.get_init_state(x)
            return self._forward_training(x, state)

    @torch.jit.ignore
    def _forward_training(
        self, x: Tensor, state: List[Tensor]
    ) -> Tuple[Tensor, List[Tensor]]:
        """
        Optionally overwrite this with base looped equation
        """
        cache_parameters(self)
        output = []
        for x_t in unbind(x, self.seq_dim):
            out, state = self.step(x_t, state)
            self.state_initializer.observe_state(state)
            state = self.state_initializer.quantize_state(state)
            output.append(out)
        decache_parameters(self)

        # cache the final hidden state
        self.state_initializer.store_state(state)

        if self.return_hidden_state:
            return stack(output, self.seq_dim), state
        else:
            # Rk: in this case signature is Tensor, but Union is not supported
            return stack(output, self.seq_dim)

    @torch.jit.ignore
    def _forward_streaming_internal_state(self, x) -> Tuple[Tensor, List[Tensor]]:
        if self.state == None:
            self.batch_dim = 0
            self.state = self.get_init_state(x)
        self.prev_state = self.state
        out, self.state = self.step(x, self.state)
        self.state = self.state_initializer.quantize_state(self.state)
        if self.return_hidden_state:
            return out, self.state
        else:
            return out

    def step(self, x_t: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        """
        Overwrite this with base update equation. Annotations are required (for now)...
        """
        raise NotImplementedError

    def set_streaming(self, stream=True):
        if stream:
            self._streaming = True
        else:
            self._streaming = False
            self.state = None
            self.prev_state = None


class MIMOSequencer(Sequencer):
    """A superset of the features of Sequencer (which is SISO), but extending to the case
    where a recurrent or sequential operation ingests and/or produces multiple sequences.

    Among the many use-cases, this will enable definition of sequencers that operate on virtual i31
    variables.
    """

    def __init__(
        self,
        num_inputs: int,
        num_outputs: int,
        state_shapes,
        batch_dim=0,
        seq_dim=1,
        return_hidden_state=True,
    ):
        super().__init__(state_shapes, batch_dim, seq_dim, return_hidden_state)
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        self.is_mimo = True

    def forward(
        self, inputs: List[Tensor], state: Optional[List[Tensor]] = None
    ) -> Tuple[List[Tensor], List[Tensor]]:
        """
        Arguments:
            inputs (list[Tensor]): a list of input sequence tensors, each of shape (batch, time, feature) if seq_dim = 1
                or (batch, feature, time) if seq_dim = 2
            state (list[Tensor], optional): a list of initial hidden-state variables, default None

        Returns:
            list[Tensor], list[Tensor]
            The first output tensor list is a list of the model's multiple sequential outputs
            The second output tensor list contains the final hidden-state values for all of the internal buffers
        """
        if self._streaming:
            return self._forward_streaming_internal_state(inputs)
        else:
            if state is None:
                state = self.get_init_state(inputs[0])
            return self._forward_training(inputs, state)

    @torch.jit.ignore
    def _forward_training(
        self, inputs: List[Tensor], state: List[Tensor]
    ) -> Tuple[List[Tensor], List[Tensor]]:
        """
        Optionally overwrite this with base looped equation
        """
        cache_parameters(self)
        # list of lists: outer list will iterate over num_outputs, inner lists over the number of time-steps
        outputs = [[] for _ in range(self.num_outputs)]

        ub_inputs = [unbind(x, self.seq_dim) for x in inputs]

        for xs in zip(*ub_inputs):
            out, state = self.step(list(xs), state)
            self.state_initializer.observe_state(state)
            state = self.state_initializer.quantize_state(state)
            for i, y in enumerate(out):
                outputs[i].append(y)

        decache_parameters(self)

        # cache the final hidden state
        self.state_initializer.store_state(state)

        # create mimo output stacks
        outputs = [stack(x, self.seq_dim) for x in outputs]

        if self.return_hidden_state:
            return outputs, state
        else:
            raise NotImplementedError("return_hidden_state=False not implemented")

    @torch.jit.ignore
    def _forward_streaming_internal_state(
        self, inputs: List[Tensor]
    ) -> Tuple[List[Tensor], List[Tensor]]:
        if self.state == None:
            self.batch_dim = 0
            self.state = self.get_init_state(inputs[0])
        self.prev_state = self.state
        out, self.state = self.step(inputs, self.state)
        self.state = self.state_initializer.quantize_state(self.state)
        if self.return_hidden_state:
            return out, self.state
        else:
            raise NotImplementedError("return_hidden_state=False not implemented")

    def step(
        self, inputs_t: List[Tensor], state: List[Tensor]
    ) -> Tuple[List[Tensor], List[Tensor]]:
        """
        Overwrite this with base update equation. Annotations are required (for now)...
        """
        raise NotImplementedError
