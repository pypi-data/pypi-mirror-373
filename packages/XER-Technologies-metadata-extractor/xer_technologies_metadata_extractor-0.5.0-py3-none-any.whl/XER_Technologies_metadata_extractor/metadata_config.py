"""
Metadata Configuration Module

This module defines which metadata fields to extract from CSV files.
It provides a centralized, easily modifiable configuration for metadata extraction.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class MetadataField:
    """Definition of a metadata field to extract."""
    name: str
    required: bool = True
    unit: Optional[str] = None
    description: str = ""
    calculation_method: str = "direct"  # direct, min, max, avg, range, duration
    source_columns: Optional[List[str]] = None
    validation_rules: Optional[Dict[str, Any]] = None


class MetadataConfig:
    """Configuration for metadata extraction."""
    
    def __init__(self):
        """Initialize with default metadata fields."""
        self.fields = self._get_default_fields()
    
    def _get_default_fields(self) -> List[MetadataField]:
        """Get the default metadata fields to extract."""
        return [
            # === CRUCIAL INFORMATION (FIRST) ===
            
            # Timing Information
            MetadataField(
                name="log_duration",
                required=True,
                unit="HH:MM:SS",
                description="Total log duration",
                calculation_method="duration",
                source_columns=["time", "timestamp"]
            ),
            MetadataField(
                name="start_time",
                required=True,
                unit="HH:MM:SS",
                description="Flight start time (UTC)",
                calculation_method="first",
                source_columns=["time", "timestamp"]
            ),
            MetadataField(
                name="end_time",
                required=True,
                unit="HH:MM:SS",
                description="Flight end time (UTC)",
                calculation_method="last",
                source_columns=["time", "timestamp"]
            ),
            MetadataField(
                name="flight_date",
                required=True,
                unit="YYYY-MM-DD",
                description="Flight date",
                calculation_method="date_from_time",
                source_columns=["time", "timestamp"]
            ),
            
            # Engine Data (Crucial)
            MetadataField(
                name="total_engine_starts",
                required=True,
                unit="count",
                description="Total number of engine starts",
                calculation_method="engine_starts",
                source_columns=["isGeneratorRunning", "time"]
            ),
            MetadataField(
                name="total_engine_hours",
                required=True,
                unit="hours",
                description="Total engine working hours",
                calculation_method="engine_hours",
                source_columns=["isGeneratorRunning", "time"]
            ),
            MetadataField(
                name="total_flight_hours",
                required=True,
                unit="hours",
                description="Total flight hours",
                calculation_method="flight_hours",
                source_columns=["droneInFlight", "time"]
            ),
            MetadataField(
                name="generator_runtime",
                required=True,
                unit="HH:MM:SS",
                description="Total generator runtime",
                calculation_method="duration_conditional",
                source_columns=["time", "isGeneratorRunning"],
                validation_rules={"condition": "isGeneratorRunning == 1"}
            ),
            
            # File Information (Crucial)
            MetadataField(
                name="file_type",
                required=True,
                unit="",
                description="File type",
                calculation_method="file_type",
                source_columns=[]
            ),
            MetadataField(
                name="timestamp",
                required=True,
                unit="",
                description="Extraction timestamp",
                calculation_method="timestamp",
                source_columns=["time", "timestamp"]
            ),
            
            # Firmware Version (Static Value)
            MetadataField(
                name="fw_version",
                required=True,
                unit="",
                description="Firmware version",
                calculation_method="first",
                source_columns=["FW", "FW_VERSION"]
            ),
            
            # Serial Number (Static Value)
            MetadataField(
                name="SN",
                required=True,
                unit="",
                description="Serial number",
                calculation_method="sn_validation",
                source_columns=["SN"]
            ),
            
            # === DYNAMIC STATISTICS ===
            # All avg_*, max_*, and std_dev_* statistics are now calculated automatically
            # for every column with more than 10 rows of valid numeric data during flight
        ]
    
    
    def get_required_fields(self) -> List[MetadataField]:
        """Get all required fields."""
        return [field for field in self.fields if field.required]
    
    def get_optional_fields(self) -> List[MetadataField]:
        """Get all optional fields."""
        return [field for field in self.fields if not field.required]
    
    def add_field(self, field: MetadataField) -> None:
        """Add a new metadata field."""
        self.fields.append(field)
    
    def remove_field(self, field_name: str) -> None:
        """Remove a metadata field by name."""
        self.fields = [field for field in self.fields if field.name != field_name]
    
    def get_field(self, field_name: str) -> Optional[MetadataField]:
        """Get a specific field by name."""
        for field in self.fields:
            if field.name == field_name:
                return field
        return None
    
    def update_field(self, field_name: str, **kwargs) -> bool:
        """Update a field's properties."""
        field = self.get_field(field_name)
        if field:
            for key, value in kwargs.items():
                if hasattr(field, key):
                    setattr(field, key, value)
            return True
        return False


# Global configuration instance
metadata_config = MetadataConfig() 