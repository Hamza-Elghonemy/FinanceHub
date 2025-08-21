import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

class ModelOutputIntegrator:
    """Integrates model analysis outputs with the UI dashboard"""
    
    def __init__(self, output_base_path: str = "c:/University/DIH/FinanceHub/output"):
        self.output_base_path = Path(output_base_path)
        self.company_details_path = self.output_base_path / "OneCompany_details"
        self.sector_comparison_path = self.output_base_path / "CompanyVsSector_PerQuarter"
    
    def load_company_analysis(self, ticker: str) -> Dict[str, Any]:
        """Load all analysis files for a specific company"""
        analysis = {}
        
        # Load from OneCompany_details
        for analysis_type in ['profitability', 'balance_sheet', 'cash_flow']:
            file_path = self.company_details_path / f"{ticker}_{analysis_type}_analysis.json"
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        analysis[analysis_type] = json.load(f)
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
        
        # Load from CompanyVsSector_PerQuarter
        for analysis_type in ['profitability', 'balance_sheet', 'cash_flow']:
            file_path = self.sector_comparison_path / f"{ticker}_{analysis_type}_analysis.json"
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        analysis[f"{analysis_type}_vs_sector"] = json.load(f)
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
        
        return analysis
    
    def get_metric_assessment(self, value: float, metric_type: str, context: Dict = None) -> Dict[str, str]:
        """
        Determine the color class and assessment for a metric
        Returns: {'class': 'excellent|good|neutral|warning|bad', 'description': str}
        """
        if pd.isna(value) or value is None:
            return {'class': 'neutral', 'description': 'No data available'}
        
        # Define thresholds for different metric types
        thresholds = {
            'profit_margin': {'excellent': 0.25, 'good': 0.15, 'neutral': 0.05, 'warning': 0.0},
            'revenue_growth': {'excellent': 0.20, 'good': 0.10, 'neutral': 0.03, 'warning': 0.0},
            'current_ratio': {'excellent': 2.5, 'good': 2.0, 'neutral': 1.5, 'warning': 1.0},
            'debt_to_equity': {'bad': 2.0, 'warning': 1.0, 'neutral': 0.5, 'good': 0.3, 'excellent': 0.1},
            'roe': {'excellent': 0.20, 'good': 0.15, 'neutral': 0.10, 'warning': 0.05},
            'fcf_margin': {'excellent': 0.20, 'good': 0.12, 'neutral': 0.05, 'warning': 0.0},
            'operating_margin': {'excellent': 0.25, 'good': 0.15, 'neutral': 0.08, 'warning': 0.02},
        }
        
        if metric_type not in thresholds:
            # Default assessment for unknown metrics
            if value > 0:
                return {'class': 'good', 'description': 'Positive value'}
            else:
                return {'class': 'bad', 'description': 'Negative value'}
        
        thresh = thresholds[metric_type]
        
        # Special handling for debt_to_equity (lower is better)
        if metric_type == 'debt_to_equity':
            if value >= thresh['bad']:
                return {'class': 'bad', 'description': 'High leverage risk'}
            elif value >= thresh['warning']:
                return {'class': 'warning', 'description': 'Elevated leverage'}
            elif value >= thresh['neutral']:
                return {'class': 'neutral', 'description': 'Moderate leverage'}
            elif value >= thresh['good']:
                return {'class': 'good', 'description': 'Conservative leverage'}
            else:
                return {'class': 'excellent', 'description': 'Very low leverage'}
        
        # Standard assessment (higher is better)
        if value >= thresh['excellent']:
            return {'class': 'excellent', 'description': 'Outstanding performance'}
        elif value >= thresh['good']:
            return {'class': 'good', 'description': 'Strong performance'}
        elif value >= thresh['neutral']:
            return {'class': 'neutral', 'description': 'Adequate performance'}
        elif value >= thresh['warning']:
            return {'class': 'warning', 'description': 'Below expectations'}
        else:
            return {'class': 'bad', 'description': 'Poor performance'}
    
    def get_trend_assessment(self, current: float, previous: float, metric_type: str = 'general') -> Dict[str, str]:
        """Assess trend direction and magnitude"""
        if pd.isna(current) or pd.isna(previous) or previous == 0:
            return {'class': 'neutral', 'description': 'No trend data', 'change': None}
        
        change = (current - previous) / abs(previous)
        
        # Determine trend class based on change magnitude and direction
        if abs(change) < 0.02:  # Less than 2% change
            trend_class = 'neutral'
            description = 'Stable'
        elif change > 0.15:  # More than 15% increase
            trend_class = 'excellent'
            description = 'Strong growth'
        elif change > 0.05:  # 5-15% increase
            trend_class = 'good'
            description = 'Growing'
        elif change > 0:  # Positive but small
            trend_class = 'neutral'
            description = 'Slight increase'
        elif change > -0.05:  # Small decrease
            trend_class = 'warning'
            description = 'Slight decline'
        elif change > -0.15:  # Moderate decrease
            trend_class = 'warning'
            description = 'Declining'
        else:  # Large decrease
            trend_class = 'bad'
            description = 'Sharp decline'
        
        # Special cases for metrics where decrease might be good
        if metric_type == 'debt_to_equity' and change < 0:
            if change < -0.15:
                trend_class = 'excellent'
                description = 'Deleveraging strongly'
            elif change < -0.05:
                trend_class = 'good'
                description = 'Reducing debt'
        
        return {
            'class': trend_class,
            'description': description,
            'change': change
        }

# Initialize the integrator
model_integrator = ModelOutputIntegrator()