from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import pandas as pd
from kumoapi.source_table import UnavailableSourceTable
from kumoapi.table import Column as ColumnDefinition
from kumoapi.table import TableDefinition
from kumoapi.typing import Dtype, Stype
from typing_extensions import Self

from kumoai import in_notebook
from kumoai.experimental.rfm import utils


@dataclass(init=False, repr=False, eq=False)
class Column:
    stype: Stype

    def __init__(
        self,
        name: str,
        dtype: Dtype,
        stype: Stype,
        is_primary_key: bool = False,
        is_time_column: bool = False,
    ) -> None:
        self._name = name
        self._dtype = Dtype(dtype)
        self._is_primary_key = is_primary_key
        self._is_time_column = is_time_column
        self.stype = Stype(stype)

    @property
    def name(self) -> str:
        return self._name

    @property
    def dtype(self) -> Dtype:
        return self._dtype

    def __setattr__(self, key: str, val: Any) -> None:
        if key == 'stype':
            if isinstance(val, str):
                val = Stype(val)
            assert isinstance(val, Stype)
            if not val.supports_dtype(self.dtype):
                raise ValueError(f"Column '{self.name}' received an "
                                 f"incompatible semantic type (got "
                                 f"dtype='{self.dtype}' and stype='{val}')")
            if self._is_primary_key and val != Stype.ID:
                raise ValueError(f"Primary key '{self.name}' must have 'ID' "
                                 f"semantic type (got '{val}')")
            if self.name == self._is_time_column and val != Stype.timestamp:
                raise ValueError(f"Time column '{self.name}' must have "
                                 f"'timestamp' semantic type (got '{val}')")

        super().__setattr__(key, val)

    def __hash__(self) -> int:
        return hash((self.name, self.stype, self.dtype))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Column):
            return False
        return hash(self) == hash(other)

    def __repr__(self) -> str:
        return (f'{self.__class__.__name__}(name={self.name}, '
                f'stype={self.stype}, dtype={self.dtype})')


class LocalTable:
    r"""A table backed by a :class:`pandas.DataFrame`.

    A :class:`LocalTable` fully specifies the relevant metadata, *i.e.*
    selected columns, column semantic types, primary keys and time columns.
    :class:`LocalTable` is used to create a :class:`LocalGraph`.

    .. code-block:: python

        import pandas as pd
        import kumoai.experimental.rfm as rfm

        # Load data from a CSV file:
        df = pd.read_csv("data.csv")

        # Create a table from a `pandas.DataFrame` and infer its metadata ...
        table = rfm.LocalTable(df, name="my_table").infer_metadata()

        # ... or create a table explicitly:
        table = rfm.LocalTable(
            df=df,
            name="my_table",
            primary_key="id",
            time_column="time",
        )

        # Verify metadata:
        table.print_metadata()

        # Change the semantic type of a column:
        table[column].stype = "text"

    Args:
        df: The data frame to create the table from.
        name: The name of the table.
        primary_key: The name of the primary key of this table, if it exists.
        time_column: The name of the time column of this table, if it exists.
    """
    def __init__(
        self,
        df: pd.DataFrame,
        name: str,
        primary_key: Optional[str] = None,
        time_column: Optional[str] = None,
    ) -> None:

        if df.empty:
            raise ValueError("Data frame must have at least one row")
        if isinstance(df.columns, pd.MultiIndex):
            raise ValueError("Data frame must not have a multi-index")
        if not df.columns.is_unique:
            raise ValueError("Data frame must have unique column names")
        if any(col == '' for col in df.columns):
            raise ValueError("Data frame must have non-empty column names")

        df = df.copy(deep=False)

        self._data = df
        self._name = name
        self._primary_key: Optional[str] = None
        self._time_column: Optional[str] = None

        self._columns: Dict[str, Column] = {}
        for column_name in df.columns:
            self.add_column(column_name)

        if primary_key is not None:
            self.primary_key = primary_key

        if time_column is not None:
            self.time_column = time_column

    @property
    def name(self) -> str:
        r"""The name of the table."""
        return self._name

    # Data column #############################################################

    def has_column(self, name: str) -> bool:
        r"""Returns ``True`` if this table holds a column with name ``name``;
        ``False`` otherwise.
        """
        return name in self._columns

    def column(self, name: str) -> Column:
        r"""Returns the data column named with name ``name`` in this table.

        Args:
            name: The name of the column.

        Raises:
            KeyError: If ``name`` is not present in this table.
        """
        if not self.has_column(name):
            raise KeyError(f"Column '{name}' not found in table '{self.name}'")
        return self._columns[name]

    @property
    def columns(self) -> List[Column]:
        r"""Returns a list of :class:`Column` objects that represent the
        columns in this table.
        """
        return list(self._columns.values())

    def add_column(self, name: str) -> Column:
        r"""Adds a column to this table.

        Args:
            name: The name of the column.

        Raises:
            KeyError: If ``name`` is already present in this table.
        """
        if name in self:
            raise KeyError(f"Column '{name}' already exists in table "
                           f"'{self.name}'")

        if name not in self._data.columns:
            raise KeyError(f"Column '{name}' does not exist in the underyling "
                           f"data frame")

        try:
            dtype = utils.to_dtype(self._data[name])
        except Exception as e:
            raise RuntimeError(f"Data type inference for column '{name}' in "
                               f"table '{self.name}' failed. Consider "
                               f"changing the data type of the column or "
                               f"removing it from the table.") from e
        try:
            stype = utils.infer_stype(self._data[name], name, dtype)
        except Exception as e:
            raise RuntimeError(f"Semantic type inference for column '{name}' "
                               f"in table '{self.name}' failed. Consider "
                               f"changing the data type of the column or "
                               f"removing it from the table.") from e

        self._columns[name] = Column(
            name=name,
            dtype=dtype,
            stype=stype,
        )

        return self._columns[name]

    def remove_column(self, name: str) -> Self:
        r"""Removes a column from this table.

        Args:
            name: The name of the column.

        Raises:
            KeyError: If ``name`` is not present in this table.
        """
        if name not in self:
            raise KeyError(f"Column '{name}' not found in table '{self.name}'")

        if self._primary_key == name:
            self.primary_key = None
        if self._time_column == name:
            self.time_column = None
        del self._columns[name]

        return self

    # Primary key #############################################################

    def has_primary_key(self) -> bool:
        r"""Returns ``True``` if this table has a primary key; ``False``
        otherwise.
        """
        return self._primary_key is not None

    @property
    def primary_key(self) -> Optional[Column]:
        r"""The primary key column of this table.

        The getter returns the primary key column of this table, or ``None`` if
        no such primary key is present.

        The setter sets a column as a primary key on this table, and raises a
        :class:`ValueError` if the primary key has a non-ID semantic type or
        if the column name does not match a column in the data frame.
        """
        if not self.has_primary_key():
            return None
        assert self._primary_key is not None
        return self[self._primary_key]

    @primary_key.setter
    def primary_key(self, name: Optional[str]) -> None:
        if name is not None and name == self._time_column:
            raise ValueError(f"Cannot specify column '{name}' as a primary "
                             f"key since it is already defined to be a time "
                             f"column")

        if self.primary_key is not None:
            self.primary_key._is_primary_key = False

        if name is None:
            self._primary_key = None
            return

        self[name].stype = Stype.ID
        self[name]._is_primary_key = True
        self._primary_key = name

    # Time column #############################################################

    def has_time_column(self) -> bool:
        r"""Returns ``True`` if this table has a time column; ``False``
        otherwise.
        """
        return self._time_column is not None

    @property
    def time_column(self) -> Optional[Column]:
        r"""The time column of this table.

        The getter returns the time column of this table, or ``None`` if no
        such time column is present.

        The setter sets a column as a time column on this table, and raises a
        :class:`ValueError` if the time column has a non-timestamp semantic
        type or if the column name does not match a column in the data frame.
        """
        if not self.has_time_column():
            return None
        assert self._time_column is not None
        return self[self._time_column]

    @time_column.setter
    def time_column(self, name: Optional[str]) -> None:
        if name is not None and name == self._primary_key:
            raise ValueError(f"Cannot specify column '{name}' as a time "
                             f"column since it is already defined to be a "
                             f"primary key")

        if self.time_column is not None:
            self.time_column._is_time_column = False

        if name is None:
            self._time_column = None
            return

        self[name].stype = Stype.timestamp
        self[name]._is_time_column = True
        self._time_column = name

    # Metadata ################################################################

    @property
    def metadata(self) -> pd.DataFrame:
        r"""Returns a :class:`pandas.DataFrame` object containing metadata
        information about the columns in this table.

        The returned dataframe has columns ``name``, ``dtype``, ``stype``,
        ``is_primary_key``, and ``is_time_column``, which provide an aggregate
        view of the properties of the columns of this table.

        Example:
            >>> import kumoai.experimental.rfm as rfm
            >>> table = rfm.LocalTable(df=..., name=...).infer_metadata()
            >>> table.metadata
                name        dtype       stype    is_primary_key is_time_column
            0   CustomerID  float64     ID       True            False
        """
        cols = self.columns

        return pd.DataFrame({
            'name':
            pd.Series(dtype=str, data=[c.name for c in cols]),
            'dtype':
            pd.Series(dtype=str, data=[c.dtype for c in cols]),
            'stype':
            pd.Series(dtype=str, data=[c.stype for c in cols]),
            'is_primary_key':
            pd.Series(
                dtype=bool,
                data=[self._primary_key == c.name for c in cols],
            ),
            'is_time_column':
            pd.Series(
                dtype=bool,
                data=[self._time_column == c.name for c in cols],
            ),
        })

    def print_metadata(self) -> None:
        r"""Prints the :meth:`~LocalTable.metadata` of the table."""
        if in_notebook():
            from IPython.display import Markdown, display
            display(
                Markdown(f"### 🏷️ Metadata of Table `{self.name}` "
                         f"({len(self._data):,} rows)"))
            df = self.metadata
            try:
                if hasattr(df.style, 'hide'):
                    display(df.style.hide(axis='index'))  # pandas=2
                else:
                    display(df.style.hide_index())  # pandas<1.3
            except ImportError:
                print(df.to_string(index=False))  # missing jinja2
        else:
            print(f"🏷️ Metadata of Table '{self.name}' "
                  f"({len(self._data):,} rows):")
            print(self.metadata.to_string(index=False))

    def infer_metadata(self, verbose: bool = True) -> Self:
        r"""Infers metadata, *i.e.*, primary keys and time columns, in the
        table.

        Args:
            verbose: Whether to print verbose output.
        """
        logs = []

        # Try to detect primary key if not set:
        if not self.has_primary_key():

            def is_candidate(column: Column) -> bool:
                if column.stype == Stype.ID:
                    return True
                if all(column.stype != Stype.ID for column in self.columns):
                    if self.name == column.name:
                        return True
                    if (self.name.endswith('s')
                            and self.name[:-1] == column.name):
                        return True
                return False

            candidates = [
                column.name for column in self.columns if is_candidate(column)
            ]

            if primary_key := utils.detect_primary_key(
                    table_name=self.name,
                    df=self._data,
                    candidates=candidates,
            ):
                self.primary_key = primary_key
                logs.append(f"primary key '{primary_key}'")

        # Try to detect time column if not set:
        if not self.has_time_column():
            candidates = [
                column.name for column in self.columns
                if column.stype == Stype.timestamp
            ]
            if time_column := utils.detect_time_column(self._data, candidates):
                self.time_column = time_column
                logs.append(f"time column '{time_column}'")

        if verbose and len(logs) > 0:
            print(f"Detected {' and '.join(logs)} in table '{self.name}'")

        return self

    # Helpers #################################################################

    def _to_api_table_definition(self) -> TableDefinition:
        cols: List[ColumnDefinition] = []
        for col in self.columns:
            cols.append(ColumnDefinition(col.name, col.stype, col.dtype))
        pkey = self._primary_key
        time_col = self._time_column
        source_table = UnavailableSourceTable(table=self.name)

        return TableDefinition(
            cols=cols,
            source_table=source_table,
            pkey=pkey,
            time_col=time_col,
        )

    # Python builtins #########################################################

    def __hash__(self) -> int:
        return hash(tuple(self.columns + [self.primary_key, self.time_column]))

    def __contains__(self, name: str) -> bool:
        return self.has_column(name)

    def __getitem__(self, name: str) -> Column:
        return self.column(name)

    def __delitem__(self, name: str) -> None:
        self.remove_column(name)

    def __repr__(self) -> str:
        return (f'{self.__class__.__name__}(\n'
                f'  name={self.name},\n'
                f'  num_columns={len(self.columns)},\n'
                f'  primary_key={self._primary_key},\n'
                f'  time_column={self._time_column},\n'
                f')')
