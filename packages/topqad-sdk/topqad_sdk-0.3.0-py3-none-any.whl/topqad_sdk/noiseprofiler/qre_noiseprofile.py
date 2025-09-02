"""Create the noise profile needed to perform qre."""

from importlib.resources import files
import topqad_sdk.noiseprofiler.data.qre_presets as qre_presets

from topqad_sdk.noiseprofiler.libprotocols import (
    Memory,
    MagicStatePreparationHookInjection,
    MagicStatePreparationRepCode,
    LatticeSurgery,
)
from topqad_sdk.noiseprofiler.models import RequestResponseModel
from topqad_sdk.noiseprofiler.libnoise.models import NoiseModelSpecificationModel
from topqad_sdk.noiseprofiler.libprotocols.models import (
    CodeModel,
    FitDataModel,
    FitParametersModel,
    ProtocolSpecificationModel,
    SimulationParametersModel,
    StabilizationTime,
)

preset_names = [
    "physical_depolarizing_baseline",
    "physical_depolarizing_baseline_throughput_matched",
    "physical_depolarizing_baseline_logical_time_matched",
    "physical_depolarizing_target",
    "physical_depolarizing_target_throughput_matched",
    "physical_depolarizing_target_logical_time_matched",
    "physical_depolarizing_desired",
    "physical_depolarizing_desired_throughput_matched",
    "physical_depolarizing_desired_logical_time_matched",
]


def get_preset_names():
    print("The available presets are as follows:")
    for name in preset_names:
        print(f'- "{name}"')


def noise_profile_from_preset(preset_name: str):
    """Load a precomputed noise profile appropriate for quantum resource estimation.

    Args:
        preset_name (str): The name of the noise profile to load. Options include
            - "physical_depolarizing_baseline"
            - "physical_depolarizing_baseline_throughput_matched"
            - "physical_depolarizing_baseline_logical_time_matched"
            - "physical_depolarizing_target"
            - "physical_depolarizing_target_throughput_matched"
            - "physical_depolarizing_target_logical_time_matched"
            - "physical_depolarizing_desired"
            - "physical_depolarizing_desired_throughput_matched"
            - "physical_depolarizing_desired_logical_time_matched"

        The profiles have the noise model parameters as follows:
        - physical_depolarizing_baseline*: parameters associated with existing state-of-the-art hardware.
        - physical_depolarizing_target*: parameters aligned with near-term research goals.
        - physical_depolarizing_desired*: an optimistic target for future high-quality devices.

        The profiles have decoder reaction times as follows:
        - base: a SotA2025 decoder that has high reaction time compared to the logical cycle time.
        - throughput-matched: the decoder's throughput matches the logical cycle time. However, the reaction time of the
          decoder is larger than the logical cycle time.
        - logical_time_matched: reaction time equal to the logical cycle time.

    Raises:
        ValueError: If unknown preset name provided.

    Returns:
        str: A json string with the noise profile.
    """
    if preset_name not in preset_names:
        raise ValueError(
            f"`preset_name` = {preset_name!r} must be one of {preset_names}"
        )

    preset_filename = preset_name + ".json"
    noise_profile = files(qre_presets).joinpath(preset_filename).read_text()

    return noise_profile


def noise_profile_from_protocols(
    memory: Memory,
    magic_state_prep: MagicStatePreparationHookInjection | MagicStatePreparationRepCode,
    lattice_surgery_distance: LatticeSurgery,
    lattice_surgery_rounds: LatticeSurgery,
):
    """Create a noise profile from a set of already computed protocols.

    This noise profile can be passed to "qre" to obtain a resource estimate.

    Each input object should have enough simulation data in it that the `fit_data` method outputs the correct fit. The
    `fit_options` may be modified for this purpose as well. Before calling this function, make sure that each fit
    extrapolates well to very low logical error rates.

    Args:
        memory (Memory): Perform a memory experiment where the distance is varied.
        magic_state_prep (MagicStatePreparationHookInjection | MagicStatePreparationRepCode): A magic state prep object
            where the largest distance of the protocol is varied.
        lattice_surgery_distance (LatticeSurgery): A lattice surgery object where the distance is varied.
        lattice_surgery_rounds (LatticeSurgery): A lattice surgery object where the merge round are varied.

    Raises:
        ValueError: If multiple noise models are founds in any of the inputs.
        ValueError: If the two lattice surgery have different noise models.

    Returns:
        str: A json string with the noise profile.
    """

    ph_list = [
        memory,
        magic_state_prep,
        lattice_surgery_distance,
        lattice_surgery_rounds,
    ]

    if any([len(protocol_handler.noise_models) != 1 for protocol_handler in ph_list]):
        raise ValueError("Each input should have exactly one noise model.")

    noise_model_label_distance = list(lattice_surgery_distance.noise_models.keys())[0]
    noise_model_label_rounds = list(lattice_surgery_rounds.noise_models.keys())[0]
    if (
        lattice_surgery_distance.noise_models[noise_model_label_distance]
        != lattice_surgery_rounds.noise_models[noise_model_label_rounds]
    ):
        raise ValueError(
            "lattice_surgery_distance and lattice_surgery_rounds have distinct noise models."
        )

    # Memory
    protocol_handler = memory
    noise_model_label = list(protocol_handler.noise_models.keys())[0]

    # create fits
    computed_fits = []

    fit_requests = [
        FitDataModel(noise_model_label=noise_model_label, ind="distance", dep="ler"),
        FitDataModel(
            noise_model_label=noise_model_label, ind="distance", dep="reaction_time"
        ),
    ]
    for fit_request in fit_requests:
        fit_params = protocol_handler.fit_data(
            ind=fit_request.ind,
            dep=fit_request.dep,
            noise_model_label=fit_request.noise_model_label,
        )

        fit_params_dict = {
            f"p_{i}": FitParametersModel(value=fp.nominal_value, error=fp.std_dev)
            for i, fp in enumerate(fit_params)
        }

        fspec = protocol_handler.fit_options[fit_request.ind, fit_request.dep]
        fit_data = FitDataModel(
            noise_model_label=fit_request.noise_model_label,
            dep=fit_request.dep,
            ind=fit_request.ind,
            fit_bounds=None,
            ind_math_symbol=fspec.ind_math_symbol,
            functional_form=fspec.fit_ansatz,
            fit_parameters=fit_params_dict,
        )

        computed_fits.append(fit_data)

    # add stabilization times
    stabilization_times_list = []
    for noise_model_label, noise_model in protocol_handler.noise_models.items():
        stabilization_time = noise_model.calculate_stabilization_time()
        stm = StabilizationTime(
            noise_model_label=noise_model_label, stabilization_time=stabilization_time
        )
        stabilization_times_list.append(stm)

    noise_models = [
        NoiseModelSpecificationModel(
            label=label,
            noise_model_name=protocol_handler.noise_models[label].noise_model_name,
            parameters=protocol_handler.noise_models[label].input_noise_parameters,
        )
        for label in protocol_handler.noise_models
    ]
    psm_memory = ProtocolSpecificationModel(
        protocol_category=protocol_handler.protocol_category,
        protocol_subcategory=protocol_handler.protocol_subcategory,
        protocol_name=protocol_handler.protocol_name,
        code=CodeModel(name="rotated_surface_code"),
        simulation_table=protocol_handler.simulation_table.to_model(),
        noise_models=noise_models,
        simulation_parameters=SimulationParametersModel(
            **protocol_handler.simulation_parameters
        ),
        fits=computed_fits,
        stabilization_times=stabilization_times_list,
    )

    # Magic state prep
    protocol_handler = magic_state_prep
    noise_model_label = list(protocol_handler.noise_models.keys())[0]

    # create fits
    computed_fits = []

    if protocol_handler.protocol_name == "magic_state_preparation_hook_injection":
        fit_requests = [
            FitDataModel(noise_model_label=noise_model_label, ind="d_2", dep="ler"),
            FitDataModel(noise_model_label=noise_model_label, ind="d_1", dep="dr"),
        ]
    elif protocol_handler.protocol_name == "magic_state_preparation_rep_code":
        fit_requests = [
            FitDataModel(
                noise_model_label=noise_model_label, ind=("distances", 1), dep="ler"
            ),
            FitDataModel(
                noise_model_label=noise_model_label, ind=("distances", 0), dep="dr"
            ),
        ]

    for fit_request in fit_requests:
        fit_params = protocol_handler.fit_data(
            ind=fit_request.ind,
            dep=fit_request.dep,
            noise_model_label=fit_request.noise_model_label,
        )

        fit_params_dict = {
            f"p_{i}": FitParametersModel(value=fp.nominal_value, error=fp.std_dev)
            for i, fp in enumerate(fit_params)
        }

        fspec = protocol_handler.fit_options[fit_request.ind, fit_request.dep]
        functional_form = fspec.fit_ansatz
        if fit_request.dep == "ler" and functional_form.find("d_1") == -1:
            functional_form += " + 0*d_1"

        fit_data = FitDataModel(
            noise_model_label=fit_request.noise_model_label,
            dep=fit_request.dep,
            ind=fit_request.ind,
            fit_bounds=None,
            ind_math_symbol=fspec.ind_math_symbol,
            functional_form=functional_form,
            fit_parameters=fit_params_dict,
        )

        computed_fits.append(fit_data)

    # add stabilization times
    stabilization_times_list = []
    for noise_model_label, noise_model in protocol_handler.noise_models.items():
        stabilization_time = noise_model.calculate_stabilization_time()
        stm = StabilizationTime(
            noise_model_label=noise_model_label, stabilization_time=stabilization_time
        )
        stabilization_times_list.append(stm)

    noise_models = [
        NoiseModelSpecificationModel(
            label=label,
            noise_model_name=protocol_handler.noise_models[label].noise_model_name,
            parameters=protocol_handler.noise_models[label].input_noise_parameters,
        )
        for label in protocol_handler.noise_models
    ]
    psm_magic_state = ProtocolSpecificationModel(
        protocol_category=protocol_handler.protocol_category,
        protocol_subcategory=protocol_handler.protocol_subcategory,
        protocol_name=protocol_handler.protocol_name,
        code=CodeModel(name="rotated_surface_code"),
        simulation_table=protocol_handler.simulation_table.to_model(),
        noise_models=noise_models,
        simulation_parameters=SimulationParametersModel(
            **protocol_handler.simulation_parameters
        ),
        fits=computed_fits,
        stabilization_times=stabilization_times_list,
    )

    # Lattice surgery
    # distance
    protocol_handler = lattice_surgery_distance
    noise_model_label = list(protocol_handler.noise_models.keys())[0]

    # create fits
    computed_fits = []

    # First do the reaction time
    fit_requests = [
        FitDataModel(
            noise_model_label=noise_model_label, ind="distance", dep="reaction_time"
        )
    ]
    for fit_request in fit_requests:
        fit_params = protocol_handler.fit_data(
            ind=fit_request.ind,
            dep=fit_request.dep,
            noise_model_label=fit_request.noise_model_label,
        )

        fit_params_dict = {
            f"p_{i}": FitParametersModel(value=fp.nominal_value, error=fp.std_dev)
            for i, fp in enumerate(fit_params)
        }

        fspec = protocol_handler.fit_options[fit_request.ind, fit_request.dep]
        fit_data = FitDataModel(
            noise_model_label=fit_request.noise_model_label,
            dep=fit_request.dep,
            ind=fit_request.ind,
            fit_bounds=None,
            ind_math_symbol=fspec.ind_math_symbol,
            functional_form=fspec.fit_ansatz,
            fit_parameters=fit_params_dict,
        )

        computed_fits.append(fit_data)

    # find distance parameters
    fit_params = protocol_handler.fit_data(
        ind="distance", dep="ler", noise_model_label=noise_model_label
    )
    fit_params_dict = {
        f"p_{i}": FitParametersModel(value=fp.nominal_value, error=fp.std_dev)
        for i, fp in enumerate(fit_params)
    }

    # find rounds parameters
    protocol_handler = lattice_surgery_rounds
    noise_model_label = list(protocol_handler.noise_models.keys())[0]

    fit_params = protocol_handler.fit_data(
        ind=("rounds", 1), dep="ler", noise_model_label=noise_model_label
    )

    fit_params_dict |= {
        f"p_{i+2}": FitParametersModel(value=fp.nominal_value, error=fp.std_dev)
        for i, fp in enumerate(fit_params)
    }

    # now construct the full model
    fit_ansatz_lattice_surgery = (
        "p_0 * (K*d + B*d + K)* d * p_1**(-(d+1)/2) + p_2 * B * d**2 * p_3**(-(d+1)/2)"
    )

    fit_data = FitDataModel(
        noise_model_label=noise_model_label,
        dep="ler",
        ind="distance",
        fit_bounds=None,
        ind_math_symbol="d",
        functional_form=fit_ansatz_lattice_surgery,
        fit_parameters=fit_params_dict,
    )

    # Add fit data first
    computed_fits = [fit_data] + computed_fits

    # add stabilization times
    stabilization_times_list = []
    for noise_model_label, noise_model in protocol_handler.noise_models.items():
        stabilization_time = noise_model.calculate_stabilization_time()
        stm = StabilizationTime(
            noise_model_label=noise_model_label, stabilization_time=stabilization_time
        )
        stabilization_times_list.append(stm)

    noise_models = [
        NoiseModelSpecificationModel(
            label=label,
            noise_model_name=protocol_handler.noise_models[label].noise_model_name,
            parameters=protocol_handler.noise_models[label].input_noise_parameters,
        )
        for label in protocol_handler.noise_models
    ]
    psm_lattice_surgery = ProtocolSpecificationModel(
        protocol_category=protocol_handler.protocol_category,
        protocol_subcategory=protocol_handler.protocol_subcategory,
        protocol_name=protocol_handler.protocol_name,
        code=CodeModel(name="rotated_surface_code"),
        simulation_table=protocol_handler.simulation_table.to_model(),
        noise_models=noise_models,
        simulation_parameters=SimulationParametersModel(
            **protocol_handler.simulation_parameters
        ),
        fits=computed_fits,
        stabilization_times=stabilization_times_list,
    )

    noise_profile = RequestResponseModel(
        protocols=[psm_memory, psm_magic_state, psm_lattice_surgery]
    )

    return noise_profile.model_dump_json(indent=4)
