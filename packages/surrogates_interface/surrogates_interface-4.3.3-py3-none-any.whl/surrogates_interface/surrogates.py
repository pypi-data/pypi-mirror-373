# -*- coding: utf-8 -*-
"""
This module provides a model-agnostic interface to surrogate models.
"""

import pickle
import warnings
from abc import abstractmethod
from enum import IntEnum, auto

import h5py
import numpy as np

from surrogates_interface.domains import *  # noqa: F401,F403
from surrogates_interface.transformers import *  # noqa: F401,F403

# String type for h5py.
H5_STR = h5py.special_dtype(vlen=str)


class ADMode(IntEnum):
    """
    Enumeration used to select if the automatic differentiation must be applied in forward or reverse mode.
    """

    #: Forward mode automatic differentiation.
    FWD = auto()
    #: Reverse mode automatic differentiation.
    REV = auto()


class SurrogateModel:
    """
    Class that stores and evaluates an existing surrogate model.

    This class cannot be used directly, because some of its functions are abstract.
    For a TensorFlow model, the user should use `TensorFlowModel`.

    Parameters
    ----------
    model : -
        Surrogate model.
    input_transformers : list-like of Transformer, optional
        List of input transformers, which will be applied from the first till the last.
    output_transformers : list-like of Transformer, optional
        List of output transformers, which will be applied from the first till the last.
    n_inputs : int
        Number of inputs (that is, input features).
    input_names : list-like of str, optional
        Names of the inputs.
    n_outputs : int
        Number of outputs (that is, output features).
    output_names : list-like of str, optional
        Names of the outputs.
    domain : GenericDomain
        Input domain of the training data.
    metadata : dict of array-like, optional
        Metadata associated to the surrogate model.
    """

    def __init__(
        self,
        model,
        input_transformers=(),
        output_transformers=(),
        input_names=(),
        output_names=(),
        n_inputs=None,
        n_outputs=None,
        domain=None,
        metadata={},
    ):
        """


        Parameters
        ----------
        model : -
            Surrogate model.
        input_transformers : list-like of Transformer, optional
            List of input transformers, which will be applied from the first till the last.
        output_transformers : list-like of Transformer, optional
            List of output transformers, which will be applied from the first till the last.
        input_names : list-like of str, optional
            Names of the input channels.
            If not provided, the inputs will be named `x_0`, `x_1`, ..., `x_n_inputs`.
        output_names : list-like of str, optional
            Names of the output channels.
            If not provided, the outputs will be named `y_0`, `y_1`, ..., `y_n_outputs`.
        n_inputs : int, optional
            Number of inputs (that is, input features). If not provided it will be inferred from `input_names`.
            It is used to compute the Jacobian and by the OpenMDAO wrappers.
        n_outputs : int, optional
            Number of outputs (that is, output features). If not provided it will be inferred from `output_names`.
            It is used to compute the Jacobian and by the OpenMDAO wrappers.
        domain : GenericDomain
            Input domain of the training data.
        metadata : dict of array-like, optional
            Metadata associated to the surrogate model.
        """
        self.model = model
        self.input_transformers = input_transformers
        self.output_transformers = output_transformers
        self.domain = domain
        self.metadata = {k: np.asarray(v) for k, v in metadata.items()}
        if len(input_names) > 0:
            self.input_names = input_names
            if n_inputs is not None:
                assert n_inputs == len(
                    input_names
                ), "The length of input_names must match n_inputs."
                self.n_inputs = n_inputs
            else:
                self.n_inputs = len(input_names)
        else:
            if n_inputs is not None:
                self.n_inputs = n_inputs
                self.input_names = [f"x_{i}" for i in range(n_inputs)]
        if len(output_names) > 0:
            self.output_names = output_names
            if n_outputs is not None:
                assert n_outputs == len(
                    output_names
                ), "The length of output_names must match n_outputs."
                self.n_outputs = n_outputs
            else:
                self.n_outputs = len(output_names)
        else:
            if n_outputs is not None:
                self.n_outputs = n_outputs
                self.output_names = [f"y_{i}" for i in range(n_outputs)]

    def _save_model(self, file_name, *args, **kwargs):
        """
        Save a generic surrogate model.

        Parameters
        ----------
        file_name : str, path-like
            File path where the model will be saved.
        *args : list
            Additional `args` are passed to the function that saves the model.
        **kwargs : dict
            Additional `kwargs` are passed to the function that saves the model.

        Returns
        -------
        None.

        """
        # Protected because normally the user does not want to call it.
        raise NotImplementedError()

    def save_h5(self, model_path, extra_data_path=None, *args, **kwargs):
        """
        Save the SurrogateModel object.

        The model will be stored into 2 files, one for the surrogate model itself,
        and the other for the extra data (input/output transformers, channel names, ...).
        The file for the extra data is saved in HDF5 format.

        Parameters
        ----------
        model_path : str
            File path where the model will be saved.
        extra_data_path : str, bytes, h5f.FileID, None
            Name of file (bytes or str), or an instance of `h5f.FileID` to bind to an existing file identifier,
            or a file-like object where the extra data will be saved.
            If None (default), the extra data is appended to the model h5 file
        *args : -
            Additional `args` are passed to `_save_model()`, which saves the surrogate model itself.
        **kwargs : -
            Additional `kwargs` are passed to `_save_model()`, which saves the surrogate model itself.

        Returns
        -------
        None.
        """
        # Save the surrogate model.
        self._save_model(model_path, *args, **kwargs)

        # Test if the model file is in HDF5 format, and therefore we can append the extra data.
        # This code is not covered because it raises the exception with TensorFlow 2.15, but does not with TensorFlow 2.10.
        # The associated test is: test_tensorflow_and_openmdao._test_save_h5_extra_data_to_non_h5_model_error
        if extra_data_path is None and not h5py.is_hdf5(model_path):  # pragma: no cover
            raise ValueError(  # pragma: no cover
                "The extra data cannot be appended to the model file, because it is not a hdf5 file. Please specify the extra_data_path argument."  # pragma: no cover
            )  # pragma: no cover

        extra_data_path = extra_data_path or model_path
        # Save the extra data.
        with h5py.File(
            extra_data_path, ["x", "r+"][extra_data_path == model_path]
        ) as fid:
            fid.create_dataset("model_type", data=self.__class__.__name__, dtype=H5_STR)
            fid.create_dataset("input_names", data=self.input_names, dtype=H5_STR)
            fid.create_dataset("output_names", data=self.output_names, dtype=H5_STR)
            fid.create_dataset("n_inputs", data=self.n_inputs, dtype="i8")
            fid.create_dataset("n_outputs", data=self.n_outputs, dtype="i8")

            grp_meta = fid.create_group("metadata")
            for key, val in self.metadata.items():
                grp_meta.create_dataset(key, data=val)

            grp_in = fid.create_group("input_transformers")
            for i in range(len(self.input_transformers)):
                group = grp_in.create_group(f"transformer_{i}")
                self.input_transformers[i]._save_h5(group)

            grp_out = fid.create_group("output_transformers")
            for i in range(len(self.output_transformers)):
                group = grp_out.create_group(f"transformer_{i}")
                self.output_transformers[i]._save_h5(group)

            grp_domain = fid.create_group("domain")
            if self.domain:
                self.domain._save_h5(grp_domain)

    @staticmethod
    def _load_model(file_name, *args, **kwargs):
        """
        Load a generic surrogate model.

        Parameters
        ----------
        file_name : str
            File path where the model was saved.
        *args : list
            Additional `args` are passed to the function that loads the model.
        **kwargs : dict
            Additional `kwargs` are passed to the function that loads the model.

        Returns
        -------
        model : -
            Surrogate model.
        """
        # Protected because normally the user does not want to call it.
        raise NotImplementedError()

    @classmethod
    def load_h5(cls, model_path, extra_data_path=None, *args, **kwargs):
        """
        Load a surrogate model.

        Parameters
        ----------
        model_path : str
            File path where the model was saved.
        extra_data_path : str, None
            File path where the extra data were saved.
            If None, default, extra data is read from the model h5 file
        *args : -
            Additional `args` are passed to `_load_model()`, which loads the surrogate model itself.
        **kwargs : -
            Additional `kwargs` are passed to `_load_model()`, which saves the surrogate model itself.

        Returns
        -------
        obj : SurrogateModel
            The surrogate model that was saved.
        """

        # Load extra data.
        with h5py.File(extra_data_path or model_path, "r") as fid:
            model_type = fid["model_type"].asstr()[()]
            if cls.__name__ != model_type:
                raise ValueError(
                    f"The model type in the extra data file ({model_type}) does not match the current one ({cls.__name__})."
                )

            input_names = [s for s in fid["input_names"].asstr()[()]]
            output_names = [s for s in fid["output_names"].asstr()[()]]
            if "n_inputs" in fid:
                n_inputs = fid["n_inputs"][()]
            elif len(input_names) > 0:
                n_inputs = len(input_names)
            else:
                # Older versions did not include the number of inputs.
                n_inputs = None
                warnings.warn(
                    "This file does not contain the number of inputs. Some features may be unavailable."
                )
            if "n_outputs" in fid:
                n_outputs = fid["n_outputs"][()]
            elif len(output_names) > 0:
                n_outputs = len(output_names)
            else:
                # Older versions did not include the number of outputs.
                n_outputs = None
                warnings.warn(
                    "This file does not contain the number of outputs. Some features may be unavailable."
                )
            metadata = {k: np.array(fid["metadata"][k]) for k in fid["metadata"]}
            # Look for the correct transformer class based on the input transformer type.
            input_transformers = [
                globals()[fid["input_transformers"][name]["type"].asstr()[()]]._load_h5(
                    fid["input_transformers"][name]
                )
                for name in fid["input_transformers"]
            ]
            # Look for the correct transformer class based on the output transformer type.
            output_transformers = [
                globals()[
                    fid["output_transformers"][name]["type"].asstr()[()]
                ]._load_h5(fid["output_transformers"][name])
                for name in fid["output_transformers"]
            ]
            # First, check if the domain exists, to allow loading files generated pre 2.2.0.
            # Then, check if type exists, to determine whether there is actually a domain.
            # Finally, look for the correct domain class based on the domain type.
            if "domain" in fid and "type" in fid["domain"]:
                domain = globals()[fid["domain"]["type"].asstr()[()]]._load_h5(
                    fid["domain"]
                )
            else:
                domain = None

        # Load model.
        model = cls._load_model(model_path, *args, **kwargs)

        return cls(
            model,
            input_transformers=input_transformers,
            output_transformers=output_transformers,
            input_names=input_names,
            output_names=output_names,
            n_inputs=n_inputs,
            n_outputs=n_outputs,
            metadata=metadata,
            domain=domain,
        )

    @abstractmethod
    def _predict_model_output(self, x):
        """
        Predict the surrogate model output. Typically, surrogates are trained on transformed input and output data,
        therefore this function expects a transformed input and will return a transformed output.
        """
        # Protected because normally the user does not want to call it.
        # Any surrogate must be evaluated. That is why this method is abstract.

    def predict_output(self, x):
        r"""
        Predict the complete model output, including all input and output transformations.

        We assume that the input :math:`x` has undergone a series of transformation :math:`f_i`

        .. math::
          \tilde{x} = f_n \circ \cdots \circ f_2 \circ f_1 \circ x

        Similarly, also the output :math:`y` has been transformed as

        .. math::
          \tilde{y} = g_m \circ \cdots \circ g_2 \circ g_1 \circ y

        Then, a surrogate model :math:`s` has been trained on the transformed input and output.

        .. math::
          \hat{\tilde{y}} = s(\tilde{x}) \simeq \tilde{y}

        The output in the original space is thus reconstructed as

        .. math::
          \hat{y} =  g_1^{-1} \circ g_2^{-1} \circ \cdots \circ g_m^{-1} \circ \hat{\tilde{y}}

        and by substitution we find

        .. math::
            \hat{y} =  g_1^{-1}(g_2^{-1}(g_m^{-1}(s(f_n(f_2(f_1(x)))))))

        Parameters
        ----------
        x : array-like of shape (n_points, n_inputs)
            Input data.

        Returns
        -------
        y : array-like of shape (n_points, n_outputs)
            Output data.
        """
        # Check if the points are inside the domain of the training data.
        if self.domain is not None:
            x_in_domain = self.domain.in_domain(x)
            if not np.all(x_in_domain):
                # n_x_outside = x.shape[0] - np.count_nonzero(x_in_domain)
                fraction_outside = 1.0 - np.count_nonzero(x_in_domain) / x.shape[0]
                warnings.warn(
                    f"{fraction_outside:.1%} of points are outside of the input domain."
                )

        # Apply direct transformations to input.
        x_transformed = x.copy()
        for transformer in self.input_transformers:
            # If possible do the transformation inplace.
            try:
                transformer.transform(x_transformed, inplace=True)
            except ValueError:
                # The PCA does not support inplace.
                x_transformed = transformer.transform(x_transformed, inplace=False)

        # Evaluate surrogate model.
        y = self._predict_model_output(x_transformed)

        # Apply inverse transformations to output.
        for transformer in reversed(self.output_transformers):
            # If possible do the inverse transformation inplace.
            try:
                transformer.inverse_transform(y, inplace=True)
            except ValueError:
                # The PCA does not support inplace.
                y = transformer.inverse_transform(y, inplace=False)
        return y

    def _predict_model_jacobian(self, x, *args, **kwargs):
        """
        Predict the surrogate model output and Jacobian.

        Typically, surrogates are trained on transformed input and output data,
        therefore this function expects a transformed input and will return a transformed output.
        """
        # Protected because normally the user does not want to call it.
        raise NotImplementedError()

    def predict_output_and_jacobian(self, x, *args, **kwargs):
        r"""
        Predict the complete model output and Jacobian, including all input and output transformations.

        Let's recall that the predicted output is given by

        .. math::
            \hat{y} =  g_1^{-1}(g_2^{-1}(g_m^{-1}(s(f_n(f_2(f_1(x)))))))
        By indicating with :math:`J_h(z)` the Jacobian of :math:`h` evaluated at :math:`z`, we obtain
        the Jacobian of the predicted output by applying the chain rule

        .. math::
            J = &J_{g_1^{-1}}(g_2^{-1}(g_m^{-1}(s(f_n(f_2(f_1(x)))))))   \\
                &J_{g_2^{-1}}(g_m^{-1}(s(f_n(f_2(f_1(x))))))   \\
                &J_{g_m^{-1}}(s(f_n(f_2(f_1(x)))))   \\
                &J_{s}(f_n(f_2(f_1(x))))   \\
                &J_{f_n}(f_2(f_1(x)))
                  J_{f_2}(f_1(x))
                   J_{f_1}(x)

        Parameters
        ----------
        x : array-like of shape (n_points, n_inputs)
            Input data.
        *args : -
            Additional `args` are passed to `_predict_model_jacobian()`.
        **kwargs : -
            Additional `kwargs` are passed to `_predict_model_jacobian()`.

        Returns
        -------
        y : array-like of shape (n_points, n_outputs)
            Output.
        jacobian : array-like of shape (n_points, n_outputs, n_inputs)
            Jacobian.
        """
        # Check if the points are inside the domain of the training data.
        if self.domain is not None:
            x_in_domain = self.domain.in_domain(x)
            if not np.all(x_in_domain):
                # n_x_outside = x.shape[0] - np.count_nonzero(x_in_domain)
                fraction_outside = 1.0 - np.count_nonzero(x_in_domain) / x.shape[0]
                warnings.warn(
                    f"{fraction_outside:.1%} of points are outside of the input domain."
                )

        # Apply direct transformations to input.
        x_transformed = x.copy()
        # The input transformation Jacobian starts as an identity matrix,
        # repeated over all points.
        if x.ndim == 1:
            x = x.reshape(1, -1)
        input_transformation_jacobian = np.tile(np.eye(x.shape[1]), (x.shape[0], 1, 1))
        for transformer in self.input_transformers:
            # Get Jacobian of current input transformation.
            in_jac = transformer.transform_gradient(x_transformed)
            # Accumulate the input transformations Jacobian.
            if in_jac.ndim == 2:
                # If the Jacobian has shape (n_points, n_in), it means it the features are independent.
                # Do the multiplication as if in_jac for each point is a diagonal matrix.
                input_transformation_jacobian *= in_jac[:, np.newaxis, :]

            else:  # in_jac.ndim == 3:
                # If the Jacobian has shape (n_points, n_out, n_in), it means that the features are dependent.
                # Therefore the chain rule is a matrix multiplication.
                input_transformation_jacobian = in_jac @ input_transformation_jacobian

            # Apply the input transformation.
            try:
                transformer.transform(x_transformed, inplace=True)
            except ValueError:
                # The PCA does not support inplace.
                x_transformed = transformer.transform(x_transformed, inplace=False)

        # Predict the model output and Jacobian.
        y, jacobian = self._predict_model_jacobian(x_transformed, *args, **kwargs)

        # Apply the input transformation Jacobian via the chain rule.
        jacobian = jacobian @ input_transformation_jacobian

        # Apply the inverse output transformation Jacobian via the chain rule.
        for transformer in reversed(self.output_transformers):
            out_jac = transformer.inverse_transform_gradient(y)

            # Accumulate the output transformations Jacobian.
            if out_jac.ndim == 2:
                # If the Jacobian has shape (n_points, n_out), it means it the features are independent.
                # Do the multiplication as if out_jac for each point is a diagonal matrix.
                jacobian *= out_jac[:, :, np.newaxis]

            else:  # out_jac.ndim == 3:
                # If the Jacobian has shape (n_points, n_out, n_in), it means that the features are dependent.
                # Therefore the chain rule is a matrix multiplication.
                jacobian = out_jac @ jacobian

            # Apply the inverse output transformation.
            try:
                transformer.inverse_transform(y, inplace=True)
            except ValueError:
                # The PCA does not support inplace.
                y = transformer.inverse_transform(y, inplace=False)
        return y, jacobian

    def predict_jacobian(self, x, *args, **kwargs):
        """
        Predict the complete model Jacobian, including all input and output transformations.

        Parameters
        ----------
        x : array-like of shape (n_points, n_inputs)
            Input data.
        *args : -
            Additional `args` are passed to `_predict_model_jacobian()`.
        **kwargs : -
            Additional `kwargs` are passed to `_predict_model_jacobian()`.

        Returns
        -------
        jacobian : array-like of shape (n_points, n_outputs, n_inputs)
            Jacobian.
        """
        _, jacobian = self.predict_output_and_jacobian(x, *args, **kwargs)
        return jacobian

    def _predict_model_vjp(self, x, dy):
        r"""
        Predict the surrogate model output and vector-Jacobian product.

        Computes

        .. math::
            \begin{align}
            \mathrm{d}\boldsymbol{x} &= J(\boldsymbol{x})^{\mathsf{T}} \mathrm{d}\boldsymbol{y}
            \\
            \mathrm{d}\boldsymbol{x}^{\mathsf{T}} &= \mathrm{d}\boldsymbol{y}^{\mathsf{T}} J(\boldsymbol{x})^{\mathsf{T}}
            \end{align}
        """
        # Protected because normally the user does not want to call it.
        raise NotImplementedError()

    def predict_vjp(self, x, dy):
        """
        Predict the surrogate model vector-Jacobian product, including all input and output transformations.

        Parameters
        ----------
        x : array-like of shape (n_points, n_inputs)
            Input data.
        dy : array-like of shape (n_points, n_outputs)
            Output variation (seed). This function is meant to work with OpenMDAO, where `dy` is a one-hot array,
            which means that `dy` is 1 for a given point and output channel and 0 for all others.

        Returns
        -------
        dx : array-like of shape (n_points, n_inputs)
            Input variation.
        """
        # Find the hot point and input channel.
        idx = dy.nonzero()
        try:
            i_point = idx[0][0]
            # i_out = idx[1][0]
        except IndexError:
            # Early exit if the seed is 0.
            return np.zeros((dy.shape[0], self.n_inputs), dtype=dy.dtype)

        # Check if the hot point is inside the domain of the training data.
        if self.domain is not None:
            x_in_domain = self.domain.in_domain(x[[i_point], :])
            if not x_in_domain[0]:
                warnings.warn("The hot point is outside of the input domain.")

        # Take one input point, apply input transformations and accumulate the Jacobian of the transformations.
        x_transformed = x[[i_point], :].copy()
        input_transformation_jacobian = np.ones((1, self.n_inputs), dtype=x.dtype)
        for transformer in self.input_transformers:
            input_transformation_jacobian *= transformer.transform_gradient(
                x_transformed
            )
            transformer.transform(x_transformed, inplace=True)

        # Compute VJP for a single point.
        # y_i  has shape (1, n_outputs)
        # dx_i has shape (1, n_inputs)
        y_i, dx_i = self._predict_model_vjp(x_transformed, dy[[i_point], :])

        # Apply input transformation jacobian via chain rule.
        dx_i *= input_transformation_jacobian

        # Apply inverse output transformations and accumulate their VJP.
        for transformer in reversed(self.output_transformers):
            dx_i *= transformer.inverse_transform_gradient(y_i) @ dy[i_point, :]
            transformer.inverse_transform(y_i, inplace=True)

        # Preallocate and assign dx.
        dx = np.zeros((dy.shape[0], self.n_inputs), dtype=dy.dtype)
        dx[[i_point], :] = dx_i
        return dx

    @abstractmethod
    def _predict_model_jvp(self, x, dx):
        r"""
        Predict the surrogate model output and Jacobian-vector product.

        Computes

        .. math::
            \mathrm{d}\boldsymbol{y} = J(\boldsymbol{x}) \mathrm{d}\boldsymbol{x}
        """
        # Protected because normally the user does not want to call it.
        raise NotImplementedError()

    def predict_jvp(self, x, dx):
        """
        Predict the surrogate model Jacobian-vector product, including all input and output transformations.

        Parameters
        ----------
        x : array-like of shape (n_points, n_inputs)
            Input data.
        dx : array-like of shape (n_points, n_inputs)
            Input variation (seed). This function is meant to work with OpenMDAO, where `dx` is a one-hot array,
            which means that `dx` is 1 for a given point and input channel and 0 for all others.

        Returns
        -------
        dy : array-like of shape (n_points, n_outputs)
            Output variation.
        """
        # Find the hot point and input channel.
        idx = dx.nonzero()
        try:
            i_point = idx[0][0]
            # i_in = idx[1][0]
        except IndexError:
            # Early exit if the seed is 0.
            return np.zeros((dx.shape[0], self.n_outputs), dtype=x.dtype)

        # Check if the hot point is inside the domain of the training data.
        if self.domain is not None:
            x_in_domain = self.domain.in_domain(x[[i_point], :])
            if not x_in_domain[0]:
                warnings.warn("The hot point is outside of the input domain.")

        # Take one input point, apply input transformations and accumulate JVP of the transformations.
        x_transformed = x[[i_point], :].copy()
        input_transformation_jvp = np.array([1.0], dtype=x.dtype)
        for transformer in self.input_transformers:
            input_transformation_jvp *= (
                transformer.transform_gradient(x_transformed) @ dx[i_point, :]
            )
            transformer.transform(x_transformed, inplace=True)

        # Compute JVP for a single point.
        # y_i and dy_i have shape (1, n_outputs)
        y_i, dy_i = self._predict_model_jvp(x_transformed, dx[[i_point], :])

        # Apply input transformation JVP via chain rule.
        dy_i *= input_transformation_jvp

        # Apply inverse output transformations and accumulate their Jacobians.
        for transformer in reversed(self.output_transformers):
            dy_i *= transformer.inverse_transform_gradient(y_i)
            transformer.inverse_transform(y_i, inplace=True)

        # Preallocate and assign dy.
        dy = np.zeros((dx.shape[0], self.n_outputs), dtype=dx.dtype)
        dy[[i_point], :] = dy_i
        return dy

    def __eq__(self, other):
        # TODO: check also the model.
        if isinstance(other, self.__class__):
            test = True
            try:
                np.testing.assert_equal(self.metadata, other.metadata)
            except AssertionError:
                test = False
            if test:
                for a, b in zip(self.input_transformers, other.input_transformers):
                    test = test and (a == b)
            if test:
                for a, b in zip(self.output_transformers, other.output_transformers):
                    test = test and (a == b)
            if test:
                for a, b in zip(self.input_names, other.input_names):
                    test = test and (a == b)
            if test:
                for a, b in zip(self.output_names, other.output_names):
                    test = test and (a == b)
            test = test and (self.n_inputs == other.n_inputs)
            test = test and (self.n_outputs == other.n_outputs)
            test = test and (self.domain == other.domain)

            return test
        return False


class TensorFlowModel(SurrogateModel):
    """
    Class that stores and evaluates an existing TensorFlow `Model`. Typically used with a `Sequential` model.
    """

    @staticmethod
    def _load_model(filepath, custom_objects=None, compile=True, options=None):
        """
        Loads a TensorFlow model saved via `model.save()`.
        Wrapper of `tf.keras.models.load_model`.

        Parameters
        ----------
        filepath: str, pathlib.Path, h5py.File
            Path to the model.
        custom_objects: dict
            Dictionary mapping names (strings) to custom classes or
            functions to be considered during deserialization.
        compile: bool
            `True` to compile the model after loading.
        options: tf.saved_model.LoadOptions
            Object that specifies options for loading from SavedModel.

        Returns
        -------
        tf.keras.Model
            A Keras model instance. If the original model was compiled, and saved
            with the optimizer, then the returned model will be compiled. Otherwise,
            the model will be left uncompiled. In the case that an uncompiled model
            is returned, a warning is displayed if the `compile` argument is set to `True`.

        Raises
        ------
        ImportError
            If loading from an hdf5 file and h5py is not available.
        IOError
            In case of an invalid savefile.
        """
        import tensorflow as tf

        return tf.keras.models.load_model(filepath, custom_objects, compile, options)

    def _save_model(self, filepath, overwrite=True, save_format="h5"):
        """
        Saves the model to Tensorflow SavedModel or a single HDF5 file.
        Wrapper of tf.keras.Model.save`.

        Parameters
        ----------
        filepath : str, path-like
            Path to `SavedModel` or `H5` file to save the model.
        overwrite : bool, optional
            `True` to silently overwrite any existing file at the
            target location, or provide the user with a manual prompt.
        save_format : str, optional
            Either `'keras'`, `'tf'` or `'h5'`, indicating whether to
            save the model in the native Keras format (.keras), in the
            TensorFlow SavedModel format (referred to as "SavedModel" below),
            or in the legacy HDF5 format (.h5). Defaults to `'h5'`.

        Returns
        -------
        None.

        """
        self.model.save(filepath, overwrite=overwrite, save_format=save_format)

    def _predict_model_output(self, x):
        """
        Predict the model output.

        Parameters
        ----------
        x : array-like of shape (n_points, n_inputs)
            Input data.

        Returns
        -------
        y : array-like of shape (n_points, n_outputs)
            Output data.
        """
        # TODO: Add support also for other arguments of predict, like use_multiprocessing.
        y = self.model(x, training=False).numpy()
        return y

    def _predict_model_output_and_jacobian_rev(self, x):
        """
        Predict the model Jacobian using reverse mode automatic differentiation,
        assuming that all batches (i.e. points) are independent.

        Parameters
        ----------
        x : array-like of shape (n_points, n_inputs)
            Input data.

        Returns
        -------
        y :  array-like of shape (n_points, n_outputs)
            Output.
        jacobian : array-like of shape (n_points, n_outputs, n_inputs)
            Jacobian.
        """
        import tensorflow as tf

        input = tf.constant(x)
        with tf.GradientTape() as tape:
            tape.watch(input)
            output = self.model(input)
        jacobian = tape.batch_jacobian(output, input).numpy()
        return output.numpy(), jacobian

    def _predict_model_output_and_jacobian_fwd(self, x):
        """
        Predict the model Jacobian using forward mode automatic differentiation,
        assuming that all batches (i.e. points) are independent.

        Parameters
        ----------
        x : array-like of shape (n_points, n_inputs)
            Input data.

        Returns
        -------
        y :  array-like of shape (n_points, n_outputs)
            Output.
        jacobian : array-like of shape (n_points, n_outputs, n_inputs)
            Jacobian.
        """
        import tensorflow as tf

        # Preallocate jacobian array.
        jacobian = np.zeros((x.shape[0], self.n_outputs, self.n_inputs))
        # Transform the input into a Tensor, and convert to single precision.
        input = tf.constant(x, dtype=tf.float32)
        # Define the direction for the derivatives.
        # The direction will be broadcasted over the points.
        tangents = np.zeros((x.shape[1]), dtype=np.float32)
        # We start from the first input.
        tangents[0] = 1
        with tf.autodiff.ForwardAccumulator(
            input, tf.broadcast_to(tangents, x.shape)
        ) as acc:
            output = self.model(input)
        jacobian[:, :, 0] = acc.jvp(output).numpy()
        # And proceed with the others.
        for i_in in range(1, self.n_inputs):
            # Reset the direction.
            tangents[i_in - 1] = 0
            # Set the current one.
            tangents[i_in] = 1
            with tf.autodiff.ForwardAccumulator(
                input, tf.broadcast_to(tangents, x.shape)
            ) as acc:
                output = self.model(input)
            jacobian[:, :, i_in] = acc.jvp(output).numpy()
        return output.numpy(), jacobian

    def _predict_model_jacobian(self, x, ad_mode=None):
        """
        Predict the model Jacobian, assuming that all batches (i.e. points) are independent.

        Parameters
        ----------
        x : array-like of shape (n_points, n_inputs)
            Input data.
        ad_mode : ADMode, optional
            Automatic differentiation mode. Can be either `ADMode.FWD` or `ADMode.REV`.
            If `None`, the choice depends on the number of input and output featurtes.

        Returns
        -------
        y :  array-like of shape (n_points, n_outputs)
            Output.
        jacobian : array-like of shape (n_points, n_outputs, n_inputs)
            Jacobian.
        """
        if ad_mode is None:
            if self.n_outputs <= self.n_inputs:
                ad_mode = ADMode.REV
            else:
                ad_mode = ADMode.FWD
        if ad_mode is ADMode.REV:
            y, jacobian = self._predict_model_output_and_jacobian_rev(x)
        elif ad_mode is ADMode.FWD:
            y, jacobian = self._predict_model_output_and_jacobian_fwd(x)
        return y, jacobian

    def _predict_model_vjp(self, x, dy):
        """
        Compute output and vector-Jacobian product using reverse-mode
        automatic differentiation, i.e. backpropagation.

        Parameters
        ----------
        x : array-like of shape (1, n_inputs)
            Input data.
        dy : array-like of shape (1, n_outputs)
            Output variation.

        Returns
        -------
        y : array-like of shape (1, n_outputs)
            Output.
        dx : array-like of shape (1, n_inputs)
            Input variation.
        """
        import tensorflow as tf

        # Compute the Jacobian.
        input = tf.constant(x)
        with tf.GradientTape() as tape:
            tape.watch(input)
            output = self.model(input)
        jacobian = tape.batch_jacobian(output, input).numpy()
        # Compute the product.
        dummy = jacobian.transpose(0, 2, 1) @ dy[:, :, np.newaxis]
        dx = dummy[:, :, 0]
        return output.numpy(), dx

    def _predict_model_jvp(self, x, dx):
        """
        Compute output and Jacobian-vector product using forward-mode
        automatic differentiation.

        Parameters
        ----------
        x : array-like of shape (1, n_inputs)
            Input data.
        dx : array-like of shape (1, n_inputs)
            Input variation.

        Returns
        -------
        y : array-like of shape (1, n_outputs)
            Output.
        dy : array-like of shape (1, n_outputs)
            Output variation.
        """
        import tensorflow as tf

        # Take the current point, and convert to float32 or otherwise
        # ForwardAccumulator will crash.
        input = tf.constant(x, dtype=tf.float32)
        tangents = tf.constant(dx, dtype=tf.float32)
        with tf.autodiff.ForwardAccumulator(input, tangents) as acc:
            output = self.model(input)
        dy = acc.jvp(output).numpy()
        return output.numpy(), dy


class SMTModel(SurrogateModel):
    """
    Class that stores and evaluates an existing SMT `SurrogateModel`.
    """

    @staticmethod
    def _load_model(filepath):
        with open(filepath, "rb") as f:
            return pickle.load(f)
        # TODO: deal with C++ models.

    def _save_model(self, filepath):
        from smt.surrogate_models import IDW, RBF, RMTB, RMTC

        if isinstance(self.model, (IDW, RBF, RMTB, RMTC)):
            raise NotImplementedError()
        else:
            # Pure Python models are saved with pickle.
            with open(filepath, "wb") as fid:
                pickle.dump(self.model, fid)

    def _predict_model_output(self, x):
        """
        Predict the model output.

        Parameters
        ----------
        x : array-like of shape (n_points, n_inputs)
            Input data.

        Returns
        -------
        y : array-like of shape (n_points, n_outputs)
            Output data.
        """
        # Switch off printing.
        print_save = self.model.options["print_prediction"]
        self.model.options["print_prediction"] = False
        # Predict output.
        y = self.model.predict_values(x)
        # Restore printing option.
        self.model.options["print_prediction"] = print_save

        return y

    def _predict_model_jacobian(self, x):
        """
        Predict the model Jacobian.

        Parameters
        ----------
        x : array-like of shape (n_points, n_inputs)
            Input data.

        Returns
        -------
        y :  array-like of shape (n_points, n_outputs)
            Output.
        jacobian : array-like of shape (n_points, n_outputs, n_inputs)
            Jacobian.
        """
        # Switch off printing.
        print_save = self.model.options["print_prediction"]
        self.model.options["print_prediction"] = False
        # Predict output.
        y = self.model.predict_values(x)
        # Predict Jacobian by looping over the inputs.
        jacobian = np.empty((x.shape[0], self.n_outputs, self.n_inputs))
        for i in range(self.n_inputs):
            jacobian[:, :, i] = self.model.predict_derivatives(x, i)
        # Restore printing option.
        self.model.options["print_prediction"] = print_save
        return y, jacobian


class SurrogateModelFamily:
    pass


class PyTorchModel(SurrogateModel):
    """
    Class that stores and evaluates an existing PyTorch model.
    """

    def __init__(self, *args, dtype=None, max_batch=50_000, **kwargs):
        import torch
        import torch._dynamo

        torch._dynamo.config.suppress_errors = True
        super().__init__(*args, **kwargs)
        self.model.eval()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.dtype = torch.float16 if dtype is None else dtype
        self.model.to(self.dtype)
        self.max_batch = max_batch

    def __to_numpy(self, _x):
        import torch

        try:
            import cupy as cp
        except ImportError:  # pragma: no cover
            cp = np
        lalib = cp if self.device == torch.device("cuda") else np  # pragma: no cover
        return lalib.asarray(_x).astype(lalib.float32)

    def __to_tensor(self, _x):
        import torch

        if len(_x.shape) < 2:
            _x = _x.reshape(1, -1)
        return torch.as_tensor(_x, device=self.device, dtype=self.dtype)

    def __record_in_dtype(self, _x):  # pragma: no cover
        # TODO: could be used to retain the input/output dtype the same
        self.in_dtype = _x.dtype

    def _predict_model_output(self, x):
        import torch

        x = self.__to_tensor(x)

        with torch.no_grad():
            output = torch.zeros(
                (x.shape[0], self.n_outputs),
                device=self.device,
                dtype=self.dtype,
            )
            for i in range(0, x.shape[0], self.max_batch):
                inter_out = self.model(x[i : i + self.max_batch])
                output[i : i + self.max_batch].copy_(
                    inter_out[: x[i : i + self.max_batch].shape[0]], non_blocking=True
                )

        return self.__to_numpy(output)

    def _predict_model_jacobian(self, x, ad_mode=None):
        if ad_mode is None:
            ad_mode = ADMode.REV if (self.n_outputs <= self.n_inputs) else ADMode.FWD

        if ad_mode is ADMode.REV:
            y, jacobian = self._predict_model_output_and_jacobian_rev(x)
        elif ad_mode is ADMode.FWD:
            y, jacobian = self._predict_model_output_and_jacobian_fwd(x)

        return y, jacobian

    def predict_output(self, x):
        y = super().predict_output(x)
        return self.__to_numpy(y)

    def _save_model(self, filepath):
        import torch

        torch.save(self.model.state_dict(), filepath)

    @staticmethod
    def _load_model(filepath, model_cls):
        import torch

        model_cls.load_state_dict(torch.load(filepath, weights_only=True))
        return model_cls

    def _predict_model_jvp(self, x, dx):
        import torch.func as torch_func

        if not hasattr(self, "batched_jvp_func"):
            def g(_x):  # fmt: skip
                return self.model(_x)

            def single_jvp(_x, _v):
                return torch_func.jvp(g, (_x,), (_v,))

            self.batched_jvp_func = torch_func.vmap(single_jvp)

        x = self.__to_tensor(x)
        dx = self.__to_tensor(dx)
        output, jvp_res = self.batched_jvp_func(x, dx)
        return self.__to_numpy(output.detach()), self.__to_numpy(jvp_res.detach())

    def _predict_model_vjp(self, x, dy):
        import torch.func as torch_func

        if not hasattr(self, "batched_vjp_func"):
            def g(_x):  # fmt: skip
                return self.model(_x)

            def single_vjp(_x, _v):
                out, f = torch_func.vjp(g, _x)
                return out, f(_v)

            self.batched_vjp_func = torch_func.vmap(single_vjp)

        x = self.__to_tensor(x)
        dy = self.__to_tensor(dy)
        output, vjp_res = self.batched_vjp_func(x, dy)
        return self.__to_numpy(output.detach()), self.__to_numpy(vjp_res[0].detach())

    def _predict_model_output_and_jacobian_fwd(self, x):
        import torch.func as torch_func

        if not hasattr(self, "y_jac_fwd_func"):
            def g(_x):  # fmt: skip
                result = self.model(_x)
                return (result, result)
            self.y_jac_fwd_func = torch_func.vmap(torch_func.jacfwd(g, has_aux=True))

        x = self.__to_tensor(x)
        jac, output = self.y_jac_fwd_func(x)
        return self.__to_numpy(output.detach()), self.__to_numpy(jac.detach())

    def _predict_model_output_and_jacobian_rev(self, x):
        import torch.func as torch_func

        if not hasattr(self, "y_jac_rev_func"):
            def g(_x):  # fmt: skip
                result = self.model(_x)
                return (result, result)
            self.y_jac_rev_func = torch_func.vmap(torch_func.jacrev(g, has_aux=True))

        x = self.__to_tensor(x)
        jac, output = self.y_jac_rev_func(x)
        return self.__to_numpy(output.detach()), self.__to_numpy(jac.detach())

    def _predict_model_jacobian_sbatch(self, x):  # pragma: no cover
        # Not used for now, but left as a reference for future if GPU memory issues arise.
        import torch
        import torch.func as torch_func

        if not hasattr(self, "y_jac_func"):
            def g(_x):  # fmt: skip
                result = self.model(_x)
                return (result, result)
            self.y_jac_func = torch_func.vmap(torch_func.jacrev(g, has_aux=True))

        x = self.__to_tensor(x)
        batch_size = x.shape[0]
        y = torch.zeros(
            (batch_size, self.n_outputs),
            device=self.device,
            dtype=self.dtype,
        )
        jac = torch.zeros(
            (batch_size, self.n_outputs, self.n_inputs),
            device=self.device,
            dtype=self.dtype,
        )
        for i in range(0, batch_size, self.max_batch):
            x_mb = x[i : i + self.max_batch]
            inter_jac, inter_y = self.y_jac_func(x_mb)
            y[i : i + self.max_batch].copy_(
                inter_y[: x_mb.shape[0]],
                non_blocking=True,
            )
            jac[i : i + self.max_batch].copy_(
                inter_jac[: x_mb.shape[0]],
                non_blocking=True,
            )

        return self.__to_numpy(y.detach()), self.__to_numpy(jac.detach())
