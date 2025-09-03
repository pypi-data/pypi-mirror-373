import functools
import logging
import os
import sys
import traceback
from logging import StreamHandler
from typing import Any, Callable, TextIO

import lightning_fabric.loggers.logger as logger_lib
import mlflow
import torch
from mlflow.entities import RunTag
from mlflow.tracking import MlflowClient
from mlflow.utils.mlflow_tags import MLFLOW_RUN_NAME
from pytorch_lightning import LightningModule, Trainer
from pytorch_lightning.callbacks import ModelCheckpoint
from pytorch_lightning.loggers import MLFlowLogger as MLFlowLoggerBase
from torch import Tensor

import sfu_torch_lib.io as io
import sfu_torch_lib.parameters as parameters_lib
import sfu_torch_lib.utils as utils


class MLFlowLogger(MLFlowLoggerBase):
    def __init__(
        self,
        run_name: str | None = None,
        tracking_uri: str | None = os.getenv('MLFLOW_TRACKING_URI'),
        tags: dict[str, Any] | None = None,
        save_dir: str | None = './mlruns',
        prefix: str = '',
        artifact_location: str | None = None,
        synchronous: bool | None = None,
    ) -> None:
        super().__init__(
            run_name=run_name,
            tracking_uri=tracking_uri,
            tags=tags,
            save_dir=save_dir,
            prefix=prefix,
            artifact_location=artifact_location,
            synchronous=synchronous,
        )

        self.logger = logging.getLogger(__name__)

    @property  # type: ignore[misc]
    @logger_lib.rank_zero_experiment
    def experiment(self) -> MlflowClient:
        if self._run_id and self._experiment_id:
            return self._mlflow_client

        self.tags = self.tags or {}

        if self._run_name is not None:
            if MLFLOW_RUN_NAME in self.tags:
                self.logger.warning(
                    f'The tag {MLFLOW_RUN_NAME} is found in tags. The value will be overridden by {self._run_name}.'
                )

            self.tags[MLFLOW_RUN_NAME] = self._run_name

        run = mlflow.active_run() or mlflow.start_run()

        self._mlflow_client.log_batch(
            run_id=run.info.run_id,
            tags=[RunTag(key, str(value)) for key, value in self.tags.items()],
        )

        self._run_id = run.info.run_id
        self._experiment_id = run.info.experiment_id
        self._experiment_name = mlflow.get_experiment(run.info.experiment_id).name

        return self._mlflow_client


class MLFlowModelCheckpoint(ModelCheckpoint):
    def __init__(self, patience: int = 0, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.patience = patience
        self.mlflow_epoch = 0
        self.mlflow_model_score: Tensor | None = None

    def state_dict(self) -> dict[str, Any]:
        return {'mlflow_model_score': self.mlflow_model_score}

    def load_state_dict(self, state_dict: dict[str, Any]) -> None:
        self.mlflow_model_score = state_dict['mlflow_model_score']

    @staticmethod
    def log_artifact(local_file: str, filename: str = 'last.ckpt') -> None:
        bucket, key = io.get_bucket_and_key(mlflow.get_artifact_uri())
        destination_path = os.path.join(key, filename)

        io.upload_s3(bucket, destination_path, local_file)

    def has_new_model(self) -> bool:
        if self.best_model_score is None:
            return False

        if self.mlflow_model_score is None:
            return True

        is_better = bool({'min': torch.lt, 'max': torch.gt}[self.mode](self.best_model_score, self.mlflow_model_score))

        return is_better

    def update_model(self, trainer: Trainer) -> None:
        if self.has_new_model() and io.exists(self.best_model_path):
            self.log_artifact(self.best_model_path)

            self.mlflow_model_score = self.best_model_score
            self.mlflow_epoch = trainer.current_epoch

    def on_train_epoch_end(self, trainer: Trainer, pl_module: LightningModule) -> None:
        super().on_train_epoch_end(trainer, pl_module)

        if trainer.current_epoch - self.mlflow_epoch >= self.patience:
            self.update_model(trainer)

    def on_train_end(self, trainer: Trainer, pl_module: LightningModule) -> None:
        super().on_train_end(trainer, pl_module)
        self.update_model(trainer)

    def on_exception(self, trainer: Trainer, pl_module: LightningModule, exception: BaseException) -> None:
        super().on_exception(trainer, pl_module, exception)
        self.update_model(trainer)


class StreamPersister:
    def __init__(self, stream: TextIO) -> None:
        self.stream = stream
        self.path = io.generate_path(f'{stream.name.strip("<>")}.log', prefix=None)
        self.file = open(self.path, mode='w')
        self.encoding = 'utf-8'

    def write(self, message: str) -> None:
        self.stream.write(message)
        self.file.write(message)

    def flush(self) -> None:
        self.stream.flush()
        self.file.flush()


def add_params(function: Callable) -> Callable:
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        parameters = parameters_lib.get_script_parameters(function, ignore_keyword_arguments=False)
        mlflow.log_params(parameters)

        return function(*args, **kwargs)

    return wrapper


def log(function: Callable, override: bool = utils.to_bool_or_false(os.getenv('DEVELOPMENT_MODE'))) -> Callable:
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        if override:
            return function(*args, **kwargs)

        sys.stdout = StreamPersister(sys.stdout)
        sys.stderr = StreamPersister(sys.stderr)

        handler = StreamHandler(sys.stderr.file)

        for name in logging.root.manager.loggerDict:
            logger = logging.getLogger(name)

            if not logger.propagate:
                logger.addHandler(handler)

        try:
            return function(*args, **kwargs)

        except Exception as exception:
            sys.stderr.write(f'{exception}\n{traceback.format_exc()}')
            raise exception

        finally:
            sys.stdout.flush()
            sys.stderr.flush()
            mlflow.log_artifact(sys.stdout.path)
            mlflow.log_artifact(sys.stderr.path)

    return wrapper


def install(function: Callable, override: bool = utils.to_bool_or_false(os.getenv('DEVELOPMENT_MODE'))) -> Callable:
    return log(add_params(function), override)


def get_metrics(run_id: str | None = None) -> dict[str, float]:
    if not run_id:
        run = mlflow.active_run()

        if run:
            run_id = run.info.run_id

    metrics = mlflow.get_run(run_id).data.metrics if run_id else {}

    return metrics
