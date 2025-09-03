import csv
import numpy as np
import os
import pandas as pd
import pyarrow
import pyarrow as pa
import pyarrow.parquet as pq
from typing import List
from datetime import datetime
from collections import defaultdict
from .schemas import *
from .config import *
from .utils import (
    read_config,
    get_report_outcome,
    update_report_with_uniqueness_check_result,
    update_report_with_invalid_row_removal_result,
    get_annotated_dataset_parts,
)
from .logger import logger



HAS_ERROR_COL = "__has_error"

ROW_NUM_COLUMN = "__row_nr"

CURRENT_FILE_PATH = os.path.abspath(__file__)

PYARROW_TYPE_BY_FORMAT_TYPE = {
    "STRING": pa.string(),
    "INTEGER": pa.int32(),
    "FLOAT": pa.float32(),
    "EMAIL": pa.string(),
    "DATE_ISO_8601": pa.string(),
    "PHONE_NUMBER_E164": pa.string(),
    "HASH_SHA_256_HEX": pa.string(),
}


def create_pandas_schema(config: ValidationConfig, use_pyarrow_string_type=True):
    """Create pandas schemas to be used for dataframes read from the output
    of the validation pipeline.

    All types should be read as pyarrow's string type, on which we base the duplication
    check. Later they can be safely transformed into the pyarrow type corresponding to
    the validation type. At this stage the previous validation should have made sure that
    the values in the CSV correspond to a format that matches the format type.

    In the special case when we write an empty DF, we should write it using the normal string type
    as somehow otherwise pandas cannot read the resulting DF.
    """
    if use_pyarrow_string_type:
        dtypes = defaultdict(lambda: pd.ArrowDtype(pa.string()))
    else:
        dtypes = defaultdict(lambda: str)
    dtypes[ROW_NUM_COLUMN] = np.uint64
    dtypes[HAS_ERROR_COL] = bool
    columns = [ROW_NUM_COLUMN, HAS_ERROR_COL] + [
        str(x) for x in range(len(config.root.config.columns))
    ]
    return columns, dtypes


def find_duplicates_pandas(csv: pd.DataFrame, unique_keys: List[List[int]]):
    """Try to find duplicates in the given CSV file and report the line
    numbers of where such duplicates where found.
    """
    errors = []
    num_duplicates_total = 0
    for subset_columns in unique_keys:
        logger.info(f"Check duplicates w/ subset cols: {subset_columns}")
        subset_columns = [str(x) for x in subset_columns]
        is_duplicated = csv.duplicated(
            subset=subset_columns,
            # Only report subsequent rows as duplicates.
            keep="first",
        )
        csv[HAS_ERROR_COL] = csv[HAS_ERROR_COL] | is_duplicated
        num_duplicates_total += sum(is_duplicated)
        duplicated_rows_subset = list(
            csv.loc[is_duplicated].index[:NUM_ERRORS_RECORD_BY_KEY_TUPLE]
        )
        for row in duplicated_rows_subset:
            errors.append(
                {
                    "code": "DUPLICATE_VALUES",
                    "location": {
                        "row": row,
                        "columns": [int(x) for x in subset_columns],
                    },
                }
            )
    return num_duplicates_total, errors


def create_empty_df(config: ValidationConfig) -> pd.DataFrame:
    columns, dtype = create_pandas_schema(config, use_pyarrow_string_type=False)
    dtypes = {col: dtype[col] for col in columns}
    df = pd.DataFrame({col: pd.Series([], dtype=dtypes[col]) for col in columns})
    # This will remove the column from the list of normal columns so that the
    # dataframe has the same structure like a non-empty one.
    df.set_index(ROW_NUM_COLUMN, inplace=True)
    return df


def create_pyarrow_schema_from_validation_config(
    config: ValidationConfig,
) -> pyarrow.Schema:
    col_ix = 0
    col_fields = []
    for column in config.root.config.columns:
        col_name = column.name
        allow_null = column.allowNull
        if not col_name:
            col_name = f"c{col_ix}"
        if column.formatType:
            format_type = column.formatType.value
            tpe = PYARROW_TYPE_BY_FORMAT_TYPE.get(format_type, pa.string())
        else:
            tpe = pa.string()
        col_fields.append(pa.field(col_name, tpe, nullable=allow_null))
        col_ix += 1
    schema = pa.schema(col_fields)
    return schema


def read_csv(path: str, config: ValidationConfig) -> Optional[pd.DataFrame]:
    try:
        columns, dtype = create_pandas_schema(config)
        def read(path, engine):
            logger.info(f"Trying to read file at '{path}' with engine '{engine}'")
            df = pd.read_csv(
                path,
                skip_blank_lines=True,  # this behavior must match Rust and Spark
                header=None,
                names=columns,
                dtype=dtype,
                # Only read a subset if columns if there are more.
                # The rows will already be marked with "true" in the error column
                # through the rust validation.
                usecols=columns,
                # In earlier versions this was required in order to read lines that
                # had more columns that specified. Now "usecols" must be used.
                # Leaving this here in case there are other cases where we should skip.
                # If dropInvalidRows is set, these lines would anyway be dropped,
                # they won't, however, appear in the count of dropped rows!
                on_bad_lines="skip",
                engine=engine,
            )
            # Set the index to the uint64-based row number column
            # that was added by the Rust pipeline.
            # This will drop the `ROW_NUM_COLUMN` column from the dataframe.
            # Note that if we used `index_col=0` when reading the CSV, it would
            # read the index_column as a string instead of a uint64.
            df.set_index(ROW_NUM_COLUMN, inplace=True)
            return df
        try:
            df = read(path, "c")
        except pd.errors.ParserError:
            logger.warning(
                f"Encountered a parser error when reading the file '{path}'. Will try again with the more permissive python engine."
            )
            # Slower than "c" but otherwise it cannot handle the case where there are
            # fewer columns in the file than expected.
            df = read(path, "python")
        return df
    except pd.errors.EmptyDataError:
        logger.warning(f"File at '{path}' was empty, returning None.")
        return None


def read_csv_from_parts(path: str, config: ValidationConfig) -> pd.DataFrame:
    """Read the table from a directory containing CSV chunks"""
    valid_dataset_parts = get_annotated_dataset_parts(path)
    logger.info(f"Found {len(valid_dataset_parts)} valid dataset parts")
    dfs = [read_csv(p, config) for p in valid_dataset_parts]
    valid_dfs = [df for df in dfs if df is not None]
    if valid_dfs:
        df = pd.concat(valid_dfs)
        # Replace NA with empty string
        #
        # If pandas encounters an empty cell like ",," it will record the value as NA.
        # For strings we say that NA is the empty string, so we need to fill this in here,
        # as otherwise we might try to create a pyarrow table later that has a potentially
        # non-nullable string column and we try to fill in NAs.
        # Also, both Rust `csv` and Spark treat empty values the same as empty quoted strings.
        string_columns = [
            str(jx)
            for jx, col in enumerate(config.root.config.columns)
            if col.formatType == FormatType.STRING
        ]
        if string_columns:
            df[string_columns] = df[string_columns].fillna("")
    else:
        df = create_empty_df(config)
    return df


def run(
    annotated_dataset_path: str,
    config_path: str,
    report_path: str,
    output_path: str,
    should_write_parquet: bool,
    should_check_uniqueness: bool,
    drop_invalid_rows: bool = False,
):
    config = read_config(config_path)

    # Read the annotated output of the validation pipeline that indicates
    # for each row whether it was valid and the original row number.
    logger.info(f"Reading input file at {annotated_dataset_path}")
    before = datetime.now()
    df = read_csv_from_parts(annotated_dataset_path, config)
    if df.shape[0] == 0:
        logger.info(f"Dataframe as output by validation pipeline is empty")
    after = datetime.now()
    logger.info(f"Reading of file took {(after - before).total_seconds()} s")

    # Check for duplicated rows if necessary
    if should_check_uniqueness:
        assert config.root.config.table is not None
        assert config.root.config.table.uniqueness is not None
        before = datetime.now()
        unique_keys: list[list[int]] = [
            [ix for ix in tpl.columns]
            for tpl in config.root.config.table.uniqueness.uniqueKeys
        ]
        logger.info(f"Checking uniqueness for keys: {unique_keys}")
        num_duplication_errors_total, duplication_errors = find_duplicates_pandas(
            df, unique_keys
        )
        update_report_with_uniqueness_check_result(
            report_path, duplication_errors, num_duplication_errors_total
        )
        after = datetime.now()
        logger.info(f"Uniqueness check took {(after - before).total_seconds()} s")

    if drop_invalid_rows:
        before = datetime.now()
        logger.info("Dropping invalid rows")
        num_invalid_rows = sum(df[HAS_ERROR_COL])
        update_report_with_invalid_row_removal_result(report_path, num_invalid_rows)
        df.drop(df[df[HAS_ERROR_COL] == True].index, inplace=True)
        after = datetime.now()
        logger.info(f"Dropping invalid rows took {(after - before).total_seconds()} s")

    df.drop(columns=[HAS_ERROR_COL], inplace=True)

    is_passed = get_report_outcome(report_path) == ValidationOutcome.PASSED
    if is_passed:
        # Copy over the input data so that downstream computations can read it.
        before = datetime.now()
        if should_write_parquet:
            schema = create_pyarrow_schema_from_validation_config(config)
            df.columns = schema.names
            table = pa.Table.from_pandas(df, schema=schema)
            pq.write_table(table, output_path)
        else:
            df.to_csv(
                output_path,
                index=False,
                header=False,
                sep=",",
                na_rep="",
                quoting=csv.QUOTE_MINIMAL,
                lineterminator="\n",
                doublequote=True,
                encoding="utf-8",
                decimal=".",
            )
        after = datetime.now()
        fmt = "parquet" if should_write_parquet else "csv"
        logger.info(f"Writing out {fmt} file took {(after - before).total_seconds()} s")
