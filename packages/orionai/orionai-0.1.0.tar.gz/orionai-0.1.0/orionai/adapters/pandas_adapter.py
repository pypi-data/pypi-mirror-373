"""
Pandas DataFrame Adapter for OrionAI
====================================

Provides specialized functionality for pandas DataFrames.
"""

import logging
from typing import Any, Dict
import pandas as pd

from ..core.manager import BaseAdapter

logger = logging.getLogger(__name__)


class PandasAdapter(BaseAdapter):
    """Adapter for pandas DataFrames."""
    
    @staticmethod
    def can_handle(obj: Any) -> bool:
        """Check if object is a pandas DataFrame."""
        return isinstance(obj, pd.DataFrame)
    
    def get_metadata(self, obj: pd.DataFrame) -> Dict[str, Any]:
        """
        Extract comprehensive metadata from pandas DataFrame.
        
        Args:
            obj: pandas DataFrame
            
        Returns:
            Dictionary containing DataFrame metadata
        """
        try:
            # Basic info
            metadata = {
                "type": "DataFrame",
                "shape": obj.shape,
                "columns": obj.columns.tolist(),
                "dtypes": obj.dtypes.to_dict(),
                "index_type": str(type(obj.index).__name__),
                "memory_usage_mb": round(obj.memory_usage(deep=True).sum() / 1024 / 1024, 2)
            }
            
            # Statistical info for numeric columns
            numeric_cols = obj.select_dtypes(include=['number']).columns.tolist()
            if numeric_cols:
                metadata["numeric_columns"] = numeric_cols
                metadata["has_numeric_data"] = True
            else:
                metadata["has_numeric_data"] = False
            
            # Categorical info
            categorical_cols = obj.select_dtypes(include=['category', 'object']).columns.tolist()
            if categorical_cols:
                metadata["categorical_columns"] = categorical_cols
                # Get unique value counts for categorical columns (limited to avoid large metadata)
                metadata["categorical_info"] = {}
                for col in categorical_cols[:5]:  # Limit to first 5 categorical columns
                    unique_count = obj[col].nunique()
                    metadata["categorical_info"][col] = {
                        "unique_count": unique_count,
                        "top_values": obj[col].value_counts().head(3).to_dict() if unique_count < 100 else "Too many unique values"
                    }
            
            # Missing data info
            missing_data = obj.isnull().sum()
            metadata["missing_data"] = missing_data[missing_data > 0].to_dict()
            metadata["has_missing_data"] = missing_data.sum() > 0
            
            # Sample data (first few rows)
            metadata["sample_data"] = obj.head(3).to_dict('records')
            
            # Date columns
            date_cols = obj.select_dtypes(include=['datetime64']).columns.tolist()
            if date_cols:
                metadata["date_columns"] = date_cols
                metadata["has_date_data"] = True
            else:
                metadata["has_date_data"] = False
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting DataFrame metadata: {str(e)}")
            return {
                "type": "DataFrame",
                "shape": obj.shape,
                "columns": obj.columns.tolist(),
                "error": str(e)
            }
    
    def optimize(self, obj: pd.DataFrame, strategy: str = "memory") -> Dict[str, Any]:
        """
        Apply optimizations to the DataFrame.
        
        Args:
            obj: pandas DataFrame to optimize
            strategy: Optimization strategy
            
        Returns:
            Dictionary with optimization results
        """
        original_memory = obj.memory_usage(deep=True).sum()
        original_memory_mb = round(original_memory / 1024 / 1024, 2)
        
        optimization_results = {
            "strategy": strategy,
            "original_memory_mb": original_memory_mb,
            "optimizations_applied": [],
            "recommendations": []
        }
        
        if strategy in ["memory", "auto"]:
            try:
                # Downcast numeric types
                numeric_cols = obj.select_dtypes(include=['int', 'float']).columns
                for col in numeric_cols:
                    original_dtype = obj[col].dtype
                    if 'int' in str(original_dtype):
                        obj[col] = pd.to_numeric(obj[col], downcast='integer')
                    elif 'float' in str(original_dtype):
                        obj[col] = pd.to_numeric(obj[col], downcast='float')
                    
                    if obj[col].dtype != original_dtype:
                        optimization_results["optimizations_applied"].append(
                            f"Downcasted {col}: {original_dtype} -> {obj[col].dtype}"
                        )
                
                # Convert object columns to categorical if beneficial
                object_cols = obj.select_dtypes(include=['object']).columns
                for col in object_cols:
                    unique_ratio = obj[col].nunique() / len(obj)
                    if unique_ratio < 0.5:  # If less than 50% unique values
                        obj[col] = obj[col].astype('category')
                        optimization_results["optimizations_applied"].append(
                            f"Converted {col} to categorical"
                        )
                
                # Calculate new memory usage
                new_memory = obj.memory_usage(deep=True).sum()
                new_memory_mb = round(new_memory / 1024 / 1024, 2)
                memory_saved = round((original_memory - new_memory) / 1024 / 1024, 2)
                
                optimization_results.update({
                    "new_memory_mb": new_memory_mb,
                    "memory_saved_mb": memory_saved,
                    "memory_reduction_percent": round((memory_saved / original_memory_mb) * 100, 2)
                })
                
            except Exception as e:
                optimization_results["error"] = str(e)
                logger.error(f"Error during DataFrame optimization: {str(e)}")
        
        # Add performance recommendations
        if obj.shape[0] > 10_000_000:  # 10M+ rows
            optimization_results["recommendations"].append(
                "Consider using Polars for better performance with large datasets"
            )
        
        if obj.shape[1] > 100:  # Many columns
            optimization_results["recommendations"].append(
                "Consider selecting only necessary columns to reduce memory usage"
            )
        
        return optimization_results
    
    def sample(self, obj: pd.DataFrame, n: int = 5) -> pd.DataFrame:
        """
        Get a sample of the DataFrame.
        
        Args:
            obj: pandas DataFrame
            n: Number of rows to sample
            
        Returns:
            Sample DataFrame
        """
        try:
            if len(obj) <= n:
                return obj
            return obj.sample(n=n, random_state=42)  # Fixed seed for reproducibility
        except Exception as e:
            logger.warning(f"Error sampling DataFrame: {e}")
            return obj.head(n)  # Fallback to head
