"""
Format definitions and utility functions for Pokemon random battle data.
"""

from typing import Dict, List, Optional, Any

# Available RandBats formats
RANDBATS_FORMATS = [
    "gen1randombattle",
    "gen2randombattle", 
    "gen3randombattle",
    "gen4randombattle",
    "gen5randombattle",
    "gen6randombattle",
    "gen7letsgorandombattle",
    "gen7randombattle",
    "gen8bdsprandombattle",
    "gen8randombattle",
    "gen8randomdoublesbattle",
    "gen9babyrandombattle",
    "gen9randombattle",
    "gen9randomdoublesbattle"
]

# Available Smogon formats (common competitive formats)
SMOGON_FORMATS = [
    # Generation 9
    "gen9ou", "gen9uu", "gen9ru", "gen9nu", "gen9pu",
    "gen9ubers", "gen9doublesou", "gen9vgc2024",
    # Generation 8
    "gen8ou", "gen8uu", "gen8ru", "gen8nu", "gen8pu",
    "gen8ubers", "gen8doublesou", "gen8vgc2022", "gen8vgc2023",
    # Generation 7
    "gen7ou", "gen7uu", "gen7ru", "gen7nu", "gen7pu",
    "gen7ubers", "gen7doublesou", "gen7vgc2017", "gen7vgc2018", "gen7vgc2019",
    # Generation 6
    "gen6ou", "gen6uu", "gen6ru", "gen6nu", "gen6pu",
    "gen6ubers", "gen6doublesou", "gen6vgc2014", "gen6vgc2015", "gen6vgc2016",
    # Generation 5
    "gen5ou", "gen5uu", "gen5ru", "gen5nu", "gen5pu",
    "gen5ubers", "gen5doublesou", "gen5vgc2011", "gen5vgc2012", "gen5vgc2013",
    # Generation 4
    "gen4ou", "gen4uu", "gen4nu", "gen4pu",
    "gen4ubers", "gen4doublesou", "gen4vgc2009", "gen4vgc2010",
    # Generation 3
    "gen3ou", "gen3uu", "gen3nu", "gen3pu",
    "gen3ubers", "gen3doublesou",
    # Generation 2
    "gen2ou", "gen2uu", "gen2nu", "gen2pu",
    "gen2ubers", "gen2doublesou",
    # Generation 1
    "gen1ou", "gen1uu", "gen1nu", "gen1pu",
    "gen1ubers", "gen1doublesou"
]

# Format mappings for RandBats extras
RANDBATS_FORMAT_MAPPINGS = {
    'gen1': ['gen1randombattle'],
    'gen2': ['gen2randombattle'],
    'gen3': ['gen3randombattle'],
    'gen4': ['gen4randombattle'],
    'gen5': ['gen5randombattle'],
    'gen6': ['gen6randombattle'],
    'gen7': ['gen7randombattle'],
    'gen8': ['gen8randombattle'],
    'gen9': ['gen9randombattle'],
    'classic': ['gen1randombattle', 'gen2randombattle', 'gen3randombattle', 'gen4randombattle'],
    'modern': ['gen8randombattle', 'gen9randombattle'],
    'doubles': ['gen8randomdoublesbattle', 'gen9randomdoublesbattle'],
    'letsgo': ['gen7letsgorandombattle'],
    'bdsp': ['gen8bdsprandombattle'],
    'baby': ['gen9babyrandombattle'],
    'all': RANDBATS_FORMATS
}

# Format mappings for Smogon extras
SMOGON_FORMAT_MAPPINGS = {
    'ou': [fmt for fmt in SMOGON_FORMATS if 'ou' in fmt and 'doubles' not in fmt],
    'uu': [fmt for fmt in SMOGON_FORMATS if 'uu' in fmt],
    'ru': [fmt for fmt in SMOGON_FORMATS if 'ru' in fmt],
    'nu': [fmt for fmt in SMOGON_FORMATS if 'nu' in fmt],
    'pu': [fmt for fmt in SMOGON_FORMATS if 'pu' in fmt],
    'ubers': [fmt for fmt in SMOGON_FORMATS if 'ubers' in fmt],
    'doubles': [fmt for fmt in SMOGON_FORMATS if 'doubles' in fmt],
    'vgc': [fmt for fmt in SMOGON_FORMATS if 'vgc' in fmt],
    'current': ['gen9ou', 'gen9uu', 'gen9ru', 'gen9nu', 'gen9pu'],
    'gen9': [fmt for fmt in SMOGON_FORMATS if fmt.startswith('gen9')],
    'gen8': [fmt for fmt in SMOGON_FORMATS if fmt.startswith('gen8')],
    'gen7': [fmt for fmt in SMOGON_FORMATS if fmt.startswith('gen7')],
    'gen6': [fmt for fmt in SMOGON_FORMATS if fmt.startswith('gen6')],
    'gen5': [fmt for fmt in SMOGON_FORMATS if fmt.startswith('gen5')],
    'gen4': [fmt for fmt in SMOGON_FORMATS if fmt.startswith('gen4')],
    'gen3': [fmt for fmt in SMOGON_FORMATS if fmt.startswith('gen3')],
    'gen2': [fmt for fmt in SMOGON_FORMATS if fmt.startswith('gen2')],
    'gen1': [fmt for fmt in SMOGON_FORMATS if fmt.startswith('gen1')],
    'all': SMOGON_FORMATS
}

# Combined format mappings
COMBINED_FORMAT_MAPPINGS = {
    'current': ['gen9randombattle', 'gen9ou', 'gen9uu'],
    'complete': ['randbats-all', 'smogon-all'],
    'competitive': ['smogon-all'],
    'random': ['randbats-all']
}

# Backward compatibility
FORMATS = RANDBATS_FORMATS
FORMAT_MAPPINGS = RANDBATS_FORMAT_MAPPINGS

# Global PokemonData instance for quick access functions
_global_data = None

__all__ = [
    # Format lists
    'RANDBATS_FORMATS',
    'SMOGON_FORMATS',
    'FORMATS',  # Backward compatibility
    
    # Format mappings
    'RANDBATS_FORMAT_MAPPINGS',
    'SMOGON_FORMAT_MAPPINGS',
    'FORMAT_MAPPINGS',  # Backward compatibility
    'COMBINED_FORMAT_MAPPINGS',
    
    # Quick access functions
    'get_pokemon',
    'get_smogon_sets',
    'list_pokemon',
    'list_smogon_pokemon',
    'update_data',
    
    # Utility functions
    'get_available_randbats_formats',
    'get_available_smogon_formats',
    'get_randbats_format_mappings',
    'get_smogon_format_mappings',
    'resolve_randbats_formats',
    'resolve_smogon_formats',
    'get_randbats_format_info',
    'get_smogon_format_info',
]


def _get_global_data():
    """Get or create global PokemonData instance."""
    global _global_data
    if _global_data is None:
        # Import here to avoid circular import
        from .core import PokemonData
        _global_data = PokemonData()
    return _global_data


def get_pokemon(pokemon_name: str, format_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Quick access function to get Pokemon data (RandBats).
    
    Args:
        pokemon_name: Name of the Pokemon
        format_name: Battle format (optional)
        
    Returns:
        Pokemon data dictionary or None
    """
    data = _get_global_data()
    return data.get_randbats(pokemon_name, format_name)


def get_smogon_sets(pokemon_name: str, format_name: str) -> Optional[Dict[str, Any]]:
    """
    Quick access function to get Smogon sets.
    
    Args:
        pokemon_name: Name of the Pokemon
        format_name: Battle format
        
    Returns:
        Smogon sets dictionary or None
    """
    data = _get_global_data()
    return data.get_smogon_sets(pokemon_name, format_name)


def list_pokemon(format_name: str) -> List[str]:
    """
    Quick access function to list Pokemon in a format (RandBats).
    
    Args:
        format_name: Battle format name
        
    Returns:
        List of Pokemon names
    """
    data = _get_global_data()
    return data.list_randbats_pokemon(format_name)


def list_smogon_pokemon(format_name: str) -> List[str]:
    """
    Quick access function to list Pokemon in a Smogon format.
    
    Args:
        format_name: Battle format name
        
    Returns:
        List of Pokemon names
    """
    data = _get_global_data()
    return data.list_smogon_pokemon(format_name)




def get_available_randbats_formats() -> List[str]:
    """
    Get list of all available RandBats formats.
    
    Returns:
        List of format names
    """
    return RANDBATS_FORMATS.copy()


def get_available_smogon_formats() -> List[str]:
    """
    Get list of all available Smogon formats.
    
    Returns:
        List of format names
    """
    return SMOGON_FORMATS.copy()


def get_randbats_format_mappings() -> Dict[str, List[str]]:
    """
    Get RandBats format mappings for extras.
    
    Returns:
        Dictionary mapping extra names to format lists
    """
    return RANDBATS_FORMAT_MAPPINGS.copy()


def get_smogon_format_mappings() -> Dict[str, List[str]]:
    """
    Get Smogon format mappings for extras.
    
    Returns:
        Dictionary mapping extra names to format lists
    """
    return SMOGON_FORMAT_MAPPINGS.copy()


def resolve_randbats_formats(formats: List[str]) -> List[str]:
    """
    Resolve RandBats format aliases to actual format names.
    
    Args:
        formats: List of format names or aliases
        
    Returns:
        List of resolved format names
    """
    resolved = []
    for fmt in formats:
        if fmt in RANDBATS_FORMAT_MAPPINGS:
            resolved.extend(RANDBATS_FORMAT_MAPPINGS[fmt])
        elif fmt in RANDBATS_FORMATS:
            resolved.append(fmt)
        else:
            # Unknown format, skip
            continue
    return list(set(resolved))  # Remove duplicates


def resolve_smogon_formats(formats: List[str]) -> List[str]:
    """
    Resolve Smogon format aliases to actual format names.
    
    Args:
        formats: List of format names or aliases
        
    Returns:
        List of resolved format names
    """
    resolved = []
    for fmt in formats:
        if fmt in SMOGON_FORMAT_MAPPINGS:
            resolved.extend(SMOGON_FORMAT_MAPPINGS[fmt])
        elif fmt in SMOGON_FORMATS:
            resolved.append(fmt)
        else:
            # Unknown format, skip
            continue
    return list(set(resolved))  # Remove duplicates


def get_randbats_format_info(format_name: str) -> Dict[str, Any]:
    """
    Get information about a specific RandBats format.
    
    Args:
        format_name: Battle format name
        
    Returns:
        Dictionary with format information
    """
    if format_name not in RANDBATS_FORMATS:
        return {}
    
    info = {
        'name': format_name,
        'generation': _extract_generation(format_name),
        'type': _extract_randbats_type(format_name),
        'available': True
    }
    
    # Add Pokemon count if data is loaded
    data = _get_global_data()
    if format_name in data._randbats_data:
        info['pokemon_count'] = len(data._randbats_data[format_name])
    
    return info


def get_smogon_format_info(format_name: str) -> Dict[str, Any]:
    """
    Get information about a specific Smogon format.
    
    Args:
        format_name: Battle format name
        
    Returns:
        Dictionary with format information
    """
    if format_name not in SMOGON_FORMATS:
        return {}
    
    info = {
        'name': format_name,
        'generation': _extract_generation(format_name),
        'type': _extract_smogon_type(format_name),
        'available': True
    }
    
    # Add Pokemon count if data is loaded
    data = _get_global_data()
    if format_name in data._smogon_data._data:
        info['pokemon_count'] = len(data._smogon_data._data[format_name])
    
    return info


def _extract_generation(format_name: str) -> str:
    """Extract generation from format name."""
    if format_name.startswith('gen'):
        return format_name[3:4]  # gen1 -> 1, gen9 -> 9
    return 'unknown'


def _extract_randbats_type(format_name: str) -> str:
    """Extract battle type from RandBats format name."""
    if 'doubles' in format_name:
        return 'doubles'
    elif 'letsgo' in format_name:
        return 'letsgo'
    elif 'bdsp' in format_name:
        return 'bdsp'
    elif 'baby' in format_name:
        return 'baby'
    else:
        return 'singles'


def _extract_smogon_type(format_name: str) -> str:
    """Extract battle type from Smogon format name."""
    if 'doubles' in format_name:
        return 'doubles'
    elif 'vgc' in format_name:
        return 'vgc'
    elif 'ou' in format_name and 'doubles' not in format_name:
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