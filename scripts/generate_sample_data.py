#!/usr/bin/env python3
"""
Generate Sample Data for Testing
Creates realistic sample data to test the dashboard without running actual scraping
"""

import json
import random
from datetime import datetime
from pathlib import Path


def generate_sample_data():
    """Generate sample scraping results"""

    # Load games and casinos from config
    config_dir = Path(__file__).parent.parent / 'config'

    with open(config_dir / 'triple_cherry_games.json', 'r') as f:
        games_data = json.load(f)

    with open(config_dir / 'casino_list.json', 'r') as f:
        casinos_data = json.load(f)

    games = [g['title'] for g in games_data['games']]
    casinos = casinos_data['casinos']

    results = []

    for casino in casinos:
        # Randomly determine if casino has TC games
        has_tc = random.random() > 0.3  # 70% have TC games

        if has_tc:
            # Randomly select games
            num_games = random.randint(1, min(8, len(games)))
            detected_games = random.sample(games, num_games)

            # Determine coverage category
            if num_games <= 2:
                coverage = 'partial'
            elif num_games <= 5:
                coverage = 'moderate'
            else:
                coverage = 'strong'

            # Random access status
            access_status = random.choices(
                ['online', 'blocked', 'timeout'],
                weights=[0.85, 0.10, 0.05]
            )[0]

            # Provider mention
            provider_mention = random.random() > 0.2

            # Generate issues
            issues = []
            if not provider_mention:
                issues.append("Games found but provider not listed")
            if random.random() > 0.9:
                issues.append("Games detected but no direct URLs found")

            result = {
                'website_url': casino['url'],
                'casino_name': casino['name'],
                'region': casino['region'],
                'country': casino['country'],
                'access_status': access_status,
                'tripleCherryFound': 'yes',
                'detected_games': detected_games,
                'game_page_urls': {game: f"{casino['url']}/games/{game.lower().replace(' ', '-')}" for game in detected_games[:3]},
                'provider_mention': provider_mention,
                'evidence': [f"Found reference to Triple Cherry in {random.choice(['provider list', 'game catalog', 'homepage'])}"],
                'notes': [],
                'scan_timestamp': datetime.now().isoformat(),
                'pages_scanned': random.randint(2, 5),
                'coverage_category': coverage,
                'issues': issues,
                'risk_level': 'high' if access_status != 'online' else ('medium' if issues else 'low')
            }

        else:
            # No TC games
            result = {
                'website_url': casino['url'],
                'casino_name': casino['name'],
                'region': casino['region'],
                'country': casino['country'],
                'access_status': 'online',
                'tripleCherryFound': 'no',
                'detected_games': [],
                'game_page_urls': {},
                'provider_mention': False,
                'evidence': [],
                'notes': ['No Triple Cherry games detected'],
                'scan_timestamp': datetime.now().isoformat(),
                'pages_scanned': random.randint(2, 4),
                'coverage_category': 'none',
                'issues': [],
                'risk_level': 'none'
            }

        results.append(result)

    # Create output structure
    output = {
        'metadata': {
            'total_casinos_scanned': len(results),
            'scan_date': datetime.now().isoformat(),
            'total_games_in_catalog': len(games),
            'note': 'SAMPLE DATA - Generated for testing purposes'
        },
        'results': results
    }

    # Save to raw data directory
    data_dir = Path(__file__).parent.parent / 'data' / 'raw'
    data_dir.mkdir(parents=True, exist_ok=True)

    filename = f"casino_data_SAMPLE_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = data_dir / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"✅ Sample data generated: {filepath}")
    print(f"📊 Casinos: {len(results)}")
    print(f"🎮 Games in catalog: {len(games)}")
    print("\nRun the following to analyze and view:")
    print(f"  python main.py --analyze")
    print(f"  python main.py --dashboard")

    return filepath


if __name__ == '__main__':
    generate_sample_data()
