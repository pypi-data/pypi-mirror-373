# Clutch Scraper

A powerful CLI tool to scrape company reviews from Clutch.co with CSV output and graceful pause functionality.

## Features

- 🏢 Scrape companies from multiple categories (Development, Marketing, Design, IT Services)
- 📊 Export reviews to separate CSV files per company
- ⏸️ Graceful pause/stop with Ctrl+C (no data loss)
- 💾 Automatic progress saving
- 🚀 Easy CLI installation and usage
- 📈 Real-time progress tracking

## Installation

```bash
pip install clutch-scraper
```

## Usage

Simply run the command after installation:

```bash
clutch-scraper
```

The tool will guide you through:
1. Selecting a category and subcategory
2. Choosing number of companies to scrape
3. Automatic scraping with progress updates

### Pausing/Stopping

Press `Ctrl+C` at any time to gracefully stop the scraper. All scraped data will be saved to CSV files.

## Output

The tool creates a timestamped directory containing:
- Individual CSV files for each company's reviews
- Progress tracking file
- Structured data with reviewer information

### CSV Structure

Each company's CSV contains:
- `company_name`: Name of the company
- `company_url`: Clutch.co profile URL
- `title`: Review title
- `text`: Review content
- `reviewer_name`: Name of reviewer
- `reviewer_position`: Job title of reviewer  
- `reviewer_location`: Location of reviewer
- `scrape_timestamp`: When the data was scraped

## Example

```bash
$ clutch-scraper

==================================================
CLUTCH.CO COMPANY & REVIEWS SCRAPER
==================================================

Select a main category:
1. Development
2. Marketing
3. Design
4. IT Services

Enter category number: 1

Select from Development:
1. Web Developers
2. Software Developers
3. Mobile App Development
...
```

## Requirements

- Python 3.7+
- Internet connection
- Dependencies: cloudscraper, beautifulsoup4, pandas, lxml

## Development

### Local Installation

```bash
git clone https://github.com/yourusername/clutch-scraper
cd clutch-scraper
pip install -e .
```

### Building

```bash
python setup.py sdist bdist_wheel
```

## License

MIT License

## Disclaimer

This tool is for educational and research purposes. Please respect Clutch.co's robots.txt and terms of service. Use responsibly with appropriate delays between requests.