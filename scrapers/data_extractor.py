"""
Data Extractor - Extracts Triple Cherry game data from casino websites
"""

import re
import json
from typing import Dict, List, Optional
from .base_scraper import BaseScraper
import logging

logger = logging.getLogger(__name__)


class DataExtractor(BaseScraper):
    """Extracts Triple Cherry specific data from casino websites"""

    def __init__(self, config: Dict, games_data: Dict):
        """
        Initialize the data extractor

        Args:
            config: Configuration dictionary
            games_data: Triple Cherry games data
        """
        super().__init__(config)
        self.games_data = games_data
        self.games_list = [game['title'] for game in games_data.get('games', [])]
        self.all_game_aliases = self._build_game_aliases()
        self.detection_config = config.get('detection', {})
        self.search_terms = self.detection_config.get('search_terms', [])
        self.provider_patterns = self.detection_config.get('provider_patterns', [])
        self.common_paths = self.detection_config.get('common_paths', [])

    def _build_game_aliases(self) -> Dict[str, List[str]]:
        """Build a mapping of games to all their aliases"""
        aliases_map = {}

        for game in self.games_data.get('games', []):
            title = game['title']
            all_names = [title] + game.get('aliases', [])
            aliases_map[title] = all_names

        return aliases_map

    def extract_casino_data(self, casino: Dict) -> Dict:
        """
        Extract all data for a single casino

        Args:
            casino: Casino information dictionary

        Returns:
            Extracted data dictionary
        """
        casino_url = casino['url']
        casino_name = casino['name']

        logger.info(f"Extracting data from: {casino_name} ({casino_url})")

        # Initialize result structure
        result = {
            'website_url': casino_url,
            'casino_name': casino_name,
            'region': casino.get('region', ''),
            'country': casino.get('country', ''),
            'access_status': 'unknown',
            'tripleCherryFound': 'no',
            'detected_games': [],
            'game_page_urls': {},
            'provider_mention': False,
            'evidence': [],
            'notes': [],
            'scan_timestamp': None,
            'pages_scanned': 0,
            'metadata': {}
        }

        # Try to fetch and analyze multiple pages
        pages_to_check = self._generate_urls_to_check(casino_url)

        for page_url, page_type in pages_to_check:
            html, status, metadata = self.fetch_page(page_url)

            result['pages_scanned'] += 1

            if html:
                result['access_status'] = status

                # Parse the page
                soup = self.parse_html(html)

                # Check for Triple Cherry mentions
                tc_found = self._check_triple_cherry_mention(html, soup)
                if tc_found['found']:
                    result['tripleCherryFound'] = 'yes'
                    result['provider_mention'] = tc_found.get('provider_mention', False)
                    result['evidence'].extend(tc_found.get('evidence', []))

                # Check for specific games
                games_found = self._detect_games(html, soup, page_url)
                if games_found:
                    for game_name, game_data in games_found.items():
                        if game_name not in result['detected_games']:
                            result['detected_games'].append(game_name)
                        if game_data.get('url'):
                            result['game_page_urls'][game_name] = game_data['url']

                # Add page-specific notes
                if page_type != 'homepage':
                    result['notes'].append(f"Found data on {page_type} page: {page_url}")

            else:
                # Update status if homepage couldn't be accessed
                if page_type == 'homepage':
                    result['access_status'] = status
                    result['notes'].append(f"Could not access website: {status}")
                    break  # Don't continue if homepage fails

        # Additional analysis
        result = self._analyze_results(result)

        return result

    def _generate_urls_to_check(self, base_url: str) -> List[tuple]:
        """Generate list of URLs to check for each casino"""
        urls = [
            (base_url, 'homepage'),
        ]

        # Add common paths
        for path in self.common_paths[:5]:  # Limit to avoid too many requests
            if path != '/':
                url = base_url.rstrip('/') + path
                page_type = path.split('/')[-1] or 'unknown'
                urls.append((url, page_type))

        return urls

    def _check_triple_cherry_mention(self, html: str, soup) -> Dict:
        """Check if Triple Cherry is mentioned on the page"""
        result = {
            'found': False,
            'provider_mention': False,
            'evidence': []
        }

        # Search for Triple Cherry terms
        search_results = self.search_text_in_page(html, self.search_terms)

        if search_results['found']:
            result['found'] = True
            result['evidence'] = search_results['evidence'][:3]  # Limit evidence

            # Check if it's in a provider context
            for pattern in self.provider_patterns:
                provider_elements = self.find_elements_by_pattern(soup, pattern)
                if provider_elements:
                    result['provider_mention'] = True
                    break

        return result

    def _detect_games(self, html: str, soup, page_url: str) -> Dict:
        """Detect specific Triple Cherry games on the page"""
        detected = {}

        for game_title, aliases in self.all_game_aliases.items():
            # Search for game title and aliases
            for alias in aliases:
                # Create flexible pattern
                pattern = re.escape(alias)
                if re.search(pattern, html, re.IGNORECASE):
                    detected[game_title] = {
                        'found_as': alias,
                        'url': None
                    }

                    # Try to find game-specific URL
                    game_links = self.extract_game_links(soup, page_url, [alias])
                    if game_links:
                        detected[game_title]['url'] = list(game_links.values())[0]

                    break  # Found this game, move to next

        return detected

    def _analyze_results(self, result: Dict) -> Dict:
        """Perform additional analysis on the results"""

        # Categorize casino by coverage
        num_games = len(result['detected_games'])

        if num_games == 0:
            result['coverage_category'] = 'none'
        elif num_games <= 2:
            result['coverage_category'] = 'partial'
        elif num_games <= 5:
            result['coverage_category'] = 'moderate'
        else:
            result['coverage_category'] = 'strong'

        # Detect potential issues
        issues = []

        if result['access_status'] in ['blocked', 'timeout']:
            issues.append(f"Access issue: {result['access_status']}")

        if result['tripleCherryFound'] == 'yes' and not result['provider_mention']:
            issues.append("Games found but provider not listed")

        if result['provider_mention'] and len(result['detected_games']) == 0:
            issues.append("Provider listed but no games detected")

        if result['detected_games'] and not result['game_page_urls']:
            issues.append("Games detected but no direct URLs found")

        result['issues'] = issues

        # Risk assessment
        if issues:
            if result['access_status'] in ['blocked', 'timeout', 'error']:
                result['risk_level'] = 'high'
            elif 'Games found but provider not listed' in issues:
                result['risk_level'] = 'medium'
            else:
                result['risk_level'] = 'low'
        else:
            result['risk_level'] = 'none'

        return result

    def search_casino(self, casino_url: str, search_term: str) -> Optional[str]:
        """
        Perform search on casino website

        Args:
            casino_url: Base casino URL
            search_term: Term to search for

        Returns:
            HTML of search results or None
        """
        # Common search URL patterns
        search_patterns = [
            f"{casino_url}/search?q={search_term}",
            f"{casino_url}/search?query={search_term}",
            f"{casino_url}/games/search?q={search_term}",
            f"{casino_url}/?s={search_term}",
        ]

        for search_url in search_patterns:
            html, status, _ = self.fetch_page(search_url)
            if html and status == 'online':
                return html

        return None
