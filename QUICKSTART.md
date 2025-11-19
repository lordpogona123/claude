# Quick Start Guide

Get up and running with Triple Cherry Casino Analytics in 5 minutes.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- (Optional) Virtual environment tool (venv, conda, etc.)

## Setup Instructions

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 2. Configure Your Casino List

You have two options:

#### Option A: Import from CSV

1. Fill out the `casino_list_template.csv` file with your casino data
2. Run the import script:

```bash
python scripts/import_casino_list.py casino_list_template.csv
```

Expected CSV format:
```csv
name,url,region,country,priority
Casino Name,https://casino-url.com,EU,Malta,high
```

#### Option B: Edit JSON Directly

Edit `config/casino_list.json` manually:

```json
{
  "casinos": [
    {
      "name": "Casino Name",
      "url": "https://casino-url.com",
      "region": "EU",
      "country": "Malta",
      "priority": "high"
    }
  ]
}
```

### 3. Update Triple Cherry Games List

Edit `config/triple_cherry_games.json` with your complete game catalog:

```json
{
  "games": [
    {
      "title": "Game Name",
      "aliases": ["GameName", "game-name"],
      "release_date": "2024-01-15",
      "game_type": "slot"
    }
  ]
}
```

## Usage

### Quick Test with Sample Data

Test the system without scraping real websites:

```bash
# Generate sample data
python scripts/generate_sample_data.py

# Analyze the sample data
python main.py --analyze

# Export reports
python main.py --export

# Launch dashboard
python main.py --dashboard
```

### Full Production Run

#### Step 1: Scrape Casino Websites

```bash
# Scrape all casinos in your list
python main.py --scrape

# Or scrape just 10 casinos for testing
python main.py --scrape --limit 10

# Or scrape specific region
python main.py --scrape --region EU
```

This will create a JSON file in `data/raw/` with all scraping results.

#### Step 2: Analyze Data

```bash
python main.py --analyze
```

This processes the raw data and generates:
- Summary statistics
- Regional analysis
- Game popularity rankings
- Risk assessments
- Business insights

Results are saved to `data/processed/`

#### Step 3: Export Reports

```bash
python main.py --export
```

This generates:
- CSV files for each analysis
- Excel workbook with all data
- Files saved to `outputs/exports/`

#### Step 4: View Dashboard

```bash
python main.py --dashboard
```

This launches an interactive web dashboard at `http://localhost:8501`

### One-Command Full Pipeline

Run everything at once:

```bash
python main.py --full
```

This will:
1. Scrape all casinos
2. Analyze the data
3. Export all reports

Then launch the dashboard with:
```bash
python main.py --dashboard
```

## Understanding the Output

### Dashboard Sections

1. **Executive Summary**
   - Key metrics at a glance
   - Total casinos, penetration rate, games detected

2. **Market Penetration**
   - Gauge charts showing coverage rates
   - Regional averages
   - Quality score

3. **Regional Distribution**
   - Bar charts by region
   - Coverage quality pie chart
   - Country heatmap

4. **Game Popularity**
   - Top 10 games by casino appearances
   - Percentage coverage

5. **Key Insights**
   - Automated insights based on data
   - Identifies opportunities and risks

6. **Recommendations**
   - Actionable recommendations
   - Prioritized by impact (High/Medium/Low)

7. **Risk Analysis**
   - Access issues (blocked, timeout)
   - Technical problems
   - Commercial concerns

8. **Detailed Tables**
   - Full operator list
   - Game popularity rankings
   - Regional summaries
   - Downloadable CSV exports

### Export Files

All exports are saved to `outputs/exports/`:

- `operator_list_YYYYMMDD_HHMMSS.csv` - Complete casino list with status
- `game_matrix_YYYYMMDD_HHMMSS.csv` - Matrix of games × casinos
- `risk_report_YYYYMMDD_HHMMSS.csv` - All identified risks
- `game_popularity_YYYYMMDD_HHMMSS.csv` - Game rankings
- `regional_summary_YYYYMMDD_HHMMSS.csv` - Regional statistics
- `triple_cherry_analytics_YYYYMMDD_HHMMSS.xlsx` - Excel workbook with all sheets

## Configuration Options

### Scraper Settings

Edit `config/scraper_config.json`:

```json
{
  "scraping": {
    "parallel_workers": 10,      // Number of concurrent scrapers
    "timeout": 30,               // Request timeout in seconds
    "retry_attempts": 3,         // Number of retries on failure
    "rate_limit_delay": 1        // Delay between requests
  }
}
```

### Search Terms

The system searches for these terms (configurable in `scraper_config.json`):
- "Triple Cherry"
- "3Cherry"
- "TCH"
- "TC Games"
- "TripleCherry"

## Troubleshooting

### Issue: "ModuleNotFoundError"

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "No raw data files found"

**Solution**: Run scraping first
```bash
python main.py --scrape
```

### Issue: "Access forbidden (403)" for many sites

**Solution**:
- Some casinos block automated requests
- Consider using proxies (configure in `scraper_config.json`)
- Reduce parallel workers
- Increase rate limit delay

### Issue: Dashboard shows no data

**Solution**: Make sure you've run analysis
```bash
python main.py --analyze
python main.py --dashboard
```

### Issue: Too slow to scrape 600+ sites

**Solution**:
- Increase parallel workers in config
- Run in batches by region
- Use more powerful hardware

## Advanced Usage

### Scrape Specific Casinos

Create a custom casino list and use it:

```bash
python scripts/import_casino_list.py my_custom_list.csv --output config/casino_list_custom.json
```

Then edit `main.py` to use the custom list.

### Schedule Regular Scans

Use cron (Linux/Mac) or Task Scheduler (Windows):

```bash
# Daily scan at 2 AM
0 2 * * * cd /path/to/project && python main.py --full
```

### Integration with Other Systems

All data is available as JSON:
- Raw scraping results: `data/raw/casino_data_*.json`
- Processed analytics: `data/processed/processed_*.json`

You can load these files in your own applications:

```python
import json

with open('data/processed/processed_YYYYMMDD_HHMMSS.json') as f:
    data = json.load(f)

# Access summary stats
summary = data['processed']['summary']
penetration_rate = summary['penetration_rate']

# Access insights
insights = data['insights']['key_insights']
```

## Best Practices

1. **Test First**: Always test with `--limit 10` before full run
2. **Respect Robots.txt**: Keep `respect_robots_txt: true` in config
3. **Rate Limiting**: Don't set `rate_limit_delay` too low
4. **Regular Updates**: Keep your casino list and games list updated
5. **Backup Data**: Archive `data/raw/` files periodically
6. **Review Insights**: Act on high-priority recommendations

## Getting Help

- Check `README.md` for detailed documentation
- Review configuration files in `config/`
- Examine sample data structure
- Check logs for error messages

## Next Steps

1. ✅ Set up environment and install dependencies
2. ✅ Configure your casino list
3. ✅ Update games catalog
4. ✅ Run test with sample data
5. ✅ Run small scrape (10-20 casinos)
6. ✅ Review results in dashboard
7. ✅ Adjust configuration as needed
8. ✅ Run full scrape
9. ✅ Generate executive reports
10. ✅ Share insights with team

You're ready to monitor Triple Cherry's market presence! 🍒
