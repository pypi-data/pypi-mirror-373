# localsets

**Fully offline Pokémon battle data. All data is bundled with the package and never downloaded at install or runtime. Updates are handled automatically by GitHub Actions and published with each new release.**

Offline Pokemon battle data with auto-updates from official sources.

## What it does

- **Random Battle Data**: Access Pokemon Showdown's RandBats data offline
- **Competitive Sets**: Get Smogon competitive Pokemon sets
- **Auto-Updates**: Automatically syncs with official repositories every 24 hours (via CI, not by end user)
- **Multiple Formats**: Supports all generations (Gen 1-9) and battle formats

## Quick Start

```python
from localsets import PokemonData

data = PokemonData(
    randbats_formats=['gen9randombattle'],
    smogon_formats=['gen9ou']
)

pikachu = data.get_randbats('pikachu', 'gen9randombattle')
sets = data.get_smogon_sets('pikachu', 'gen9ou')
```

## Installation

```bash
pip install localsets
```

## CLI Usage

```bash
# Get random battle Pokemon
localsets randbats get pikachu --format gen9randombattle

# Get competitive sets
localsets smogon get pikachu gen9ou
```

## Data Sources

- **RandBats**: [pkmn/randbats](https://github.com/pkmn/randbats) - Pokemon Showdown random battle data
- **Smogon**: [smogon/pokemon-showdown](https://github.com/smogon/pokemon-showdown) - Competitive Pokemon sets

## Features

- Offline-first with bundled data
- Automatic updates via GitHub Actions (not by end user)
- Support for all Pokemon generations
- Both random battle and competitive formats
- Simple Python API and CLI interface
- Graceful fallbacks and error handling 
