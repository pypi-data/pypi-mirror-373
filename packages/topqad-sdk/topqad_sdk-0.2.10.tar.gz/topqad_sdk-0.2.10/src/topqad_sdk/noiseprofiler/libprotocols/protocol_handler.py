from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import numpy as np
import json

from pydantic import BaseModel
from scipy.optimize import root_scalar
from uncertainties import unumpy, wrap
from uncertainties.core import Variable

from topqad_sdk.noiseprofiler.fit import fit_data, convert_sympy_formula_to_numpy_func
from topqad_sdk.noiseprofiler.libnoise import NoiseModel
from topqad_sdk.noiseprofiler.libprotocols import models
from topqad_sdk.noiseprofiler.simtable import FieldHeader, SimTable

from topqad_sdk.clients import NoiseProfilerClient
from topqad_sdk.library import HardwareParameters
from topqad_sdk._exceptions import TopQADTimeoutError


def u_format(x: Variable, separate: bool = False) -> str:
    """Format a variable with uncertainity Y as a string in form X.XX(Y).

    Args:
        x (Variable): The number to format.
        separate (bool, optional): Controls if the nominal and std dev values are separated. If True output is a tuple
            of form (X.XX, 0.0Y). Defaults to False.

    Returns:
        str | tuple: The formatted number.

    Examples:
        2.34 ± 0.013 -> 2.34(1)
        8.12 ± 0.3 -> 8.1(3)
        18.15 ± 1.1 -> 18(1)
    """
    # Get nominal value and standard deviation
    nominal = x.nominal_value
    std_dev = x.std_dev

    # Find the position of the first significant digit in uncertainty
    if std_dev == 0:
        return f"{nominal:.6g}"

    # Get the order of magnitude of the uncertainty
    uncertainty_magnitude = -int(np.floor(np.log10(std_dev)))

    # Round uncertainty to 1 significant digit
    rounded_uncertainty = round(std_dev * 10**uncertainty_magnitude)

    # Format the nominal value to the appropriate decimal places
    if uncertainty_magnitude <= 0:
        # For cases like 18.15 ± 1.1
        decimal_places = 0
        rounded_nominal = round(nominal, decimal_places)
        if separate:
            return f"{rounded_nominal:g}", f"{std_dev:.1g}"
        return f"{rounded_nominal:g}({rounded_uncertainty})"
    else:
        # For cases like 2.34 ± 0.013
        decimal_places = uncertainty_magnitude
        rounded_nominal = round(nominal, decimal_places)
        if separate:
            return f"{rounded_nominal:g}", f"{std_dev:.1g}"
        return f"{rounded_nominal:.{decimal_places}f}({rounded_uncertainty})"


@dataclass
class FitSpecification:
    r"""Contains all information to specify a fit for a given class of curves.

    Args:
        fit_ansatz (Callable): The fit function.
        param_bounds (tuple[list, list]): The parameter bounds.
        y_scale (str): Either 'linear' or 'log'.
        fit_ansatz_latex (str): The latex description of the fit function. Use raw strings.

    Examples:
        def fit_ansatz_memory_d_ler(distance, p_1, p_2):
            return -(distance+1)/2 * np.log(p_2) + 2*np.log(distance) + np.log(p_1)

        FitSpecification(fit_ansatz=fit_ansatz_memory_d_ler,
                        param_bounds=([0, 0], [np.inf, np.inf]),
                        y_scale='log',
                        fit_ansatz_latex=r"{p_1} d^2 \times {p_2}^{{-\frac{{d+1}}{{2}}}}",
                        )
    """

    fit_ansatz: str
    param_bounds: tuple[list, list]
    y_scale: str
    fit_ansatz_latex: str
    ind_math_symbol: str


class ProtocolHandler:
    """Handler class for working with FTQC protocols.

    To work with a protocol, one needs to be able to
        - generate instances of the protocol,
        - simulate the protocol instances and collect data
        - fit the data
        - plot the data

    This class contains functionality to do all of this.

    Args:
        protocol_category (str): The main protocol category, such as "memory" or "magic_state_preparation_unit".
        protocol_subcategory (str): The subcategory if there are various kinds of say "memory" protocols.
        protocol_name (str): The unique name of the protocol such as "magic_state_preparation_rep_code".
        protocol_parameters (BaseModel): A pydantic model that specifies all the protocol parameters.
        fit_options (dict[tuple[str, str], FitSpecification]): A dictionary mapping (ind, dep) parameters to a fit
            specification. These fit options will then be used by the fitting and plotting routines.
        includes_postselection (bool): Whether the protocol has post-selection in it.
        simulation_table (SimTable): Contains all data related to the simulation statistics.
        noise_models (dict[str | float | tuple[str, float], NoiseModel]): dictionary of noise models with their labels as keys.
        simulation_parameters (dict[str, Any]): simulation parameters. Use `set_simulation_parameters` method to change these.
    """

    protocol_category: str
    protocol_subcategory: str
    protocol_name: str
    protocol_parameters: BaseModel
    fit_options: dict[tuple[str, str], FitSpecification]
    includes_postselection: bool

    def __init__(self) -> None:
        self.noise_models: dict[str | float | tuple[str, float], NoiseModel] = {}

        fields = [
            FieldHeader(key, kind="protocol_parameter")
            for key in self.protocol_parameters.model_fields.keys()
        ]

        fields += [
            FieldHeader(
                "noise_model_label", full_label="Noise Model", kind="noise_model"
            )
        ]

        fields += [FieldHeader("decoder", full_label="Decoder", kind="decoder")]

        fields += [
            FieldHeader(
                "shots", full_label="Shots", kind="stat", math_symbol="N_s", intfmt="_"
            )
        ]
        fields += [
            FieldHeader(
                "errors",
                full_label="Errors",
                kind="stat",
                math_symbol="N_e",
                intfmt="_",
            )
        ]
        if self.includes_postselection:
            fields += [
                FieldHeader(
                    "discards",
                    full_label="Discards",
                    kind="stat",
                    math_symbol="N_d",
                    intfmt="_",
                )
            ]

        fields += [
            FieldHeader(
                "ler",
                full_label="Logical Error Rate per Shot",
                kind="computed",
                math_symbol="P_L",
                compute_formula="N_e/N_s",
                floatfmt=".2e",
            )
        ]
        fields += [
            FieldHeader(
                "ler_error",
                full_label="ler_error",
                kind="computed",
                math_symbol="delta_L",
                compute_formula="sqrt(P_L * (1-P_L) / N_s)",
                floatfmt=".2e",
            )
        ]

        if self.includes_postselection:
            fields += [
                FieldHeader(
                    "dr",
                    full_label="Discard Rate per Shot",
                    kind="computed",
                    math_symbol="P_d",
                    compute_formula="N_d/N_s",
                    floatfmt=".2e",
                )
            ]
            fields += [
                FieldHeader(
                    "dr_error",
                    full_label="dr_error",
                    kind="computed",
                    math_symbol="delta_d",
                    compute_formula="sqrt(P_d * (1-P_d) / N_s)",
                    floatfmt=".2e",
                )
            ]

        fields += [FieldHeader("to_simulate", kind="internal", hidden=True)]

        self.simulation_table: SimTable = SimTable(fields=fields)

        # set default simulation parameters
        self.set_simulation_parameters()

    def __repr__(self) -> str:
        """Create a table to display protocol instances that are to be simulated."""
        return self.simulation_table.__repr__()

    def add_noise_model(
        self,
        noise_model: NoiseModel,
        *,
        label: str | float | tuple[str, float] = "noise_model",
    ) -> None:
        """Add a noise model that will be used in simulations.

        Multiple noise models can be added. Each one should have a unique label (`label_str`, `label_numeric`).

        Args:
            noise_model (NoiseModel): The noise model to add.
            label (str | float | tuple[str, float], optional): The label for the parameters. Defaults to 'noise_model'.

        Raises:
            ValueError: If `noise_model` is not a noise model.
            Exception: If `label` is already used for an existing noise model.

        """
        if not isinstance(noise_model, NoiseModel):
            raise ValueError("`noise_model` is not a noise model.")

        if label in self.noise_models:
            raise Exception(
                f"Noise model labelled by '{label}' has already been added."
            )
        self.noise_models[label] = noise_model

    def add_instance(
        self,
        *,
        noise_model_labels: (
            str
            | float
            | tuple[str, float]
            | list[str | float | tuple[str, float]]
            | None
        ) = None,
        decoder="pymatching",
        **kwargs,
    ):
        """Add instance of protocol parameters to be simulated.

        This method should be overridden to explicitly specify the protocol parameters with types.
        """
        if len(self.noise_models) == 0:
            raise RuntimeError(
                "Add at least one noise model before adding protocol instances."
            )
        # check that protocol parameters are correct
        parameters_model = self.protocol_parameters(**kwargs)

        if type(noise_model_labels) is str | float | tuple[str, float]:
            noise_model_labels = [noise_model_labels]
        elif noise_model_labels is None:
            noise_model_labels = self.noise_models.keys()

        if not all(label in self.noise_models for label in noise_model_labels):
            raise AttributeError("Noise model label not found.")

        for label in noise_model_labels:
            self.simulation_table.add_row(
                **parameters_model.model_dump(),
                noise_model_label=label,
                decoder=decoder,
                to_simulate=True,
            )

    def set_simulation_parameters(
        self,
        max_n_samples: int = 10**8,
        signal_to_noise: float = 10,
        num_workers: int = 8,
        save_data: bool = False,
        save_data_dir: str = "data/output",
        save_data_filename: Optional[str] = None,
    ):
        """Set simulation parameters

        Args:
            max_n_samples (int, optional): The maximum samples that will be collected. Defaults to 10**8.
            signal_to_noise (float, optional): Signal to noise ratio used to determine how many samples will be
                collected. Defaults to 10.
            num_workers (int, optional): The number of worker processes that sinter should use. Defaults to 8.
            save_data (bool, optional): Whether to save simulation data to file.
            save_data_dir (str, optional): Directory where data file is saved, which is created if needed. Defaults to
                'data/output'.
            save_data_filename (str, optional): The name of the pickle file containing list[stim.TaskStats]. Defaults to
                f"simulation_table_{self.protocol_name}.pkl".
        """
        if save_data_filename is None:
            save_data_filename = f"simulation_table_{self.protocol_name}.pkl"

        self.simulation_parameters = {
            "max_n_samples": max_n_samples,
            "signal_to_noise": signal_to_noise,
            "num_workers": num_workers,
            "save_data": save_data,
            "save_data_dir": save_data_dir,
            "save_data_filename": save_data_filename,
        }

    def execute_simulation(
        self,
    ) -> None:
        r"""Execute the simulation for the protocol instances specified in the simulation table.

        The Noise Profiler simulator uses a heuristic to avoid simulations that are unlikely to yield good statistics.
        It first collects $10\%$ of the samples. If no errors are observed, then the remaining samples are not collected.
        In this case, the output statistical parameters will have the value "F" (indicating failure).
        """
        # noise models specification list
        noise_models = [
            models.NoiseModelSpecificationModel(
                label=label,
                noise_model_name=self.noise_models[label].noise_model_name,
                parameters=self.noise_models[label].input_noise_parameters,
            )
            for label in self.noise_models
        ]
        psm = models.ProtocolSpecificationModel(
            protocol_category=self.protocol_category,
            protocol_subcategory=self.protocol_subcategory,
            protocol_name=self.protocol_name,
            code=models.CodeModel(name="rotated_surface_code"),
            simulation_table=self.simulation_table.to_model(),
            noise_models=noise_models,
            simulation_parameters=models.SimulationParametersModel(
                **self.simulation_parameters
            ),
        )

        # Format Protocol Model
        np_dict = psm.model_dump()
        np = {"protocols": [np_dict]}

        # Initialize Noise Profiler Client
        noise_profiler_client = NoiseProfilerClient(
            polling_interval=50, polling_max_attempts=20
        )
        # Define parameters
        hardware_params = HardwareParameters()
        hardware_params.load_from_dict(np)

        # Send Request to Noise Profiler
        try:
            response = noise_profiler_client.run_and_get_result(
                hardware_params=hardware_params,
            )
        except TopQADTimeoutError as e:
            timeout_message = (
                f" Please check the portal or call execute_simulation() again to"
                f" see the status of this job and, upon completion, to obtain"
                f" your results."
            )
            raise TopQADTimeoutError(f"{e} {timeout_message}")

        # Update the simulation table
        data_dict = response.model_dump()
        sim_table = data_dict.get("protocols", [{}])[0].get("simulation_table", {})
        sim_table = SimTable.from_json(json.dumps(sim_table))
        self.simulation_table = sim_table

    def fit_data(
        self,
        ind: str,
        dep: str,
        noise_model_label: str = "noise_model",
        SNR_threshold: float = 5,
        Abs_threshold: float = np.inf,
    ) -> tuple[Variable, ...]:
        """Fit data for some combination of variables.

        The fit function used must be present in self.fit_options[ind, dep].

        Args:
            ind (str): The independent variable name.
            dep (str): The dependent variable name.
            noise_model_label (str): The noise model for which to fit data. Defaults to "noise_model".
            SNR_threshold (float): Points with signal-to-noise below this threshold are discarded. Defaults to 5.
            Abs_threshold (float): Points whose value is higher than this absolute threshold are discarded. Defaults to `np.inf`.

        Raises:
            ValueError: If (ind, dep) is not a key in self.fit_options.

        Returns:
            tuple[Variable, ...]: The fit parameters as uncertainities Variable types. Use p.nominal_value and p.std_dev
            to access the stored values.
        """

        if (ind, dep) not in self.fit_options.keys():
            raise ValueError

        # only pick the specified noise model values
        sd = self.simulation_table.filter(
            condition=lambda s: s["noise_model_label"] == noise_model_label
        )

        # filter out any rows whose data has not been collected
        sd = sd.filter(condition=lambda s: s[dep] != "?")

        # extract data
        xs, ys, es = sd[[ind]].data(), sd[[dep]].data(), sd[[dep + "_error"]].data()

        fspec = self.fit_options[ind, dep]

        fit_ansatz_func = convert_sympy_formula_to_numpy_func(
            formula=fspec.fit_ansatz, scale=fspec.y_scale
        )

        fitted_params = fit_data(
            xs,
            ys,
            es,
            fit_ansatz=fit_ansatz_func,
            fit_param_bounds=fspec.param_bounds,
            fit_y_scale=fspec.y_scale,
            SNR_threshold=SNR_threshold,
            Abs_threshold=Abs_threshold,
        )
        return fitted_params

    def plot(
        self,
        ind: str,
        dep: str,
        fit: bool = False,
        SNR_threshold: float = 5,
        Abs_threshold: float = np.inf,
        extrapolate: bool = False,
        extrapolate_to_dep: float = 1e-8,
        save_fig: bool = False,
        save_fig_dir: str = "data/output",
        save_fig_filename: Optional[str] = None,
        ax: Axes | None = None,
    ):
        """Plot the collected simulation data.

        Each noise model data is plotted as a separate line on the plot.

        Args:
            ind (str): The independent variable to use on the horizontal axis.
            dep (str): The dependent variable to use on the vertical axis. Can only be "ler" or "dr".
            fit (bool, optional): Whether to fit the data. Defaults to False.
            SNR_threshold (float): Points with signal-to-noise below this threshold are discarded for fits. Defaults to 5.
            Abs_threshold (float): Points whose value is higher than this absolute threshold are discarded for fits. Defaults to `np.inf`.
            extrapolate (bool, optional): Whether to extrapolate the dep var to. Defaults to False.
            extrapolate_to_dep (float, optional): The value to extrapolate the dep var to. Defaults to 1e-8.
            save_fig (bool, optional): Whether to safe the figure. Defaults to False.
            save_fig_dir (str, optional): Directory in which figure is saved. Directory is created if needed. Defaults
                to 'data/output'.
            save_fig_filename(str, optional): Filename of saved figure. Defaults to
                f'plot_{self.protocol_name}_{ind}_{dep}.png'.
            ax (Axes, optional): A matplotlib Axes. If passed, then the plot is added to this axis. Defaults to None.

        Raises:
            ValueError: If (ind, dep) is not a key in self.fit_options.
            ValueError: If ax is not None or does not have type Axes.
            ValueError: If extrapolation fails.
            Exception: Fitting failed to yield reasonable values.
        """

        if fit and (ind, dep) not in self.fit_options.keys():
            raise ValueError(
                f"Add {(ind, dep)} to self.fit_options to plot this combination."
            )

        if ax is not None and type(ax) is not Axes:
            raise ValueError("Unrecognized ax object.")

        if ax is None:
            fig, plot_ax = plt.subplots(figsize=(4, 4))
        else:
            fig = ax.get_figure()
            plot_ax = ax

        cmap = plt.get_cmap("Dark2").colors
        plot_ax.set_prop_cycle(color=cmap)

        # enumerate over noise models.
        for i, noise_model_label in enumerate(self.noise_models.keys()):

            sd = self.simulation_table.filter(
                condition=lambda s: s["noise_model_label"] == noise_model_label
            )

            # filter out any rows whose data has not been collected
            sd = sd.filter(condition=lambda s: s[dep] != "?")

            xs, ys, es = sd[[ind]].data(), sd[[dep]].data(), sd[[dep + "_error"]].data()

            # First draw data points
            if fit:
                # if we also draw the fit line, then data is not labelled for legend
                plot_ax.errorbar(
                    xs,
                    ys,
                    yerr=es,
                    ls="",
                    capsize=3,
                    mfc=cmap[i],
                    marker="o",
                    color=cmap[i],
                    ms=1.25,
                )
            else:
                plot_ax.errorbar(
                    xs,
                    ys,
                    yerr=es,
                    ls="",
                    capsize=3,
                    mfc=cmap[i],
                    marker="o",
                    color=cmap[i],
                    ms=1.25,
                    label=noise_model_label,
                )
                plot_ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(1, 1))

            # If fitting then find parameters.
            if fit:
                fspec = self.fit_options[ind, dep]

                fit_ansatz_func_linear = convert_sympy_formula_to_numpy_func(
                    formula=fspec.fit_ansatz, scale="linear"
                )

                fit_ansatz_func_scaled = convert_sympy_formula_to_numpy_func(
                    formula=fspec.fit_ansatz, scale=fspec.y_scale
                )

                # if we use the uncertainities Variables for parameters, then the fit function
                # must be wrapped. Unwrapped function will give error.
                # Unfortunately, these wrapped functions don't work with vector inputs,
                # so they must be manually called for all sets of inputs.
                uncertainites_wrapped_fit_ansatz = wrap(fit_ansatz_func_linear)

                fitted_params = fit_data(
                    xs,
                    ys,
                    es,
                    fit_ansatz=fit_ansatz_func_scaled,
                    fit_param_bounds=fspec.param_bounds,
                    fit_y_scale=fspec.y_scale,
                    SNR_threshold=SNR_threshold,
                    Abs_threshold=Abs_threshold,
                )

                try:
                    [u_format(p) for p in fitted_params]
                except:
                    raise Exception("Fit parameters cannot be displayed.")

                # now figure out the fit line depending on if we are extrapolating
                if not extrapolate:
                    xs_array = np.array(xs)

                else:
                    out = root_scalar(
                        lambda d: fit_ansatz_func_linear(
                            d, *(p.n for p in fitted_params)
                        )
                        - extrapolate_to_dep,
                        x0=xs[-1],
                    )

                    # Seems hardcoded for integer type ind vars. Generalize this logic.
                    if out.converged:
                        root = int(np.ceil(out.root))
                        max_xs = root + 1 if root % 2 == 0 else root
                    else:
                        raise ValueError("Failed to extrapolate to indicated value.")

                    xs_array = np.arange(xs[0], max_xs + 1, 1, dtype=int)

                # Now draw
                legend_label = (
                    f"{noise_model_label} \n"
                    + "$"
                    + fspec.fit_ansatz_latex.format(
                        **{f"p_{i}": u_format(p) for i, p in enumerate(fitted_params)}
                    )
                    + "$"
                )

                fitted_ys = np.array(
                    [
                        uncertainites_wrapped_fit_ansatz(d, *fitted_params)
                        for d in xs_array
                    ]
                )

                fitted_ys_mean = unumpy.nominal_values(fitted_ys)
                fitted_ys_std = unumpy.std_devs(fitted_ys)

                # Here we plot a central line and a shaded area around it to indicate uncertainity
                plot_ax.plot(
                    xs_array, fitted_ys_mean, color=cmap[i], ls="-", label=legend_label
                )
                plot_ax.fill_between(
                    xs_array,
                    fitted_ys_mean - fitted_ys_std,
                    fitted_ys_mean + fitted_ys_std,
                    color=cmap[i],
                    ls="",
                    alpha=0.5,
                )

                plot_ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(1, 1))

                if fspec.y_scale == "log":
                    plot_ax.semilogy(base=10)

        if type(ind) == str:
            plot_ax.set_xlabel(self.simulation_table.fields[ind].full_label)
        else:
            plot_ax.set_xlabel(self.simulation_table.fields[ind[0]].full_label)
        if type(dep) == str:
            plot_ax.set_ylabel(self.simulation_table.fields[dep].full_label)
        else:
            plot_ax.set_ylabel(self.simulation_table.fields[dep[0]].full_label)
        plot_ax.grid(which="major", alpha=0.2)
        plot_ax.grid(which="minor", alpha=0.05)

        # save fig if needed
        if save_fig:
            if save_fig_filename is None:
                save_fig_filename = f"plot_{self.protocol_name}_{ind}_{dep}.png"
            Path(save_fig_dir).mkdir(parents=True, exist_ok=True)
            save_fig_path = Path(save_fig_dir, save_fig_filename)
            fig.savefig(save_fig_path, bbox_inches="tight")

        if ax is not None:
            plt.close(fig)
