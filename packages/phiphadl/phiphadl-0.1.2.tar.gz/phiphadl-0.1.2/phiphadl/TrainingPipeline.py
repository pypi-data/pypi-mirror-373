import os
import shutil
from pathlib import Path
import argparse
import time
from datetime import datetime
from typing import Optional, List, Literal
import torch
import logging
from torch.utils.data import DataLoader

from .utils.LoggerColorFormatter import TerminalColorFormatter, LogColorFormatter
from .exceptionHandler.TrainingExceptionHandler import TrainingExceptionHandler


class TrainingPipeline:
    def __init__(
        self,
        model: torch.nn.Module,
        criterion: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        scheduler: Optional[torch.optim.lr_scheduler._LRScheduler] = None,
        scheduler_step_method: Literal["min_val_loss", "max_val_acc"] = None,
        train_loader: DataLoader = None,
        val_loader: DataLoader = None,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
        save_checkpoint: bool = False,
        save_methods: Optional[List[str]] = [
            "best_val_loss"
        ],
        checkpoint_folder: str = "./checkpoints/",
        log_folder: str = "./logs",
    ):
        """
        Initializes the TrainingPipeline.

        Args:
            model: The PyTorch model to train.
            criterion: The loss function.
            optimizer: The optimizer.
            scheduler: Optional learning rate scheduler.
            scheduler_step_on: Step on EPOCH based on 'min_val_loss' or 'max_val_acc'.
            train_loader: DataLoader for training data.
            val_loader: Optional DataLoader for validation data.
            device: Device to train on ('cuda' or 'cpu').
            save_checkpoint: Whether to save checkpoints.
            save_methods: Method to decide when to save ('best_val_loss', 'best_val_acc', 'every_n_epochs').
            checkpoint_folder: Directory to save checkpoints.
            log_folder: Path to save the log file.
        """
        self.model = model.to(device)
        self.criterion = criterion
        self.optimizer = optimizer
        self.scheduler = scheduler
        self.scheduler_step_method = scheduler_step_method
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.device = device
        self.save_checkpoint = save_checkpoint
        self.save_methods = save_methods
        self.save_every_n = (
            int(save_methods[2].split("_")[1]) if "every_" in save_methods[2] else None
        )
        self.checkpoint_folder = checkpoint_folder
        self.checkpoint_folder_root = checkpoint_folder
        self.log_folder = log_folder
    
        self.exception_handler = None

        ### FLAGS ###
        self.log_setup_flag = False
        self.write_log = "new"

        ### PARSE ARGUMENTS SETUP ###
        parser = argparse.ArgumentParser(add_help=True)
        parser.add_argument(
            "--write_log",
            choices=["overwrite", "new"],
            default="new",
            help="overwrite the latest log files or create new ones",
        )
        args, _ = parser.parse_known_args()
        self.write_log = args.write_log
        if self.write_log not in ["overwrite", "new"]:
            raise ValueError("self.write_log must be 'overwrite' or 'new'")

        ### LOGGING SETUP ###
        self._setup_logging_and_checkpoint()
        self.log_setup_flag = True

        ### UTILS SETUP ###
        self.best_val_loss = float("inf")
        self.best_val_acc = 0.0

    def _setup_logging_and_checkpoint(self):
        message_to_log = ""
        if not os.path.exists(self.checkpoint_folder):
            os.makedirs(self.checkpoint_folder)
            message_to_log += (
                f"Created checkpoint directory at {self.checkpoint_folder}\n"
            )
        if not os.path.exists(self.log_folder):
            os.makedirs(self.log_folder)
            message_to_log += (
                f"Created log directory at {os.path.dirname(self.log_folder)}\n"
            )

        log_root = Path(self.log_folder)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") + "_train"
        if self.write_log == "new":
            subfolder = log_root / timestamp
            subfolder.mkdir(parents=True, exist_ok=True)
            message_to_log += (
                f"🆕 [NEW LOG] Creating new log files in {str(subfolder)}\n"
            )
        elif self.write_log == "overwrite":
            subfolders = [f for f in log_root.iterdir() if f.is_dir()]
            if not subfolders:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") + "_train"
                subfolder = log_root / timestamp
                subfolder.mkdir(parents=True, exist_ok=True)
            else:
                subfolder = sorted(subfolders)[-1]
            message_to_log += (
                f"📝 [OVERWRITE LOG] Overwriting latest log file in {str(subfolder)}\n"
            )

        if hasattr(self, "logger") and self.logger.handlers:
            for handler in self.logger.handlers[:]:
                self.logger.removeHandler(handler)
                if isinstance(handler, logging.FileHandler):
                    handler.close()

        self.logger = logging.getLogger(__name__)
        self.logger.handlers.clear()
        self.logger.setLevel(logging.INFO)
        terminal_formatter = TerminalColorFormatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        log_formatter = LogColorFormatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_folder=str(subfolder),
            log_file_name='training',
        )

        file_handler = logging.StreamHandler()
        file_handler.setFormatter(log_formatter)
        self.logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(terminal_formatter)
        self.logger.addHandler(stream_handler)

        
        # Update exception handler log folder
        self.exception_handler = TrainingExceptionHandler(str(subfolder), 'training_exception')
        
        checkpoint_root = Path(self.checkpoint_folder)
        subfolder = checkpoint_root / timestamp
        subfolder.mkdir(parents=True, exist_ok=True)
        self.checkpoint_folder = str(subfolder)

        for message in message_to_log.strip().split("\n"):
            self.logger.info(message)

    def _train_epoch(self):
        """Runs one training epoch."""
        self.model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for batch in self.train_loader:
            *inputs, labels = batch
            inputs, labels = [input.to(self.device) for input in inputs], labels.to(
                self.device
            )
            self.optimizer.zero_grad()

            outputs = self.exception_handler.safe_forward(self.model, inputs)
            loss = self.exception_handler.safe_criterion(
                self.criterion, outputs, labels
            )
            self.exception_handler.safe_backward(loss)
            self.exception_handler.safe_optimizer_step(self.optimizer)

            running_loss += loss.item()
            predicted, batch_correct = self.exception_handler.safe_predict(
                outputs, labels
            )
            correct += batch_correct
            total += labels.size(0)

        epoch_loss = running_loss / len(self.train_loader)
        epoch_acc = correct / total
        return epoch_loss, epoch_acc

    def _val_epoch(self):
        """Runs one validation epoch."""
        if not self.val_loader:
            self.logger.error(
                "No validation loader provided, skipping validation epoch."
            )
            return None, None

        self.model.eval()
        running_loss = 0.0
        correct = 0
        total = 0

        with torch.no_grad():
            for batch in self.val_loader:
                *inputs, labels = batch
                inputs, labels = [input.to(self.device) for input in inputs], labels.to(
                    self.device
                )
                outputs = self.exception_handler.safe_forward(self.model, inputs)
                loss = self.exception_handler.safe_criterion(
                    self.criterion, outputs, labels
                )
                running_loss += loss.item()
                predicted, batch_correct = self.exception_handler.safe_predict(
                    outputs, labels
                )
                correct += batch_correct
                total += labels.size(0)

        epoch_loss = running_loss / len(self.val_loader)
        epoch_acc = correct / total
        return epoch_loss, epoch_acc

    def _save_checkpoint(self, epoch, val_loss=None, val_acc=None):
        """Saves the checkpoint."""
        state = {
            "epoch": epoch,
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "scheduler_state_dict": (
                self.scheduler.state_dict() if self.scheduler else None
            ),
            "val_loss": val_loss,
            "val_acc": val_acc,
        }

        saved_checkpoints = []
        if "best_val_loss" in self.save_methods and val_loss is not None:
            if val_loss < self.best_val_loss:
                self.best_val_loss = val_loss
                checkpoint_file = os.path.join(
                    self.checkpoint_folder, f"best_val_loss.pth"
                )
                torch.save(state, checkpoint_file)
                saved_checkpoints.append("best_val_loss")
        if "best_val_acc" in self.save_methods and val_acc is not None:
            if val_acc > self.best_val_acc:
                self.best_val_acc = val_acc
                checkpoint_file = os.path.join(
                    self.checkpoint_folder, f"best_val_acc.pth"
                )
                torch.save(state, checkpoint_file)
                saved_checkpoints.append("best_val_acc")
        if f"every_{self.save_every_n}_epochs" in self.save_methods:
            if (epoch + 1) % self.save_every_n == 0:
                checkpoint_file = os.path.join(
                    self.checkpoint_folder, f"checkpoint_epoch_{epoch+1}.pth"
                )
                torch.save(state, checkpoint_file)
                saved_checkpoints.append("epoch_checkpoint")
        if saved_checkpoints:
            self.logger.info(
                f"🚩 [CHECKPOINT] Saved checkpoint at {self.checkpoint_folder}: {', '.join(saved_checkpoints)}"
            )

    def train(self, epochs: int):
        """
        Runs the training loop for the specified number of epochs.
        """
        if not self.train_loader:
            raise ValueError("train_loader must be provided to train.")

        start_time = time.time()

        self.logger.info(
            f"🚀 [EVENT] Starting training for {epochs} epochs on device: {self.device}"
        )

        for epoch in range(epochs):
            train_loss, train_acc = self._train_epoch()
            val_loss, val_acc = self._val_epoch()

            if self.scheduler and self.val_loader:
                self.exception_handler.safe_scheduler_step(
                    self.scheduler, self.scheduler_step_method, val_loss
                )

            log_msg = f"✅ [EPOCH {epoch+1}/{epochs}] Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}"
            if val_loss is not None:
                log_msg += f" | Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}"
            self.logger.info(log_msg)

            self._save_checkpoint(epoch + 1, val_loss, val_acc)

        # Log training time
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.logger.info(
            f"🎉 [EVENT] Training completed in {elapsed_time:.2f} seconds."
        )

    def inference(self, inputs: List[torch.Tensor]) -> torch.Tensor:
        """
        Performs inference on a single batch of inputs using the trained model.

        Args:
            inputs: List of input tensors to the model.

        Returns:
            Model output tensor (predictions).
        """
        self.model.eval()
        with torch.no_grad():
            inputs = [x.to(self.device) for x in inputs]
            outputs = self.exception_handler.safe_forward(self.model, inputs)
            if outputs is None:
                self.logger.error("Inference failed due to forward pass error")
                return torch.tensor([]).to(self.device)
            return outputs

    ### UTILS ###    
    def clear_all_logs(self):
        """
        Deletes all logs and subfolders in the specified log folder.
        """
        log_root = Path(self.log_folder)
        if log_root.exists():
            shutil.rmtree(log_root)
            os.makedirs(log_root)

    def clear_all_checkpoints(self):
        """
        Deletes all checkpoints in the specified log folder.
        """
        log_root = Path(self.checkpoint_folder_root)
        if log_root.exists():
            shutil.rmtree(log_root)
            os.makedirs(log_root)

