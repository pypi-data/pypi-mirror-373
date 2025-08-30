from fmot import CONFIG
from fmot.test.utm.get_utms import ALL_UTMS
from fmot.test.utm.test_utm_quantization_error import test_quantization_error
import argparse
import torch
import matplotlib.pyplot as plt

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--testcase", type=str, choices=ALL_UTMS.keys())
    parser.add_argument("--precision", type=str, default="double")
    parser.add_argument("--rounded", action="store_true")
    args = parser.parse_args()

    CONFIG.quant_round = args.rounded

    utm = ALL_UTMS[args.testcase]
    print(utm)

    input = utm.get_random_inputs(batch_size=1)
    print([x.shape for x in input])
    input_np = [x.numpy()[0] for x in input]
    qmodel = utm.get_quantized_model(bw_conf=args.precision)
    graph = utm.get_fqir(bw_conf=args.precision)

    with torch.no_grad():
        y0 = qmodel(*input)
    y1 = graph.run(*input_np, dequant=True)

    if isinstance(y0, (list, tuple)):
        y0 = y0[0]
        y1 = y1[0]
    y0 = y0[0].numpy()

    utm.test_fqir_runtime(bw_conf=args.precision)

    graph = utm.get_fqir(bw_conf=args.precision)
    print(graph.subgraphs["ARITH"])
    utm.test_fqir_runtime(bw_conf=args.precision)

    test_quantization_error(args.testcase, args.precision)
