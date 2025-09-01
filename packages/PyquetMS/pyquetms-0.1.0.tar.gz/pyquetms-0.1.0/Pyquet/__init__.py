"""
Pyquet - Memory-efficient mzML to Parquet converter for mass spectrometry files.

This package provides streaming conversion of mzML files to Parquet format
with minimal memory usage, suitable for processing large datasets.
"""

from .mzml_converter import (
    convert_mzml_to_parquet_streaming,
    get_file_info,
    decode_binary_data
)

__version__ = "0.1.0"
__author__ = "Avni Badiwale"
__email__ = "avnibadiwale@gmail.com"
__description__ = "Memory-efficient mzML to Parquet converter for mass spectrometry files"

__all__ = [
    "convert_mzml_to_parquet_streaming",
    "get_file_info", 
    "decode_binary_data"
]
