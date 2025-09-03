#!/usr/bin/env python3
"""
YouTube Data API v3 specific usage examples
Demonstrates the preferred, official method for video information extraction
"""

import os
from yt_info_extract import YouTubeVideoInfoExtractor


def example_api_setup():
    """Example showing how to set up and use the YouTube Data API v3"""
    print("=== YouTube Data API v3 Setup Example ===")
    
    # Method 1: Set API key as environment variable (recommended)
    # export YOUTUBE_API_KEY="your_api_key_here"
    
    # Method 2: Pass API key directly (less secure for production)
    api_key = "your_api_key_here"  # Replace with your actual API key
    
    # Check if API key is set
    env_api_key = os.environ.get("YOUTUBE_API_KEY")
    if env_api_key:
        print("✓ API key found in environment variables")
        extractor = YouTubeVideoInfoExtractor(strategy="api")
    elif api_key != "your_api_key_here":
        print("✓ Using API key from code (not recommended for production)")
        extractor = YouTubeVideoInfoExtractor(api_key=api_key, strategy="api")
    else:
        print("⚠ No API key provided. Set YOUTUBE_API_KEY environment variable")
        print("or replace 'your_api_key_here' with your actual API key")
        return
    
    # Test the API key
    if extractor.test_api_key():
        print("✓ API key is valid and working")
    else:
        print("✗ API key test failed")
        return
    
    # Get video information using API
    video_id = "jNQXAC9IVRw"
    print(f"\nExtracting info for video: {video_id}")
    
    info = extractor.get_video_info(video_id)
    
    if info:
        print(f"✓ Successfully extracted using: {info['extraction_method']}")
        print(f"Title: {info['title']}")
        print(f"Channel: {info['channel_name']}")
        print(f"Views: {info['views']:,}" if info['views'] else "Views: Unknown")
        print(f"Published: {info['publication_date']}")
    else:
        print("✗ Failed to extract video information")


def example_api_batch_processing():
    """Example of efficient batch processing with API"""
    print("\n=== API Batch Processing Example ===")
    
    # Note: The API allows up to 50 video IDs in a single request
    # This is much more quota-efficient than individual requests
    
    extractor = YouTubeVideoInfoExtractor(strategy="api")
    
    if not extractor.test_api_key():
        print("⚠ API key not available, skipping API batch example")
        return
    
    video_ids = [
        "jNQXAC9IVRw",  # Me at the zoo
        "_OBlgSz8sSM",  # Charlie bit my finger
        "9bZkp7q19f0",  # Gangnam Style
        "kffacxfA7G4",  # Baby Shark
        "pRpeEdMmmQ0",  # Shakira - Whenever, Wherever
    ]
    
    print(f"Processing {len(video_ids)} videos with API...")
    
    # The extractor will automatically batch API requests for efficiency
    results = extractor.batch_extract(video_ids, strategy="api", delay_between_requests=0.1)
    
    print(f"\nResults:")
    for i, result in enumerate(results):
        if result.get('error'):
            print(f"{i+1}. ERROR: {result.get('error')}")
        else:
            title = result['title'][:40] + "..." if len(result['title']) > 40 else result['title']
            views = result.get('views', 0)
            method = result.get('extraction_method', 'unknown')
            print(f"{i+1}. {title} | {views:,} views | {method}")


def example_api_quota_management():
    """Example showing quota-conscious usage"""
    print("\n=== API Quota Management Example ===")
    
    extractor = YouTubeVideoInfoExtractor(strategy="api")
    
    if not extractor.test_api_key():
        print("⚠ API key not available, skipping quota management example")
        return
    
    print("YouTube Data API v3 Quota Information:")
    print("- Default quota: 10,000 units per day")
    print("- videos.list() cost: 1 unit per request (up to 50 video IDs)")
    print("- search.list() cost: 100 units per request (avoid for known IDs)")
    print()
    
    # Demonstrate efficient usage
    video_ids = ["jNQXAC9IVRw", "_OBlgSz8sSM", "9bZkp7q19f0"]
    
    print(f"✓ Efficient: Getting {len(video_ids)} videos in 1 API call (1 quota unit)")
    
    # This uses only 1 quota unit regardless of the number of video IDs (up to 50)
    results = extractor.batch_extract(video_ids, strategy="api")
    successful = len([r for r in results if not r.get('error')])
    
    print(f"✓ Success rate: {successful}/{len(video_ids)}")
    print(f"✓ Quota cost: ~1 unit for {len(video_ids)} videos")
    print()
    
    print("Daily capacity with default quota:")
    print("- Individual requests: ~10,000 videos per day")
    print("- Batched requests: ~500,000 videos per day (50 per request)")


def example_api_error_handling():
    """Example showing API-specific error handling"""
    print("\n=== API Error Handling Example ===")
    
    # Test with various scenarios
    test_cases = [
        ("jNQXAC9IVRw", "Valid video ID"),
        ("invalid_id_123", "Invalid video ID format"),
        ("abcdefghijk", "Valid format but non-existent video"),
    ]
    
    extractor = YouTubeVideoInfoExtractor(strategy="api")
    
    if not extractor.test_api_key():
        print("⚠ API key not available, skipping API error handling example")
        return
    
    for video_id, description in test_cases:
        print(f"\nTesting: {description} ({video_id})")
        
        result = extractor.get_video_info(video_id)
        
        if result:
            print(f"✓ Success: {result['title'][:50]}")
        else:
            print("✗ Failed (expected for invalid IDs)")


def example_api_vs_alternatives():
    """Compare API results with alternative methods"""
    print("\n=== API vs Alternatives Comparison ===")
    
    video_id = "jNQXAC9IVRw"
    strategies = ["api", "yt_dlp", "pytubefix"]
    results = {}
    
    print(f"Comparing extraction methods for video: {video_id}")
    
    for strategy in strategies:
        print(f"\nTrying {strategy}...")
        
        try:
            extractor = YouTubeVideoInfoExtractor(strategy=strategy)
            
            if strategy == "api" and not extractor.test_api_key():
                print(f"  ⚠ {strategy}: API key not available")
                continue
            
            available = extractor.get_available_strategies()
            if strategy not in available:
                print(f"  ⚠ {strategy}: Not available (dependency missing)")
                continue
            
            result = extractor.get_video_info(video_id)
            
            if result:
                results[strategy] = result
                print(f"  ✓ {strategy}: Success")
                print(f"    Title: {result['title'][:50]}")
                print(f"    Views: {result.get('views', 'N/A')}")
                print(f"    Method: {result.get('extraction_method')}")
            else:
                print(f"  ✗ {strategy}: Failed")
                
        except Exception as e:
            print(f"  ✗ {strategy}: Error - {e}")
    
    # Compare results
    if len(results) > 1:
        print(f"\n=== Comparison Results ===")
        
        # Compare titles
        titles = {method: info['title'] for method, info in results.items()}
        if len(set(titles.values())) == 1:
            print("✓ All methods returned the same title")
        else:
            print("⚠ Title differences found:")
            for method, title in titles.items():
                print(f"  {method}: {title}")
        
        # Compare views
        views = {method: info.get('views') for method, info in results.items()}
        view_values = [v for v in views.values() if v is not None]
        if len(set(view_values)) <= 1:
            print("✓ View counts are consistent")
        else:
            print("⚠ View count differences found:")
            for method, view_count in views.items():
                print(f"  {method}: {view_count}")


if __name__ == "__main__":
    print("YouTube Data API v3 Usage Examples")
    print("=" * 50)
    print("Note: These examples require a valid YouTube Data API v3 key")
    print("Get your free API key at: https://console.cloud.google.com/")
    print("=" * 50)
    
    example_api_setup()
    example_api_batch_processing()
    example_api_quota_management()
    example_api_error_handling()
    example_api_vs_alternatives()
    
    print("\n" + "=" * 50)
    print("API examples completed!")
    print("\nRemember:")
    print("- API method is the most reliable and compliant")
    print("- Default quota: 10,000 units/day (very generous for most use cases)")
    print("- Batch requests for maximum efficiency")
    print("- Always handle errors gracefully")
