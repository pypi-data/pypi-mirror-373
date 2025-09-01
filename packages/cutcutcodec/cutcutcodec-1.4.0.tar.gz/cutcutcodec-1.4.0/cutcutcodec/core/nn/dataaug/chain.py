#!/usr/bin/env python3

"""Merge several data augmentation together."""

import numbers
import random
import typing

import torch


class ChainDataaug:
    """Random applycation of the dataaug.

    Attributes
    ----------
    proba : list[float]
        The probability list (readonly).
    """

    def __init__(
        self,
        dataaugs: typing.Iterable[typing.Callable[[torch.Tensor], torch.Tensor]],
        probas: typing.Iterable[numbers.Real]
    ):
        """Initialise the selector.

        Parameters
        ----------
        dataaugs : list[callable]
            The dataaugs chain.
        probas : list[float], optional
            The probabilities for the dataaugs to be applyed.
        """
        assert hasattr(dataaugs, "__iter__"), dataaugs.__class__.__name__
        dataaugs = list(dataaugs)
        assert all(callable(d) for d in dataaugs), dataaugs
        if probas is None:
            probas = [1.0 for _ in range(len(dataaugs))]
        else:
            assert hasattr(probas, "__iter__"), probas.__class__.__name__
            probas = list(probas)
            assert all(isinstance(p, numbers.Real) for p in probas), probas
            assert all(0.0 <= p <= 1.0 for p in probas), probas
            assert len(dataaugs) == len(probas), (dataaugs, probas)

        self.dataaugs = dataaugs
        self._probas = probas

    def __call__(self, data: torch.Tensor) -> torch.Tensor:
        """Apply the dataaugs."""
        for dataaug, proba in zip(self.dataaugs, self._probas):
            if random.random() <= proba:
                data = dataaug(data)
        return data

    @property
    def proba(self) -> list[float]:
        """Return the probability list."""
        return self._proba
