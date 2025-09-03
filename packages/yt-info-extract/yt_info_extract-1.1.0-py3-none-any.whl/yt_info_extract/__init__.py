"""
YouTube Video Information Extractor (yt_info_extract)

A robust Python library for extracting YouTube video metadata including title, description,
channel name, publication date, and view count with multiple extraction strategies.

Usage:
    # SDK/API Usage
    from yt_info_extract import YouTubeVideoInfoExtractor

    extractor = YouTubeVideoInfoExtractor(api_key="YOUR_API_KEY")
    info = extractor.get_video_info("jNQXAC9IVRw")

    # CLI Usage
    $ yt-info jNQXAC9IVRw
    $ yt-info -f json -o video_info.json jNQXAC9IVRw
    $ yt-info --batch video_ids.txt --output-dir output/

Features:
    - Extract video metadata from YouTube videos via video ID only
    - Multiple extraction strategies: YouTube Data API v3, yt-dlp, pytubefix
    - Automatic fallback between extraction methods
    - Batch processing for multiple videos
    - Multiple output formats: text, JSON, CSV
    - Command-line interface and Python library
    - Robust error handling and retry logic
"""

__version__ = "1.1.0"
__author__ = "Khaldoon Sinjab"
__email__ = "sinjab@gmail.com"
__description__ = "YouTube video information extraction with multiple strategies"

from typing import Dict, List, Optional, Union

# Main API exports
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
    validate_video_info,
)


# Convenience functions for common use cases
def get_video_info(
    video_input: str,
    api_key: Optional[str] = None,
    strategy: str = "auto",
    **extractor_options,
) -> Optional[Dict]:
    """
    Quick function to get video information.

    Args:
        video_input: YouTube video ID (11 characters)
        api_key: YouTube Data API v3 key (optional, gets from env if not provided)
        strategy: Extraction strategy ("auto", "api", "yt_dlp", "pytubefix")
        **extractor_options: Additional options for the extractor

    Returns:
        Dictionary containing video information

    Example:
        info = get_video_info("jNQXAC9IVRw")
        info = get_video_info("jNQXAC9IVRw", api_key="YOUR_KEY")
        info = get_video_info("jNQXAC9IVRw", strategy="yt_dlp")
    """
    extractor = YouTubeVideoInfoExtractor(api_key=api_key, strategy=strategy, **extractor_options)
    return extractor.get_video_info(video_input)


def get_video_info_batch(
    video_inputs: List[str],
    api_key: Optional[str] = None,
    strategy: str = "auto",
    delay_between_requests: float = 0.5,
    **extractor_options,
) -> List[Dict]:
    """
    Quick function to get information for multiple videos.

    Args:
        video_inputs: List of YouTube video IDs (11 characters each)
        api_key: YouTube Data API v3 key (optional, gets from env if not provided)
        strategy: Extraction strategy ("auto", "api", "yt_dlp", "pytubefix")
        delay_between_requests: Delay between requests to avoid rate limiting
        **extractor_options: Additional options for the extractor

    Returns:
        List of video information dictionaries

    Example:
        videos = ["jNQXAC9IVRw", "dQw4w9WgXcQ"]
        results = get_video_info_batch(videos)
        results = get_video_info_batch(videos, api_key="YOUR_KEY", strategy="api")
    """
    extractor = YouTubeVideoInfoExtractor(api_key=api_key, strategy=strategy, **extractor_options)
    return extractor.batch_extract(video_inputs, strategy, delay_between_requests)


def get_video_stats(
    video_input: str,
    api_key: Optional[str] = None,
    strategy: str = "auto",
    **extractor_options,
) -> Optional[Dict]:
    """
    Quick function to get formatted video statistics.

    Args:
        video_input: YouTube video ID (11 characters)
        api_key: YouTube Data API v3 key (optional, gets from env if not provided)
        strategy: Extraction strategy ("auto", "api", "yt_dlp", "pytubefix")
        **extractor_options: Additional options for the extractor

    Returns:
        Dictionary containing formatted video statistics

    Example:
        stats = get_video_stats("jNQXAC9IVRw")
        print(f"Title: {stats['title']}")
        print(f"Views: {stats['formatted_views']}")
    """
    video_info = get_video_info(video_input, api_key, strategy, **extractor_options)
    if video_info:
        return extract_video_stats(video_info)
    return None


def export_video_info(
    video_data: Union[Dict, List[Dict]], output_file: str, format_type: str = "json", **kwargs
) -> bool:
    """
    Quick function to export video information to file.

    Args:
        video_data: Single video info dict or list of video info dicts
        output_file: Path to output file
        format_type: Export format ("json" or "csv")
        **kwargs: Additional export options

    Returns:
        True if successful, False otherwise

    Example:
        info = get_video_info("jNQXAC9IVRw")
        export_video_info(info, "video.json")

        batch_results = get_video_info_batch(["jNQXAC9IVRw", "dQw4w9WgXcQ"])
        export_video_info(batch_results, "videos.csv", format_type="csv")
    """
    if format_type.lower() == "json":
        pretty = kwargs.get("pretty", True)
        return export_to_json(video_data, output_file, pretty)
    elif format_type.lower() == "csv":
        if isinstance(video_data, dict):
            video_data = [video_data]
        return export_to_csv(video_data, output_file)
    else:
        raise ValueError("format_type must be 'json' or 'csv'")


def test_extraction_methods() -> Dict[str, bool]:
    """
    Test availability of different extraction methods.

    Returns:
        Dictionary indicating which methods are available

    Example:
        methods = test_extraction_methods()
        print("Available methods:", [k for k, v in methods.items() if v])
    """
    extractor = YouTubeVideoInfoExtractor()

    return {
        "youtube_api": extractor.youtube_service is not None,
        "yt_dlp": "yt_dlp" in extractor.get_available_strategies(),
        "pytubefix": "pytubefix" in extractor.get_available_strategies(),
    }


# Module metadata
__all__ = [
    # Main class
    "YouTubeVideoInfoExtractor",
    # Utility functions
    "export_to_json",
    "export_to_csv",
    "load_video_ids_from_file",
    "format_views",
    "format_publication_date",
    "clean_description",
    "extract_video_stats",
    "create_summary_report",
    "validate_video_info",
    # Convenience functions
    "get_video_info",
    "get_video_info_batch",
    "get_video_stats",
    "export_video_info",
    "test_extraction_methods",
]
