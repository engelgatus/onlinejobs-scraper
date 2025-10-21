# OnlineJobs.ph Job Scraper 🤖

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?logo=python&logoColor=white)](https://python.org)
[![GitHub Actions](https://img.shields.io/github/actions/workflow/status/engelgatus/onlinejobs-scraper/scraper.yml?branch=main&logo=github&label=Build)](https://github.com/engelgatus/onlinejobs-scraper/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Web Scraping](https://img.shields.io/badge/Web-Scraping-orange.svg?logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJMMTMuMDkgOC4yNkwyMSA5TDEzLjA5IDE1Ljc0TDEyIDIyTDEwLjkxIDE1Ljc0TDMgOUwxMC45MSA4LjI2TDEyIDJaIiBmaWxsPSJ3aGl0ZSIvPgo8L3N2Zz4K)](https://github.com/topics/web-scraping)
[![Discord](https://img.shields.io/badge/Discord-Integration-7289da.svg?logo=discord&logoColor=white)](https://discord.com)
[![SQLite](https://img.shields.io/badge/Database-SQLite-blue.svg?logo=sqlite&logoColor=white)](https://sqlite.org)
[![Ethical Scraping](https://img.shields.io/badge/Ethical-Scraping-green.svg?logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJMMTMuMDkgOC4yNkwyMSA5TDEzLjA5IDE1Ljc0TDEyIDIyTDEwLjkxIDE1Ljc0TDMgOUwxMC45MSA4LjI2TDEyIDJaIiBmaWxsPSJ3aGl0ZSIvPgo8L3N2Zz4K)](https://github.com/topics/ethical-scraping)

Automated job scraper that monitors OnlineJobs.ph for jobs matching your keywords and sends new findings to Discord twice daily.

> **⚠️ Production Note:** This is a portfolio showcase repository. The automated scheduling is disabled in this public version. For actual deployment, use a private repository with proper environment variables and GitHub Actions enabled.

## 🎯 Features

- **Smart Filtering**: Searches for jobs with keywords like "automation", "entry level", "associate", "admin", "operations"
- **Duplicate Prevention**: SQLite database tracks scraped jobs to avoid spam
- **Discord Integration**: Sends formatted job alerts with clickable links
- **Automated Schedule**: Runs twice daily via GitHub Actions (free tier)
- **Date Filtering**: Configurable lookback period (default: 5 days)
- **Production Ready**: Error handling, rate limiting, and robust parsing

## ⚡ Quick Setup

### 1. Create Discord Webhook

1. Go to your Discord server → Server Settings → Integrations
2. Click "Create Webhook" 
3. Name it "OnlineJobs Bot"
4. Select your "Command Center" channel
5. Copy the webhook URL

### 2. Set Up Repository

Run the directory setup command:
```bash
mkdir -p .github/workflows data && touch {scraper.py,database.py,discord_sender.py,config.py,main.py,requirements.txt,README.md,.github/workflows/scraper.yml,.gitignore}
```

Copy all the provided code into respective files.

### 3. Configure GitHub Repository

1. Push your code to GitHub
2. Go to Settings → Secrets and Variables → Actions
3. Click "New repository secret"
4. Name: `DISCORD_WEBHOOK_URL`
5. Value: Your Discord webhook URL from step 1

### 4. Test Locally (Optional)

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable
export DISCORD_WEBHOOK_URL="your_webhook_url_here"

# Test Discord connection
python main.py --test-discord

# Run a test scrape
python main.py --days 1
```

### 5. Enable GitHub Actions

1. Go to Actions tab in your repository  
2. Enable workflows if prompted
3. Manual test: Click "OnlineJobs.ph Scraper" → "Run workflow"

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Keywords to search for
KEYWORDS = [
    "automation",
    "entry level", 
    "associate",
    "admin",
    "operations"
]

# Days to look back on first scrape
DEFAULT_DAYS_BACK = 5

# Max pages to scrape per keyword  
MAX_PAGES_PER_KEYWORD = 2
```

## 📅 Schedule

The scraper runs automatically twice daily:
- **8:00 AM UTC** (4:00 AM EST)  
- **8:00 PM UTC** (4:00 PM EST)

To change the schedule, edit the cron expression in `.github/workflows/scraper.yml`:

```yaml
schedule:
  - cron: '0 8,20 * * *'  # 8 AM and 8 PM UTC
```

## 💾 Database Schema

SQLite database with these tables:

### jobs
- `job_id` - Unique identifier
- `title` - Job title
- `company` - Company name
- `url` - Direct job URL
- `description` - Job description
- `salary` - Salary info (if available)
- `job_type` - Full-time/Part-time
- `posted_date` - When job was posted
- `keyword_matched` - Which keyword matched
- `scraped_at` - When we scraped it
- `sent_to_discord` - Whether sent to Discord

### scrape_history  
- `scrape_date` - When scrape happened
- `jobs_found` - Total jobs found
- `new_jobs` - New jobs added
- `keywords_searched` - Keywords used

## 🔍 Commands

```bash
# Basic scrape (5 days back)
python main.py

# Custom date range
python main.py --days 10

# Test Discord webhook  
python main.py --test-discord

# View database stats
python main.py --stats

# Clean old jobs (30+ days)
python main.py --cleanup 30

# Show help
python main.py --help
```

## 📊 Discord Output

Each new job appears as a rich embed with:
- ✅ Job title (clickable link to OnlineJobs.ph)
- 👤 Contact person (extracted from job listings)
- 💼 Job type (Full-time/Part-time)
- 🔍 Matched keyword
- 💰 Salary (if available)
- 📝 Description preview
- 📅 Posting date

## 🚫 Anti-Bot Measures

Built-in protections:
- Random delays between requests (1-3 seconds)
- Realistic browser headers
- Maximum 2 pages per keyword
- Batch Discord messages (10 jobs max)
- Multiple parsing strategies for site changes

## ⚠️ Troubleshooting

### No jobs found
- Check if OnlineJobs.ph site structure changed
- Verify keywords are relevant 
- Try increasing `--days` parameter
- Check scraper logs for parsing errors

### Discord not working
- Test webhook: `python main.py --test-discord`
- Verify webhook URL in GitHub secrets
- Check Discord channel permissions
- Ensure webhook hasn't been deleted

### GitHub Actions failing
- Check Actions tab for error logs
- Verify `DISCORD_WEBHOOK_URL` secret is set
- Ensure repository has Actions enabled
- Check if free tier minutes exceeded

## 📝 File Structure

```
onlinejobs-scraper/
├── .github/
│   └── workflows/
│       └── scraper.yml          # GitHub Actions workflow
├── data/
│   └── jobs.db                  # SQLite database (auto-created)
├── config.py                    # Configuration settings
├── database.py                  # SQLite database operations
├── discord_sender.py            # Discord webhook integration
├── main.py                      # CLI entry point
├── scraper.py                   # Core scraping logic
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## 🔄 How It Works

1. **Keyword Search**: Searches OnlineJobs.ph for each configured keyword
2. **Job Extraction**: Parses job cards using multiple strategies
3. **Duplicate Check**: Compares against SQLite database
4. **Detail Scraping**: Visits individual job pages for full info
5. **Keyword Validation**: Final check against title + description
6. **Discord Notification**: Sends new jobs as rich embeds
7. **Database Update**: Marks jobs as sent, logs session

## 📈 GitHub Actions Free Tier

- ✅ 2,000 minutes per month
- ✅ This scraper uses ~3-5 minutes per run
- ✅ 60 runs per month = ~300 minutes used
- ✅ Plenty of headroom for twice daily automation

## 🎛️ Advanced Usage

### Custom Keywords
```python
# Add to config.py
KEYWORDS = [
    "python developer",
    "virtual assistant", 
    "data entry",
    "customer service",
    "social media"
]
```

### Different Schedule
```yaml
# In .github/workflows/scraper.yml
schedule:
  - cron: '0 6,12,18 * * *'  # 3 times daily
  - cron: '0 9 * * 1-5'      # Weekdays only at 9 AM
```

### Local Development
```bash
# Set up virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run with debug output
python main.py --days 1
```

## 🔐 Environment Variables

- `DISCORD_WEBHOOK_URL` - Required. Your Discord webhook URL
- `GITHUB_ACTIONS` - Auto-set by GitHub Actions

## 📊 Performance

Typical run statistics:
- **Execution Time**: 2-5 minutes
- **Memory Usage**: ~50MB
- **Network Requests**: 20-100 per run
- **Database Size**: ~1MB per 1000 jobs

## 📋 Legal Notice

This project is for **educational and personal portfolio purposes only**.

### Compliance & Ethics
- ✅ **Respects OnlineJobs.ph terms of service**
- ✅ **Uses only publicly available job listings**
- ✅ **Implements respectful scraping practices**
- ✅ **Not for commercial use or data redistribution**
- ✅ **Rate limited and server-friendly**

### Technical Safeguards
- **Request delays**: 1-3 seconds between requests
- **Limited scope**: Maximum 2 pages per keyword  
- **Robots.txt compliance**: Automated checking
- **No parallel requests**: Single-threaded, respectful access
- **Standard headers**: Transparent browser identification

### Data Handling
- **Public information only**: Job titles, descriptions, and contact details
- **No personal data storage**: No private or sensitive information
- **Local use only**: Personal job notifications via Discord
- **No redistribution**: Data used solely for individual job search

### Purpose Statement
This scraper demonstrates:
- Professional Python development skills
- Ethical web scraping practices  
- Database and API integration
- Automated workflow implementation
- Respectful data handling

**Note**: This project showcases technical capabilities in a responsible manner, adhering to ethical scraping guidelines and respecting website terms of service.


## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is open source and available under the MIT License.

## 🛟 Support

- Create an issue for bugs or feature requests
- Check existing issues before creating new ones
- Provide logs and error messages when reporting problems

---

**Happy job hunting! 🎯**