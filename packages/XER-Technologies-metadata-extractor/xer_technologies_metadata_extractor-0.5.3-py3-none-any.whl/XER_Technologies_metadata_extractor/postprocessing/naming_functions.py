#!/usr/bin/env python3
"""
CSV Column Naming Functions

This module provides functions for renaming CSV columns and adding derived columns.
Extracted from naming_script.py for use in consolidated processing pipeline.
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple
import sys

# Column mapping dictionary - centralized for consistency
COLUMNS_DICT = {
    'gen_speed': 'SN',
    'batt_curr': 'MAP',
    'load_curr': 'MAT',
    'power': 'ECU_voltage',
    'voltage': 'UC_voltage',
    'PDU_voltage': 'UC_voltage',
    'rectifier_tem': 'MOSFET_temperature',
    'current_setpoint': 'HUB_fuel_pressure',
    'gen_temp': 'generator_temperature',
    'run_time': 'FW',
    'maintenance': 'RC_enable',
    'rpm': 'generator_rpm',
    'fuel_consumed': 'battery_current',
    'fuel_flow': 'fuel_level',
    'engine_load': 'PDU_current',
    'throttle_position': 'ECU_throttle',
    'spark_dwell_time': 'UC_throttle',
    'ecu_throttle': 'ECU_throttle',
    'uc_throttle': 'UC_throttle',
    'barometric_pressure': 'ECU_fuel_pressure',
    'intake_manifold_pressure': 'frame_temperature',
    'intake_manifold_temperature': 'CHT_1',
    'CHT1' : 'CHT_1',
    'cylinder_head_temperature': 'engine_fan_current_1',
    'ignition_timing': 'OAT',
    'injection_time': 'PDU_temperature',
    'CHT2' : 'CHT_2',
    'exhaust_gas_temperature': 'CHT_2',
    'throttle_out': 'engine_fan_current_2',
    'Pt_compensation': 'PMU_fan_current'
}


def find_csv_files(folder_path: str) -> List[Path]:
    """
    Find all CSV files in the specified directory and subdirectories.
    
    Args:
        folder_path: Path to the directory to search
        
    Returns:
        List of Path objects for found CSV files
    """
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"Error: Folder '{folder_path}' does not exist.")
        return []
    
    if not folder.is_dir():
        print(f"Error: '{folder_path}' is not a directory.")
        return []
    
    csv_files = list(folder.rglob("*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in '{folder_path}' or its subdirectories.")
        return []
    
    print(f"Found {len(csv_files)} CSV file(s) in '{folder_path}':")
    for file in csv_files:
        rel_path = file.relative_to(folder)
        print(f"  - {rel_path}")
    
    return csv_files


def create_backup_file(csv_file_path: Path) -> bool:
    """
    Create a backup of the CSV file.
    
    Args:
        csv_file_path: Path to the CSV file
        
    Returns:
        bool: True if backup was created successfully
    """
    try:
        backup_path = csv_file_path.with_suffix('.csv.backup')
        
        # If backup already exists, create a timestamped version
        if backup_path.exists():
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = csv_file_path.with_suffix(f'.csv.backup.{timestamp}')
        
        # Read and save backup
        df = pd.read_csv(csv_file_path)
        df.to_csv(backup_path, index=False)
        print(f"  Backup created: {backup_path.name}")
        return True
        
    except Exception as e:
        print(f"  Warning: Could not create backup: {str(e)}")
        return False


def rename_columns_and_add_derived(df: pd.DataFrame, column_mapping: Dict[str, str] = None) -> Tuple[pd.DataFrame, int]:
    """
    Rename columns in a DataFrame according to the provided mapping and add derived columns.
    
    Args:
        df: Input DataFrame
        column_mapping: Dictionary mapping old column names to new column names (default: COLUMNS_DICT)
        
    Returns:
        Tuple of (modified DataFrame, number of columns renamed)
    """
    if column_mapping is None:
        column_mapping = COLUMNS_DICT
    
    # Apply column renaming
    renamed_count = 0
    original_columns = df.columns.tolist()
    new_columns = []
    
    for col in df.columns:
        if col in column_mapping:
            new_name = column_mapping[col]
            new_columns.append(new_name)
            print(f"    '{col}' -> '{new_name}'")
            renamed_count += 1
        else:
            new_columns.append(col)
            print(f"    '{col}' (unchanged)")
    
    # Update column names
    df.columns = new_columns

    # Add 'isGeneratorRunning' column if not present
    if 'isGeneratorRunning' not in df.columns:
        # Determine which column to use for RPM (after renaming)
        rpm_col = None
        if 'generator_rpm' in df.columns:
            rpm_col = 'generator_rpm'
        elif 'rpm' in df.columns:
            rpm_col = 'rpm'
        
        if rpm_col:
            df['isGeneratorRunning'] = (df[rpm_col] > 2000).astype(int)
            print(f"    'isGeneratorRunning' column added (1 if {rpm_col} > 2000, else 0)")
        else:
            print("    Skipped adding 'isGeneratorRunning': no RPM column found.")
    else:
        print("    'isGeneratorRunning' column already exists (unchanged)")

    # Add 'droneInFlight' column if not present
    if 'droneInFlight' not in df.columns:
        # Determine which column to use for RPM (after renaming)
        rpm_col = None
        if 'generator_rpm' in df.columns:
            rpm_col = 'generator_rpm'
        elif 'rpm' in df.columns:
            rpm_col = 'rpm'
        
        if rpm_col:
            df['droneInFlight'] = (df[rpm_col] > 5100).astype(int)
            print(f"    'droneInFlight' column added (1 if {rpm_col} > 5100, else 0)")
        else:
            print("    Skipped adding 'droneInFlight': no RPM column found.")
    else:
        print("    'droneInFlight' column already exists (unchanged)")

    return df, renamed_count


def process_csv_naming(csv_file_path: Path, column_mapping: Dict[str, str] = None, backup: bool = True) -> Tuple[bool, int]:
    """
    Process a single CSV file: create backup, rename columns, and add derived columns.
    
    Args:
        csv_file_path: Path to the CSV file
        column_mapping: Dictionary mapping old column names to new column names
        backup: Whether to create a backup of the original file
    
    Returns:
        Tuple of (success: bool, renamed_count: int)
    """
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file_path)
        
        # Create backup if requested
        if backup:
            create_backup_file(csv_file_path)
        
        # Apply column renaming and add derived columns
        df, renamed_count = rename_columns_and_add_derived(df, column_mapping)

        # Save the updated CSV
        df.to_csv(csv_file_path, index=False)
        
        return True, renamed_count
    
    except Exception as e:
        print(f"  Error processing {csv_file_path.name}: {str(e)}")
        return False, 0


def validate_renamed_columns(df: pd.DataFrame) -> Dict[str, bool]:
    """
    Validate that required columns for calculations are present after renaming.
    
    Args:
        df: DataFrame with renamed columns
        
    Returns:
        Dictionary indicating which required column types are available
    """
    validation = {
        'uc_voltage_available': False,
        'pdu_current_available': False,
        'rpm_available': False,
        'throttle_available': False
    }
    
    # Check for voltage columns (for PMU power calculation)
    voltage_cols = ['UC_voltage', 'voltage']  # UC_voltage is the correct voltage column
    validation['uc_voltage_available'] = any(col in df.columns for col in voltage_cols)
    
    # Check for current columns (for PMU power calculation)
    current_cols = ['PDU_current', 'engine_load', 'Battery_current']
    validation['pdu_current_available'] = any(col in df.columns for col in current_cols)
    
    # Check for RPM columns (for engine power calculation)
    rpm_cols = ['generator_rpm', 'rpm']
    validation['rpm_available'] = any(col in df.columns for col in rpm_cols)
    
    # Check for throttle columns (for engine power calculation)
    throttle_cols = ['ECU_throttle', 'throttle_position', 'ecu_throttle']
    validation['throttle_available'] = any(col in df.columns for col in throttle_cols)
    
    return validation 