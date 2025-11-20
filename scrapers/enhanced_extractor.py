"""
Enhanced Data Extractor with JavaScript Support
Detects Triple Cherry games on modern casino websites
"""

import re
import json
from typing import Dict, List, Optional
from .base_scraper import BaseScraper
import logging

logger = logging.getLogger(__name__)


class EnhancedDataExtractor(BaseScraper):
    """Enhanced extractor with aggressive game detection"""

    def __init__(self, config: Dict, games_data: Dict):
        """Initialize the enhanced data extractor"""
        super().__init__(config)
        self.games_data = games_data
        self.games_list = [game['title'] for game in games_data.get('games', [])]
        self.all_game_aliases = self._build_game_aliases()
        self.detection_config = config.get('detection', {})
        self.search_terms = self.detection_config.get('search_terms', [])
        self.provider_patterns = self.detection_config.get('provider_patterns', [])
        self.common_paths = self.detection_config.get('common_paths', [])

    def _build_game_aliases(self) -> Dict[str, List[str]]:
        """Build comprehensive alias mapping with partial matches"""
        aliases_map = {}
        for game in self.games_data.get('games', []):
            title = game['title']
            all_names = [title] + game.get('aliases', [])

            # Add MANY more variations
            variations = set()
            for name in all_names:
                variations.add(name)
                variations.add(name.lower())
                variations.add(name.upper())
                variations.add(name.replace(' ', ''))
                variations.add(name.replace(' ', '-'))
                variations.add(name.replace(' ', '_'))
                variations.add(name.replace(' ', '.'))
                variations.add(re.sub(r'[^a-z0-9]', '', name.lower()))
                variations.add(re.sub(r'[^a-z0-9]', '-', name.lower()))

                # Add with "slot", "game" suffixes
                variations.add(f"{name.lower()}-slot")
                variations.add(f"{name.lower()}-game")
                variations.add(f"{name.lower()}slot")

                # For multi-word games, add partial matches
                words = name.split()
                if len(words) > 1:
                    # Add last significant word (e.g., "Crash" from "Goal Crash")
                    if len(words[-1]) > 3:
                        variations.add(words[-1].lower())
                    # Add combined last words
                    if len(words) >= 2:
                        variations.add(f"{words[-2].lower()}{words[-1].lower()}")
                        variations.add(f"{words[-2].lower()}-{words[-1].lower()}")

            aliases_map[title] = list(variations)

        return aliases_map

    def extract_casino_data(self, casino: Dict) -> Dict:
        """Extract data with enhanced detection"""
        casino_url = casino['url']
        casino_name = casino['name']

        logger.info(f"REAL SCAN: {casino_name} ({casino_url})")

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
            'metadata': {},
            'detection_method': 'none'
        }

        # Try homepage first
        html, status, metadata = self.fetch_page(casino_url)
        result['pages_scanned'] += 1

        if html:
            result['access_status'] = status

            # ENHANCED DETECTION - Multiple methods
            detected_games = set()

            # Method 1: Search in visible text
            games_method1 = self._detect_in_visible_text(html)
            if games_method1:
                detected_games.update(games_method1)
                result['detection_method'] = 'visible_text'
                logger.info(f"  → Found {len(games_method1)} games in visible text")

            # Method 2: Search in script tags and JSON
            games_method2 = self._detect_in_scripts(html)
            if games_method2:
                detected_games.update(games_method2)
                result['detection_method'] = 'script_tags'
                logger.info(f"  → Found {len(games_method2)} games in scripts")

            # Method 3: Search in data attributes
            games_method3 = self._detect_in_attributes(html)
            if games_method3:
                detected_games.update(games_method3)
                result['detection_method'] = 'html_attributes'
                logger.info(f"  → Found {len(games_method3)} games in attributes")

            # Method 4: Check common game pages
            if not detected_games:
                games_method4 = self._check_common_paths(casino_url)
                if games_method4:
                    detected_games.update(games_method4)
                    result['detection_method'] = 'subpage_scan'
                    result['pages_scanned'] += 3
                    logger.info(f"  → Found {len(games_method4)} games on subpages")

            # Update results
            if detected_games:
                result['tripleCherryFound'] = 'yes'
                result['detected_games'] = sorted(list(detected_games))
                result['evidence'].append(f"Detected using: {result['detection_method']}")
                logger.info(f"  ✅ FOUND {len(detected_games)} games: {', '.join(list(detected_games)[:3])}...")
            else:
                logger.info(f"  ❌ No games found")

            # Check for provider mention
            tc_found = self._check_triple_cherry_mention(html)
            if tc_found['found']:
                result['provider_mention'] = tc_found.get('provider_mention', False)
                result['evidence'].extend(tc_found.get('evidence', []))

        else:
            result['access_status'] = status
            result['notes'].append(f"Could not access website: {status}")
            logger.warning(f"  ⚠️ Access failed: {status}")

        # Analyze results
        result = self._analyze_results(result)

        return result

    def _detect_in_visible_text(self, html: str) -> List[str]:
        """Detect games in visible text content"""
        found_games = []

        # Parse HTML
        soup = self.parse_html(html)
        text_content = soup.get_text().lower()

        # Search for each game
        for game_title, aliases in self.all_game_aliases.items():
            for alias in aliases:
                if alias.lower() in text_content:
                    found_games.append(game_title)
                    break

        return found_games

    def _detect_in_scripts(self, html: str) -> List[str]:
        """Detect games in JavaScript and JSON data - ENHANCED"""
        found_games = []

        soup = self.parse_html(html)

        # Search in script tags
        script_tags = soup.find_all('script')
        for script in script_tags:
            script_content = script.string
            if script_content:
                script_lower = script_content.lower()

                # Try to parse as JSON if it looks like JSON
                if '{' in script_content and ('"games"' in script_lower or '"providers"' in script_lower):
                    try:
                        json_data = json.loads(script_content)
                        # Recursively search JSON structure
                        found_games.extend(self._search_json_structure(json_data))
                    except:
                        pass

                # Check each game alias
                for game_title, aliases in self.all_game_aliases.items():
                    for alias in aliases:
                        if len(alias) >= 4 and alias.lower() in script_lower:
                            found_games.append(game_title)
                            break

        # Also check for JSON-LD schemas
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                json_data = json.loads(script.string)
                found_games.extend(self._search_json_structure(json_data))
            except:
                pass

        return list(set(found_games))

    def _search_json_structure(self, obj, depth=0) -> List[str]:
        """Recursively search JSON structure for game names"""
        if depth > 10:  # Prevent infinite recursion
            return []

        found = []

        if isinstance(obj, dict):
            for key, value in obj.items():
                # Check keys and values
                key_lower = str(key).lower()
                value_str = str(value).lower()

                for game_title, aliases in self.all_game_aliases.items():
                    for alias in aliases:
                        if len(alias) >= 4:
                            if alias.lower() in key_lower or alias.lower() in value_str:
                                found.append(game_title)

                # Recurse into nested structures
                if isinstance(value, (dict, list)):
                    found.extend(self._search_json_structure(value, depth + 1))

        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    found.extend(self._search_json_structure(item, depth + 1))
                else:
                    item_str = str(item).lower()
                    for game_title, aliases in self.all_game_aliases.items():
                        for alias in aliases:
                            if len(alias) >= 4 and alias.lower() in item_str:
                                found.append(game_title)

        return list(set(found))

    def _detect_in_attributes(self, html: str) -> List[str]:
        """Detect games in HTML data attributes"""
        found_games = []

        soup = self.parse_html(html)

        # Search in all tags with data attributes
        all_tags = soup.find_all(True)  # All tags
        for tag in all_tags:
            # Check all attributes
            for attr_name, attr_value in tag.attrs.items():
                if isinstance(attr_value, str):
                    attr_lower = attr_value.lower()

                    # Check each game
                    for game_title, aliases in self.all_game_aliases.items():
                        for alias in aliases:
                            if alias.lower() in attr_lower:
                                found_games.append(game_title)
                                break

        return found_games

    def _check_common_paths(self, base_url: str) -> List[str]:
        """Check common paths for games - EXPANDED"""
        found_games = []

        # EXPANDED path list
        paths_to_check = [
            '/games', '/slots', '/casino', '/providers',
            '/games/slots', '/casino/games', '/slots/all',
            '/game-providers', '/software', '/game-library',
            '/slots/providers', '/casino/providers', '/games/providers',
            '/triple-cherry', '/triplecherry', '/games/triple-cherry',
            '/api/games', '/games.json', '/api/providers'
        ]

        for path in paths_to_check:
            url = base_url.rstrip('/') + path
            html, status, _ = self.fetch_page(url)

            if html and status == 'online':
                # Check using all detection methods
                games = set()
                games.update(self._detect_in_visible_text(html))
                games.update(self._detect_in_scripts(html))
                games.update(self._detect_in_attributes(html))
                found_games.extend(list(games))

        return list(set(found_games))

    def _check_triple_cherry_mention(self, html: str) -> Dict:
        """Check if Triple Cherry is mentioned"""
        result = {
            'found': False,
            'provider_mention': False,
            'evidence': []
        }

        # Search for Triple Cherry terms
        search_results = self.search_text_in_page(html, self.search_terms)

        if search_results['found']:
            result['found'] = True
            result['evidence'] = search_results['evidence'][:2]

            # Check if it's in provider context
            soup = self.parse_html(html)
            for pattern in self.provider_patterns:
                provider_elements = self.find_elements_by_pattern(soup, pattern)
                if provider_elements:
                    result['provider_mention'] = True
                    break

        return result

    def _analyze_results(self, result: Dict) -> Dict:
        """Analyze results and categorize"""

        num_games = len(result['detected_games'])

        # Coverage category
        if num_games == 0:
            result['coverage_category'] = 'none'
        elif num_games <= 2:
            result['coverage_category'] = 'partial'
        elif num_games <= 5:
            result['coverage_category'] = 'moderate'
        else:
            result['coverage_category'] = 'strong'

        # Detect issues
        issues = []

        if result['access_status'] in ['blocked', 'timeout']:
            issues.append(f"Access issue: {result['access_status']}")

        if result['tripleCherryFound'] == 'yes' and not result['provider_mention']:
            issues.append("Games found but provider not listed")

        if result['provider_mention'] and len(result['detected_games']) == 0:
            issues.append("Provider listed but no games detected")

        result['issues'] = issues

        # Risk level
        if result['access_status'] in ['blocked', 'timeout', 'error']:
            result['risk_level'] = 'high'
        elif issues:
            result['risk_level'] = 'medium'
        else:
            result['risk_level'] = 'low' if num_games > 0 else 'none'

        return result
