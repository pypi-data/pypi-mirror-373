"""
Polars DataFrame Adapter for OrionAI
====================================

Provides specialized functionality for Polars DataFrames.
"""

import logging
from typing import Any, Dict

from ..core.manager import BaseAdapter

logger = logging.getLogger(__name__)


class PolarsAdapter(BaseAdapter):
    """Adapter for Polars DataFrames."""
    
    @staticmethod
    def can_handle(obj: Any) -> bool:
        """Check if object is a Polars DataFrame."""
        try:
            import polars as pl
            return isinstance(obj, pl.DataFrame)
        except ImportError:
            return False
    
    def get_metadata(self, obj: Any) -> Dict[str, Any]:
        """
        Extract comprehensive metadata from Polars DataFrame.
        
        Args:
            obj: Polars DataFrame
            
        Returns:
            Dictionary containing DataFrame metadata
        """
        try:
            import polars as pl
            
            metadata = {
                "type": "PolarsDataFrame",
                "shape": obj.shape,
                "columns": obj.columns,
                "dtypes": {col: str(dtype) for col, dtype in zip(obj.columns, obj.dtypes)}
            }
            
            # Get column type information
            numeric_cols = []
            string_cols = []
            date_cols = []
            boolean_cols = []
            
            for col, dtype in zip(obj.columns, obj.dtypes):
                if dtype in [pl.Int8, pl.Int16, pl.Int32, pl.Int64, pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64, pl.Float32, pl.Float64]:
                    numeric_cols.append(col)
                elif dtype == pl.Utf8:
                    string_cols.append(col)
                elif dtype in [pl.Date, pl.Datetime]:
                    date_cols.append(col)
                elif dtype == pl.Boolean:
                    boolean_cols.append(col)
            
            metadata.update({
                "numeric_columns": numeric_cols,
                "string_columns": string_cols,
                "date_columns": date_cols,
                "boolean_columns": boolean_cols,
                "has_numeric_data": len(numeric_cols) > 0,
                "has_string_data": len(string_cols) > 0,
                "has_date_data": len(date_cols) > 0
            })
            
            # Get null counts
            null_counts = obj.null_count()
            metadata["null_counts"] = {
                col: null_counts[col][0] for col in null_counts.columns
            }
            metadata["has_missing_data"] = any(null_counts[col][0] > 0 for col in null_counts.columns)
            
            # Get sample data
            metadata["sample_data"] = obj.head(3).to_dicts()
            
            # Memory usage (estimated)
            metadata["estimated_memory_mb"] = obj.estimated_size("mb")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting Polars DataFrame metadata: {str(e)}")
            return {
                "type": "PolarsDataFrame",
                "shape": obj.shape if hasattr(obj, 'shape') else "unknown",
                "columns": obj.columns if hasattr(obj, 'columns') else [],
                "error": str(e)
            }
    
    def optimize(self, obj: Any, strategy: str = "memory") -> Dict[str, Any]:
        """
        Apply optimizations to the Polars DataFrame.
        
        Args:
            obj: Polars DataFrame to optimize
            strategy: Optimization strategy
            
        Returns:
            Dictionary with optimization results
        """
        import polars as pl
        
        original_memory = obj.estimated_size("mb")
        
        optimization_results = {
            "strategy": strategy,
            "original_memory_mb": original_memory,
            "optimizations_applied": [],
            "recommendations": []
        }
        
        if strategy in ["memory", "auto"]:
            try:
                optimizations = []
                
                # Polars is already quite optimized, but we can suggest some optimizations
                for col, dtype in zip(obj.columns, obj.dtypes):
                    if dtype == pl.Float64:
                        # Check if we can downcast to Float32
                        col_data = obj.select(col).to_series()
                        if col_data.min() >= -3.4e38 and col_data.max() <= 3.4e38:
                            obj = obj.with_columns(pl.col(col).cast(pl.Float32))
                            optimizations.append(f"Downcasted {col} from Float64 to Float32")
                    
                    elif dtype in [pl.Int64, pl.UInt64]:
                        # Check if we can use smaller integer types
                        col_data = obj.select(col).to_series()
                        min_val, max_val = col_data.min(), col_data.max()
                        
                        if dtype == pl.Int64:
                            if min_val >= -2147483648 and max_val <= 2147483647:
                                obj = obj.with_columns(pl.col(col).cast(pl.Int32))
                                optimizations.append(f"Downcasted {col} from Int64 to Int32")
                            elif min_val >= -32768 and max_val <= 32767:
                                obj = obj.with_columns(pl.col(col).cast(pl.Int16))
                                optimizations.append(f"Downcasted {col} from Int64 to Int16")
                
                new_memory = obj.estimated_size("mb")
                memory_saved = original_memory - new_memory
                
                optimization_results.update({
                    "optimizations_applied": optimizations,
                    "new_memory_mb": new_memory,
                    "memory_saved_mb": memory_saved,
                    "memory_reduction_percent": round((memory_saved / original_memory) * 100, 2) if original_memory > 0 else 0
                })
                
            except Exception as e:
                optimization_results["error"] = str(e)
                logger.error(f"Error during Polars DataFrame optimization: {str(e)}")
        
        # Add recommendations
        if obj.shape[0] > 1_000_000:  # 1M+ rows
            optimization_results["recommendations"].append(
                "Consider using lazy evaluation with pl.scan_* functions for better memory efficiency"
            )
        
        if len(obj.columns) > 50:
            optimization_results["recommendations"].append(
                "Consider selecting only necessary columns to reduce memory usage"
            )
        
        return optimization_results
