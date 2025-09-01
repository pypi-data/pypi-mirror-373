#!/usr/bin/env python3

"""Implement a convolutive network for video enhancement."""

import torch

from cutcutcodec.core.filter.video.resize import resize
from cutcutcodec.core.nn.start import load


class CNN(torch.nn.Module):
    """Improve RGB image quality keeping the resolution."""

    def __init__(self, dropout: float = 0.05, **kwargs):
        """Initialise the layers.

        Parameters
        ----------
        dropout : float, default=0.05
            The dropout rate after all layers.
        """
        super().__init__()
        self.layer1 = torch.nn.Sequential(  # (n, 1, 3*c, h, w) -> (n, 3*4, c, h, w)
            torch.nn.Conv3d(
                1, 12, (9, 3, 3), padding=(4, 1, 1), padding_mode="replicate", stride=(3, 1, 1)
            ),
            torch.nn.ELU(),
            torch.nn.Conv3d(12, 12, (1, 3, 3), padding=(0, 1, 1)),
            torch.nn.ELU(),
            torch.nn.Dropout(dropout),
        )
        self.layer2 = torch.nn.Sequential(  # (n, 3*4, c, h, w) -> (n, 3*8, c, h/2, w/2)
            torch.nn.Conv3d(12, 24, (1, 5, 5), padding=(0, 2, 2), stride=(1, 2, 2)),
            torch.nn.ELU(),
            torch.nn.Dropout(dropout),
            torch.nn.Conv3d(24, 24, (1, 3, 3), padding=(0, 1, 1)),
            torch.nn.ELU(),
            torch.nn.Dropout(dropout),
        )
        self.layer3 = torch.nn.Sequential(  # (n, 3*8, c, h/2, w/2) -> (n, 3*16, c, h/4, w/4)
            torch.nn.Conv3d(24, 48, (1, 5, 5), padding=(0, 2, 2), stride=(1, 2, 2)),
            torch.nn.ELU(),
            torch.nn.Dropout(dropout),
            torch.nn.Conv3d(48, 48, (1, 3, 3), padding=(0, 1, 1)),
            torch.nn.ELU(),
            torch.nn.Dropout(dropout),
        )
        self.middle = torch.nn.Sequential(
            # (n, 3*16, c, h/4, w/4) -> (n, 3*32, c, h/8, w/8)
            torch.nn.Conv3d(48, 96, (1, 5, 5), padding=(0, 2, 2), stride=(1, 2, 2)),
            torch.nn.ELU(),
            torch.nn.Dropout(dropout),
            # temporal exploration
            torch.nn.Conv3d(96, 96, (3, 3, 3), padding=(1, 1, 1)),
            torch.nn.ELU(),
            torch.nn.Dropout(dropout),
            # (n, 3*32, c, h/8, w/8) -> (n, 3*16, c, h/4, w/4)
            torch.nn.ConvTranspose3d(96, 48, (1, 4, 4), padding=(0, 1, 1), stride=(1, 2, 2)),
            torch.nn.ELU(),
            torch.nn.Dropout(dropout),
        )
        self.layer3rev = torch.nn.Sequential(  # (n, 3*16 * 2, c, h/4, w/4) -> (n, 3*8, c, h/2, w/2)
            torch.nn.ConvTranspose3d(96, 48, (1, 4, 4), padding=(0, 1, 1), stride=(1, 2, 2)),
            torch.nn.ELU(),
            torch.nn.Dropout(dropout),
            torch.nn.Conv3d(48, 24, (1, 3, 3), padding=(0, 1, 1)),
            torch.nn.ELU(),
            torch.nn.Dropout(dropout),
        )
        self.layer2rev = torch.nn.Sequential(  # (n, 3*8 * 2, c, h/2, w/2) -> (n, 3*4, c, h, w)
            torch.nn.ConvTranspose3d(48, 24, (1, 4, 4), padding=(0, 1, 1), stride=(1, 2, 2)),
            torch.nn.ELU(),
            torch.nn.Dropout(dropout),
            torch.nn.Conv3d(24, 12, (1, 3, 3), padding=(0, 1, 1)),
            torch.nn.ELU(),
            torch.nn.Dropout(dropout),
        )
        self.layer1rev = torch.nn.Sequential(  # (n, 3*4 * 2, c, h, w) -> (n, 1, 3*c, h, w)
            torch.nn.ConvTranspose3d(24, 12, (9, 5, 5), padding=(3, 2, 2), stride=(3, 1, 1)),
            torch.nn.ELU(),
            torch.nn.Dropout(dropout),
            torch.nn.Conv3d(12, 9, (1, 3, 3), padding=(0, 1, 1)),
            torch.nn.ELU(),
            torch.nn.Conv3d(9, 1, (1, 3, 3), padding=(0, 1, 1)),
        )
        load(self, kwargs.get("weights", None))

    def forward(self, video: torch.Tensor) -> torch.Tensor:  # pylint: disable=W0221
        """Improve the quality of the middle frame of the 5 consecutives rgb frames.

        Parameters
        ----------
        video : torch.Tensor
            The contanenation of 5 or more video batched frames
            in standard rgb linear format of shape (n, h, w, 3*f).

        Returns
        -------
        middle_frame : torch.Tensor
            The enhanced third frame of the sequence, of shape (n, h, w, 3*f).

        Examples
        --------
        >>> import torch
        >>> from cutcutcodec.core.nn.model.enhancement.cnn import CNN
        >>> CNN()(torch.rand((2, 128, 256, 15))).shape
        torch.Size([2, 128, 256, 15])
        >>>
        """
        assert isinstance(video, torch.Tensor), video.__class__.__name__
        assert video.dtype.is_floating_point, video.dtype
        assert video.ndim >= 3, video.shape
        if video.ndim != 4:
            return self.forward(video.reshape(-1, *video.shape[-3:])).reshape(*video.shape)
        assert video.shape[-1] % 3 == 0, video.shape

        shape = (video.shape[0], 8*(video.shape[1]//8), 8*(video.shape[2]//8))
        lat0 = resize(video, shape, copy=True)
        ispos = lat0 > 1e-6
        lat0[ispos] = lat0[ispos]**(1.0/2.2)  # to non linear
        lat0 = lat0.movedim(-1, -3)[..., None, :, :, :]  # (n, h, w, 3*c) -> (n, 1, 3*c, h, w)

        lat1 = self.layer1(lat0)
        lat2 = self.layer2(lat1)
        lat3 = self.layer3(lat2)
        lat4 = self.middle(lat3)
        lat3 = self.layer3rev(torch.cat([lat4, lat3], dim=-4))
        lat2 = self.layer2rev(torch.cat([lat3, lat2], dim=-4))
        lat1 = self.layer1rev(torch.cat([lat2, lat1], dim=-4))

        lat0 = lat1[..., 0, :, :, :].movedim(-3, -1)  # (n, 1, 3*c, h, w) -> (n, h, w, 3*c)
        ispos = lat0 > 1e-6
        lat0[ispos] = lat0[ispos]**2.2  # back to linear
        lat0 = resize(lat0, video.shape, copy=False)
        return lat0
