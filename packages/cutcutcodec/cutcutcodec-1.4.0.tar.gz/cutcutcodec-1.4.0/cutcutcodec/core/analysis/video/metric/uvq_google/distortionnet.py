#!/usr/bin/env python3

"""A modified version of the Google UVQ source file.

As the original file is under apache lisence,
I should mention that this is a modified version of the source file:

https://github.com/google/uvq/blob/main/uvq_pytorch/utils/distortionnet.py
"""

import functools

import numpy as np
import torch

from cutcutcodec.core.nn.start import load
from . import custom_nn_layers


default_distortionnet_batchnorm2d = functools.partial(
    torch.nn.BatchNorm2d, eps=0.001, momentum=0
)

# Input video size
VIDEO_HEIGHT = 720
VIDEO_WIDTH = 1280
VIDEO_CHANNELS = 3

# Input patch size (video is broken to patches and input to model)
PATCH_HEIGHT = 360
PATCH_WIDTH = 640
PATCH_DEPTH = 1

# Output feature size
DIM_HEIGHT_FEATURE = 16
DIM_WIDTH_FEATURE = 16
DIM_CHANNEL_FEATURE = 100

OUTPUT_LABEL_DIM = 26


class DistortionNet(torch.nn.Module):
    """Model to eval the distorsion."""

    def __init__(self, dropout=0.2, **kwargs):
        super().__init__()
        stochastic_depth_prob_step = 0.0125
        stochastic_depth_prob = [x * stochastic_depth_prob_step for x in range(16)]
        self.features = torch.nn.Sequential(
            custom_nn_layers.Conv2dNormActivationSamePadding(
                3,
                32,
                kernel_size=3,
                stride=2,
                activation_layer=torch.nn.SiLU,
                norm_layer=default_distortionnet_batchnorm2d,
            ),
            custom_nn_layers.MBConvSamePadding(
                32,
                1,
                16,
                3,
                1,
                stochastic_depth_prob[0],
                norm_layer=default_distortionnet_batchnorm2d,
            ),
            custom_nn_layers.MBConvSamePadding(
                16,
                6,
                24,
                3,
                2,
                stochastic_depth_prob[1],
                norm_layer=default_distortionnet_batchnorm2d,
            ),
            custom_nn_layers.MBConvSamePadding(
                24,
                6,
                24,
                3,
                1,
                stochastic_depth_prob[2],
                norm_layer=default_distortionnet_batchnorm2d,
            ),
            custom_nn_layers.MBConvSamePadding(
                24,
                6,
                40,
                5,
                2,
                stochastic_depth_prob[3],
                norm_layer=default_distortionnet_batchnorm2d,
            ),
            custom_nn_layers.MBConvSamePadding(
                40,
                6,
                40,
                5,
                1,
                stochastic_depth_prob[4],
                norm_layer=default_distortionnet_batchnorm2d,
            ),
            custom_nn_layers.MBConvSamePadding(
                40,
                6,
                80,
                3,
                2,
                stochastic_depth_prob[5],
                norm_layer=default_distortionnet_batchnorm2d,
            ),
            custom_nn_layers.MBConvSamePadding(
                80,
                6,
                80,
                3,
                1,
                stochastic_depth_prob[6],
                norm_layer=default_distortionnet_batchnorm2d,
            ),
            custom_nn_layers.MBConvSamePadding(
                80,
                6,
                80,
                3,
                1,
                stochastic_depth_prob[7],
                norm_layer=default_distortionnet_batchnorm2d,
            ),
            custom_nn_layers.MBConvSamePadding(
                80,
                6,
                112,
                5,
                1,
                stochastic_depth_prob[8],
                norm_layer=default_distortionnet_batchnorm2d,
            ),
            custom_nn_layers.MBConvSamePadding(
                112,
                6,
                112,
                5,
                1,
                stochastic_depth_prob[9],
                norm_layer=default_distortionnet_batchnorm2d,
            ),
            custom_nn_layers.MBConvSamePadding(
                112,
                6,
                112,
                5,
                1,
                stochastic_depth_prob[10],
                norm_layer=default_distortionnet_batchnorm2d,
            ),
            custom_nn_layers.MBConvSamePadding(
                112,
                6,
                192,
                5,
                2,
                stochastic_depth_prob[11],
                norm_layer=default_distortionnet_batchnorm2d,
            ),
            custom_nn_layers.MBConvSamePadding(
                192,
                6,
                192,
                5,
                1,
                stochastic_depth_prob[12],
                norm_layer=default_distortionnet_batchnorm2d,
            ),
            custom_nn_layers.MBConvSamePadding(
                192,
                6,
                192,
                5,
                1,
                stochastic_depth_prob[13],
                norm_layer=default_distortionnet_batchnorm2d,
            ),
            custom_nn_layers.MBConvSamePadding(
                192,
                6,
                192,
                5,
                1,
                stochastic_depth_prob[14],
                norm_layer=default_distortionnet_batchnorm2d,
            ),
            custom_nn_layers.MBConvSamePadding(
                192,
                6,
                320,
                3,
                1,
                stochastic_depth_prob[15],
                norm_layer=default_distortionnet_batchnorm2d,
            ),
            custom_nn_layers.Conv2dSamePadding(
                320, 100, kernel_size=(12, 20), stride=1, bias=False
            ),
        )
        self.avgpool = torch.nn.Sequential(
            torch.nn.MaxPool2d(kernel_size=(5, 13), stride=1, padding=0),
            custom_nn_layers.PermuteLayerNHWC(),
        )
        self.classifier = torch.nn.Sequential(
            torch.nn.Dropout(p=dropout),
            torch.nn.Flatten(),
            torch.nn.Linear(6400, 512, bias=True),
            torch.nn.ReLU6(),
            torch.nn.Linear(512, 26, bias=True),
            torch.nn.Sigmoid(),
        )
        load(self, kwargs.get("weights", None))  # e3cfeaa6042dc45d9016c855030c351b

    def forward(self, x):
        """Eval the model."""
        x = self.features(x)
        features = self.avgpool(x)
        label_probs = self.classifier(features)
        return features, label_probs


class DistortionNetInference:  # pylint: disable=R0902
    """Model to eval the distortion."""

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
        self.model = DistortionNet(**kwargs)
        if eval_mode:
            self.model.eval()
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

    def predict_and_get_features(self, frame) -> tuple[np.ndarray, np.ndarray]:
        """Eval the model."""
        with torch.no_grad():
            features, _ = self.model(torch.Tensor(frame))
        return (
            features.detach().numpy()
        )

    def get_features_for_all_frames(
        self,
        video: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Eval the model."""
        feature = np.ndarray(
            (
                video.shape[0],
                self.feature_height,
                self.feature_width,
                self.feature_channels,
            ),
            np.float32,
        )
        patch = np.ndarray(
            (1, self.video_channels, self.patch_height, self.patch_width),
            np.float32,
        )
        for k in range(video.shape[0]):
            for j in range(self.num_patches_y):
                for i in range(self.num_patches_x):
                    patch[0, :] = video[
                        k,
                        0,
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
