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
                
                # Use the correct selector
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
            
            # CONTACT PERSON EXTRACTION
            contact_person = ""
            
            # CONTACT PERSON EXTRACTION  
            contact_patterns = [
                # Pattern 1: Job Type + Contact Person (2-3 words) • Posted
                r'(?:Full Time|Part Time|Any|Gig)\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\s*•\s*Posted',
                
                # Pattern 2: Job Type + Contact Person (single word) • Posted
                r'(?:Full Time|Part Time|Any|Gig)\s*([A-Z][a-z]{3,20})\s*•\s*Posted',
                
                # Pattern 3: Contact Person (2-3 words) • Posted (no job type)
                r'\s([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\s*•\s*Posted',
                
                # Pattern 4: Special case for "Hiring Manager", "Hiring admin", etc.
                r'\s(Hiring\s+[A-Z][a-z]+)\s*•\s*Posted',
                
                # Pattern 5: Special case for company names ending in recognizable suffixes
                r'\s([A-Z][A-Z]{2,}\s+[A-Z][a-z]+)\s*•\s*Posted',  # "MTZ Financials"
            ]
            
            for pattern in contact_patterns:
                match = re.search(pattern, job_title)
                if match:
                    potential_contact = match.group(1).strip()
                    
                    # Validate it's a real name (not job type or other text)
                    excluded_words = [
                        'Full', 'Time', 'Part', 'Any', 'Gig', 'Posted', 'Oct', 'Nov', 'Dec', 
                        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep',
                        'jobs', 'Displaying', 'out', 'of', 'Remote', 'Urgent', 'Hiring',
                        'ASAP', 'Immediate', 'Fixed', 'Price'
                    ]
                    
                    # Check if it's a valid name 
                    if (len(potential_contact) >= 3 and 
                        len(potential_contact) <= 50 and
                        not any(word.lower() in potential_contact.lower() for word in excluded_words) and
                        not re.match(r'^\d', potential_contact) and  # Doesn't start with number
                        re.match(r'^[A-Z]', potential_contact)):    # Starts with capital
                        
                        # Special handling for single words that should be expanded
                        if potential_contact in ['Manager', 'Admin', 'Specialist'] and 'Hiring' in job_title:
                            # Try to find "Hiring Manager" instead of just "Manager"
                            hiring_match = re.search(r'(Hiring\s+' + potential_contact + ')', job_title, re.IGNORECASE)
                            if hiring_match:
                                contact_person = hiring_match.group(1)
                            else:
                                contact_person = potential_contact
                        else:
                            contact_person = potential_contact
                        break
            
            # Get parent for company extraction
            parent = job_link.parent
            company_name = "Company not listed"
            
            if parent:
                link_context = job_link.get_text(strip=True)
                company_patterns = [
                    r'([A-Za-z\s&\.]+?)\s*•\s*Posted',
                    r'([A-Za-z\s&\.]+?)\s*•',
                    r'(?:Full Time|Part Time|Any)\s*([A-Za-z\s&\.]+?)\s*•',
                ]
                
                for pattern in company_patterns:
                    match = re.search(pattern, link_context, re.IGNORECASE)
                    if match:
                        potential_company = match.group(1).strip()
                        if (len(potential_company) > 2 and 
                            len(potential_company) < 50 and
                            not re.match(r'^(Displaying|jobs|out|of|\d+)', potential_company, re.IGNORECASE)):
                            company_name = potential_company
                            break
            
            job_data = {
                'job_id': job_id,
                'title': job_title,
                'company': company_name,
                'contact_person_initial': contact_person,  # Store the extracted contact
                'url': job_url,
                'posted_date': datetime.now(),
                'job_type': 'Not specified',
                'keyword_matched': keyword,
                'scraped_at': datetime.now()
            }
            
            return job_data
            
        except Exception as e:
            print(f"    Error in extract_job_data_from_link: {e}")
            return None
    
    def get_job_details(self, job_url):
        """Scrape detailed job information using precise HTML selectors"""
        try:
            time.sleep(random.uniform(1, 2))
            response = self.session.get(job_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 1. Extract Job Title
            job_title = ""
            title_elem = soup.select_one('h1.job__title')
            if title_elem:
                job_title = title_elem.get_text(strip=True)
                job_title = re.sub(r'&amp;', '&', job_title)
            
            # 2. Extract Job Type
            job_type = "Not specified"
            job_type_patterns = [
                r'TYPE OF WORK.*?<p class="fs-18">\s*([^<]+)',
                r'Job Type.*?<p class="fs-18">\s*([^<]+)',
            ]
            
            page_html = str(soup)
            for pattern in job_type_patterns:
                match = re.search(pattern, page_html, re.IGNORECASE | re.DOTALL)
                if match:
                    job_type = match.group(1).strip()
                    break
            
            if job_type == "Not specified":
                if 'Full Time' in page_html:
                    job_type = 'Full Time'
                elif 'Part Time' in page_html:
                    job_type = 'Part Time'
            
            # 3. Extract Salary
            salary = ""
            salary_patterns = [
                r'SALARY.*?<p class="fs-18">\s*([^<]+)',
                r'Salary.*?<p class="fs-18">\s*([^<]+)',
                r'<p class="fs-18">\s*(\$[\d,]+(?:\.\d{2})?(?:/hr|/hour|/month)?)\s*</p>',
                r'<p class="fs-18">\s*(\d+/hr|\$\d+)\s*</p>',
            ]
            
            for pattern in salary_patterns:
                match = re.search(pattern, page_html, re.IGNORECASE | re.DOTALL)
                if match:
                    salary = match.group(1).strip()
                    break
            
            # 4. Extract Contact Person - SIMPLIFIED VERSION
            contact_person = ""
            
            # Look for contact person patterns in HTML
            contact_patterns = [
                r'Contact Person:\s*<strong>([^<]+)</strong>',
                r'Contact Person:\s*([^\n\r<]+)',
                r'Employer:\s*<strong>([^<]+)</strong>',
            ]
            
            for pattern in contact_patterns:
                match = re.search(pattern, page_html, re.IGNORECASE)
                if match:
                    contact_person = match.group(1).strip()
                    break
            
            # Backup: Card structure
            if not contact_person:
                employer_cards = soup.select('.card-body')
                for card in employer_cards:
                    text = card.get_text()
                    if 'Contact Person' in text:
                        strong_elem = card.select_one('strong')
                        if strong_elem:
                            contact_person = strong_elem.get_text(strip=True)
                            break
            
            # 5. Extract Posted Date
            posted_date = ""
            date_patterns = [
                r'DATE UPDATED.*?<p class="fs-18">\s*([^<]+)',
                r'Posted.*?<p class="fs-18">\s*([^<]+)',
                r'<p class="fs-18">\s*([A-Za-z]{3}\s+\d{1,2},\s+\d{4})\s*</p>',
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, page_html, re.IGNORECASE | re.DOTALL)
                if match:
                    posted_date = match.group(1).strip()
                    break
            
            # 6. Extract Description
            description = ""
            desc_selectors = [
                '.job-description',
                '.job-overview', 
                '.card-body p',
                'div[class*="description"]',
                'div[class*="overview"]'
            ]
            
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    desc_text = desc_elem.get_text(separator=' ', strip=True)
                    if 'TYPE OF WORK' not in desc_text and len(desc_text) > 100:
                        description = desc_text
                        break
            
            if not description:
                main_content = soup.select_one('.container .row')
                if main_content:
                    paragraphs = main_content.find_all('p')
                    desc_parts = []
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        if len(text) > 50 and 'Contact Person' not in text:
                            desc_parts.append(text)
                            if len(' '.join(desc_parts)) > 300:
                                break
                    description = ' '.join(desc_parts)
            
            return {
                'clean_title': job_title[:200] if job_title else "",
                'job_type_clean': job_type,
                'salary_clean': salary,
                'contact_person': contact_person[:100] if contact_person else "",
                'posted_date_clean': posted_date,
                'description': description[:600] if description else "",
            }
            
        except Exception as e:
            print(f"    Error getting job details from {job_url}: {e}")
            return {
                'clean_title': "",
                'job_type_clean': "",
                'salary_clean': "",
                'contact_person': "",
                'posted_date_clean': "",
                'description': "",
            }


    def is_within_date_range(self, posted_date, days_back):
        """Check if job is within date range"""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        return posted_date >= cutoff_date

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
        return True

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

                    # Use initial contact person as fallback
                    if not details.get('contact_person') and job_data.get('contact_person_initial'):
                        details['contact_person'] = job_data['contact_person_initial']
                        print(f"    📝 Using extracted contact person: '{details['contact_person']}'")

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
        
        # 🔥 CRITICAL: SEND TO DISCORD (this was missing!)
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