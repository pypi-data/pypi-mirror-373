import shutil
import sys
import os
from datetime import datetime
from typing import Optional

from .config import DEFAULT_USE_SPARK_FILE_SIZE_THRESHOLD_BYTES
from . import spark
from . import default
from . import validate
from .utils import is_report_passed, read_config
from .schemas import ValidationOutcome
from .error import ValidationError
from .logger import logger


def run(
    input_path: str,
    config_path: str,
    report_path: str,
    types_path: str,
    output_path: str,
    force_spark: bool = False,
    spark_threshold_bytes: int = DEFAULT_USE_SPARK_FILE_SIZE_THRESHOLD_BYTES,
    temp_dir: str = "/scratch",
    drop_invalid_rows: bool = False,
    chunk_size_bytes: Optional[int] = None,
):
    config = read_config(config_path)

    does_input_file_exist = os.path.exists(input_path)
    if not does_input_file_exist:
        raise ValidationError("Input file does not exist")

    input_file_size = os.path.getsize(input_path)
    logger.info(f"Input file size: {round(input_file_size / 1000000, 2)} MB")

    if force_spark or input_file_size > spark_threshold_bytes:
        use_spark = True
    else:
        use_spark = False

    # Whether this pipeline should produce parquet or csv file output.
    should_write_parquet = output_path.endswith(".parquet")

    # Check whether we should detect duplicates.
    should_check_uniqueness = (
        config.root.config.table is not None
        and config.root.config.table.uniqueness is not None
        and config.root.config.table.uniqueness.uniqueKeys is not None
    )

    # Where to store the annotated output of the validation pipeline
    annotated_dataset_path = os.path.join(temp_dir, "_annotated_dataset")

    # Override the size of the chunks into which the input file is split.
    if chunk_size_bytes is None:
        chunk_size_bytes = os.environ.get("VALIDATION_CHUNK_SIZE_BYTES")
        if chunk_size_bytes is not None:
            if int(chunk_size_bytes) > 0:
                chunk_size_bytes = int(chunk_size_bytes)
            else:
                raise Exception("The setting `chunk_size_bytes` must be a positive integer")

    # Override the number of threads used to validate the chunked input file.
    n_concurrent_threads = os.environ.get("VALIDATION_N_CONCURRENT_THREADS")
    if bool(n_concurrent_threads):
        n_concurrent_threads = int(n_concurrent_threads)
    else:
        n_concurrent_threads = None

    # Override the number of chunks that are kept in memory, waiting to be
    # processed by a thread.
    data_channel_size = os.environ.get("VALIDATION_DATA_CHANNEL_SIZE")
    if bool(data_channel_size):
        data_channel_size = int(data_channel_size)
    else:
        data_channel_size = None

    logger.info(
        f"Running with config:"
        f" spark [{use_spark}]"
        f", uniqueness_check [{should_check_uniqueness}]"
        f", drop_invalid_rows [{drop_invalid_rows}]"
        f", chunk_size [{chunk_size_bytes or 'default'}]"
        f", parallelism [{n_concurrent_threads or 'default'}]"
        f", data_channel_size [{data_channel_size or 'default'}]"
    )
    logger.info(
        f"Run validation pipeline, storing annotated output at '{annotated_dataset_path}'"
    )
    before = datetime.now()

    _num_rows_total = validate.run_validation_program(
        input_path=input_path,
        config_path=config_path,
        output_path=report_path,
        types_path=types_path,
        annotated_dataset_path=annotated_dataset_path,
        chunk_size_bytes=chunk_size_bytes,
        n_concurrent_threads=n_concurrent_threads,
        data_channel_size=data_channel_size,
    )
    after = datetime.now()
    logger.info(f"Validation pipeline took {(after - before).total_seconds() / 60} min")

    if not is_report_passed(report_path) and not drop_invalid_rows:
        logger.info(f"Validation FAILED and no rows to drop. Will exit.")
        sys.exit(0)

    if not use_spark:
        logger.info(f"Continue w/ pipeline (pandas)")
        default.run(
            annotated_dataset_path=annotated_dataset_path,
            should_write_parquet=should_write_parquet,
            should_check_uniqueness=should_check_uniqueness,
            config_path=config_path,
            report_path=report_path,
            output_path=output_path,
            drop_invalid_rows=drop_invalid_rows,
        )
    else:
        logger.info(f"Continue w/ pipeline (spark)")
        spark.run(
            annotated_dataset_path=annotated_dataset_path,
            should_write_parquet=should_write_parquet,
            should_check_uniqueness=should_check_uniqueness,
            config_path=config_path,
            report_path=report_path,
            output_path=output_path,
            temp_dir=temp_dir,
            drop_invalid_rows=drop_invalid_rows,
        )
