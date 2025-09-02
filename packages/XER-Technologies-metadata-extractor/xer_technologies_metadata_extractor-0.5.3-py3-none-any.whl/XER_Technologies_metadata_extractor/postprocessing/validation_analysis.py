#!/usr/bin/env python3
"""
Validation Analysis Script for XER Calculated Columns

This script analyzes the reasonability of the new calculated columns:
- PMU_power (UC_voltage * PDU_current)
- Engine_power (2D interpolation from RPM/throttle)
- System_efficiency (PMU_power / Engine_power * 100)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import List, Dict, Tuple
import warnings
warnings.filterwarnings('ignore')

class CalculationValidator:
    """Validator for XER calculation reasonability checks."""
    
    def __init__(self, csv_file_path: str):
        """Initialize validator with CSV file."""
        self.csv_file_path = Path(csv_file_path)
        self.df = None
        self.validation_results = {}
        
    def load_data(self) -> bool:
        """Load CSV data."""
        try:
            self.df = pd.read_csv(self.csv_file_path)
            print(f"Loaded {len(self.df)} rows from {self.csv_file_path.name}")
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def analyze_input_columns(self) -> Dict:
        """Analyze the input columns used for calculations."""
        print("\n" + "="*60)
        print("INPUT COLUMN ANALYSIS")
        print("="*60)
        
        input_analysis = {}
        key_columns = ['UC_voltage', 'PDU_current', 'generator_rpm', 'ECU_throttle']
        
        for col in key_columns:
            if col in self.df.columns:
                data = self.df[col].dropna()
                analysis = {
                    'count': len(data),
                    'mean': data.mean(),
                    'std': data.std(),
                    'min': data.min(),
                    'max': data.max(),
                    'unique_values': len(data.unique()),
                    'zero_count': (data == 0).sum(),
                    'negative_count': (data < 0).sum()
                }
                input_analysis[col] = analysis
                
                print(f"\n{col}:")
                print(f"  Range: {analysis['min']:.3f} to {analysis['max']:.3f}")
                print(f"  Mean ± Std: {analysis['mean']:.3f} ± {analysis['std']:.3f}")
                print(f"  Unique values: {analysis['unique_values']}")
                print(f"  Zero values: {analysis['zero_count']} ({100*analysis['zero_count']/analysis['count']:.1f}%)")
                print(f"  Negative values: {analysis['negative_count']} ({100*analysis['negative_count']/analysis['count']:.1f}%)")
                
                # Flag potential issues
                if analysis['std'] == 0:
                    print(f"  ⚠️  WARNING: No variation in {col} (constant value)")
                if analysis['negative_count'] > analysis['count'] * 0.1:  # >10% negative
                    print(f"  ⚠️  WARNING: High proportion of negative values in {col}")
            else:
                print(f"\n{col}: ❌ NOT FOUND")
                input_analysis[col] = None
        
        return input_analysis
    
    def analyze_calculated_columns(self) -> Dict:
        """Analyze the calculated output columns."""
        print("\n" + "="*60)
        print("CALCULATED COLUMN ANALYSIS")
        print("="*60)
        
        calc_analysis = {}
        calc_columns = ['PMU_power', 'Engine_power', 'System_efficiency']
        
        for col in calc_columns:
            if col in self.df.columns:
                data = self.df[col].dropna()
                analysis = {
                    'count': len(data),
                    'mean': data.mean(),
                    'std': data.std(),
                    'min': data.min(),
                    'max': data.max(),
                    'unique_values': len(data.unique()),
                    'zero_count': (data == 0).sum(),
                    'negative_count': (data < 0).sum()
                }
                calc_analysis[col] = analysis
                
                print(f"\n{col}:")
                print(f"  Range: {analysis['min']:.3f} to {analysis['max']:.3f}")
                print(f"  Mean ± Std: {analysis['mean']:.3f} ± {analysis['std']:.3f}")
                print(f"  Unique values: {analysis['unique_values']}")
                print(f"  Zero values: {analysis['zero_count']} ({100*analysis['zero_count']/analysis['count']:.1f}%)")
                print(f"  Negative values: {analysis['negative_count']} ({100*analysis['negative_count']/analysis['count']:.1f}%)")
                
                # Column-specific validation
                if col == 'PMU_power':
                    self._validate_pmu_power(data, analysis)
                elif col == 'Engine_power':
                    self._validate_engine_power(data, analysis)
                elif col == 'System_efficiency':
                    self._validate_system_efficiency(data, analysis)
            else:
                print(f"\n{col}: ❌ NOT FOUND")
                calc_analysis[col] = None
        
        return calc_analysis
    
    def _validate_pmu_power(self, data, analysis):
        """Validate PMU power calculations."""
        print("  PMU Power Validation:")
        
        # Check if calculation matches UC_voltage * PDU_current
        if 'UC_voltage' in self.df.columns and 'PDU_current' in self.df.columns:
            calculated_power = self.df['UC_voltage'] * self.df['PDU_current']
            diff = abs(self.df['PMU_power'] - calculated_power).max()
            print(f"    ✓ Calculation accuracy: max difference = {diff:.6f}")
            
            # Check for reasonable power ranges
            if abs(analysis['min']) > 1000 or abs(analysis['max']) > 5000:
                print(f"    ⚠️  WARNING: PMU power values seem very high (>{1000}W)")
            
            if analysis['negative_count'] > 0:
                print(f"    ℹ️  INFO: Negative power indicates power flow direction")
        else:
            print("    ❌ Cannot validate: missing input columns")
    
    def _validate_engine_power(self, data, analysis):
        """Validate engine power calculations."""
        print("  Engine Power Validation:")
        
        # Check for variation
        if analysis['std'] < 10:  # Very low standard deviation
            print(f"    ⚠️  WARNING: Very low variation in engine power (std={analysis['std']:.3f})")
            
        # Check for reasonable ranges (typical generator: 500-3000W)
        if analysis['min'] < 100 or analysis['max'] > 5000:
            print(f"    ⚠️  WARNING: Engine power outside typical generator range (100-5000W)")
        
        # Check if values are constant (interpolation issue)
        if analysis['unique_values'] == 1:
            print(f"    ⚠️  WARNING: Engine power is constant - check RPM/throttle variation")
    
    def _validate_system_efficiency(self, data, analysis):
        """Validate system efficiency calculations."""
        print("  System Efficiency Validation:")
        
        # Check reasonable efficiency range (typically 20-90%)
        valid_range = (data > 0) & (data <= 100)
        valid_count = valid_range.sum()
        print(f"    Valid efficiency range (0-100%): {valid_count}/{len(data)} ({100*valid_count/len(data):.1f}%)")
        
        if analysis['max'] > 100:
            print(f"    ⚠️  WARNING: Efficiency >100% detected (max={analysis['max']:.1f}%)")
        
        # Check for typical generator efficiency range
        typical_range = (data >= 20) & (data <= 90)
        typical_count = typical_range.sum()
        print(f"    Typical range (20-90%): {typical_count}/{len(data)} ({100*typical_count/len(data):.1f}%)")
        
        if typical_count < len(data) * 0.5:  # <50% in typical range
            print(f"    ⚠️  WARNING: Many efficiency values outside typical range")
    
    def check_calculation_relationships(self):
        """Check relationships between calculated values."""
        print("\n" + "="*60)
        print("CALCULATION RELATIONSHIP ANALYSIS")
        print("="*60)
        
        required_cols = ['PMU_power', 'Engine_power', 'System_efficiency', 'UC_voltage', 'PDU_current']
        if all(col in self.df.columns for col in required_cols):
            
            # 1. PMU Power vs Input Variables
            print("\n1. PMU Power Correlation with Inputs:")
            pmu_uc_corr = self.df['PMU_power'].corr(self.df['UC_voltage'])
            pmu_pdu_corr = self.df['PMU_power'].corr(self.df['PDU_current'])
            print(f"   PMU_power vs UC_voltage: {pmu_uc_corr:.3f}")
            print(f"   PMU_power vs PDU_current: {pmu_pdu_corr:.3f}")
            
            # 2. Engine Power vs Input Variables
            if 'generator_rpm' in self.df.columns and 'ECU_throttle' in self.df.columns:
                print("\n2. Engine Power Correlation with Inputs:")
                eng_rpm_corr = self.df['Engine_power'].corr(self.df['generator_rpm'])
                eng_throttle_corr = self.df['Engine_power'].corr(self.df['ECU_throttle'])
                print(f"   Engine_power vs generator_rpm: {eng_rpm_corr:.3f}")
                print(f"   Engine_power vs ECU_throttle: {eng_throttle_corr:.3f}")
                
                if abs(eng_rpm_corr) < 0.1 and abs(eng_throttle_corr) < 0.1:
                    print("   ⚠️  WARNING: Low correlation between engine power and RPM/throttle")
            
            # 3. System Efficiency Calculation Check
            print("\n3. System Efficiency Calculation Check:")
            # Manual calculation: efficiency = (abs(PMU_power) / Engine_power) * 100
            manual_eff = (abs(self.df['PMU_power']) / self.df['Engine_power']) * 100
            manual_eff = manual_eff.replace([np.inf, -np.inf], 0)  # Handle division by zero
            
            diff = abs(self.df['System_efficiency'] - manual_eff).max()
            print(f"   Max difference from manual calculation: {diff:.6f}%")
            
            if diff > 1.0:  # More than 1% difference
                print("   ⚠️  WARNING: Significant difference in efficiency calculation")
        else:
            print("Missing required columns for relationship analysis")
    
    def generate_summary_report(self):
        """Generate a summary of validation findings."""
        print("\n" + "="*60)
        print("VALIDATION SUMMARY & RECOMMENDATIONS")
        print("="*60)
        
        issues = []
        recommendations = []
        
        # Check for common issues and generate recommendations
        if 'PMU_power' in self.df.columns:
            pmu_negative_pct = (self.df['PMU_power'] < 0).mean() * 100
            if pmu_negative_pct > 50:
                issues.append(f"PMU power is negative in {pmu_negative_pct:.1f}% of readings")
                recommendations.append("Consider investigating PDU current polarity or power flow direction")
        
        if 'Engine_power' in self.df.columns:
            eng_unique = self.df['Engine_power'].nunique()
            if eng_unique < 10:
                issues.append(f"Engine power has very low variation ({eng_unique} unique values)")
                recommendations.append("Check RPM and throttle input variation, verify interpolation setup")
        
        if 'System_efficiency' in self.df.columns:
            eff_data = self.df['System_efficiency'].dropna()
            low_eff_pct = (eff_data < 10).mean() * 100
            if low_eff_pct > 80:
                issues.append(f"System efficiency is very low (<10%) in {low_eff_pct:.1f}% of readings")
                recommendations.append("Investigate power measurement scaling or calculation methodology")
        
        print("\n🚨 Issues Found:")
        if issues:
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")
        else:
            print("   ✅ No major issues detected")
        
        print("\n💡 Recommendations:")
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        else:
            print("   ✅ Calculations appear reasonable")
        
        # Suggest plots to create
        print("\n📊 Suggested Validation Plots:")
        print("   1. Time series of PMU_power, Engine_power, System_efficiency")
        print("   2. Scatter plot: PMU_power vs (UC_voltage * PDU_current)")
        print("   3. Scatter plot: Engine_power vs generator_rpm (colored by ECU_throttle)")
        print("   4. Histogram of System_efficiency values")
        print("   5. Correlation matrix of all calculated and input variables")
    
    def run_full_validation(self):
        """Run complete validation analysis."""
        if not self.load_data():
            return False
        
        print(f"Validating calculations in: {self.csv_file_path.name}")
        print(f"Total rows: {len(self.df)}, Total columns: {len(self.df.columns)}")
        
        # Run all validation steps
        self.analyze_input_columns()
        self.analyze_calculated_columns()
        self.check_calculation_relationships()
        self.generate_summary_report()
        
        return True

def main():
    """Main function for running validation."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python validation_analysis.py <csv_file_path>")
        print("Example: python validation_analysis.py testfiles/XFD_103_20250409_1557.csv")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    validator = CalculationValidator(csv_file)
    
    if validator.run_full_validation():
        print(f"\n✅ Validation complete for {csv_file}")
    else:
        print(f"\n❌ Validation failed for {csv_file}")
        sys.exit(1)

if __name__ == "__main__":
    main() 