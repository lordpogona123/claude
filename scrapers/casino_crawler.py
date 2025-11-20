"""
Casino Crawler - Orchestrates scraping across multiple casino websites
"""

import json
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)

try:
    from .enhanced_extractor import EnhancedDataExtractor as DataExtractor
except ImportError:
    from .data_extractor import DataExtractor


class CasinoCrawler:
    """Manages parallel crawling of multiple casino websites"""

    def __init__(self, config: Dict, games_data: Dict, casinos_data: Dict):
        """
        Initialize the crawler

        Args:
            config: Scraper configuration
            games_data: Triple Cherry games data
            casinos_data: Casino list data
        """
        self.config = config
        self.games_data = games_data
        self.casinos_data = casinos_data
        self.casinos_list = casinos_data.get('casinos', [])
        self.parallel_workers = config.get('scraping', {}).get('parallel_workers', 5)
        self.results = []

    def crawl_all(self, limit: Optional[int] = None, filter_region: Optional[str] = None) -> List[Dict]:
        """
        Crawl all casinos in the list

        Args:
            limit: Optional limit on number of casinos to crawl
            filter_region: Optional region filter (EU, LATAM, Asia, etc.)

        Returns:
            List of extraction results
        """
        # Filter casinos if needed
        casinos_to_crawl = self.casinos_list

        if filter_region:
            casinos_to_crawl = [c for c in casinos_to_crawl if c.get('region') == filter_region]

        if limit:
            casinos_to_crawl = casinos_to_crawl[:limit]

        logger.info(f"Starting crawl of {len(casinos_to_crawl)} casinos with {self.parallel_workers} workers")

        # Parallel crawling
        with ThreadPoolExecutor(max_workers=self.parallel_workers) as executor:
            # Submit all tasks
            future_to_casino = {
                executor.submit(self._crawl_single_casino, casino): casino
                for casino in casinos_to_crawl
            }

            # Process completed tasks with progress bar
            with tqdm(total=len(casinos_to_crawl), desc="Crawling casinos") as pbar:
                for future in as_completed(future_to_casino):
                    casino = future_to_casino[future]
                    try:
                        result = future.result()
                        self.results.append(result)
                    except Exception as e:
                        logger.error(f"Error crawling {casino['name']}: {str(e)}")
                        # Add error result
                        self.results.append({
                            'website_url': casino['url'],
                            'casino_name': casino['name'],
                            'access_status': 'error',
                            'error': str(e),
                            'tripleCherryFound': 'unknown'
                        })
                    finally:
                        pbar.update(1)

        logger.info(f"Crawl completed. Processed {len(self.results)} casinos")
        return self.results

    def _crawl_single_casino(self, casino: Dict) -> Dict:
        """
        Crawl a single casino website

        Args:
            casino: Casino information dictionary

        Returns:
            Extraction result
        """
        extractor = DataExtractor(self.config, self.games_data)

        try:
            result = extractor.extract_casino_data(casino)
            result['scan_timestamp'] = datetime.now().isoformat()
            return result
        finally:
            extractor.close()

    def save_results(self, output_dir: str, filename: str = None) -> str:
        """
        Save crawl results to JSON file

        Args:
            output_dir: Directory to save results
            filename: Optional custom filename

        Returns:
            Path to saved file
        """
        os.makedirs(output_dir, exist_ok=True)

        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"casino_data_{timestamp}.json"

        filepath = os.path.join(output_dir, filename)

        # Prepare output data
        output = {
            'metadata': {
                'total_casinos_scanned': len(self.results),
                'scan_date': datetime.now().isoformat(),
                'total_games_in_catalog': len(self.games_data.get('games', [])),
            },
            'results': self.results
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        logger.info(f"Results saved to: {filepath}")
        return filepath

    def get_summary_stats(self) -> Dict:
        """
        Generate summary statistics from crawl results

        Returns:
            Dictionary of summary statistics
        """
        if not self.results:
            return {}

        total = len(self.results)
        with_tc = sum(1 for r in self.results if r.get('tripleCherryFound') == 'yes')
        online = sum(1 for r in self.results if r.get('access_status') == 'online')
        blocked = sum(1 for r in self.results if r.get('access_status') == 'blocked')
        timeout = sum(1 for r in self.results if r.get('access_status') == 'timeout')

        # Game detection
        all_games = []
        for r in self.results:
            all_games.extend(r.get('detected_games', []))

        unique_games = set(all_games)

        # Provider mentions
        provider_mentions = sum(1 for r in self.results if r.get('provider_mention'))

        # Coverage categories
        coverage_stats = {
            'none': sum(1 for r in self.results if r.get('coverage_category') == 'none'),
            'partial': sum(1 for r in self.results if r.get('coverage_category') == 'partial'),
            'moderate': sum(1 for r in self.results if r.get('coverage_category') == 'moderate'),
            'strong': sum(1 for r in self.results if r.get('coverage_category') == 'strong'),
        }

        # Risk levels
        risk_stats = {
            'none': sum(1 for r in self.results if r.get('risk_level') == 'none'),
            'low': sum(1 for r in self.results if r.get('risk_level') == 'low'),
            'medium': sum(1 for r in self.results if r.get('risk_level') == 'medium'),
            'high': sum(1 for r in self.results if r.get('risk_level') == 'high'),
        }

        return {
            'total_casinos_scanned': total,
            'casinos_online': online,
            'casinos_blocked': blocked,
            'casinos_timeout': timeout,
            'casinos_with_triple_cherry': with_tc,
            'penetration_rate': round((with_tc / total * 100), 2) if total > 0 else 0,
            'unique_games_detected': len(unique_games),
            'games_detected_list': sorted(list(unique_games)),
            'provider_mentions': provider_mentions,
            'provider_mention_rate': round((provider_mentions / total * 100), 2) if total > 0 else 0,
            'coverage_distribution': coverage_stats,
            'risk_distribution': risk_stats,
        }
