import bisect
import collections
import copy
import itertools
import math
from typing import List, Union, Iterable, Iterator, TypeVar, Sequence, Tuple, Optional

import numpy as np
from torch.utils.data.sampler import BatchSampler, Sampler


T = TypeVar('T')


class ImageDataset:
    def __len__(self) -> int:
        raise NotImplementedError

    def get_height_and_width(self, index: int) -> Tuple[int, int]:
        raise NotImplementedError


class GroupedBatchSampler(BatchSampler):
    def __init__(self, sampler: Union[Sampler[int], Iterable[int]], group_ids: List[int], batch_size: int) -> None:
        """
        Wraps another sampler to yield a mini-batch of indices. It enforces that the batch only contain elements from
        the same group. It also tries to provide mini-batches which follows an ordering which is as close as possible
        to the ordering from the original sampler.

        :param sampler: Base sampler.
        :param group_ids: If the sampler produces indices in range [0, N), `group_ids` must be a list of `N` ints which
        contains the group id of each sample. The group ids must be a continuous set of integers starting from 0,
        i.e. they must be in the range [0, num_groups).
        :param batch_size: Size of mini-batch.
        """
        super().__init__(sampler, batch_size, drop_last=True)
        self.group_ids = group_ids

    def __iter__(self) -> Iterator[List[int]]:
        buffer_per_group = collections.defaultdict(list)
        samples_per_group = collections.defaultdict(list)
        num_batches = 0

        for index in self.sampler:
            group_id = self.group_ids[index]

            buffer_per_group[group_id].append(index)
            samples_per_group[group_id].append(index)

            if len(buffer_per_group[group_id]) == self.batch_size:
                yield buffer_per_group[group_id]
                num_batches += 1
                del buffer_per_group[group_id]

            assert len(buffer_per_group[group_id]) < self.batch_size

        # now we have run out of elements that satisfy the group criteria, let's return the remaining
        # elements so that the size of the sampler is deterministic
        expected_num_batches = len(self)
        num_remaining = expected_num_batches - num_batches

        if num_remaining > 0:
            # for the remaining batches, take first the buffers with the largest number of elements
            for group_id, _ in sorted(buffer_per_group.items(), key=lambda x: len(x[1]), reverse=True):
                remaining = self.batch_size - len(buffer_per_group[group_id])
                samples_from_group_id = repeat_to_at_least(samples_per_group[group_id], remaining)
                buffer_per_group[group_id].extend(samples_from_group_id[:remaining])

                assert len(buffer_per_group[group_id]) == self.batch_size

                yield buffer_per_group[group_id]

                num_remaining -= 1

                if num_remaining == 0:
                    break

        assert num_remaining == 0


def repeat_to_at_least(sequence: Sequence[T], n: int) -> List[T]:
    repeat_times = math.ceil(n / len(sequence))

    repeated = list(itertools.chain.from_iterable(itertools.repeat(sequence, repeat_times)))

    return repeated


def compute_aspect_ratios(dataset: ImageDataset, indices: Optional[Sequence[int]] = None) -> List[float]:
    if indices is None:
        indices = range(len(dataset))

    aspect_ratios = [width / height for height, width in map(dataset.get_height_and_width, indices)]

    return aspect_ratios


def quantize(x: List[float], bins: list[float]) -> List[int]:
    bins = copy.deepcopy(bins)
    bins = sorted(bins)

    quantized = list(map(lambda y: bisect.bisect_right(bins, y), x))

    return quantized


def create_aspect_ratio_groups(dataset: ImageDataset, k: int = 0) -> list[int]:
    aspect_ratios = compute_aspect_ratios(dataset)

    bins = (2 ** np.linspace(-1, 1, 2 * k + 1)).tolist() if k > 0 else [1.0]
    groups = quantize(aspect_ratios, bins)  # type: ignore

    return groups
