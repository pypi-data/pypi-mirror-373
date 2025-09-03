import torch

from fmot import ConvertedModel
from fmot.model_templates import RNNArch, TinyLSTM
from fmot.sparse import prune_model_parameters


def test_rnnarch():
    """Checks that the WWD RNNArch tutorial works"""
    sr = 16000
    n_fft = 512
    hop_length = n_fft // 2
    model = RNNArch(n_fft=n_fft, hop_size=hop_length)

    # Let's create random wav files of length 3*sr
    batch_size = 5
    seq_len = 3 * sr
    wav1 = torch.randn(batch_size, seq_len)
    wav2 = torch.randn(batch_size, seq_len)

    # We need to reshape the wavs, so it will match the STFT signature
    pad_amount = hop_length - (seq_len % hop_length)
    wav1 = torch.nn.functional.pad(wav1, (0, pad_amount))
    wav2 = torch.nn.functional.pad(wav2, (0, pad_amount))
    wav1 = torch.reshape(wav1, (batch_size, -1, hop_length))
    wav2 = torch.reshape(wav2, (batch_size, -1, hop_length))
    quant_inputs = [wav1, wav2]

    qmodel = ConvertedModel(model, batch_dim=0, seq_dim=1)
    qmodel.quantize(quant_inputs)

    _ = qmodel.trace()

    assert True


def test_tinylstm():
    """Checks that the TinyLSTM tutorial works"""
    sr = 16000
    n_fft = 512
    hop_length = n_fft // 2
    model = TinyLSTM()

    # Let's create random wav files of length 3*sr
    batch_size = 5
    seq_len = 3 * sr
    wav1 = torch.randn(batch_size, seq_len)
    wav2 = torch.randn(batch_size, seq_len)

    # We need to reshape the wavs, so it will match the STFT signature
    pad_amount = hop_length - (seq_len % hop_length)
    wav1 = torch.nn.functional.pad(wav1, (0, pad_amount))
    wav2 = torch.nn.functional.pad(wav2, (0, pad_amount))
    wav1 = torch.reshape(wav1, (batch_size, -1, hop_length))
    wav2 = torch.reshape(wav2, (batch_size, -1, hop_length))
    quant_inputs = [wav1, wav2]

    prune_model_parameters(model, amount=0.9, pencil_size=4)

    qmodel = ConvertedModel(model, batch_dim=0, seq_dim=1)
    qmodel.quantize(quant_inputs)

    _ = qmodel.trace()

    assert True
