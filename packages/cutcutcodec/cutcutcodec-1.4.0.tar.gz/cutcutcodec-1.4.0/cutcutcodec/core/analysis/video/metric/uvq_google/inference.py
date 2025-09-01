#!/usr/bin/env python3

"""A modified version of the Google UVQ source file.

As the original file is under apache lisence,
I should mention that this is a modified version of the source file:

https://github.com/google/uvq/blob/main/uvq_pytorch/inference.py
"""

import torch

from cutcutcodec.core.filter.video.resize import resize_pad
from . import aggregationnet, compressionnet, contentnet, distortionnet

# Explicitly set input size
VIDEO_HEIGHT = 720
VIDEO_WIDTH = 1280
VIDEO_FPS = 5
VIDEO_CHANNEL = 3

# ContentNet specs
INPUT_HEIGHT_CONTENT = 496
INPUT_WIDTH_CONTENT = 496
INPUT_CHANNEL_CONTENT = 3
DIM_LABEL_CONTENT = 3862

# Output feature size
DIM_HEIGHT_FEATURE = 16
DIM_WIDTH_FEATURE = 16
DIM_CHANNEL_FEATURE = 100


class UVQInference(torch.nn.Module):
    """Main UVQ class."""

    def __init__(self):
        """Load all the sub modules."""
        super().__init__()
        self.contentnet = contentnet.ContentNetInference()
        self.compressionnet = compressionnet.CompressionNetInference()
        self.distotionnet = distortionnet.DistortionNetInference()
        self.aggregationnet = aggregationnet.AggregationNetInference()

    def forward(self, video: torch.Tensor) -> torch.Tensor:
        """Eval the metric for each batch.

        Parameters
        ----------
        video : torch.Tensor
            The video slices batch of shape (n, 5, h, w, 3).
            It has to be in RGB in range [0, 1].

        Returns
        -------
        metric : torch.Tensor
            The uvq metric for each batch of 5 frames, of shape (n,).
        """
        video = video.movedim(4, 2)  # (n, 5, 3, h, w)
        video = (video * 2.0) - 1.0  # in range [-1, 1]
        video_big = resize_pad(video, (None, None, None, VIDEO_HEIGHT, VIDEO_WIDTH))
        video_small = resize_pad(
            video, (None, None, None, INPUT_HEIGHT_CONTENT, INPUT_WIDTH_CONTENT)
        )
        content_features = (  # (n, 16, 16, 100)
            self.contentnet.get_features_for_all_frames(video=video_small)
        )
        compression_features = (  # (n, 16, 16, 100)
            self.compressionnet.get_features_for_all_frames(video=video_big.numpy(force=True))
        )
        distortion_features = (  # (n, 16, 16, 100)
            self.distotionnet.get_features_for_all_frames(video=video_big)
        )
        result = self.aggregationnet.predict(  # (n,)
            compression_features, content_features, distortion_features
        )
        return result
