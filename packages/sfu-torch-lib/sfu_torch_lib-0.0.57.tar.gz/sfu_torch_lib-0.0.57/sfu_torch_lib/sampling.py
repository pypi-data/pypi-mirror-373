import math
import random
from typing import Iterator, Optional, TypeVar, Sequence, Sized

import torch
from torch import Generator
from torch.utils.data import Dataset, Sampler


TCovariant = TypeVar('TCovariant', covariant=True)


class RandomSubsetSequenceSampler(Sampler[int]):
    def __init__(self, data_source: Sized, num_samples: int, generator: Optional[Generator] = None) -> None:
        super().__init__(data_source)

        generator if generator else get_generator()
        dataset_size = len(data_source)

        assert num_samples <= dataset_size

        self.num_samples = num_samples
        self.indices = torch.randperm(dataset_size, generator=generator).tolist()
        self.start_index = 0

    def __len__(self) -> int:
        return self.num_samples

    def __iter__(self) -> Iterator[int]:
        indices = self.indices[self.start_index:self.start_index + self.num_samples]

        if len(indices) < self.num_samples:
            self.start_index = self.num_samples - len(indices)
            indices += self.indices[:self.start_index]
        else:
            self.start_index += self.num_samples

        yield from indices


class RandomSubset(Dataset[TCovariant], Sized):
    def __init__(self, dataset: Sequence[TCovariant], size: int) -> None:
        self.dataset = dataset
        self.size = min(size, len(dataset))

    def __len__(self) -> int:
        return self.size

    def __getitem__(self, index: int) -> TCovariant:
        remainder = len(self.dataset) % self.size
        group_size = len(self.dataset) // self.size
        group_size += 1 if index < remainder else 0

        index_subjacent = index + self.size * random.randrange(group_size)
        element = self.dataset[index_subjacent]

        return element


def get_num_steps(dataset_size: int, batch_size: int, frequency: int = 10) -> int:
    return max(1, math.floor(dataset_size / batch_size / frequency))


def get_generator() -> Generator:
    seed = int(torch.empty((), dtype=torch.int64).random_().item())
    generator = Generator()
    generator.manual_seed(seed)

    return generator
