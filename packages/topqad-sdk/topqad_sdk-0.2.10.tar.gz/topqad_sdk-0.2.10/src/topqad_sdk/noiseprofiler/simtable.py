import inspect
from collections.abc import Callable
from typing import Any

import numpy as np
import sympy as sp
import tabulate
from pydantic import BaseModel


class FieldHeaderModel(BaseModel):
    name: str
    full_label: str
    kind: str | None = None
    math_symbol: str | None = None
    compute_formula: Callable | str | None = None
    floatfmt: str
    intfmt: str
    hidden: bool


class SimTableModel(BaseModel):
    FieldHeaders: list[FieldHeaderModel]
    data: list[dict[str, Any]]


class FieldHeader:

    def __init__(
        self,
        name: str,
        kind: str,
        *,
        full_label: str | None = None,
        math_symbol: str | None = None,
        compute_formula: Callable | str | None = None,
        floatfmt: str = ".2f",
        intfmt: str = ",",
        hidden: bool = False,
    ):
        """Create a field header.

        Args:
            name (str): The short name of the field used for referencing.
            kind (str): Describes the kind of the field. Recognized kinds are "protocol_parameter", "noise_model",
            "decoder", "stat", "computed", "internal".
            full_label (str | None, optional): The full name of the field, used for instance for plot labels. If `None`,
            then is set to `name`. Defaults to `None`.
            math_symbol (str | None, optional): The sympy symbol used for this field in formulas. Defaults to None.
            compute_formula (Callable | str | None): Formula used to compute the values in the column. Required if
            `kind="computed"`. Defaults to None. String formulas should be valid sympy formulas. For example, the
            logical error rate formula is `errors/shots` where "errors" and "shots" are the short names of other fields.
            floatfmt (str, optional): tabulate package floatfmt for rendering floating point numbers. Defaults to ".2f".
            intfmt (str, optional): tabulate package intfmt for rendering integers. Defaults to ",".
            hidden (bool, optional): If `True` then not shown in printed output. Defaults to False.
        """

        self.name = name
        self.kind = kind
        self.math_symbol = math_symbol
        if kind == "computed" and compute_formula is None:
            raise ValueError(
                f"Computed field {self.name} must have the compute_formula declared."
            )
        self.compute_formula = compute_formula
        self.floatfmt = floatfmt
        self.intfmt = intfmt
        self.hidden = hidden

        if full_label is None:
            self.full_label = name
        else:
            self.full_label = full_label

    def __repr__(self) -> str:
        args = [f"'{self.name}'"]

        if self.name != self.full_label:
            args.append(f"full_label='{self.full_label}'")

        if self.kind is not None:
            args.append(f"kind={self.kind}")

        return f"Field({', '.join(args)})"

    def __eq__(self, other):
        """Check if other is equal to self. Other can be Field, str or tuple.

        All the following should evaluate to True.
        """
        if type(other) is FieldHeader:
            return (
                other.name == self.name
                and other.full_label == self.full_label
                and other.kind == self.kind
                and other.math_symbol == self.math_symbol
                and other.compute_formula == self.compute_formula
                and other.floatfmt == self.floatfmt
                and other.intfmt == self.intfmt
                and other.hidden == self.hidden
            )

    def __hash__(self):
        return hash(self.__str__())

    def copy(self):
        return FieldHeader(
            name=self.name,
            full_label=self.full_label,
            kind=self.kind,
            math_symbol=self.math_symbol,
            compute_formula=self.compute_formula,
            floatfmt=self.floatfmt,
            intfmt=self.intfmt,
            hidden=self.hidden,
        )

    def to_model(self):
        return FieldHeaderModel(
            name=self.name,
            full_label=self.full_label,
            kind=self.kind,
            math_symbol=self.math_symbol,
            compute_formula=self.compute_formula,
            floatfmt=self.floatfmt,
            intfmt=self.intfmt,
            hidden=self.hidden,
        )

    def to_json(self):
        return self.to_model.model_dump_json()

    @classmethod
    def from_json(cls, json_data: str):
        return cls(**FieldHeaderModel.model_validate_json(json_data).model_dump())


class SimTable:
    """This class provides storage for simulation data.

    Data is stored in a flat 2D table. Each column is described by a FieldHeader.
    """

    def __init__(self, fields: list[FieldHeader] | list[str]):
        """Initialize a simtable with some columns."""

        if type(fields[0]) is str:
            fields = [FieldHeader(name) for name in fields]

        self.fields: dict[str, FieldHeader] = dict()
        self._stats_dict: dict[str, Any] = dict()

        for f in fields:
            if f.name in self.fields:
                raise KeyError("Repeated field name used.")
            self.fields[f.name] = f
            self._stats_dict[f.name] = []

        self.floatfmt = tuple(f.floatfmt for f in self.fields.values())
        self.intfmt = tuple(f.intfmt for f in self.fields.values())

    def __getitem__(self, index: str | tuple | int | slice) -> "SimTable":
        """Get some entries in the simtable.

        Generally integer indexes refer to rows while string index refers to columns. If multiple columns or rows are
        required then they should be wrapped in a list. If a subset of both rows and columns are required, then the row
        index/indices should be passed first followed by the column indices. The following examples illustrate how to
        access various entries of a simulation table.

        >>> magic = libprotocols.MagicStatePreparationRepCode()
        >>> magic.add_noise_model(libnoise.UniformDepolarizing(p=0.001))
        >>> for d in range(3, 13+1, 2):
        ...     magic.add_instance(distances=[3, d], rounds = [3, d], inject_state='X')
        >>> simulation_table = magic.simulation_table
        >>> st = simulation_table['inject_state'];
        >>> st = simulation_table[['inject_state']]
        >>> st = simulation_table[[('distances', 0)]]
        >>> st = simulation_table[['inject_state', ('distances', 0)]]
        >>> st = simulation_table[0]
        >>> st = simulation_table[[0, 1, 2]]
        >>> st = simulation_table[3:5]
        >>> st = simulation_table[0, ['shots']]
        >>> st = simulation_table[[1], ['shots']]
        >>> st = simulation_table[3:5, ['inject_state', 'rounds', ('distances', 0)]]

        Here the special syntax `simulation_table[[('distances', 0)]]` only works if every entry of
        `simulation_table["distances"]` is a list. Then the 0th entry of each such list is returned as a column.

        Args:
            index (str | tuple | int | slice): The index to get.

        Raises:
            KeyError: If index is str and column not in simtable.
            KeyError: If index is (str, int) or (str, slice) and target column doesn't exist.
            KeyError: If unrecognized index.

        Returns:
            SimTable: The sliced simtable.
        """
        # target a whole col: simulation_table['colname']
        if type(index) is str:
            if index not in self.fields:
                raise KeyError
            f = self.fields[index]
            col_data = self.__class__(fields=[f])
            col_data._stats_dict[f.name] = self._stats_dict[f.name]
            return col_data
        # target one or more columns: simulation_table[['basis', ('distances', 0)]]
        elif type(index) is list and all(type(x) in [str, tuple] for x in index):
            field_headers = []
            for ind in index:
                if type(ind) is str:
                    if ind not in self.fields:
                        raise KeyError
                    else:
                        field_headers.append(self.fields[ind])
                elif type(ind) is tuple:
                    if (
                        len(ind) != 2
                        or type(ind[0]) is not str
                        or type(ind[1]) not in (int, slice)
                    ):
                        raise KeyError
                    elif ind[0] not in self.fields:
                        raise KeyError
                    else:
                        f = self.fields[ind[0]].copy()
                        if type(ind[1]) is int:
                            f.name = ind[0] + f"[{ind[1]}]"
                        else:
                            start = ind[1].start if ind[1].start is not None else ""
                            stop = ind[1].stop if ind[1].stop is not None else ""
                            step = ind[1].step if ind[1].step is not None else ""

                            # Construct the slice string
                            if step and step != 1:
                                f.name = ind[0] + f"[{start}:{stop}:{step}]"
                            else:
                                f.name = ind[0] + f"[{start}:{stop}]"
                        field_headers.append(f)

            col_data = self.__class__(fields=field_headers)

            for f, ind in zip(field_headers, index):
                if type(ind) is str:
                    col_data._stats_dict[f.name] = self._stats_dict[f.name]
                else:
                    col_data._stats_dict[f.name] = [
                        row[ind[1]] for row in self._stats_dict[ind[0]]
                    ]

            return col_data

        # target a row or row slice: simulation_table[4] or simulation_table[5:7]
        elif type(index) in (int, slice):
            row_data = self.create_empty_copy()
            for field, val in self._stats_dict.items():
                row_data._stats_dict[field] = (
                    [val[index]] if type(index) is int else val[index]
                )
            return row_data
        # target rows by list of integers: simulation_table[[0, 1, 2]]
        elif type(index) is list and all(type(x) is int for x in index):
            row_data = self.create_empty_copy()
            for field, val in self._stats_dict.items():
                row_data._stats_dict[field] = [val[i] for i in index]
            return row_data
        # target rows by a list of a single slice: simulation_table[[3:5]]
        elif type(index) is list and len(index) == 1 and type(index[0]) is slice:
            row_data = self.create_empty_copy()
            for field, val in self._stats_dict.items():
                row_data._stats_dict[field] = val[index[0]]
            return row_data
        elif type(index) is tuple and len(index) == 2:
            col_data = self.__getitem__(index[1])
            table_data = col_data.__getitem__(index[0])
            return table_data
        else:
            raise KeyError

    def __iter__(self):
        """Iterate through the database rows.

        Yields a dictionary for each row.
        """
        for i in range(len(self)):
            yield {field: values[i] for field, values in self._stats_dict.items()}

    def __len__(self) -> int:
        """Number of rows in the simtable."""
        if len(self._stats_dict.values()) == 0:
            return 0
        else:
            return len(next(iter(self._stats_dict.values())))

    def __repr__(self) -> str:
        """A string representation of the simtable.

        This cannot be evaluated to recreated the simtable.
        """
        return self.__table_str(
            table_dict={
                v: self._stats_dict[k] for k, v in self.fields.items() if not v.hidden
            }
        )

    def __setitem__(
        self, index: tuple[int | list[int], str | list[str]], value: Any
    ) -> None:
        """Set the value of an entry in the simtable.

        Args:
            index (tuple[int | list[int], str | list[str]]): The index of the entry. Must specify one row and one column.
            value (Any): The value to set.

        Raises:
            KeyError: If the index is not recognized.
        """
        # Both row and column must be provided
        if type(index) is tuple and len(index) == 2:
            # the column name is provided directly
            if type(index[1]) is str:
                field_name = index[1]
            # the column name is wrapped in a list
            elif (
                type(index[1]) is list
                and len(index[1]) == 1
                and type(index[1][0]) is str
            ):
                field_name = index[1][0]
            else:
                raise KeyError("Can't recognize column index.")

            # the row index is provided directly
            if type(index[0]) is int:
                row_index = index[0]
            # the row index is wrapped in a list
            elif (
                type(index[0]) is list
                and len(index[0]) == 1
                and type(index[0][0]) is int
            ):
                row_index = index[0][0]
            else:
                KeyError("Can't recognize row index.")
        else:
            KeyError("You must specify both row and column indexes to set a value.")

        if field_name not in self._stats_dict:
            raise KeyError("Column does not exist.")
        if row_index >= len(self):
            raise KeyError("Row index is too large.")

        self._stats_dict[field_name][row_index] = value

    def __table_str(self, table_dict) -> str:
        """Convert the simtable into table stored in a string."""
        headers = []
        for f in table_dict.keys():
            if f.math_symbol is not None:
                headers.append(f"{f.name} ({f.math_symbol})")
            else:
                headers.append(f.name)
        tablestr = tabulate.tabulate(
            table_dict,
            headers=headers,
            tablefmt="simple",
            stralign="center",
            numalign="center",
            floatfmt=self.floatfmt,
            intfmt=self.intfmt,
        )

        return tablestr

    def add_col(self, col_field: FieldHeader | str, formula: Callable = lambda s: "?"):
        """Add col to the sim table

        Args:
            col_field (Field | str): The column field.
            formula (Callable, optional): The formula to use to compute the data in the column by operating on each row.
                Defaults to lambda s: "?".
        """

        f = col_field if type(col_field) is FieldHeader else FieldHeader(col_field)
        if f.name in self.fields:
            raise KeyError("Column header already exists.")

        self.fields[f.name] = f

        self._stats_dict[f.name] = [formula(row) for row in self]
        self.floatfmt += (f.floatfmt,)
        self.intfmt += (f.intfmt,)

    def add_row(self, **kwargs):
        """Add a row of data.

        If any columns are missing, a "?" is added instead.

        Raises:
            AttributeError: If data for unknown column is provided.
        """
        for field_name in kwargs.keys():
            if field_name not in self.fields:
                raise AttributeError(f"Unknown field name {field_name}.")

        for field_name in self.fields.keys():
            if field_name in kwargs:
                self._stats_dict[field_name].append(kwargs[field_name])
            else:
                self._stats_dict[field_name].append("?")

    def compute_computed_columns(self, row_ind: int | None = None) -> None:
        """Compute the value of all columns with computed kind in the table.

        Columns are computed in turn from left to rigth.

        Args:
            row_ind (int | None, optional): Only compute the specified row. Defaults to None.
        """
        symbol_to_column_dic = {
            sp.symbols(v.math_symbol): k
            for k, v in self.fields.items()
            if v.math_symbol is not None
        }

        if row_ind is None:
            for f in self.fields:
                if self.fields[f].kind == "computed":
                    if isinstance(self.fields[f].compute_formula, Callable):
                        self._stats_dict[f] = [
                            self.fields[f].compute_formula(row) for row in self
                        ]
                    else:
                        sp_formula = sp.sympify(
                            self.fields[f].compute_formula, evaluate=False
                        )
                        for i, row in enumerate(self):
                            value_dict = {
                                symb: row[symbol_to_column_dic[symb]]
                                for symb in sp_formula.free_symbols
                            }
                            if any(v in ["?", "F"] for v in value_dict.values()):
                                continue
                            self[i, f] = float(sp_formula.subs(value_dict).evalf())
        elif type(row_ind) is int:
            for f in self.fields:
                if self.fields[f].kind == "computed":
                    row = {k: v[0] for k, v in self[row_ind]._stats_dict.items()}
                    if isinstance(self.fields[f].compute_formula, Callable):
                        self._stats_dict[f][row_ind] = self.fields[f].compute_formula(
                            row
                        )
                    else:
                        sp_formula = sp.sympify(
                            self.fields[f].compute_formula, evaluate=False
                        )
                        value_dict = {
                            symb: row[symbol_to_column_dic[symb]]
                            for symb in sp_formula.free_symbols
                        }
                        if any(v in ["?", "F"] for v in value_dict.values()):
                            continue
                        self[row_ind, f] = float(sp_formula.subs(value_dict).evalf())

    def create_empty_copy(self) -> "SimTable":
        """
        Create a new empty SimTable with the same field headers as this table.

        Returns:
            SimTable: A new SimTable instance with identical field headers but no data rows.
        """
        # Create a list of the current field headers
        field_headers = list(self.fields.values())

        # Create a new SimTable with the same field headers
        new_table = SimTable(field_headers)

        return new_table

    @classmethod
    def create_from_function_parameters(cls, func: Callable):
        """Return a list of parameter names for a function, excluding *args and **kwargs parameters.

        Args:
            func (Callable): Function whose parameters to extract.
        """
        excluded_kinds = (
            inspect.Parameter.VAR_POSITIONAL,  # *args
            inspect.Parameter.VAR_KEYWORD,  # **kwargs
        )

        signature = inspect.signature(func)
        field_headers = [
            name
            for name, param in signature.parameters.items()
            if param.kind not in excluded_kinds
        ]

        return SimTable(field_headers)

    def data(self) -> list:
        """If database is a single column, return data as list.

        Raises:
            ValueError: If self has multiple columns.

        Returns:
            list: The list of values in the column.
        """
        if len(self.fields) == 1:
            return list(self._stats_dict.values())[0]
        else:
            raise ValueError("This method only works on tables with one column.")

    def filter(self, condition: Callable = lambda s: True) -> "SimTable":
        """Output a table filtered by the condition.

        Args:
            condition (Callable, optional): A lambda function that determines if row should be in output. Defaults to
            lambda s: True.

        Returns:
            SimTable: The filtered rows.
        """
        filtered_data = self.__class__(fields=list(self.fields.values()))

        for row in self:
            if condition(row):
                filtered_data.add_row(**{v: row[v] for v in self.fields})

        return filtered_data

    @classmethod
    def from_json(cls, json_str: str) -> "SimTable":
        """
        Create a SimTable instance from a json string.

        Args:
            json_str (str): json string

        Returns:
            SimTable: A new SimTable instance populated from the json.
        """
        # Parse the JSON using the SimTableModel
        table_model = SimTableModel.model_validate_json(json_str)

        # Convert field header models back to FieldHeader objects
        fields = []
        for header_model in table_model.FieldHeaders:
            # Create FieldHeader from each model
            field = FieldHeader(
                name=header_model.name,
                full_label=header_model.full_label,
                kind=header_model.kind,
                math_symbol=header_model.math_symbol,
                compute_formula=header_model.compute_formula,
                floatfmt=header_model.floatfmt,
                intfmt=header_model.intfmt,
                hidden=header_model.hidden,
            )
            fields.append(field)

        # Create a new SimTable with these fields
        sim_table = cls(fields)

        # Add each row of data to the table
        for row_data in table_model.data:
            sim_table.add_row(**row_data)

        return sim_table

    def get_field_names_of_kind(self, kind: str) -> list:
        """Get all field names of a particular kind.

        Args:
            kind (str): The kind to search for.

        Returns:
            list: List of field names that match the kind.
        """
        # protocol_parameter, noise_model, stat, computed, internal
        field_names = [k for k, v in self.fields.items() if v.kind == kind]

        return field_names

    def group(self, condition: Callable = lambda s: True):
        """Output a dictionary of simtables specified by the condition.

        Args:
            condition (Callable, optional): Condition to group by that is applied to each row.

        Returns:
            dict[SimTable]: The keys of the dictionary are the unique outputs of conditon.
        """
        groups: dict[SimTable] = dict()

        for row in self:
            group_key = condition(row)
            groups.setdefault(
                group_key, self.__class__(fields=list(self.fields.values()))
            )
            groups[group_key].add_row(**row)

        return groups

    def num_fields(self) -> int:
        """Count the number of fields in the table."""
        return len(self.fields)

    def print_full_table(self) -> None:
        """Print the entire table, including hidden columns."""
        print(
            self.__table_str(
                table_dict={v: self._stats_dict[k] for k, v in self.fields.items()}
            )
        )

    def sort_by(self, column: str, reverse: bool = False, key: Callable = None) -> None:
        """
        Sort the table by a particular column inplace.

        Args:
            column (str): The name of the column to sort by
            reverse (bool, optional): Whether to sort in descending order. Defaults to False.
            key (Callable, optional): A function that takes a value and returns a sort key.
                If None, values are compared directly. Defaults to None.

        Raises:
            ValueError: If the specified column doesn't exist in the table
        """
        # Check if the column exists
        if column not in self.fields:
            raise ValueError(
                f"Column '{column}' not found in table. Available columns: {list(self.fields.keys())}"
            )

        # Get the values from the specified column
        values = self._stats_dict[column]

        # Create a list of indices
        indices = list(range(len(self)))

        # Sort indices based on the values in the specified column
        if key is None:
            # Use direct comparison if no key function is provided
            sorted_indices = sorted(indices, key=lambda i: values[i], reverse=reverse)
        else:
            # Use the provided key function
            sorted_indices = sorted(
                indices, key=lambda i: key(values[i]), reverse=reverse
            )

        for field_name in self.fields.keys():
            values = self._stats_dict[field_name]
            self._stats_dict[field_name] = [values[i] for i in sorted_indices]

    def to_json(self) -> str:
        """
        Convert the SimTable to json.

        Returns:
            str: The json representation of the table.
        """
        table_model = self.to_model()

        return table_model.model_dump_json(indent=4)

    def to_model(self) -> SimTableModel:
        # Build the schema section
        FieldHeaders = [field.to_model() for field in self.fields.values()]

        # Build the data section
        table_data = []
        # Determine how many rows we have by checking the first field's data length
        for row in self:
            table_data.append(row)

        # Combine schema and data
        table_model = SimTableModel(FieldHeaders=FieldHeaders, data=table_data)

        return table_model
