import requests
from bs4 import BeautifulSoup
import re

url = 'https://www.onlinejobs.ph/jobseekers/jobsearch?q=admin'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

job_links = soup.find_all('a', href=re.compile(r'/jobseekers/job/'))

print(f"=== FOUND {len(job_links)} JOB LINKS ===")

for i, link in enumerate(job_links[:10]):  # Show first 10
    href = link.get('href')
    text = link.get_text(strip=True)
    
    print(f"\n{i+1}. HREF: {href}")
    print(f"   TEXT: '{text}' (length: {len(text)})")
    
    # Check filtering conditions
    skip_reasons = []
    if 'See More' in text:
        skip_reasons.append("Contains 'See More'")
    if not text:
        skip_reasons.append("Empty text")
    if len(text) < 5:
        skip_reasons.append("Text too short")
        
    if skip_reasons:
        print(f"   SKIP: {', '.join(skip_reasons)}")
    else:
        print(f"   KEEP: Would be processed")
        
        # Try to extract job ID
        job_id_match = re.search(r'/job/.*?-(\d+)', href)
        if not job_id_match:
            job_id_match = re.search(r'/job/(\d+)', href)
        
        if job_id_match:
            print(f"   JOB_ID: {job_id_match.group(1)}")
        else:
            print(f"   JOB_ID: Could not extract!")

print(f"\n=== SUMMARY ===")
kept = 0
for link in job_links:
    text = link.get_text(strip=True)
    if not ('See More' in text or not text or len(text) < 5):
        kept += 1

print(f"Total links: {len(job_links)}")
print(f"Would keep: {kept}")
print(f"Would skip: {len(job_links) - kept}")
