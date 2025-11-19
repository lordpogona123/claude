#!/usr/bin/env python3
"""
Import Casino List from CSV
Converts CSV file to the JSON format required by the system
"""

import csv
import json
import argparse
from pathlib import Path


def import_csv_to_json(csv_path, output_path=None):
    """
    Import casino list from CSV to JSON

    Expected CSV columns:
    - name (required)
    - url (required)
    - region (optional: EU, LATAM, Asia, Africa, NA)
    - country (optional)
    - priority (optional: high, medium, low)

    Args:
        csv_path: Path to CSV file
        output_path: Path to output JSON file (default: config/casino_list.json)
    """
    if output_path is None:
        output_path = Path(__file__).parent.parent / 'config' / 'casino_list.json'

    casinos = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Required fields
            if not row.get('name') or not row.get('url'):
                print(f"Warning: Skipping row with missing name or url: {row}")
                continue

            casino = {
                'name': row['name'].strip(),
                'url': row['url'].strip(),
                'region': row.get('region', '').strip() or 'Unknown',
                'country': row.get('country', '').strip() or 'Unknown',
                'priority': row.get('priority', '').strip().lower() or 'medium'
            }

            casinos.append(casino)

    # Create output structure
    output = {
        'casinos': casinos,
        'metadata': {
            'total_casinos': len(casinos),
            'last_updated': None,
            'source': str(csv_path)
        }
    }

    # Save to JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✅ Successfully imported {len(casinos)} casinos")
    print(f"📄 Saved to: {output_path}")

    # Show regional distribution
    regions = {}
    for casino in casinos:
        region = casino['region']
        regions[region] = regions.get(region, 0) + 1

    print("\nRegional distribution:")
    for region, count in sorted(regions.items()):
        print(f"  {region}: {count} casinos")


def main():
    parser = argparse.ArgumentParser(description='Import casino list from CSV')
    parser.add_argument('csv_file', help='Path to CSV file')
    parser.add_argument('--output', '-o', help='Output JSON file path')

    args = parser.parse_args()

    import_csv_to_json(args.csv_file, args.output)


if __name__ == '__main__':
    main()
