"""
Browser-Based Casino Crawler - Uses Playwright for JavaScript execution
"""

import json
import os
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from tqdm import tqdm
import logging

from .playwright_scraper import PlaywrightScraper

logger = logging.getLogger(__name__)


class BrowserCrawler:
    """Manages browser-based crawling with Playwright"""

    def __init__(self, config: Dict, games_data: Dict, casinos_data: Dict):
        """Initialize browser crawler"""
        self.config = config
        self.games_data = games_data
        self.casinos_data = casinos_data
        self.casinos_list = casinos_data.get('casinos', [])
        # Reduce concurrent browsers to avoid overwhelming system
        self.concurrent_browsers = min(config.get('scraping', {}).get('parallel_workers', 5), 5)
        self.results = []

    async def crawl_all_async(self, limit: Optional[int] = None, filter_region: Optional[str] = None) -> List[Dict]:
        """Crawl all casinos using browser automation"""
        # Filter casinos
        casinos_to_crawl = self.casinos_list

        if filter_region:
            casinos_to_crawl = [c for c in casinos_to_crawl if c.get('region') == filter_region]

        if limit:
            casinos_to_crawl = casinos_to_crawl[:limit]

        logger.info(f"Starting BROWSER crawl of {len(casinos_to_crawl)} casinos with {self.concurrent_browsers} concurrent browsers")

        # Create semaphore to limit concurrent browsers
        semaphore = asyncio.Semaphore(self.concurrent_browsers)

        async def crawl_with_semaphore(casino):
            async with semaphore:
                return await self._crawl_single_casino(casino)

        # Create progress bar
        with tqdm(total=len(casinos_to_crawl), desc="Browser crawling") as pbar:
            # Process in batches
            tasks = []
            for casino in casinos_to_crawl:
                task = crawl_with_semaphore(casino)
                tasks.append(task)

            # Gather results
            for coro in asyncio.as_completed(tasks):
                try:
                    result = await coro
                    self.results.append(result)
                except Exception as e:
                    logger.error(f"Error in crawler: {str(e)}")
                finally:
                    pbar.update(1)

        logger.info(f"Browser crawl completed. Processed {len(self.results)} casinos")
        return self.results

    async def _crawl_single_casino(self, casino: Dict) -> Dict:
        """Crawl single casino with browser"""
        scraper = PlaywrightScraper(self.config, self.games_data)

        try:
            await scraper.init_browser()
            result = await scraper.extract_casino_data(casino)
            return result
        except Exception as e:
            logger.error(f"Error crawling {casino['name']}: {str(e)}")
            return {
                'website_url': casino['url'],
                'casino_name': casino['name'],
                'access_status': 'error',
                'error': str(e),
                'tripleCherryFound': 'unknown',
                'detected_games': [],
                'scan_timestamp': datetime.now().isoformat()
            }
        finally:
            await scraper.close_browser()

    def crawl_all(self, limit: Optional[int] = None, filter_region: Optional[str] = None) -> List[Dict]:
        """Synchronous wrapper for async crawl"""
        return asyncio.run(self.crawl_all_async(limit, filter_region))

    def save_results(self, output_dir: str, filename: str = None) -> str:
        """Save crawl results to JSON"""
        os.makedirs(output_dir, exist_ok=True)

        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"casino_data_BROWSER_{timestamp}.json"

        filepath = os.path.join(output_dir, filename)

        output = {
            'metadata': {
                'total_casinos_scanned': len(self.results),
                'scan_date': datetime.now().isoformat(),
                'total_games_in_catalog': len(self.games_data.get('games', [])),
                'scan_method': 'browser_automation_playwright',
                'note': 'Full browser automation with JavaScript execution'
            },
            'results': self.results
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        logger.info(f"Results saved to: {filepath}")
        return filepath

    def get_summary_stats(self) -> Dict:
        """Generate summary statistics"""
        if not self.results:
            return {}

        total = len(self.results)
        with_tc = sum(1 for r in self.results if r.get('tripleCherryFound') == 'yes')
        online = sum(1 for r in self.results if r.get('access_status') == 'online')

        all_games = []
        for r in self.results:
            all_games.extend(r.get('detected_games', []))

        unique_games = set(all_games)
        provider_mentions = sum(1 for r in self.results if r.get('provider_mention'))

        return {
            'total_casinos_scanned': total,
            'casinos_online': online,
            'casinos_with_triple_cherry': with_tc,
            'penetration_rate': round((with_tc / total * 100), 2) if total > 0 else 0,
            'unique_games_detected': len(unique_games),
            'games_detected_list': sorted(list(unique_games)),
            'provider_mentions': provider_mentions,
        }
