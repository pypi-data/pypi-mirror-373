# -*- coding: utf-8 -*-
"""
The classes contained in this module allow to find when a set of points is contained in the domain.
"""

from abc import ABC, abstractmethod

import h5py
import numpy as np

# String type for h5py.
H5_STR = h5py.special_dtype(vlen=str)


class GenericDomain(ABC):
    """Base class for all domains."""

    @property
    @abstractmethod
    def fields(self):
        """List of fields in hdf5 group and GenericDomain object."""

    @abstractmethod
    def in_domain(self, x):
        """Check that the input points are inside the domain."""

    def _save_h5(self, group):
        """Save this domain to a h5py `Group`.

        Parameters
        ----------
        group : h5py.Group
            Group where this object will be saved.
        """
        group.create_dataset("type", data=self.__class__.__name__, dtype=H5_STR)
        for f in self.fields:
            group.create_dataset(f, data=getattr(self, f))

    @classmethod
    def _load_h5(cls, group):
        """
        Load this domain from a h5py `Group`.

        Parameters
        ----------
        group : h5py.Group
            Group where this object has been saved.

        Returns
        -------
        obj : GenericDomain
            The saved domain.
        """
        # Protected because this function should be called by SurrogateModel.load_h5.
        return cls(*[group[f][:] for f in cls.fields])


class BoxDomain(GenericDomain):
    """Implements a n-dimensional box domain."""

    fields = ["min", "max"]

    def __init__(self, min, max):
        """Create a new `BoxDomain`, based on the given min and max for each feature.

        Parameters
        ----------
        min : array-like of shape (n_features)
            Minimum for each feature.
        max : array-like of shape (n_features)
            Maximum for each feature.
        """
        self.min = np.asarray(min)
        self.max = np.asarray(max)
        assert np.all(np.greater_equal(self.max, self.min))

    def in_domain(self, x):
        """Check that the input points are inside the domain.

        Parameters
        ----------
        x : array-like of shape (n_points, n_features)
            Input points.

        Returns
        -------
        y : array-like of shape (n_points, )
            Array with `True` if a point is inside the domain and `False` otherwise.
        """
        # Test x >= min for each dimension.
        test_min = np.greater_equal(x, self.min)

        # Test x <= max for each dimension.
        test_max = np.less_equal(x, self.max)

        # Test min <= x <= max for each dimension.
        test_minmax = np.logical_and(test_min, test_max)

        # Test min <= x <= max for all dimensions.
        return np.all(test_minmax, axis=1)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            test_min = np.array_equal(self.min, other.min)
            test_max = np.array_equal(self.max, other.max)
            return test_min and test_max
        return False
