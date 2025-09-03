import json
import glob
import os

from .schemas import ValidationConfig, ValidationReport
from .schemas import *
from .logger import logger


def read_config(path: str) -> ValidationConfig:
    with open(path, "r") as file:
        data = json.load(file)
        return ValidationConfig(**data)


def read_report(path: str) -> ValidationReport:
    with open(path, "r") as file:
        data = json.load(file)
        return ValidationReport(**data)


def update_report_outcome(path: str, outcome: ValidationOutcome):
    with open(path, "r") as file:
        data = json.load(file)
        report = ValidationReport(**data)
        report.root.report.outcome = outcome
    with open(path, "w") as file:
        file.write(report.model_dump_json(by_alias=True))


def get_report_outcome(path: str) -> ValidationOutcome:
    report = read_report(path)
    return report.root.report.outcome


def is_report_passed(path: str) -> bool:
    return read_report(path).root.report.outcome == ValidationOutcome.PASSED


def get_annotated_dataset_parts(path: str):
    parts = sorted(glob.glob(os.path.join(path, "*.csv")))
    filtered_parts = []
    for p in parts:
        if os.path.exists(p) and os.path.getsize(p) > 0:
            filtered_parts.append(p)
    return filtered_parts


def update_report_with_uniqueness_check_result(
    report_path: str, duplication_errors, num_duplication_errors_total: int
):
    logger.info(f"Found {num_duplication_errors_total} rows with duplicate values")
    with open(report_path, "r") as f:
        report = json.load(f)
    report["report"]["numInvalidRowsTotal"] += num_duplication_errors_total
    report["report"]["uniqueness"] = {
        "recordedErrors": duplication_errors,
        "numErrorsTotal": num_duplication_errors_total,
    }
    if num_duplication_errors_total and num_duplication_errors_total > 0:
        report["report"]["outcome"] = "FAILED"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)


def update_report_with_invalid_row_removal_result(
    report_path: str, num_rows_removed: int
):
    logger.info(f"Dropped {num_rows_removed} invalid rows")
    with open(report_path, "r") as f:
        report = json.load(f)
    report["report"]["dropInvalidRows"] = {"numInvalidRowsDropped": num_rows_removed}
    report["report"]["outcome"] = "PASSED"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)


def update_report_with_passed_outcome(
    report_path: str,
):
    logger.info("Marking report as passed")
    with open(report_path, "r") as f:
        report = json.load(f)
    report["report"]["outcome"] = "PASSED"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
