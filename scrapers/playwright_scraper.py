"""
Playwright Browser Scraper - Executes JavaScript for accurate game detection
"""

import asyncio
import re
import json
from typing import Dict, List, Optional
from playwright.async_api import async_playwright, Page, Browser
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class PlaywrightScraper:
    """Browser-based scraper using Playwright for JavaScript execution"""

    def __init__(self, config: Dict, games_data: Dict):
        """Initialize Playwright scraper"""
        self.config = config
        self.games_data = games_data
        self.games_list = [game['title'] for game in games_data.get('games', [])]
        self.all_game_aliases = self._build_game_aliases()
        self.timeout = config.get('scraping', {}).get('timeout', 30) * 1000  # Convert to ms
        self.browser = None
        self.context = None

    def _build_game_aliases(self) -> Dict[str, List[str]]:
        """Build comprehensive game alias mapping"""
        aliases_map = {}
        for game in self.games_data.get('games', []):
            title = game['title']
            all_names = [title] + game.get('aliases', [])

            # Add variations
            variations = []
            for name in all_names:
                variations.append(name)
                variations.append(name.lower())
                variations.append(name.replace(' ', ''))
                variations.append(name.replace(' ', '-'))
                variations.append(name.replace(' ', '_'))
                variations.append(re.sub(r'[^a-z0-9]', '', name.lower()))

            aliases_map[title] = list(set(variations))

        return aliases_map

    async def init_browser(self):
        """Initialize browser instance"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-proxy-server',
                '--disable-features=IsolateOrigins,site-per-process'
            ]
        )
        self.context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            bypass_csp=True,
            ignore_https_errors=True
        )

    async def close_browser(self):
        """Close browser instance"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def extract_casino_data(self, casino: Dict) -> Dict:
        """Extract data from casino using browser automation"""
        casino_url = casino['url']
        casino_name = casino['name']

        logger.info(f"🌐 BROWSER SCAN: {casino_name} ({casino_url})")

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
            'scan_timestamp': datetime.now().isoformat(),
            'pages_scanned': 0,
            'metadata': {},
            'detection_method': 'browser_automation'
        }

        try:
            page = await self.context.new_page()

            # Navigate to casino homepage
            try:
                response = await page.goto(casino_url, wait_until='networkidle', timeout=self.timeout)
                result['pages_scanned'] += 1

                if response and response.status == 200:
                    result['access_status'] = 'online'

                    # Wait for page to fully load
                    await page.wait_for_timeout(2000)  # 2 seconds for JS execution

                    # Get page content after JavaScript execution
                    content = await page.content()

                    # Detect games in rendered content
                    detected_games = self._detect_games_in_content(content)

                    if detected_games:
                        result['detected_games'].extend(detected_games)
                        result['tripleCherryFound'] = 'yes'
                        logger.info(f"  ✅ FOUND {len(detected_games)} games: {', '.join(list(detected_games)[:3])}")

                    # Check subpages
                    for path in ['/games', '/slots', '/casino', '/providers']:
                        try:
                            subpage_url = casino_url.rstrip('/') + path
                            await page.goto(subpage_url, wait_until='networkidle', timeout=self.timeout)
                            await page.wait_for_timeout(1500)

                            result['pages_scanned'] += 1
                            subcontent = await page.content()

                            subpage_games = self._detect_games_in_content(subcontent)
                            if subpage_games:
                                for game in subpage_games:
                                    if game not in result['detected_games']:
                                        result['detected_games'].append(game)
                                        result['tripleCherryFound'] = 'yes'
                        except Exception as e:
                            # Subpage failed, continue
                            pass

                    # Check for Triple Cherry provider mention
                    if 'triple cherry' in content.lower() or 'triplecherry' in content.lower():
                        result['provider_mention'] = True
                        result['evidence'].append("Triple Cherry mentioned in page content")

                    if result['detected_games']:
                        result['detected_games'] = sorted(list(set(result['detected_games'])))
                        logger.info(f"  ✅ TOTAL: {len(result['detected_games'])} games found")
                    else:
                        logger.info(f"  ❌ No games found")

                else:
                    result['access_status'] = f'http_error_{response.status if response else "unknown"}'
                    logger.warning(f"  ⚠️ HTTP {response.status if response else 'unknown'}")

            except asyncio.TimeoutError:
                result['access_status'] = 'timeout'
                logger.warning(f"  ⚠️ Timeout")
            except Exception as e:
                result['access_status'] = 'error'
                logger.warning(f"  ⚠️ Error: {str(e)[:50]}")

            await page.close()

        except Exception as e:
            result['access_status'] = 'error'
            result['notes'].append(f"Browser error: {str(e)[:100]}")
            logger.error(f"  ❌ Browser error: {str(e)[:50]}")

        # Analyze results
        result = self._analyze_results(result)
        return result

    def _detect_games_in_content(self, content: str) -> List[str]:
        """Detect games in page content"""
        found_games = []
        content_lower = content.lower()

        for game_title, aliases in self.all_game_aliases.items():
            for alias in aliases:
                if alias.lower() in content_lower:
                    found_games.append(game_title)
                    break

        return found_games

    def _analyze_results(self, result: Dict) -> Dict:
        """Analyze and categorize results"""
        num_games = len(result['detected_games'])

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
        if result['access_status'] in ['blocked', 'timeout', 'error']:
            issues.append(f"Access issue: {result['access_status']}")

        if result['tripleCherryFound'] == 'yes' and not result['provider_mention']:
            issues.append("Games found but provider not listed")

        if result['provider_mention'] and num_games == 0:
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
