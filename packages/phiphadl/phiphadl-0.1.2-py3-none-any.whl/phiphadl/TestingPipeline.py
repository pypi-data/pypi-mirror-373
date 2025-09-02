import os
import shutil
from pathlib import Path
import argparse
from datetime import datetime
import torch
import torch.nn.functional as F
import logging
from torch.utils.data import DataLoader
from typing import Optional, List
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, roc_curve, auc, classification_report
import seaborn as sns

from .utils.LoggerColorFormatter import TerminalColorFormatter, LogColorFormatter
from .exceptionHandler.TrainingExceptionHandler import TrainingExceptionHandler


class TestingPipeline:
    def __init__(
        self,
        model: torch.nn.Module,
        criterion: torch.nn.Module,
        test_loader: DataLoader = None,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
        log_folder: str = "./logs",
        load_checkpoint: Optional[str] = None,
        plot_confusion_matrix: bool = False,
        plot_roc_auc: bool = False,
        classification_report: bool = False,
        num_classes: int = 3,  # Default to 3 classes as per your example
    ):
        """
        Initializes the TestingPipeline.

        Args:
            model: The PyTorch model to evaluate.
            criterion: The loss function for evaluation.
            test_loader: DataLoader for test data.
            device: Device to evaluate on ('cuda' or 'cpu').
            log_folder: Path to save the log file and plots.
            load_checkpoint: Path to a checkpoint file to load model weights (optional).
            plot_confusion_matrix: Whether to plot and save the confusion matrix.
            plot_roc_auc: Whether to plot and save ROC-AUC curves.
            classification_report: Whether to generate and save the classification report.
            num_classes: Number of classes for classification (used for ROC-AUC and report).
        """
        self.model = model.to(device)
        self.criterion = criterion
        self.test_loader = test_loader
        self.device = device
        self.log_folder = log_folder
        self.load_checkpoint = load_checkpoint
        self.plot_confusion_matrix = plot_confusion_matrix
        self.plot_roc_auc = plot_roc_auc
        self.classification_report = classification_report
        self.num_classes = num_classes

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
            raise ValueError("write_log must be 'overwrite' or 'new'")

        ### LOGGING SETUP ###
        self._setup_logging()
        self.log_setup_flag = True

        ### EXCEPTION HANDLER SETUP ###
        self.log_subfolder = self._get_log_subfolder()
        self.exception_handler = TrainingExceptionHandler(str(self.log_subfolder), 'testing_exception')

        ### LOAD CHECKPOINT ###
        if self.load_checkpoint:
            self._load_checkpoint()

    def _get_log_subfolder(self) -> Path:
        """Helper method to get the log subfolder path."""
        log_root = Path(self.log_folder)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") + "_test"
        if self.write_log == "new":
            subfolder = log_root / timestamp
        elif self.write_log == "overwrite":
            subfolders = [f for f in log_root.iterdir() if f.is_dir()]
            subfolder = sorted(subfolders)[-1] if subfolders else log_root / timestamp
        return subfolder

    def _setup_logging(self):
        """Sets up logging for the testing pipeline."""
        message_to_log = ""
        if not os.path.exists(self.log_folder):
            os.makedirs(self.log_folder)
            message_to_log += f"Created log directory at {self.log_folder}\n"

        log_root = Path(self.log_folder)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") + "_test"
        if self.write_log == "new":
            subfolder = log_root / timestamp
            subfolder.mkdir(parents=True, exist_ok=True)
            message_to_log += f"🆕 [NEW LOG] Creating new log files in {str(subfolder)}\n"
        elif self.write_log == "overwrite":
            subfolders = [f for f in log_root.iterdir() if f.is_dir()]
            if not subfolders:
                subfolder = log_root / timestamp
                subfolder.mkdir(parents=True, exist_ok=True)
            else:
                subfolder = sorted(subfolders)[-1]
            message_to_log += f"📝 [OVERWRITE LOG] Overwriting latest log file in {str(subfolder)}\n"

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
            log_file_name='testing',
        )

        file_handler = logging.StreamHandler()
        file_handler.setFormatter(log_formatter)
        self.logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(terminal_formatter)
        self.logger.addHandler(stream_handler)

        for message in message_to_log.strip().split("\n"):
            self.logger.info(message)

    def _load_checkpoint(self):
        """Loads model weights from a checkpoint file."""
        if not os.path.exists(self.load_checkpoint):
            self.logger.error(f"Checkpoint file {self.load_checkpoint} does not exist.")
            raise FileNotFoundError(f"Checkpoint file {self.load_checkpoint} not found.")
        
        checkpoint = torch.load(self.load_checkpoint, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.logger.info(f"📍 [EVENT] Loaded checkpoint from {self.load_checkpoint}")

    def _plot_confusion_matrix(self, y_true: np.ndarray, y_pred: np.ndarray):
        """Plots and saves the confusion matrix."""
        cm = confusion_matrix(y_true, y_pred)
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        
        # Save the plot
        cm_path = self.log_subfolder / 'confusion_matrix.png'
        plt.savefig(cm_path)
        plt.close()
        self.logger.info(f"📈 [EVENT] Saved confusion matrix to {cm_path}")

    def _plot_roc_auc(self, y_true: np.ndarray, y_score: np.ndarray):
        """Plots and saves ROC-AUC curves for each class."""
        plt.figure(figsize=(8, 6))
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c']  # Distinct colors for up to 3 classes
        for i in range(self.num_classes):
            y_true_binary = (y_true == i).astype(int)
            fpr, tpr, _ = roc_curve(y_true_binary, y_score[:, i])
            roc_auc = auc(fpr, tpr)
            plt.plot(fpr, tpr, color=colors[i % len(colors)], lw=2,
                     label=f'Class {i} (AUC = {roc_auc:.2f})')
        
        plt.plot([0, 1], [0, 1], 'k--', lw=2)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC-AUC Curves')
        plt.legend(loc="lower right")
        
        # Save the plot
        roc_path = self.log_subfolder / 'roc_auc.png'
        plt.savefig(roc_path)
        plt.close()
        self.logger.info(f"📈 [EVENT] Saved ROC-AUC curves to {roc_path}")

    def _generate_classification_report(self, y_true: np.ndarray, y_pred: np.ndarray):
        """Generates and saves the classification report."""
        report = classification_report(y_true, y_pred, digits=4)
        self.logger.info(f"Classification Report:\n{report}")
        
        # Save the report to a file
        report_path = self.log_subfolder / 'classification_report.txt'
        with open(report_path, 'w') as f:
            f.write(report)
        self.logger.info(f"📈 [EVENT] Saved classification report to {report_path}")

    def evaluate(self):
        """
        Evaluates the model on the test dataset.

        Returns:
            Tuple of (test_loss, test_acc) or (None, None) if test_loader is not provided.
        """
        if not self.test_loader:
            self.logger.error("No test loader provided, skipping evaluation.")
            return None, None

        self.model.eval()
        running_loss = 0.0
        correct = 0
        total = 0
        all_preds = []
        all_labels = []
        all_scores = []

        self.logger.info(f"🚀 [EVENT] Starting evaluation on device: {self.device}")

        with torch.no_grad():
            for batch in self.test_loader:
                *inputs, labels = batch
                inputs, labels = [input.to(self.device) for input in inputs], labels.to(self.device)
                outputs = self.exception_handler.safe_forward(self.model, inputs)
                loss = self.exception_handler.safe_criterion(self.criterion, outputs, labels)
                running_loss += loss.item()
                predicted, batch_correct = self.exception_handler.safe_predict(outputs, labels)
                correct += batch_correct
                total += labels.size(0)

                # Collect predictions and scores for visualization/report
                if self.plot_confusion_matrix or self.plot_roc_auc or self.classification_report:
                    all_preds.append(predicted.cpu().numpy())
                    all_labels.append(labels.cpu().numpy())
                    all_scores.append(F.softmax(outputs, dim=1).cpu().numpy())

        test_loss = running_loss / len(self.test_loader)
        test_acc = correct / total
        self.logger.info(f"✅ [EVALUATION] Test Loss: {test_loss:.4f}, Test Acc: {test_acc:.4f}")

        # Generate visualizations and report if requested
        if (self.plot_confusion_matrix or self.plot_roc_auc or self.classification_report) and all_preds:
            y_true = np.concatenate(all_labels)
            y_pred = np.concatenate(all_preds)
            y_score = np.concatenate(all_scores)

            if self.plot_confusion_matrix:
                self._plot_confusion_matrix(y_true, y_pred)
            if self.plot_roc_auc:
                self._plot_roc_auc(y_true, y_score)
            if self.classification_report:
                self._generate_classification_report(y_true, y_pred)

        return test_loss, test_acc

    def inference(self, inputs: List[torch.Tensor]) -> torch.Tensor:
        """
        Performs inference on a single batch of inputs using the model.

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


    