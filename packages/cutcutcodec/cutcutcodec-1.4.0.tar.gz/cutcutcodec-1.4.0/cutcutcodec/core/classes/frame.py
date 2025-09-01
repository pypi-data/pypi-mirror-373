#!/usr/bin/env python3

"""Defines the structure of a base frame, inerit from torch array."""

import abc
import logging
import typing

import numpy as np
import torch


class Frame(torch.Tensor):
    """A General Frame.

    Attributes
    ----------
    context : object
        Any information to throw during the transformations.
    """

    def __new__(
        cls,
        data: torch.Tensor | np.ndarray | typing.Container,
        context: object = None,
        **kwargs,
    ):
        """Initialise and create the class.

        Parameters
        ----------
        context : object
            Any value to throw between the tensor operations.
        data : arraylike
            The data to use for this array. Do not copy if it is possible
        **kwargs : dict
            Transmitted to the `torch.Tensor` initialisator.
        """
        if isinstance(data, torch.Tensor):
            frame = super().__new__(cls, data, **kwargs)  # no copy
            frame.context = context
            return frame
        if isinstance(data, np.ndarray):
            return Frame.__new__(cls, torch.from_numpy(data), context=context, **kwargs)  # no copy
        logging.warning("please only intitialize a frame from a torch tensor or a numpy ndarray")
        return Frame.__new__(cls, torch.tensor(data), context=context, **kwargs)  # copy

    def __repr__(self):
        """Allow to add context to the display.

        Examples
        --------
        >>> from cutcutcodec.core.classes.frame import Frame
        >>> Frame([0.0, 1.0, 2.0], context="context_value")
        Frame([0., 1., 2.], context='context_value')
        >>>
        """
        base = super().__repr__()
        return f"{base[:-1]}, context={repr(self.context)})"

    @classmethod
    def __torch_function__(cls, func, types, args=(), kwargs=None):
        """Enable to throw `context` into the new generations.

        Examples
        --------
        >>> import torch
        >>> from cutcutcodec.core.classes.frame import Frame
        >>> class Frame_(Frame):
        ...     def check_state(self):
        ...         assert self.item()  # just for the example
        ...
        >>>
        >>> # transmission context
        >>> (frame := Frame_([.5], context="context_value"))
        Frame_([0.5000], context='context_value')
        >>> frame.clone()  # deep copy
        Frame_([0.5000], context='context_value')
        >>> torch.sin(frame)  # external call
        Frame_([0.4794], context='context_value')
        >>> frame / 2  # internal method
        Frame_([0.2500], context='context_value')
        >>> frame.numpy()  # cast in an other type
        array([0.5], dtype=float32)
        >>> frame *= 2  # inplace
        >>> frame
        Frame_([1.], context='context_value')
        >>>
        >>> # cast if state not correct
        >>> torch.concatenate([frame, frame], axis=0)  #
        tensor([1., 1.])
        >>> frame * 0  # no correct because has to be != 0
        tensor([0.])
        >>> frame *= 0
        >>> frame
        tensor([0.])
        >>>
        """
        if kwargs is None:
            kwargs = {}
        result = super().__torch_function__(func, types, args, kwargs)
        if isinstance(result, cls):
            if isinstance(args[0], cls):  # args[0] is self
                result.context = args[0].context  # args[0] is self
                try:
                    result.check_state()
                except AssertionError:
                    return torch.Tensor(result)
            else:
                return torch.Tensor(result)
        return result

    @abc.abstractmethod
    def check_state(self) -> None:
        """Apply verifications.

        Raises
        ------
        AssertionError
            If something wrong in this frame.
        """
        raise NotImplementedError

    @property
    def shape(self) -> tuple[int, ...]:
        """Solve pylint error E1136: Value 'self.shape' is unsubscriptable."""
        return tuple(super().shape)
