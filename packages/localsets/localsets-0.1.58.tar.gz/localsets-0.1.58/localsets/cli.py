"""
Command line interface for localsets (standard library only).
"""

import sys
import argparse
import json
from localsets import __version__
from localsets.core import PokemonData

def main_cli():
    parser = argparse.ArgumentParser(description="localsets minimal CLI")
    parser.add_argument('--version', action='store_true', help='Show version and exit')
    subparsers = parser.add_subparsers(dest='command')

    rb = subparsers.add_parser('randbats', help='Search random battle sets')
    rb.add_argument('species', help='Pokemon species or ID')
    rb.add_argument('--format', help='Battle format (optional)')

    sm = subparsers.add_parser('smogon', help='Search Smogon sets')
    sm.add_argument('species', help='Pokemon species or ID')
    sm.add_argument('--format', help='Battle format (optional)')

    args = parser.parse_args()
    if args.version:
        print(f"localsets version {__version__}")
        return
    if args.command is None:
        print(f"localsets CLI is installed and working! Version: {__version__}")
        print("Try 'localsets randbats <species>' or 'localsets smogon <species>'")
        return
    data = PokemonData()
    if args.command == 'randbats':
        if args.format:
            result = data.get_randbats(args.species, args.format)
            print(json.dumps(result, indent=2) if result else f"No data found for {args.species} in {args.format}")
        else:
            results = {}
            for fmt in data.get_randbats_formats():
                res = data.get_randbats(args.species, fmt)
                if res:
                    results[fmt] = res
            print(json.dumps(results, indent=2) if results else f"No data found for {args.species}")
    elif args.command == 'smogon':
        if args.format:
            result = data.get_smogon_sets(args.species, args.format)
            print(json.dumps(result, indent=2) if result else f"No data found for {args.species} in {args.format}")
        else:
            results = data.search_smogon(args.species)
            print(json.dumps(results, indent=2) if results else f"No data found for {args.species}")

if __name__ == "__main__":
    main_cli() 
