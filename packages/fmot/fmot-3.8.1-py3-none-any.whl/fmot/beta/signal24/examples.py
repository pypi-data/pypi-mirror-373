import torch
from fmot.beta.signal24 import (
    STFT,
    ISTFT,
    Cast16,
    ComplexMultiply,
)
from fmot.nn.signal_processing import BarniMagnitude
from torch import nn, Tensor
from fmot.precisions import int8, int16, int24, Precision
import fmot


class ExampleModel(nn.Module):
    """
    Example Overlap-Add system with higher-precision STFT/iSTFT.

    Runs an LSTM on the STFT components, but sets the complex mask to (1 + 0j)
    everywhere to test identity behavior.

    Applies a gain of 1 with a higher-precision STFT/ISTFT.

    The new fmot.beta.signal24.STFT operator returns two views of the
    STFT coefficients -- one in higher precision (int24 or int16), and the other
    always in int16 precision. Note that when `act_precision == int16`, both views
    are identical. See the forward method below to see how to interact with this
    new output format.
    """

    def __init__(
        self,
        hop_length: int,
        window_length: int,
        window_fn: Tensor = None,
        act_precision: Precision = int24,
        weight_precision: Precision = int16,
    ):
        super().__init__()
        self.stft = STFT(
            n_fft=window_length,
            hop_size=hop_length,
            n_stages="auto",
            act_precision=act_precision,
            weight_precision=weight_precision,
            window_fn=window_fn,
        )
        self.mag = BarniMagnitude()

        n_fft = window_length // 2 + 1
        self.rnn = nn.LSTM(n_fft, n_fft, batch_first=True)

        self.complex_mul = ComplexMultiply(act_precision)

        self.istft = ISTFT(
            n_fft=window_length,
            hop_size=hop_length,
            n_stages="auto",
            act_precision=act_precision,
            weight_precision=weight_precision,
            window_fn=window_fn,
        )

    def forward(self, audio: Tensor):
        """
        fmot.beta.signal24.STFT returns two versions of the STFT coefficients,
        stored into two tuples:
        - (re_hp, im_hp): high-precision STFT coefficients --> cannot at this time
            be directly consumed by DNN operations, but we can apply a complex
            mask and ISTFT to these
        - (re_16, im_16): int16 STFT coefficients (just a cast-down version of the _hp
            coefficents), suitable for DNN operations.
        """
        (re_hp, im_hp), (re_16, im_16) = self.stft(audio)

        # run DNN, get real/imag mask components
        mag = self.mag(re_16, im_16)
        mask_re, _ = self.rnn(mag)
        mask_im = mask_re * 0
        mask_re = mask_re * 0 + 1

        # apply mask to the higher-precision STFT components
        re, im = self.complex_mul(mask_re, mask_im, re_hp, im_hp)

        # ISTFT will internally use higher precisions, automatically cast
        # the final result to int16
        out = self.istft(re, im)
        return out


def get_pure_tone_calib(
    batch_size: int, num_batches: int, num_frames: int, hop_length: int, levels_dbfs=[0]
):
    """
    Pure-tone 0dBFS calibration data at logarithmic-spaced frequences is recommended whenever
    quantizing a system with a decomposed STFT layer.
    """
    num_freqs = batch_size * num_batches
    periods = torch.logspace(1e2 * num_freqs, 1, num_freqs)
    time = torch.arange(num_frames * hop_length)
    waveforms = torch.sin(2 * torch.pi / periods.unsqueeze(1) * time.unsqueeze(0))

    gained_waveforms = []
    for level_dbfs in levels_dbfs:
        gained_waveforms.append(waveforms * 10 ** (level_dbfs / 20))

    waveforms = torch.cat(gained_waveforms, 0)

    batches = []
    for i in range(num_batches * len(levels_dbfs)):
        batches.append(
            waveforms[i * batch_size : (i + 1) * batch_size].reshape(
                batch_size, num_frames, hop_length
            )
        )

    return batches


def test_ola_quantization(model: nn.Module, hop_length: int, plot=False):
    y = model(torch.randn(8, 10, hop_length))

    cmodel = fmot.ConvertedModel(model, batch_dim=0, seq_dim=1)
    cmodel.set_input_details(0, -15)
    cmodel.set_output_details(0, -15)

    # recommended: include 0dBFS pure tone data in calibration set (along with speech)
    calib = get_pure_tone_calib(
        batch_size=8,
        num_batches=4,
        num_frames=20,
        hop_length=hop_length,
        levels_dbfs=[0, -25, -70],
    )
    cmodel.quantize(calib)

    x = torch.randn(8, 20, hop_length)
    x = x / torch.max(torch.abs(x))
    gains_db = torch.linspace(0, 0, x.shape[1] * x.shape[2]).reshape(
        1, x.shape[1], x.shape[2]
    )
    gains = 10 ** (gains_db / 20)
    x = x * gains
    y = cmodel(x)

    tgt = x[:, :-1].flatten()
    est = y[:, 1:].flatten()

    if plot:
        import matplotlib.pyplot as plt

        plt.plot(tgt.cpu().numpy().flatten(), est.detach().cpu().numpy().flatten(), ".")
        plt.show()

    qsnr_quant = 10 * torch.log10(torch.mean(tgt**2) / torch.mean((tgt - est) ** 2))

    y = model(x)
    est = y[:, 1:].flatten()

    qsnr_fp = 10 * torch.log10(torch.mean(tgt**2) / torch.mean((tgt - est) ** 2))

    graph = cmodel.trace()

    x = x[0].numpy()
    y_fqir = graph.run(x, dequant=True)

    tgt = x[:-1].flatten()
    est = y_fqir[1:].flatten()

    qsnr_fqir = 10 * np.log10(np.mean(tgt**2) / np.mean((tgt - est) ** 2))

    # compare FQIR to QUANT output:
    est_quant = y[0].flatten().detach().numpy()
    est_fqir = y_fqir.flatten()

    quant_fqir_mse = np.mean((est_quant - est_fqir) ** 2)

    return qsnr_fp, qsnr_quant, qsnr_fqir, quant_fqir_mse, graph


if __name__ == "__main__":
    import numpy as np
    import os

    # if not None, will save FQIR files in this directory
    # SAVEDIR = "/home/scott/gmac/femtomapper/test/test_production_fqir/models"
    SAVEDIR = None

    hop_length = 128
    window_length = 256
    window_fn = torch.hann_window(window_length)

    for act_precision in [int16, int24]:
        for weight_precision in [int8, int16]:
            model = ExampleModel(
                hop_length,
                window_length,
                n_stages="auto",
                window_fn=window_fn,
                act_precision=act_precision,
                weight_precision=weight_precision,
            )

            qsnr_fp, qsnr_quant, qsnr_fqir, mismatch, graph = test_ola_quantization(
                model, hop_length, plot=False
            )
            print(
                f"With {act_precision} x {weight_precision} and STFT/ISTFT:"
                f"\n\tF.P. reconstruction SNR: {qsnr_fp:.1f}dB"
                f"\n\tQAT reconstruction SNR: {qsnr_quant:.1f}dB"
                f"\n\tFQIR reconstruction SNR: {qsnr_fqir:.1f}dB"
                f"\n\tFQIR-QUANT mismatch: {mismatch:.1f}"
            )

            if SAVEDIR is not None:
                loc = os.path.join(
                    SAVEDIR, f"example_ola_{act_precision}x{weight_precision}.pt"
                )
                torch.save(graph, loc)
