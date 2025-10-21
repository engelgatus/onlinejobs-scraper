#!/usr/bin/env python3
"""
scraper.py - Main OnlineJobs.ph scraper (FIXED VERSION)
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import random
import re
from urllib.parse import urljoin
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
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })
        
        self.keywords = Config.KEYWORDS
        
    def search_jobs_by_keyword(self, keyword, days_back=5):
        """Search for jobs containing specific keyword"""
        jobs = []
        page = 1
        
        while page <= Config.MAX_PAGES_PER_KEYWORD:
            search_params = {
                'q': keyword,
                'page': page
            }
            
            try:
                print(f"  Searching page {page} for '{keyword}'...")
                response = self.session.get(self.search_url, params=search_params, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # FIXED: Use the correct selector based on debug results
                job_links = soup.find_all('a', href=re.compile(r'/jobseekers/job/'))
                
                # Filter out "See More" links and duplicates
                unique_jobs_on_page = {}
                for link in job_links:
                    href = link.get('href')
                    text = link.get_text(strip=True)
                    
                    # Skip "See More" links and empty links
                    if text == 'See More' or not text or len(text) < 10:
                        continue
                        
                    # Extract job ID to avoid duplicates
                    job_id_match = re.search(r'/job/.*?-(\d+)', href)
                    if not job_id_match:
                        job_id_match = re.search(r'/job/(\d+)', href)
                    
                    if job_id_match:
                        job_id = job_id_match.group(1)
                        if job_id not in unique_jobs_on_page:
                            unique_jobs_on_page[job_id] = link
                
                if not unique_jobs_on_page:
                    print(f"    No unique job links found on page {page}")
                    break
                
                print(f"    Found {len(unique_jobs_on_page)} unique job links on page {page}")
                
                page_jobs = []
                for job_id, link in unique_jobs_on_page.items():
                    try:
                        job_data = self.extract_job_data_from_link(link, keyword, job_id)
                        if job_data and self.is_within_date_range(job_data['posted_date'], days_back):
                            page_jobs.append(job_data)
                    except Exception as e:
                        print(f"    Error extracting job: {e}")
                        continue
                
                jobs.extend(page_jobs)
                print(f"    Added {len(page_jobs)} valid jobs from page {page}")
                
                if not page_jobs:
                    break
                    
                page += 1
                time.sleep(random.uniform(3, 6))
                
            except Exception as e:
                print(f"  Error searching page {page} for '{keyword}': {e}")
                break
        
        return jobs
    
    def extract_job_data_from_link(self, job_link, keyword, job_id):
        """Extract job data from job link element"""
        try:
            job_url = urljoin(self.base_url, job_link['href'])
            
            # Extract job title from link text
            job_title = job_link.get_text(strip=True)
            job_title = re.sub(r'\s+', ' ', job_title).strip()[:255]
            
            # Try to find parent element for more info
            parent = job_link.parent
            company_name = "Company not listed"
            
            # Look for company info in siblings or parent
            if parent:
                # Try to find company name in nearby text
                parent_text = parent.get_text()
                # Look for patterns like "Company Name •Posted on"
                company_match = re.search(r'([^•]+)•', parent_text)
                if company_match:
                    company_name = company_match.group(1).strip()[:100]
            
            job_data = {
                'job_id': job_id,
                'title': job_title,
                'company': company_name,
                'url': job_url,
                'posted_date': datetime.now(),  # Will be refined when we get job details
                'job_type': 'Not specified',
                'keyword_matched': keyword,
                'scraped_at': datetime.now()
            }
            
            return job_data
            
        except Exception as e:
            print(f"    Error in extract_job_data_from_link: {e}")
            return None
    
    def get_job_details(self, job_url):
        """Scrape detailed job information"""
        try:
            time.sleep(random.uniform(1, 2))
            response = self.session.get(job_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract description from multiple possible locations
            description = ""
            desc_selectors = [
                'div[class*="description"]',
                'div[class*="job"]', 
                'div[class*="detail"]',
                '.content'
            ]
            
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    desc_text = desc_elem.get_text(strip=True)
                    if len(desc_text) > 50:  # Only use substantial descriptions
                        description = desc_text
                        break
            
            return {
                'description': description[:500] + "..." if len(description) > 500 else description,
                'salary': ""
            }
            
        except Exception as e:
            print(f"    Error getting job details: {e}")
            return {'description': "", 'salary': ""}
    
    def is_within_date_range(self, posted_date, days_back):
        """Check if job is within date range"""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        return posted_date >= cutoff_date
    
    #def matches_keywords(self, job_data):
        """Check if job matches keywords"""
       # text_to_search = f"{job_data['title']} {job_data.get('description', '')}".lower()
       # return any(keyword.lower() in text_to_search for keyword in self.keywords)

    def matches_keywords(self, job_data):
    """Check if job matches keywords with broader term matching"""
    text_to_search = f"{job_data['title']} {job_data.get('description', '')}".lower()
    
    # Broader related terms for each keyword
    broader_terms = {
        'admin': ['administration', 'administrative', 'office', 'assistant', 'support', 
                  'coordinator', 'clerk', 'secretary', 'receptionist', 'data entry'],
        'automation': ['automated', 'script', 'workflow', 'process', 'bot', 'rpa', 
                       'zapier', 'integration', 'api', 'system'],
        'entry level': ['junior', 'trainee', 'intern', 'beginner', 'new grad', 
                        'graduate', 'starter', 'entry-level', 'no experience'],
        'associate': ['junior', 'coordinator', 'specialist', 'assistant', 'analyst', 
                      'representative', 'officer', 'team member'],
        'operations': ['ops', 'operational', 'management', 'coordinator', 'supervisor', 
                       'logistics', 'workflow', 'process', 'production', 'business']
    }
    
    # Check original keyword or related terms
    for keyword in self.keywords:
        # Direct keyword match
        if keyword.lower() in text_to_search:
            return True
        
        # Check related terms for this keyword
        related_terms = broader_terms.get(keyword, [])
        for term in related_terms:
            if term in text_to_search:
                return True
    
    # Also accept jobs if they were found by our keyword search
    # (trust OnlineJobs.ph's search relevance)
    return True  # Since we searched for our keywords, assume relevance
    
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
            
            time.sleep(random.uniform(2, 4))
        
        # Remove duplicates
        unique_jobs = {}
        for job in all_jobs:
            unique_jobs[job['job_id']] = job
        
        print(f"📊 Found {len(unique_jobs)} unique jobs after deduplication")
        
        # Process new jobs
        for job_id, job_data in unique_jobs.items():
            try:
                if not self.db.job_exists(job_id):
                    print(f"  Processing new job: {job_data['title'][:50]}...")
                    
                    # Get detailed info
                    details = self.get_job_details(job_data['url'])
                    job_data.update(details)
                    
                    # Final keyword check
                    if self.matches_keywords(job_data):
                        if self.db.save_job(job_data):
                            new_jobs.append(job_data)
                            print(f"    ✅ Saved: {job_data['title']}")
                        else:
                            print(f"    ❌ Failed to save: {job_data['title']}")
                    else:
                        print(f"    ⏭️  Doesn't match keywords")
                else:
                    print(f"  Job already exists: {job_data['title'][:50]}")
            except Exception as e:
                print(f"  Error processing job {job_id}: {e}")
        
        # Send to Discord
        if new_jobs:
            print(f"📤 Sending {len(new_jobs)} new jobs to Discord")
            try:
                success = self.discord.send_jobs_batch(new_jobs)
                if success:
                    print("✅ Successfully sent jobs to Discord")
                else:
                    print("❌ Failed to send jobs to Discord")
            except Exception as e:
                print(f"❌ Error sending to Discord: {e}")
        else:
            print("📭 No new jobs found")
        
        return len(new_jobs)

if __name__ == "__main__":
    scraper = OnlineJobsScraper()
    new_jobs_count = scraper.run_scrape()
    print(f"🏁 Scraping completed. {new_jobs_count} new jobs found.")