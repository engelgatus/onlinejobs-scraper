#!/usr/bin/env python3
"""
main.py - Main entry point for the OnlineJobs.ph scraper
"""

import sys
import argparse
from datetime import datetime
from config import Config
from scraper import OnlineJobsScraper
from database import JobDatabase
from discord_sender import DiscordSender

def run_scraper(days_back=None, test_discord=False):
    """Main function to run the scraper"""
    
    # Print configuration
    Config.print_config()
    
    # Validate configuration
    config_issues = Config.validate_config()
    if config_issues:
        print("❌ Configuration Issues:")
        for issue in config_issues:
            print(f"  - {issue}")
        if not test_discord:  # Allow Discord test even without full config
            return False
    
    # Test Discord webhook if requested
    if test_discord:
        print("\n🧪 Testing Discord webhook...")
        discord = DiscordSender()
        if discord.test_webhook():
            print("✅ Discord webhook test successful!")
            return True
        else:
            print("❌ Discord webhook test failed!")
            return False
    
    # Set default days back
    if days_back is None:
        days_back = Config.DEFAULT_DAYS_BACK
    
    print(f"\n🕷️ Starting OnlineJobs.ph scraper...")
    print(f"📅 Looking for jobs from the last {days_back} days")
    print(f"🔍 Keywords: {', '.join(Config.KEYWORDS)}")
    
    # Initialize and run scraper
    scraper = OnlineJobsScraper()
    
    try:
        new_jobs_count = scraper.run_scrape(days_back=days_back)
        
        print(f"\n✅ Scraping completed successfully!")
        print(f"🆕 Found {new_jobs_count} new jobs")
        
        # Get database stats
        db = JobDatabase()
        stats = db.get_stats()
        print(f"📊 Database stats:")
        print(f"  - Total jobs: {stats['total_jobs']}")
        print(f"  - Sent to Discord: {stats['sent_jobs']}")
        print(f"  - Pending: {stats['unsent_jobs']}")
        
        # Send summary to Discord if there were new jobs
        if new_jobs_count > 0:
            try:
                discord = DiscordSender()
                discord.send_summary(
                    total_jobs=stats['total_jobs'],
                    new_jobs=new_jobs_count,
                    keywords_searched=Config.KEYWORDS
                )
            except Exception as e:
                print(f"Warning: Could not send summary to Discord: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(
        description='OnlineJobs.ph Job Scraper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run with default settings (5 days back)
  python main.py --days 10          # Scrape jobs from last 10 days
  python main.py --test-discord     # Test Discord webhook only
  python main.py --stats            # Show database statistics
  python main.py --cleanup 30       # Remove jobs older than 30 days
        """
    )
    
    parser.add_argument(
        '--days', 
        type=int, 
        help='Number of days back to scrape (default: 5)'
    )
    parser.add_argument(
        '--test-discord', 
        action='store_true', 
        help='Test Discord webhook and exit'
    )
    parser.add_argument(
        '--stats', 
        action='store_true', 
        help='Show database statistics and exit'
    )
    parser.add_argument(
        '--cleanup', 
        type=int, 
        metavar='DAYS',
        help='Clean up jobs older than N days and exit'
    )
    parser.add_argument(
        '--version', 
        action='version', 
        version='OnlineJobs.ph Scraper v1.0.0'
    )
    
    args = parser.parse_args()
    
    # Show stats
    if args.stats:
        try:
            db = JobDatabase()
            stats = db.get_stats()
            print("📊 Database Statistics:")
            print(f"  Total jobs: {stats['total_jobs']}")
            print(f"  Sent to Discord: {stats['sent_jobs']}")
            print(f"  Unsent jobs: {stats['unsent_jobs']}")
            print(f"  Recent jobs (7 days): {stats['recent_jobs']}")
            if stats['last_scrape']:
                print(f"  Last scrape: {stats['last_scrape'][0]} ({stats['last_scrape'][1]} new jobs)")
            else:
                print("  Last scrape: Never")
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            sys.exit(1)
        return
    
    # Cleanup old jobs
    if args.cleanup:
        try:
            db = JobDatabase()
            deleted = db.cleanup_old_jobs(args.cleanup)
            print(f"🗑️ Cleaned up {deleted} jobs older than {args.cleanup} days")
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
            sys.exit(1)
        return
    
    # Test Discord webhook
    if args.test_discord:
        success = run_scraper(test_discord=True)
        sys.exit(0 if success else 1)
    
    # Run scraper
    print("🚀 OnlineJobs.ph Scraper v1.0.0")
    print("=" * 50)
    
    success = run_scraper(days_back=args.days)
    
    if success:
        print("\n🎉 Scraper completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Scraper failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
