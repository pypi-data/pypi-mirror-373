"""
Data Analysis Tool for AIFlow agents.

Provides real data analysis capabilities using pandas and numpy.
NO SIMULATION - Only real data processing and analysis.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from .base_tool import BaseTool

# Optional imports - will gracefully handle if not available
try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class DataAnalysisTool(BaseTool):
    """
    Professional data analysis tool for agents.
    
    Provides real statistical analysis, data processing, and insights.
    NO SIMULATION OR MOCK BEHAVIOR.
    """
    
    def __init__(self):
        """Initialize the data analysis tool."""
        super().__init__(
            name="data_analysis",
            description="Analyze CSV files and datasets with real statistical computations"
        )
        
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas and numpy are required for data analysis. Install with: pip install pandas numpy")
    
    async def execute(self, operation: str, filepath: str = None, data: Any = None, **kwargs) -> Dict[str, Any]:
        """
        Execute a data analysis operation.
        
        Args:
            operation: Analysis type ("analyze_csv", "statistics", "correlations", "trends")
            filepath: Path to CSV file (for file-based operations)
            data: Direct data input (for data-based operations)
            **kwargs: Operation-specific parameters
            
        Returns:
            Dict containing analysis results with real metrics
        """
        try:
            if operation == "analyze_csv":
                if not filepath:
                    raise ValueError("filepath required for analyze_csv operation")
                return await self._analyze_csv_file(filepath, **kwargs)
            elif operation == "statistics":
                return await self._calculate_statistics(filepath, data, **kwargs)
            elif operation == "correlations":
                return await self._calculate_correlations(filepath, data, **kwargs)
            elif operation == "trends":
                return await self._analyze_trends(filepath, data, **kwargs)
            else:
                raise ValueError(f"Unsupported operation: {operation}")
                
        except Exception as e:
            return {
                "success": False,
                "operation": operation,
                "error": str(e),
                "filepath": filepath
            }
    
    async def _analyze_csv_file(self, filepath: str, **kwargs) -> Dict[str, Any]:
        """Analyze CSV file with comprehensive real statistics."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {filepath}")
        
        # Read CSV with pandas
        df = pd.read_csv(filepath)
        
        # Basic information
        analysis = {
            "success": True,
            "operation": "analyze_csv",
            "filepath": filepath,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "data_types": df.dtypes.astype(str).to_dict(),
            "memory_usage": df.memory_usage(deep=True).sum(),
            "file_size": path.stat().st_size
        }
        
        # Missing values analysis
        missing_values = df.isnull().sum()
        analysis["missing_values"] = missing_values.to_dict()
        analysis["missing_percentage"] = (missing_values / len(df) * 100).to_dict()
        
        # Numeric columns analysis
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            numeric_stats = df[numeric_cols].describe()
            analysis["numeric_statistics"] = numeric_stats.to_dict()
            
            # Additional numeric insights
            analysis["numeric_insights"] = {}
            for col in numeric_cols:
                col_data = df[col].dropna()
                analysis["numeric_insights"][col] = {
                    "unique_values": int(col_data.nunique()),
                    "variance": float(col_data.var()),
                    "skewness": float(col_data.skew()),
                    "kurtosis": float(col_data.kurtosis()),
                    "outliers_iqr": self._count_outliers_iqr(col_data)
                }
        
        # Categorical columns analysis
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        if categorical_cols:
            analysis["categorical_analysis"] = {}
            for col in categorical_cols:
                value_counts = df[col].value_counts()
                analysis["categorical_analysis"][col] = {
                    "unique_values": int(df[col].nunique()),
                    "most_frequent": str(value_counts.index[0]) if len(value_counts) > 0 else None,
                    "most_frequent_count": int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                    "top_5_values": value_counts.head(5).to_dict()
                }
        
        # Data quality assessment
        analysis["data_quality"] = {
            "completeness_score": float((1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100),
            "duplicate_rows": int(df.duplicated().sum()),
            "duplicate_percentage": float(df.duplicated().sum() / len(df) * 100)
        }
        
        return analysis
    
    async def _calculate_statistics(self, filepath: str = None, data: Any = None, **kwargs) -> Dict[str, Any]:
        """Calculate comprehensive statistics for dataset."""
        df = await self._load_data(filepath, data)
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            raise ValueError("No numeric columns found for statistical analysis")
        
        stats = {
            "success": True,
            "operation": "statistics",
            "numeric_columns": numeric_cols,
            "statistics": {}
        }
        
        for col in numeric_cols:
            col_data = df[col].dropna()
            stats["statistics"][col] = {
                "count": int(len(col_data)),
                "mean": float(col_data.mean()),
                "median": float(col_data.median()),
                "mode": float(col_data.mode().iloc[0]) if len(col_data.mode()) > 0 else None,
                "std": float(col_data.std()),
                "variance": float(col_data.var()),
                "min": float(col_data.min()),
                "max": float(col_data.max()),
                "range": float(col_data.max() - col_data.min()),
                "q1": float(col_data.quantile(0.25)),
                "q3": float(col_data.quantile(0.75)),
                "iqr": float(col_data.quantile(0.75) - col_data.quantile(0.25)),
                "skewness": float(col_data.skew()),
                "kurtosis": float(col_data.kurtosis())
            }
        
        return stats
    
    async def _calculate_correlations(self, filepath: str = None, data: Any = None, **kwargs) -> Dict[str, Any]:
        """Calculate correlation matrix for numeric columns."""
        df = await self._load_data(filepath, data)
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2:
            raise ValueError("At least 2 numeric columns required for correlation analysis")
        
        correlation_matrix = df[numeric_cols].corr()
        
        # Find strong correlations
        strong_correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:  # Strong correlation threshold
                    strong_correlations.append({
                        "column1": correlation_matrix.columns[i],
                        "column2": correlation_matrix.columns[j],
                        "correlation": float(corr_value),
                        "strength": "strong positive" if corr_value > 0.7 else "strong negative"
                    })
        
        return {
            "success": True,
            "operation": "correlations",
            "correlation_matrix": correlation_matrix.to_dict(),
            "strong_correlations": strong_correlations,
            "numeric_columns": numeric_cols
        }
    
    async def _analyze_trends(self, filepath: str = None, data: Any = None, **kwargs) -> Dict[str, Any]:
        """Analyze trends in time series or sequential data."""
        df = await self._load_data(filepath, data)
        
        # Try to identify date columns
        date_cols = []
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    pd.to_datetime(df[col].head())
                    date_cols.append(col)
                except:
                    continue
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        trends = {
            "success": True,
            "operation": "trends",
            "date_columns": date_cols,
            "numeric_columns": numeric_cols,
            "trend_analysis": {}
        }
        
        # Analyze trends for numeric columns
        for col in numeric_cols:
            col_data = df[col].dropna()
            if len(col_data) > 1:
                # Calculate trend using linear regression slope
                x = np.arange(len(col_data))
                slope = np.polyfit(x, col_data, 1)[0]
                
                trends["trend_analysis"][col] = {
                    "slope": float(slope),
                    "trend_direction": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable",
                    "trend_strength": abs(float(slope)),
                    "start_value": float(col_data.iloc[0]),
                    "end_value": float(col_data.iloc[-1]),
                    "total_change": float(col_data.iloc[-1] - col_data.iloc[0]),
                    "percentage_change": float((col_data.iloc[-1] - col_data.iloc[0]) / col_data.iloc[0] * 100) if col_data.iloc[0] != 0 else 0
                }
        
        return trends
    
    async def _load_data(self, filepath: str = None, data: Any = None):
        """Load data from file or direct input."""
        if filepath:
            path = Path(filepath)
            if not path.exists():
                raise FileNotFoundError(f"Data file not found: {filepath}")
            return pd.read_csv(filepath)
        elif data is not None:
            if isinstance(data, dict):
                return pd.DataFrame(data)
            elif isinstance(data, list):
                return pd.DataFrame(data)
            else:
                raise ValueError("Unsupported data format")
        else:
            raise ValueError("Either filepath or data must be provided")
    
    def _count_outliers_iqr(self, series) -> int:
        """Count outliers using IQR method."""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return int(((series < lower_bound) | (series > upper_bound)).sum())
    
    def _get_parameters_schema(self) -> Dict[str, Any]:
        """Get the parameters schema for data analysis."""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["analyze_csv", "statistics", "correlations", "trends"],
                    "description": "Data analysis operation to perform"
                },
                "filepath": {
                    "type": "string",
                    "description": "Path to CSV file for analysis"
                },
                "data": {
                    "description": "Direct data input (dict or list)"
                }
            },
            "required": ["operation"]
        }
