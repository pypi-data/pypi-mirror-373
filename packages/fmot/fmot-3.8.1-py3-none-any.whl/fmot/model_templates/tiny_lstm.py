import torch
from torch import nn, Tensor

from fmot.nn.fft.stft import STFT, ISTFT
from fmot.nn.signal_processing import Magnitude, MelFilterBank, MelTranspose


class FCStack(nn.Module):
    """
    Stack of Fully-Connected layers
    """

    def __init__(self, input_size, hidden_size, num_layers):
        """

        Args:
            input_size (int): size of the input
            hidden_size (int): size of the hidden layer
            num_layers (int): number of FC layers
        """
        super().__init__()
        assert num_layers >= 2
        self.in_layers = nn.ModuleList()
        in_sizes = [input_size] + [hidden_size] * (num_layers - 2)
        for in_size in in_sizes:
            self.in_layers.append(nn.Linear(in_size, hidden_size))
        self.out_layer = nn.Linear(hidden_size, hidden_size)
        self.relu = nn.ReLU()

    def forward(self, x):
        for l in self.in_layers:
            x = self.relu(l(x))
        x = self.out_layer(x).sigmoid()
        return x


class TinyLSTM(nn.Module):
    """Implementation of the architecture from the paper 'TinyLSTMs: Efficient Neural Speech Enhancement for
    Hearing Aids' (https://arxiv.org/pdf/2005.11138)

    High-Level model architecture:
        STFT -> Mel-Fetures -> Compression -> RNN -> FCs -> Spectral-Masking -> Inverse-Mel -> ISTFT
    """

    def __init__(
        self,
        sr=16000,
        n_fft=512,
        n_mels=128,
        rnn_num_layers=2,
        rnn_hidden_size=256,
        rnn_type="lstm",
        fc_num_layers=2,
        fmin=0.0,
        fmax=None,
        mel_exponent=0.3,
        dropout=0,
    ):
        """

        Args:
            sr: sample rate
            n_fft: length of the windowed signal
            n_mels: number of mel features
            rnn_num_layers: numbers of layers in the RNN part of the metwork
            rnn_hidden_size: hidden size in the RNN part of the network
            rnn_type: type of rnn layer
            fc_num_layers: number of fully-connected layers after the RNN
            fmin: min frequency for the Mel transform
            fmax: max frequency for the mel transform
            mel_exponent: exponant to apply to the mel spectrogram for range compression
            dropout: dropout in the RNN layers
        """
        super().__init__()
        self.sr = sr
        self.n_fft = n_fft
        self.hop_size = n_fft // 2
        # Mel related hyper-parameters
        self.n_mels = n_mels
        self.mel_exponent = mel_exponent
        self.fmin = fmin
        self.fmax = fmax
        # RNN hyper-parameters
        self.rnn_num_layers = rnn_num_layers
        self.rnn_type = rnn_type
        self.fc_num_layers = fc_num_layers
        self.rnn_hidden_size = rnn_hidden_size
        self.dropout = dropout

        # frontend: STFT -> Magnitude -> Mel
        window_fn = torch.hann_window(n_fft)
        self.stft = STFT(
            n_fft=n_fft, hop_size=self.hop_size, window_fn=window_fn, n_stages="auto"
        )
        self.istft = ISTFT(
            n_fft=n_fft, hop_size=self.hop_size, window_fn=window_fn, n_stages="auto"
        )
        self.abs = Magnitude()
        self.mel = MelFilterBank(
            sr=sr, n_fft=n_fft, n_mels=n_mels, fmin=fmin, fmax=fmax
        )
        self.melinv = MelTranspose(sr, n_fft, n_mels, fmin, fmax)

        # construct multilayer RNN
        rnn_kwargs = dict(
            input_size=n_mels,
            hidden_size=rnn_hidden_size,
            num_layers=rnn_num_layers,
            batch_first=True,
            dropout=dropout,
        )
        if rnn_type == "lstm":
            self.rnn = nn.LSTM(**rnn_kwargs)
        elif rnn_type == "gru":
            self.rnn = nn.GRU(**rnn_kwargs)
        elif rnn_type == "rnn":
            self.rnn = nn.RNN(**rnn_kwargs)
        else:
            raise Exception("Unknown RNN layer.")

        # construct FC stack
        if fc_num_layers >= 2:
            self.fcs = FCStack(rnn_hidden_size, n_mels, fc_num_layers)
        else:
            self.fcs = nn.Sequential(nn.Linear(rnn_hidden_size, n_mels), nn.Sigmoid())

        self.melinv = MelTranspose(sr, n_fft, n_mels, fmin, fmax)
        self.min_gain = 0

    def forward(self, x: Tensor) -> Tensor:
        """
        Arguments:
            x (Tensor): input audio sequence, in non-overlapping frames of length :attr:`hop_length`.
                Shape: :attr:`(B, N, hop_length)`

        Returns:
            y (Tensor): output sequence, same shape as input sequence. The output sequence is truncated
                by :attr:`hop_length` and the first frame is all zeros.

        Truncation:
            Because of the staggered nature of overlap-add ISTFT, the output sequence is truncated
            by :attr:`hop_length` and the first frame is all zeros. For input :attr:`x` and
            output :attr:`y`, `y[:, i+1]` corresponds to `x[:, i]`, with `y[:, 0] = 0` and
            `y[:, -1]` corresponding to `x[:, -2]`.

            It is recommended to pad the input sequence on the right with zeros to avoid the impact
            of truncation.
        """
        re, im = self.stft(x)
        mag = self.abs(re, im)
        mel = self.mel(mag).pow(self.mel_exponent)

        x, __ = self.rnn(mel)
        mel_mask = self.fcs(x)

        stft_mask = self.melinv(mel_mask)

        re_masked = stft_mask * re
        im_masked = stft_mask * im

        y = self.istft(re_masked, im_masked)

        return y
