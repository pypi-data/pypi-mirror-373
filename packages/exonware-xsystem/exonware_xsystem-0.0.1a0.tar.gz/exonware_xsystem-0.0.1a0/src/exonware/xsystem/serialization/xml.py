"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: August 31, 2025

XML Serializer Implementation

Uses production-grade libraries (dicttoxml + xmltodict) following
the xSystem principle: use existing libraries, don't reinvent the wheel.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

# Use production-grade XML libraries
try:
    import dicttoxml
    import xmltodict
    XML_AVAILABLE = True
except ImportError:
    XML_AVAILABLE = False

from .iSerialization import iSerialization
from .aSerialization import aSerialization


class XmlSerializer(aSerialization):
    """
    Ultra-simple XML serializer using production libraries.
    
    ✅ FOLLOWS xSYSTEM PRINCIPLE: Use existing libraries!
    - dicttoxml: dict → XML (production-grade)
    - xmltodict: XML → dict (production-grade)
    
    Total implementation: ~10 lines instead of 300+
    """
    
    def __init__(
        self,
        validate_input: bool = True,
        validate_paths: bool = True,
        use_atomic_writes: bool = True,
        max_depth: int = 100,
        max_size_mb: int = 50
    ) -> None:
        """Initialize XML serializer."""
        super().__init__(
            validate_input=validate_input,
            validate_paths=validate_paths,
            use_atomic_writes=use_atomic_writes,
            max_depth=max_depth,
            max_size_mb=max_size_mb
        )
        
        if not XML_AVAILABLE:
            raise ImportError(
                "XML serialization requires 'dicttoxml' and 'xmltodict' packages. "
                "Install with: pip install dicttoxml xmltodict"
            )
    
    @property
    def format_name(self) -> str:
        """Get the format name."""
        return "XML"
    
    @property
    def file_extensions(self) -> Tuple[str, ...]:
        """Get supported file extensions."""
        return (".xml",)
    
    @property
    def mime_type(self) -> str:
        """Get the MIME type."""
        return "application/xml"
    
    @property
    def is_binary_format(self) -> bool:
        """Check if this is a binary format."""
        return False
    
    @property
    def supports_streaming(self) -> bool:
        """Check if streaming is supported."""
        return False
    
    def dumps_text(self, data: Any) -> str:
        """
        Serialize data to XML using dicttoxml.
        
        ✅ PRODUCTION LIBRARY: dicttoxml.dicttoxml()
        """
        if self.validate_input:
            self._validate_data_security(data)
        
        try:
            # Use production library - that's it!
            xml_bytes = dicttoxml.dicttoxml(data, custom_root='root', attr_type=False)
            return xml_bytes.decode('utf-8')
        except Exception as e:
            self._handle_serialization_error("serialization", e)
    
    def loads_text(self, data: str) -> Dict[str, Any]:
        """
        Deserialize XML using xmltodict.
        
        ✅ PRODUCTION LIBRARY: xmltodict.parse()
        """
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        
        if not isinstance(data, str):
            raise ValueError(f"Expected string or bytes, got {type(data)}")
        
        try:
            # Use production library - that's it!
            result = xmltodict.parse(data)
            
            if self.validate_input:
                self._validate_data_security(result)
            
            return result
        except Exception as e:
            self._handle_serialization_error("deserialization", e)
    
    # 🎯 OPTIMIZATION: save_file and load_file inherited from base class!
    # No need to implement - base class handles all file operations with auto-detection
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get XML format schema information."""
        return {
            "format": "XML",
            "version": "1.0",
            "description": "eXtensible Markup Language via dicttoxml/xmltodict",
            "features": {
                "binary": False,
                "hierarchical": True,
                "production_libraries": ["dicttoxml", "xmltodict"],
                "streaming": False
            },
            "file_extensions": list(self.file_extensions),
            "mime_type": self.mime_type
        }
    
    def get_config(self) -> Dict[str, Any]:
        """Get current serializer configuration."""
        config = super().get_config()
        config.update({
            "libraries": ["dicttoxml", "xmltodict"],
            "xml_available": XML_AVAILABLE
        })
        return config


# Error classes for consistency
class XmlError(Exception):
    """Base exception for XML serialization errors."""
    pass