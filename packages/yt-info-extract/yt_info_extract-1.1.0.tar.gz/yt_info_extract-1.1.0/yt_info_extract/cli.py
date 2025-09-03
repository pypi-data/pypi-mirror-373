#!/usr/bin/env python3
"""
YouTube Video Information Extractor - Command Line Interface
CLI for extracting video metadata with various output formats and strategies.
"""

import argparse
import os
import sys
from pathlib import Path

from .extractor import YouTubeVideoInfoExtractor
from .utils import (
    clean_description,
    create_summary_report,
    export_to_csv,
    export_to_json,
    extract_video_stats,
    format_publication_date,
    format_views,
    load_video_ids_from_file,
)


def print_video_info(video_info, format_type="text"):
    """Print video information in specified format"""
    if not video_info or video_info.get("error"):
        print(f"❌ Failed to extract video information")
        if video_info and video_info.get("error"):
            print(f"   Error: {video_info['error']}")
        return

    if format_type == "text":
        print(f"📹 Title: {video_info.get('title', 'N/A')}")
        print(f"📺 Channel: {video_info.get('channel_name', 'N/A')}")
        print(f"👀 Views: {format_views(video_info.get('views'))}")
        print(f"📅 Published: {format_publication_date(video_info.get('publication_date'))}")
        print(f"🔧 Method: {video_info.get('extraction_method', 'N/A')}")

        description = video_info.get("description")
        if description:
            cleaned_desc = clean_description(description, 200)
            print(f"📝 Description: {cleaned_desc}")
        else:
            print("📝 Description: Not available")

    elif format_type == "compact":
        title = (
            video_info.get("title", "N/A")[:50] + "..."
            if len(video_info.get("title", "")) > 50
            else video_info.get("title", "N/A")
        )
        channel = video_info.get("channel_name", "N/A")
        views = format_views(video_info.get("views"))
        method = video_info.get("extraction_method", "N/A")
        print(f"{title} | {channel} | {views} | {method}")

    elif format_type == "stats":
        stats = extract_video_stats(video_info)
        print("Video Statistics:")
        print(f"  Title: {stats['title']}")
        print(f"  Channel: {stats['channel']}")
        print(f"  Views: {stats['formatted_views']} ({stats['raw_views']:,})")
        print(f"  Published: {stats['formatted_date']}")
        print(f"  Description Length: {stats['description_length']} characters")
        print(f"  Has Description: {'Yes' if stats['has_description'] else 'No'}")
        print(f"  Extraction Method: {stats['extraction_method']}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Extract video information from YouTube videos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s jNQXAC9IVRw
  %(prog)s -f json -o video_info.json jNQXAC9IVRw
  %(prog)s -s yt_dlp jNQXAC9IVRw
  %(prog)s --batch video_ids.txt --output-dir output/
  %(prog)s --api-key YOUR_KEY jNQXAC9IVRw
  
🔑 API Key Examples:
  %(prog)s --api-key "AIza..." jNQXAC9IVRw
  export YOUTUBE_API_KEY="AIza..."; %(prog)s jNQXAC9IVRw
  
📊 Output Format Examples:
  %(prog)s -f stats jNQXAC9IVRw
  %(prog)s -f compact jNQXAC9IVRw
  %(prog)s -f json --pretty jNQXAC9IVRw
        """,
    )

    # Positional arguments
    parser.add_argument("video_input", nargs="?", help="YouTube video ID (11 characters)")

    # API and strategy options
    parser.add_argument(
        "--api-key", help="YouTube Data API v3 key (or set YOUTUBE_API_KEY env var)"
    )

    parser.add_argument(
        "-s",
        "--strategy",
        choices=["auto", "api", "yt_dlp", "pytubefix"],
        default="auto",
        help="Extraction strategy (default: auto)",
    )

    # Output format options
    parser.add_argument(
        "-f",
        "--format",
        choices=["text", "compact", "stats", "json", "csv"],
        default="text",
        help="Output format (default: text)",
    )

    parser.add_argument("-o", "--output", help="Output file path (required for json/csv formats)")

    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")

    # Batch processing
    parser.add_argument("--batch", help="Path to file containing video IDs (one per line)")

    parser.add_argument("--output-dir", help="Output directory for batch processing")

    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Delay between requests in batch mode (seconds, default: 0.5)",
    )

    # Testing and info options
    parser.add_argument("--test-api", action="store_true", help="Test API key validity and exit")

    parser.add_argument(
        "--list-strategies",
        action="store_true",
        help="List available extraction strategies and exit",
    )

    parser.add_argument(
        "--summary", action="store_true", help="Generate summary report for batch processing"
    )

    # Advanced options
    parser.add_argument(
        "--timeout", type=float, default=30, help="Request timeout in seconds (default: 30)"
    )

    parser.add_argument(
        "--retries", type=int, default=3, help="Maximum number of retries (default: 3)"
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    # Set up logging
    if args.verbose:
        import logging

        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize extractor
    try:
        extractor = YouTubeVideoInfoExtractor(
            api_key=args.api_key,
            strategy=args.strategy,
            timeout=args.timeout,
            max_retries=args.retries,
        )
    except Exception as e:
        print(f"❌ Failed to initialize extractor: {e}")
        return 1

    # Handle info commands
    if args.test_api:
        if extractor.test_api_key():
            print("✅ API key is valid")
            return 0
        else:
            print("❌ API key is invalid or not provided")
            return 1

    if args.list_strategies:
        strategies = extractor.get_available_strategies()
        print("Available extraction strategies:")
        for strategy in strategies:
            print(f"  • {strategy}")
        if not strategies:
            print("  No strategies available. Install dependencies or provide API key.")
        return 0

    # Validate arguments
    if not args.batch and not args.video_input:
        parser.error("Either provide a video_input or use --batch option")

    if args.format in ["json", "csv"] and not args.output and not args.batch:
        parser.error(f"--output is required for {args.format} format")

    # Single video processing
    if args.video_input:
        print(f"🔍 Extracting information for: {args.video_input}")

        video_info = extractor.get_video_info(args.video_input)

        if not video_info:
            print("❌ Failed to extract video information")
            return 1

        # Handle output formats
        if args.format == "json":
            if args.output:
                success = export_to_json(video_info, args.output, args.pretty)
                if success:
                    print(f"✅ Exported to {args.output}")
                else:
                    return 1
            else:
                import json

                if args.pretty:
                    print(json.dumps(video_info, ensure_ascii=False, indent=2))
                else:
                    print(json.dumps(video_info, ensure_ascii=False))

        elif args.format == "csv":
            success = export_to_csv([video_info], args.output)
            if success:
                print(f"✅ Exported to {args.output}")
            else:
                return 1

        else:
            print_video_info(video_info, args.format)

    # Batch processing
    elif args.batch:
        print(f"📋 Loading video IDs from: {args.batch}")

        video_ids = load_video_ids_from_file(args.batch)
        if not video_ids:
            print("❌ No video IDs loaded")
            return 1

        print(f"🔄 Processing {len(video_ids)} videos...")

        results = extractor.batch_extract(video_ids, args.strategy, args.delay)

        # Handle batch output
        if args.output_dir:
            output_dir = Path(args.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Export results
            if args.format == "json":
                output_file = output_dir / "batch_results.json"
                export_to_json(results, str(output_file), args.pretty)
            elif args.format == "csv":
                output_file = output_dir / "batch_results.csv"
                export_to_csv(results, str(output_file))
            else:
                # Export as both for convenience
                json_file = output_dir / "batch_results.json"
                csv_file = output_dir / "batch_results.csv"
                export_to_json(results, str(json_file), True)
                export_to_csv(results, str(csv_file))

            print(f"✅ Batch results saved to {output_dir}")

        # Generate summary
        if args.summary:
            print("\n📊 SUMMARY REPORT")
            print("=" * 50)

            summary = create_summary_report(results)

            print(f"Total videos processed: {summary['total_videos_processed']}")
            print(f"Successful extractions: {summary['successful_extractions']}")
            print(f"Failed extractions: {summary['failed_extractions']}")
            print(f"Success rate: {summary['success_rate']}")

            print(f"\n👀 View Statistics:")
            view_stats = summary["view_statistics"]
            print(f"  Total views: {view_stats['formatted_total']}")
            print(f"  Average views: {view_stats['formatted_average']}")

            print(f"\n🔧 Extraction Methods:")
            for method, count in summary["extraction_methods"].items():
                print(f"  {method}: {count} videos")

            if summary["top_channels"]:
                print(f"\n📺 Top Channels:")
                for channel, count in list(summary["top_channels"].items())[:5]:
                    print(f"  {channel}: {count} videos")

        # Show sample results
        successful_results = [r for r in results if not r.get("error")]
        if successful_results:
            print(f"\n📋 Sample results (showing first 3):")
            for i, result in enumerate(successful_results[:3]):
                print(f"\n{i+1}. {result.get('title', 'N/A')}")
                print(f"   Channel: {result.get('channel_name', 'N/A')}")
                print(f"   Views: {format_views(result.get('views'))}")
                print(f"   Method: {result.get('extraction_method', 'N/A')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
