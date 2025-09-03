: {info['title']}")
            else:
                print(f"✗ Failed with {strategy}")
                
        except Exception as e:
            print(f"✗ Error with {strategy}: {e}")


def example_batch_processing():
    """Example of processing multiple videos"""
    print("\n=== Batch Processing Example ===")
    
    # List of video IDs to process
    video_ids = [
        "jNQXAC9IVRw",  # Me at the zoo
        "dQw4w9WgXcQ",  # Rick Roll (if you want to test)
        "_OBlgSz8sSM",  # Charlie bit my finger
    ]
    
    print(f"Processing {len(video_ids)} videos...")
    
    # Using convenience function
    from yt_info_extract import get_video_info_batch
    
    results = get_video_info_batch(
        video_ids, 
        delay_between_requests=1.0  # Be nice to YouTube's servers
    )
    
    print(f"\nResults summary:")
    successful = len([r for r in results if not r.get('error')])
    print(f"Successful: {successful}/{len(results)}")
    
    for i, result in enumerate(results):
        if result.get('error'):
            print(f"{i+1}. ERROR: {result.get('error')}")
        else:
            title = result['title'][:50] + "..." if len(result['title']) > 50 else result['title']
            views = result.get('views', 0)
            method = result.get('extraction_method', 'unknown')
            print(f"{i+1}. {title} | {views:,} views | {method}")


def example_formatted_stats():
    """Example showing formatted statistics"""
    print("\n=== Formatted Stats Example ===")
    
    video_id = "jNQXAC9IVRw"
    
    # Get formatted stats
    stats = get_video_stats(video_id)
    
    if stats:
        print("Formatted Video Statistics:")
        print(f"  Title: {stats['title']}")
        print(f"  Channel: {stats['channel']}")
        print(f"  Views: {stats['formatted_views']}")
        print(f"  Published: {stats['formatted_date']}")
        print(f"  Description Length: {stats['description_length']} characters")
        print(f"  Has Description: {'Yes' if stats['has_description'] else 'No'}")
        print(f"  Extraction Method: {stats['extraction_method']}")


def example_export_data():
    """Example of exporting data to files"""
    print("\n=== Export Data Example ===")
    
    video_id = "jNQXAC9IVRw"
    
    # Get video info
    info = get_video_info(video_id)
    
    if info:
        # Export to JSON
        json_success = export_video_info(info, "video_info.json", format_type="json")
        if json_success:
            print("✓ Exported to video_info.json")
        
        # Export to CSV (needs to be in a list for CSV)
        csv_success = export_video_info([info], "video_info.csv", format_type="csv")
        if csv_success:
            print("✓ Exported to video_info.csv")
        
        # You can also export batch results
        batch_results = get_video_info_batch([video_id, "dQw4w9WgXcQ"])
        export_video_info(batch_results, "batch_results.json")
        export_video_info(batch_results, "batch_results.csv", format_type="csv")
        print("✓ Exported batch results")


def example_error_handling():
    """Example showing error handling"""
    print("\n=== Error Handling Example ===")
    
    # Try with invalid video ID
    invalid_id = "invalid123"
    print(f"Trying invalid video ID: {invalid_id}")
    
    info = get_video_info(invalid_id)
    if info:
        print("Unexpectedly got info!")
    else:
        print("✓ Correctly handled invalid video ID")
    
    # Try with private/deleted video (example ID)
    private_id = "privateVideo"  # This won't work
    print(f"Trying potentially problematic video ID: {private_id}")
    
    info = get_video_info(private_id)
    if info:
        print(f"Got info: {info['title']}")
    else:
        print("✓ Handled problematic video gracefully")


def example_url_formats():
    """Example showing different URL format support"""
    print("\n=== URL Format Support Example ===")
    
    # Different URL formats for the same video
    formats = [
        "jNQXAC9IVRw",  # Just the ID
        "https://www.youtube.com/watch?v=jNQXAC9IVRw",  # Standard URL
        "https://youtu.be/jNQXAC9IVRw",  # Short URL
        "https://www.youtube.com/embed/jNQXAC9IVRw",  # Embed URL
    ]
    
    print("Testing different URL formats for the same video:")
    
    for fmt in formats:
        print(f"\nFormat: {fmt}")
        info = get_video_info(fmt)
        
        if info:
            print(f"✓ Success: {info['title'][:50]}...")
            print(f"  Method: {info['extraction_method']}")
        else:
            print("✗ Failed")


if __name__ == "__main__":
    print("YouTube Video Information Extractor - Basic Usage Examples")
    print("=" * 60)
    
    # Run examples
    example_basic_usage()
    example_fallback_strategies()
    example_batch_processing()
    example_formatted_stats()
    example_export_data()
    example_error_handling()
    example_url_formats()
    
    # Uncomment to test with API key
    # example_with_api_key()
    
    print("\n" + "=" * 60)
    print("Examples completed! Check the generated files:")
    print("- video_info.json")
    print("- video_info.csv")
    print("- batch_results.json")
    print("- batch_results.csv")
