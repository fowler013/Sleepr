#!/usr/bin/env python3
"""
Quick test of enhanced newsletter with API integration
"""

import requests
import asyncio
from enhanced_newsletter_generator import EnhancedNewsletterGenerator

async def quick_test():
    """Quick test of enhanced newsletter generation"""
    print("🚀 QUICK TEST: Enhanced Newsletter with Full API Integration")
    print("=" * 70)
    
    # Test API connection
    try:
        health_response = requests.get("http://localhost:8080/health", timeout=5)
        print(f"🔗 API Health Check: {health_response.status_code} - {health_response.json()}")
    except Exception as e:
        print(f"❌ API Connection Failed: {e}")
        return
    
    # Test waiver wire endpoint
    try:
        waiver_response = requests.get("http://localhost:8080/api/v1/public/analytics/waiver-wire", timeout=5)
        print(f"📊 Waiver Wire API: {waiver_response.status_code}")
        if waiver_response.status_code == 200:
            print(f"   Response: {waiver_response.text[:100]}...")
    except Exception as e:
        print(f"⚠️ Waiver Wire API: {e}")
    
    # Generate enhanced newsletter
    generator = EnhancedNewsletterGenerator()
    
    try:
        newsletter = await generator.generate_super_enhanced_newsletter(
            '1197641763607556096', 
            'A League Far Far Away (API Test)',
            week=1
        )
        print("\n✅ Enhanced newsletter generated successfully!")
        print(f"📄 Length: {len(newsletter)} characters")
        
        # Show first few lines
        lines = newsletter.split('\n')
        print("\n📋 First 10 lines:")
        for i, line in enumerate(lines[:10], 1):
            print(f"   {i}. {line}")
        
    except Exception as e:
        print(f"❌ Newsletter generation failed: {e}")

if __name__ == "__main__":
    asyncio.run(quick_test())
