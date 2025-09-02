# -*- coding: utf-8 -*-
"""
The classes contained in this module allow to transform the input and output, so that its is more suitable for training a surrogate model.
They are heavily inspired by the equivalent ones in `scikit-learn`. The main differences are that they provide the analytical gradient
and a serialization in HDF5 format.
"""

from abc import ABC, abstractmethod

import h5py
import numpy as np

# String type for h5py.
H5_STR = h5py.special_dtype(vlen=str)


class Transformer(ABC):
    """Base class for all transformers."""

    @property
    @abstractmethod
    def fields(self):
        "List of fields in sklearn_scaler, hdf5 group and Transformer object."

    @abstractmethod
    def transform(self, x, inplace):
        """Apply the direct transformation."""

    @abstractmethod
    def inverse_transform(self, x, inplace):
        """Apply the inverse transformation."""

    @abstractmethod
    def transform_gradient(self, x):
        """Compute the gradient of the direct transformation."""

    @abstractmethod
    def inverse_transform_gradient(self, x):
        """Compute the gradient of the inverse transformation."""

    def _save_h5(self, group):
        """Save this transformer to a h5py `Group`.

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
        Loads this transformer from a h5py `Group`.

        Parameters
        ----------
        group : h5py.Group
            Group where this object has been saved.

        Returns
        -------
        obj : Transformer
            The saved transformer.
        """
        # Protected because this function should be called by SurrogateModel.load_h5.
        return cls(*[group[f][:] for f in cls.fields])

    @staticmethod
    def from_sklearn(sklearn_obj):
        """
        Create a new transformer, based on a scikit-learn scaler/transformer that has already been fitted.

        Parameters
        ----------
        sklearn_scaler : {sklearn.preprocessing.MinMaxScaler,
                          sklearn.preprocessing.StandardScaler,
                          sklearn.preprocessing.PowerTransformer,
                          sklearn.decomposition.PCA}
            A Scaler object from scikit-learn, that has already been fitted.

        """
        if getattr(sklearn_obj, "clip", False):
            raise ValueError(
                "clip is not supported, because it cannot be differentiated."
            )
        cls = globals().get(sklearn_obj.__class__.__name__, None)
        if cls is None:
            raise NotImplementedError(f"{sklearn_obj.__class__.__name__} not supported")
        return cls(*[getattr(sklearn_obj, f) for f in cls.fields])


class GainOffsetScaler(Transformer):
    """
    Transform features by gain and offset

    transformed = untransformed * gain + offset

    Base class for `MinMaxScaler` and `StandardScaler`.
    """

    def __init__(self, gain, offset):
        """Create a new GainOffsetScaler, based on the given gain and offset.

        Parameters
        ----------
        gain : array-like of shape (n_features)
            Per feature relative scaling of the data. Equivalent to `(max - min) / (X.max(axis=0) - X.min(axis=0))`
        offset : array-like of shape (n_features)
            Per feature adjustment for minimum. Equivalent to `min - X.min(axis=0) * self.gain_`
        """
        self.gain_ = np.asarray(gain)
        self.inv_gain_ = (
            1.0 / self.gain_
        )  # Saved because multiplying is faster than dividing.
        self.offset_ = np.asarray(offset)

    def transform(self, x, inplace=True):
        """Apply the direct transformation.

        Parameters
        ----------
        x : array-like of shape (n_points, n_features)
            Input data that will be transformed.
        inplace : bool
            `True` if the transformation must happen inplace, which means that no additional memory is allocated.

        Returns
        -------
        y : array-like of shape (n_points, n_features)
            Transformed data.
        """
        if inplace:
            x *= self.gain_
            x += self.offset_
        else:
            y = x * self.gain_ + self.offset_
            return y

    def inverse_transform(self, x, inplace=True):
        """Apply the inverse transformation.

        Parameters
        ----------
        x : array-like of shape (n_points, n_features)
            Input data that will be transformed.
        inplace : bool
            `True` if the transformation must happen inplace, which means that no additional memory is allocated.

        Returns
        -------
        y : array-like of shape (n_points, n_features)
            Transformed data.
        """
        if inplace:
            x -= self.offset_
            x *= self.inv_gain_
        else:
            y = (x - self.offset_) * self.inv_gain_
            return y

    def transform_gradient(self, x):
        """Compute the gradient of the direct transformation.

        Parameters
        ----------
        x : array-like of shape (n_points, n_features)
            Input data.

        Returns
        -------
        y : array-like of shape (n_points, n_features)
            Gradient of the direct transformation evaluated on the input data.
            Since all features are independent, the gradient is stored in compact form.
            Warning: a read-only view is returned.
        """
        y = np.broadcast_to(self.gain_, x.shape)
        return y

    def inverse_transform_gradient(self, x):
        """Compute the gradient of the inverse transformation.

        Parameters
        ----------
        x : array-like of shape (n_points, n_features)
            Input data.

        Returns
        -------
        y : array-like of shape (n_points, n_features)
            Gradient of the inverse transformation evaluated on the input data.
            Since all features are independent, the gradient is stored in compact form.
            Warning: a read-only view is returned.
        """
        y = np.broadcast_to(self.inv_gain_, x.shape)
        return y

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            test_gain = np.array_equal(self.gain_, other.gain_)
            test_offset = np.array_equal(self.offset_, other.offset_)
            return test_gain and test_offset
        return False


class MinMaxScaler(GainOffsetScaler):
    """
    Transform features by scaling each feature to a given range.

    This class is heavily inspired by the equivalent one in scikit-learn, which should be used for its construction.
    It does not provide a function to fit, but allows to transform, and provides the analytical gradient.

    transformed = untransformed * scale + min

    """

    fields = ("scale_", "min_")

    def __init__(self, scale, min):
        """
        Create a new min-max scaler, based on the given scale and min.

        Parameters
        ----------
        scale : array-like of shape (n_features)
            Per feature relative scaling of the data. Equivalent to `(max - min) / (X.max(axis=0) - X.min(axis=0))`.
        min : array-like of shape (n_features)
            Per feature adjustment for minimum. Equivalent to `min - X.min(axis=0) * self.gain_`.
        """
        GainOffsetScaler.__init__(self, scale, min)

    scale_ = property(lambda self: self.gain_)
    min_ = property(lambda self: self.offset_)


class StandardScaler(GainOffsetScaler):
    """
    Standardize features by removing the mean and scaling to unit variance.

    This class is heavily inspired by the equivalent one in scikit-learn, which should be used for its construction.
    It does not provide a function to fit, but allows to transform, and provides the analytical gradient.

    transformed = (untransformed - mean) / scale
    """

    fields = ("scale_", "mean_")

    def __init__(self, scale, mean):
        """
        Create a new standard scaler, based on the given scale and mean.

        Parameters
        ----------
        scale : array-like of shape (n_features)
            Per feature relative scaling of the data to achieve zero mean and unit variance.
            Generally this is calculated using `np.sqrt(var_)`. If a variance is zero, we
            cannot achieve unit variance, and the data is left as-is, giving a scaling factor of 1.
        mean : array-like of shape (n_features)
            The mean value for each feature in the training set.
        """
        GainOffsetScaler.__init__(
            self, 1 / np.asarray(scale), -np.asarray(mean) / scale
        )

    scale_ = property(lambda self: self.inv_gain_)
    inv_scale_ = property(lambda self: self.gain_)
    mean_ = property(lambda self: -self.offset_ * self.scale_)


class PCA(Transformer):
    """
    Principal component analysis (PCA).
    """

    fields = ("components_", "mean_", "whiten", "explained_variance_")

    def __init__(self, components, mean=None, whiten=False, explained_variance=None):
        """
        Create a new Principal component analysis (PCA).

        Parameters
        ----------
        components_ : ndarray of shape (n_components, n_features)
            Principal axes in feature space, representing the directions of maximum variance in the data.
            Equivalently, the right singular vectors of the centered input data, parallel to its eigenvectors.
            The components are sorted by decreasing explained_variance_.
        mean : ndarray of shape (n_features,), optional
            Per-feature empirical mean, estimated from the training set. The default is `None`.
        whiten : bool, optional
            When `True` the `components_` vectors are multiplied by the square root of `n_samples` and then
            divided by the singular values to ensure uncorrelated outputs with unit component-wise variances.
            Whitening will remove some information from the transformed signal (the relative variance scales
            of the components) but can sometime improve the predictive accuracy of the downstream estimators
            by making their data respect some hard-wired assumptions. The default is `False`.
        explained_variance : ndarray of shape (n_components,), optional
            The amount of variance explained by each of the selected components.
            The variance estimation uses `n_samples - 1` degrees of freedom.
            Equal to `n_components` largest eigenvalues of the covariance matrix of `x`. The default is `None`.

        Returns
        -------
        None.

        """
        # Save the fields.
        self.components_ = np.asarray(components)
        self.mean_ = np.asarray(mean)
        self.whiten = np.array(
            [whiten]
        )  # Encapsulating will allow _load_h5() to work without changes.
        self.explained_variance_ = np.asarray(
            explained_variance
        )  # Needed by _save_h5().

        # Update fields.
        self.n_components = components.shape[0]
        self.n_features = components.shape[1]
        self.explained_std_ = np.sqrt(explained_variance)
        if whiten:
            self.components_direct_ = (
                self.components_ / self.explained_std_[:, np.newaxis]
            )
            self.components_inverse_ = (
                self.components_ * self.explained_std_[:, np.newaxis]
            )
        else:
            self.components_direct_ = self.components_
            self.components_inverse_ = self.components_

    def transform(self, x, inplace=False):
        r"""
        Apply the direct transformation.

        The transformation is given by

        .. math::
          y = C^T (x - m) / \sigma

        with :math:`x` the input data, :math:`m` the mean, :math:`C` the components
        and :math:`\sigma` the explained standard deviation.

        Parameters
        ----------
        x : ndarray of shape (n_points, n_features)
            Input data that will be transformed.
        inplace : bool, optional
            Must be `False`. Although it would be possible to update the first `n_components` columns of `x`,
            we choose to not do it, so that `predict_output()` can be supported more easily.

        Returns
        -------
        y : ndarray of shape (n_points, n_components)
            Projection of `x` in the first principal components.
        """
        if inplace:
            raise ValueError("The PCA transformation cannot be done inplace.")
            # if self.mean_ is not None:
            #     x -= self.mean_
            # # Multiply by the PCA basis and rewrite the first columns.
            # np.matmul(x, self.components_direct_.T, out=x[:, : self.n_components])
        else:
            if self.mean_ is not None:
                y = x - self.mean_
            y = y @ self.components_direct_.T
            return y

    def inverse_transform(self, x, inplace):
        r"""
        Apply the inverse transformation.

        The inverse transformation is given by

        .. math::
          y = C (\sigma x) + m

        with :math:`x` the input data, :math:`m` the mean, :math:`C` the components
        and :math:`\sigma` the explained standard deviation.

        Parameters
        ----------
        x : array-like of shape (n_points, n_components)
            Input data that will be inverse-transformed.
        inplace : bool
            Since `n_features >= n_components`, it is not possible to
            apply the inverse transformation inplace. Therefore, this parameter must be `False`.

        Raises
        ------
        ValueError
            If `inplace=True`.

        Returns
        -------
        y : ndarray of shape (n_samples, n_features)
            Input data after applying the inverse PCA.

        """
        if inplace:
            raise ValueError("The PCA inverse transformation cannot be done inplace.")
        else:
            y = x @ self.components_inverse_
            if self.mean_ is not None:
                y += self.mean_
            return y

    def transform_gradient(self, x):
        """Compute the gradient of the direct transformation.

        Parameters
        ----------
        x : array-like of shape (n_points, n_features)
            Input data.

        Returns
        -------
        y : array-like of shape (n_points, n_components, n_features)
            Gradient of the direct transformation evaluated on the input data.
            Warning: a read-only view is returned.
        """
        return np.broadcast_to(
            self.components_direct_, (x.shape[0], self.n_components, self.n_features)
        )

    def inverse_transform_gradient(self, x):
        """Compute the gradient of the inverse transformation.

        Parameters
        ----------
        x : array-like of shape (n_points, n_components)
            Input data.

        Returns
        -------
        y : array-like of shape (n_points, n_features, n_components)
            Gradient of the inverse transformation evaluated on the input data.
            Warning: a read-only view is returned.
        """
        return np.broadcast_to(
            self.components_inverse_.T, (x.shape[0], self.n_features, self.n_components)
        )

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            test = np.array_equal(self.components_, other.components_)
            test = test and np.array_equal(self.mean_, other.mean_)
            test = test and np.array_equal(
                self.explained_variance_, other.explained_variance_
            )
            test = test and (self.whiten == other.whiten)
            return test
        return False


class PowerTransformer:
    """
    Factory to build power transformers.
    """

    # The fields are used by `Transformer.from_sklearn()`.
    fields = ("lambdas_", "method", "standardize")

    def __new__(cls, lambdas, method="yeo-johnson", standardize=False):
        """
        Create a new power transformer with the given parameters.

        Parameters
        ----------
        lambdas_ : array-like of shape (n_features)
            The parameters of the power transformation for the selected features.
        method : str
            The power transform method. Available methods are:
              - `"yeo-johnson"`, works with positive and negative values.
              - `"box-cox"`, only works with strictly positive values. Not implemented yet.
        standardize : bool
            The `standardize` option is not available. Please add a :py:class:`StandardScaler`.
        """
        if standardize:
            raise NotImplementedError(
                "The standardize option is not supported. Please add a StandardScaler."
            )
        if method == "yeo-johnson":
            return PowerTransformerYeoJohnson(lambdas)

        # elif method == "box-cox":
        else:
            raise NotImplementedError()


class PowerTransformerYeoJohnson(Transformer):
    """
    Power transformer with the yeo-johnson method.
    """

    fields = ("lambdas_",)

    def __init__(self, lambdas):
        """
        Create a new power transformer with the given parameters.

        Parameters
        ----------
        lambdas_ : array-like of shape (n_features)
            The parameters of the power transformation for all features.
        """
        self.lambdas_ = np.asarray(lambdas)

    # lambdas_ = property(lambda self: self.lambdas_)

    def transform(self, x, inplace=True):
        r"""Apply the direct transformation.

        The transformation can be found in `In-Kwon Yeo and Richard A. Johnson, A new family of power transformations
        to Improve normality or symmetry <https://doi.org/10.1093/biomet/87.4.954>`_, Eq. (2.1), here reported for convenience.
        
        .. math::
          y = \begin{cases}
                  \ln(x + 1)                                     &  \text{if $x \ge 0$ and $\lambda = 0$}     \\
                  ((x + 1)^\lambda - 1) / \lambda                &  \text{if $x \ge 0$ and $\lambda \neq 0$}  \\
                  -((-x + 1)^{2 - \lambda} - 1) / (2 - \lambda)  &  \text{if $x < 0$   and $\lambda \neq 2$}  \\
                  -\ln(-x + 1)                                   &  \text{if $x < 0$   and $\lambda = 2$}     \\
              \end{cases}

        where :math:`\lambda` is a feature-dependent coefficient.

        Parameters
        ----------
        x : array-like of shape (n_points, n_features)
            Input data that will be transformed.
        inplace : bool
            `True` if the transformation must happen inplace, which means that no additional memory is allocated.

        Returns
        -------
        y : array-like of shape (n_points, n_features)
            Transformed data.
        """
        # Inspired from https://github.com/scikit-learn/scikit-learn/blob/main/sklearn/preprocessing/_data.py#L3322
        if inplace:
            # Loop over the features.
            for i in range(x.shape[1]):
                # Get lambda for current feature.
                lmbda = self.lambdas_[i]

                # When x >= 0.
                if np.abs(lmbda) < np.spacing(1.0):
                    # Binary mask.
                    pos = x[:, i] >= 0.0
                    np.log1p(x[:, i], out=x[:, i], where=pos)

                else:  # lambdas_[i] != 0
                    # Binary mask.
                    pos = x[:, i] >= 0.0
                    x[pos, i] += 1.0
                    np.power(x[:, i], lmbda, out=x[:, i], where=pos)
                    x[pos, i] -= 1.0
                    x[pos, i] /= lmbda

                # When x < 0.
                if np.abs(lmbda - 2.0) > np.spacing(1.0):
                    # Binary mask.
                    neg = x[:, i] < 0.0
                    np.negative(x[:, i], out=x[:, i], where=neg)
                    x[neg, i] += 1.0
                    np.power(x[:, i], 2.0 - lmbda, out=x[:, i], where=neg)
                    x[neg, i] -= 1.0
                    x[neg, i] /= 2.0 - lmbda
                    np.negative(x[:, i], out=x[:, i], where=neg)

                else:  # lmbda == 2
                    # Binary mask.
                    neg = x[:, i] < 0.0
                    np.negative(x[:, i], out=x[:, i], where=neg)
                    np.log1p(x[:, i], out=x[:, i], where=neg)
                    np.negative(x[:, i], out=x[:, i], where=neg)

        else:  # not inplace
            y = np.zeros_like(x)

            # Loop over the features.
            for i in range(x.shape[1]):
                # Get lambda for current feature.
                lmbda = self.lambdas_[i]

                # When x >= 0.
                if np.abs(lmbda) < np.spacing(1.0):
                    # Binary mask.
                    pos = x[:, i] >= 0.0
                    y[pos, i] = np.log1p(x[pos, i])

                else:  # lmbda != 0
                    # Binary mask.
                    pos = x[:, i] >= 0.0
                    y[pos, i] = (np.power(x[pos, i] + 1.0, lmbda) - 1.0) / lmbda

                # When x < 0.
                if np.abs(lmbda - 2.0) > np.spacing(1.0):
                    # Binary mask.
                    neg = x[:, i] < 0.0
                    y[neg, i] = -(np.power(-x[neg, i] + 1.0, 2.0 - lmbda) - 1.0) / (
                        2.0 - lmbda
                    )

                else:  # lmbda == 2
                    # Binary mask.
                    neg = x[:, i] < 0.0
                    y[neg, i] = -np.log1p(-x[neg, i])

            return y

    def inverse_transform(self, x, inplace):
        r"""Apply the inverse transformation.

        The inverse transformation is:

        .. math::
          y = \begin{cases}
                  e^x - 1                                    &  \text{if $x \ge 0$ and $\lambda = 0$}     \\
                  \sqrt[\lambda]{\lambda x + 1} - 1          &  \text{if $x \ge 0$ and $\lambda \neq 0$}  \\
                  1 - (1 + x (\lambda - 2))^{1/(2-\lambda)}  &  \text{if $x < 0$   and $\lambda \neq 2$}  \\
                  1 - e^{-x}                                 &  \text{if $x < 0$   and $\lambda = 2$}     \\
              \end{cases}

        where :math:`\lambda` is a feature-dependent coefficient.

        Parameters
        ----------
        x : array-like of shape (n_points, n_features)
            Input data that will be transformed.
        inplace : bool
            `True` if the transformation must happen inplace, which means that no additional memory is allocated.

        Returns
        -------
        y : array-like of shape (n_points, n_features)
            Transformed data.
        """
        # Inspired from https://github.com/scikit-learn/scikit-learn/blob/main/sklearn/preprocessing/_data.py#L3301
        if inplace:
            # Loop over the features.
            for i in range(x.shape[1]):
                # Get lambda for current feature.
                lmbda = self.lambdas_[i]

                # When x >= 0
                if np.abs(lmbda) < np.spacing(1.0):
                    # Binary mask.
                    pos = x[:, i] >= 0.0
                    np.expm1(x[:, i], out=x[:, i], where=pos)

                else:  # lmbda != 0
                    # Binary mask.
                    pos = x[:, i] >= 0.0
                    x[pos, i] *= lmbda
                    x[pos, i] += 1.0
                    np.power(x[:, i], 1.0 / lmbda, out=x[:, i], where=pos)
                    x[pos, i] -= 1.0

                # When x < 0
                if np.abs(lmbda - 2.0) > np.spacing(1.0):
                    # Binary mask.
                    neg = x[:, i] < 0.0
                    x[neg, i] *= -(2.0 - lmbda)
                    x[neg, i] += 1.0
                    np.power(x[:, i], 1.0 / (2.0 - lmbda), out=x[:, i], where=neg)
                    np.negative(x[:, i], out=x[:, i], where=neg)
                    x[neg, i] += 1.0

                else:  # lmbda == 2
                    # Binary mask.
                    neg = x[:, i] < 0.0
                    np.negative(x[:, i], out=x[:, i], where=neg)
                    np.expm1(x[:, i], out=x[:, i], where=neg)
                    np.negative(x[:, i], out=x[:, i], where=neg)

        else:  # not inplace
            y = np.zeros_like(x)

            # Loop over the features.
            for i in range(x.shape[1]):
                # Get lambda for current feature.
                lmbda = self.lambdas_[i]

                # When x >= 0
                if np.abs(lmbda) < np.spacing(1.0):
                    # Binary mask.
                    pos = x[:, i] >= 0.0
                    y[pos, i] = np.expm1(x[pos, i])
                else:  # lmbda != 0
                    # Binary mask.
                    pos = x[:, i] >= 0.0
                    y[pos, i] = np.power(x[pos, i] * lmbda + 1.0, 1.0 / lmbda) - 1.0

                # When x < 0
                if np.abs(lmbda - 2.0) > np.spacing(1.0):
                    # Binary mask.
                    neg = x[:, i] < 0.0
                    y[neg, i] = 1.0 - np.power(
                        -(2.0 - lmbda) * x[neg, i] + 1.0, 1.0 / (2.0 - lmbda)
                    )
                else:  # lmbda == 2
                    # Binary mask.
                    neg = x[:, i] < 0.0
                    y[neg, i] = -np.expm1(-x[neg, i])

            return y

    def transform_gradient(self, x):
        r"""Compute the gradient of the Yeo Johnson direct transformation.
        
        .. math::
          y = \begin{cases}
                  1 / (1 + x)              &  \text{if $x \ge 0$ and $\lambda = 0$}     \\
                  (x + 1)^{\lambda - 1}    &  \text{if $x \ge 0$ and $\lambda \neq 0$}  \\
                  (1 - x)^{1 - \lambda}    &  \text{if $x < 0$   and $\lambda \neq 2$}  \\
                  1 / (1 - x)              &  \text{if $x < 0$   and $\lambda = 2$}     \\
              \end{cases}

        where :math:`\lambda` is a feature-dependent coefficient.

        Parameters
        ----------
        x : array-like of shape (n_points, n_features)
            Input data.

        Returns
        -------
        y : array-like of shape (n_points, n_features)
            Gradient of the transformation evaluated on the input data.
            Since all features are independent, the gradient is stored in compact form.
        """
        y = np.zeros_like(x)

        # Loop over the features.
        for i in range(x.shape[1]):
            # Get lambda for current feature.
            lmbda = self.lambdas_[i]

            # When x >= 0.
            if np.abs(lmbda) < np.spacing(1.0):
                # Binary mask.
                pos = x[:, i] >= 0.0
                y[pos, i] = 1.0 / (1.0 + x[pos, i])

            else:  # lmbda != 0
                # Binary mask.
                pos = x[:, i] >= 0.0
                y[pos, i] = np.power(x[pos, i] + 1.0, lmbda - 1.0)

            # When x < 0.
            if np.abs(lmbda - 2.0) > np.spacing(1.0):
                # Binary mask.
                neg = x[:, i] < 0.0
                y[neg, i] = np.power(1.0 - x[neg, i], 1.0 - lmbda)

            else:  # lmbda == 2
                # Binary mask.
                neg = x[:, i] < 0.0
                y[neg, i] = 1.0 / (1.0 - x[neg, i])

        return y

    def inverse_transform_gradient(self, x):
        r"""Compute the gradient of the inverse Yeo Johnson direct transformation.
        
        .. math::
          y = \begin{cases}
                  e^x                                         &  \text{if $x \ge 0$ and $\lambda = 0$}     \\
                  (\lambda x + 1)^{1/\lambda - 1}             &  \text{if $x \ge 0$ and $\lambda \neq 0$}  \\
                  (1 + x (\lambda - 2))^{1/(2-\lambda) - 1}   &  \text{if $x < 0$   and $\lambda \neq 2$}  \\
                  e^{-x}                                      &  \text{if $x < 0$   and $\lambda = 2$}     \\
              \end{cases}

        where :math:`\lambda` is a feature-dependent coefficient.

        Parameters
        ----------
        x : array-like of shape (n_points, n_features)
            Input data.

        Returns
        -------
        y : array-like of shape (n_points, n_features)
            Gradient of the inverse transformation evaluated on the input data.
            Since all features are independent, the gradient is stored in compact form.
        """
        y = np.zeros_like(x)

        # Loop over the features.
        for i in range(x.shape[1]):
            # Get lambda for current feature.
            lmbda = self.lambdas_[i]

            # When x >= 0
            if np.abs(lmbda) < np.spacing(1.0):
                # Binary mask.
                pos = x[:, i] >= 0.0
                y[pos, i] = np.exp(x[pos, i])
            else:  # lmbda != 0
                # Binary mask.
                pos = x[:, i] >= 0.0
                y[pos, i] = np.power(x[pos, i] * lmbda + 1.0, 1.0 / lmbda - 1.0)

            # When x < 0
            if np.abs(lmbda - 2.0) > np.spacing(1.0):
                neg = x[:, i] < 0.0
                y[neg, i] = np.power(
                    1.0 + (lmbda - 2.0) * x[neg, i], 1.0 / (2.0 - lmbda) - 1.0
                )
            else:  # lmbda == 2
                neg = x[:, i] < 0.0
                y[neg, i] = np.exp(-x[neg, i])

        return y

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return np.array_equal(self.lambdas_, other.lambdas_)
        return False


class StandardScalerTorch(StandardScaler):

    def __init__(self, scale, mean):
        import torch

        super().__init__(scale, mean)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.device = device
        def __np2torch(v):  # fmt: skip
            return torch.as_tensor(v).to(device)
        self.gain_ = __np2torch(self.gain_)
        self.inv_gain_ = __np2torch(self.inv_gain_)
        self.offset_ = __np2torch(self.offset_)

    def transform(self, x, inplace=True):
        import torch

        if inplace:
            raise ValueError("No inplace...")
        x = torch.as_tensor(x, device=self.device, dtype=torch.float32)
        return super().transform(x, inplace)

    def inverse_transform(self, x, inplace=True):
        import torch

        if inplace:
            raise ValueError("No inplace...")
        x = torch.as_tensor(x, device=self.device, dtype=torch.float32)
        return super().inverse_transform(x, inplace)

    def transform_gradient(self, x):
        import torch

        return torch.broadcast_to(self.gain_, x.shape).numpy()

    def inverse_transform_gradient(self, x):
        import torch

        return torch.broadcast_to(self.inv_gain_, x.shape).numpy()

    def __eq__(self, other):
        import torch

        if isinstance(other, self.__class__):
            test_gain = torch.equal(self.gain_, other.gain_)
            test_offset = torch.equal(self.offset_, other.offset_)
            return test_gain and test_offset
        return False
