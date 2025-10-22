# OnlineJobs.ph Job Scraper 🤖

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?logo=python&logoColor=white)](https://python.org)
[![GitHub Actions](https://img.shields.io/github/actions/workflow/status/engelgatus/onlinejobs-scraper/scraper.yml?branch=main&logo=github&label=Build)](https://github.com/engelgatus/onlinejobs-scraper/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Web Scraping](https://img.shields.io/badge/Web-Scraping-orange.svg?logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJMMTMuMDkgOC4yNkwyMSA5TDEzLjA5IDE1Ljc0TDEyIDIyTDEwLjkxIDE1Ljc0TDMgOUwxMC45MSA4LjI2TDEyIDJaIiBmaWxsPSJ3aGl0ZSIvPgo8L3N2Zz4K)](https://github.com/topics/web-scraping)
[![Discord](https://img.shields.io/badge/Discord-Integration-7289da.svg?logo=discord&logoColor=white)](https://discord.com)
[![SQLite](https://img.shields.io/badge/Database-SQLite-blue.svg?logo=sqlite&logoColor=white)](https://sqlite.org)
[![Ethical Scraping](https://img.shields.io/badge/Ethical-Scraping-green.svg?logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJMMTMuMDkgOC4yNkwyMSA5TDEzLjA5IDE1Ljc0TDEyIDIyTDEwLjkxIDE1Ljc0TDMgOUwxMC45MSA4LjI2TDEyIDJaIiBmaWxsPSJ3aGl0ZSIvPgo8L3N2Zz4K)](https://github.com/topics/ethical-scraping)

Intelligent job scraper that monitors OnlineJobs.ph for relevant positions while filtering out unwanted job types. Features smart keyword matching, exclusion filtering, and automated Discord notifications.

> **⚠️ Production Note:** This is a portfolio showcase repository. The automated scheduling is disabled in this public version. For actual deployment, use a private repository with proper environment variables and GitHub Actions enabled.

## 🎯 Key Features

### ✅ **Smart Job Filtering**
- **Keyword Matching**: Searches for "automation", "entry level", "associate", "admin", "operations"
- **🆕 Exclusion Filtering**: Automatically removes customer service, call center, and telemarketing jobs
- **Broader Term Recognition**: Matches related terms (e.g., "administrative" matches "admin")
- **Professional Quality**: Only relevant positions reach your Discord

### 🤖 **Advanced Automation**
- **Duplicate Prevention**: SQLite database prevents job spam
- **Contact Extraction**: AI-powered contact person identification
- **Discord Integration**: Rich embed notifications with clickable links
- **Scheduled Runs**: Automated twice-daily execution via GitHub Actions

### 🛡️ **Ethical & Reliable**
- **Respectful Scraping**: Rate limiting and robots.txt compliance
- **Error Handling**: Robust parsing with fallback strategies
- **Production Ready**: Professional logging and monitoring

## ⚡ Quick Setup

### 1. Create Discord Webhook

1. Go to your Discord server → Server Settings → Integrations
2. Click "Create Webhook" 
3. Name it "OnlineJobs Bot"
4. Select your target channel (e.g., "job-alerts")
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

### Basic Keywords (config.py)

```python
# Jobs to SEARCH FOR
KEYWORDS = [
    "automation",
    "entry level", 
    "associate",
    "admin",
    "operations"
]
```

### 🆕 **Exclusion Filtering** (New Feature!)

Filter out unwanted job types automatically:

```python
# Jobs to EXCLUDE from results
EXCLUDED_KEYWORDS = [
    "outbound call",
    "inbound sales", 
    "cold calling",
    "appointment setter",
    "customer service",
    "call center",
    "phone support",
    "telemarketing"
]
```

### ⚙️ **How to Customize Your Exclusions**

#### Method 1: Edit config.py (Permanent)

1. Open `config.py` in your repository
2. Find the `EXCLUDED_KEYWORDS` list
3. Add or remove keywords as needed:

```python
EXCLUDED_KEYWORDS = [
    "outbound call",
    "inbound sales", 
    "cold calling",
    "appointment setter",
    "customer service",
    "call center",
    "phone support",
    "telemarketing",
    # Add your own exclusions:
    "data entry clerk",
    "social media manager",
    "content writer"
]
```

4. Commit and push your changes
5. GitHub Actions will use the new exclusions on next run

#### Method 2: Environment Variable (Temporary/Testing)

```bash
# For local testing
export EXCLUDED_KEYWORDS="customer service,call center,telemarketing,data entry"
python main.py --days 1
```

```yaml
# For GitHub Actions (add to repository secrets)
EXCLUDED_KEYWORDS: "customer service,call center,telemarketing,data entry"
```

### 🎯 **Exclusion Examples**

| Will Filter Out ❌ | Will Keep ✅ |
|---|---|
| "Customer Service Representative" | "Administrative Assistant" |
| "Outbound Call Center Agent" | "Operations Coordinator" |
| "Telemarketing Specialist" | "Automation Engineer" |
| "Cold Calling Expert" | "Entry Level Data Analyst" |
| "Phone Support Technician" | "Business Associate" |
| "Appointment Setter - Sales" | "Office Administrator" |

### 📊 **Filter Performance**

The exclusion system processes jobs in this order:

1. **🔍 Search** - Find jobs matching your KEYWORDS
2. **🚫 Exclude** - Remove jobs containing EXCLUDED_KEYWORDS  
3. **✅ Validate** - Check against broader term matching
4. **📤 Deliver** - Send high-quality jobs to Discord

**Result**: Significant improvement in job relevance.

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
- 🚫 **Exclusion status** (filtered jobs show in logs)

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
- **🆕 Check if exclusions are too broad** - temporarily remove exclusions to test

### Too many unwanted jobs
- **🆕 Add more exclusion keywords** to `EXCLUDED_KEYWORDS`
- Check Discord output for common patterns in unwanted jobs
- Refine your keyword strategy

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
├── config.py                    # 🆕 Configuration + exclusions
├── database.py                  # SQLite database operations
├── discord_sender.py            # Discord webhook integration
├── main.py                      # CLI entry point
├── scraper.py                   # 🆕 Enhanced filtering logic
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## 🔄 How It Works

1. **Keyword Search**: Searches OnlineJobs.ph for each configured keyword
2. **Job Extraction**: Parses job cards using multiple strategies
3. **🆕 Exclusion Filter**: Removes unwanted job types (customer service, etc.)
4. **Duplicate Check**: Compares against SQLite database
5. **Detail Scraping**: Visits individual job pages for full info
6. **Keyword Validation**: Final check against title + description with broader terms
7. **Discord Notification**: Sends filtered, high-quality jobs as rich embeds
8. **Database Update**: Marks jobs as sent, logs session

## 🔐 Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|----------|
| `DISCORD_WEBHOOK_URL` | ✅ Yes | Your Discord webhook URL | `https://discord.com/api/webhooks/...` |
| `KEYWORDS` | ❌ Optional | Custom search keywords | `"admin,automation,operations"` |
| `EXCLUDED_KEYWORDS` | ❌ Optional | Custom exclusion keywords | `"customer service,call center"` |
| `GITHUB_ACTIONS` | ❌ Auto-set | GitHub Actions indicator | `"true"` (auto-detected) |

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

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### 🆕 **Contributing Ideas**
- Additional exclusion keywords for common job types
- Better contact person extraction patterns
- Enhanced salary parsing
- Alternative notification channels (Slack, Telegram)
- Job categorization and tagging

## 📄 License

This project is open source and available under the MIT License.

## 🛟 Support

- Create an issue for bugs or feature requests
- Check existing issues before creating new ones
- Provide logs and error messages when reporting problems
- **🆕 Include your exclusion keywords when reporting filtering issues**

---

**Happy job hunting! 🎯** 

*Now with much cleaner, more relevant results thanks to smart exclusions.*