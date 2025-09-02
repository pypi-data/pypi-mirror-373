"""
Data reader for Pokemon random battle data (offline only).
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any

from .formats import FORMATS

logger = logging.getLogger(__name__)

class DataReader:
    """
    Handles reading Pokemon random battle data from local files only.
    """
    def __init__(self, data_dir: Path):
        """
        Initialize DataReader.
        Args:
            data_dir: Directory containing local data files
        """
        self.data_dir = data_dir

    def get_format_data(self, format_name: str) -> Optional[Dict[str, Any]]:
        """
        Load data for a given format from local file.
        Args:
            format_name: Format name to load
        Returns:
            Data dictionary, or None if not found
        """
        data_file = self.data_dir / f"{format_name}.json"
        if not data_file.exists():
            logger.warning(f"Data file not found: {data_file}")
            return None
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read data for {format_name}: {e}")
            return None

    def get_metadata(self, format_name: str) -> Optional[Dict[str, Any]]:
        """
        Load metadata for a given format from local file.
        Args:
            format_name: Format name to load
        Returns:
            Metadata dictionary, or None if not found
        """
        metadata_file = self.data_dir / f"{format_name}_metadata.json"
        if not metadata_file.exists():
            logger.warning(f"Metadata file not found: {metadata_file}")
            return None
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read metadata for {format_name}: {e}")
            return None

__all__ = ['DataReader'] 