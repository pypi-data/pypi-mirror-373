"""
PyTorch Model Adapter for OrionAI
=================================

Provides specialized functionality for PyTorch models.
"""

import logging
from typing import Any, Dict

from ..core.manager import BaseAdapter

logger = logging.getLogger(__name__)


class TorchAdapter(BaseAdapter):
    """Adapter for PyTorch models."""
    
    @staticmethod
    def can_handle(obj: Any) -> bool:
        """Check if object is a PyTorch model."""
        try:
            import torch
            return isinstance(obj, torch.nn.Module)
        except ImportError:
            return False
    
    def get_metadata(self, obj: Any) -> Dict[str, Any]:
        """
        Extract comprehensive metadata from PyTorch model.
        
        Args:
            obj: PyTorch model
            
        Returns:
            Dictionary containing model metadata
        """
        try:
            import torch
            
            metadata = {
                "type": "TorchModel",
                "model_class": obj.__class__.__name__,
                "training_mode": obj.training
            }
            
            # Get model parameters info
            total_params = sum(p.numel() for p in obj.parameters())
            trainable_params = sum(p.numel() for p in obj.parameters() if p.requires_grad)
            
            metadata.update({
                "total_parameters": total_params,
                "trainable_parameters": trainable_params,
                "non_trainable_parameters": total_params - trainable_params
            })
            
            # Get layer information
            layers_info = []
            for name, module in obj.named_modules():
                if len(list(module.children())) == 0:  # Leaf modules only
                    layer_info = {
                        "name": name,
                        "type": module.__class__.__name__
                    }
                    
                    # Add specific info for common layer types
                    if hasattr(module, 'in_features') and hasattr(module, 'out_features'):
                        layer_info.update({
                            "in_features": module.in_features,
                            "out_features": module.out_features
                        })
                    elif hasattr(module, 'in_channels') and hasattr(module, 'out_channels'):
                        layer_info.update({
                            "in_channels": module.in_channels,
                            "out_channels": module.out_channels
                        })
                        if hasattr(module, 'kernel_size'):
                            layer_info["kernel_size"] = module.kernel_size
                    
                    layers_info.append(layer_info)
            
            metadata["layers"] = layers_info[:20]  # Limit to first 20 layers
            metadata["total_layers"] = len(layers_info)
            
            # Get model structure summary
            model_str = str(obj)
            metadata["model_summary"] = model_str[:1000] + "..." if len(model_str) > 1000 else model_str
            
            # Check for common model types
            model_name = obj.__class__.__name__.lower()
            if 'resnet' in model_name:
                metadata["model_family"] = "ResNet"
            elif 'vgg' in model_name:
                metadata["model_family"] = "VGG"
            elif 'bert' in model_name:
                metadata["model_family"] = "BERT"
            elif 'transformer' in model_name:
                metadata["model_family"] = "Transformer"
            else:
                metadata["model_family"] = "Custom"
            
            # Get device information
            try:
                first_param = next(obj.parameters())
                metadata["device"] = str(first_param.device)
                metadata["dtype"] = str(first_param.dtype)
            except StopIteration:
                metadata["device"] = "No parameters"
                metadata["dtype"] = "No parameters"
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting PyTorch model metadata: {str(e)}")
            return {
                "type": "TorchModel",
                "error": str(e)
            }
