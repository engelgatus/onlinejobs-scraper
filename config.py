#!/usr/bin/env python3
"""
config.py - Configuration settings for OnlineJobs.ph scraper
"""

import os
from typing import List

class Config:
    # Keywords to search for in job titles and descriptions
    KEYWORDS: List[str] = [
        "automation",
        "entry level", 
        "associate",
        "admin",
        "operations"
    ]
    
    # Discord webhook URL - SET THIS IN ENVIRONMENT VARIABLE
    DISCORD_WEBHOOK_URL: str = os.getenv('DISCORD_WEBHOOK_URL', '')
    
    # Database settings
    DATABASE_PATH: str = "data/jobs.db"
    
    # Scraping settings
    DEFAULT_DAYS_BACK: int = 5  # How many days back to scrape initially
    MAX_PAGES_PER_KEYWORD: int = 10  # Limit pages to scrape per keyword
    REQUEST_DELAY_MIN: float = 1.0  # Minimum delay between requests (seconds)
    REQUEST_DELAY_MAX: float = 3.0  # Maximum delay between requests (seconds)
    
    # Rate limiting
    MAX_JOBS_PER_DISCORD_MESSAGE: int = 10
    
    # User agent for requests
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    # GitHub Actions specific
    IS_GITHUB_ACTIONS: bool = os.getenv('GITHUB_ACTIONS', 'false').lower() == 'true'
    
    @classmethod
    def validate_config(cls):
        """Validate configuration settings"""
        issues = []
        
        if not cls.DISCORD_WEBHOOK_URL:
            issues.append("DISCORD_WEBHOOK_URL environment variable is not set")
        
        if not cls.KEYWORDS:
            issues.append("No keywords configured for job searching")
        
        return issues
    
    @classmethod
    def print_config(cls):
        """Print current configuration (safe for logging)"""
        print("=== Configuration ===")
        print(f"Keywords: {', '.join(cls.KEYWORDS)}")
        print(f"Days back: {cls.DEFAULT_DAYS_BACK}")
        print(f"Max pages per keyword: {cls.MAX_PAGES_PER_KEYWORD}")
        print(f"Database path: {cls.DATABASE_PATH}")
        print(f"Discord webhook configured: {'Yes' if cls.DISCORD_WEBHOOK_URL else 'No'}")
        print(f"Running in GitHub Actions: {cls.IS_GITHUB_ACTIONS}")
        print("===================")

# Environment-specific configurations
if Config.IS_GITHUB_ACTIONS:
    # Adjust for GitHub Actions environment
    Config.DATABASE_PATH = "/tmp/jobs.db"  # Use tmp directory in GitHub Actions