import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
import re

class DataUtils:
    """Utility functions for data manipulation and analysis"""
    
    @staticmethod
    def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize column names"""
        df_clean = df.copy()
        
        # Convert to lowercase and remove special characters
        df_clean.columns = (
            df_clean.columns
            .str.lower()
            .str.strip()
            .str.replace(r'[^\w\s]', '', regex=True)
            .str.replace(r'\s+', '_', regex=True)
        )
        
        return df_clean
    
    @staticmethod
    def detect_column_type(series: pd.Series) -> str:
        """Detect the most likely data type for a column"""
        
        # Remove null values for analysis
        non_null_series = series.dropna()
        
        if non_null_series.empty:
            return 'unknown'
        
        # Check if numeric
        if pd.api.types.is_numeric_dtype(non_null_series):
            return 'numeric'
        
        # Try to convert to numeric
        try:
            pd.to_numeric(non_null_series)
            return 'numeric'
        except (ValueError, TypeError):
            pass
        
        # Check if datetime
        try:
            pd.to_datetime(non_null_series)
            return 'datetime'
        except (ValueError, TypeError):
            pass
        
        # Check if categorical (limited unique values)
        unique_ratio = non_null_series.nunique() / len(non_null_series)
        if unique_ratio < 0.5:
            return 'categorical'
        
        return 'text'
    
    @staticmethod
    def find_similar_columns(columns: List[str], target_patterns: List[str]) -> List[str]:
        """Find columns that match target patterns using fuzzy matching"""
        
        matches = []
        
        for col in columns:
            col_lower = col.lower()
            for pattern in target_patterns:
                pattern_lower = pattern.lower()
                
                # Exact match
                if col_lower == pattern_lower:
                    matches.append(col)
                    break
                
                # Contains pattern
                elif pattern_lower in col_lower or col_lower in pattern_lower:
                    matches.append(col)
                    break
                
                # Fuzzy match (simple similarity)
                elif DataUtils._calculate_similarity(col_lower, pattern_lower) > 0.7:
                    matches.append(col)
                    break
        
        return matches
    
    @staticmethod
    def _calculate_similarity(str1: str, str2: str) -> float:
        """Calculate simple similarity between two strings"""
        
        # Use Jaccard similarity for simplicity
        set1 = set(str1.lower())
        set2 = set(str2.lower())
        
        if not set1 and not set2:
            return 1.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    @staticmethod
    def validate_engine_hours(hours_series: pd.Series) -> Tuple[pd.Series, List[str]]:
        """Validate and clean engine hours data"""
        
        warnings = []
        cleaned_series = hours_series.copy()
        
        # Convert to numeric, coercing errors to NaN
        cleaned_series = pd.to_numeric(cleaned_series, errors='coerce')
        
        # Check for negative values
        negative_count = (cleaned_series < 0).sum()
        if negative_count > 0:
            warnings.append(f"Found {negative_count} negative engine hours values")
            cleaned_series = cleaned_series.where(cleaned_series >= 0)
        
        # Check for extremely high values (> 50,000 hours)
        high_values = cleaned_series > 50000
        high_count = high_values.sum()
        if high_count > 0:
            warnings.append(f"Found {high_count} unusually high engine hours (>50,000)")
        
        # Check for null values
        null_count = cleaned_series.isnull().sum()
        if null_count > 0:
            warnings.append(f"Found {null_count} invalid/missing engine hours values")
        
        return cleaned_series, warnings
    
    @staticmethod
    def generate_summary_stats(df: pd.DataFrame, numeric_columns: List[str]) -> Dict:
        """Generate comprehensive summary statistics"""
        
        summary = {}
        
        for col in numeric_columns:
            if col in df.columns:
                series = df[col].dropna()
                
                if not series.empty:
                    summary[col] = {
                        'count': len(series),
                        'mean': series.mean(),
                        'median': series.median(),
                        'std': series.std(),
                        'min': series.min(),
                        'max': series.max(),
                        'q25': series.quantile(0.25),
                        'q75': series.quantile(0.75),
                        'missing_count': df[col].isnull().sum(),
                        'missing_percentage': (df[col].isnull().sum() / len(df)) * 100
                    }
        
        return summary
    
    @staticmethod
    def detect_outliers(series: pd.Series, method: str = 'iqr') -> pd.Series:
        """Detect outliers in a numeric series"""
        
        if method == 'iqr':
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            return (series < lower_bound) | (series > upper_bound)
        
        elif method == 'zscore':
            z_scores = np.abs((series - series.mean()) / series.std())
            return pd.Series(z_scores > 3, index=series.index)
        
        else:
            raise ValueError("Method must be 'iqr' or 'zscore'")
    
    @staticmethod
    def export_to_formats(df: pd.DataFrame, base_filename: str) -> Dict[str, bytes]:
        """Export DataFrame to multiple formats"""
        
        exports = {}
        
        # CSV export
        csv_buffer = df.to_csv(index=False).encode('utf-8')
        exports['csv'] = csv_buffer
        
        # Excel export
        try:
            import io
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Data', index=False)
            exports['excel'] = excel_buffer.getvalue()
        except ImportError:
            pass
        
        return exports