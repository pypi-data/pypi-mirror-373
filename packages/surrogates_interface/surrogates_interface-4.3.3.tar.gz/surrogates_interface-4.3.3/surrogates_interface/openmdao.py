# -*- coding: utf-8 -*-
"""
In this module, we wrap the surrogate models into OpenMDAO components.
"""

from enum import IntEnum, auto

import numpy as np
import openmdao.api as om

# from surrogates_interface.surrogates import SurrogateModel


class InputOutputType(IntEnum):
    """
    Enumeration used by `SurrogateModelComp` to determine the type of the input and output.
    """

    #: The input or output dimensions of a surrogate model are combined into one.
    JOINED = auto()
    #: The input or output dimensions of a surrogate model are kept separate.
    SPLIT = auto()


class SurrogateModelCompFD(om.ExplicitComponent):
    """
    Wraps `SurrogateModel` into an OpenMDAO explicit component.
    The gradient is approximated via finite differences.

    Parameters
    ----------
    model : subclass of SurrogateModel
        Surrogate model to be wrapped.
    n_points : int
        Number of points over which to evaluate the surrogate model.
    input_type : InputOutputType
        Type of the input.
          - If `InputOutputType.JOINED` there will be only 1 input named `input_name`.
          - If `InputOutputType.SPLIT` there will be 1 input per input channel. Their names will be taken from `model.input_names`.
    output_type : InputOutputType
        Type of the output.
          - If `InputOutputType.JOINED` there will be only 1 output named `output_name`.
          - If `InputOutputType.SPLIT` there will be 1 input per output channel. Their names will be taken from `model.output_names`.
    input_name : str, default 'x'
        Name of the input, that is used when `input_type = InputOutputType.JOINED`.
    output_name : str, default 'y'
        Name of the output, that is used when `output_type = InputOutputType.JOINED`.
    """

    @staticmethod
    def _check_in_out_type(name, value):
        """
        Check that `value` is defined in `InputOutputType`.

        Parameters
        ----------
        name : str
            Name of the option.
        value : InputOutputType
            Value of the option.

        Returns
        -------
        None.

        Raises
        ------
        ValueError
            If value is not valid for option.
        """
        if value not in iter(InputOutputType):
            raise ValueError(
                f"Option {name}, here {value}, must be defined in `InputOutputType`."
            )

    def initialize(self):
        self.options.declare(
            "model",
            # types=SurrogateModel,
            desc="Surrogate model to be wrapped.",
            recordable=False,
        )  # There is nothing to record here.

        self.options.declare(
            "n_points",
            types=int,
            desc="Number of points over which to evaluate the surrogate model.",
        )

        self.options.declare(
            "input_type",
            desc="""Type of the input.
                                  - If `InputOutputType.JOINED` there will be only 1 input named `options["input_name"]`.
                                  - If `InputOutputType.SPLIT` there will be 1 input per channel. Their names will be taken from `model.input_names`.
                                  """,
            check_valid=self._check_in_out_type,
        )

        self.options.declare(
            "output_type",
            desc="""Type of the output.
                               - If `InputOutputType.JOINED` there will be only 1 output named `options["output_name"]`.
                               - If `InputOutputType.SPLIT` there will be 1 output per channel. Their names will be taken from `model.output_names`.
                               """,
            check_valid=self._check_in_out_type,
        )

        self.options.declare(
            "input_name",
            default="x",
            desc="Name of the input, that is used when `input_type = InputOutputType.JOINED`.",
        )

        self.options.declare(
            "output_name",
            default="y",
            desc="Name of the output, that is used when `output_type = InputOutputType.JOINED`.",
        )

    def setup(self):
        if self.options["input_type"] is InputOutputType.JOINED:
            self.add_input(
                self.options["input_name"],
                shape=(self.options["n_points"], self.options["model"].n_inputs),
            )
        else:
            for name in self.options["model"].input_names:
                self.add_input(name, shape=(self.options["n_points"]))

        if self.options["output_type"] is InputOutputType.JOINED:
            self.add_output(
                self.options["output_name"],
                shape=(self.options["n_points"], self.options["model"].n_outputs),
            )
        else:
            for name in self.options["model"].output_names:
                self.add_output(name, shape=(self.options["n_points"]))

    def setup_partials(self):
        """
        Setup the partial derivatives.
        """
        self.declare_partials("*", "*", method="fd")  # pragma: no cover

    def compute(self, inputs, outputs):
        """
        Wrapper of `SurrogateModel.predict_output()`.

        Parameters
        ----------
        inputs : dict
            Inputs.
              - If `input_type is InputOutputType.JOINED` we expect one input named `options["input_name"]` of shape `(n_points, n_inputs)`.
              - If `input_type is InputOutputType.SPLIT` we expect one input per feature of shape `(n_points,)`.
                The inputs will be stacked according to `model.input_names`.
        outputs : dict
            Outputs.
              - If `output_type is InputOutputType.JOINED` we expect one output named `options["output_name"]` of shape `(n_points, n_outputs)`.
                The outputs will be stacked according to `model.output_names`.
              - If `output_type is InputOutputType.SPLIT` we expect one output per feature of shape `(n_points,)`.

        Returns
        -------
        None.

        """
        # Compose the input.
        if self.options["input_type"] is InputOutputType.JOINED:
            x = inputs[self.options["input_name"]]

        elif self.options["input_type"] is InputOutputType.SPLIT:
            x = np.column_stack(
                [inputs[key] for key in self.options["model"].input_names]
            )

        # Evaluate the model.
        y = self.options["model"].predict_output(x)

        # Compose the output.
        if self.options["output_type"] is InputOutputType.JOINED:
            outputs[self.options["output_name"]] = y

        elif self.options["output_type"] is InputOutputType.SPLIT:
            for i in range(self.options["model"].n_outputs):
                outputs[self.options["model"].output_names[i]] = y[:, i]


class SurrogateModelComp(SurrogateModelCompFD):
    """
    Wraps `SurrogateModel` into an OpenMDAO explicit component.
    The exact gradient is provided via `compute_partials`.
    """

    def setup_partials(self):
        """
        Setup the partial derivatives.

        The format of the Jacobian depends if the user selected `JOINED` or `SPLIT` for the input and output.
        Since the points are independent, the Jacobian is a block diagonal matrix
        with shape `(n_points * n_outputs, n_points * n_inputs)`,
        where each block has shape `(n_outputs, n_inputs)`.
        If the user selected `SPLIT` than there is only 1 feature, while with `JOINED` all features are kept.

        Note that in a time series model the points are dependent, and this code will be incorrect.
        """

        # The following code defines the sparsity pattern in COO format.

        # Shorthand  for the number of points.
        ns = self.options["n_points"]

        # Set the number of inputs.
        if self.options["input_type"] is InputOutputType.JOINED:
            ni = self.options["model"].n_inputs

        elif self.options["input_type"] is InputOutputType.SPLIT:
            ni = 1

        # Set the number of outputs.
        if self.options["output_type"] is InputOutputType.JOINED:
            no = self.options["model"].n_outputs

        elif self.options["output_type"] is InputOutputType.SPLIT:
            no = 1

        # Define the block-diagonal matrix.
        self.declare_partials(
            "*",
            "*",
            method="exact",
            rows=np.arange(ns * no).repeat(ni),
            cols=np.arange(ns * ni).reshape((ns, ni)).repeat(no, 0).flatten(),
        )

    def compute_partials(self, inputs, partials, discrete_inputs=None):
        """
        Wrapper of `SurrogateModel.predict_jacobian()`.

        Parameters
        ----------
        inputs : dict
            Inputs.
              - If `input_type is InputOutputType.JOINED` we expect one input named `options["input_name"]` of shape `(n_points, n_inputs)`.
              - If `input_type is InputOutputType.SPLIT` we expect one input per feature of shape `(n_points,)`.
                The inputs will be stacked according to `model.input_names`.
        partials : dict
            Jacobian.
              - If `output_type is InputOutputType.JOINED` we expect one Jacobian of shape `(n_points, n_outputs)`.
              - If `output_type is InputOutputType.SPLIT` we expect `n_outputs` Jacobians of shape `(n_points,)`.

        Returns
        -------
        None.

        """
        # Compose the input.
        if self.options["input_type"] is InputOutputType.JOINED:
            x = inputs[self.options["input_name"]]
        elif self.options["input_type"] is InputOutputType.SPLIT:
            x = np.column_stack(
                [inputs[key] for key in self.options["model"].input_names]
            )

        # Evaluate the model.
        jacobian = self.options["model"].predict_jacobian(x)

        # Compose the output.
        if self.options["output_type"] is InputOutputType.JOINED:
            if self.options["input_type"] is InputOutputType.JOINED:
                partials[self.options["output_name"], self.options["input_name"]] = (
                    jacobian.ravel()
                )

            elif self.options["input_type"] is InputOutputType.SPLIT:
                for j in range(self.options["model"].n_inputs):
                    partials[
                        self.options["output_name"],
                        self.options["model"].input_names[j],
                    ] = jacobian[:, :, j].ravel()

        elif self.options["output_type"] is InputOutputType.SPLIT:
            if self.options["input_type"] is InputOutputType.JOINED:
                for i in range(self.options["model"].n_outputs):
                    partials[
                        self.options["model"].output_names[i],
                        self.options["input_name"],
                    ] = jacobian[:, i, :].ravel()

            elif self.options["input_type"] is InputOutputType.SPLIT:
                for i in range(self.options["model"].n_outputs):
                    for j in range(self.options["model"].n_inputs):
                        partials[
                            self.options["model"].output_names[i],
                            self.options["model"].input_names[j],
                        ] = jacobian[:, i, j]


class SurrogateModelCompMatrixFree(SurrogateModelCompFD):
    """
    Wraps `SurrogateModel` into an OpenMDAO explicit component that uses the matrix-free API.
    """

    def setup_partials(self):
        pass

    def compute_jacvec_product(
        self, inputs, d_inputs, d_outputs, mode, discrete_inputs=None
    ):
        # Compose the input.
        if self.options["input_type"] is InputOutputType.JOINED:
            x = inputs[self.options["input_name"]]
        elif self.options["input_type"] is InputOutputType.SPLIT:
            x = np.column_stack(
                [inputs[key] for key in self.options["model"].input_names]
            )

        # Check for forward or reverse mode.
        if mode == "fwd":
            if self.options["output_type"] is InputOutputType.JOINED:
                if self.options["input_type"] is InputOutputType.JOINED:
                    dx = d_inputs[self.options["input_name"]]
                    dy = self.options["model"].predict_jvp(x, dx)
                    d_outputs[self.options["output_name"]] = dy

                elif self.options["input_type"] is InputOutputType.SPLIT:
                    for in_name in d_inputs:
                        i_in = self.options["model"].input_names.index(in_name)
                        dx = np.zeros(
                            (
                                self.options["n_points"],
                                self.options["model"].n_inputs,
                            )
                        )
                        dx[:, i_in] = d_inputs[in_name]
                        dy = self.options["model"].predict_jvp(x, dx)
                        d_outputs[self.options["output_name"]] += dy

            elif self.options["output_type"] is InputOutputType.SPLIT:
                if self.options["input_type"] is InputOutputType.JOINED:
                    dx = d_inputs[self.options["input_name"]]
                    dy = self.options["model"].predict_jvp(x, dx)
                    for out_name in d_outputs:
                        i_out = self.options["model"].output_names.index(out_name)
                        d_outputs[out_name] += dy[:, i_out]

                elif self.options["input_type"] is InputOutputType.SPLIT:
                    for in_name in d_inputs:
                        i_in = self.options["model"].input_names.index(in_name)
                        dx = np.zeros(
                            (
                                self.options["n_points"],
                                self.options["model"].n_inputs,
                            )
                        )
                        dx[:, i_in] = d_inputs[in_name]
                        dy = self.options["model"].predict_jvp(x, dx)
                        for out_name in d_outputs:
                            i_out = self.options["model"].output_names.index(out_name)
                            d_outputs[out_name] += dy[:, i_out]

        else:  # mode == 'rev'
            if self.options["output_type"] is InputOutputType.JOINED:
                dy = d_outputs[self.options["output_name"]]
                dx = self.options["model"].predict_vjp(x, dy)

                if self.options["input_type"] is InputOutputType.JOINED:
                    d_inputs[self.options["input_name"]] += dx

                elif self.options["input_type"] is InputOutputType.SPLIT:
                    for in_name in d_inputs:
                        i_in = self.options["model"].input_names.index(in_name)
                        d_inputs[in_name] += dx[:, i_in]

            elif self.options["output_type"] is InputOutputType.SPLIT:
                for out_name in d_outputs:
                    i_out = self.options["model"].output_names.index(out_name)
                    dy = np.zeros(
                        (self.options["n_points"], self.options["model"].n_outputs)
                    )
                    dy[:, i_out] = d_outputs[out_name]
                    dx = self.options["model"].predict_vjp(x, dy)

                    if self.options["input_type"] is InputOutputType.JOINED:
                        d_inputs[self.options["input_name"]] += dx

                    elif self.options["input_type"] is InputOutputType.SPLIT:
                        for in_name in d_inputs:
                            i_in = self.options["model"].input_names.index(in_name)
                            d_inputs[in_name] += dx[:, i_in]
