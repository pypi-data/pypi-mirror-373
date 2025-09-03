import torch
import fmot
import numpy as np


class SingleInputModel(torch.nn.Module):
    def __init__(self, d_model: int):
        super().__init__()
        self.lstm = torch.nn.LSTM(
            d_model, d_model, batch_first=True, num_layers=1, dropout=0.0
        )

    def forward(self, ac1: torch.Tensor) -> torch.Tensor:
        """
        ac1: (torch.Tensor) -> Input Tensor (B, SEQ_LEN, DIM)
        """
        out, _ = self.lstm(ac1)
        return out


class MultipleInputModel(torch.nn.Module):
    def __init__(self, d_model: int):
        super().__init__()
        self.lstm = torch.nn.LSTM(
            d_model, d_model, batch_first=True, num_layers=1, dropout=0.0
        )

    def forward(self, ac1: torch.Tensor, ac2: torch.Tensor) -> torch.Tensor:
        """
        ac1: (torch.Tensor) -> Input Tensor 1 (B, SEQ_LEN, DIM)
        ac2: (torch.Tensor) -> Input Tensor 2 (B, SEQ_LEN, DIM)
        """
        ac1_out, _ = self.lstm(ac1 * 2.0)
        ac2_out, _ = self.lstm(ac2)
        return ac1_out + ac2_out


def test_single_input():
    B, S, D = 1, 5, 64

    model = SingleInputModel(d_model=D)
    cmodel = fmot.ConvertedModel(model, batch_dim=0, seq_dim=1)

    n_calib_samples = 5
    calib_data = [torch.randn(B, S, D) for _ in range(n_calib_samples)]

    cmodel.quantize(calib_data)
    fqir_graph = cmodel.trace()

    test_sample = torch.randn(B, S, D)

    cmodel_out = cmodel(test_sample)
    fqir_out = fqir_graph.run(test_sample[0].cpu().detach().numpy(), dequant=True)

    assert np.allclose(
        cmodel_out.cpu().detach().numpy(), fqir_out, atol=1e-2
    ), "cmodel and FQIR outputs do not match!"


def test_multiple_inputs():
    B, S, D = 1, 5, 64

    model = MultipleInputModel(d_model=D)
    cmodel = fmot.ConvertedModel(model, batch_dim=0, seq_dim=1)

    n_calib_samples = 5
    calib_data_ac1 = [torch.randn(B, S, D) for _ in range(n_calib_samples)]
    calib_data_ac2 = [torch.randn(B, S, D) for _ in range(n_calib_samples)]

    # For multiple inputs, combine them as tuples
    calib_data = [(ac1, ac2) for ac1, ac2 in zip(calib_data_ac1, calib_data_ac2)]
    cmodel.quantize(calib_data)
    fqir_graph = cmodel.trace()

    test_sample_ac1 = torch.randn(B, S, D)
    test_sample_ac2 = torch.randn(B, S, D)

    cmodel_out = cmodel(test_sample_ac1, test_sample_ac2)
    fqir_out = fqir_graph.run(
        test_sample_ac1[0].cpu().detach().numpy(),
        test_sample_ac2[0].cpu().detach().numpy(),
        dequant=True,
    )

    # Assertions
    assert np.allclose(
        cmodel_out.cpu().detach().numpy(), fqir_out, atol=1e-2
    ), "cmodel and FQIR outputs do not match!"


if __name__ == "__main__":
    test_multiple_inputs()
    test_single_input()
