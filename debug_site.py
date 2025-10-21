import requests
from bs4 import BeautifulSoup
import re

def debug_onlinejobs():
    url = 'https://www.onlinejobs.ph/jobseekers/jobsearch?q=automation'
    
    try:
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        print(f"=== RESPONSE STATUS ===")
        print(response.status_code)
        
        print(f"\n=== CONTENT TYPE ===")
        print(response.headers.get('content-type', 'Unknown'))
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"\n=== PAGE TITLE ===")
        print(soup.title.string if soup.title else 'No title')
        
        print(f"\n=== FIRST 1000 CHARS ===")
        print(response.text[:1000])
        
        # Look for common job listing patterns
        print(f"\n=== POTENTIAL JOB ELEMENTS ===")
        
        # Try different selectors
        selectors_to_try = [
            'div[class*="job"]',
            'article',
            'tr',
            'a[href*="/job"]',
            'a[href*="/jobseekers/job/"]',
            '.job-item',
            '.jobpost',
            '[data-job-id]'
        ]
        
        for selector in selectors_to_try:
            elements = soup.select(selector)
            print(f"{selector}: {len(elements)} elements found")
            
        # Look for job URLs specifically
        job_links = soup.find_all('a', href=re.compile(r'/jobseekers/job/'))
        print(f"\nJob links found: {len(job_links)}")
        
        if job_links:
            print("First few job URLs:")
            for i, link in enumerate(job_links[:3]):
                print(f"  {i+1}. {link.get('href')} - {link.get_text(strip=True)[:50]}")
                
        # Check if we got redirected or blocked
        print(f"\n=== FINAL URL ===")
        print(response.url)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_onlinejobs()
