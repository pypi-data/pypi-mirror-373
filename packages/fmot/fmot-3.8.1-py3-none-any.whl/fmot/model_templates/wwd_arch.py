from typing import Callable
import torch
from torch import nn

from fmot.nn.fft.stft import STFT, ISTFT
from fmot.nn.signal_processing import Magnitude, MelFilterBank, MelTranspose, LogEps
from fmot.nn import ThresholdSparsifier


class MelFrontend(nn.Module):
    """
    STFT -> Magnitude -> Mel Transform
    """

    def __init__(
        self,
        sample_rate: int,
        n_mels: int,
        n_fft: int,
        hop_size: int,
        window_size: int = None,
        window_fn: Callable[..., torch.Tensor] = torch.hann_window,
        **kwargs
    ):
        """

        Args:
            sample_rate: sampling rate of the input waveform
            n_mels: number of Mel features
            n_fft: length of the windowed signal
            hop_size: number of audio samples between adjacent STFT columns
            window_size: aach frame of audio is windowed by window of length win_length
                and then padded with zeros to match n_fft
            window_fn: a window function
            **kwargs: dictionary to feed for Mel arguments
        """
        super().__init__()

        if window_fn is not None:
            window_fn = window_fn(window_size)

        self.stft = STFT(
            n_fft=n_fft,
            hop_size=hop_size,
            n_stages="auto",
            window_size=window_size,
            window_fn=window_fn,
        )

        self.magnitude = Magnitude()
        self.mel = MelFilterBank(sample_rate, n_fft, n_mels=n_mels, **kwargs)

    def forward(self, x):
        re, im = self.stft(x)
        mag = self.magnitude(re, im)
        mel = self.mel(mag)
        return mel


class RNNArch(nn.Module):
    """This is an example of an RNN architecture with frontend that can be used for Wakeword Detection

    High-Level model architecture:
        MelFrontend -> Log-Compression -> Linear -> AdaptiveSparsifier -> RNN(s) -> Linear
    """

    def __init__(
        self,
        sample_rate=16000,
        n_mels=64,
        n_fft=256,
        hop_size=128,
        window_fn=torch.hann_window,
        window_size=None,
        rnn_hidden_size=64,
        rnn_num_layers=2,
        dropout=0.0,
    ):
        """

        Args:
            sample_rate: sampling rate of the input waveform
            n_mels: number of Mel features
            n_fft: length of the windowed signal
            hop_size: number of audio samples between adjacent STFT columns
            window_size: aach frame of audio is windowed by window of length win_length
                and then padded with zeros to match n_fft
            window_fn: a window function
            rnn_hidden_size: hidden size of the RNN part of the network
            rnn_num_layers: number of RNN layers
            dropout: dropout in the RNN part of the network
        """
        super().__init__()
        self.n_mels = n_mels
        self.n_fft = n_fft
        self.hop_size = hop_size
        self.rnn_num_layers = rnn_num_layers
        self.rnn_hidden_size = rnn_hidden_size
        self.dropout = dropout
        if window_size is None:
            window_size = n_fft

        self.frontend = MelFrontend(
            sample_rate,
            n_mels,
            n_fft,
            hop_size,
            window_size,
            window_fn,
        )
        self.log = LogEps()

        self.lin_in = nn.Linear(self.n_mels, rnn_hidden_size)
        self.sp = ThresholdSparsifier(rnn_hidden_size)
        self.rnn_layers = nn.ModuleList()
        for i in range(rnn_num_layers):
            layer = nn.LSTM(
                input_size=rnn_hidden_size,
                hidden_size=rnn_hidden_size,
                batch_first=True,
                dropout=self.dropout,
            )
            self.rnn_layers.append(layer)
        self.lin_out = nn.Linear(rnn_hidden_size, 1)

    def forward(self, x):
        mel_spec = self.frontend(x)
        log_melspec = self.log(mel_spec)
        y = self.lin_in(log_melspec)
        y = self.sp(y)
        for l in self.rnn_layers:
            y, __ = l(y)
        y = self.lin_out(y)
        return y
