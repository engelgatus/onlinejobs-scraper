#!/usr/bin/env python3
"""
config.py - Configuration settings for OnlineJobs.ph scraper
"""

import os
from typing import List

# Try to load .env file for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, skip
    pass

class Config:
    # Keywords to search for in job titles and descriptions
    KEYWORDS: List[str] = [
        "automation",
        "entry level", 
        "associate",
        "admin",
        "operations"
    ]
    
    # Override keywords from environment if provided
    env_keywords = os.getenv('KEYWORDS', '').strip()
    if env_keywords:
        KEYWORDS = [k.strip() for k in env_keywords.split(',') if k.strip()]
    
    # Discord webhook URL - SET THIS IN ENVIRONMENT VARIABLE
    DISCORD_WEBHOOK_URL: str = os.getenv('DISCORD_WEBHOOK_URL', '')
    
    # Database settings
    DATABASE_PATH: str = os.getenv('DATABASE_PATH', 'data/jobs.db')
    
    # Scraping settings
    DEFAULT_DAYS_BACK: int = int(os.getenv('DEFAULT_DAYS_BACK', '5'))
    MAX_PAGES_PER_KEYWORD: int = int(os.getenv('MAX_PAGES_PER_KEYWORD', '10'))
    REQUEST_DELAY_MIN: float = float(os.getenv('REQUEST_DELAY_MIN', '1.0'))
    REQUEST_DELAY_MAX: float = float(os.getenv('REQUEST_DELAY_MAX', '3.0'))
    
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
        
        if cls.DEFAULT_DAYS_BACK <= 0:
            issues.append("DEFAULT_DAYS_BACK must be greater than 0")
            
        if cls.MAX_PAGES_PER_KEYWORD <= 0:
            issues.append("MAX_PAGES_PER_KEYWORD must be greater than 0")
        
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
        print(f"Request delay: {cls.REQUEST_DELAY_MIN}-{cls.REQUEST_DELAY_MAX}s")
        print("===================")

# Environment-specific configurations
if Config.IS_GITHUB_ACTIONS:
    # Adjust for GitHub Actions environment
    Config.DATABASE_PATH = "/tmp/jobs.db"  # Use tmp directory in GitHub Actions
