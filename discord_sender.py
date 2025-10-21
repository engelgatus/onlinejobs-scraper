#!/usr/bin/env python3
"""
discord_sender.py - Discord webhook integration for OnlineJobs.ph scraper
Enhanced with beautiful embeds and smart formatting
"""

import requests
import json
import re
import time
from datetime import datetime
from config import Config


class DiscordSender:
    def __init__(self):
        self.webhook_url = Config.DISCORD_WEBHOOK_URL
        self.max_embed_chars = 4096
        self.max_embeds_per_message = 10
    
    def create_job_embed(self, job_data):
        """Create a beautiful Discord embed using precisely extracted data"""
        
        # Use the clean extracted data
        clean_title = job_data.get('clean_title') or self.clean_job_title(job_data.get('title', '')) or "Job Position"
        contact_person = job_data.get('contact_person') or 'Not specified'
        salary_info = job_data.get('salary_clean') or 'Not specified'
        job_type = job_data.get('job_type_clean') or job_data.get('job_type', 'Not specified')
        posted_date = job_data.get('posted_date_clean') or self.format_post_date(job_data.get('posted_date'))
        
        embed = {
            "title": f"🔥 {clean_title}",
            "url": job_data['url'],
            "color": 0x00ff88,
            "timestamp": datetime.utcnow().isoformat(),
            
            "fields": [
                {
                    "name": "👤 Contact Person",
                    "value": contact_person,
                    "inline": True
                },
                {
                    "name": "💰 Salary", 
                    "value": salary_info,
                    "inline": True
                },
                {
                    "name": "⏰ Job Type",
                    "value": job_type,
                    "inline": True
                },
                {
                    "name": "🎯 Keyword Match",
                    "value": f"`{job_data.get('keyword_matched', 'N/A')}`",
                    "inline": True
                },
                {
                    "name": "📅 Posted", 
                    "value": posted_date,
                    "inline": True
                },
                {
                    "name": "🌐 Location",
                    "value": "🇵🇭 Philippines (Remote)",
                    "inline": True
                }
            ],
            
            "footer": {
                "text": "OnlineJobs.ph • Click title to apply"
            }
        }

        # Add clean description
        description = job_data.get('description', '').strip()
        if description and len(description) > 50:
            if len(description) > 400:
                description = description[:350] + "..."
            
            embed["description"] = f"**📋 Job Description:**\n{description}"
        
        return embed




    def clean_company_name(self, company):
        """Clean up company name"""
        if not company or company.strip() in ['', 'None', 'N/A']:
            return 'Not specified'
        
        company = str(company).strip()
        
        # Remove common artifacts
        company = re.sub(r'Displaying \d+ out of \d+\+ jobs', '', company)
        company = re.sub(r'•.*$', '', company)  # Remove bullet points and after
        company = re.sub(r'\s+', ' ', company).strip()
        
        # If company name is too long or looks weird, truncate
        if len(company) > 50 or not re.search(r'[a-zA-Z]', company):
            return 'Not specified'
        
        return company[:50]

    def clean_job_title(self, title):
        """Extract clean job title from messy OnlineJobs.ph format - AGGRESSIVE CLEANING"""
        if not title:
            return "Job Position"
        
        # Convert to string and strip
        title = str(title).strip()
        
        # Remove common OnlineJobs.ph patterns (more aggressive)
        patterns_to_remove = [
            r'TYPE OF WORK.*?(?=\w{3,}|$)',  # Remove "TYPE OF WORK..." 
            r'SALARY.*?(?=\w{3,}|$)',       # Remove "SALARY..."
            r'HOURS PER WEEK.*?(?=\w{3,}|$)', # Remove "HOURS PER WEEK..."
            r'Part Time|Full Time|Any',      # Remove job types
            r'\$[\d,]+(?:\.\d{2})?(?:/\w+)?', # Remove salary amounts
            r'PHP[\s\d,]+(?:/\w+)?',         # Remove PHP amounts
            r'TBD|TBDDATE|UPDATE.*?\d{4}',   # Remove TBD, dates
            r'•.*$',                         # Remove everything after bullet
            r'[A-Z]{2,}\s*[A-Z]{2,}\s*[A-Z]{2,}.*$', # Remove ALLCAPS strings
            r'\s*-\s*\d+$',                  # Remove trailing numbers
        ]
        
        for pattern in patterns_to_remove:
            title = re.sub(pattern, '', title, flags=re.IGNORECASE)
        
        # Clean up whitespace and extract meaningful title
        title = re.sub(r'\s+', ' ', title).strip()
        
        # If title is now too short or empty, try to extract from start
        if len(title) < 3:
            original = str(title).strip()
            # Look for the first meaningful words (3+ chars, not numbers/symbols)
            words = re.findall(r'\b[A-Za-z]{3,}(?:\s+[A-Za-z]{2,}){0,4}\b', original)
            if words:
                title = words[0]
            else:
                title = "Job Position"
        
        # Final cleanup - remove any remaining artifacts
        title = re.sub(r'^[^a-zA-Z]*', '', title)  # Remove leading non-letters
        title = re.sub(r'[^a-zA-Z\s&()-]*$', '', title)  # Remove trailing junk
        
        return title[:60].strip()  # Keep reasonable length

    def format_description(self, description):
        """Format job description - MUCH cleaner"""
        if not description or len(description.strip()) < 20:
            return "Click title for full job details"
        
        # Convert to string and clean
        desc = str(description).strip()
        
        # Remove OnlineJobs.ph artifacts more aggressively
        artifacts_to_remove = [
            r'READ UNTIL THE END!.*?(?=\w{3,}|$)',
            r'DO NOT APPLY THROUGH ONLINE JOB!.*?(?=\w{3,}|$)', 
            r'TYPE OF WORK.*?(?=\w{3,}|$)',
            r'SALARY.*?(?=\w{3,}|$)',
            r'HOURS PER WEEK.*?(?=\w{3,}|$)',
            r'DATE UPDATE.*?\d{4}',
            r'Posted on.*?\d{4}',
            r'\$[\d,]+(?:\.\d{2})?(?:/\w+)?', # Remove salary mentions
            r'PHP[\s\d,]+(?:/\w+)?',
        ]
        
        for pattern in artifacts_to_remove:
            desc = re.sub(pattern, '', desc, flags=re.IGNORECASE)
        
        # Clean up whitespace
        desc = re.sub(r'\s+', ' ', desc).strip()
        
        # Intelligent truncation
        if len(desc) > 300:
            # Find last complete sentence under 250 chars
            truncated = desc[:250]
            last_sentence_end = max(
                truncated.rfind('.'),
                truncated.rfind('!'), 
                truncated.rfind('?')
            )
            
            if last_sentence_end > 100:
                desc = desc[:last_sentence_end + 1]
            else:
                # Find last comma or space
                last_break = max(truncated.rfind(','), truncated.rfind(' '))
                if last_break > 100:
                    desc = desc[:last_break] + "..."
                else:
                    desc = desc[:250] + "..."
        
        # If description is still messy or too short, provide fallback
        if len(desc.strip()) < 20 or not re.search(r'[a-zA-Z]', desc):
            return "Click title for full job details"
        
        return desc


    def extract_salary_info(self, job_data):
        """Extract salary information from title or description"""
        text = f"{job_data['title']} {job_data.get('description', '')}"
        
        # Look for various salary patterns
        salary_patterns = [
            r'\$\d+(?:,\d{3})*(?:\.\d{2})?(?:\s*-\s*\$\d+(?:,\d{3})*(?:\.\d{2})?)?(?:\s*per\s*\w+)?',  # $1,000-$2,000 per month
            r'PHP\s*\d+(?:,\d{3})*(?:\s*/\s*\w+)?',  # PHP 50,000/month
            r'\d+(?:,\d{3})*\s*PHP(?:\s*/\s*\w+)?',  # 50,000 PHP/month
            r'\$\d+(?:\.\d{2})?\s*(?:to\s*\$\d+(?:\.\d{2})?)?\s*(?:per|/)\s*hour',  # $15 to $25 per hour
            r'\d+k\s*-\s*\d+k',  # 30k-50k
            r'Starting\s+at\s+\d+(?:,\d{3})*\s*PHP',  # Starting at 45,000 PHP
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                salary = match.group().strip()
                # Clean up and limit length
                salary = re.sub(r'\s+', ' ', salary)
                return salary[:50]  # Keep reasonable length
        
        # Check for existing salary field
        if job_data.get('salary') and job_data['salary'].strip():
            return job_data['salary'][:50]
        
        return None

    def format_description(self, description):
        """Format job description for Discord"""
        # Remove extra whitespace and clean up
        desc = re.sub(r'\s+', ' ', description).strip()
        
        # Remove common OnlineJobs.ph artifacts
        desc = re.sub(r'READ UNTIL THE END!\s*', '', desc, flags=re.IGNORECASE)
        desc = re.sub(r'DO NOT APPLY THROUGH ONLINE JOB!\s*', '', desc, flags=re.IGNORECASE)
        
        # Truncate intelligently - find last complete sentence under 400 chars
        if len(desc) > 400:
            truncated = desc[:350]
            last_period = truncated.rfind('.')
            last_exclamation = truncated.rfind('!')
            last_question = truncated.rfind('?')
            last_sentence = max(last_period, last_exclamation, last_question)
            
            if last_sentence > 200:  # If we found a reasonable cutoff
                desc = desc[:last_sentence + 1]
            else:
                desc = desc[:350] + "..."
        
        return desc

    def format_post_date(self, posted_date):
        """Format posting date nicely"""
        if not posted_date:
            return "Recently"
        
        # Handle string dates
        if isinstance(posted_date, str):
            try:
                posted_date = datetime.fromisoformat(posted_date.replace('Z', '+00:00'))
            except:
                return "Recently"
        
        if not isinstance(posted_date, datetime):
            return "Recently"
        
        now = datetime.now()
        # Make both timezone-naive for comparison
        if posted_date.tzinfo:
            posted_date = posted_date.replace(tzinfo=None)
        if now.tzinfo:
            now = now.replace(tzinfo=None)
        
        diff = now - posted_date
        
        if diff.days == 0:
            hours = diff.seconds // 3600
            if hours == 0:
                return "Just now"
            elif hours == 1:
                return "1 hour ago"
            else:
                return f"{hours} hours ago"
        elif diff.days == 1:
            return "Yesterday" 
        elif diff.days < 7:
            return f"{diff.days} days ago"
        elif diff.days < 30:
            weeks = diff.days // 7
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        else:
            return posted_date.strftime("%b %d, %Y")

    def send_jobs_batch(self, jobs):
        """Send multiple jobs to Discord in optimized batches of 10"""
        if not jobs:
            return True
        
        if not self.webhook_url:
            print("Error: Discord webhook URL not configured")
            return False
        
        # Split jobs into batches of 10 (Discord limit for embeds)
        batches = [jobs[i:i + 10] for i in range(0, len(jobs), 10)]
        total_success = 0
        
        for batch_num, batch in enumerate(batches):
            try:
                # Create embeds for this batch
                embeds = []
                for job in batch:
                    embed = self.create_job_embed(job)
                    embeds.append(embed)
                
                # Send batch with header message
                batch_header = f"🔍 **New Jobs Found** - Batch {batch_num + 1}/{len(batches)}" if len(batches) > 1 else f"🔍 **{len(batch)} New Jobs Found**"
                
                payload = {
                    "content": batch_header,
                    "embeds": embeds,
                    "username": "OnlineJobs.ph Bot",
                    "avatar_url": "https://www.onlinejobs.ph/assets/img/logo.png"
                }
                
                response = requests.post(
                    self.webhook_url,
                    data=json.dumps(payload),
                    headers={"Content-Type": "application/json"},
                    timeout=15
                )
                
                if response.status_code == 204:
                    print(f"Successfully sent batch {batch_num + 1} to Discord ({len(batch)} jobs)")
                    total_success += len(batch)
                    
                    # Mark jobs as sent in database
                    try:
                        from database import JobDatabase
                        db = JobDatabase()
                        for job in batch:
                            db.mark_as_sent(job['job_id'])
                    except:
                        pass
                    
                    # Delay between batches to avoid rate limits
                    if batch_num < len(batches) - 1:  # Don't delay after last batch
                        time.sleep(1.0)
                else:
                    print(f"Failed to send batch {batch_num + 1}. Status: {response.status_code}")
                    
            except Exception as e:
                print(f"Error sending batch {batch_num + 1}: {e}")
        
        # Send summary after all batches
        if jobs:
            time.sleep(0.5)  # Small delay before summary
            self.send_enhanced_summary(len(jobs), total_success, [job['keyword_matched'] for job in jobs])
        
        print(f"Successfully sent {total_success}/{len(jobs)} jobs to Discord")
        return total_success > 0


    def send_enhanced_summary(self, total_jobs, sent_jobs, keywords):
        """Send an enhanced summary message to Discord"""
        if not self.webhook_url:
            return False
        
        try:
            # Get unique keywords
            unique_keywords = list(set(keywords))
            keyword_text = ", ".join(unique_keywords)
            
            # Determine summary color based on success rate
            success_rate = (sent_jobs / total_jobs) if total_jobs > 0 else 0
            if success_rate >= 0.9:
                color = 0x00ff88  # Green - great success
            elif success_rate >= 0.7:
                color = 0xffa500  # Orange - partial success  
            else:
                color = 0xff4444  # Red - poor success
            
            embed = {
                "title": "📊 Scraping Summary",
                "color": color,
                "fields": [
                    {
                        "name": "Total Jobs Found",
                        "value": f"**{total_jobs}**",
                        "inline": True
                    },
                    {
                        "name": "New Jobs",
                        "value": f"**{sent_jobs}**",
                        "inline": True
                    },
                    {
                        "name": "Success Rate",
                        "value": f"**{success_rate:.1%}**",
                        "inline": True
                    },
                    {
                        "name": "Keywords Searched",
                        "value": keyword_text,
                        "inline": False
                    }
                ],
                "footer": {
                    "text": f"OnlineJobs.ph Scraper • {datetime.now().strftime('%b %d at %I:%M %p')}",
                    "icon_url": "https://www.onlinejobs.ph/favicon.ico"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add success message based on results
            if sent_jobs > 0:
                embed["description"] = f"🎉 Successfully processed **{sent_jobs}** new job opportunities!"
            else:
                embed["description"] = "📭 No new jobs found this time. The scraper will continue monitoring."
            
            payload = {
                "embeds": [embed],
                "username": "OnlineJobs.ph Bot",
                "avatar_url": "https://www.onlinejobs.ph/assets/img/logo.png"
            }
            
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            return response.status_code == 204
            
        except Exception as e:
            print(f"Error sending summary to Discord: {e}")
            return False

    # Keep existing legacy methods for backward compatibility
    def send_job_batch(self, jobs, batch_num, total_batches):
        """Legacy method - redirects to new enhanced sending"""
        return self.send_jobs_batch(jobs)
    
    def send_summary(self, total_jobs, new_jobs, keywords_searched):
        """Legacy method - redirects to enhanced summary"""
        return self.send_enhanced_summary(total_jobs, new_jobs, keywords_searched)

    def format_date(self, date_obj):
        """Legacy method - redirects to enhanced date formatting"""
        return self.format_post_date(date_obj)
    
    def test_webhook(self):
        """Test the Discord webhook connection with enhanced formatting"""
        if not self.webhook_url:
            print("Error: Discord webhook URL not configured")
            return False
        
        try:
            test_embed = {
                "title": "🧪 Webhook Test",
                "description": "OnlineJobs.ph scraper webhook is working perfectly!",
                "color": 0x00ff88,
                "fields": [
                    {
                        "name": "🚀 Status",
                        "value": "All systems operational",
                        "inline": True
                    },
                    {
                        "name": "📡 Connection",
                        "value": "Webhook active",
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "OnlineJobs.ph Bot • Test completed",
                    "icon_url": "https://www.onlinejobs.ph/favicon.ico"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            payload = {
                "content": "Testing webhook connection...",
                "embeds": [test_embed],
                "username": "OnlineJobs.ph Bot",
                "avatar_url": "https://www.onlinejobs.ph/assets/img/logo.png"
            }
            
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 204:
                print("✅ Discord webhook test successful!")
                return True
            else:
                print(f"❌ Webhook test failed. Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Webhook test error: {e}")
            return False
