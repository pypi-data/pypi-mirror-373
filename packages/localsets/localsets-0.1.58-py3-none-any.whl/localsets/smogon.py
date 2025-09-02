"""
Smogon competitive sets data management.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

logger = logging.getLogger(__name__)


class SmogonSets:
    """
    Class for managing Smogon competitive sets data.
    
    This data is bundled at build time and does not require runtime updates.
    """
    
    def __init__(self, formats: Optional[List[str]] = None):
        """
        Initialize SmogonSets instance.
        
        Args:
            formats: List of format names to load. If None, loads all available.
        """
        self.formats = formats or []
        self._data: Dict[str, Dict] = {}
        self._loaded_formats: set = set()
        
        # Load data
        self._load_data()
    
    def _load_data(self):
        """Load data for all specified formats."""
        if not self.formats:
            # Load all available formats
            self._discover_formats()
        
        for format_name in self.formats:
            if format_name not in self._loaded_formats:
                self._load_format(format_name)
    
    def _discover_formats(self):
        """Discover available Smogon formats from bundled data."""
        data_dir = Path(__file__).parent / "smogon_data"
        if data_dir.exists():
            for file_path in data_dir.glob("*.json"):
                format_name = file_path.stem
                if format_name not in self.formats:
                    self.formats.append(format_name)
    
    def _load_format(self, format_name: str):
        """Load data for a specific format."""
        try:
            # Load from bundled data
            bundled_file = Path(__file__).parent / "smogon_data" / f"{format_name}.json"
            if bundled_file.exists():
                with open(bundled_file, 'r', encoding='utf-8') as f:
                    self._data[format_name] = json.load(f)
                self._loaded_formats.add(format_name)
                logger.debug(f"Loaded {format_name} from bundled data")
                return
            
            # Create empty data if nothing available
            self._data[format_name] = {}
            self._loaded_formats.add(format_name)
            logger.warning(f"No data available for {format_name}")
            
        except Exception as e:
            logger.error(f"Failed to load {format_name}: {e}")
            self._data[format_name] = {}
            self._loaded_formats.add(format_name)
    
    def get_sets(self, pokemon_name: str, format_name: str) -> Optional[Dict[str, Any]]:
        """
        Get all sets for a Pokemon in a specific format.
        
        Args:
            pokemon_name: Name of the Pokemon (case-insensitive)
            format_name: Battle format
            
        Returns:
            Dictionary of sets or None if not found
        """
        if format_name not in self._data:
            logger.warning(f"Format {format_name} not available")
            return None
        
        # Normalize Pokemon name
        pokemon_name = self._normalize_name(pokemon_name)
        
        # Search in format data
        format_data = self._data[format_name]
        if pokemon_name in format_data:
            return format_data[pokemon_name]
        
        # Try fuzzy matching
        for key in format_data.keys():
            if self._normalize_name(key) == pokemon_name:
                return format_data[key]
        
        return None
    
    def get_set(self, pokemon_name: str, format_name: str, set_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific set for a Pokemon.
        
        Args:
            pokemon_name: Name of the Pokemon
            format_name: Battle format
            set_name: Name of the specific set
            
        Returns:
            Set data dictionary or None if not found
        """
        sets = self.get_sets(pokemon_name, format_name)
        if sets and set_name in sets:
            return sets[set_name]
        return None
    
    def list_sets(self, pokemon_name: str, format_name: str) -> List[str]:
        """
        List all set names for a Pokemon in a format.
        
        Args:
            pokemon_name: Name of the Pokemon
            format_name: Battle format
            
        Returns:
            List of set names
        """
        sets = self.get_sets(pokemon_name, format_name)
        if sets:
            return list(sets.keys())
        return []
    
    def list_pokemon(self, format_name: str) -> List[str]:
        """
        List all Pokemon available in a specific format.
        
        Args:
            format_name: Battle format name
            
        Returns:
            List of Pokemon names
        """
        if format_name not in self._data:
            logger.warning(f"Format {format_name} not available")
            return []
        
        return list(self._data[format_name].keys())
    
    def get_formats(self) -> List[str]:
        """Get list of available formats."""
        return list(self._loaded_formats)
    
    def search(self, pokemon_name: str) -> Dict[str, Dict[str, Any]]:
        """
        Search for a Pokemon across all loaded formats.
        
        Args:
            pokemon_name: Name of the Pokemon
            
        Returns:
            Dictionary mapping format names to Pokemon sets
        """
        results = {}
        for format_name in self._loaded_formats:
            sets = self.get_sets(pokemon_name, format_name)
            if sets:
                results[format_name] = sets
        return results
    
    def _normalize_name(self, name: str) -> str:
        """
        Normalize Pokemon name for comparison.
        
        Args:
            name: Pokemon name
            
        Returns:
            Normalized name
        """
        # Remove all non-alphanumeric characters and convert to lowercase
        return ''.join(c for c in name.lower() if c.isalnum())
    
    def get_format_info(self, format_name: str) -> Dict[str, Any]:
        """
        Get information about a specific format.
        
        Args:
            format_name: Battle format name
            
        Returns:
            Dictionary with format information
        """
        if format_name not in self._data:
            return {}
        
        info = {
            'name': format_name,
            'generation': self._extract_generation(format_name),
            'type': self._extract_type(format_name),
            'pokemon_count': len(self._data[format_name]),
            'available': True
        }
        
        return info
    
    def _extract_generation(self, format_name: str) -> str:
        """Extract generation from format name."""
        if format_name.startswith('gen'):
            return format_name[3:4]  # gen1 -> 1, gen9 -> 9
        return 'unknown'
    
    def _extract_type(self, format_name: str) -> str:
        """Extract battle type from format name."""
        if 'doubles' in format_name:
            return 'doubles'
        elif 'vgc' in format_name:
            return 'vgc'
        elif 'ou' in format_name:
            return 'ou'
        elif 'uu' in format_name:
            return 'uu'
        elif 'ru' in format_name:
            return 'ru'
        elif 'nu' in format_name:
            return 'nu'
        elif 'pu' in format_name:
            return 'pu'
        elif 'ubers' in format_name:
            return 'ubers'
        else:
            return 'other' 

__all__ = ['SmogonSets'] 