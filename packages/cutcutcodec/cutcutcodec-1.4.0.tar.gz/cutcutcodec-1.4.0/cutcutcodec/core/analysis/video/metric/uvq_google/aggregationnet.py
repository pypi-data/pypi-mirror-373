#!/usr/bin/env python3

"""A modified version of the Google UVQ source file.

As the original file is under apache lisence,
I should mention that this is a modified version of the source file:

https://github.com/google/uvq/blob/main/uvq_pytorch/utils/aggregationnet.py
"""

import numpy as np
import torch

from cutcutcodec.core.nn.start import load


NUM_CHANNELS_PER_SUBNET = 100
NUM_FILTERS = 256
CONV2D_KERNEL_SIZE = (1, 1)
MAXPOOL2D_KERNEL_SIZE = (16, 16)

BN_DEFAULT_EPS = 0.001
BN_DEFAULT_MOMENTUM = 1
DROPOUT_RATE = 0.2


class AggregationNet(torch.nn.Module):
    """Basic class to average all scores."""

    def __init__(self, subnets: list[str]):
        super().__init__()
        self.subnets = subnets
        self.conv1 = torch.nn.Conv2d(
            len(subnets) * NUM_CHANNELS_PER_SUBNET,
            NUM_FILTERS,
            kernel_size=CONV2D_KERNEL_SIZE,
            bias=True,
        )
        self.bn1 = torch.nn.BatchNorm2d(
            NUM_FILTERS, eps=BN_DEFAULT_EPS, momentum=BN_DEFAULT_MOMENTUM
        )
        self.relu1 = torch.nn.ReLU()
        self.maxpool1 = torch.nn.MaxPool2d(kernel_size=MAXPOOL2D_KERNEL_SIZE)
        self.dropout1 = torch.nn.Dropout(p=DROPOUT_RATE)
        self.linear1 = torch.nn.Linear(bias=True, in_features=NUM_FILTERS, out_features=1)

    def forward(self, features: dict[str, torch.Tensor]):
        """Mix all features."""
        x = (
            features[self.subnets[0]]
            if len(self.subnets) == 1
            else torch.cat([features[i] for i in self.subnets], dim=1)
        )
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu1(x)
        x = self.maxpool1(x)
        x = self.dropout1(x)
        x = torch.nn.Flatten()(x)
        x = self.linear1(x)
        return x


class AggregationNetInference(torch.nn.Module):
    """Average all the scores."""

    def __init__(self, eval_mode=True, **kwargs):
        super().__init__()
        self.models = torch.nn.ModuleList(
            [
                AggregationNet(["compression", "content", "distortion"]),
                AggregationNet(["compression", "content", "distortion"]),
                AggregationNet(["compression", "content", "distortion"]),
                AggregationNet(["compression", "content", "distortion"]),
                AggregationNet(["compression", "content", "distortion"]),
            ]
        )
        if eval_mode:
            self.eval()
        load(self, kwargs.get("weights", None))  # f65da816bf4ca0bb91a24e3ba62fb02b

    def forward(
        self,
        compression_features: np.ndarray,
        content_features: np.ndarray,
        distortion_features: np.ndarray,
    ) -> float:
        """Compute the final score."""
        feature_results = []
        with torch.no_grad():
            for model in self.models:
                res = model(
                    {
                        "compression": torch.Tensor(
                            compression_features.transpose(0, 3, 1, 2)
                        ),
                        "content": torch.Tensor(content_features.transpose(0, 3, 1, 2)),
                        "distortion": torch.Tensor(
                            distortion_features.transpose(0, 3, 1, 2)
                        ),
                    }
                )
                feature_results.append(res)
        return torch.cat(feature_results, dim=1).mean(dim=1)

    def predict(self, *args, **kwargs) -> float:
        """Compute the final score."""
        return self.forward(*args, **kwargs)
