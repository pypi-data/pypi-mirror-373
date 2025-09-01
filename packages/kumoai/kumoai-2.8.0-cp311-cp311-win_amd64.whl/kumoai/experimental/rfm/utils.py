import re
import warnings
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
import pyarrow as pa
from kumoapi.typing import Dtype, Stype

from kumoai.experimental.rfm.infer import (
    contains_categorical,
    contains_id,
    contains_multicategorical,
    contains_timestamp,
)

# Mapping from pandas/numpy dtypes to Kumo Dtypes
PANDAS_TO_DTYPE: Dict[Any, Dtype] = {
    np.dtype('bool'): Dtype.bool,
    pd.BooleanDtype(): Dtype.bool,
    pa.bool_(): Dtype.bool,
    np.dtype('byte'): Dtype.int,
    pd.UInt8Dtype(): Dtype.int,
    np.dtype('int16'): Dtype.int,
    pd.Int16Dtype(): Dtype.int,
    np.dtype('int32'): Dtype.int,
    pd.Int32Dtype(): Dtype.int,
    np.dtype('int64'): Dtype.int,
    pd.Int64Dtype(): Dtype.int,
    np.dtype('float32'): Dtype.float,
    pd.Float32Dtype(): Dtype.float,
    np.dtype('float64'): Dtype.float,
    pd.Float64Dtype(): Dtype.float,
    np.dtype('object'): Dtype.string,
    pd.StringDtype(storage='python'): Dtype.string,
    pd.StringDtype(storage='pyarrow'): Dtype.string,
    pa.string(): Dtype.string,
    pa.binary(): Dtype.binary,
    np.dtype('datetime64[ns]'): Dtype.date,
    np.dtype('timedelta64[ns]'): Dtype.timedelta,
    pa.list_(pa.float32()): Dtype.floatlist,
    pa.list_(pa.int64()): Dtype.intlist,
    pa.list_(pa.string()): Dtype.stringlist,
}


def to_dtype(ser: pd.Series) -> Dtype:
    """Extracts the :class:`Dtype` from a :class:`pandas.Series`.

    Args:
        ser: A :class:`pandas.Series` to analyze.

    Returns:
        The data type.
    """
    if pd.api.types.is_datetime64_any_dtype(ser.dtype):
        return Dtype.date

    if isinstance(ser.dtype, pd.CategoricalDtype):
        return Dtype.string

    if pd.api.types.is_object_dtype(ser.dtype):
        index = ser.iloc[:1000].first_valid_index()
        if index is not None and pd.api.types.is_list_like(ser[index]):
            pos = ser.index.get_loc(index)
            assert isinstance(pos, int)
            ser = ser.iloc[pos:pos + 1000].dropna()

            if not ser.map(pd.api.types.is_list_like).all():
                raise ValueError("Data contains a mix of list-like and "
                                 "non-list-like values")

            ser = ser[ser.map(lambda x: not isinstance(x, list) or len(x) > 0)]

            dtypes = ser.apply(lambda x: PANDAS_TO_DTYPE.get(
                np.array(x).dtype, Dtype.string)).unique().tolist()

            invalid_dtypes = set(dtypes) - {
                Dtype.string,
                Dtype.int,
                Dtype.float,
            }
            if len(invalid_dtypes) > 0:
                raise ValueError(f"Data contains unsupported list data types: "
                                 f"{list(invalid_dtypes)}")

            if Dtype.string in dtypes:
                return Dtype.stringlist

            if dtypes == [Dtype.int]:
                return Dtype.intlist

            return Dtype.floatlist

    if ser.dtype not in PANDAS_TO_DTYPE:
        raise ValueError(f"Unsupported data type '{ser.dtype}'")

    return PANDAS_TO_DTYPE[ser.dtype]


def infer_stype(ser: pd.Series, column_name: str, dtype: Dtype) -> Stype:
    r"""Infers the semantic type of a column.

    Args:
        ser: A :class:`pandas.Series` to analyze.
        column_name: The name of the column (used for pattern matching).
        dtype: The data type.

    Returns:
        The semantic type.
    """
    if contains_id(ser, column_name, dtype):
        return Stype.ID

    if contains_timestamp(ser, column_name, dtype):
        return Stype.timestamp

    if contains_multicategorical(ser, column_name, dtype):
        return Stype.multicategorical

    if contains_categorical(ser, column_name, dtype):
        return Stype.categorical

    return dtype.default_stype


def detect_primary_key(
    table_name: str,
    df: pd.DataFrame,
    candidates: list[str],
) -> Optional[str]:
    r"""Auto-detect potential primary key column.

    Args:
        table_name: The table name.
        df: The pandas DataFrame to analyze
        candidates: A list of potential candidates.

    Returns:
        The name of the detected primary key, or ``None`` if not found.
    """
    # A list of (potentially modified) table names that are eligible to match
    # with a primary key, i.e.:
    # - UserInfo -> User
    # - snakecase <-> camelcase
    # - camelcase <-> snakecase
    # - plural <-> singular (users -> user, eligibilities -> eligibility)
    # - verb -> noun (qualifying -> qualify)
    _table_names = {table_name}
    if table_name.lower().endswith('_info'):
        _table_names.add(table_name[:-5])
    elif table_name.lower().endswith('info'):
        _table_names.add(table_name[:-4])

    table_names = set()
    for _table_name in _table_names:
        table_names.add(_table_name.lower())
        snakecase = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', _table_name)
        snakecase = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', snakecase)
        table_names.add(snakecase.lower())
        camelcase = _table_name.replace('_', '')
        table_names.add(camelcase.lower())
        if _table_name.lower().endswith('s'):
            table_names.add(_table_name.lower()[:-1])
            table_names.add(snakecase.lower()[:-1])
            table_names.add(camelcase.lower()[:-1])
        else:
            table_names.add(_table_name.lower() + 's')
            table_names.add(snakecase.lower() + 's')
            table_names.add(camelcase.lower() + 's')
        if _table_name.lower().endswith('ies'):
            table_names.add(_table_name.lower()[:-3] + 'y')
            table_names.add(snakecase.lower()[:-3] + 'y')
            table_names.add(camelcase.lower()[:-3] + 'y')
        elif _table_name.lower().endswith('y'):
            table_names.add(_table_name.lower()[:-1] + 'ies')
            table_names.add(snakecase.lower()[:-1] + 'ies')
            table_names.add(camelcase.lower()[:-1] + 'ies')
        if _table_name.lower().endswith('ing'):
            table_names.add(_table_name.lower()[:-3])
            table_names.add(snakecase.lower()[:-3])
            table_names.add(camelcase.lower()[:-3])

    scores: list[tuple[str, int]] = []
    for col_name in candidates:
        col_name_lower = col_name.lower()

        score = 0

        if col_name_lower == 'id':
            score += 4

        for table_name_lower in table_names:

            if col_name_lower == table_name_lower:
                score += 4  # USER -> USER
                break

            for suffix in ['id', 'hash', 'key', 'code', 'uuid']:
                if not col_name_lower.endswith(suffix):
                    continue

                if col_name_lower == f'{table_name_lower}_{suffix}':
                    score += 5  # USER -> USER_ID
                    break

                if col_name_lower == f'{table_name_lower}{suffix}':
                    score += 5  # User -> UserId
                    break

                if col_name_lower.endswith(f'{table_name_lower}_{suffix}'):
                    score += 2

                if col_name_lower.endswith(f'{table_name_lower}{suffix}'):
                    score += 2

            # `rel-bench` hard-coding :(
            if table_name == 'studies' and col_name == 'nct_id':
                score += 1

        ser = df[col_name].iloc[:1_000_000]
        score += 3 * (ser.nunique() / len(ser))

        scores.append((col_name, score))

    scores = [x for x in scores if x[-1] >= 4]
    scores.sort(key=lambda x: x[-1], reverse=True)

    if len(scores) == 0:
        return None

    if len(scores) == 1:
        return scores[0][0]

    # In case of multiple candidates, only return one if its score is unique:
    if scores[0][1] != scores[1][1]:
        return scores[0][0]

    max_score = max(scores, key=lambda x: x[1])
    candidates = [col_name for col_name, score in scores if score == max_score]
    warnings.warn(f"Found multiple potential primary keys in table "
                  f"'{table_name}': {candidates}. Please specify the primary "
                  f"key for this table manually.")

    return None


def detect_time_column(
    df: pd.DataFrame,
    candidates: list[str],
) -> Optional[str]:
    r"""Auto-detect potential time column.

    Args:
        df: The pandas DataFrame to analyze
        candidates: A list of potential candidates.

    Returns:
        The name of the detected time column, or ``None`` if not found.
    """
    candidates = [  # Exclude all candidates with `*last*` in column names:
        col_name for col_name in candidates
        if not re.search(r'(^|_)last(_|$)', col_name, re.IGNORECASE)
    ]

    if len(candidates) == 0:
        return None

    if len(candidates) == 1:
        return candidates[0]

    # If there exists a dedicated `create*` column, use it as time column:
    create_candidates = [
        candidate for candidate in candidates
        if candidate.lower().startswith('create')
    ]
    if len(create_candidates) == 1:
        return create_candidates[0]
    if len(create_candidates) > 1:
        candidates = create_candidates

    # Find the most optimal time column. Usually, it is the one pointing to
    # the oldest timestamps:
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', message='Could not infer format')
        min_timestamp_dict = {
            key: pd.to_datetime(df[key].iloc[:10_000], 'coerce')
            for key in candidates
        }
    min_timestamp_dict = {
        key: value.min().tz_localize(None)
        for key, value in min_timestamp_dict.items()
    }
    min_timestamp_dict = {
        key: value
        for key, value in min_timestamp_dict.items() if not pd.isna(value)
    }

    if len(min_timestamp_dict) == 0:
        return None

    return min(min_timestamp_dict, key=min_timestamp_dict.get)  # type: ignore


PUNCTUATION = re.compile(r"[\'\"\.,\(\)\!\?\;\:]")
MULTISPACE = re.compile(r"\s+")


def normalize_text(
    ser: pd.Series,
    max_words: Optional[int] = 50,
) -> pd.Series:
    r"""Normalizes text into a list of lower-case words.

    Args:
        ser: The :class:`pandas.Series` to normalize.
        max_words: The maximum number of words to return.
            This will auto-shrink any large text column to avoid blowing up
            context size.
    """
    if len(ser) == 0 or pd.api.types.is_list_like(ser.iloc[0]):
        return ser

    def normalize_fn(line: str) -> list[str]:
        line = PUNCTUATION.sub(" ", line)
        line = re.sub(r"<br\s*/?>", " ", line)  # Handle <br /> or <br>
        line = MULTISPACE.sub(" ", line)
        words = line.split()
        if max_words is not None:
            words = words[:max_words]
        return words

    ser = ser.fillna('').astype(str)

    if max_words is not None:
        # We estimate the number of words as 5 characters + 1 space in an
        # English text on average. We need this pre-filter here, as word
        # splitting on a giant text can be very expensive:
        ser = ser.str[:6 * max_words]

    ser = ser.str.lower()
    ser = ser.map(normalize_fn)

    return ser
