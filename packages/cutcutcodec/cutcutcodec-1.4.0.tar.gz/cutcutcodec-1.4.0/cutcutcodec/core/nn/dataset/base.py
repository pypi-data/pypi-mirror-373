#!/usr/bin/env python3

"""Basic generic dataloader."""

import logging
import numbers
import pathlib
import typing

import torch


class Dataset(torch.utils.data.Dataset):
    """Select files managing the probability.

    Examples
    --------
    >>> from cutcutcodec.core.nn.dataset.base import Dataset
    >>> from cutcutcodec.utils import get_project_root
    >>> def selector(path) -> bool:
    ...     return path.suffix == ".py"
    ...
    >>> dataset = Dataset(get_project_root(), selector, max_len=128)
    >>> len(dataset)
    128
    >>> dataset[0].relative_to(get_project_root())
    PosixPath('__init__.py')
    >>> dataset[1].relative_to(get_project_root())
    PosixPath('__main__.py')
    >>> dataset[2].relative_to(get_project_root())
    PosixPath('doc.py')
    >>> dataset[3].relative_to(get_project_root())
    PosixPath('utils.py')
    >>> dataset[4].relative_to(get_project_root())
    PosixPath('config/__init__.py')
    >>> dataset[5].relative_to(get_project_root())
    PosixPath('core/__init__.py')
    >>> dataset[6].relative_to(get_project_root())
    PosixPath('testing/__init__.py')
    >>>
    """

    def __init__(
        self,
        root: pathlib.Path | str | bytes,
        selector: typing.Callable[[pathlib.Path], bool],
        **kwargs,
    ):
        """Initialise and create the class.

        Parameters
        ----------
        root : pathlike
            The root folder containing all the files of the dataset.
        selector : callable
            Function that take a file pathlib.Path and return True to keep it or False to reject.
        follow_symlinks : bool, default=False
            Follow the symbolink links if set to True.
        max_len : int, optional
            The maximum number of files contained in the dataset.
        decision_depth : int, default=1
            The threshold level before to flatten the tree.
            If 0, all the file have the same proba to be drawn.
            If 1, the decision tree has only one root node
            If n, the decision tree has a maximum of n decks.
        """
        root = pathlib.Path(root).expanduser().resolve()
        assert root.is_dir(), root
        assert callable(selector), selector.__class__.__name__
        assert isinstance(kwargs.get("follow_symlinks", False), bool), \
            kwargs["follow_symlinks"].__class__.__name__
        if kwargs.get("max_len", None) is not None:
            assert isinstance(kwargs["max_len"], numbers.Integral), \
                kwargs["max_len"].__class__.__name__
            assert kwargs["max_len"] > 0, kwargs["max_len"]
        assert isinstance(kwargs.get("decision_depth", 1), numbers.Integral), \
            kwargs["decision_depth"].__class__.__name__
        assert kwargs.get("decision_depth", 1) >= 0, kwargs["decision_depth"]
        self._root = root
        self._selector = selector
        self._follow_symlinks = kwargs.get("follow_symlinks", False)
        self._max_len = None if kwargs.get("max_len", None) is None else int(kwargs["max_len"])
        self._decision_depth = int(kwargs.get("decision_depth", 1))
        self._tree: list[pathlib.Path | list] = self.scan()

    def __getitem__(self, idx: int, *, _tree=None) -> pathlib.Path:
        """Pick out a file from the dataset.

        Parameters
        ----------
        idx : int
            The index of the file, has to be in [0, len(self)[.

        Returns
        -------
        file : pathlib.Path
            The absolute path of the file.

        Notes
        -----
        This method should be overwritten.
        """
        assert isinstance(idx, int), idx.__class__.__name__
        tree = _tree or self._tree
        files = [f for f in tree if isinstance(f, pathlib.Path)]
        dirs_len = len(tree) - len(files)  # assume sorted files then dirs
        if not dirs_len:
            file = files[idx % len(files)]
            logging.info("the file %s if yield twice", file)
            return file
        if idx < len(files):
            return files[idx]
        idx, dir_idx = divmod(idx-len(files), dirs_len)
        return Dataset.__getitem__(self, idx, _tree=tree[dir_idx+len(files)])

    def __len__(self, *, _tree=None) -> int:
        """Return the number of images contained in the dataset."""
        tree = _tree or self._tree
        size = sum(1 if isinstance(e, pathlib.Path) else self.__len__(_tree=e) for e in tree)
        if self._max_len:
            size = min(self._max_len, size)
        return size

    def scan(self, *, _root=None, _depth=0) -> list[pathlib.Path | list]:
        """Rescan the dataset to update the properties."""
        if _root is None:
            self._tree = []
            tree = self._tree  # reference
            root = _root or self._root
        else:
            tree = []
            root = _root

        # scan
        items = sorted(root.iterdir())
        tree.extend(f for f in items if f.is_file() and self._selector(f))
        dirs = [
            self.scan(_root=d, _depth=_depth+1) for d in items
            if d.is_dir() or (self._follow_symlinks and d.is_symlink())
        ]

        # filter and flatten
        if _depth >= self._decision_depth:
            tree.extend(f for d in dirs if d for f in d)
        else:
            tree.extend(d for d in dirs if d)

        return tree
