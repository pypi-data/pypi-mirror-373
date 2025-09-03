from fmot.fqir import registry_v1
import fmot.qat as Q

oplinks_v1 = {
    Q.nn.VVAdd: registry_v1["vvadd"],
    Q.nn.VIAdd: registry_v1["viadd"],
    Q.nn.VVSub: registry_v1["vvsub"],
    Q.nn.Neg: registry_v1["vneg"],
    Q.nn.VVMul: registry_v1["vvmul"],
    Q.nn.VIMul: registry_v1["vimul"],
    Q.nn.Matmul: registry_v1["matmul"],
    Q.nn.NoShiftMM: registry_v1["matmul"],
    Q.nn.AddMM: registry_v1["addmm"],
    Q.nn.ReLU: registry_v1["relu"],
    Q.nn.Transpose: registry_v1["transpose"],
    Q.nn.FTranspose: registry_v1["transpose"],
    Q.nn.Reshape: registry_v1["reshape"],
    Q.nn.Quantizer: registry_v1["quantize"],
    Q.nn.Chunk: registry_v1["chunk"],
    Q.nn.Split: registry_v1["split"],
    Q.nn.BareCat: registry_v1["cat"],
    Q.nn.Stack: registry_v1["stack"],
    Q.nn.Sum: registry_v1["sum"],
    Q.nn.OnesLike: registry_v1["constant_like"],
    Q.nn.Shift: registry_v1["shift"],
    Q.nn.Requantize: registry_v1["shift"],
    Q.nn.RecursiveStateHandler: registry_v1["shift"],
    Q.nn.RequantizeFromBitwidthQuanta: registry_v1["shift"],
    Q.nn.Gt0: registry_v1["gt0"],
    Q.nn.Squeeze: registry_v1["squeeze"],
    Q.nn.TemporalUnfold1d: registry_v1["temporal_unfold_unkernelized"],
    Q.nn.TemporalFoldTranspose1d: registry_v1["temporal_transpose_fold_unkernelized"],
    Q.nn.FastILUT: registry_v1["pwlin"],
    Q.nn.GMACv2: registry_v1["gmac_v2"],
    Q.nn.PrecisionSplit: registry_v1["gmac_v2"],
    Q.nn.F_TemporalConv2d: registry_v1["temporal_conv2d"],
    Q.nn.F_TemporalConv1d: registry_v1["temporal_conv2d"],
}

lut_ops = [Q.nn.LUT, Q.nn.RSqrtPlusEps, Q.nn.PowFrac, Q.nn.BareLUT]
for op in lut_ops:
    oplinks_v1[op] = registry_v1["lut"]
