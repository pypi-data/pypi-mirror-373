import pandas as pd
from jinja2 import Template

# Define common inline styles as constants
COMMON_STYLES = {
    "box": (
        "border: 1px solid #ccc; "
        "border-radius: 6px; "
        "padding: 12px; "
        "width: 220px; "
        "margin-bottom: 10px;"
    ),
    "title": "font-size: 14px; font-weight: bold; margin-bottom: 4px;",
    "value": "font-size: 18px; font-weight: bold;",
    "details_style": "margin-bottom: 0em;",
    "summary_style": "cursor: pointer; font-size: 16px; font-weight: bold; padding: 4px 0;",
    "p_style_summary": "margin: 4px 0 12px 0; font-size: 14px; color: #555;",
    "p_style_title": "margin: 4px 0 8px 0; font-size: 13px;",
    "div_style": "margin-left: 20px; margin-top: 5px;",
    "ul_style": "margin: 4px 0 12px 0; padding-left: 18px; font-size: 13px;",
    "table_style": "margin: 4px 0 12px 0; font-size: 13px; border: '0'",
    "section_indent": "margin-left: 20px;",
}


class Report:
    """
    Represents a detailed quantum resource estimation report with structured access to its fields.
    """

    def __init__(self, report: dict):
        """
        Initialize the Report with a dictionary containing report data.

        Args:
            report (dict): Dictionary containing report data.
        """
        self.report = report
        self.data = self._flatten_value_unit_fields(report)

        # Optionally, you can extract top-level fields for easier access
        self.summary = self.data.get("summary", {})
        self.error_budgets = self.data.get("error_budgets", {})
        self.physical_resources_estimation = self.data.get(
            "physical_resources_estimation", {}
        )
        self.magic_state_factory = self.data.get("magic_state_factory", {})
        self.device_emulation = self.data.get("device_emulation", {})
        self.logical_tiles = self.data.get("logical_tiles", {})
        self.schedule_metadata = self.data.get("schedule_metadata", {})

    def _flatten_value_unit_fields(self, report: dict) -> dict:
        """
        Recursively traverse the report data and convert any dict of the form
        {"value": xx, "unit": yy} to the string "xx yy", with value rounded to 2 decimals.
        """

        def _flatten(obj):
            if isinstance(obj, dict):
                if set(obj.keys()) == {"value", "unit"}:
                    value = obj["value"]
                    # Try to round if value is a number
                    if isinstance(value, (int, float)):
                        value = round(value, 2)
                    return f"{value} {obj['unit']}"
                return {k: _flatten(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [_flatten(item) for item in obj]
            else:
                return obj

        return _flatten(report)

    def _repr_html_(self):
        html_sections = [
            "<h2>Assembler Report Summary</h2>",
            self._render_summary(),
            self._render_error_budget(),
            self._render_logical_resources(),
            self._render_physical_resources(),
            self._render_magic_state_factory(),
            self._render_noise_profiling(),
            self._render_compiling(),
        ]
        return "\n".join(html_sections)

    def _render_summary(self):
        summary = self.data.get("summary", {})

        runtime_info = summary.get("expected_runtime", {})
        if isinstance(runtime_info, dict):
            runtime_str = (
                f"{runtime_info.get('value', 'N/A')} {runtime_info.get('unit', '')}"
            )
        else:
            runtime_str = str(runtime_info)

        qubit_count = summary.get("num_physical_qubits", "N/A")
        qubit_str = f"{qubit_count:,}" if isinstance(qubit_count, int) else qubit_count

        cost = summary.get("computation_cost", 0)

        return f"""
        <div style="display: flex; gap: 20px; margin-bottom: 20px;">
            <div style="{COMMON_STYLES['box']}">
            <b style="{COMMON_STYLES['title']}">Expected Runtime</b><br>
            <span style="{COMMON_STYLES['value']}">{runtime_str}</span>
            </div>
            <div style="{COMMON_STYLES['box']}">
            <b style="{COMMON_STYLES['title']}">Physical Qubit Count</b><br>
            <span style="{COMMON_STYLES['value']}">{qubit_str}</span>
            </div>
            <div style="{COMMON_STYLES['box']}">
            <b style="{COMMON_STYLES['title']}">Computation Cost</b><br>
            <span style="{COMMON_STYLES['value']}">${cost:,.2f}</span>
            </div>
        </div>
        """

    def _render_error_budget(self):
        error_data = self.data.get("error_budgets", {})
        output = error_data.get("output", {})
        budget = error_data.get("input", {}).get("target_error_bound", "N/A") * 100

        # Extract component errors
        sk = output.get("synthesis_error", 0) * 100
        algo = output.get("core_processor_error", 0) * 100
        factory = output.get("magic_state_factory_error", 0) * 100

        accumulated = output.get("accumulated_error_bound", 0) * 100

        def format_percentage(value):
            if value == 0:
                return "0%"
            elif value < 1e-6:
                return f"{value:.2e}"
            else:
                return f"{value:.4f}%"

        # Summary and breakdown
        summary_html = f"""
        <div style="{COMMON_STYLES['div_style']}">
            <b>Target Error Budget:</b> {format_percentage(budget)}<br>
            <b>Accumulated Error:</b> {format_percentage(accumulated)}<br>
        </div>
        """

        breakdown_df = pd.DataFrame(
            {
                "Error Source": ["Synthesis", "Core Processor", "Magic State Factory"],
                "Error Rate": [
                    format_percentage(sk),
                    format_percentage(algo),
                    format_percentage(factory),
                ],
            }
        )

        breakdown_html = breakdown_df.to_html(
            index=False,
            escape=False,
            border=0,
            classes="error-breakdown",
        )

        note_html = f"""
        <p style="{COMMON_STYLES['p_style_summary']}">
            Overall error tolerance set for the application and how it is allocated across key components.
        </p>
        """

        # Entire collapsible section
        return f"""
        <details style="{COMMON_STYLES['details_style']}">
            <summary style="{COMMON_STYLES['summary_style']}">Error Budget</summary>
            <div style="{COMMON_STYLES['div_style']}">
            {note_html}
            {summary_html}
            {breakdown_html}
            </div>
        </details>
        """

    def _render_logical_resources(self):
        raw = self.data.get("logical_tiles", {})

        def merge_counts(a, b):
            keys = set(a) | set(b)
            return {k: a.get(k, 0) + b.get(k, 0) for k in keys}

        core = merge_counts(raw.get("memory", {}), raw.get("buffer", {}))

        # Collect MSF levels dynamically
        msf_entries = []
        for k in raw:
            if k.startswith("msf_level_"):
                try:
                    level_num = int(k.split("_")[-1])
                    msf_entries.append((level_num, raw[k]))
                except ValueError:
                    continue  # in case of malformed keys

        # Sort by level number
        msf_entries.sort(key=lambda x: x[0])

        # Add human-readable zone names and grouped data
        grouped = [(f"MSF Level {lvl}", counts) for lvl, counts in msf_entries]
        grouped.append(("Core Processor", core))

        rename = {
            "data": "Computational",  # default label for core processor
            "bus": "Bus",
            "ancillary": "Correction Preparation",
            "magic": "Output",
            "magic_state_preparation_unit": "Magic State Preparation",
            "cstorage": "Correction Storage",
            "growth": "Code Growth",
            "storage": "Magic State Storage",
            "total": "Total",
        }

        all_keys = set()
        for _, counts in grouped:
            all_keys.update(counts.keys())
        ordered_keys = ["total"] + sorted(k for k in all_keys if k != "total")

        # Build the data rows
        rows = []
        for zone, counts in grouped:
            row = {"Zone": zone}
            for k in ordered_keys:
                # Rename 'data' to 'DU Data' in MSF zones
                if k == "data" and zone.startswith("MSF Level"):
                    display_name = "DU Data"
                else:
                    display_name = rename.get(k, k)
                row[display_name] = counts.get(k, None)
            rows.append(row)

        df = pd.DataFrame(rows)

        def fmt(val):
            if pd.isna(val):
                return ""
            elif isinstance(val, float):
                return f"{val:.0f}"
            return val

        styled = (
            df.style.format(fmt)
            .set_properties(subset=["Total"], **{"font-weight": "bold"})
            .hide(axis="index")
        )

        return f"""
        <details style="{COMMON_STYLES['details_style']}">
            <summary style="{COMMON_STYLES['summary_style']}">Logical Resources</summary>
            <div style="{COMMON_STYLES['div_style']}">
            <p style="{COMMON_STYLES['p_style_summary']}">
                Number of logical tiles used in different zones of the architecture.
            </p>
            {styled.to_html()}
            </div>
        </details>
        """

    def _render_physical_resources(self):
        physical = self.data.get("physical_resources_estimation", {})
        core = physical.get("core_processor_info", {})
        msf = physical.get("magic_state_factory_info", {})

        # Collect MSF levels dynamically
        msf_rows = []
        for i in range(len(msf.get("code_distance", []))):
            msf_rows.append(
                {
                    "Zone": f"MSF Level {i}",
                    "Code Distance": msf["code_distance"][i],
                    "Qubits/Logical Tile": msf["physical_qubits_per_logical_tile"][i],
                    "Physical Qubits Count": msf["num_physical_qubits"][i],
                }
            )

        # Core processor row
        core_row = {
            "Zone": "Core Processor",
            "Code Distance": core.get("code_distance", ""),
            "Qubits/Logical Tile": core.get("physical_qubits_per_logical_tile", ""),
            "Physical Qubits Count": core.get("total_number_physical_qubits", 0),
        }

        # Combine and compute percentages
        all_rows = msf_rows + [core_row]
        total_qubits = sum(row["Physical Qubits Count"] for row in all_rows)

        for row in all_rows:
            qubits = row["Physical Qubits Count"]
            row["% of Total"] = (
                f"{(qubits / total_qubits * 100):.2f}%" if total_qubits else "0%"
            )

        df = pd.DataFrame(all_rows)

        def fmt(val):
            if isinstance(val, int):
                return f"{val:,}"
            return val

        styled = df.style.format(fmt).hide(axis="index")

        return f"""
        <details style="{COMMON_STYLES['details_style']}">
            <summary style="{COMMON_STYLES['summary_style']}">Physical Resources</summary>
            <div style="{COMMON_STYLES['div_style']}">
            <p style="{COMMON_STYLES['p_style_summary']}">
                Physical qubit requirements for each zone.
            </p>
            {styled.to_html()}
            </div>
        </details>
        """

    def _render_magic_state_factory(self):
        msf = self.data.get("magic_state_factory", {})
        emu = self.data.get("device_emulation", {})

        # Distillation rate and slowdown factor
        slowdown = msf.get("slowdown_factor", None)
        rate = msf.get("distillation_rate", None)

        try:
            slowdown_str = f"{float(slowdown):.2f}×"
        except Exception:
            slowdown_str = "—"

        try:
            rate_val = float(rate.split()[0]) if isinstance(rate, str) else float(rate)
            rate_unit = " ".join(rate.split()[1:]) if isinstance(rate, str) else "µs"
            rate_str = f"{rate_val:.2f} {rate_unit}"
        except Exception:
            rate_str = "—"

        rate_info = f"""
            <p style="{COMMON_STYLES['p_style_title']}">
            <b>Distillation Rate:</b> {rate_str} / magic state ({slowdown_str} slower than the Core Processor's logical cycle time)
            </p>
        """

        # Per-level distillation info
        levels = msf.get("distillation_levels", 0)
        protocols = msf.get("distillation_protocol_per_level", [])
        units = msf.get("num_distillation_units", [])
        runtimes = msf.get("distillation_runtime", [])
        acceptances = msf.get("acceptance_probability", [])
        output_errors = msf.get("logical_magic_state_error_rate", [])

        def format_error(val):
            try:
                return f"{float(val):.2e}"
            except (ValueError, TypeError):
                return "—"

        per_level_rows = []
        for i in range(levels):
            runtime_str = "—"
            if i < len(runtimes):
                rt = runtimes[i]
                if isinstance(rt, dict):
                    runtime_str = f"{rt.get('value', '—')} {rt.get('unit', '')}"
                else:
                    runtime_str = str(rt)

            row = {
                "Level": i,
                "Protocol": protocols[i] if i < len(protocols) else "—",
                "Units": units[i] if i < len(units) else "—",
                "Cycle Runtime": runtime_str,
                "Acceptance Prob.": acceptances[i] if i < len(acceptances) else "—",
                "Output Error Rate": (
                    format_error(output_errors[i]) if i < len(output_errors) else "—"
                ),
            }
            per_level_rows.append(row)

        level_df = pd.DataFrame(per_level_rows)
        level_html = level_df.to_html(index=False, escape=False, border=0)

        # Fidelity evolution
        raw_preparation_error = (
            emu.get("magic_state_preparation", None)
            .get("logical_error_rate", {})
            .get("value", None)
        )
        required_error_rate = msf.get("required_logical_magic_state_error_rate", None)

        stages = ["Preparation"]
        for i in range(levels):
            stages.append(f"After Level {i}")
        stages.append("Required Target")

        rates = [raw_preparation_error] + output_errors + [required_error_rate]

        fidelity_df = pd.DataFrame(
            {
                "Stage": stages,
                "Error Rate": [format_error(v) for v in rates],
            }
        )
        fidelity_html = fidelity_df.to_html(index=False, escape=False, border=0)

        return f"""
        <details style="{COMMON_STYLES['details_style']}">
            <summary style="{COMMON_STYLES['summary_style']}">Magic State Factory</summary>
            <div style="{COMMON_STYLES['div_style']}">
            <p style="{COMMON_STYLES['p_style_summary']}">
            Overview of the Magic State Factory, including distillation rates, per-level details, and fidelity evolution across stages.
            </p>
            {rate_info}
            <h4 style="{COMMON_STYLES['title']}">Distillation Levels</h4>
            <div style="{COMMON_STYLES['section_indent']}">
            {level_html}
            </div>
            <h4 style="{COMMON_STYLES['title']}">Fidelity Evolution</h4>
            <div style="{COMMON_STYLES['section_indent']}">
            {fidelity_html}
            </div>
            </div>
        </details>
        """

    def _render_noise_profiling(self):
        data = self.data.get("device_emulation", {})

        # Dynamically extract zones and assign labels
        zone_keys = data.get("logical_cycle_time", {}).get("zones", {}).keys()
        zones = list(zone_keys)

        def format_zone_label(zone):
            if "magic_state_factory_level_" in zone:
                level = zone.split("_")[-1]
                return f"MSF Level {level}"
            return zone.replace("_", " ").title()

        zone_labels = {zone: format_zone_label(zone) for zone in zones}

        # Summary description
        summary_html = f"""
        <p style="{COMMON_STYLES['p_style_summary']}">
            Expected error correction code metrics and FTQC operations noises across different zones in the architecture.
        </p>
        """

        # QECC Metrics
        lct_form = data.get("logical_cycle_time", {}).get("functional_form", "N/A")

        lct_rows = []
        for zone in zones:
            cycle = data.get("logical_cycle_time", {}).get("zones", {}).get(zone, {})
            lct_rows.append(
                {
                    "Zone": zone_labels.get(zone, zone),
                    "Logical Cycle Time": f"{cycle or '—'}",
                }
            )
        lct_df = pd.DataFrame(lct_rows)
        lct_table = lct_df.to_html(index=False, border=0)

        # Memory
        memory = data.get("memory", {})
        mem_err_form = memory.get("logical_error_rate", {}).get(
            "functional_form", "N/A"
        )
        mem_reaction_form = memory.get("reaction_time", {}).get(
            "functional_form", "N/A"
        )

        memory_rows = []
        for zone in zones:
            err = memory.get("logical_error_rate", {}).get("zones", {}).get(zone)
            reaction = memory.get("reaction_time", {}).get("zones", {}).get(zone, {})
            memory_rows.append(
                {
                    "Zone": zone_labels.get(zone, zone),
                    "Logical Error Rate": (
                        f"{err:.2e}" if isinstance(err, (float, int)) else "—"
                    ),
                    "Reaction Time": f"{reaction or '—'}",
                }
            )
        memory_df = pd.DataFrame(memory_rows)
        memory_table = memory_df.to_html(index=False, border=0)

        # Magic State Preparation
        msp = data.get("magic_state_preparation", {})
        msp_err = msp.get("logical_error_rate", {})
        msp_discard = msp.get("discard_rate", {})
        msp_err_val = msp_err.get("value")
        msp_discard_val = msp_discard.get("value")

        msp_rows = [
            {
                "Target Code Distance": msp.get("target_code_distance", "—"),
                "Logical Error Rate": (
                    f"{msp_err_val:.2e}"
                    if isinstance(msp_err_val, (int, float))
                    else "—"
                ),
                "Discard Rate": (
                    f"{msp_discard_val:.2%}"
                    if isinstance(msp_discard_val, (int, float))
                    else "—"
                ),
            }
        ]
        msp_df = pd.DataFrame(msp_rows)
        msp_table = msp_df.to_html(index=False, border=0)
        msp_err_form = msp_err.get("functional_form", "N/A")
        msp_discard_form = msp_discard.get("functional_form", "N/A")

        # Lattice Surgery
        ls = data.get("lattice_surgery", {})
        ls_err_form = ls.get("logical_error_rate", {}).get("functional_form", "N/A")
        ls_reaction_form = ls.get("reaction_time", {}).get("functional_form", "N/A")

        return f"""
        <details style="{COMMON_STYLES["details_style"]}">
            <summary style="{COMMON_STYLES["summary_style"]}">Noise Profiling</summary>
            <div style="{COMMON_STYLES["div_style"]}">
                {summary_html}

                <h4>QECC Metrics</h4>
                <div style="{COMMON_STYLES['section_indent']}">
                    <p style="{COMMON_STYLES['p_style_title']}">
                        <b>Logical Cycle Time (in seconds):</b> {lct_form}
                    </p>
                    {lct_table}
                </div>

                <h4>Memory</h4>
                <div style="{COMMON_STYLES['section_indent']}">
                    <p style="{COMMON_STYLES['p_style_title']}">
                        <b>Logical Error Rate:</b> {mem_err_form}<br>
                        <b>Reaction Time (in seconds):</b> {mem_reaction_form}
                    </p>
                    {memory_table}
                </div>

                <h4>Magic State Preparation</h4>
                <div style="{COMMON_STYLES['section_indent']}">
                    <p style="{COMMON_STYLES['p_style_title']}">
                        <b>Logical Error Rate:</b> {msp_err_form}<br>
                        <b>Discard Rate:</b> {msp_discard_form}
                    </p>
                    {msp_table}
                </div>

                <h4>Lattice Surgery</h4>
                <div style="{COMMON_STYLES['section_indent']}">
                    <p style="{COMMON_STYLES['p_style_title']}">
                        <b>Logical Error Rate:</b> {ls_err_form}<br>
                        <b>Reaction Time (in seconds):</b> {ls_reaction_form}
                    </p>
                </div>
            </div>
        </details>
        """

    def _render_compiling(self):
        # Extract data
        compilation = self.data.get("compilation_data", {})
        circuit = compilation.get("circuit", {})

        circuit_name = circuit.get("name", "N/A")
        instruction_set = circuit.get("instruction_set", "—").replace("_", " ").title()
        qubit_count = circuit.get("computational_qubit_count", "—")
        synthesis_error = circuit.get("synthesis_accumulated_error", None)
        gate_counts = circuit.get("gate_count", {})

        def format_value(val):
            if isinstance(val, (int, float)):
                return f"{val:.2e}" if abs(val) >= 1e5 else f"{val}"
            return "—"

        num_pi4 = format_value(gate_counts.get("pi4"))
        num_pi8 = format_value(gate_counts.get("pi8"))
        num_meas = format_value(gate_counts.get("measure"))
        qubit_count_str = format_value(qubit_count)
        synthesis_error_str = format_value(synthesis_error)

        # Intro summary
        summary_intro_html = f"""
        <p style="{COMMON_STYLES['p_style_summary']}">
            Summarize the compiled quantum circuit and outlines assumptions made about the compilation process.
        </p>
        """

        # Summary
        summary_html = f"""
        <h4>Compiled Circuit Summary</h4>
        <table style="{COMMON_STYLES['table_style']}" border="0">
            <tr><td><b>Circuit Name:</b></td><td>{circuit_name}</td></tr>
            <tr><td><b>Instruction Set:</b></td><td>{instruction_set}</td></tr>
            <tr><td><b>Computational Qubits:</b></td><td>{qubit_count_str}</td></tr>
            <tr><td><b>π/4 Rotations:</b></td><td>{num_pi4}</td></tr>
            <tr><td><b>π/8 Rotations:</b></td><td>{num_pi8}</td></tr>
            <tr><td><b>Measurements:</b></td><td>{num_meas}</td></tr>
            <tr><td><b>Synthesis Accumulated Error:</b></td><td>{synthesis_error_str}</td></tr>
        </table>
        """

        # Assumptions
        assumptions_html = f"""
        <h4>Assumptions</h4>
        <ul style="{COMMON_STYLES["ul_style"]}">
            <li>Fully transpiled circuit, i.e., only π/8 rotations are scheduled and π/4 rotations are assumed to be commuted out.</li>
            <li>Lattice surgeries for π/8 rotations in the memory zone are assumed to involve measurements on all computational qubits and use the entire quantum bus.</li>
            <li>π/8 rotations are scheduled in serial.</li>
        </ul>
        """

        return f"""
        <details style="{COMMON_STYLES["details_style"]}">
            <summary style="{COMMON_STYLES["summary_style"]}">Compiling</summary>
            <div style="{COMMON_STYLES["div_style"]}">
                {summary_intro_html}
                {summary_html}
                {assumptions_html}
            </div>
        </details>
        """
