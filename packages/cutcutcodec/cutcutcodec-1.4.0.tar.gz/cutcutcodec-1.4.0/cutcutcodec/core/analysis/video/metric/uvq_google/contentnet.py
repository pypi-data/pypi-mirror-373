#!/usr/bin/env python3

"""A modified version of the Google UVQ source file.

As the original file is under apache lisence,
I should mention that this is a modified version of the source file:

https://github.com/google/uvq/blob/main/uvq_pytorch/utils/contentnet.py
"""

import numpy as np
import torch

from cutcutcodec.core.nn.start import load
from . import custom_nn_layers


# Output feature size
DIM_HEIGHT_FEATURE = 16
DIM_WIDTH_FEATURE = 16
DIM_CHANNEL_FEATURE = 100

# ContentNet specs
DIM_LABEL_CONTENT = 3862


class ContentNet(torch.nn.Module):
    """Model to find the features."""

    def __init__(self, dropout: float = 0.2, **kwargs):
        super().__init__()
        stochastic_depth_prob_step = 0.0125
        stochastic_depth_prob = [x * stochastic_depth_prob_step for x in range(16)]
        self.features = torch.nn.Sequential(
            custom_nn_layers.Conv2dNormActivationSamePadding(
                3, 32, kernel_size=3, stride=2, activation_layer=torch.nn.SiLU
            ),
            custom_nn_layers.MBConvSamePadding(32, 1, 16, 3, 1, stochastic_depth_prob[0]),
            custom_nn_layers.MBConvSamePadding(16, 6, 24, 3, 2, stochastic_depth_prob[1]),
            custom_nn_layers.MBConvSamePadding(24, 6, 24, 3, 1, stochastic_depth_prob[2]),
            custom_nn_layers.MBConvSamePadding(24, 6, 40, 5, 2, stochastic_depth_prob[3]),
            custom_nn_layers.MBConvSamePadding(40, 6, 40, 5, 1, stochastic_depth_prob[4]),
            custom_nn_layers.MBConvSamePadding(40, 6, 80, 3, 2, stochastic_depth_prob[5]),
            custom_nn_layers.MBConvSamePadding(80, 6, 80, 3, 1, stochastic_depth_prob[6]),
            custom_nn_layers.MBConvSamePadding(80, 6, 80, 3, 1, stochastic_depth_prob[7]),
            custom_nn_layers.MBConvSamePadding(80, 6, 112, 5, 1, stochastic_depth_prob[8]),
            custom_nn_layers.MBConvSamePadding(112, 6, 112, 5, 1, stochastic_depth_prob[9]),
            custom_nn_layers.MBConvSamePadding(112, 6, 112, 5, 1, stochastic_depth_prob[10]),
            custom_nn_layers.MBConvSamePadding(112, 6, 192, 5, 2, stochastic_depth_prob[11]),
            custom_nn_layers.MBConvSamePadding(192, 6, 192, 5, 1, stochastic_depth_prob[12]),
            custom_nn_layers.MBConvSamePadding(192, 6, 192, 5, 1, stochastic_depth_prob[13]),
            custom_nn_layers.MBConvSamePadding(192, 6, 192, 5, 1, stochastic_depth_prob[14]),
            custom_nn_layers.MBConvSamePadding(192, 6, 320, 3, 1, stochastic_depth_prob[15]),
            custom_nn_layers.Interpolate(size=(16, 16), mode="bilinear", align_corners=False),
            custom_nn_layers.Conv2dSamePadding(320, 100, kernel_size=16, stride=1),
        )
        self.avgpool = torch.nn.AdaptiveAvgPool2d((1, 1))
        self.classifier = torch.nn.Sequential(
            torch.nn.Dropout(dropout),
            torch.nn.Flatten(),
            torch.nn.Linear(100, DIM_LABEL_CONTENT),
            torch.nn.Sigmoid(),
        )
        load(self, kwargs.get("weights", None))  # 85c8865f2c0a2a2b2eb942fa5d2be795

    def forward(self, x):
        """Eval the model."""
        features = self.features(x)
        x = self.avgpool(features)
        return features


class ContentNetInference:
    """Find the features in the image."""

    def __init__(
        self, eval_mode=True, **kwargs
    ):
        self.model = ContentNet(**kwargs)
        if eval_mode:
            self.model.eval()
        self.features_transpose = (0, 2, 3, 1)

    def predict_and_get_features(self, frame) -> tuple[np.ndarray, np.ndarray]:
        """Eval the model and get the features."""
        with torch.no_grad():
            features = self.model(torch.Tensor(np.expand_dims(frame, 0)))
        return features.detach().numpy().transpose(*self.features_transpose)

    def get_features_for_all_frames(
        self, video: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """Eval the model."""
        feature = np.ndarray(
            (
                video.shape[0],
                DIM_HEIGHT_FEATURE,
                DIM_WIDTH_FEATURE,
                DIM_CHANNEL_FEATURE,
            ),
            np.float32,
        )
        for k in range(video.shape[0]):
            frame_features = self.predict_and_get_features(
                video[k, 0, :, :, :]
            )
            feature[k, :, :, :] = frame_features
        return feature
