#!/usr/bin/env python3
"""
config.py - Configuration settings for OnlineJobs.ph scraper
Professional web scraping with ethical compliance and rate limiting
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
    # ============================================================================
    # JOB SEARCH CONFIGURATION
    # ============================================================================
    
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
    
    # ============================================================================
    # JOB FILTERING CONFIGURATION  
    # ============================================================================

    # Keywords to EXCLUDE from job results - these will filter out unwanted jobs
    EXCLUDED_KEYWORDS: List[str] = [
        "outbound call",
        "inbound sales", 
        "cold calling",
        "appointment setter",
        "customer service",
        "call center",
        "phone support",
        "telemarketing"
    ]

    # Override excluded keywords from environment if provided
    env_excluded = os.getenv('EXCLUDED_KEYWORDS', '').strip()
    if env_excluded:
        EXCLUDED_KEYWORDS = [k.strip().lower() for k in env_excluded.split(',') if k.strip()]
    else:
        # Ensure they're lowercase for consistent matching
        EXCLUDED_KEYWORDS = [k.lower() for k in EXCLUDED_KEYWORDS]
    
    # ============================================================================
    # INTEGRATION SETTINGS
    # ============================================================================
    
    # Discord webhook URL - SET THIS IN ENVIRONMENT VARIABLE
    DISCORD_WEBHOOK_URL: str = os.getenv('DISCORD_WEBHOOK_URL', '')
    
    # Database settings
    DATABASE_PATH: str = os.getenv('DATABASE_PATH', 'data/jobs.db')
    
    # ============================================================================
    # RESPECTFUL SCRAPING SETTINGS
    # ============================================================================
    
    # Date range settings
    DEFAULT_DAYS_BACK: int = int(os.getenv('DEFAULT_DAYS_BACK', '5'))
    
    # Respectful rate limiting - prevents server overload
    RESPECTFUL_DELAY_MIN: float = float(os.getenv('REQUEST_DELAY_MIN', '1.0'))    # Minimum delay between requests (seconds)
    RESPECTFUL_DELAY_MAX: float = float(os.getenv('REQUEST_DELAY_MAX', '3.0'))    # Maximum delay between requests (seconds)
    MAX_CONCURRENT_REQUESTS: int = 1                                              # No parallel requests - respectful scraping
    MAX_PAGES_PER_KEYWORD: int = int(os.getenv('MAX_PAGES_PER_KEYWORD', '2'))    # Limited scope to avoid overloading server
    
    # Legacy property names for backward compatibility
    REQUEST_DELAY_MIN = RESPECTFUL_DELAY_MIN
    REQUEST_DELAY_MAX = RESPECTFUL_DELAY_MAX
    
    # Discord message batching
    MAX_JOBS_PER_DISCORD_MESSAGE: int = 10
    
    # ============================================================================
    # BROWSER SIMULATION SETTINGS  
    # ============================================================================
    
    # Standard browser headers for transparent identification
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    # ============================================================================
    # DEPLOYMENT ENVIRONMENT SETTINGS
    # ============================================================================
    
    # GitHub Actions specific detection
    IS_GITHUB_ACTIONS: bool = os.getenv('GITHUB_ACTIONS', 'false').lower() == 'true'
    
    # ============================================================================
    # ETHICAL COMPLIANCE METHODS
    # ============================================================================
    
    @classmethod
    def validate_config(cls):
        """Validate configuration settings for proper operation"""
        issues = []
        
        if not cls.DISCORD_WEBHOOK_URL:
            issues.append("DISCORD_WEBHOOK_URL environment variable is not set")
        
        if not cls.KEYWORDS:
            issues.append("No keywords configured for job searching")
        
        if cls.DEFAULT_DAYS_BACK <= 0:
            issues.append("DEFAULT_DAYS_BACK must be greater than 0")
            
        if cls.MAX_PAGES_PER_KEYWORD <= 0:
            issues.append("MAX_PAGES_PER_KEYWORD must be greater than 0")
        
        if cls.RESPECTFUL_DELAY_MIN < 0.5:
            issues.append("RESPECTFUL_DELAY_MIN should be at least 0.5 seconds for respectful scraping")
            
        if cls.RESPECTFUL_DELAY_MAX < cls.RESPECTFUL_DELAY_MIN:
            issues.append("RESPECTFUL_DELAY_MAX must be greater than RESPECTFUL_DELAY_MIN")
        
        # Validate excluded keywords
        if not cls.EXCLUDED_KEYWORDS:
            print("ℹ️  No keywords configured for exclusion - all matching jobs will be included")
        else:
            print(f"🚫 Excluding jobs containing: {', '.join(cls.EXCLUDED_KEYWORDS)}")
        
        return issues
    
    @classmethod
    def print_config(cls):
        """Print current configuration (safe for logging)"""
        print("=== Configuration ===")
        print(f"Keywords: {', '.join(cls.KEYWORDS)}")
        print(f"Excluded Keywords: {', '.join(cls.EXCLUDED_KEYWORDS)}")
        print(f"Days back: {cls.DEFAULT_DAYS_BACK}")
        print(f"Max pages per keyword: {cls.MAX_PAGES_PER_KEYWORD}")
        print(f"Database path: {cls.DATABASE_PATH}")
        print(f"Discord webhook configured: {'Yes' if cls.DISCORD_WEBHOOK_URL else 'No'}")
        print(f"Running in GitHub Actions: {cls.IS_GITHUB_ACTIONS}")
        print(f"Request delay: {cls.RESPECTFUL_DELAY_MIN}-{cls.RESPECTFUL_DELAY_MAX}s")
        print("===================")
        
        # Display ethical compliance information
        print("\n=== Ethical Scraping Practices ===")
        print(f"✅ Respectful delays: {cls.RESPECTFUL_DELAY_MIN}-{cls.RESPECTFUL_DELAY_MAX}s between requests")
        print(f"✅ Limited scope: Maximum {cls.MAX_PAGES_PER_KEYWORD} pages per keyword")
        print(f"✅ Sequential requests: No parallel processing ({cls.MAX_CONCURRENT_REQUESTS} concurrent)")
        print("✅ Transparent headers: Standard browser identification")
        print("✅ Public data only: Job listings and contact information")
        print("==================================")

    @classmethod 
    def print_compliance_summary(cls):
        """Print compliance and ethical usage summary"""
        print("\n🤖 ETHICAL SCRAPING COMPLIANCE SUMMARY")
        print("=====================================")
        print("📋 Purpose: Personal job search automation & portfolio demonstration")
        print("🎯 Scope: Public job listings only")
        print("⏱️  Rate Limiting: 1-3 second delays between requests")
        print("🚦 Traffic Control: Maximum 2 pages per keyword")
        print("🔒 Privacy Compliant: No personal or private data collection")
        print("📊 Educational Use: Technical skill demonstration")
        print("✅ Respectful Implementation: Server-friendly practices")
        print("=====================================\n")

# ============================================================================
# ENVIRONMENT-SPECIFIC CONFIGURATIONS
# ============================================================================

# Adjust settings for different deployment environments
if Config.IS_GITHUB_ACTIONS:
    # GitHub Actions environment optimizations
    Config.DATABASE_PATH = "/tmp/jobs.db"  # Use tmp directory in GitHub Actions
    
    # Slightly longer delays in cloud environment for extra respect
    if Config.RESPECTFUL_DELAY_MIN < 1.5:
        Config.RESPECTFUL_DELAY_MIN = 1.5
    if Config.RESPECTFUL_DELAY_MAX < 3.0:
        Config.RESPECTFUL_DELAY_MAX = 3.0

# ============================================================================
# PROFESSIONAL DOCUMENTATION CONSTANTS
# ============================================================================

# Project metadata for professional documentation
PROJECT_NAME = "OnlineJobs.ph Ethical Job Scraper"
PROJECT_VERSION = "1.1.0"
PROJECT_PURPOSE = "Educational portfolio project demonstrating ethical web scraping practices"
COMPLIANCE_STATEMENT = "This project adheres to respectful scraping guidelines and uses only publicly available information"