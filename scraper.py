#!/usr/bin/env python3
"""
scraper.py - Main OnlineJobs.ph scraper
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import random
import re
from urllib.parse import urljoin, urlparse
from database import JobDatabase
from discord_sender import DiscordSender
from config import Config

class OnlineJobsScraper:
    def __init__(self):
        self.base_url = "https://www.onlinejobs.ph"
        self.search_url = f"{self.base_url}/jobseekers/jobsearch"
        self.session = requests.Session()
        self.db = JobDatabase()
        self.discord = DiscordSender()
        
        # Setup headers to avoid bot detection
        self.session.headers.update({
            'User-Agent': Config.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Keywords to search for
        self.keywords = Config.KEYWORDS
        
    def search_jobs_by_keyword(self, keyword, days_back=5):
        """Search for jobs containing specific keyword"""
        jobs = []
        page = 1
        
        while True:
            search_params = {
                'q': keyword,
                'page': page
            }
            
            try:
                print(f"  Searching page {page} for '{keyword}'...")
                response = self.session.get(self.search_url, params=search_params, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try multiple selectors to find job listings
                job_cards = (
                    soup.find_all('div', class_=['job-item', 'job-list-item', 'jobpost-item']) or
                    soup.find_all('div', attrs={'data-job-id': True}) or
                    soup.find_all('a', href=re.compile(r'/jobseekers/job/')) or
                    soup.find_all('tr', class_=['job-row', 'jobpost']) or
                    soup.select('.job-item, .jobpost-item, a[href*="/jobseekers/job/"]')
                )
                
                if not job_cards:
                    print(f"    No job cards found on page {page}")
                    break
                
                print(f"    Found {len(job_cards)} job cards on page {page}")
                
                page_jobs = []
                for card in job_cards:
                    try:
                        job_data = self.extract_job_data(card, keyword)
                        if job_data and self.is_within_date_range(job_data['posted_date'], days_back):
                            page_jobs.append(job_data)
                    except Exception as e:
                        print(f"    Error extracting job data: {e}")
                        continue
                
                jobs.extend(page_jobs)
                print(f"    Added {len(page_jobs)} valid jobs from page {page}")
                
                # Stop if no jobs on this page or reached max pages
                if not page_jobs or page >= Config.MAX_PAGES_PER_KEYWORD:
                    break
                    
                page += 1
                time.sleep(random.uniform(Config.REQUEST_DELAY_MIN, Config.REQUEST_DELAY_MAX))
                
            except Exception as e:
                print(f"  Error searching page {page} for '{keyword}': {e}")
                break
        
        return jobs
    
    def extract_job_data(self, job_element, keyword):
        """Extract job data from job card element"""
        try:
            # Find job link - try multiple strategies
            job_link = None
            job_url = None
            
            # Strategy 1: Direct link element
            if job_element.name == 'a' and '/jobseekers/job/' in str(job_element.get('href', '')):
                job_link = job_element
            
            # Strategy 2: Find child link
            if not job_link:
                job_link = job_element.find('a', href=re.compile(r'/jobseekers/job/'))
            
            # Strategy 3: Find any link with job pattern
            if not job_link:
                job_link = job_element.find('a', href=lambda x: x and 'job' in x)
            
            if job_link and job_link.get('href'):
                job_url = urljoin(self.base_url, job_link['href'])
            else:
                print("    No valid job URL found")
                return None
            
            # Extract job title
            title_elem = (
                job_element.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']) or
                job_element.find(['a', 'span'], class_=re.compile(r'title|job-title|name')) or
                job_link
            )
            job_title = title_elem.get_text(strip=True) if title_elem else "Title not found"
            
            # Clean up title
            job_title = re.sub(r'\s+', ' ', job_title).strip()
            if not job_title or job_title == "Title not found":
                job_title = f"Job from keyword: {keyword}"
            
            # Extract company name
            company_elem = (
                job_element.find(['span', 'div', 'p'], class_=re.compile(r'company|employer')) or
                job_element.find(['span', 'div', 'p']) or
                job_element.find(text=re.compile(r'Company|Employer', re.I))
            )
            
            if company_elem:
                if hasattr(company_elem, 'get_text'):
                    company_name = company_elem.get_text(strip=True)
                else:
                    company_name = str(company_elem).strip()
            else:
                company_name = "Company not listed"
            
            # Clean up company name
            company_name = re.sub(r'\s+', ' ', company_name).strip()
            if len(company_name) > 100:
                company_name = company_name[:100] + "..."
            
            # Extract posting date
            date_elem = (
                job_element.find('time') or
                job_element.find(['span', 'div'], class_=re.compile(r'date|time|posted')) or
                job_element.find(text=re.compile(r'\d{1,2}:\d{2}|\d+ (hour|day|week)'))
            )
            posted_date = self.parse_posting_date(date_elem)
            
            # Extract job type
            job_type = self.extract_job_type(job_element)
            
            # Generate unique job ID from URL
            job_id_match = re.search(r'/job/.*?-(\d+)', job_url)
            if job_id_match:
                job_id = job_id_match.group(1)
            else:
                # Fallback: use hash of URL
                job_id = str(abs(hash(job_url)))
            
            job_data = {
                'job_id': job_id,
                'title': job_title[:255],  # Limit title length
                'company': company_name[:100],  # Limit company name
                'url': job_url,
                'posted_date': posted_date,
                'job_type': job_type,
                'keyword_matched': keyword,
                'scraped_at': datetime.now()
            }
            
            return job_data
            
        except Exception as e:
            print(f"    Error in extract_job_data: {e}")
            return None
    
    def get_job_details(self, job_url):
        """Scrape detailed job information from job page"""
        try:
            time.sleep(random.uniform(1, 2))  # Rate limiting
            response = self.session.get(job_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract job description
            description_selectors = [
                'div.job-description',
                'div.description', 
                'div.job-detail',
                'div.job-content',
                '.jobpost-description',
                '.job-desc'
            ]
            
            description = ""
            for selector in description_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    description = desc_elem.get_text(strip=True)
                    break
            
            # If no description found, try broader search
            if not description:
                content_div = soup.find('div', class_=re.compile(r'content|detail|desc'))
                if content_div:
                    description = content_div.get_text(strip=True)
            
            # Extract salary info if available
            salary_selectors = [
                'span.salary',
                '.salary-info',
                '.pay-range'
            ]
            
            salary = ""
            for selector in salary_selectors:
                salary_elem = soup.select_one(selector)
                if salary_elem:
                    salary = salary_elem.get_text(strip=True)
                    break
            
            # Look for salary in text
            if not salary:
                salary_match = re.search(r'\$\d+[\d,]*(?:\.\d{2})?(?:\s*-\s*\$\d+[\d,]*(?:\.\d{2})?)?', response.text)
                if salary_match:
                    salary = salary_match.group()
            
            return {
                'description': description[:500] + "..." if len(description) > 500 else description,
                'salary': salary[:50] if salary else ""  # Limit salary length
            }
            
        except Exception as e:
            print(f"    Error getting job details for {job_url}: {e}")
            return {'description': "", 'salary': ""}
    
    def extract_job_type(self, job_element):
        """Extract job type (Full-time/Part-time) from job element"""
        text = job_element.get_text().lower()
        if 'full time' in text or 'full-time' in text or 'fulltime' in text:
            return 'Full-time'
        elif 'part time' in text or 'part-time' in text or 'parttime' in text:
            return 'Part-time'
        elif 'contract' in text:
            return 'Contract'
        elif 'freelance' in text:
            return 'Freelance'
        return 'Not specified'
    
    def parse_posting_date(self, date_element):
        """Parse posting date from various formats"""
        if not date_element:
            return datetime.now()
        
        # Extract text from element
        if hasattr(date_element, 'get_text'):
            date_text = date_element.get_text().lower()
        elif hasattr(date_element, 'get'):
            date_text = date_element.get('datetime', '').lower()
        else:
            date_text = str(date_element).lower()
        
        # Handle relative dates
        now = datetime.now()
        
        # Hours ago
        hours_match = re.search(r'(\d+)\s*(?:hours?|hrs?|h)\s*ago', date_text)
        if hours_match:
            hours = int(hours_match.group(1))
            return now - timedelta(hours=hours)
        
        # Days ago
        days_match = re.search(r'(\d+)\s*(?:days?|d)\s*ago', date_text)
        if days_match:
            days = int(days_match.group(1))
            return now - timedelta(days=days)
        
        # Weeks ago
        weeks_match = re.search(r'(\d+)\s*(?:weeks?|w)\s*ago', date_text)
        if weeks_match:
            weeks = int(weeks_match.group(1))
            return now - timedelta(weeks=weeks)
        
        # Today/yesterday
        if 'today' in date_text:
            return now
        elif 'yesterday' in date_text:
            return now - timedelta(days=1)
        
        # Default to current time
        return now
    
    def is_within_date_range(self, posted_date, days_back):
        """Check if job posting is within specified date range"""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        return posted_date >= cutoff_date
    
    def matches_keywords(self, job_data):
        """Check if job matches any of our target keywords in title or description"""
        text_to_search = f"{job_data['title']} {job_data.get('description', '')}".lower()
        
        return any(keyword.lower() in text_to_search for keyword in self.keywords)
    
    def run_scrape(self, days_back=5):
        """Main scraping function"""
        print(f"🕷️ Starting OnlineJobs.ph scrape - looking {days_back} days back")
        
        all_jobs = []
        new_jobs = []
        
        # Search for each keyword
        for keyword in self.keywords:
            print(f"🔍 Searching for keyword: '{keyword}'")
            try:
                jobs = self.search_jobs_by_keyword(keyword, days_back)
                all_jobs.extend(jobs)
                print(f"  Found {len(jobs)} jobs for '{keyword}'")
            except Exception as e:
                print(f"  Error searching for '{keyword}': {e}")
            
            time.sleep(random.uniform(2, 4))  # Delay between keyword searches
        
        # Remove duplicates based on job_id
        unique_jobs = {}
        for job in all_jobs:
            unique_jobs[job['job_id']] = job
        
        print(f"📊 Found {len(unique_jobs)} unique jobs after deduplication")
        
        # Check for new jobs and get detailed info
        for job_id, job_data in unique_jobs.items():
            try:
                if not self.db.job_exists(job_id):
                    print(f"  Processing new job: {job_data['title'][:50]}...")
                    
                    # Get detailed job information
                    details = self.get_job_details(job_data['url'])
                    job_data.update(details)
                    
                    # Final keyword check on full job data
                    if self.matches_keywords(job_data):
                        # Save to database
                        if self.db.save_job(job_data):
                            new_jobs.append(job_data)
                            print(f"    ✅ Saved new job: {job_data['title']}")
                        else:
                            print(f"    ❌ Failed to save job: {job_data['title']}")
                    else:
                        print(f"    ⏭️  Job doesn't match keywords after detailed check")
                else:
                    print(f"  Job already exists: {job_data['title'][:50]}")
            except Exception as e:
                print(f"  Error processing job {job_id}: {e}")
        
        # Log scraping session
        try:
            self.db.log_scrape(len(unique_jobs), len(new_jobs), self.keywords)
        except Exception as e:
            print(f"Warning: Could not log scrape session: {e}")
        
        # Send new jobs to Discord
        if new_jobs:
            print(f"📤 Sending {len(new_jobs)} new jobs to Discord")
            try:
                success = self.discord.send_jobs_batch(new_jobs)
                if success:
                    print("✅ Successfully sent jobs to Discord")
                else:
                    print("❌ Failed to send some jobs to Discord")
            except Exception as e:
                print(f"❌ Error sending to Discord: {e}")
        else:
            print("📭 No new jobs found")
        
        return len(new_jobs)

if __name__ == "__main__":
    scraper = OnlineJobsScraper()
    new_jobs_count = scraper.run_scrape()
    print(f"🏁 Scraping completed. {new_jobs_count} new jobs found.")
