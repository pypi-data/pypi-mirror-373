"""
File Adapter for OrionAI
========================

Handles various file types including PDFs, CSVs, text files, etc.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict

from ..core.manager import BaseAdapter

logger = logging.getLogger(__name__)


class FileAdapter(BaseAdapter):
    """Adapter for file objects."""
    
    @staticmethod
    def can_handle(obj: Any) -> bool:
        """Check if object is a file path or file-like object."""
        if isinstance(obj, (str, Path)):
            return os.path.exists(str(obj))
        
        # Check for file-like objects
        return hasattr(obj, 'read') or hasattr(obj, 'readline')
    
    def get_metadata(self, obj: Any) -> Dict[str, Any]:
        """
        Extract metadata from file object.
        
        Args:
            obj: File path or file-like object
            
        Returns:
            Dictionary containing file metadata
        """
        try:
            if isinstance(obj, (str, Path)):
                file_path = Path(obj)
                metadata = {
                    "type": "File",
                    "file_path": str(file_path.absolute()),
                    "file_name": file_path.name,
                    "file_extension": file_path.suffix.lower(),
                    "file_size_bytes": file_path.stat().st_size,
                    "exists": file_path.exists()
                }
                
                if file_path.exists():
                    # Add file type specific metadata
                    ext = file_path.suffix.lower()
                    
                    if ext == '.pdf':
                        metadata.update(self._get_pdf_metadata(file_path))
                    elif ext == '.csv':
                        metadata.update(self._get_csv_metadata(file_path))
                    elif ext in ['.txt', '.md', '.py', '.js', '.html', '.xml']:
                        metadata.update(self._get_text_metadata(file_path))
                    elif ext in ['.xlsx', '.xls']:
                        metadata.update(self._get_excel_metadata(file_path))
                    elif ext in ['.json']:
                        metadata.update(self._get_json_metadata(file_path))
                
                return metadata
            
            else:
                # File-like object
                return {
                    "type": "File",
                    "file_type": "file_like_object",
                    "has_read": hasattr(obj, 'read'),
                    "has_readline": hasattr(obj, 'readline'),
                    "object_type": str(type(obj).__name__)
                }
                
        except Exception as e:
            logger.error(f"Error extracting file metadata: {str(e)}")
            return {
                "type": "File",
                "error": str(e)
            }
    
    def _get_pdf_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract PDF-specific metadata."""
        metadata = {"content_type": "pdf"}
        
        try:
            # Try to use PyMuPDF (fitz) if available
            import fitz
            doc = fitz.open(str(file_path))
            metadata.update({
                "page_count": doc.page_count,
                "has_text": True,
                "pdf_metadata": doc.metadata
            })
            
            # Extract some sample text
            if doc.page_count > 0:
                first_page = doc[0]
                sample_text = first_page.get_text()[:500]
                metadata["sample_text"] = sample_text
            
            doc.close()
            
        except ImportError:
            try:
                # Fallback to pdfplumber
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    metadata.update({
                        "page_count": len(pdf.pages),
                        "has_text": True
                    })
                    
                    if pdf.pages:
                        sample_text = pdf.pages[0].extract_text()
                        if sample_text:
                            metadata["sample_text"] = sample_text[:500]
                        
            except ImportError:
                metadata["error"] = "No PDF library available (install PyMuPDF or pdfplumber)"
        
        except Exception as e:
            metadata["error"] = f"Error reading PDF: {str(e)}"
        
        return metadata
    
    def _get_csv_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract CSV-specific metadata."""
        metadata = {"content_type": "csv"}
        
        try:
            import pandas as pd
            
            # Read a small sample to get column info
            sample_df = pd.read_csv(file_path, nrows=5)
            metadata.update({
                "columns": sample_df.columns.tolist(),
                "estimated_rows": "unknown",  # Would need to count lines
                "dtypes": sample_df.dtypes.to_dict(),
                "sample_data": sample_df.head(3).to_dict('records')
            })
            
        except ImportError:
            metadata["error"] = "Pandas not available for CSV analysis"
        except Exception as e:
            metadata["error"] = f"Error reading CSV: {str(e)}"
        
        return metadata
    
    def _get_text_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract text file metadata."""
        metadata = {"content_type": "text"}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            metadata.update({
                "line_count": content.count('\\n') + 1,
                "char_count": len(content),
                "word_count": len(content.split()),
                "sample_content": content[:500] if content else ""
            })
            
        except UnicodeDecodeError:
            try:
                # Try different encoding
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                metadata["encoding"] = "latin-1"
                metadata.update({
                    "line_count": content.count('\\n') + 1,
                    "char_count": len(content),
                    "sample_content": content[:500] if content else ""
                })
            except Exception as e:
                metadata["error"] = f"Error reading text file: {str(e)}"
        
        except Exception as e:
            metadata["error"] = f"Error reading text file: {str(e)}"
        
        return metadata
    
    def _get_excel_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract Excel file metadata."""
        metadata = {"content_type": "excel"}
        
        try:
            import pandas as pd
            
            # Get sheet names
            excel_file = pd.ExcelFile(file_path)
            metadata["sheet_names"] = excel_file.sheet_names
            
            # Get info about first sheet
            if excel_file.sheet_names:
                first_sheet = pd.read_excel(file_path, sheet_name=0, nrows=5)
                metadata.update({
                    "columns": first_sheet.columns.tolist(),
                    "dtypes": first_sheet.dtypes.to_dict(),
                    "sample_data": first_sheet.head(3).to_dict('records')
                })
            
        except ImportError:
            metadata["error"] = "Pandas/openpyxl not available for Excel analysis"
        except Exception as e:
            metadata["error"] = f"Error reading Excel file: {str(e)}"
        
        return metadata
    
    def _get_json_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract JSON file metadata."""
        metadata = {"content_type": "json"}
        
        try:
            import json
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            metadata.update({
                "data_type": str(type(data).__name__),
                "structure": self._analyze_json_structure(data)
            })
            
            if isinstance(data, dict):
                metadata["keys"] = list(data.keys())[:10]  # First 10 keys
            elif isinstance(data, list):
                metadata["array_length"] = len(data)
                if data:
                    metadata["first_item_type"] = str(type(data[0]).__name__)
        
        except Exception as e:
            metadata["error"] = f"Error reading JSON file: {str(e)}"
        
        return metadata
    
    def _analyze_json_structure(self, data: Any, max_depth: int = 3) -> str:
        """Analyze JSON structure recursively."""
        if max_depth <= 0:
            return "..."
        
        if isinstance(data, dict):
            if not data:
                return "{}"
            sample_keys = list(data.keys())[:3]
            key_samples = []
            for key in sample_keys:
                value_type = self._analyze_json_structure(data[key], max_depth - 1)
                key_samples.append(f'"{key}": {value_type}')
            result = "{" + ", ".join(key_samples)
            if len(data) > 3:
                result += ", ..."
            result += "}"
            return result
        elif isinstance(data, list):
            if not data:
                return "[]"
            first_item = self._analyze_json_structure(data[0], max_depth - 1)
            return f"[{first_item}, ...]" if len(data) > 1 else f"[{first_item}]"
        elif isinstance(data, str):
            return "string"
        elif isinstance(data, (int, float)):
            return "number"
        elif isinstance(data, bool):
            return "boolean"
        elif data is None:
            return "null"
        else:
            return str(type(data).__name__)
