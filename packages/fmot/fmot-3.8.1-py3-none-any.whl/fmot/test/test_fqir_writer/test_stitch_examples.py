import torch
from torch import nn, Tensor
import fmot

N_MELS = 32
HOP = 128
WINDOW = 256
D_HIDDEN = 64


class MelSpec(nn.Module):
    def __init__(self, hop: int, window: int, n_mels: int):
        super().__init__()

        self.stft = fmot.nn.STFT(window, hop, window_fn=torch.hann_window(window))
        self.mag = fmot.nn.signal.Magnitude()
        self.mel = fmot.nn.signal.MelFilterBank(16000, window, n_mels)

    def forward(self, audio: Tensor):
        re, im = self.stft(audio)
        mag = self.mag(re, im)
        mels = self.mel(mag)
        return mels


class LSTMClassifier(nn.Module):
    def __init__(self, n_mels: int, hidden_size: int, n_labels: int):
        super().__init__()
        self.lstm = nn.LSTM(n_mels, hidden_size, batch_first=True)
        self.proj_out = nn.Linear(hidden_size, n_labels)

    def forward(self, mels: Tensor):
        feats, _ = self.lstm(mels)
        return self.proj_out(feats)


def get_graphs():
    mel_spec = MelSpec(HOP, WINDOW, N_MELS)
    classifier_a = LSTMClassifier(N_MELS, D_HIDDEN, 5)
    classifier_b = LSTMClassifier(N_MELS, D_HIDDEN, 7)

    cmodel_mel = fmot.ConvertedModel(mel_spec, batch_dim=0, seq_dim=1)
    cmodel_a = fmot.ConvertedModel(classifier_a, batch_dim=0, seq_dim=1)
    cmodel_b = fmot.ConvertedModel(classifier_b, batch_dim=0, seq_dim=1)

    calib_mel = [torch.randn(8, 10, HOP) for _ in range(10)]
    calib_classifier = [mel_spec(x) for x in calib_mel]

    cmodel_mel.quantize(calib_mel)
    cmodel_a.quantize(calib_classifier)
    cmodel_b.quantize(calib_classifier)

    mel_fqir = cmodel_mel.trace()
    a_fqir = cmodel_a.trace()
    b_fqir = cmodel_b.trace()

    return mel_fqir, a_fqir, b_fqir


from fmot.fqir.writer import new_fqir_graph, FQIRWriter
import numpy as np


def merge_graphs(mel_fqir, a_fqir, b_fqir):
    # initialize an empty graph
    graph = new_fqir_graph()
    writer = FQIRWriter.from_fqir(graph)

    # add input and inline the mel fqir
    (audio,) = writer.add_inputs_from_graph(mel_fqir)
    (mels,) = writer.inline_fqir_graph(mel_fqir, inputs=[audio])

    # inline the two classifiers, using the mel-features as input
    (out_a,) = writer.inline_fqir_graph(a_fqir, inputs=[mels])
    (out_b,) = writer.inline_fqir_graph(b_fqir, inputs=[mels])

    # add outputs
    writer.add_outputs([out_a, out_b])

    # verify
    x = np.random.randint(low=-(2**15), high=2**15 - 1, size=[10, HOP])

    # first, run each graph
    mel_vals = mel_fqir.run(x, dequant=False)
    a_vals_0 = a_fqir.run(mel_vals, dequant=False)
    b_vals_0 = b_fqir.run(mel_vals, dequant=False)

    # now, run the end-to-end graph
    a_vals_1, b_vals_1 = graph.run(x, dequant=False)

    assert np.array_equal(a_vals_0, a_vals_1)
    assert np.array_equal(b_vals_0, b_vals_1)


def test_example_1():
    mel_fqir, a_fqir, b_fqir = get_graphs()
    merge_graphs(mel_fqir, a_fqir, b_fqir)


if __name__ == "__main__":
    test_example_1()
