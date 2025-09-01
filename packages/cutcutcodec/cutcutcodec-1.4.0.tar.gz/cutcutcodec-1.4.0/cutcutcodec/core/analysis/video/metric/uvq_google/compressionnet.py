#!/usr/bin/env python3

"""A modified version of the Google UVQ source file.

As the original file is under apache lisence,
I should mention that this is a modified version of the source file:

https://github.com/google/uvq/blob/main/uvq_pytorch/utils/compressionnet.py
"""

import numpy as np
import torch

from cutcutcodec.core.nn.start import load
from . import custom_nn_layers


# Input video size
VIDEO_HEIGHT = 720
VIDEO_WIDTH = 1280
VIDEO_CHANNELS = 3

# Input patch size (video is broken to patches and input to model)
PATCH_HEIGHT = 180
PATCH_WIDTH = 320
PATCH_DEPTH = 5

# Output feature size
DIM_HEIGHT_FEATURE = 16
DIM_WIDTH_FEATURE = 16
DIM_CHANNEL_FEATURE = 100

OUTPUT_LABEL_DIM = 1


class CompressionNet(torch.nn.Module):  # pylint: disable=R0902
    """Model to eval the compresion artifacts."""

    def __init__(self, **kwargs):
        super().__init__()
        self.inception_block1 = custom_nn_layers.InceptionMixedBlock()
        self.final_conv3d = torch.nn.Conv3d(
            1024, 100, kernel_size=(1, 3, 7), stride=1, bias=False
        )
        self.avgpool_3d = torch.nn.AvgPool3d(kernel_size=(1, 4, 4), stride=1)
        self.conv3d_0c = custom_nn_layers.Conv3DSamePadding(
            100, 1, kernel_size=(1, 1, 1), stride=(1, 1, 1), bias=True
        )
        self.sigmoid = torch.nn.Sigmoid()
        self.nonlinear1 = torch.nn.Linear(1600, 1600, bias=True)
        self.relu = torch.nn.ReLU()
        self.nonlinear2 = torch.nn.Linear(1600, 1600, bias=True)
        load(self, kwargs.get("weights", None))  # 631ac8be291fd6c627e6b3b54ce37fdd

    def forward(self, x):
        """Eval the nn."""
        inception_b1 = self.inception_block1(x)
        inception_v1_conv3d = self.final_conv3d(inception_b1)
        x = self.avgpool_3d(inception_v1_conv3d)
        features = inception_v1_conv3d.squeeze(dim=2)
        x = self.conv3d_0c(x)
        x = torch.mean(x, dim=(0, 1, 2))
        compress_level_orig = self.sigmoid(x)
        reshape_3 = features.permute(0, 2, 3, 1).reshape(features.shape[0], -1)
        non_linear1 = self.nonlinear1(reshape_3)
        non_linear1 = self.relu(non_linear1)
        _ = self.nonlinear2(non_linear1)
        return features, compress_level_orig


class CompressionNetInference:  # pylint: disable=R0902
    """Give a score about compression artifact."""

    def __init__(  # pylint: disable=R0913,R0917
        self,
        eval_mode=True,
        video_height=VIDEO_HEIGHT,
        video_width=VIDEO_WIDTH,
        video_channels=VIDEO_CHANNELS,
        patch_height=PATCH_HEIGHT,
        patch_width=PATCH_WIDTH,
        depth=PATCH_DEPTH,
        feature_channels=DIM_CHANNEL_FEATURE,
        feature_height=DIM_HEIGHT_FEATURE,
        feature_width=DIM_WIDTH_FEATURE,
        label_dim=OUTPUT_LABEL_DIM,
        **kwargs
    ):
        self.model = CompressionNet(**kwargs)
        if eval_mode:
            self.model.eval()
        self.features_transpose = (0, 2, 3, 1)
        self.num_patches_x = int(video_width / patch_width)
        self.num_patches_y = int(video_height / patch_height)
        self.feature_channels = feature_channels
        self.feature_height = feature_height
        self.feature_width = feature_width
        self.patch_width = patch_width
        self.patch_height = patch_height
        self.video_width = video_width
        self.video_height = video_height
        self.video_channels = video_channels
        self.depth = depth
        self.patch_feature_height = int(feature_height / self.num_patches_y)
        self.patch_feature_width = int(feature_width / self.num_patches_x)
        self.label_dim = label_dim

    def predict_and_get_features(self, patch) -> tuple[np.ndarray, np.ndarray]:
        """Eval the model on one frame."""
        with torch.no_grad():
            features, _ = self.model(torch.Tensor(patch))
        return (
            features.detach().numpy().transpose(*self.features_transpose)
        )

    def get_features_for_all_frames(
        self,
        video: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Eval the model on all frames."""
        feature = np.ndarray(
            (
                video.shape[0],
                self.feature_height,
                self.feature_width,
                self.feature_channels,
            ),
            np.float32,
        )
        video = video.transpose(0, 2, 1, 3, 4)
        patch = np.ndarray(
            (
                1,
                self.video_channels,
                self.depth,
                self.patch_height,
                self.patch_width,
            ),
            np.float32,
        )

        for k in range(video.shape[0]):
            for j in range(self.num_patches_y):
                for i in range(self.num_patches_x):
                    patch[0, :] = video[
                        k,
                        :,
                        :,
                        j * self.patch_height: (j + 1) * self.patch_height,
                        i * self.patch_width: (i + 1) * self.patch_width,
                    ]
                    patch_feature = self.predict_and_get_features(patch)
                    feature[
                        k,
                        j * self.patch_feature_height: (j + 1) * self.patch_feature_height,
                        i * self.patch_feature_width: (i + 1) * self.patch_feature_width,
                        :,
                    ] = patch_feature
        return feature
