#!/usr/bin/env python3
"""
discord_sender.py - Discord webhook integration for OnlineJobs.ph scraper
"""

import requests
import json
from datetime import datetime
from config import Config

class DiscordSender:
    def __init__(self):
        self.webhook_url = Config.DISCORD_WEBHOOK_URL
        self.max_embed_chars = 4096
        self.max_embeds_per_message = 10
    
    def create_job_embed(self, job_data):
        """Create a Discord embed for a job posting"""
        
        # Truncate description if too long
        description = job_data.get('description', 'No description available')
        if len(description) > 500:
            description = description[:497] + "..."
        
        # Create embed
        embed = {
            "title": job_data['title'][:256],  # Discord title limit
            "url": job_data['url'],
            "color": 0x00ff00,  # Green color
            "fields": [
                {
                    "name": "Company",
                    "value": job_data['company'] or "Not specified",
                    "inline": True
                },
                {
                    "name": "Job Type",
                    "value": job_data.get('job_type', 'Not specified'),
                    "inline": True
                },
                {
                    "name": "Keyword Match",
                    "value": job_data['keyword_matched'],
                    "inline": True
                }
            ],
            "footer": {
                "text": f"OnlineJobs.ph • Posted: {self.format_date(job_data['posted_date'])}"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add salary if available
        if job_data.get('salary') and job_data['salary'].strip():
            embed["fields"].append({
                "name": "Salary",
                "value": job_data['salary'][:100],  # Limit salary field length
                "inline": True
            })
        
        # Add description if available
        if description and description.strip():
            embed["description"] = description
        
        return embed
    
    def format_date(self, date_obj):
        """Format datetime object for display"""
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
            except:
                return date_obj
        
        if isinstance(date_obj, datetime):
            return date_obj.strftime("%Y-%m-%d %H:%M")
        
        return str(date_obj)
    
    def send_jobs_batch(self, jobs):
        """Send multiple jobs to Discord in batches"""
        if not jobs:
            return True
        
        if not self.webhook_url:
            print("Error: Discord webhook URL not configured")
            return False
        
        # Split jobs into batches of 10 (Discord limit)
        batches = [jobs[i:i + self.max_embeds_per_message] for i in range(0, len(jobs), self.max_embeds_per_message)]
        
        for batch_num, batch in enumerate(batches):
            success = self.send_job_batch(batch, batch_num + 1, len(batches))
            if not success:
                return False
        
        return True
    
    def send_job_batch(self, jobs, batch_num, total_batches):
        """Send a single batch of jobs to Discord"""
        try:
            embeds = []
            for job in jobs:
                embed = self.create_job_embed(job)
                embeds.append(embed)
            
            # Create message content
            content = f"🔍 **New Jobs Found** ({len(jobs)} jobs)"
            if total_batches > 1:
                content += f" - Batch {batch_num}/{total_batches}"
            
            payload = {
                "content": content,
                "embeds": embeds,
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
                print(f"Successfully sent batch {batch_num} to Discord ({len(jobs)} jobs)")
                
                # Mark jobs as sent in database (if database instance available)
                try:
                    from database import JobDatabase
                    db = JobDatabase()
                    for job in jobs:
                        db.mark_as_sent(job['job_id'])
                except:
                    pass  # Database marking is optional
                
                return True
            else:
                print(f"Failed to send Discord message. Status: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error sending to Discord: {e}")
            return False
    
    def send_summary(self, total_jobs, new_jobs, keywords_searched):
        """Send a summary message to Discord"""
        if not self.webhook_url:
            return False
        
        try:
            embed = {
                "title": "📊 Scraping Summary",
                "color": 0x0099ff,  # Blue color
                "fields": [
                    {
                        "name": "Total Jobs Found",
                        "value": str(total_jobs),
                        "inline": True
                    },
                    {
                        "name": "New Jobs",
                        "value": str(new_jobs),
                        "inline": True
                    },
                    {
                        "name": "Keywords Searched",
                        "value": ", ".join(keywords_searched),
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "OnlineJobs.ph Scraper"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            payload = {
                "embeds": [embed],
                "username": "OnlineJobs.ph Bot"
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
    
    def test_webhook(self):
        """Test the Discord webhook connection"""
        if not self.webhook_url:
            print("Error: Discord webhook URL not configured")
            return False
        
        try:
            test_embed = {
                "title": "🧪 Webhook Test",
                "description": "OnlineJobs.ph scraper webhook is working!",
                "color": 0x00ff00,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            payload = {
                "content": "Testing webhook connection...",
                "embeds": [test_embed],
                "username": "OnlineJobs.ph Bot"
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