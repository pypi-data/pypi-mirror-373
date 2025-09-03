#!/usr/bin/env python3
"""
Tests to fill coverage gaps
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import yt_info_extract.cli
import yt_info_extract.extractor
from yt_info_extract import YouTubeVideoInfoExtractor
from yt_info_extract.cli import main


class TestCoverageGaps:
    """Tests to improve coverage for missed lines"""

    @patch("yt_info_extract.extractor.YT_DLP_AVAILABLE", False)
    @patch("yt_info_extract.extractor.PYTUBEFIX_AVAILABLE", False)
    @patch("yt_info_extract.extractor.GOOGLE_API_AVAILABLE", False)
    def test_no_extraction_methods_available(self):
        """Test when no extraction methods are available"""
        extractor = YouTubeVideoInfoExtractor()

        # Should have no available strategies
        strategies = extractor.get_available_strategies()
        assert strategies == []

        # Auto strategy should fail when no methods available
        result = extractor.get_video_info("jNQXAC9IVRw", strategy="auto")
        assert result is None

    @patch("yt_info_extract.extractor.build")
    def test_api_generic_error(self, mock_build):
        """Test API extraction with generic error"""
        mock_service = MagicMock()
        mock_videos = MagicMock()
        mock_list = MagicMock()
        mock_request = MagicMock()

        mock_build.return_value = mock_service
        mock_service.videos.return_value = mock_videos
        mock_videos.list.return_value = mock_request

        # Mock generic error
        mock_request.execute.side_effect = Exception("Network error")

        extractor = YouTubeVideoInfoExtractor(api_key="test_key")
        result = extractor._get_video_info_api("jNQXAC9IVRw")

        assert result is None

    @patch("yt_info_extract.extractor.yt_dlp.YoutubeDL")
    @patch("yt_info_extract.extractor.YT_DLP_AVAILABLE", True)
    def test_yt_dlp_download_error(self, mock_yt_dlp_class):
        """Test yt-dlp extraction with download error"""
        mock_yt_dlp = MagicMock()
        mock_yt_dlp_class.return_value.__enter__.return_value = mock_yt_dlp

        # Mock download error
        import yt_dlp

        mock_yt_dlp.extract_info.side_effect = yt_dlp.utils.DownloadError("Video unavailable")

        extractor = YouTubeVideoInfoExtractor()
        result = extractor._get_video_info_yt_dlp("jNQXAC9IVRw")

        assert result is None

    @patch("yt_info_extract.extractor.YouTube")
    @patch("yt_info_extract.extractor.PYTUBEFIX_AVAILABLE", True)
    def test_pytubefix_error(self, mock_youtube_class):
        """Test pytubefix extraction with error"""
        mock_youtube_class.side_effect = Exception("Connection error")

        extractor = YouTubeVideoInfoExtractor()
        result = extractor._get_video_info_pytubefix("jNQXAC9IVRw")

        assert result is None

    @patch("yt_info_extract.extractor.YouTube")
    @patch("yt_info_extract.extractor.PYTUBEFIX_AVAILABLE", True)
    def test_pytubefix_no_publish_date(self, mock_youtube_class):
        """Test pytubefix extraction with no publish date"""
        mock_youtube = MagicMock()
        mock_youtube_class.return_value = mock_youtube

        mock_youtube.title = "Test Video"
        mock_youtube.description = "Test description"
        mock_youtube.author = "Test Channel"
        mock_youtube.publish_date = None  # No publish date
        mock_youtube.views = 1000

        extractor = YouTubeVideoInfoExtractor()
        result = extractor._get_video_info_pytubefix("jNQXAC9IVRw")

        assert result is not None
        assert result["publication_date"] is None

    def test_batch_extract_with_errors(self):
        """Test batch extraction with mixed results"""
        extractor = YouTubeVideoInfoExtractor()

        with patch.object(extractor, "get_video_info") as mock_get_info:
            # Mock results: success, failure, success
            mock_get_info.side_effect = [
                {"title": "Video 1", "views": 1000},
                None,  # Failure
                {"title": "Video 3", "views": 3000},
            ]

            # Use valid video IDs that won't fail ID extraction
            video_ids = ["jNQXAC9IVRw", "dQw4w9WgXcQ", "kJQP7kiw5Fk"]
            results = extractor.batch_extract(video_ids)

            assert len(results) == 3
            assert results[0]["title"] == "Video 1"
            assert results[1]["error"] == "Extraction failed"
            assert results[1]["video_id"] == "dQw4w9WgXcQ"
            assert results[2]["title"] == "Video 3"


class TestCLICoverage:
    """Test CLI coverage gaps"""

    @patch("yt_info_extract.cli.YouTubeVideoInfoExtractor")
    @patch("yt_info_extract.cli.load_video_ids_from_file")
    @patch("yt_info_extract.cli.export_to_json")
    @patch("yt_info_extract.cli.export_to_csv")
    def test_batch_with_output_dir_json_format(
        self, mock_export_csv, mock_export_json, mock_load_ids, mock_extractor_class
    ):
        """Test batch processing with output directory and JSON format"""
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor
        mock_load_ids.return_value = ["id1", "id2"]
        mock_extractor.batch_extract.return_value = [{"title": "Video 1"}, {"title": "Video 2"}]
        mock_export_json.return_value = True
        mock_export_csv.return_value = True

        with tempfile.TemporaryDirectory() as temp_dir:
            test_args = [
                "yt-info",
                "--batch",
                "test_batch.txt",
                "--output-dir",
                temp_dir,
                "--format",
                "json",
            ]

            with patch("sys.argv", test_args):
                result = main()

            assert result == 0
            mock_export_json.assert_called_once()

    @patch("yt_info_extract.cli.YouTubeVideoInfoExtractor")
    @patch("yt_info_extract.cli.load_video_ids_from_file")
    @patch("yt_info_extract.cli.export_to_csv")
    def test_batch_with_output_dir_csv_format(
        self, mock_export_csv, mock_load_ids, mock_extractor_class
    ):
        """Test batch processing with output directory and CSV format"""
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor
        mock_load_ids.return_value = ["id1"]
        mock_extractor.batch_extract.return_value = [{"title": "Video 1"}]
        mock_export_csv.return_value = True

        with tempfile.TemporaryDirectory() as temp_dir:
            test_args = [
                "yt-info",
                "--batch",
                "test_batch.txt",
                "--output-dir",
                temp_dir,
                "--format",
                "csv",
            ]

            with patch("sys.argv", test_args):
                result = main()

            assert result == 0
            mock_export_csv.assert_called_once()

    @patch("yt_info_extract.cli.YouTubeVideoInfoExtractor")
    @patch("yt_info_extract.cli.load_video_ids_from_file")
    @patch("yt_info_extract.cli.export_to_json")
    @patch("yt_info_extract.cli.export_to_csv")
    def test_batch_with_output_dir_default_formats(
        self, mock_export_csv, mock_export_json, mock_load_ids, mock_extractor_class
    ):
        """Test batch processing with output directory and default formats"""
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor
        mock_load_ids.return_value = ["id1"]
        mock_extractor.batch_extract.return_value = [{"title": "Video 1"}]
        mock_export_json.return_value = True
        mock_export_csv.return_value = True

        with tempfile.TemporaryDirectory() as temp_dir:
            test_args = ["yt-info", "--batch", "test_batch.txt", "--output-dir", temp_dir]

            with patch("sys.argv", test_args):
                result = main()

            assert result == 0
            # Should export both JSON and CSV for convenience
            mock_export_json.assert_called_once()
            mock_export_csv.assert_called_once()


class TestUtilsCoverage:
    """Test utils coverage gaps"""

    def test_export_to_csv_with_none_values(self):
        """Test CSV export with None values"""
        from yt_info_extract.utils import export_to_csv

        video_data = [
            {
                "title": "Video 1",
                "channel_name": None,
                "views": None,
                "publication_date": None,
                "description": None,
            }
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            temp_file = f.name

        try:
            result = export_to_csv(video_data, temp_file)
            assert result is True

            # Verify file was created and has content
            with open(temp_file, "r") as f:
                content = f.read()
                assert (
                    "title,channel_name,views,publication_date,description,extraction_method"
                    in content
                )
                assert "Video 1" in content
        finally:
            os.unlink(temp_file)
