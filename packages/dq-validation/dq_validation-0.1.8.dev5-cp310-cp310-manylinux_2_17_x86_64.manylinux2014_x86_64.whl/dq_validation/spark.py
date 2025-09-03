import json
import tempfile
import shutil
import functools

import os
from typing import List
from datetime import datetime
from . import validate

from .spark_utils import spark_session
import pyspark.sql.functions as F
from pyspark.sql import DataFrame, Window
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    FloatType,
    BooleanType,
    LongType,
)
from pyspark.storagelevel import StorageLevel
from .schemas import ValidationConfig
from .error import ValidationError
from .schemas import *
from .config import *
from .utils import (
    read_config,
    get_report_outcome,
    update_report_with_uniqueness_check_result,
    update_report_with_invalid_row_removal_result,
    get_annotated_dataset_parts
)
from .logger import logger


HAS_ERROR_COL = "__has_error"

ROW_NUM_COLUMN = "__row_nr"

CURRENT_FILE_PATH = os.path.abspath(__file__)

SPARK_TYPE_BY_FORMAT_TYPE = {
    "STRING": StringType(),
    "INTEGER": IntegerType(),
    "FLOAT": FloatType(),
    "EMAIL": StringType(),
    "DATE_ISO_8601": StringType(),
    "PHONE_NUMBER_E164": StringType(),
    "HASH_SHA_256_HEX": StringType(),
}


def write_df_as_single_file(df: DataFrame, path: str, temp_dir: str):
    """Write a dataframe into a single CSV file and store the result at `path`"""
    filename = os.path.basename(path)
    with tempfile.TemporaryDirectory(dir=temp_dir) as d:
        csv_parts_dir = os.path.join(d, filename)
        # Make sure to escape quotes within strings by repeating the quote character
        # (as it is done by Pandas and Excel).
        (
            df.write
              .option("header", "false")
              .option("quote", '"')
              .option("escape", '"')
              .csv(csv_parts_dir, header=None)
        )
        csv_parts = [
            os.path.join(csv_parts_dir, f)
            for f in os.listdir(csv_parts_dir)
            if f.endswith(".csv")
        ]
        logger.info(f"Will merge {len(csv_parts)} CSV part files")
        temp_merged_path = os.path.join(d, "__temp-merged.csv")
        with open(temp_merged_path, "wb") as temp_out:
            for ix, part in enumerate(csv_parts):
                with open(part, "rb") as f:
                    shutil.copyfileobj(f, temp_out)
                os.remove(part)  # delete the part file to free up space
                logger.debug(
                    f"Moved part file '{part}' into '{temp_merged_path}' ({ix + 1} / {len(csv_parts)})"
                )
        shutil.move(temp_merged_path, path)


def add_erroneous_row_ids(df: DataFrame, row_nrs_df: DataFrame) -> DataFrame:
    if HAS_ERROR_COL not in df.columns:
        raise ValidationError(f"Column '{HAS_ERROR_COL}' must exist in columns")
    has_error_col_new = f"{HAS_ERROR_COL}_new"
    df = (
        df.join(
            row_nrs_df.withColumn(has_error_col_new, F.lit(True)),
            on=ROW_NUM_COLUMN,
            how="left_outer",
        )
        .na.fill(False, subset=[has_error_col_new])
        .withColumn(HAS_ERROR_COL, F.col(HAS_ERROR_COL) | F.col(has_error_col_new))
        .drop(has_error_col_new)
    )
    return df


def create_spark_schema_from_validation_config(
    config: ValidationConfig, string_only: bool = False
) -> List[StructField]:
    col_ix = 0
    col_fields = []
    for column in config.root.config.columns:
        col_name = column.name
        allow_null = column.allowNull
        if not col_name:
            col_name = f"c{col_ix}"
        if column.formatType:
            format_type = column.formatType.value
            spark_type = (
                StringType()
                if string_only
                else SPARK_TYPE_BY_FORMAT_TYPE.get(format_type, StringType())
            )
        else:
            spark_type = StringType()
        col_fields.append(StructField(col_name, spark_type, allow_null))
        col_ix += 1
    return col_fields


def find_duplicates_spark(
    df: DataFrame, unique_keys: List[List[int]], row_nr_column: str, has_error_col: str
):
    """
    Try to find duplicates in the given DataFrame and report the
    line numbers of where such duplicates where found.
    """
    errors = []
    num_duplicates_total = 0
    before = datetime.now()

    duplicated_dfs = []
    for subset_columns_ix in unique_keys:
        df_columns = [
            column
            for column in df.columns
            if column != row_nr_column and column != has_error_col
        ]
        subset_columns = [df_columns[col_ix] for col_ix in subset_columns_ix]

        # Check for duplicates based on the subset of columns
        window_spec = Window.partitionBy(*subset_columns)
        min_row_nr_column = f"{ROW_NUM_COLUMN}_min"
        df_with_dup_flag = (
            df.withColumn(min_row_nr_column, F.min(ROW_NUM_COLUMN).over(window_spec))
            .withColumn(
                "is_duplicated", F.col(ROW_NUM_COLUMN) > F.col(min_row_nr_column)
            )
            .drop(min_row_nr_column)
        )

        # Filter duplicates
        duplicated_df = (
            df_with_dup_flag.filter("is_duplicated == true")
            .select(row_nr_column)
            .persist(StorageLevel.DISK_ONLY)
        )
        num_duplicates = duplicated_df.count()
        num_duplicates_total += num_duplicates

        # Collect the row numbers of duplicates (limited to NUM_ERRORS_RECORD_BY_KEY_TUPLE)
        duplicated_rows_subset = (
            duplicated_df.sort(row_nr_column)
            .limit(NUM_ERRORS_RECORD_BY_KEY_TUPLE)
            .collect()
        )

        duplicated_dfs.append(duplicated_df)

        for row in duplicated_rows_subset:
            errors.append(
                {
                    "code": "DUPLICATE_VALUES",
                    "location": {
                        "row": row[row_nr_column],
                        "columns": subset_columns_ix,
                    },
                }
            )

    after = datetime.now()
    logger.info(f"Finding duplicates took {(after - before).total_seconds() / 60} min")

    duplicated_df = functools.reduce(lambda a, b: a.union(b), duplicated_dfs).distinct()

    return duplicated_df, num_duplicates_total, errors


def run(
    annotated_dataset_path: str,
    config_path: str,
    report_path: str,
    output_path: str,
    should_write_parquet: bool,
    should_check_uniqueness: bool,
    temp_dir: str = "/scratch",
    drop_invalid_rows: bool = False,
):
    config = read_config(config_path)

    spark_settings = {}

    if bool(os.environ.get("VALIDATION_SPARK_NUM_PARTITIONS")):
        num_partitions = os.environ["VALIDATION_SPARK_NUM_PARTITIONS"]
        spark_settings["spark.sql.shuffle.partitions"] = num_partitions
        spark_settings["spark.default.parallelism"] = num_partitions
    for env, key in [
        ("VALIDATION_SPARK_DRIVER_MEMORY", "spark.driver.memory"),
        ("VALIDATION_SPARK_MEMORY_FRACTION", "spark.memory.fraction"),
        ("VALIDATION_SPARK_MEMORY_STORAGE_FRACTION", "spark.memory.storageFraction"),
        ("VALIDATION_SPARK_DRIVER_CORES", "spark.driver.cores"),
        ("VALIDATION_SPARK_DRIVER_EXTRA_JAVA_OPTIONS", "spark.driver.extraJavaOptions"),
        ("VALIDATION_SPARK_DRIVER_MEMORY_OVERHEAD", "spark.driver.memoryOverhead"),
        (
            "VALIDATION_SPARK_DRIVER_MEMORY_OVERHEAD_FACTOR",
            "spark.driver.memoryOverheadFactor",
        ),
    ]:
        if bool(os.environ.get(env)):
            spark_settings[key] = os.environ[env]

    with spark_session(
        temp_dir,
        name="Validation",
        config=list(spark_settings.items()),
    ) as ss:
        # For the validation itself we read the file as if everything was defined as a string.
        # The upstream validation already checked whether the cells themselves are correctly formed.
        dataset_schema_string_only =\
            create_spark_schema_from_validation_config(config, string_only=True)
        # When finally writing a parquet file (or when writing an empty parquet) we should use the
        # correct schema.
        dataset_schema =\
            create_spark_schema_from_validation_config(config, string_only=False)
        column_names = [f.name for f in dataset_schema_string_only]
        string_column_names = [
            column_names[jx]
            for jx, col in enumerate(config.root.config.columns)
            if col.formatType == FormatType.STRING
        ]
        # These columns were added by the validation pipeline
        annotated_df_cols = [
            StructField(ROW_NUM_COLUMN, LongType()),
            StructField(HAS_ERROR_COL, BooleanType()),
        ]
        spark_schema_string_only = StructType(annotated_df_cols + dataset_schema_string_only)
        spark_schema = StructType(annotated_df_cols + dataset_schema)

        # It might happen that the input is empty, in this case we still might
        # need to store a parquet file so the pipeline should proceed as usual.
        dataset_parts = get_annotated_dataset_parts(annotated_dataset_path)
        if len(dataset_parts) > 0:
            df = (
                ss
                .read
                # Options for reading a file in which quotes within quotes might have been
                # escaped by repeating the double quote, e.g.:
                # first_column,"this is the ""second, column, with"" commas",third_column
                .option("header", "false")
                .option("multiLine", "true")
                .option("mode", "PERMISSIVE")
                .option("quote", '"')
                .option("escape", '"')
                .csv(annotated_dataset_path, schema=spark_schema_string_only)
                # Fill NAs in string columns with empty strings like we do with pandas
                .fillna("", subset=string_column_names)
            )
        else:
            df = ss.createDataFrame([], spark_schema)

        # Store the DF as parquet again s.t. it uses minimal disk space
        # (not using DISK_ONLY caching as it still takes up 60-70% of the file size)
        temp_parquet_path = os.path.join(temp_dir, "_temp-dataset.parquet")
        logger.info(f"Write file to '{temp_parquet_path}'")
        df.write.parquet(temp_parquet_path)
        logger.info(f"Read file from '{temp_parquet_path}'")
        df = ss.read.parquet(temp_parquet_path)

        logger.info(f"Deleting file at '{annotated_dataset_path}'")
        if os.path.exists(annotated_dataset_path):
            shutil.rmtree(annotated_dataset_path)

        if should_check_uniqueness:
            if config.root.config.table is None:
                raise ValidationError("Table validation settings must be defined")
            if config.root.config.table.uniqueness is None:
                raise ValidationError("Uniqueness validations settings must be defined")
            before = datetime.now()
            unique_keys: list[list[int]] = [
                [ix for ix in tpl.columns]
                for tpl in config.root.config.table.uniqueness.uniqueKeys
            ]
            logger.info(f"Checking uniqueness for keys: {unique_keys}")
            duplicate_row_nrs_df, num_duplication_errors_total, duplication_errors = (
                find_duplicates_spark(df, unique_keys, ROW_NUM_COLUMN, HAS_ERROR_COL)
            )
            update_report_with_uniqueness_check_result(
                report_path, duplication_errors, num_duplication_errors_total
            )
            after = datetime.now()
            logger.info(
                f"Uniqueness check took {(after - before).total_seconds() / 60} min"
            )
            df = add_erroneous_row_ids(df, duplicate_row_nrs_df)

        if drop_invalid_rows:
            logger.info("Dropping invalid rows")
            num_invalid_rows = df.filter(F.col(HAS_ERROR_COL) == True).count()
            df = df.filter(F.col(HAS_ERROR_COL) == False)
            update_report_with_invalid_row_removal_result(report_path, num_invalid_rows)

        df = df.drop(HAS_ERROR_COL, ROW_NUM_COLUMN)

        is_passed = get_report_outcome(report_path) == ValidationOutcome.PASSED
        if is_passed:
            # Copy over the input data so that downstream computations can read it.
            before = datetime.now()
            if should_write_parquet:
                logger.info("Write table to parquet file")
                with tempfile.TemporaryDirectory(dir=temp_dir) as d:
                    temp_output_path = os.path.join(d, "_temp-dataset.parquet")
                    # Cast the DF that was read as having only string columns back to the correct schema,
                    # so that downstream computations can read it.
                    recast_columns = []
                    for current_field, target_field in zip(df.schema.fields, dataset_schema):
                        recast_columns.append(
                            F.col(current_field.name).cast(target_field.dataType).alias(target_field.name)
                        )
                    df.select(*recast_columns).write.parquet(temp_output_path)
                    shutil.copytree(temp_output_path, output_path)
            else:
                logger.info("Write table to CSV file")
                write_df_as_single_file(df, output_path, temp_dir=temp_dir)
            after = datetime.now()
            fmt = "parquet" if should_write_parquet else "csv"
            logger.info(
                f"Writing out {fmt} file took {(after - before).total_seconds() / 60} min"
            )
