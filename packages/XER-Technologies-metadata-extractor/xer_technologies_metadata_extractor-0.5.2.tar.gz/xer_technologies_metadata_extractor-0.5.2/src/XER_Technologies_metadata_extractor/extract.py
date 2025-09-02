import os
import traceback
from datetime import datetime
from io import StringIO
from typing import Any, BinaryIO, Dict, Union

import pandas as pd

from XER_Technologies_metadata_extractor.validation import (
    FileValidator,
    ValidationResult,
)


class MetadataExtractor:
    """
    Simplified metadata extractor for XER CSV files.

    Accepts bytes or file-like objects instead of file paths, making it suitable
    for both local file processing and cloud storage streaming.
    """

    def __init__(self) -> None:
        """Initialize the metadata extractor."""
        self.validator = FileValidator()

    def _read_data(self, file_data: Union[bytes, BinaryIO]) -> bytes:
        """Helper to read data from bytes or file-like object."""
        if hasattr(file_data, "read"):
            data_bytes = file_data.read()
            if hasattr(file_data, "seek"):
                file_data.seek(0)  # Reset for potential reuse
            return data_bytes
        return file_data

    def validate_data(
        self, file_data: Union[bytes, BinaryIO], filename: str
    ) -> ValidationResult:
        """
        Validate data automatically based on filename extension.

        Args:
            file_data: File data as bytes or file-like object
            filename: Name of the file being validated

        Returns:
            ValidationResult with detailed validation feedback
        """
        data_bytes = self._read_data(file_data)
        file_extension = os.path.splitext(filename)[1].lower()

        if file_extension == ".csv":
            return self.validator.precheck_csv_file(data_bytes, filename)
        else:
            return ValidationResult(
                is_valid=False,
                message=f"Unsupported file type: {file_extension}. Supported types: .csv",
            )

    def extract_from_csv_data(self, file_data: Union[bytes, BinaryIO]) -> pd.DataFrame:
        """
        Extract data from CSV bytes or file-like object.

        Args:
            file_data: CSV data as bytes or file-like object

        Returns:
            pd.DataFrame: The CSV data as a pandas DataFrame
        """
        data_bytes = self._read_data(file_data)
        text_data = data_bytes.decode("utf-8")
        return pd.read_csv(StringIO(text_data))

    def extract_csv_metadata(
        self, csv_data: Union[bytes, BinaryIO], csv_filename: str, verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Extract all available metadata from a CSV file.

        Args:
            csv_data: CSV file data as bytes or file-like object
            csv_filename: Name of the CSV file
            verbose: Whether to print detailed information during processing

        Returns:
            dict: Comprehensive metadata including:
                - Timing information (duration, start/end times, date)
                - Power data (PMU power, engine power, efficiency)
                - Generator data (RPM, runtime, flight time)
                - Engine data (starts, working hours)
                - Temperature, voltage, current data
                - Post-processing metadata
                - Validation results
        """
        if verbose:
            print("🔍 Starting CSV metadata extraction...")

        results: Dict[str, Any] = {
            "extraction_timestamp": datetime.now().isoformat(),
            "errors": [],
            "warnings": [],
        }

        try:
            # 1. Validate file data
            validation = self.validate_data(csv_data, csv_filename)
            if not validation.is_valid:
                results["errors"].append(f"File validation failed: {validation.message}")
                if verbose:
                    print(f"   ❌ File validation failed: {validation.message}")
                return results

            if verbose:
                print(f"   ✅ File validation: {'✅ Valid' if validation.is_valid else '❌ Invalid'}")
                if validation.warnings:
                    print(f"      Warnings: {len(validation.warnings)} found")

            # 3. Extract CSV data and calculate metadata
            try:
                df = self.extract_from_csv_data(csv_data)
                
                if verbose:
                    print(f"   📊 Loaded CSV: {len(df)} rows, {len(df.columns)} columns")
                    print(f"      Columns: {list(df.columns)}")

                # Import and use the new metadata calculator
                from .metadata_calculator import metadata_calculator
                
                # Calculate all metadata using the configurable system
                metadata = metadata_calculator.calculate_metadata(df, csv_filename, verbose)
                
                # Merge metadata into results
                results.update(metadata)
                
                if verbose:
                    print(f"   ✓ Metadata extraction completed successfully")

            except Exception as e:
                error_msg = f"Could not calculate metadata: {str(e)}"
                results["warnings"].append(error_msg)
                if verbose:
                    print(f"   ⚠️  Metadata calculation failed: {str(e)}")
                    print(f"   Traceback: {traceback.format_exc()}")

        except Exception as e:
            error_msg = f"Error processing CSV file: {str(e)}"
            results["errors"].append(error_msg)
            if verbose:
                print(f"   ❌ {error_msg}")
                print(f"   Traceback: {traceback.format_exc()}")

        return results
