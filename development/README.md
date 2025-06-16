# Development Tools & Analysis

This directory contains the development and analysis tools used to create the PyQwerty bot.

## 📊 Contents

- **scripts/**: Message crawling and style analysis tools
- **data/raw/**: Original Discord message exports
- **analysis/**: Style analysis results and reports
- **docs/**: Development documentation and change logs

## 🔧 Development Tools

### Message Crawler
```bash
python scripts/message_crawler.py
```

### Style Analysis
```bash
python scripts/deep_style_analyzer.py
python scripts/message_examples_extractor.py
```

### Testing
```bash
python test_bot.py
```

## 📁 File Structure

```
development/
├── scripts/
│   ├── message_crawler.py       # Discord message crawler
│   ├── deep_style_analyzer.py   # Comprehensive style analysis
│   └── message_examples_extractor.py  # Extract examples
├── data/
│   └── raw/                     # Original message exports
├── analysis/                    # Generated analysis results
├── docs/                        # Development documentation
└── test_bot.py                  # Component testing
```

## 🚀 Production Bot

The production bot is in the `/bot` directory and is deployed via Docker.
See the main DEPLOYMENT.md for production deployment instructions.
