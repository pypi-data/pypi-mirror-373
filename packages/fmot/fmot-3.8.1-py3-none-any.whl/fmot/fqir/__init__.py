from .variables import TensorProto, TensorSignature
from .nodes.optypes import registry_v1
from .nodes import NodeProto
from .graph_proto import GraphProto
from . import variables, nodes, graph_proto, writer
from . import metadata

# keep this to support legacy FQIR format
import sys

sys.setrecursionlimit(10000)
