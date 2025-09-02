#!/usr/bin/env python3
"""
CSV Calculation Functions

This module provides the XERDataCalculator class and related functions for calculating
PMU power, engine power, and system efficiency. Extracted from calculations_script.py
for use in consolidated processing pipeline.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import warnings
from scipy.interpolate import interp1d


class XERDataCalculator:
    """Calculator class for XER data analysis calculations."""
    
    def __init__(self, reference_data_dir: str = "reference_data"):
        """
        Initialize the calculator with reference data directory.
        
        Args:
            reference_data_dir: Path to directory containing reference RPM/power CSV files
        """
        self.reference_data_dir = Path(reference_data_dir)
        self.reference_interpolators = {}
        self.throttle_values = [30, 40, 50, 60, 70, 80, 90, 99]
        self.power_matrix = None
        self.rpm_grid = None
        self.throttle_grid = None
        
        # Column mapping for different naming conventions (compatible with naming_script.py output)
        self.column_mapping = {
            'voltage': ['voltage', 'UC_voltage', 'ECU_voltage'],  # UC_voltage is the main voltage column
            'current': ['engine_load', 'Battery_current'],
            'uc_voltage': ['UC_voltage'],  # UC_voltage comes from naming script (voltage -> UC_voltage)
            'pdu_current': ['PDU_current'],  # PDU_current comes from naming script (engine_load -> PDU_current)
            'rpm': ['rpm', 'generator_rpm'],  # generator_rpm comes from naming script (rpm -> generator_rpm)
            'throttle': ['throttle_position', 'ecu_throttle', 'ECU_throttle'],  # ECU_throttle comes from naming script
            'time': ['time']
        }
        
    def load_reference_data(self) -> bool:
        """
        Load reference data files and create 1D interpolation functions.
        
        Returns:
            bool: True if reference data loaded successfully, False otherwise
        """
        try:
            print("Loading reference data...")
            
            if not self.reference_data_dir.exists():
                print(f"Warning: Reference data directory {self.reference_data_dir} not found.")
                print("Creating fallback interpolation functions...")
                self._create_fallback_interpolators()
                return False
            
            for throttle in self.throttle_values:
                file_path = self.reference_data_dir / f"RPM_power_{throttle}_throttle.csv"
                
                if file_path.exists():
                    ref_data = pd.read_csv(file_path)
                    
                    # Validate reference data format (case-insensitive)
                    rpm_col = None
                    power_col = None
                    for col in ref_data.columns:
                        if col.lower() == 'rpm':
                            rpm_col = col
                        elif col.lower() == 'power':
                            power_col = col
                    
                    if not rpm_col or not power_col:
                        print(f"Warning: Invalid format in {file_path}. Expected 'rpm' and 'power' columns.")
                        continue
                    
                    # Sort by RPM for interpolation
                    ref_data = ref_data.sort_values(rpm_col)
                    
                    # Create 1D interpolator
                    self.reference_interpolators[throttle] = interp1d(
                        ref_data[rpm_col], 
                        ref_data[power_col],
                        bounds_error=False,
                        fill_value='extrapolate'
                    )
                    print(f"Loaded reference data for {throttle}% throttle: {len(ref_data)} points")
                else:
                    print(f"Warning: Reference file {file_path} not found.")
            
            if not self.reference_interpolators:
                print("No reference data files found. Creating fallback interpolation...")
                self._create_fallback_interpolators()
                return False
            
            self._create_2d_interpolation_surface()
            return True
            
        except Exception as e:
            print(f"Error loading reference data: {e}")
            self._create_fallback_interpolators()
            return False
    
    def _create_fallback_interpolators(self):
        """Create simple fallback interpolation functions when reference data is unavailable."""
        print("Creating fallback interpolation functions...")
        
        # Simple approximation: Power increases with RPM and throttle
        for throttle in self.throttle_values:
            # Create a simple linear relationship as fallback
            rpm_range = np.array([3000, 4000, 5000, 6000, 7000, 8000])
            # Power scales with throttle percentage and RPM
            power_range = (rpm_range - 3000) * (throttle / 100) * 0.01  # Simple scaling
            
            self.reference_interpolators[throttle] = interp1d(
                rpm_range,
                power_range,
                bounds_error=False,
                fill_value='extrapolate'
            )
        
        self._create_2d_interpolation_surface()
    
    def _create_2d_interpolation_surface(self):
        """Create 2D interpolation surface for bivariate interpolation."""
        print("Creating 2D interpolation surface...")
        
        # Define grids
        max_rpm = 8000  # Default maximum
        self.rpm_grid = np.arange(3000, max_rpm + 100, 100)
        self.throttle_grid = np.array(self.throttle_values, dtype=float)
        
        # Create power matrix
        self.power_matrix = np.zeros((len(self.rpm_grid), len(self.throttle_grid)))
        
        for i, rpm_value in enumerate(self.rpm_grid):
            for j, throttle_value in enumerate(self.throttle_grid):
                if throttle_value in self.reference_interpolators:
                    try:
                        power = self.reference_interpolators[throttle_value](rpm_value)
                        self.power_matrix[i, j] = max(0.1, float(power))
                    except:
                        self.power_matrix[i, j] = 0.1
                else:
                    self.power_matrix[i, j] = 0.1
        
        print(f"Created {self.power_matrix.shape} interpolation surface")
    
    def _find_column(self, df: pd.DataFrame, column_type: str) -> Optional[str]:
        """
        Find the actual column name from alternatives.
        
        Args:
            df: DataFrame to search
            column_type: Type of column ('voltage', 'current', 'rpm', 'throttle', 'time')
            
        Returns:
            str: Actual column name if found, None otherwise
        """
        if column_type in self.column_mapping:
            for col_name in self.column_mapping[column_type]:
                if col_name in df.columns:
                    return col_name
        return None
    
    def _bivariate_interpolate(self, input_rpm: float, input_throttle: float) -> float:
        """
        Perform bivariate interpolation to estimate engine power.
        
        Args:
            input_rpm: Raw RPM reading
            input_throttle: Throttle position percentage
            
        Returns:
            float: Interpolated power in kW
        """
        # Zero or very low RPM = zero power (engine not running)
        if input_rpm <= 100:  # Allow small threshold for noise
            return 0.0
        
        # Step 1: Apply RPM calibration
        calibrated_rpm = (7.5 / 9) * input_rpm + 1500
        
        # Step 2: Find surrounding grid points
        rpm_idx = np.searchsorted(self.rpm_grid, calibrated_rpm)
        throttle_idx = np.searchsorted(self.throttle_grid, input_throttle)
        
        # Handle boundary conditions
        rpm_idx = max(1, min(len(self.rpm_grid) - 1, rpm_idx))
        throttle_idx = max(1, min(len(self.throttle_grid) - 1, throttle_idx))
        
        # Get surrounding values
        rpm_lower, rpm_upper = self.rpm_grid[rpm_idx-1], self.rpm_grid[rpm_idx]
        throttle_lower, throttle_upper = self.throttle_grid[throttle_idx-1], self.throttle_grid[throttle_idx]
        
        # Get corner values from power matrix
        power_11 = self.power_matrix[rpm_idx-1, throttle_idx-1]
        power_12 = self.power_matrix[rpm_idx-1, throttle_idx]
        power_21 = self.power_matrix[rpm_idx, throttle_idx-1]
        power_22 = self.power_matrix[rpm_idx, throttle_idx]
        
        # Step 4: Bilinear interpolation
        if rpm_upper != rpm_lower:
            rpm_weight = (calibrated_rpm - rpm_lower) / (rpm_upper - rpm_lower)
        else:
            rpm_weight = 0
            
        if throttle_upper != throttle_lower:
            throttle_weight = (input_throttle - throttle_lower) / (throttle_upper - throttle_lower)
        else:
            throttle_weight = 0
        
        power_interp_1 = power_11 + (power_21 - power_11) * rpm_weight
        power_interp_2 = power_12 + (power_22 - power_12) * rpm_weight
        final_power = power_interp_1 + (power_interp_2 - power_interp_1) * throttle_weight
        
        return max(0.1, final_power)
    
    def calculate_pmu_power(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate PMU power from UC voltage and PDU current measurements.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with PMU_power column added
        """
        print("Calculating PMU power...")
        
        # Find required columns
        uc_voltage_col = self._find_column(df, 'uc_voltage')
        pdu_current_col = self._find_column(df, 'pdu_current')
        
        if not uc_voltage_col:
            print("Warning: UC_voltage column not found. Setting PMU_power to 0.")
            df['PMU_power'] = 0
            return df
        
        if not pdu_current_col:
            print("Warning: PDU_current column not found. Setting PMU_power to 0.")
            df['PMU_power'] = 0
            return df
        
        print(f"Using UC voltage column: {uc_voltage_col}")
        print(f"Using PDU current column: {pdu_current_col}")
        
        # Calculate PMU power: PMU_power = UC_voltage * PDU_current
        df['PMU_power'] = df[uc_voltage_col] * df[pdu_current_col]
        
        # Handle NaN values
        df['PMU_power'] = df['PMU_power'].fillna(0)
        
        pmu_power_values = df['PMU_power'].values
        print(f"PMU power calculated. Range: {pmu_power_values.min():.2f} to {pmu_power_values.max():.2f} W")
        
        return df
    
    def calculate_engine_power(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate engine power using 2D interpolation.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with Engine_power column added
        """
        print("Calculating Engine power...")
        
        # Find required columns
        rpm_col = self._find_column(df, 'rpm')
        throttle_col = self._find_column(df, 'throttle')
        
        if not rpm_col or not throttle_col:
            print(f"Warning: Missing required columns. RPM: {rpm_col}, Throttle: {throttle_col}")
            print("Setting Engine_power to 0.")
            df['Engine_power'] = 0
            return df
        
        print(f"Using RPM column: {rpm_col}, Throttle column: {throttle_col}")
        
        # Calculate engine power for each row
        engine_power = []
        
        for _, row in df.iterrows():
            hub_rpm = row[rpm_col]
            ecu_throttle = row[throttle_col]
            
            if pd.isna(hub_rpm) or pd.isna(ecu_throttle):
                engine_power.append(0)
                continue
            
            # Use 2D interpolation
            try:
                engine_power_kw = self._bivariate_interpolate(hub_rpm, ecu_throttle)
                engine_power_watts = engine_power_kw * 1000
                engine_power.append(engine_power_watts)
            except Exception as e:
                print(f"Warning: Interpolation failed for RPM={hub_rpm}, Throttle={ecu_throttle}: {e}")
                engine_power.append(0)
        
        df['Engine_power'] = engine_power
        print(f"Engine power calculated. Range: {min(engine_power):.2f} to {max(engine_power):.2f} W")
        
        return df
    
    def calculate_system_efficiency(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate system efficiency and apply rolling average.
        
        Args:
            df: Input DataFrame with PMU_power and Engine_power columns
            
        Returns:
            DataFrame with System_efficiency column added
        """
        print("Calculating System efficiency...")
        
        if 'PMU_power' not in df.columns or 'Engine_power' not in df.columns:
            print("Warning: PMU_power or Engine_power columns missing. Setting System_efficiency to 0.")
            df['System_efficiency'] = 0
            return df
        
        # Calculate efficiency for each row
        efficiency = []
        
        for _, row in df.iterrows():
            pmu_power = row['PMU_power']
            engine_power = row['Engine_power']
            
            # Validation checks
            if (pd.isna(pmu_power) or pd.isna(engine_power) or 
                engine_power <= 0.1 or abs(pmu_power) < 0.01):
                efficiency.append(0)
                continue
            
            eff = (abs(pmu_power) / engine_power) * 100
            
            # Quality control filters
            if eff > 150:
                eff = 0  # Upper limit
            elif eff <= 0:
                eff = 0  # Lower limit
            
            efficiency.append(eff)
        
        df['System_efficiency'] = efficiency
        
        valid_efficiencies = [e for e in efficiency if e > 0]
        if valid_efficiencies:
            print(f"System efficiency calculated. Valid range: {min(valid_efficiencies):.2f}% to {max(valid_efficiencies):.2f}%")
        else:
            print("System efficiency calculated. No valid efficiency values found.")
        
        return df
    
    def _apply_rolling_average(self, data: List[float], window_size: int = 10) -> List[float]:
        """
        Apply rolling average with center alignment.
        
        Args:
            data: List of values to smooth
            window_size: Size of rolling window
            
        Returns:
            List of smoothed values
        """
        smoothed = data.copy()
        shift = -5  # Center alignment
        
        for i in range(len(data)):
            # Define window bounds
            start = max(0, i - window_size // 2)
            end = min(len(data), i + window_size // 2 + 1)
            
            # Calculate mean of valid values in window
            window_values = [data[j] for j in range(start, end) if not pd.isna(data[j]) and data[j] > 0]
            
            if len(window_values) > 0:
                rolling_mean = sum(window_values) / len(window_values)
            else:
                rolling_mean = 0
            
            # Apply shift for center alignment
            shifted_index = i - shift
            if 0 <= shifted_index < len(data):
                smoothed[shifted_index] = rolling_mean
        
        return smoothed
    
    def process_calculations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process all calculations on a DataFrame.
        
        Args:
            df: Input DataFrame with renamed columns
            
        Returns:
            DataFrame with calculated columns added
        """
        # Apply calculations in order
        df = self.calculate_pmu_power(df)
        df = self.calculate_engine_power(df)
        df = self.calculate_system_efficiency(df)
        
        return df
    
    def filter_data_by_power(self, df: pd.DataFrame, min_power: float = 100) -> pd.DataFrame:
        """
        Filter data by minimum power threshold.
        
        Args:
            df: Input DataFrame
            min_power: Minimum PMU power threshold in Watts
            
        Returns:
            Filtered DataFrame
        """
        if 'PMU_power' not in df.columns:
            print("Warning: PMU_power column not found for filtering.")
            return df
        
        initial_count = len(df)
        filtered_df = df[df['PMU_power'] > min_power].copy()
        final_count = len(filtered_df)
        
        print(f"Power filtering (>{min_power}W): {initial_count} -> {final_count} rows ({100*final_count/initial_count:.1f}%)")
        
        return filtered_df
    
    def remove_outliers(self, df: pd.DataFrame, threshold: float = 3) -> pd.DataFrame:
        """
        Remove statistical outliers using Z-score analysis.
        
        Args:
            df: Input DataFrame
            threshold: Z-score threshold for outlier detection
            
        Returns:
            DataFrame with outliers removed
        """
        print(f"Removing outliers with Z-score threshold: {threshold}")
        
        critical_columns = ['PMU_power', 'System_efficiency', 'throttle_position', 'rpm', 'voltage']
        
        # Use actual column names from the DataFrame
        available_columns = [col for col in critical_columns if col in df.columns]
        
        # Also check alternative column names
        for col_type in ['rpm', 'throttle', 'voltage']:
            actual_col = self._find_column(df, col_type)
            if actual_col and actual_col not in available_columns:
                available_columns.append(actual_col)
        
        initial_count = len(df)
        filtered_df = df.copy()
        
        for column in available_columns:
            if column in filtered_df.columns:
                values = filtered_df[column].dropna()
                if len(values) > 0:
                    mean_val = values.mean()
                    std_val = values.std()
                    
                    if std_val > 0:
                        z_scores = abs((filtered_df[column] - mean_val) / std_val)
                        outlier_mask = z_scores < threshold
                        filtered_df = filtered_df[outlier_mask]
                        print(f"  {column}: removed {initial_count - len(filtered_df)} outliers")
        
        final_count = len(filtered_df)
        print(f"Outlier removal: {initial_count} -> {final_count} rows ({100*final_count/initial_count:.1f}%)")
        
        return filtered_df 