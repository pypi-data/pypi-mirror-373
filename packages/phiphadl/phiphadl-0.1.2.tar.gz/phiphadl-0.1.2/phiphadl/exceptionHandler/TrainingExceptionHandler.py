import torch
import argparse
import datetime
import logging
import os
from typing import Optional, Union, List, Dict, Any, Tuple, Literal
from ..utils.LoggerColorFormatter import TerminalColorFormatter, LogColorFormatter


class TrainingExceptionHandler:
    def __init__(self, log_folder, log_file_name='training_exception'):
        """
        Initializes the TrainingExceptionHandler for handling errors in training operations.
        """
        self.log_folder = log_folder
        os.makedirs(self.log_folder, exist_ok=True)
        
        # Set up dual-stream logging (file and terminal)
        self.logger = logging.getLogger(__name__ + "_exception")
        self.logger.setLevel(logging.ERROR)
        terminal_formatter = TerminalColorFormatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        log_formatter = LogColorFormatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_folder=self.log_folder,
            log_file_name=log_file_name
        )

        # File handler
        file_handler = logging.StreamHandler()
        file_handler.setFormatter(log_formatter)
        self.logger.addHandler(file_handler)

        # Stream handler for terminal output
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(terminal_formatter)
        self.logger.addHandler(stream_handler)

    def safe_forward(
        self,
        model: torch.nn.Module,
        inputs: Union[List[torch.Tensor], Dict[str, torch.Tensor]],
    ) -> Optional[torch.Tensor]:
        """
        Safely performs the model forward pass.

        Args:
            model: The PyTorch model.
            inputs: List or dictionary of input tensors.

        Returns:
            Model outputs or None if an error occurs.
        """
        try:
            if isinstance(inputs, (list, tuple)):
                outputs = model(*inputs)
            else:
                raise ValueError("Inputs must be a list/tuple of tensors")
            return outputs
        except Exception as e:
            self.logger.error(f"Forward pass failed: {str(e)}")
            return None

    def safe_criterion(
        self, criterion: torch.nn.Module, outputs: torch.Tensor, labels: torch.Tensor
    ) -> Optional[torch.Tensor]:
        """
        Safely computes the loss using the criterion.

        Args:
            criterion: The loss function.
            outputs: Model outputs.
            labels: Ground truth labels.

        Returns:
            Loss tensor or None if an error occurs.
        """
        try:
            if outputs is None:
                raise ValueError("Model outputs are None, cannot compute loss")
            loss = criterion(outputs, labels)
            return loss
        except Exception as e:
            self.logger.error(f"Loss computation (criterion) failed: {str(e)}")
            return None

    def safe_backward(self, loss: torch.Tensor) -> bool:
        """
        Safely performs backpropagation.

        Args:
            loss: The loss tensor.

        Returns:
            True if successful, False if an error occurs.
        """
        try:
            if loss is None:
                raise ValueError("Loss is None, cannot perform backpropagation")
            loss.backward()
            return True
        except Exception as e:
            self.logger.error(f"Backpropagation failed: {str(e)}")
            return False

    def safe_optimizer_step(self, optimizer: torch.optim.Optimizer) -> bool:
        """
        Safely performs an optimizer step.

        Args:
            optimizer: The optimizer.

        Returns:
            True if successful, False if an error occurs.
        """
        try:
            optimizer.step()
            return True
        except Exception as e:
            self.logger.error(f"Optimizer step failed: {str(e)}")
            return False

    def safe_scheduler_step(
        self,
        scheduler: torch.optim.lr_scheduler._LRScheduler,
        scheduler_step_method: Literal["min_val_loss", "max_val_acc"] = None,
        metric: float = None,
    ) -> bool:
        """
        Safely performs a scheduler step.

        Args:
            scheduler_step_method: Strategy for stepping ('min_val_loss' or 'max_val_acc').
            metric: Validation metric (e.g., val_loss or val_acc), required for adaptive schedulers.

        Returns:
            True if successful, False if an error occurs.
        """
        try:
            if scheduler_step_method == "min_val_loss":
                if metric is None:
                    raise ValueError(
                        "Validation loss is required for 'min_val_loss' scheduler stepping"
                    )
                scheduler.step(metric)

            elif scheduler_step_method == "max_val_acc":
                if metric is None:
                    raise ValueError(
                        "Validation accuracy is required for 'max_val_acc' scheduler stepping"
                    )
                # If higher accuracy is better, invert it for schedulers like ReduceLROnPlateau
                scheduler.step(metric)
            elif scheduler_step_method is None:
                raise ValueError("No scheduler_step_method provided")

            else:
                raise ValueError(
                    f"Unknown scheduler_step_method: {scheduler_step_method}"
                )

            return True

        except Exception as e:
            self.logger.error(f"Scheduler step failed: {str(e)}")
            return False

    def safe_predict(
        self, outputs: torch.Tensor, labels: torch.Tensor
    ) -> Tuple[Optional[torch.Tensor], Optional[int]]:
        """
        Safely computes predictions and correct count for accuracy.

        Args:
            outputs: Model outputs.

        Returns:
            Tuple of (predicted tensor, correct count) or (None, 0) if an error occurs.
        """
        try:
            if outputs is None:
                raise ValueError("Outputs are None, cannot compute predictions")
            _, predicted = outputs.max(1)  # predicted class indices
            correct = predicted.eq(labels).sum().item()  # count matches
            return predicted, correct

        except Exception as e:
            self.logger.error(f"Prediction computation failed: {str(e)}")
            return None, 0
