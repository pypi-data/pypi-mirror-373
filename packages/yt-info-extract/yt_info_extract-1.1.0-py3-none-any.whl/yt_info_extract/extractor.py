#!/usr/bin/env python3
"""
YouTube Video Information Extractor
Multi-strategy implementation with YouTube Data API v3 as primary and fallback methods
"""

import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Union

# Import for different extraction strategies
try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

try:
    import yt_dlp

    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

try:
    from pytubefix import YouTube

    PYTUBEFIX_AVAILABLE = True
except ImportError:
    PYTUBEFIX_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class YouTubeVideoInfoExtractor:
    """
    YouTube video information extractor with multi-strategy approach.

    Primary strategy: YouTube Data API v3 (official, reliable, requires API key)
    Fallback strategies: yt-dlp, pytubefix (unofficial, no API key required)

    Features:
    - Extract video title, description, channel name, publication date, and views
    - Multi-strategy extraction with automatic fallback
    - Support for YouTube video IDs only
    - Rate limiting and error handling
    - Configurable timeout and retry logic

    Example:
        # Using API key (recommended)
        extractor = YouTubeVideoInfoExtractor(api_key="YOUR_API_KEY")
        info = extractor.get_video_info("jNQXAC9IVRw")

        # Using fallback methods (no API key)
        extractor = YouTubeVideoInfoExtractor()
        info = extractor.get_video_info("jNQXAC9IVRw")
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        strategy: str = "auto",  # "api", "yt_dlp", "pytubefix", "auto"
        timeout: float = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.75,
        rate_limit_delay: float = 0.1,
    ):
        """
        Initialize the YouTube video info extractor.

        Args:
            api_key: YouTube Data API v3 key (optional, gets from env if not provided)
            strategy: Extraction strategy ("auto", "api", "yt_dlp", "pytubefix")
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff factor for retries
            rate_limit_delay: Delay between requests to avoid rate limiting
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.rate_limit_delay = rate_limit_delay
        self.strategy = strategy.lower()

        # Set up API key
        self.api_key = api_key or os.environ.get("YOUTUBE_API_KEY")

        # Initialize YouTube API service if available and API key provided
        self.youtube_service = None
        if GOOGLE_API_AVAILABLE and self.api_key:
            try:
                self.youtube_service = build("youtube", "v3", developerKey=self.api_key)
                logger.info("YouTube Data API v3 service initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize YouTube API service: {e}")

        # Validate strategy
        valid_strategies = ["auto", "api", "yt_dlp", "pytubefix"]
        if self.strategy not in valid_strategies:
            raise ValueError(f"Invalid strategy. Must be one of: {valid_strategies}")

        # Check availability of fallback methods
        if self.strategy == "yt_dlp" and not YT_DLP_AVAILABLE:
            raise ImportError("yt-dlp is not installed. Install with: pip install yt-dlp")

        if self.strategy == "pytubefix" and not PYTUBEFIX_AVAILABLE:
            raise ImportError("pytubefix is not installed. Install with: pip install pytubefix")

    def _validate_video_id(self, video_id: str) -> Optional[str]:
        """
        Validate YouTube video ID format.

        Args:
            video_id: YouTube video ID

        Returns:
            Video ID if valid, None if invalid
        """
        import re

        # YouTube video IDs are exactly 11 characters and contain only alphanumeric, underscore, and hyphen
        if len(video_id) == 11 and re.match(r"^[A-Za-z0-9_-]{11}$", video_id):
            return video_id

        logger.error(
            f"Invalid video ID format: {video_id}. Must be exactly 11 characters (A-Z, a-z, 0-9, _, -)"
        )
        return None

    def _get_video_info_api(self, video_id: str) -> Optional[Dict]:
        """
        Extract video information using YouTube Data API v3.

        Args:
            video_id: YouTube video ID

        Returns:
            Video information dictionary or None on failure
        """
        if not self.youtube_service:
            logger.error("YouTube API service not available")
            return None

        try:
            # Construct the request
            request = self.youtube_service.videos().list(part="snippet,statistics", id=video_id)

            # Execute the request
            response = request.execute()

            if not response.get("items"):
                logger.error(f"No video found with ID: {video_id}")
                return None

            # Parse the response
            video_item = response["items"][0]
            snippet = video_item.get("snippet", {})
            statistics = video_item.get("statistics", {})

            return {
                "title": snippet.get("title"),
                "description": snippet.get("description"),
                "channel_name": snippet.get("channelTitle"),
                "publication_date": snippet.get("publishedAt"),
                "views": (
                    int(statistics.get("viewCount", 0)) if statistics.get("viewCount") else None
                ),
                "extraction_method": "youtube_api",
            }

        except HttpError as e:
            logger.error(f"YouTube API HTTP error {e.resp.status}: {e.content}")
            return None
        except Exception as e:
            logger.error(f"YouTube API unexpected error: {e}")
            return None

    def _get_video_info_yt_dlp(self, video_id: str) -> Optional[Dict]:
        """
        Extract video information using yt-dlp.

        Args:
            video_id: YouTube video ID

        Returns:
            Video information dictionary or None on failure
        """
        if not YT_DLP_AVAILABLE:
            logger.error("yt-dlp is not available")
            return None

        video_url = f"https://www.youtube.com/watch?v={video_id}"

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                sanitized_info = ydl.sanitize_info(info)

                # Convert upload_date to ISO format
                publication_date = None
                upload_date_str = sanitized_info.get("upload_date")
                if upload_date_str:
                    publication_date = datetime.strptime(upload_date_str, "%Y%m%d").isoformat()

                return {
                    "title": sanitized_info.get("title"),
                    "description": sanitized_info.get("description"),
                    "channel_name": sanitized_info.get("channel") or sanitized_info.get("uploader"),
                    "publication_date": publication_date,
                    "views": sanitized_info.get("view_count"),
                    "extraction_method": "yt_dlp",
                }

        except yt_dlp.utils.DownloadError as e:
            logger.error(f"yt-dlp download error: {e}")
            return None
        except Exception as e:
            logger.error(f"yt-dlp unexpected error: {e}")
            return None

    def _get_video_info_pytubefix(self, video_id: str) -> Optional[Dict]:
        """
        Extract video information using pytubefix.

        Args:
            video_id: YouTube video ID

        Returns:
            Video information dictionary or None on failure
        """
        if not PYTUBEFIX_AVAILABLE:
            logger.error("pytubefix is not available")
            return None

        video_url = f"https://www.youtube.com/watch?v={video_id}"

        try:
            yt = YouTube(video_url)

            return {
                "title": yt.title,
                "description": yt.description,
                "channel_name": yt.author,
                "publication_date": yt.publish_date.isoformat() if yt.publish_date else None,
                "views": yt.views,
                "extraction_method": "pytubefix",
            }

        except Exception as e:
            logger.error(f"pytubefix error: {e}")
            return None

    def get_video_info(self, video_input: str, strategy: Optional[str] = None) -> Optional[Dict]:
        """
        Extract video information using the specified or default strategy.

        Args:
            video_input: YouTube video ID (11 characters)
            strategy: Override default strategy ("api", "yt_dlp", "pytubefix", "auto")

        Returns:
            Dictionary containing video information:
            {
                "title": str,
                "description": str,
                "channel_name": str,
                "publication_date": str (ISO format),
                "views": int,
                "extraction_method": str
            }
        """
        # Extract video ID
        video_id = self._validate_video_id(video_input)
        if not video_id:
            logger.error(f"Invalid video input: {video_input}")
            return None

        # Determine strategy
        use_strategy = strategy or self.strategy

        # Rate limiting
        time.sleep(self.rate_limit_delay)

        result = None

        if use_strategy == "auto":
            # Try strategies in order of preference: API -> yt-dlp -> pytubefix
            strategies = []

            if self.youtube_service:
                strategies.append("api")
            if YT_DLP_AVAILABLE:
                strategies.append("yt_dlp")
            if PYTUBEFIX_AVAILABLE:
                strategies.append("pytubefix")

            if not strategies:
                logger.error(
                    "No extraction methods available. Install dependencies or provide API key."
                )
                return None

            for strat in strategies:
                logger.info(f"Attempting extraction with strategy: {strat}")
                result = self._extract_with_retry(video_id, strat)
                if result:
                    break

        else:
            # Use specific strategy
            result = self._extract_with_retry(video_id, use_strategy)

        if result:
            logger.info(
                f"Successfully extracted info for video {video_id} using {result.get('extraction_method')}"
            )
            return result
        else:
            logger.error(f"Failed to extract video information for {video_id}")
            return None

    def _extract_with_retry(self, video_id: str, strategy: str) -> Optional[Dict]:
        """
        Extract with retry logic.

        Args:
            video_id: YouTube video ID
            strategy: Extraction strategy

        Returns:
            Video information or None
        """
        for attempt in range(self.max_retries):
            try:
                if strategy == "api":
                    result = self._get_video_info_api(video_id)
                elif strategy == "yt_dlp":
                    result = self._get_video_info_yt_dlp(video_id)
                elif strategy == "pytubefix":
                    result = self._get_video_info_pytubefix(video_id)
                else:
                    logger.error(f"Unknown strategy: {strategy}")
                    return None

                if result:
                    return result

            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed with {strategy}: {e}")

            # Exponential backoff
            if attempt < self.max_retries - 1:
                delay = self.backoff_factor**attempt
                logger.info(f"Retrying in {delay:.2f} seconds...")
                time.sleep(delay)

        return None

    def get_available_strategies(self) -> List[str]:
        """
        Get list of available extraction strategies.

        Returns:
            List of available strategy names
        """
        strategies = []

        if self.youtube_service:
            strategies.append("api")
        if YT_DLP_AVAILABLE:
            strategies.append("yt_dlp")
        if PYTUBEFIX_AVAILABLE:
            strategies.append("pytubefix")

        return strategies

    def test_api_key(self) -> bool:
        """
        Test if the YouTube API key is valid by making a simple request.

        Returns:
            True if API key is valid, False otherwise
        """
        if not self.youtube_service:
            return False

        try:
            # Test with a well-known video ID
            request = self.youtube_service.videos().list(part="snippet", id="jNQXAC9IVRw")
            response = request.execute()
            return len(response.get("items", [])) > 0
        except Exception as e:
            logger.error(f"API key test failed: {e}")
            return False

    def batch_extract(
        self,
        video_inputs: List[str],
        strategy: Optional[str] = None,
        delay_between_requests: float = 0.5,
    ) -> List[Dict]:
        """
        Extract information for multiple videos.

        Args:
            video_inputs: List of YouTube video IDs (11 characters each)
            strategy: Override default strategy
            delay_between_requests: Delay between requests to avoid rate limiting

        Returns:
            List of video information dictionaries
        """
        results = []

        for i, video_input in enumerate(video_inputs):
            logger.info(f"Processing video {i + 1}/{len(video_inputs)}: {video_input}")

            result = self.get_video_info(video_input, strategy)
            if result:
                results.append(result)
            else:
                logger.warning(f"Failed to extract info for video: {video_input}")
                results.append(
                    {
                        "video_id": self._validate_video_id(video_input),
                        "error": "Extraction failed",
                        "extraction_method": None,
                    }
                )

            # Rate limiting between requests
            if i < len(video_inputs) - 1:
                time.sleep(delay_between_requests)

        return results
