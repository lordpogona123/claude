#!/usr/bin/env python3
"""
Triple Cherry Casino Analytics Platform
Main execution script

Usage:
    python main.py --full              # Run complete pipeline
    python main.py --scrape            # Scrape only
    python main.py --analyze           # Analyze existing data
    python main.py --dashboard         # Launch dashboard
    python main.py --export            # Export reports only
"""

import argparse
import json
import os
import sys
from datetime import datetime
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import modules
from scrapers.casino_crawler import CasinoCrawler
from analytics.data_processor import DataProcessor
from analytics.insights_generator import InsightsGenerator
from analytics.export_manager import ExportManager


def load_config():
    """Load configuration files"""
    config_dir = Path(__file__).parent / 'config'

    try:
        with open(config_dir / 'scraper_config.json', 'r') as f:
            scraper_config = json.load(f)

        with open(config_dir / 'triple_cherry_games.json', 'r') as f:
            games_data = json.load(f)

        with open(config_dir / 'casino_list.json', 'r') as f:
            casinos_data = json.load(f)

        return scraper_config, games_data, casinos_data

    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in configuration file: {e}")
        sys.exit(1)


def run_scraping(config, games_data, casinos_data, limit=None, region=None):
    """Run the web scraping process"""
    logger.info("=" * 60)
    logger.info("STARTING WEB SCRAPING")
    logger.info("=" * 60)

    # Create crawler
    crawler = CasinoCrawler(config, games_data, casinos_data)

    # Crawl casinos
    results = crawler.crawl_all(limit=limit, filter_region=region)

    # Save results
    data_dir = Path(__file__).parent / 'data' / 'raw'
    filepath = crawler.save_results(str(data_dir))

    # Display summary
    stats = crawler.get_summary_stats()

    logger.info("\n" + "=" * 60)
    logger.info("SCRAPING SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total casinos scanned: {stats['total_casinos_scanned']}")
    logger.info(f"Casinos online: {stats['casinos_online']}")
    logger.info(f"Casinos with Triple Cherry: {stats['casinos_with_triple_cherry']}")
    logger.info(f"Penetration rate: {stats['penetration_rate']}%")
    logger.info(f"Unique games detected: {stats['unique_games_detected']}")
    logger.info(f"Provider mentions: {stats['provider_mentions']}")
    logger.info("=" * 60 + "\n")

    return filepath


def run_analysis(raw_data_path=None):
    """Run data analysis on scraped data"""
    logger.info("=" * 60)
    logger.info("STARTING DATA ANALYSIS")
    logger.info("=" * 60)

    # Load raw data
    if raw_data_path is None:
        # Find most recent raw data file
        data_dir = Path(__file__).parent / 'data' / 'raw'
        files = list(data_dir.glob('casino_data_*.json'))

        if not files:
            logger.error("No raw data files found. Run scraping first.")
            return None

        raw_data_path = max(files, key=lambda x: x.stat().st_ctime)

    logger.info(f"Loading data from: {raw_data_path}")

    with open(raw_data_path, 'r') as f:
        raw_data = json.load(f)

    # Process data
    processor = DataProcessor(raw_data)
    processed_data = processor.generate_processed_data()

    # Generate insights
    insights_gen = InsightsGenerator(processed_data, raw_data.get('results', []))
    insights = insights_gen.generate_full_report()
    insights['generated_at'] = datetime.now().isoformat()

    # Combine all data
    output = {
        'metadata': {
            'scan_date': raw_data.get('metadata', {}).get('scan_date', ''),
            'analysis_date': datetime.now().isoformat(),
            'source_file': str(raw_data_path)
        },
        'processed': processed_data,
        'insights': insights
    }

    # Save processed data
    processed_dir = Path(__file__).parent / 'data' / 'processed'
    processed_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    processed_path = processed_dir / f'processed_{timestamp}.json'

    with open(processed_path, 'w') as f:
        json.dump(output, f, indent=2)

    logger.info(f"Processed data saved to: {processed_path}")

    # Print executive summary
    print("\n" + insights['executive_summary'])

    logger.info("=" * 60 + "\n")

    return processed_path


def run_export(processed_data_path=None):
    """Run export process"""
    logger.info("=" * 60)
    logger.info("EXPORTING REPORTS")
    logger.info("=" * 60)

    # Load processed data
    if processed_data_path is None:
        # Find most recent processed data file
        data_dir = Path(__file__).parent / 'data' / 'processed'
        files = list(data_dir.glob('processed_*.json'))

        if not files:
            logger.error("No processed data files found. Run analysis first.")
            return

        processed_data_path = max(files, key=lambda x: x.stat().st_ctime)

    logger.info(f"Loading data from: {processed_data_path}")

    with open(processed_data_path, 'r') as f:
        data = json.load(f)

    # Create export manager
    export_mgr = ExportManager(
        data.get('processed', {}),
        data.get('processed', {}).get('summary', {})  # Simplified for export
    )

    # Load raw results for detailed exports
    source_file = data.get('metadata', {}).get('source_file', '')
    if source_file and os.path.exists(source_file):
        with open(source_file, 'r') as f:
            raw_data = json.load(f)
            export_mgr.raw_results = raw_data.get('results', [])

    # Export all reports
    output_dir = Path(__file__).parent / 'outputs' / 'exports'
    exports = export_mgr.export_all(str(output_dir))

    logger.info("\nExported files:")
    for export_type, filepath in exports.items():
        logger.info(f"  - {export_type}: {filepath}")

    logger.info("=" * 60 + "\n")


def launch_dashboard():
    """Launch the Streamlit dashboard"""
    logger.info("=" * 60)
    logger.info("LAUNCHING DASHBOARD")
    logger.info("=" * 60)

    dashboard_path = Path(__file__).parent / 'dashboard' / 'app.py'

    logger.info(f"Starting Streamlit dashboard...")
    logger.info("Dashboard will open in your browser at http://localhost:8501")
    logger.info("Press Ctrl+C to stop the dashboard")
    logger.info("=" * 60 + "\n")

    import subprocess
    subprocess.run(['streamlit', 'run', str(dashboard_path)])


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description='Triple Cherry Casino Analytics Platform',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --full                 # Run complete pipeline
  python main.py --scrape --limit 10    # Scrape 10 casinos only
  python main.py --scrape --region EU   # Scrape EU casinos only
  python main.py --analyze              # Analyze existing data
  python main.py --export               # Export reports
  python main.py --dashboard            # Launch dashboard
        """
    )

    parser.add_argument('--full', action='store_true',
                        help='Run complete pipeline (scrape + analyze + export)')
    parser.add_argument('--scrape', action='store_true',
                        help='Run scraping only')
    parser.add_argument('--analyze', action='store_true',
                        help='Run analysis only (on existing data)')
    parser.add_argument('--export', action='store_true',
                        help='Export reports only')
    parser.add_argument('--dashboard', action='store_true',
                        help='Launch interactive dashboard')
    parser.add_argument('--limit', type=int,
                        help='Limit number of casinos to scrape')
    parser.add_argument('--region', type=str,
                        help='Filter casinos by region (EU, LATAM, Asia, etc.)')

    args = parser.parse_args()

    # Show help if no arguments
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    # Load configuration
    config, games_data, casinos_data = load_config()

    # Execute based on arguments
    try:
        if args.full:
            # Run complete pipeline
            logger.info("Running FULL pipeline: Scrape → Analyze → Export")
            raw_path = run_scraping(config, games_data, casinos_data, args.limit, args.region)
            processed_path = run_analysis(raw_path)
            run_export(processed_path)
            logger.info("✅ Full pipeline completed successfully!")
            logger.info("Run 'python main.py --dashboard' to view results")

        elif args.scrape:
            run_scraping(config, games_data, casinos_data, args.limit, args.region)
            logger.info("✅ Scraping completed!")
            logger.info("Run 'python main.py --analyze' to process the data")

        elif args.analyze:
            run_analysis()
            logger.info("✅ Analysis completed!")
            logger.info("Run 'python main.py --export' to generate reports")

        elif args.export:
            run_export()
            logger.info("✅ Export completed!")

        elif args.dashboard:
            launch_dashboard()

        else:
            parser.print_help()

    except KeyboardInterrupt:
        logger.info("\n\nProcess interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
