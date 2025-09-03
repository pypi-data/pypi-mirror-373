from typing import Optional

import torch
import torch.nn as nn


class DLModel:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model: Optional[nn.Module] = None
        self.optimizer: Optional[torch.optim.Optimizer] = None
        self.criterion: Optional[nn.Module] = None

    def build_model(self) -> None:
        """
        Initialize the PyTorch model architecture.
        Should be implemented by child classes.
        """
        raise NotImplementedError

    def setup_training(self, learning_rate: float) -> None:
        """
        Setup training components like optimizer and loss function

        Arguments
        ---------
        learning_rate: float
            Learning rate for the optimizer
        """
        if self.model is None:
            raise ValueError("Model must be built before setting up training")

        # Default optimizer and criterion - can be overridden in child classes
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        self.criterion = nn.MSELoss()

    def train_step(self, X: torch.Tensor, y: torch.Tensor) -> float:
        """
        Perform one training step

        Arguments
        ---------
        X: torch.Tensor
            Input tensor
        y: torch.Tensor
            Target tensor

        Returns:
        --------
            float: Loss value for this step
        """
        # Set the model to training mode
        self.model.train()
        # Zero the gradients
        self.optimizer.zero_grad()
        # Forward pass
        outputs = self.model(X)
        # Compute the loss
        loss = self.criterion(outputs, y)
        # Backward pass and optimization step
        loss.backward()
        # Update the model parameters using backpropagation
        self.optimizer.step()
        # Return the loss value for this step
        return loss.item()

    def predict(self, X: torch.Tensor) -> torch.Tensor:
        """
        Make predictions using the model

        Arguments:
        ----------
        X: torch.Tensor
            Input tensor

        Returns:
        --------
        torch.Tensor: Model predictions
        """
        self.model.eval()
        with torch.no_grad():
            return self.model(X)

    def save_model(self, path: str) -> None:
        """
        Save the model state

        Arguments:
        ----------
        path: str
            Path to save the model
        """
        if self.model is None:
            raise ValueError("No model to save")
        torch.save(
            {
                "model_state_dict": self.model.state_dict(),
                "optimizer_state_dict": (
                    self.optimizer.state_dict() if self.optimizer else None
                ),
                "model_params": self.model_params,
            },
            path,
        )

    def load_model(self, path: str) -> None:
        """
        Load the model state

        Arguments:
        ----------
        path: str
            Path to the saved model
        """
        if self.model is None:
            raise ValueError("Model must be built before loading weights")

        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        if self.optimizer and checkpoint["optimizer_state_dict"]:
            self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
