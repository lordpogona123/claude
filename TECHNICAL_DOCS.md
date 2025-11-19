# Technical Documentation

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Main Application (main.py)                │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
        ┌───────▼────────┐          ┌──────▼─────────┐
        │   Scrapers     │          │   Analytics    │
        └───────┬────────┘          └──────┬─────────┘
                │                           │
    ┌───────────┼───────────┐      ┌────────┼────────┐
    │           │           │      │        │        │
┌───▼───┐  ┌───▼───┐  ┌───▼───┐  │   ┌────▼────┐  │
│ Base  │  │Casino │  │ Data  │  │   │  Data   │  │
│Scraper│  │Crawler│  │Extract│  │   │Processor│  │
└───────┘  └───────┘  └───────┘  │   └────┬────┘  │
                                  │        │        │
                            ┌─────▼────┐  ▼  ┌─────▼─────┐
                            │ Insights │     │  Export   │
                            │Generator │     │  Manager  │
                            └──────────┘     └───────────┘
                                    │             │
                                    └──────┬──────┘
                                           │
                                    ┌──────▼──────┐
                                    │  Dashboard  │
                                    │ (Streamlit) │
                                    └─────────────┘
```

## Module Documentation

### 1. Scrapers Module (`scrapers/`)

#### BaseScraper (`base_scraper.py`)

Base class providing core web scraping functionality.

**Key Methods:**

```python
fetch_page(url: str, method: str = 'GET') -> Tuple[Optional[str], str, Dict]
```
- Fetches a web page with retry logic
- Returns: (html_content, status, metadata)
- Handles timeouts, connection errors, redirects
- Implements rate limiting

```python
parse_html(html: str) -> BeautifulSoup
```
- Parses HTML using BeautifulSoup with lxml parser

```python
search_text_in_page(html: str, search_terms: List[str]) -> Dict
```
- Searches for multiple terms in page content
- Returns matches with context snippets

```python
extract_game_links(soup: BeautifulSoup, base_url: str, game_terms: List[str]) -> Dict[str, str]
```
- Extracts links to specific game pages
- Normalizes text for fuzzy matching

**Configuration:**
- Timeout: Configurable request timeout
- Retry attempts: Number of retries on failure
- Rate limiting: Delay between requests
- User agent: Custom user agent string

#### DataExtractor (`data_extractor.py`)

Extracts Triple Cherry specific data from casino websites.

**Key Methods:**

```python
extract_casino_data(casino: Dict) -> Dict
```
- Main extraction method
- Crawls multiple pages per casino
- Returns structured result dictionary

```python
_check_triple_cherry_mention(html: str, soup) -> Dict
```
- Checks for TC brand mentions
- Identifies provider listing
- Returns evidence snippets

```python
_detect_games(html: str, soup, page_url: str) -> Dict
```
- Detects specific TC games
- Uses game aliases for flexible matching
- Finds game-specific URLs

```python
_analyze_results(result: Dict) -> Dict
```
- Post-processing analysis
- Categorizes coverage (none/partial/moderate/strong)
- Assesses risk levels

**Output Structure:**

```json
{
  "website_url": "string",
  "casino_name": "string",
  "region": "string",
  "country": "string",
  "access_status": "online|blocked|timeout|error",
  "tripleCherryFound": "yes|no",
  "detected_games": ["Game1", "Game2"],
  "game_page_urls": {"Game1": "url"},
  "provider_mention": true|false,
  "evidence": ["snippet1", "snippet2"],
  "notes": ["note1"],
  "coverage_category": "none|partial|moderate|strong",
  "risk_level": "none|low|medium|high",
  "issues": ["issue1"]
}
```

#### CasinoCrawler (`casino_crawler.py`)

Orchestrates parallel crawling across multiple casinos.

**Key Methods:**

```python
crawl_all(limit: Optional[int], filter_region: Optional[str]) -> List[Dict]
```
- Parallel crawling using ThreadPoolExecutor
- Progress bar with tqdm
- Error handling per casino

```python
save_results(output_dir: str, filename: str) -> str
```
- Saves results to JSON
- Includes metadata

```python
get_summary_stats() -> Dict
```
- Generates quick statistics
- Penetration rates, game counts, etc.

**Threading:**
- Configurable worker count
- Thread-safe result collection
- Individual extractor per thread

### 2. Analytics Module (`analytics/`)

#### DataProcessor (`data_processor.py`)

Processes and aggregates scraped data.

**Key Methods:**

```python
create_operator_dataframe() -> pd.DataFrame
```
- Converts raw data to pandas DataFrame
- Useful for data manipulation

```python
create_game_matrix() -> pd.DataFrame
```
- Creates games × casinos presence matrix
- Binary values (0 = absent, 1 = present)

```python
calculate_regional_stats() -> Dict
```
- Aggregates data by region
- Calculates penetration rates
- Lists countries per region

```python
calculate_game_popularity() -> List[Dict]
```
- Ranks games by appearance frequency
- Calculates coverage percentages

```python
identify_risks() -> Dict
```
- Categorizes risks:
  - Access issues (blocked, timeout)
  - Technical issues (missing URLs, poor listing)
  - Commercial issues (provider without games)
  - High-risk casinos

```python
calculate_coverage_quality() -> Dict
```
- Groups casinos by coverage category
- Identifies upsell opportunities

**Data Structures:**

Regional Stats:
```json
{
  "EU": {
    "total_casinos": 100,
    "with_triple_cherry": 75,
    "penetration_rate": 75.0,
    "total_games_detected": 450,
    "countries": ["Malta", "Spain", "UK"],
    "casinos": ["Casino1", "Casino2"]
  }
}
```

#### InsightsGenerator (`insights_generator.py`)

Generates business insights and recommendations.

**Key Methods:**

```python
generate_executive_summary() -> str
```
- Text-based executive summary
- Key metrics and highlights

```python
generate_key_insights() -> List[str]
```
- Automated insight detection
- Identifies trends and anomalies
- Highlights opportunities

```python
generate_recommendations() -> List[Dict]
```
- Actionable recommendations
- Prioritized (HIGH/MEDIUM/LOW)
- Includes next steps

```python
generate_opportunities() -> List[Dict]
```
- Market opportunity identification
- New partnerships
- Geographic expansion

**Insight Logic:**

- Penetration thresholds:
  - <30%: Low penetration warning
  - 30-60%: Moderate
  - >60%: Strong

- Coverage analysis:
  - Strong partners: 5+ games
  - Upsell targets: 1-2 games
  - New opportunities: 0 games

#### ExportManager (`export_manager.py`)

Handles all data exports.

**Export Methods:**

```python
export_operator_list(output_path: str) -> str
```
- Complete casino list with all fields
- CSV format

```python
export_game_matrix(output_path: str) -> str
```
- Game presence matrix
- Yes/No format for readability

```python
export_risk_report(output_path: str) -> str
```
- All identified risks
- Categorized and prioritized

```python
export_game_popularity(output_path: str) -> str
```
- Game rankings
- Sorted by appearance count

```python
export_regional_summary(output_path: str) -> str
```
- Regional statistics summary

```python
export_to_excel(output_path: str) -> str
```
- Multi-sheet Excel workbook
- Includes all data types

**Excel Structure:**
- Sheet 1: Summary
- Sheet 2: Operators
- Sheet 3: Regional
- Sheet 4: Game Popularity
- Sheet 5: Risks

### 3. Dashboard (`dashboard/`)

#### Streamlit Application (`app.py`)

Interactive web dashboard using Streamlit and Plotly.

**Key Functions:**

```python
load_latest_data() -> Tuple[Dict, List]
```
- Loads most recent processed data
- Returns (processed_data, raw_results)

```python
create_coverage_gauge(value: float, title: str) -> go.Figure
```
- Gauge chart for percentage metrics
- Color-coded ranges

```python
create_regional_chart(regional_stats: Dict) -> go.Figure
```
- Grouped bar chart
- Total vs TC presence

```python
create_game_popularity_chart(game_popularity: List) -> go.Figure
```
- Horizontal bar chart
- Color-coded by coverage percentage

```python
create_coverage_pie(coverage_quality: Dict) -> go.Figure
```
- Donut chart
- Coverage quality distribution

```python
create_country_heatmap(country_dist: Dict) -> go.Figure
```
- Heatmap visualization
- Top countries by penetration

**Dashboard Layout:**

1. Header with branding
2. Executive summary metrics (4 columns)
3. Penetration gauges (3 columns)
4. Regional charts (2 columns)
5. Game popularity chart
6. Country heatmap
7. Key insights section
8. Recommendations (expandable)
9. Risk analysis (2 columns)
10. Detailed data tables (tabs)

**Interactivity:**
- Sidebar filters
- Downloadable CSVs
- Expandable sections
- Responsive layout

## Data Flow

### 1. Scraping Flow

```
Config Files → CasinoCrawler → ThreadPoolExecutor
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
              DataExtractor     DataExtractor     DataExtractor
                    │                 │                 │
              BaseScraper        BaseScraper       BaseScraper
                    │                 │                 │
                HTTP Requests   HTTP Requests   HTTP Requests
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      │
                              Results Collection
                                      │
                            Save to data/raw/
```

### 2. Analysis Flow

```
data/raw/casino_data_*.json
         │
    DataProcessor
         │
    ┌────┴────────────────┐
    │                     │
Regional Stats      Game Rankings
    │                     │
Coverage Quality    Risk Analysis
    │                     │
    └────┬────────────────┘
         │
   Processed Data
         │
  InsightsGenerator
         │
   ┌─────┴─────┐
   │           │
Insights   Recommendations
   │           │
   └─────┬─────┘
         │
Save to data/processed/
```

### 3. Export Flow

```
data/processed/processed_*.json
         │
   ExportManager
         │
    ┌────┴──────────┐
    │               │
CSV Exports    Excel Export
    │               │
    └────┬──────────┘
         │
Save to outputs/exports/
```

## Performance Considerations

### Scraping Performance

**Parallel Workers:**
- Default: 10 workers
- Recommended: 5-15 (depends on network)
- Too many: May trigger rate limits
- Too few: Slow completion

**Memory Usage:**
- ~50MB per worker
- HTML caching disabled by default
- Results accumulated in memory

**Network:**
- Average 2-3 requests per casino
- ~30s total per casino (including delays)
- 600 casinos ≈ 30-60 minutes with 10 workers

### Dashboard Performance

**Data Loading:**
- JSON parsing: O(n) where n = file size
- Caching: None (reloads on refresh)
- Recommendation: <1000 casinos for smooth UI

**Chart Rendering:**
- Plotly: Client-side rendering
- Interactive charts may lag with >500 data points
- Use sampling for very large datasets

## Error Handling

### Network Errors

```python
try:
    html, status, metadata = fetch_page(url)
except requests.exceptions.Timeout:
    # Retry with exponential backoff
except requests.exceptions.ConnectionError:
    # Mark as unreachable
```

### Data Errors

- Missing required fields: Use defaults
- Invalid JSON: Skip and log error
- Encoding issues: Force UTF-8

### Graceful Degradation

- Single casino failure: Continue with others
- Missing configuration: Use defaults
- No data available: Show helpful message

## Testing

### Unit Tests

```bash
pytest tests/
```

### Integration Tests

```bash
# Test with sample data
python scripts/generate_sample_data.py
python main.py --analyze
python main.py --export
```

### Manual Testing

```bash
# Test single region
python main.py --scrape --region EU --limit 5

# Verify outputs
ls -la data/raw/
ls -la data/processed/
ls -la outputs/exports/
```

## Extending the System

### Adding New Scrapers

1. Subclass `BaseScraper`
2. Implement custom extraction logic
3. Register in `CasinoCrawler`

### Adding New Analytics

1. Add methods to `DataProcessor`
2. Update `InsightsGenerator` logic
3. Add to `ExportManager`
4. Create dashboard visualization

### Adding New Visualizations

1. Create chart function in `dashboard/app.py`
2. Add to layout
3. Wire up data source

### Custom Integrations

All data is JSON - easy to integrate:

```python
import json

# Load processed data
with open('data/processed/processed_*.json') as f:
    data = json.load(f)

# Your custom logic here
```

## Security Considerations

### Web Scraping Ethics

- Respect `robots.txt`
- Implement rate limiting
- Use appropriate user agent
- Don't overload servers

### Data Privacy

- No personal data collected
- Public website information only
- GDPR compliant (public data)

### API Keys / Credentials

- None required for basic scraping
- If using proxies: Store in `.env` file
- Never commit credentials

## Maintenance

### Regular Updates

1. Update casino list monthly
2. Update games catalog on new releases
3. Review and tune configuration
4. Archive old data files

### Monitoring

- Check logs for patterns
- Review error rates
- Monitor penetration trends
- Track new opportunities

### Optimization

- Tune parallel workers
- Adjust retry logic
- Update search patterns
- Optimize query paths

## Troubleshooting

See QUICKSTART.md for common issues and solutions.

## API Reference

See inline docstrings in each module for detailed API documentation.
