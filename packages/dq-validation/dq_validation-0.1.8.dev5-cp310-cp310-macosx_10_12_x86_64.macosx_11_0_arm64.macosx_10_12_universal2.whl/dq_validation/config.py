# How many errors to record when checking for duplicate rows.
NUM_ERRORS_RECORD_BY_KEY_TUPLE = 10
# How many errors to record in the validation report for errors that affect individual
# cells (e.g. wrong email format).
DEFAULT_NUM_RECORD_CELL_ERRORS = 500
# How many errors to record for errors that affect whole rows (e.g. too many columns).
DEFAULT_NUM_RECORD_SCHEMA_ERRORS = 500
# If the input file is smaller or equal to that threshold, use
# pandas instead of spark to check for duplicates or writing parquet.
# This way we avoid spinning up a spark session (especially important
# during CI runs where we work with small test files).
# Note that with a size of >3G we ran into issues during the pandas duplication
# check due to a pyarrow array capacity limit.
DEFAULT_USE_SPARK_FILE_SIZE_THRESHOLD_BYTES = 2 * 10 ** 9
