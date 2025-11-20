#!/usr/bin/env python3
"""
Test Browser Scraper on 5 Casinos
Quick validation before full scan
"""

import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from scrapers.playwright_scraper import PlaywrightScraper
from scrapers.browser_crawler import BrowserCrawler

async def main():
    logger.info("=" * 60)
    logger.info("TESTING BROWSER-BASED SCRAPER")
    logger.info("Testing on 5 casinos with JavaScript execution")
    logger.info("=" * 60)

    # Load configuration
    with open('config/scraper_config.json', 'r') as f:
        config = json.load(f)

    with open('config/triple_cherry_games.json', 'r') as f:
        games_data = json.load(f)

    with open('config/test_casinos.json', 'r') as f:
        test_data = json.load(f)

    # Create crawler
    crawler = BrowserCrawler(config, games_data, test_data)

    # Run scraping
    start_time = datetime.now()
    results = await crawler.crawl_all_async()
    end_time = datetime.now()

    duration = (end_time - start_time).total_seconds()

    # Analyze results
    total = len(results)
    accessible = sum(1 for r in results if r['access_status'] == 'online')
    with_games = sum(1 for r in results if r['tripleCherryFound'] == 'yes')
    total_games = sum(len(r['detected_games']) for r in results)

    logger.info("\n" + "=" * 60)
    logger.info("TEST RESULTS")
    logger.info("=" * 60)
    logger.info(f"Duration: {duration:.1f} seconds")
    logger.info(f"Casinos tested: {total}")
    logger.info(f"Accessible: {accessible}/{total} ({accessible/total*100:.1f}%)")
    logger.info(f"With Triple Cherry games: {with_games}/{total} ({with_games/total*100:.1f}%)")
    logger.info(f"Total games detected: {total_games}")
    logger.info("=" * 60)

    # Show detailed results
    logger.info("\nDETAILED RESULTS:")
    for r in results:
        status_emoji = "✅" if r['access_status'] == 'online' else "❌"
        games_emoji = "🎮" if r['tripleCherryFound'] == 'yes' else "  "
        logger.info(f"{status_emoji} {games_emoji} {r['casino_name']:20s} - {len(r['detected_games'])} games - {r['detection_method']}")
        if r['detected_games']:
            logger.info(f"     Games: {', '.join(r['detected_games'][:3])}")

    # Save results
    output_dir = Path('data/raw')
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f'test_browser_scan_{timestamp}.json'

    output = {
        'metadata': {
            'scan_type': 'browser_test',
            'scan_date': datetime.now().isoformat(),
            'duration_seconds': duration,
            'casinos_tested': total
        },
        'summary': {
            'total_casinos': total,
            'accessible': accessible,
            'with_triple_cherry': with_games,
            'penetration_rate': round(with_games/total*100, 2) if total > 0 else 0,
            'total_games_detected': total_games
        },
        'results': results
    }

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    logger.info(f"\n✅ Results saved to: {output_file}")

    # Compare with previous results
    logger.info("\n" + "=" * 60)
    logger.info("COMPARISON WITH PREVIOUS SCRAPER")
    logger.info("=" * 60)
    logger.info(f"Previous (Enhanced): 1.6% penetration on full scan")
    logger.info(f"New (Browser):       {with_games/total*100:.1f}% penetration on test")
    logger.info("=" * 60)

if __name__ == '__main__':
    asyncio.run(main())
