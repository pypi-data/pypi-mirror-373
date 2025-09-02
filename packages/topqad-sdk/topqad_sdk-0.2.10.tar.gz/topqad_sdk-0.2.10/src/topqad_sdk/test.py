from src.topqad_sdk import noiseprofiler
from src.topqad_sdk.library import HardwareParameters


def main():
    physical_depolarizing_baseline = {
        "preparation_error": {"value": 0.02, "unit": ""},
        "reset_error": {"value": 0.01, "unit": ""},
        "measurement_error": {"value": 0.01, "unit": ""},
        "one_qubit_gate_error": {"value": 0.0004, "unit": ""},
        "two_qubit_gate_error": {"value": 0.003, "unit": ""},
        "T1_longitudinal_relaxation_time": {"value": 100, "unit": "μs"},
        "T2_transverse_relaxation_time": {"value": 100, "unit": "μs"},
        "preparation_time": {"value": 1000, "unit": "ns"},
        "reset_time": {"value": 200, "unit": "ns"},
        "measurement_time": {"value": 200, "unit": "ns"},
        "one_qubit_gate_time": {"value": 25, "unit": "ns"},
        "two_qubit_gate_time": {"value": 25, "unit": "ns"},
    }

    # creates noise model
    noise_model_baseline = noiseprofiler.libnoise.PhysicalDepolarizing.from_dict(
        physical_depolarizing_baseline
    )

    # memory
    memory = noiseprofiler.libprotocols.Memory()
    memory.add_noise_model(noise_model_baseline, label="baseline")
    for d in range(3, 7 + 1, 2):
        memory.add_instance(distance=d, rounds=d, basis="Z")

    memory.execute_simulation()

    print(memory.simulation_table)

    # magic state prep
    magic = noiseprofiler.libprotocols.MagicStatePreparationRepCode()
    magic.add_noise_model(noise_model_baseline, label="baseline")
    for d_2 in range(3, 7 + 1, 2):
        magic.add_instance(distances=[3, d_2], rounds=[2, None])

    magic.execute_simulation()

    print(magic.simulation_table)


if __name__ == "__main__":
    main()
