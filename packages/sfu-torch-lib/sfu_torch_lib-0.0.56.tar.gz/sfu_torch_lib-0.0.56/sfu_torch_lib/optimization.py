import functools
from typing import Tuple, Sequence, Iterator, Optional, NamedTuple, Union, List

import torch
import torch.autograd as autograd
from torch import Tensor
from torch.optim import Optimizer  # type: ignore


class LossArguments(NamedTuple):
    target_losses: Union[Tensor, Sequence[Tensor]]
    adaptive_loss: Optional[Tensor] = None
    scale_factor: float = 1.0


def scale_tensor(tensor: Tensor, scale: Union[float, Tensor] = 1.0) -> Tensor:
    return tensor * scale if scale != 1 else tensor


def get_parameters(optimizer: Optimizer) -> Iterator[Tensor]:
    yield from (
        parameter
        for parameter_group in optimizer.param_groups
        for _, parameters in parameter_group.items()
        for parameter in (parameters if isinstance(parameters, list) else [parameters])
        if torch.is_tensor(parameter) and parameter.requires_grad
    )


def manual_step(optimizer: Optimizer, loss: Tensor, allow_unused: bool = False) -> None:
    optimizer.zero_grad()

    parameters = list(get_parameters(optimizer))
    gradients = autograd.grad(loss, parameters, retain_graph=True, allow_unused=allow_unused)

    for parameter, gradient in zip(parameters, gradients):
        parameter.grad = gradient

    optimizer.step()


def calculate_norms(
    gradients_first: Sequence[Optional[Tensor]],
    gradients_second: Sequence[Optional[Tensor]],
) -> Tuple[Tensor, Tensor]:
    norm_first, norm_second = functools.reduce(
        lambda first, second: (first[0] + second[0], first[1] + second[1]),
        (
            (torch.sum(gradient_first**2), torch.sum(gradient_second**2))
            for gradient_first, gradient_second in zip(gradients_first, gradients_second)
            if gradient_first is not None and gradient_second is not None
        ),
    )

    norm_first, norm_second = torch.sqrt(norm_first), torch.sqrt(norm_second)

    return norm_first, norm_second


def combine_gradients(
    gradients_first: Sequence[Optional[Tensor]],
    gradients_second: Sequence[Optional[Tensor]],
    bidirectional: bool = True,
    scale_factor_first: Union[float, Tensor] = 1.0,
    scale_factor_second: Union[float, Tensor] = 1.0,
) -> Iterator[Optional[Tensor]]:
    norm_first, norm_second = calculate_norms(gradients_first, gradients_second)

    scale_factor_first *= torch.minimum(norm_first, norm_second) / norm_first
    scale_factor_first = scale_factor_first if bidirectional else 1.0

    scale_factor_second *= torch.minimum(norm_first, norm_second) / norm_second

    for gradient_first, gradient_second in zip(gradients_first, gradients_second):
        if gradient_first is not None and gradient_second is not None:
            yield scale_tensor(gradient_first, scale_factor_first) + scale_tensor(gradient_second, scale_factor_second)

        elif gradient_first is not None:
            yield scale_tensor(gradient_first, scale_factor_first)

        elif gradient_second is not None:
            yield scale_tensor(gradient_second, scale_factor_second)

        else:
            yield None


def combine_gradients_losses(losses: Sequence[Tensor], parameters: Sequence[Tensor]) -> Iterator[Optional[Tensor]]:
    yield from functools.reduce(
        lambda first, second: combine_gradients(list(first), list(second)),
        (autograd.grad(loss, parameters, retain_graph=True, allow_unused=True) for loss in losses),  # type: ignore
    )


def collect_gradients(parameters: Sequence[Tensor], losses: Sequence[LossArguments]) -> Iterator[List[Tensor]]:
    collected_gradients = []

    for loss in losses:
        target_losses = [loss.target_losses] if isinstance(loss.target_losses, Tensor) else loss.target_losses
        gradients = combine_gradients_losses(target_losses, parameters)

        if loss.adaptive_loss is None:
            gradients = (
                scale_tensor(gradient, loss.scale_factor) if gradient is not None else gradient
                for gradient in gradients
            )

        else:
            gradients = combine_gradients(
                gradients_first=list(gradients),
                gradients_second=autograd.grad(loss.adaptive_loss, parameters, retain_graph=True, allow_unused=True),
                bidirectional=False,
                scale_factor_second=loss.scale_factor,
            )

        collected_gradients.append(gradients)

    yield from ([gradient for gradient in gradients if gradient is not None] for gradients in zip(*collected_gradients))


def step_adaptive_clipping(optimizer: Optimizer, losses: Sequence[LossArguments]) -> None:
    optimizer.zero_grad()

    parameters = list(get_parameters(optimizer))
    gradients = collect_gradients(parameters, losses)

    for parameter, gradient in zip(parameters, gradients):
        if len(gradient) > 0:
            parameter.grad = torch.add(*gradient)

    optimizer.step()
