"""
Data Processor - Processes and aggregates scraped casino data
"""

import json
import pandas as pd
from typing import Dict, List
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    """Processes and aggregates scraped casino data"""

    def __init__(self, raw_data: Dict):
        """
        Initialize with raw scraping data

        Args:
            raw_data: Raw data from crawler (JSON format)
        """
        self.raw_data = raw_data
        self.results = raw_data.get('results', [])
        self.metadata = raw_data.get('metadata', {})

    def create_operator_dataframe(self) -> pd.DataFrame:
        """
        Create a pandas DataFrame of operator-level data

        Returns:
            DataFrame with operator information
        """
        data = []

        for result in self.results:
            row = {
                'Casino Name': result.get('casino_name', ''),
                'URL': result.get('website_url', ''),
                'Region': result.get('region', ''),
                'Country': result.get('country', ''),
                'Access Status': result.get('access_status', ''),
                'Triple Cherry Found': result.get('tripleCherryFound', ''),
                'Games Count': len(result.get('detected_games', [])),
                'Provider Mention': result.get('provider_mention', False),
                'Coverage Category': result.get('coverage_category', ''),
                'Risk Level': result.get('risk_level', ''),
                'Issues': ', '.join(result.get('issues', [])),
                'Pages Scanned': result.get('pages_scanned', 0),
                'Scan Timestamp': result.get('scan_timestamp', ''),
            }
            data.append(row)

        df = pd.DataFrame(data)
        return df

    def create_game_matrix(self) -> pd.DataFrame:
        """
        Create a matrix of games vs casinos

        Returns:
            DataFrame with casinos as rows, games as columns
        """
        # Get all unique games
        all_games = set()
        for result in self.results:
            all_games.update(result.get('detected_games', []))

        all_games = sorted(list(all_games))

        # Build matrix
        matrix_data = []

        for result in self.results:
            row = {'Casino': result.get('casino_name', '')}
            detected = result.get('detected_games', [])

            for game in all_games:
                row[game] = 1 if game in detected else 0

            matrix_data.append(row)

        df = pd.DataFrame(matrix_data)
        return df

    def calculate_regional_stats(self) -> Dict:
        """
        Calculate statistics by region

        Returns:
            Dictionary of regional statistics
        """
        regional_data = {}

        # Group by region
        for result in self.results:
            region = result.get('region', 'Unknown')

            if region not in regional_data:
                regional_data[region] = {
                    'total_casinos': 0,
                    'with_triple_cherry': 0,
                    'total_games_detected': 0,
                    'countries': set(),
                    'casinos': []
                }

            regional_data[region]['total_casinos'] += 1

            if result.get('tripleCherryFound') == 'yes':
                regional_data[region]['with_triple_cherry'] += 1

            regional_data[region]['total_games_detected'] += len(result.get('detected_games', []))

            country = result.get('country', 'Unknown')
            regional_data[region]['countries'].add(country)

            regional_data[region]['casinos'].append(result.get('casino_name', ''))

        # Convert sets to lists for JSON serialization
        for region in regional_data:
            regional_data[region]['countries'] = sorted(list(regional_data[region]['countries']))
            regional_data[region]['penetration_rate'] = round(
                (regional_data[region]['with_triple_cherry'] / regional_data[region]['total_casinos'] * 100),
                2
            ) if regional_data[region]['total_casinos'] > 0 else 0

        return regional_data

    def calculate_game_popularity(self) -> List[Dict]:
        """
        Calculate game popularity (frequency across casinos)

        Returns:
            List of games with their appearance counts
        """
        all_games = []

        for result in self.results:
            all_games.extend(result.get('detected_games', []))

        game_counts = Counter(all_games)

        popularity = [
            {
                'game': game,
                'appearances': count,
                'percentage': round((count / len(self.results) * 100), 2)
            }
            for game, count in game_counts.most_common()
        ]

        return popularity

    def identify_risks(self) -> Dict:
        """
        Identify and categorize risks across casinos

        Returns:
            Dictionary of risk categories
        """
        risks = {
            'access_issues': [],
            'technical_issues': [],
            'commercial_issues': [],
            'high_risk_casinos': []
        }

        for result in self.results:
            casino_name = result.get('casino_name', '')

            # Access issues
            if result.get('access_status') in ['blocked', 'timeout', 'error']:
                risks['access_issues'].append({
                    'casino': casino_name,
                    'status': result.get('access_status'),
                    'url': result.get('website_url')
                })

            # Technical issues
            issues = result.get('issues', [])
            for issue in issues:
                if 'not listed' in issue.lower() or 'no direct urls' in issue.lower():
                    risks['technical_issues'].append({
                        'casino': casino_name,
                        'issue': issue,
                        'url': result.get('website_url')
                    })

            # Commercial issues
            if result.get('provider_mention') and len(result.get('detected_games', [])) == 0:
                risks['commercial_issues'].append({
                    'casino': casino_name,
                    'issue': 'Provider listed but no games found',
                    'url': result.get('website_url')
                })

            # High risk casinos
            if result.get('risk_level') == 'high':
                risks['high_risk_casinos'].append({
                    'casino': casino_name,
                    'issues': issues,
                    'url': result.get('website_url')
                })

        return risks

    def calculate_coverage_quality(self) -> Dict:
        """
        Calculate coverage quality metrics

        Returns:
            Dictionary of coverage metrics
        """
        coverage = {
            'none': [],
            'partial': [],
            'moderate': [],
            'strong': []
        }

        for result in self.results:
            category = result.get('coverage_category', 'none')
            casino_info = {
                'name': result.get('casino_name'),
                'games_count': len(result.get('detected_games', [])),
                'games': result.get('detected_games', [])
            }
            coverage[category].append(casino_info)

        return coverage

    def get_country_distribution(self) -> Dict:
        """
        Get distribution of casinos by country

        Returns:
            Dictionary mapping countries to casino counts
        """
        country_data = {}

        for result in self.results:
            country = result.get('country', 'Unknown')

            if country not in country_data:
                country_data[country] = {
                    'total': 0,
                    'with_tc': 0,
                    'casinos': []
                }

            country_data[country]['total'] += 1

            if result.get('tripleCherryFound') == 'yes':
                country_data[country]['with_tc'] += 1

            country_data[country]['casinos'].append(result.get('casino_name'))

        # Add penetration rate
        for country in country_data:
            country_data[country]['penetration_rate'] = round(
                (country_data[country]['with_tc'] / country_data[country]['total'] * 100),
                2
            ) if country_data[country]['total'] > 0 else 0

        return country_data

    def generate_processed_data(self) -> Dict:
        """
        Generate all processed data structures

        Returns:
            Dictionary containing all processed analytics
        """
        logger.info("Processing data and generating analytics...")

        processed = {
            'summary': {
                'total_casinos': len(self.results),
                'casinos_with_tc': sum(1 for r in self.results if r.get('tripleCherryFound') == 'yes'),
                'penetration_rate': round(
                    (sum(1 for r in self.results if r.get('tripleCherryFound') == 'yes') / len(self.results) * 100),
                    2
                ) if len(self.results) > 0 else 0,
                'total_unique_games': len(set(
                    game for r in self.results for game in r.get('detected_games', [])
                )),
            },
            'regional_stats': self.calculate_regional_stats(),
            'country_distribution': self.get_country_distribution(),
            'game_popularity': self.calculate_game_popularity(),
            'coverage_quality': self.calculate_coverage_quality(),
            'risks': self.identify_risks(),
        }

        logger.info("Data processing completed")
        return processed
