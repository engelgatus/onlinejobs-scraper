#!/usr/bin/env python3
"""
database.py - SQLite database operations for OnlineJobs.ph scraper
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path

class JobDatabase:
    def __init__(self, db_path="data/jobs.db"):
        self.db_path = db_path
        # Create data directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create jobs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                company TEXT,
                url TEXT UNIQUE NOT NULL,
                description TEXT,
                salary TEXT,
                job_type TEXT,
                posted_date TIMESTAMP,
                keyword_matched TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sent_to_discord BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Create scrape_history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scrape_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scrape_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                jobs_found INTEGER,
                new_jobs INTEGER,
                keywords_searched TEXT
            )
        ''')
        
        # Create index for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_posted_date ON jobs(posted_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_scraped_at ON jobs(scraped_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sent_discord ON jobs(sent_to_discord)')
        
        conn.commit()
        conn.close()
    
    def job_exists(self, job_id):
        """Check if job already exists in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM jobs WHERE job_id = ?', (job_id,))
        exists = cursor.fetchone() is not None
        
        conn.close()
        return exists
    
    def save_job(self, job_data):
        """Save job data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO jobs 
                (job_id, title, company, url, description, salary, job_type, 
                 posted_date, keyword_matched, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_data['job_id'],
                job_data['title'],
                job_data['company'],
                job_data['url'],
                job_data.get('description', ''),
                job_data.get('salary', ''),
                job_data.get('job_type', ''),
                job_data['posted_date'],
                job_data['keyword_matched'],
                job_data['scraped_at']
            ))
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
        finally:
            conn.close()
    
    def get_unsent_jobs(self):
        """Get jobs that haven't been sent to Discord yet"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT job_id, title, company, url, description, salary, job_type, 
                   posted_date, keyword_matched
            FROM jobs 
            WHERE sent_to_discord = FALSE
            ORDER BY posted_date DESC
        ''')
        
        jobs = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        job_list = []
        for job in jobs:
            job_dict = {
                'job_id': job[0],
                'title': job[1],
                'company': job[2],
                'url': job[3],
                'description': job[4],
                'salary': job[5],
                'job_type': job[6],
                'posted_date': job[7],
                'keyword_matched': job[8]
            }
            job_list.append(job_dict)
        
        return job_list
    
    def mark_as_sent(self, job_id):
        """Mark job as sent to Discord"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE jobs SET sent_to_discord = TRUE WHERE job_id = ?', (job_id,))
        conn.commit()
        conn.close()
    
    def get_recent_jobs(self, days=7):
        """Get jobs from the last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT job_id, title, company, url, posted_date, keyword_matched
            FROM jobs 
            WHERE posted_date >= datetime('now', '-{} days')
            ORDER BY posted_date DESC
        '''.format(days))
        
        jobs = cursor.fetchall()
        conn.close()
        return jobs
    
    def log_scrape(self, jobs_found, new_jobs, keywords):
        """Log scraping session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO scrape_history (jobs_found, new_jobs, keywords_searched)
            VALUES (?, ?, ?)
        ''', (jobs_found, new_jobs, ', '.join(keywords)))
        
        conn.commit()
        conn.close()
    
    def get_stats(self):
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total jobs
        cursor.execute('SELECT COUNT(*) FROM jobs')
        total_jobs = cursor.fetchone()[0]
        
        # Jobs sent to Discord
        cursor.execute('SELECT COUNT(*) FROM jobs WHERE sent_to_discord = TRUE')
        sent_jobs = cursor.fetchone()[0]
        
        # Recent jobs (last 7 days)
        cursor.execute('SELECT COUNT(*) FROM jobs WHERE posted_date >= datetime("now", "-7 days")')
        recent_jobs = cursor.fetchone()[0]
        
        # Last scrape
        cursor.execute('SELECT scrape_date, new_jobs FROM scrape_history ORDER BY scrape_date DESC LIMIT 1')
        last_scrape = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_jobs': total_jobs,
            'sent_jobs': sent_jobs,
            'unsent_jobs': total_jobs - sent_jobs,
            'recent_jobs': recent_jobs,
            'last_scrape': last_scrape
        }
    
    def cleanup_old_jobs(self, days=30):
        """Remove jobs older than N days to keep database size manageable"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM jobs WHERE posted_date < datetime("now", "-{} days")'.format(days))
        deleted = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return deleted