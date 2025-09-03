"""
Adapter Manager for OrionAI
===========================

Manages registration and selection of appropriate adapters for different object types.
"""

import logging
from typing import Any, Dict, Optional, Type

logger = logging.getLogger(__name__)


class BaseAdapter:
    """Base class for all object adapters."""
    
    @staticmethod
    def can_handle(obj: Any) -> bool:
        """Check if this adapter can handle the given object."""
        raise NotImplementedError
    
    def get_metadata(self, obj: Any) -> Dict[str, Any]:
        """Extract metadata from the object."""
        raise NotImplementedError
    
    def optimize(self, obj: Any, strategy: str = "memory") -> Dict[str, Any]:
        """Apply optimizations to the object."""
        return {"message": "Optimization not implemented for this adapter"}


class AdapterManager:
    """
    Registry and manager for object adapters.
    """
    
    def __init__(self):
        self._adapters = []
        self._register_default_adapters()
    
    def register_adapter(self, adapter_class: Type[BaseAdapter], priority: int = 0):
        """
        Register a new adapter.
        
        Args:
            adapter_class: Adapter class to register
            priority: Priority level (higher = checked first)
        """
        self._adapters.append((priority, adapter_class))
        self._adapters.sort(key=lambda x: x[0], reverse=True)
        logger.info(f"Registered adapter: {adapter_class.__name__}")
    
    def get_adapter(self, obj: Any) -> Optional[BaseAdapter]:
        """
        Get appropriate adapter for the given object.
        
        Args:
            obj: Object to find adapter for
            
        Returns:
            Adapter instance or None if no suitable adapter found
        """
        for priority, adapter_class in self._adapters:
            if adapter_class.can_handle(obj):
                logger.debug(f"Selected adapter: {adapter_class.__name__}")
                return adapter_class()
        
        logger.warning(f"No adapter found for object type: {type(obj)}")
        return None
    
    def list_adapters(self) -> list:
        """List all registered adapters."""
        return [(priority, adapter_class.__name__) for priority, adapter_class in self._adapters]
    
    def _register_default_adapters(self):
        """Register default adapters for common object types."""
        try:
            from ..adapters.pandas_adapter import PandasAdapter
            self.register_adapter(PandasAdapter, priority=10)
        except ImportError:
            logger.debug("Pandas not available, skipping PandasAdapter")
        
        try:
            from ..adapters.polars_adapter import PolarsAdapter
            self.register_adapter(PolarsAdapter, priority=9)
        except ImportError:
            logger.debug("Polars not available, skipping PolarsAdapter")
        
        try:
            from ..adapters.torch_adapter import TorchAdapter
            self.register_adapter(TorchAdapter, priority=8)
        except ImportError:
            logger.debug("PyTorch not available, skipping TorchAdapter")
        
        try:
            from ..adapters.file_adapter import FileAdapter
            self.register_adapter(FileAdapter, priority=5)
        except ImportError:
            logger.debug("File adapter dependencies not available")
        
        logger.info("Default adapters registered")
