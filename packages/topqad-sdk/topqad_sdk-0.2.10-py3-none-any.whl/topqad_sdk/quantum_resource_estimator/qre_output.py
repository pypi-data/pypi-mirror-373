import json
from .report import Report
from pathlib import Path


def build_report_views(results):
    """
    Parse raw quantum resource estimation report results into structured report objects.

    This function converts the raw quantum resource estimation report data into two forms:
      1. A summary view (`QREOutputs`) aggregating all reports.
      2. A dictionary mapping each architecture/pareto point to a
         detailed `Report` object.

    Args:
        results: An object containing quantum resource estimation reports, expected to have
                 a `results.assembler_reports` attribute.

    Returns:
        tuple:
            - summary_view (QREOutputs): Aggregated summary of all qre reports.
            - full_reports (dict[str, Report]): Dictionary of detailed report objects,
              keyed by pareto point or architecture name.
    """
    summary_view = None
    full_reports = {}

    reports_dict = {
        report.pareto_point: report.model_dump() for report in results.assembler_reports
    }

    summary_view = QREOutputs(reports_dict)

    for name, data in reports_dict.items():
        full_reports[name] = Report(data)

    return summary_view, full_reports


def download_reports(reports: dict, output_file: str | Path = "reports.json"):
    """
    Save all Report objects into a single JSON file.

    Each Report object's internal `data` dictionary is serialized.

    Args:
        reports (dict): Dictionary of Report objects, keyed by name.
        output_file (str | Path, optional): Path of the JSON file to create.
            Defaults to "reports.json" in the current directory.
    """
    output_file = Path(output_file)

    # Convert each Report object to its internal dict
    serializable_reports = {name: report.data for name, report in reports.items()}

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(serializable_reports, f, indent=2)

    print("Successfully downloaded QRE Reports")


class QREOutputs:
    """
    Result of the Quantum Resource Estimator containing the report contents on the Pareto frontier
    solutions.
    """

    reports: dict[str, Report]

    def as_dict(self):
        """Convert the model to a dictionary."""
        return {name: report.data for name, report in self.reports.items()}

    def to_json(self, save_path="qre_output.json", indent=2):
        """
        Save the quantum resource estimaton output to a JSON file.

        Args:
            save_path (str or Path): Path to save the JSON file. Defaults to "qre_output.json".
            indent (int): Number of spaces to use for indentation in the JSON file. Defaults to 2.
        """
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(self.as_dict(), f, indent=indent)
        print(f"Quantum resource estimation output JSON saved to {save_path}")

    def __init__(self, reports: dict[str, dict]):
        """
        Initialize the QREOutputs with reports.

        Args:
            reports (dict): Dictionary containing report contents for each slowdown
            factor representing optimal space-time tradeoffs.
        """
        self.reports = {str(k): Report(v) for k, v in reports.items()}

    def get_summary(self) -> dict:
        """
        Returns a summary dictionary for each architecture, mapping architecture name to
        its summary fields.
        """
        return {arch: report.summary for arch, report in self.reports.items()}

    def time_optimal_architecture(self) -> Report:
        """
        Returns the time-optimal architecture report.

        The time-optimal architecture is the one with the lowest expected runtime.
        """
        if not self.reports:
            raise ValueError(
                "No reports available to determine time-optimal architecture."
            )

        # Find the report with the minimum expected runtime
        return min(
            self.reports.values(),
            key=lambda r: r.summary.get("expected_runtime", float("inf")),
        )

    def space_optimal_architecture(self) -> Report:
        """
        Returns the space-optimal architecture report.

        The space-optimal architecture is the one with the lowest number of physical qubits.
        """
        if not self.reports:
            raise ValueError(
                "No reports available to determine space-optimal architecture."
            )

        # Find the report with the minimum number of physical qubits
        return min(
            self.reports.values(),
            key=lambda r: r.summary.get("num_physical_qubits", float("inf")),
        )

    def show_report(self, report_name: str) -> Report:
        """
        Returns the report for a specific architecture.

        Args:
            report_name (str): The name of the architecture to retrieve the report for.

        Returns:
            Report: The report object for the specified architecture.
        """
        if report_name not in self.reports:
            raise ValueError(
                f"Report '{report_name}' not found in quantum resource estimation output."
            )
        return self.reports[report_name]

    def _repr_html_(self):
        """
        HTML representation for Jupyter Notebook.
        Shows a table with Architecture, Expected Runtime, Physical Qubit Count,
        Core Processor Code Distance, Magic State Factory Code Distance, and Number of
        Distillation Units.
        """
        if not self.reports:
            return "<i>No reports available.</i>"

        # Columns to display
        columns = [
            ("Architecture", None),
            ("Expected Runtime", "expected_runtime"),
            ("Physical Qubit Count", "num_physical_qubits"),
            ("Core Code Distance", "core_processor_code_distance"),
            ("MSF Code Distance", "magic_state_factory_code_distance"),
            ("# Distillation Units", "num_distillation_units"),
        ]

        def fmt(val):
            if isinstance(val, float):
                if abs(val) >= 1e6 or (abs(val) < 1e-3 and val != 0):
                    return f"{val:.3e}"
                return f"{val:.6g}"
            return val

        def fmt_qubits(val):
            if isinstance(val, int) or (isinstance(val, float) and val.is_integer()):
                return f"{val:,}"
            else:
                return f"{val:,.3f}"

        table_rows = []
        # Header
        header = (
            "<tr>"
            + "".join(
                f"<th style='text-align:left; padding:2px 6px;'>{col[0]}</th>"
                for col in columns
            )
            + "</tr>"
        )
        table_rows.append(header)
        # Data rows
        for arch_name, report in self.reports.items():
            expected_runtime = report.summary.get("expected_runtime", "")
            physical_qubit_count = report.summary.get("num_physical_qubits", "")
            core_processor_code_distance = report.physical_resources_estimation.get(
                "core_processor_info", {}
            ).get("code_distance", "")
            magic_state_factory_code_distance = (
                report.physical_resources_estimation.get(
                    "magic_state_factory_info", {}
                ).get("code_distance", "")
            )
            num_distillation_units = report.magic_state_factory.get(
                "num_distillation_units", ""
            )

            row = (
                "<tr>"
                f"<td style='padding:2px 6px;'>{arch_name}</td>"
                f"<td style='padding:2px 6px;'>{expected_runtime}</td>"
                f"<td style='padding:2px 6px;'>{fmt_qubits(physical_qubit_count)}</td>"
                f"<td style='padding:2px 6px;'>{fmt(core_processor_code_distance)}</td>"
                f"<td style='padding:2px 6px;'>{fmt(magic_state_factory_code_distance)}</td>"
                f"<td style='padding:2px 6px;'>{fmt(num_distillation_units)}</td>"
                "</tr>"
            )
            table_rows.append(row)

        template_str = f"""
        <div style="line-height:1.3; font-size: 95%;">
        <b>Space-Time Optimal Architectures</b><br>
        <table style="border-collapse: collapse; font-size: 90%; margin-top: 8px;">
            {''.join(table_rows)}
        </table>
        </div>
        """
        return template_str
