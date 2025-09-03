#!/usr/bin/env python3
"""
Utility functions for YouTube video information extraction and processing
"""

import csv
import json
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


def format_views(view_count: Optional[int]) -> str:
    """
    Format view count in human-readable format.

    Args:
        view_count: Number of views

    Returns:
        Formatted view count string (e.g., "1.2M views", "1,234 views")
    """
    if view_count is None:
        return "Unknown views"

    if view_count >= 1_000_000_000:
        return f"{view_count / 1_000_000_000:.1f}B views"
    elif view_count >= 1_000_000:
        return f"{view_count / 1_000_000:.1f}M views"
    elif view_count >= 1_000:
        return f"{view_count / 1_000:.1f}K views"
    else:
        return f"{view_count:,} views"


def format_publication_date(pub_date: Optional[str]) -> str:
    """
    Format publication date in human-readable format.

    Args:
        pub_date: ISO format date string

    Returns:
        Formatted date string
    """
    if not pub_date:
        return "Unknown date"

    try:
        # Handle both with and without timezone
        if pub_date.endswith("Z"):
            dt = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
        elif "+" in pub_date or pub_date.count("-") > 2:
            dt = datetime.fromisoformat(pub_date)
        else:
            dt = datetime.fromisoformat(pub_date)

        return dt.strftime("%B %d, %Y")
    except (ValueError, AttributeError) as e:
        logger.warning(f"Could not parse date {pub_date}: {e}")
        return pub_date


def clean_description(description: Optional[str], max_length: int = 500) -> str:
    """
    Clean and truncate video description.

    Args:
        description: Raw video description
        max_length: Maximum length of cleaned description

    Returns:
        Cleaned description
    """
    if not description:
        return "No description available"

    # Remove excessive whitespace
    cleaned = re.sub(r"\s+", " ", description.strip())

    # Truncate if too long
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length].strip() + "..."

    return cleaned


def extract_video_stats(video_info: Dict) -> Dict[str, Any]:
    """
    Extract and format video statistics.

    Args:
        video_info: Video information dictionary

    Returns:
        Dictionary with formatted statistics
    """
    return {
        "title": video_info.get("title", "Unknown"),
        "channel": video_info.get("channel_name", "Unknown"),
        "formatted_views": format_views(video_info.get("views")),
        "raw_views": video_info.get("views"),
        "formatted_date": format_publication_date(video_info.get("publication_date")),
        "raw_date": video_info.get("publication_date"),
        "description_preview": clean_description(video_info.get("description"), 200),
        "extraction_method": video_info.get("extraction_method", "Unknown"),
        "has_description": bool(video_info.get("description")),
        "description_length": len(video_info.get("description", "")),
    }


def export_to_json(
    video_data: Union[Dict, List[Dict]], output_file: str, pretty: bool = True
) -> bool:
    """
    Export video information to JSON file.

    Args:
        video_data: Single video info dict or list of video info dicts
        output_file: Path to output JSON file
        pretty: Whether to format JSON with indentation

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            if pretty:
                json.dump(video_data, f, ensure_ascii=False, indent=2)
            else:
                json.dump(video_data, f, ensure_ascii=False)

        logger.info(f"Successfully exported data to {output_file}")
        return True

    except Exception as e:
        logger.error(f"Failed to export to JSON: {e}")
        return False


def export_to_csv(video_data: List[Dict], output_file: str) -> bool:
    """
    Export video information to CSV file.

    Args:
        video_data: List of video information dictionaries
        output_file: Path to output CSV file

    Returns:
        True if successful, False otherwise
    """
    if not video_data:
        logger.error("No data to export")
        return False

    try:
        # Define CSV columns
        fieldnames = [
            "title",
            "channel_name",
            "views",
            "publication_date",
            "description",
            "extraction_method",
        ]

        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()

            for video in video_data:
                # Clean data for CSV
                row = {}
                for field in fieldnames:
                    value = video.get(field, "")
                    # Handle None values and clean strings
                    if value is None:
                        row[field] = ""
                    elif isinstance(value, str):
                        # Clean multiline descriptions for CSV
                        row[field] = value.replace("\n", " ").replace("\r", " ")
                    else:
                        row[field] = str(value)

                writer.writerow(row)

        logger.info(f"Successfully exported data to {output_file}")
        return True

    except Exception as e:
        logger.error(f"Failed to export to CSV: {e}")
        return False


def load_video_ids_from_file(file_path: str) -> List[str]:
    """
    Load video IDs from a text file (one per line).

    Args:
        file_path: Path to text file containing video IDs

    Returns:
        List of video IDs
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            # Read lines and filter out empty ones
            video_ids = [line.strip() for line in f.readlines() if line.strip()]

        logger.info(f"Loaded {len(video_ids)} video IDs from {file_path}")
        return video_ids

    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return []
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return []


def validate_video_info(video_info: Dict) -> Dict[str, Any]:
    """
    Validate and normalize video information.

    Args:
        video_info: Video information dictionary

    Returns:
        Dictionary with validation results and normalized data
    """
    validation = {"is_valid": True, "errors": [], "warnings": [], "normalized_data": {}}

    # Check required fields
    required_fields = ["title", "channel_name"]
    for field in required_fields:
        if not video_info.get(field):
            validation["errors"].append(f"Missing or empty required field: {field}")
            validation["is_valid"] = False

    # Check optional but important fields
    if not video_info.get("views"):
        validation["warnings"].append("View count is missing")

    if not video_info.get("publication_date"):
        validation["warnings"].append("Publication date is missing")

    if not video_info.get("description"):
        validation["warnings"].append("Description is missing")

    # Normalize data
    validation["normalized_data"] = {
        "title": str(video_info.get("title", "")).strip(),
        "channel_name": str(video_info.get("channel_name", "")).strip(),
        "views": video_info.get("views") if isinstance(video_info.get("views"), int) else None,
        "publication_date": video_info.get("publication_date"),
        "description": (
            str(video_info.get("description", "")).strip()
            if video_info.get("description")
            else None
        ),
        "extraction_method": video_info.get("extraction_method", "unknown"),
    }

    return validation


def create_summary_report(video_data_list: List[Dict]) -> Dict[str, Any]:
    """
    Create a summary report from a list of video information.

    Args:
        video_data_list: List of video information dictionaries

    Returns:
        Summary report dictionary
    """
    if not video_data_list:
        return {"error": "No video data provided"}

    total_videos = len(video_data_list)
    successful_extractions = len([v for v in video_data_list if not v.get("error")])

    # Statistics
    total_views = 0
    view_counts = []
    extraction_methods = {}
    channels = {}
    dates = []

    for video in video_data_list:
        if video.get("error"):
            continue

        # Views
        if video.get("views"):
            total_views += video["views"]
            view_counts.append(video["views"])

        # Extraction methods
        method = video.get("extraction_method", "unknown")
        extraction_methods[method] = extraction_methods.get(method, 0) + 1

        # Channels
        channel = video.get("channel_name", "Unknown")
        channels[channel] = channels.get(channel, 0) + 1

        # Dates
        if video.get("publication_date"):
            dates.append(video["publication_date"])

    # Calculate statistics
    avg_views = total_views / len(view_counts) if view_counts else 0
    max_views = max(view_counts) if view_counts else 0
    min_views = min(view_counts) if view_counts else 0

    return {
        "total_videos_processed": total_videos,
        "successful_extractions": successful_extractions,
        "failed_extractions": total_videos - successful_extractions,
        "success_rate": (
            f"{(successful_extractions / total_videos) * 100:.1f}%" if total_videos > 0 else "0%"
        ),
        "view_statistics": {
            "total_views": total_views,
            "average_views": int(avg_views),
            "max_views": max_views,
            "min_views": min_views,
            "formatted_total": format_views(total_views),
            "formatted_average": format_views(int(avg_views)),
        },
        "extraction_methods": extraction_methods,
        "top_channels": dict(sorted(channels.items(), key=lambda x: x[1], reverse=True)[:10]),
        "date_range": {
            "earliest": min(dates) if dates else None,
            "latest": max(dates) if dates else None,
            "total_videos_with_dates": len(dates),
        },
    }
