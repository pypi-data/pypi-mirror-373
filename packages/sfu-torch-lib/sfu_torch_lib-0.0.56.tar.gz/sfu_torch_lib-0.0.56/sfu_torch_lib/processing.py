import functools
from typing import Callable, List, Optional, Sequence, Tuple, Union

import numpy as np
import torch
import torchvision.transforms.functional as functional
from PIL.Image import Image
from torch import Tensor
from torch.nn import Module
from torchvision.transforms import (
    ColorJitter,
    GaussianBlur,
    RandomCrop,
    RandomHorizontalFlip,
    RandomResizedCrop,
    RandomRotation,
)
from torchvision.transforms.functional import InterpolationMode

import sfu_torch_lib.tree as tree_lib


class ResizeTree(Module):
    def __init__(self, size: Tuple[int, int], interpolations: Sequence[InterpolationMode]) -> None:
        super().__init__()

        self.size = size
        self.interpolations = interpolations

    def forward(self, tree):
        return tree_lib.map_tree(
            lambda image, interpolation: functional.resize(image, self.size, interpolation),  # type: ignore
            tree,
            self.interpolations,
        )


class ResizedCropTree(Module):
    def __init__(
        self,
        size: Tuple[int, int],
        interpolations: Sequence[InterpolationMode],
    ) -> None:
        super().__init__()

        self.size = size
        self.interpolations = interpolations

    def resize_crop(self, image: Union[Image, Tensor], interpolation: InterpolationMode) -> Union[Image, Tensor]:
        crop_height, crop_width = self.size
        _, image_height, image_width = functional.get_dimensions(image)  # type: ignore

        assert image_height >= crop_height and image_width >= crop_width

        if image_height - crop_height > image_width - crop_width:
            target_height = round(crop_width * image_height / image_width)
            target_width = crop_width
        else:
            target_height = crop_height
            target_width = round(crop_height * image_width / image_height)

        image = functional.resize(image, [target_height, target_width], interpolation)  # type: ignore
        image = functional.center_crop(image, self.size)  # type: ignore

        return image

    def forward(self, tree):
        return tree_lib.map_tree(self.resize_crop, tree, self.interpolations)


class RandomCropTree(Module):
    def __init__(self, size: Tuple[int, int]) -> None:
        super().__init__()
        self.size = size

    def forward(self, tree):
        i, j, h, w = RandomCrop.get_params(tree[0], self.size)

        tree = tree_lib.map_tree(lambda image: functional.crop(image, i, j, h, w), tree)

        return tree


class RandomResizedCropTree(Module):
    def __init__(
        self,
        size: Tuple[int, int],
        interpolations: Sequence[InterpolationMode],
        scale: Tuple[float, float] = (0.08, 1.0),
        ratio: Tuple[float, float] = (3.0 / 4.0, 4.0 / 3.0),
    ) -> None:
        super().__init__()

        self.size = size
        self.interpolations = interpolations
        self.scale = scale
        self.ratio = ratio

    def forward(self, tree):
        i, j, h, w = RandomResizedCrop.get_params(tree[0], self.scale, self.ratio)  # type: ignore

        tree = tree_lib.map_tree(
            lambda image, interpolation: functional.resized_crop(image, i, j, h, w, self.size, interpolation),  # type: ignore
            tree,
            self.interpolations,
        )

        return tree


class RandomBoundedResizedCropTree(Module):
    def __init__(
        self,
        size: Tuple[int, int],
        interpolations: Sequence[InterpolationMode],
        scale: Tuple[float, float] = (0.08, 1.0),
        ratio: Tuple[float, float] = (3.0 / 4.0, 4.0 / 3.0),
    ) -> None:
        super().__init__()

        self.size = size
        self.interpolations = interpolations
        self.scale = scale
        self.ratio = ratio

    def forward(self, tree):
        scale_minimum, scale_maximum = self.scale
        crop_height, crop_width = self.size
        _, image_height, image_width = functional.get_dimensions(tree[0])

        scale_minimum = max(scale_minimum, crop_height / image_height, crop_width / image_width)
        scale_maximum = max(scale_maximum, scale_minimum)
        scale = (scale_minimum, scale_maximum)

        i, j, h, w = RandomResizedCrop.get_params(tree[0], scale, self.ratio)  # type: ignore

        tree = tree_lib.map_tree(
            lambda image, interpolation: functional.resized_crop(image, i, j, h, w, self.size, interpolation),  # type: ignore
            tree,
            self.interpolations,
        )

        return tree


class RandomHorizontalFlipTree(RandomHorizontalFlip):
    def forward(self, tree):
        flip = torch.rand(1) < self.p

        tree = tree_lib.map_tree(lambda image: functional.hflip(image) if flip else image, tree)

        return tree


class ColorJitterTree(ColorJitter):
    @staticmethod
    def transform(function_indices, brightness_factor, contrast_factor, saturation_factor, hue_factor, image):
        for function_index in function_indices:
            if function_index == 0 and brightness_factor is not None:
                image = functional.adjust_brightness(image, brightness_factor)
            elif function_index == 1 and contrast_factor is not None:
                image = functional.adjust_contrast(image, contrast_factor)
            elif function_index == 2 and saturation_factor is not None:
                image = functional.adjust_saturation(image, saturation_factor)
            elif function_index == 3 and hue_factor is not None:
                image = functional.adjust_hue(image, hue_factor)

        return image

    def forward(self, tree):
        transform = functools.partial(
            self.transform,
            *self.get_params(self.brightness, self.contrast, self.saturation, self.hue),  # type: ignore
        )

        new_images = tree_lib.map_tree(transform, tree)

        return new_images


class ToTensorTree(Module):
    def __init__(self, *dtypes: np.dtype) -> None:
        super().__init__()

        self.dtypes = dtypes

    def forward(self, tree):
        return tree_lib.map_tree(lambda image, dtype: torch.from_numpy(np.array(image, dtype)), tree, self.dtypes)


class ConvertImageTree(Module):
    def __init__(self, *modes: Optional[str]) -> None:
        super().__init__()

        self.modes = modes

    @staticmethod
    def transform(image: Image, mode: Optional[str]) -> Image:
        return image.convert(mode) if mode is not None else image

    def forward(self, tree):
        return tree_lib.map_tree(self.transform, tree, self.modes)


class EncodeImageTree(Module):
    def __init__(self, means: Optional[Tensor] = None, scales: Optional[Tensor] = None) -> None:
        super().__init__()

        self.means = means
        self.scales = scales

    def transform(self, tensor: Tensor) -> Tensor:
        tensor = torch.permute(tensor, (2, 0, 1))
        tensor -= self.means[:, None, None] if self.means is not None else 0
        tensor /= self.scales[:, None, None] if self.scales is not None else 255

        return tensor

    def forward(self, tree):
        return tree_lib.map_tree(self.transform, tree)


class RandomRotationTree(Module):
    def __init__(
        self,
        degrees: float | tuple[float, float],
        interpolations: Sequence[InterpolationMode],
        expand: bool = False,
        center: Optional[Tuple[float, float]] = None,
        fill: Union[float, List[float]] = 0.0,
    ) -> None:
        super().__init__()

        self.degrees = [-degrees, degrees] if isinstance(degrees, float) else list(degrees)  # type: ignore
        self.interpolations = interpolations
        self.expand = expand
        self.center = center
        self.fill = fill

    def forward(self, tree):
        angle = RandomRotation.get_params(self.degrees)

        new_tree = tree_lib.map_tree(
            lambda image, interpolation: functional.rotate(
                img=image,
                angle=angle,
                interpolation=interpolation,
                expand=self.expand,
                center=self.center,  # type: ignore
                fill=self.fill,  # type: ignore
            ),
            tree,
            self.interpolations,
        )

        return new_tree


class GaussianBlurTree(GaussianBlur):
    def forward(self, tree):
        sigma = self.get_params(self.sigma[0], self.sigma[1])  # type: ignore

        new_tree = tree_lib.map_tree(
            lambda image,: functional.gaussian_blur(image, self.kernel_size, [sigma, sigma]),  # type: ignore
            tree,
        )

        return new_tree


class SelectTree(Module):
    def __init__(self, paths) -> None:
        super().__init__()

        self.paths = paths

    def forward(self, tree):
        return tree_lib.select_tree(tree, self.paths)


class ComposeTree(Module):
    def __init__(self, steps: List[Tuple[List[int], Callable]]) -> None:
        super().__init__()

        self.steps = steps

    def forward(self, tree):
        for paths, function in self.steps:
            tree = tree_lib.map_tree_subset(function, tree, paths)

        return tree


def with_sequence(function: Callable):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        transformation = function(*args, **kwargs)
        return lambda x: transformation(x) if isinstance(x, Sequence) else transformation((x,))[0]

    return wrapper
