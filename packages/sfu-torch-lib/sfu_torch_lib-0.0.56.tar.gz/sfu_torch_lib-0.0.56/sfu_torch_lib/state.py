import logging
import os
from typing import Any

import mlflow
import mlflow.artifacts as artifacts
import torch
from pytorch_lightning import LightningModule

import sfu_torch_lib.io as io
import sfu_torch_lib.utils as utils

logger = logging.getLogger(__name__)


def checkpoint_exists(run_id: str, filename: str = 'last.ckpt') -> bool:
    return filename in (artifact.path for artifact in artifacts.list_artifacts(run_id=run_id))


def get_localized_checkpoint_path(
    run_id: str,
    filename: str = 'last.ckpt',
    overwrite: bool = True,
    cache: bool = False,
) -> str | None:
    if not checkpoint_exists(run_id, filename):
        return None

    artifact_uri = mlflow.get_run(run_id).info.artifact_uri

    assert isinstance(artifact_uri, str)

    checkpoint_path = io.localize_cached(
        os.path.join(artifact_uri, filename),
        f'{run_id}_{filename}',
        overwrite,
        cache,
    )

    return checkpoint_path


def get_resumable_checkpoint_path(
    run_id: str | None,
    run_id_pretrained: str | None,
    filename: str = 'last.ckpt',
    overwrite: bool = True,
    cache: bool = False,
) -> tuple[str | None, bool]:
    if run_id:
        checkpoint_path = get_localized_checkpoint_path(run_id, filename, overwrite, cache)

        if checkpoint_path:
            return checkpoint_path, False

    if run_id_pretrained:
        checkpoint_path = get_localized_checkpoint_path(run_id_pretrained, filename, overwrite, cache)

        if checkpoint_path:
            return checkpoint_path, True

    return None, True


def get_checkpoint(run_id: str, filename: str = 'last.ckpt') -> dict[str, Any] | None:
    checkpoint_path = get_localized_checkpoint_path(run_id, filename)

    if checkpoint_path is None:
        return None

    with io.open(checkpoint_path) as checkpoint_file:
        checkpoint = torch.load(checkpoint_file)

    return checkpoint


def load_model[T: LightningModule](
    run_id: str,
    module_class: type[T] | None = None,
    filename: str = 'last.ckpt',
    overwrite: bool = True,
    cache: bool = False,
    **kwargs,
) -> T:
    checkpoint_path = get_localized_checkpoint_path(run_id, filename, overwrite, cache)

    assert checkpoint_path

    if module_class is not None:
        module_class_asserted = module_class

    else:
        module_class_asserted = utils.get_run_class(run_id)
        assert isinstance(module_class_asserted, T.__class__)

    with io.open(checkpoint_path) as checkpoint_file:
        model = module_class_asserted.load_from_checkpoint(checkpoint_file, **kwargs)

    return model


def load_checkpoint_state(checkpoint_path: str, model: LightningModule, strict: bool = True) -> None:
    device = torch.device('cuda') if torch.cuda.device_count() else torch.device('cpu')

    with io.open(checkpoint_path) as checkpoint_file:
        checkpoint = torch.load(checkpoint_file, device, weights_only=False)

    model.load_state_dict(checkpoint['state_dict'], strict)


def load_run_state(run_id: str, model: LightningModule, filename: str = 'last.ckpt', strict: bool = True) -> None:
    checkpoint_path = get_localized_checkpoint_path(run_id, filename)

    assert checkpoint_path

    load_checkpoint_state(checkpoint_path, model, strict)
