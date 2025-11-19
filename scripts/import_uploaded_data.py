#!/usr/bin/env python3
"""
Import Casino and Games Data from Uploaded CSV
Processes the 'urlinksSS - Paginas (1).csv' file
"""

import csv
import json
import re
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime


def extract_region_from_url(url):
    """Guess region from URL domain"""
    domain = urlparse(url).netloc.lower()

    # Latin America TLDs
    if any(tld in domain for tld in ['.mx', '.br', '.ar', '.cl', '.co', '.pe', '.uy', '.ve']):
        return 'LATAM'

    # European TLDs
    if any(tld in domain for tld in ['.eu', '.de', '.fr', '.es', '.it', '.uk', '.com', '.live']):
        return 'EU'

    # Asian TLDs
    if any(tld in domain for tld in ['.jp', '.cn', '.kr', '.sg', '.ph', '.asia']):
        return 'Asia'

    # Default
    return 'Unknown'


def extract_country_from_url(url):
    """Guess country from URL domain"""
    domain = urlparse(url).netloc.lower()

    country_map = {
        '.mx': 'Mexico',
        '.br': 'Brazil',
        '.ar': 'Argentina',
        '.cl': 'Chile',
        '.co': 'Colombia',
        '.pe': 'Peru',
        '.uy': 'Uruguay',
        '.ve': 'Venezuela',
        '.es': 'Spain',
        '.de': 'Germany',
        '.fr': 'France',
        '.it': 'Italy',
        '.uk': 'United Kingdom',
        '.jp': 'Japan',
        '.cn': 'China',
        '.kr': 'South Korea',
        '.ph': 'Philippines',
    }

    for tld, country in country_map.items():
        if tld in domain:
            return country

    return 'Unknown'


def extract_casino_name_from_url(url):
    """Extract casino name from URL"""
    domain = urlparse(url).netloc
    # Remove www. and TLD
    name = domain.replace('www.', '').split('.')[0]
    # Capitalize
    return name.capitalize()


def parse_csv_file(csv_path):
    """Parse the uploaded CSV file with multiline game fields"""

    casinos = []
    all_games = set()

    with open(csv_path, 'r', encoding='utf-8') as f:
        # Skip header
        next(f)

        current_url = None
        current_games = []

        for line in f:
            line = line.rstrip('\n')

            # Check if line starts with http (new casino entry)
            if line.startswith('http'):
                # Save previous casino if exists
                if current_url and current_url.startswith('http'):
                    casino_name = extract_casino_name_from_url(current_url)
                    region = extract_region_from_url(current_url)
                    country = extract_country_from_url(current_url)

                    casinos.append({
                        'name': casino_name,
                        'url': current_url,
                        'region': region,
                        'country': country,
                        'priority': 'high' if len(current_games) > 5 else 'medium',
                        'games_found': current_games  # Temporary field for analysis
                    })

                    all_games.update(current_games)

                # Parse new entry
                parts = line.split(',', 1)
                current_url = parts[0].strip()
                current_games = []

                if len(parts) > 1 and parts[1]:
                    # Remove quotes if present
                    games_text = parts[1].strip('"').strip()
                    if games_text and not games_text.startswith('Casino de'):
                        current_games.append(games_text)
            elif line and current_url:
                # Continuation of games list
                game = line.strip('"').strip()
                if game and not game.startswith('Casino de'):
                    current_games.append(game)

        # Don't forget the last casino
        if current_url and current_url.startswith('http'):
            casino_name = extract_casino_name_from_url(current_url)
            region = extract_region_from_url(current_url)
            country = extract_country_from_url(current_url)

            casinos.append({
                'name': casino_name,
                'url': current_url,
                'region': region,
                'country': country,
                'priority': 'high' if len(current_games) > 5 else 'medium',
                'games_found': current_games
            })

            all_games.update(current_games)

    return casinos, sorted(all_games)


def create_casino_list_json(casinos, output_path):
    """Create casino_list.json"""

    # Remove temporary games_found field
    clean_casinos = []
    for casino in casinos:
        clean_casino = {k: v for k, v in casino.items() if k != 'games_found'}
        clean_casinos.append(clean_casino)

    output = {
        'casinos': clean_casinos,
        'metadata': {
            'total_casinos': len(clean_casinos),
            'last_updated': datetime.now().isoformat(),
            'source': 'urlinksSS - Paginas (1).csv',
            'regions': {}
        }
    }

    # Calculate regional distribution
    regions = {}
    for casino in clean_casinos:
        region = casino['region']
        regions[region] = regions.get(region, 0) + 1

    output['metadata']['regions'] = regions

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    return output_path


def create_games_json(games, output_path):
    """Create triple_cherry_games.json"""

    games_list = []

    for game in games:
        # Create variations of the game name for aliases
        aliases = [
            game,
            game.replace(' ', ''),  # No spaces
            game.replace(' ', '-').lower(),  # Lowercase with dashes
            game.replace("'", ''),  # No apostrophes
        ]

        # Remove duplicates
        aliases = list(set(aliases))

        games_list.append({
            'title': game,
            'aliases': aliases,
            'release_date': 'Unknown',
            'game_type': 'slot'
        })

    output = {
        'games': games_list,
        'metadata': {
            'total_games': len(games_list),
            'last_updated': datetime.now().isoformat(),
            'source': 'urlinksSS - Paginas (1).csv',
            'note': 'Game catalog extracted from casino data'
        }
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    return output_path


def generate_statistics(casinos):
    """Generate statistics about the imported data"""

    total = len(casinos)

    # Regional distribution
    regions = {}
    for casino in casinos:
        region = casino['region']
        regions[region] = regions.get(region, 0) + 1

    # Country distribution
    countries = {}
    for casino in casinos:
        country = casino['country']
        countries[country] = countries.get(country, 0) + 1

    # Games per casino
    games_counts = [len(c['games_found']) for c in casinos]
    avg_games = sum(games_counts) / len(games_counts) if games_counts else 0

    return {
        'total_casinos': total,
        'regions': regions,
        'countries': countries,
        'avg_games_per_casino': round(avg_games, 2),
        'casinos_with_games': sum(1 for c in casinos if c['games_found'])
    }


def main():
    """Main import process"""

    print("=" * 60)
    print("IMPORTING CASINO AND GAMES DATA")
    print("=" * 60)

    # Paths
    base_dir = Path(__file__).parent.parent
    csv_path = base_dir / 'urlinksSS - Paginas (1).csv'
    config_dir = base_dir / 'config'

    if not csv_path.exists():
        print(f"❌ Error: CSV file not found at {csv_path}")
        return

    print(f"\n📂 Reading: {csv_path}")

    # Parse CSV
    casinos, games = parse_csv_file(csv_path)

    print(f"\n✅ Parsed successfully!")
    print(f"   - Casinos: {len(casinos)}")
    print(f"   - Games: {len(games)}")

    # Generate statistics
    stats = generate_statistics(casinos)

    print(f"\n📊 Statistics:")
    print(f"   - Total casinos: {stats['total_casinos']}")
    print(f"   - Casinos with games: {stats['casinos_with_games']}")
    print(f"   - Average games per casino: {stats['avg_games_per_casino']}")

    print(f"\n🌍 Regional distribution:")
    for region, count in sorted(stats['regions'].items()):
        print(f"   - {region}: {count} casinos")

    print(f"\n🌎 Top 10 countries:")
    top_countries = sorted(stats['countries'].items(), key=lambda x: x[1], reverse=True)[:10]
    for country, count in top_countries:
        print(f"   - {country}: {count} casinos")

    # Create JSON files
    print(f"\n📝 Creating configuration files...")

    casino_json = config_dir / 'casino_list.json'
    games_json = config_dir / 'triple_cherry_games.json'

    create_casino_list_json(casinos, casino_json)
    create_games_json(games, games_json)

    print(f"\n✅ Files created:")
    print(f"   - {casino_json}")
    print(f"   - {games_json}")

    print(f"\n🎮 Top 10 games:")
    for i, game in enumerate(sorted(games)[:10], 1):
        print(f"   {i}. {game}")

    print(f"\n{'=' * 60}")
    print("✅ IMPORT COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"\nNext steps:")
    print(f"  1. Review the generated files in config/")
    print(f"  2. Run: python main.py --scrape --limit 10 (test with 10 casinos)")
    print(f"  3. Run: python main.py --full (full scrape)")
    print(f"  4. Run: python main.py --dashboard (view results)")
    print()


if __name__ == '__main__':
    main()
