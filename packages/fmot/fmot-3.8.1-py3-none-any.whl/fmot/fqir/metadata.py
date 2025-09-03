import numpy as np
from dataclasses import dataclass
from . import GraphProto
from typing import *


@dataclass
class ReshapeSpec:
    """Defines the strategy used to reshape an input or output to the model.

    Our stride-optimization often will reshape an input from (L, Cin) to
    (L//S, Cin * S). This spec can define the specifics of this transformation.

    Attributes:
        feature_dim (int): feature dimension
        base_features (int): number of features (before transformation)
        is_input (bool): True if the tensor is a model input, False if it is an output
        sequence_dim (int): sequence dimension (or None)
        repeat_factor (int): number of repeats to compute the transformed tensor

    Examples:

        Input Reshaping:

        .. code:: python

            reshaper = ReshapeSpec(feature_dim=1, sequence_dim=0, base_features=64, repeat_factor=2, is_input=True)
            x = np.randn(10, 64)
            y = reshaper.reshape_input(x)
            print(y.shape)
            >>> (5, 128)

        Output Reshaping:

        .. code:: python

            reshaper = ReshapeSpec(feature_dim=1, sequence_dim=0, base_features=64, repeat_factor=2, is_input=False)
            x = np.randn(5, 128)
            y = reshaper.reshape_input(x)
            print(y.shape)
            >>> (10, 64)
    """

    feature_dim: int
    base_features: int
    is_input: bool
    sequence_dim: Optional[int] = None
    repeat_factor: int = 1

    def reshape_input(self, x: np.ndarray) -> np.ndarray:
        if self.repeat_factor == 1:
            return x
        elif x.shape[self.feature_dim] == self.repeat_factor * self.base_features:
            # don't need to perform reshape
            return x
        elif self.sequence_dim is not None:
            s_dim = self.sequence_dim
            f_dim = self.feature_dim

            length_in = x.shape[s_dim]
            feat_in = x.shape[f_dim]

            length_out = length_in // self.repeat_factor
            feat_out = feat_in * self.repeat_factor

            # uniformize to (time, feat) format
            x = np.transpose(x, axes=[s_dim, f_dim])

            # trim to integer multiple of repeat_factor
            x = x[: length_out * self.repeat_factor]

            # create stacked input features
            y = np.empty((length_out, feat_out), dtype=x.dtype)

            for t_out in range(length_out):
                vectors = []
                for offset in range(self.repeat_factor):
                    t_in = t_out * self.repeat_factor + offset
                    vectors.append(x[t_in])
                y_t = np.concatenate(vectors, axis=0)
                y[t_out] = y_t

            # invert the transpose
            y = np.transpose(y, axes=[s_dim, f_dim])
            return y
        else:
            raise ValueError("Cannot reshape an input without a sequence dimension")

    def reshape_output(self, x: np.ndarray) -> np.ndarray:
        if self.repeat_factor == 1:
            return x
        elif self.sequence_dim is not None:
            s_dim = self.sequence_dim
            f_dim = self.feature_dim

            length_in = x.shape[s_dim]
            feat_in = x.shape[f_dim]

            length_out = length_in * self.repeat_factor
            feat_out = feat_in // self.repeat_factor

            # uniformize to (time, feat) format
            x = np.transpose(x, axes=[s_dim, f_dim])

            # create stacked input features
            y = np.empty((length_out, feat_out), dtype=x.dtype)

            for t_in in range(length_in):
                vectors = np.split(x[t_in], self.repeat_factor, axis=0)
                for offset, vect in enumerate(vectors):
                    y[t_in * self.repeat_factor + offset] = vect

            # invert the transpose
            y = np.transpose(y, axes=[s_dim, f_dim])
            return y
        else:
            raise ValueError("Cannot reshape an output without a sequence dimension")

    def starting_shape(self):
        time = "T"
        feature = self.base_features

        output = [time, feature]
        if self.sequence_dim == 1:
            output = output[::-1]
        elif self.sequence_dim is None:
            output = [output[-1]]
        return output

    def ending_shape(self):
        time = f"T//{self.repeat_factor}"
        feature = self.base_features * self.repeat_factor

        output = [time, feature]
        if self.sequence_dim == 1:
            output = output[::-1]
        elif self.sequence_dim is None:
            output = [output[-1]]
        return output

    def __repr__(self):
        return f"<Original shape -> Transformed shape> : {self.starting_shape()} -> {self.ending_shape()}"


class IOMetaData:
    """Defines ReshapeSpecs for a model's input/output signature"""

    def __init__(self):
        self.input_spec: List[ReshapeSpec] = []
        self.output_spec: List[ReshapeSpec] = []

    def add_input_spec(self, spec: ReshapeSpec):
        self.input_spec.append(spec)

    def add_output_spec(self, spec: ReshapeSpec):
        self.output_spec.append(spec)

    def run_graph(self, graph: GraphProto, inputs: List[np.ndarray], **kwargs):
        if len(inputs) != len(self.input_spec):
            raise ValueError(
                f"Not enough inputs. Expected {len(self.input_spec)}, recieved {len(inputs)}."
            )

        new_inputs = []
        for x, reshaper in zip(inputs, self.input_spec):
            new_inputs.append(reshaper.reshape_input(x))

        outputs = graph.run(*new_inputs, **kwargs)
        if isinstance(outputs, np.ndarray):
            outputs = [outputs]

        if len(outputs) != len(self.output_spec):
            raise ValueError(
                f"Not enough outputs. Expected {len(self.output_spec)}, recieved {len(outputs)}."
            )

        new_outputs = []
        for x, reshaper in zip(outputs, self.output_spec):
            new_outputs.append(reshaper.reshape_output(x))

        if len(new_outputs) == 0:
            return
        elif len(new_outputs) == 1:
            return new_outputs[0]
        else:
            return new_outputs

    def __repr__(self):
        ret = "IOMetadata:\n  Inputs:"
        for input in self.input_spec:
            ret += f"\n    {input}"
        ret += "\n  Outputs:"
        for output in self.output_spec:
            ret += f"\n    {output}"
        return ret
