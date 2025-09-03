import torch
import torch.nn as nn
from neuralforecast.models import LSTM

from forecaster_toolkit.models.dl.DLModel import DLModel


class LSTMModel(DLModel):
    def __init__(self):
        self.model = LSTM()
        self.linear = nn.Linear(self.hidden_size, self.output_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of the LSTM model

        Arguments:
        ----------
        x: torch.Tensor
            Input tensor

        Returns:
        --------
        torch.Tensor: Model predictions
        """
        lstm_out, _ = self.lstm(x)
        # Take the last time step output from the LSTM
        out = self.linear(lstm_out[:, -1, :])
        return out

    def save_model(self, path: str) -> None:
        """
        Save the model state

        Arguments:
        ----------
        path: str
            Path to save the model
        """
        super().save_model(path)
