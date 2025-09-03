import fmot.qat as Q
import torch

# A list of modules not to be traced:

TRACING_BLACKLIST = [
    Q.nn.QuantWrapper,
    Q.nn.QuantCollection,
    Q.nn.DictQuantCollection,
    Q.nn.Quantizer,
    Q.nn.StateQuantizer,
    Q.nn.MinMaxObserver,
    Q.nn.ParameterQuantizer,
    Q.nn.FixedRangeObserver,
    Q.nn.StateInitializer,
    torch.nn.ModuleDict,
    torch.nn.LSTM,
    torch.nn.Unfold,
    Q.nn.ListQuantCollection,
]
