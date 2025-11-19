# Triple Cherry Casino Analytics Platform

An advanced data extraction and analytics system for monitoring Triple Cherry's online slot game presence across 600+ casino websites worldwide.

## Overview

This platform provides:
- **Automated Web Scraping**: Crawls 600+ casino websites to detect Triple Cherry games
- **Data Extraction**: Structured extraction of game presence, provider mentions, and metadata
- **Executive Dashboard**: Visual analytics for market penetration and performance signals
- **Risk Detection**: Identifies technical and commercial risks across operators
- **Export Capabilities**: CSV/Excel reports for business intelligence

## Features

### Web Scraping & Data Extraction
- Multi-threaded crawling of casino websites
- Intelligent detection of Triple Cherry games across multiple page types
- Handles geo-blocking, dynamic content, and iframes
- Captures evidence (HTML snippets, screenshots)
- Structured JSON output per website

### Analytics & Insights
- Coverage overview (penetration rates, game distribution)
- Geographical distribution analysis
- Operator coverage quality metrics
- Game performance signals
- Technical and commercial risk detection

### Executive Dashboard
- Interactive visualizations (charts, heatmaps, gauges)
- Real-time filtering and drill-down capabilities
- Traffic-light risk indicators
- CEO-ready summary views
- Downloadable reports

## Project Structure

```
/
├── config/                  # Configuration files
│   ├── casino_list.json    # List of 600+ casino websites
│   ├── triple_cherry_games.json  # Triple Cherry game catalog
│   └── scraper_config.json # Scraper settings
├── scrapers/               # Web scraping modules
│   ├── base_scraper.py    # Base scraper class
│   ├── casino_crawler.py  # Multi-site crawler
│   └── data_extractor.py  # Data extraction logic
├── analytics/              # Data processing & analytics
│   ├── data_processor.py  # Data aggregation
│   ├── insights_generator.py  # Insights & recommendations
│   └── export_manager.py  # CSV/Excel exports
├── dashboard/              # Interactive dashboard
│   ├── app.py            # Streamlit dashboard
│   └── components/       # Dashboard components
├── data/                  # Data storage
│   ├── raw/              # Raw scraping results
│   └── processed/        # Processed analytics data
├── outputs/              # Generated outputs
│   ├── reports/          # Executive reports
│   └── exports/          # CSV/Excel files
└── main.py               # Main execution script
```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# For browser automation (optional, for JavaScript-heavy sites)
playwright install chromium
```

## Usage

### Quick Start

```bash
# Run full scraping + analytics + dashboard
python main.py --full

# Run scraping only
python main.py --scrape

# Generate dashboard from existing data
python main.py --dashboard

# Export reports only
python main.py --export
```

### Dashboard Access

```bash
# Launch interactive dashboard
streamlit run dashboard/app.py
```

The dashboard will open at `http://localhost:8501`

### Configuration

Edit `config/casino_list.json` to update the list of casino websites:

```json
{
  "casinos": [
    {
      "name": "Example Casino",
      "url": "https://example-casino.com",
      "region": "EU",
      "country": "Malta"
    }
  ]
}
```

Edit `config/triple_cherry_games.json` to update the game catalog:

```json
{
  "games": [
    {
      "title": "Cash Pig",
      "aliases": ["CashPig", "Cash-Pig"],
      "release_date": "2023-01-15"
    }
  ]
}
```

## Output Examples

### JSON Data Extract
```json
{
  "website_url": "https://example-casino.com",
  "access_status": "online",
  "tripleCherryFound": "yes",
  "detected_games": ["Cash Pig", "Power of Gods", "Egyptian Rebirth II"],
  "game_page_urls": {
    "Cash Pig": "https://example-casino.com/games/cash-pig",
    "Power of Gods": "https://example-casino.com/games/power-of-gods"
  },
  "provider_mention": true,
  "evidence": "<div class='provider'>Triple Cherry</div>",
  "notes": "Dynamic JS catalog, all games loaded via API"
}
```

### Dashboard Features
- **Coverage Overview**: Total sites scanned, penetration rate, unique games detected
- **Geo Distribution**: Regional heatmap with operator counts
- **Operator Quality**: Categorization by game count (partial vs strong presence)
- **Game Rankings**: Most frequently appearing games across casinos
- **Risk Indicators**: Sites with broken links, outdated versions, geo-blocks

## Key Metrics Tracked

- Total websites scanned
- Websites with Triple Cherry presence
- Total unique games detected
- Penetration rate (%)
- Regional distribution
- Provider mention rate
- Average games per operator
- Technical risks identified
- Commercial opportunities

## Advanced Features

### Parallel Scraping
Configurable worker threads for faster crawling:
```python
# In scraper_config.json
"parallel_workers": 10,
"timeout": 30,
"retry_attempts": 3
```

### Evidence Capture
Optional screenshot capture for visual verification:
```python
"capture_screenshots": true,
"screenshot_format": "png"
```

### GEO Handling
Automatic proxy rotation for geo-blocked sites:
```python
"use_proxies": true,
"proxy_regions": ["EU", "US", "LATAM"]
```

## Technical Stack

- **Web Scraping**: requests, BeautifulSoup, Selenium, Playwright
- **Data Processing**: pandas, numpy
- **Dashboard**: Streamlit, Plotly
- **Exports**: openpyxl, csv
- **Async Operations**: asyncio, aiohttp

## Maintenance

### Updating Casino List
```bash
python scripts/update_casino_list.py --import casinos.csv
```

### Re-scanning Specific Operators
```bash
python main.py --scrape --filter "region=EU"
python main.py --scrape --urls casino1.com,casino2.com
```

## Support & Documentation

For detailed documentation, see `/docs` folder.

For issues or feature requests, contact the development team.

## License

Internal use only - Triple Cherry proprietary.
