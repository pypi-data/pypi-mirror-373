"""
Validation module for XER Technologies Metadata Extractor.

Provides validation functions for CSV files.
"""

from typing import List, NamedTuple, Optional, Union

from XER_Technologies_metadata_extractor.file_config import (
    CSV_ENCODING,
    MIN_CSV_LINES,
)


class ValidationResult(NamedTuple):
    """Result of file validation with detailed feedback."""

    is_valid: bool
    message: str
    warnings: List[str] = []


class FileValidator:
    """Handles validation of CSV files for metadata extraction."""

    def __init__(self) -> None:
        """Initialize the file validator."""
        pass

    def precheck_csv_file(self, file_data: Union[bytes, str], filename: str) -> ValidationResult:
        """
        Comprehensive precheck for CSV files.

        Args:
            file_data: Raw file data as bytes or string
            filename: Name of the file being validated

        Returns:
            ValidationResult with validation status, message, and warnings
        """
        warnings: List[str] = []

        # Basic file checks
        basic_check = self._basic_file_checks(file_data, filename, ".csv")
        if not basic_check.is_valid:
            return basic_check

        # Handle both string and bytes input
        if isinstance(file_data, str):
            content = file_data
        else:
            # Decode and parse CSV content
            try:
                content = file_data.decode(CSV_ENCODING)
            except UnicodeDecodeError as e:
                return ValidationResult(
                    is_valid=False,
                    message=f"CSV file is not properly encoded (expected {CSV_ENCODING}): {str(e)}",
                )

        lines = content.strip().split("\n")

        # Check minimum line count
        if len(lines) < MIN_CSV_LINES:
            return ValidationResult(
                is_valid=False,
                message=f"CSV file has insufficient data (found {len(lines)} lines, minimum {MIN_CSV_LINES} required)",
            )

        # Validate CSV structure and XFD format
        header = [col.strip() for col in lines[0].split(",")]
        data_sample = lines[1:MIN_CSV_LINES]  # Sample for validation

        structure_result = self._validate_csv_structure(header, data_sample)
        if not structure_result.is_valid:
            return ValidationResult(
                is_valid=False, message=structure_result.message, warnings=warnings
            )

        return ValidationResult(
            is_valid=True,
            message="CSV file validation successful. File appears to be valid CSV format.",
            warnings=warnings,
        )



    def _basic_file_checks(
        self, file_data: Union[bytes, str], filename: str, expected_ext: str
    ) -> ValidationResult:
        """Perform basic file validation checks."""
        if not filename:
            return ValidationResult(is_valid=False, message="Filename is required")

        if not file_data:
            return ValidationResult(is_valid=False, message="File data is empty")
        import os

        file_extension = os.path.splitext(filename)[1].lower()
        if file_extension != expected_ext:
            return ValidationResult(
                is_valid=False,
                message=f"Expected {expected_ext} file, got {file_extension}",
            )

        return ValidationResult(is_valid=True, message="Basic checks passed")

    def _validate_csv_structure(
        self, header: List[str], data_sample: List[str]
    ) -> ValidationResult:
        """Validate basic CSV structure and detect extra columns."""
        if not header:
            return ValidationResult(is_valid=False, message="CSV header is empty")

        header_col_count = len(header)

        # Check for extra columns in data rows
        for i, row in enumerate(data_sample, 1):
            if not row.strip():  # Skip empty rows
                continue

            columns = [col.strip() for col in row.split(",")]
            if len(columns) > header_col_count:
                return ValidationResult(
                    is_valid=False,
                    message=f"Row {i} has {len(columns)} columns but header has {header_col_count}. "
                    f"Extra columns detected without corresponding headers.",
                )

        return ValidationResult(is_valid=True, message="CSV structure is valid")




