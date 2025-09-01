#!/usr/bin/env python3

"""Utils to train and create a dataset."""

import itertools
import json
import pathlib
import re
import tempfile
import typing

import cv2
import matplotlib.pyplot as plt
import numpy as np
import torch
import tqdm

from cutcutcodec.core.analysis.video.metric import ssim as compute_ssim
from cutcutcodec.core.classes.colorspace import Colorspace
from cutcutcodec.core.io.framecaster import to_rgb
from cutcutcodec.core.nn.dataaug.chain import ChainDataaug
from cutcutcodec.core.nn.dataaug.video import Transcoder, interlace
from cutcutcodec.core.nn.dataset.video import VideoDataset
from cutcutcodec.core.nn.start import save
from cutcutcodec.core.opti.parallel import map as threaded_map
from .cnn import CNN


def plot(log: typing.Optional[pathlib.Path | str | bytes] = None):
    """Draw the training curves."""
    def read(filename: pathlib.Path) -> object:
        with open(filename, "r", encoding="utf-8") as raw:
            return json.load(raw)
    log = pathlib.Path(log).expanduser()
    files = list(log.iterdir())
    train_ = {int(re.search(r"\d+", f.stem).group()): read(f) for f in files if "train" in f.name}
    val = {int(re.search(r"\d+", f.stem).group()): read(f) for f in files if "val" in f.name}
    epoch = sorted(train_)
    plt.errorbar(
        epoch,
        [np.mean(train_[e]) for e in epoch],
        yerr=[np.std(train_[e]) for e in epoch],
        capsize=5.0,
        label="train",
    )
    epoch = sorted(val)
    plt.errorbar(
        epoch,
        [np.mean(val[e]) for e in epoch],
        yerr=[np.std(val[e]) for e in epoch],
        capsize=5.0,
        label="val",
    )
    plt.xlabel("epoch")
    plt.ylabel("ssim")
    plt.legend()
    plt.show()


def train(
    dataset: VideoDataset | pathlib.Path | str | bytes,
    model: typing.Optional[CNN] = None,
    log: typing.Optional[pathlib.Path | str | bytes] = None,
):
    """Train the model.

    Parameters
    ----------
    dataset : VideoDataset or pathlike
        The dataset containing the videos and dataaug or the folder.
    model : CNN, optional
        Use the default constructor if not provided.
    log : pathlike
        The directory to store the logs.

    Examples
    --------
    >>> from cutcutcodec.core.nn.model.enhancement.train import train
    >>> # train("~/dataset/video_xiph")
    >>>
    """
    # preparation
    if not isinstance(dataset, VideoDataset):
        dataset = VideoDataset(
            dataset,
            dataaug=ChainDataaug([Transcoder("libx264"), interlace], [1, 0.1]),
            size=100_000_000,  # targeted batch data size in bytes
            shape=(480, 720),
            max_len=1,  # nbr of samples in database
            # n_min=1,  # minimum nbr of frames per video slice
        )
    if model is None:
        model = CNN()
    else:
        assert isinstance(model, CNN), model.__class__.__name__
    if log is not None:
        log = pathlib.Path(log).expanduser()
    else:
        log = pathlib.Path(tempfile.gettempdir()) / "log_train"
    log.mkdir(parents=True, exist_ok=True)

    # train
    optim = torch.optim.RAdam(model.parameters(), lr=1e-4, weight_decay=1e-7)
    train_loader, val_loader = torch.utils.data.random_split(dataset, [0.8, 0.2])
    val_loader = list(val_loader)  # frozen the validation set
    train_loader = val_loader = list(train_loader)  # for the overfiting test

    for epoch in itertools.count():
        if (log / f"ssim_train_epoch_{epoch:03d}.json").exists():
            continue

        # train
        model.train()
        ssims = []
        for (distorded, reference) in tqdm.tqdm(
            threaded_map(train_loader.__getitem__, range(len(train_loader)), maxsize=2),
            desc=f"epoch {epoch}",
            total=len(train_loader),
        ):
            optim.zero_grad()
            restored = model(distorded)
            # reference = torch.cat([  # convert lin rgb to yuv
            #     c[:, :, None]
            #     for c in Colorspace.from_default_working().to_function(
            #         Colorspace.from_default_target(), compile=False
            #     )(
            #         r=reference[:, :, 0], g=reference[:, :, 1], b=reference[:, :, 2]
            #     )
            # ], dim=2)
            # restored = torch.cat([  # convert lin rgb to yuv
            #     c[:, :, None]
            #     for c in Colorspace.from_default_working().to_function(
            #         Colorspace.from_default_target(), compile=False
            #     )(
            #         r=restored[:, :, 0], g=restored[:, :, 1], b=restored[:, :, 2]
            #     )
            # ], dim=2)
            ssim = compute_ssim(reference, restored, weights=(6, 1, 1))
            # ssim = -((reference - restored)**2).mean()
            print(f"ssim: {float(ssim):.3f}")
            ssims.append(float(ssim))
            (1.0 - ssim).sum().backward()
            optim.step()
        save(model)
        with open(log / f"ssim_train_epoch_{epoch:03d}.json", "w", encoding="utf-8") as file:
            json.dump(ssims, file)

        # validation
        model.eval()
        ssims = []
        for i, (distorded, reference) in enumerate(tqdm.tqdm(val_loader)):
            # compute loss
            with torch.no_grad():
                restored = model(distorded)
                distorded = torch.cat([  # convert lin rgb to yuv
                    c[:, :, None]
                    for c in Colorspace.from_default_working().to_function(
                        Colorspace.from_default_target()
                    )(
                        r=distorded[:, :, 0], g=distorded[:, :, 1], b=distorded[:, :, 2]
                    )
                ], dim=2)
                reference = torch.cat([  # convert lin rgb to yuv
                    c[:, :, None]
                    for c in Colorspace.from_default_working().to_function(
                        Colorspace.from_default_target()
                    )(
                        r=reference[:, :, 0], g=reference[:, :, 1], b=reference[:, :, 2]
                    )
                ], dim=2)
                restored = torch.cat([  # convert lin rgb to yuv
                    c[:, :, None]
                    for c in Colorspace.from_default_working().to_function(
                        Colorspace.from_default_target()
                    )(
                        r=restored[:, :, 0], g=restored[:, :, 1], b=restored[:, :, 2]
                    )
                ], dim=2)
                ssim = compute_ssim(reference, restored, weights=(6, 1, 1))
                ssims.append(float(ssim))
            # write images
            reference = reference[
                :, :, 3*(reference.shape[2]//6):3*(reference.shape[2]//6)+3
            ].detach()
            distorded = distorded[
                :, :, 3*(distorded.shape[2]//6):3*(distorded.shape[2]//6)+3
            ].detach()
            restored = restored[
                :, :, 3*(restored.shape[2]//6):3*(restored.shape[2]//6)+3
            ].detach()
            cv2.imwrite(
                str(log / f"epoch_{epoch:03d}_{i}_brut.png"),
                to_rgb(
                    cv2.cvtColor(
                        torch.cat([
                            c[:, :, None]
                            for c in Colorspace.from_default_target().to_function(
                                Colorspace.from_default_target_rgb()
                            )(
                                y=reference[:, :, 0], u=reference[:, :, 1], v=reference[:, :, 2]
                            )
                        ], dim=2).numpy(force=True),
                        cv2.COLOR_RGB2BGR,
                    )
                ),
            )
            cv2.imwrite(
                str(log / f"epoch_{epoch:03d}_{i}_dis.png"),
                to_rgb(
                    cv2.cvtColor(
                        torch.cat([
                            c[:, :, None]
                            for c in Colorspace.from_default_target().to_function(
                                Colorspace.from_default_target_rgb()
                            )(
                                y=distorded[:, :, 0], u=distorded[:, :, 1], v=distorded[:, :, 2]
                            )
                        ], dim=2).numpy(force=True),
                        cv2.COLOR_RGB2BGR,
                    )
                ),
            )
            cv2.imwrite(
                str(log / f"epoch_{epoch:03d}_{i}_res.png"),
                to_rgb(
                    cv2.cvtColor(
                        torch.cat([
                            c[:, :, None]
                            for c in Colorspace.from_default_target().to_function(
                                Colorspace.from_default_target_rgb()
                            )(
                                y=restored[:, :, 0], u=restored[:, :, 1], v=restored[:, :, 2]
                            )
                        ], dim=2).numpy(force=True),
                        cv2.COLOR_RGB2BGR,
                    )
                ),
            )
        with open(log / f"ssim_val_epoch_{epoch}.json", "w", encoding="utf-8") as file:
            json.dump(ssims, file)
