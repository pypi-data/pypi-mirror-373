#!/usr/bin/env python3
"""
Tests for CLI functionality
"""

import os
import sys
import tempfile
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from yt_info_extract.cli import main, print_video_info


class TestPrintVideoInfo:
    """Test video info printing functions"""

    def test_print_video_info_text_format(self, capsys):
        """Test text format printing"""
        video_info = {
            "title": "Test Video",
            "channel_name": "Test Channel",
            "views": 1000000,
            "publication_date": "2005-04-23T00:00:00Z",
            "description": "Test description",
            "extraction_method": "youtube_api",
        }

        print_video_info(video_info, "text")
        captured = capsys.readouterr()

        assert "📹 Title: Test Video" in captured.out
        assert "📺 Channel: Test Channel" in captured.out
        assert "👀 Views: 1.0M views" in captured.out
        assert "📅 Published: April 23, 2005" in captured.out
        assert "🔧 Method: youtube_api" in captured.out
        assert "📝 Description: Test description" in captured.out

    def test_print_video_info_compact_format(self, capsys):
        """Test compact format printing"""
        video_info = {
            "title": "Test Video",
            "channel_name": "Test Channel",
            "views": 1000000,
            "extraction_method": "youtube_api",
        }

        print_video_info(video_info, "compact")
        captured = capsys.readouterr()

        assert "Test Video | Test Channel | 1.0M views | youtube_api" in captured.out

    def test_print_video_info_compact_long_title(self, capsys):
        """Test compact format with long title"""
        video_info = {
            "title": "A" * 100,  # Very long title
            "channel_name": "Test Channel",
            "views": 1000,
            "extraction_method": "api",
        }

        print_video_info(video_info, "compact")
        captured = capsys.readouterr()

        output = captured.out.strip()
        # Should truncate title to 50 chars + "..."
        assert len(output.split("|")[0].strip()) == 53  # 50 + "..."
        assert "..." in output

    def test_print_video_info_stats_format(self, capsys):
        """Test stats format printing"""
        video_info = {
            "title": "Test Video",
            "channel_name": "Test Channel",
            "views": 1000000,
            "publication_date": "2005-04-23T00:00:00Z",
            "description": "Test description",
            "extraction_method": "youtube_api",
        }

        print_video_info(video_info, "stats")
        captured = capsys.readouterr()

        assert "Video Statistics:" in captured.out
        assert "Title: Test Video" in captured.out
        assert "Channel: Test Channel" in captured.out
        assert "Views: 1.0M views (1,000,000)" in captured.out
        assert "Published: April 23, 2005" in captured.out
        assert "Description Length:" in captured.out
        assert "Has Description: Yes" in captured.out
        assert "Extraction Method: youtube_api" in captured.out

    def test_print_video_info_error(self, capsys):
        """Test printing with error info"""
        video_info = {"error": "Extraction failed", "video_id": "invalid_id"}

        print_video_info(video_info, "text")
        captured = capsys.readouterr()

        assert "❌ Failed to extract video information" in captured.out
        assert "Error: Extraction failed" in captured.out

    def test_print_video_info_none(self, capsys):
        """Test printing with None video info"""
        print_video_info(None, "text")
        captured = capsys.readouterr()

        assert "❌ Failed to extract video information" in captured.out

    def test_print_video_info_no_description(self, capsys):
        """Test printing with no description"""
        video_info = {
            "title": "Test Video",
            "channel_name": "Test Channel",
            "views": 1000000,
            "extraction_method": "youtube_api",
        }

        print_video_info(video_info, "text")
        captured = capsys.readouterr()

        assert "📝 Description: Not available" in captured.out


class TestCLIMain:
    """Test main CLI functionality"""

    @patch("yt_info_extract.cli.YouTubeVideoInfoExtractor")
    def test_main_single_video_text(self, mock_extractor_class):
        """Test single video extraction with text output"""
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor

        video_info = {
            "title": "Test Video",
            "channel_name": "Test Channel",
            "views": 1000000,
            "extraction_method": "api",
        }
        mock_extractor.get_video_info.return_value = video_info

        test_args = ["yt-info", "jNQXAC9IVRw"]

        with patch.object(sys, "argv", test_args):
            with patch("builtins.print") as mock_print:
                result = main()

        assert result == 0
        mock_extractor.get_video_info.assert_called_once_with("jNQXAC9IVRw")

        # Check that video info was printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Test Video" in call for call in print_calls)

    @patch("yt_info_extract.cli.YouTubeVideoInfoExtractor")
    def test_main_single_video_failed(self, mock_extractor_class):
        """Test single video extraction failure"""
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.get_video_info.return_value = None

        test_args = ["yt-info", "invalid_id"]

        with patch.object(sys, "argv", test_args):
            result = main()

        assert result == 1

    @patch("yt_info_extract.cli.YouTubeVideoInfoExtractor")
    @patch("yt_info_extract.cli.export_to_json")
    def test_main_json_output(self, mock_export_json, mock_extractor_class):
        """Test JSON output format"""
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor

        video_info = {"title": "Test Video"}
        mock_extractor.get_video_info.return_value = video_info
        mock_export_json.return_value = True

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_file = f.name

        try:
            test_args = ["yt-info", "-f", "json", "-o", temp_file, "jNQXAC9IVRw"]

            with patch.object(sys, "argv", test_args):
                result = main()

            assert result == 0
            mock_export_json.assert_called_once_with(video_info, temp_file, False)
        finally:
            os.unlink(temp_file)

    def test_main_json_output_pretty_print_requires_output_file(self):
        """Test JSON output with pretty printing requires output file"""
        test_args = ["yt-info", "-f", "json", "--pretty", "jNQXAC9IVRw"]

        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit):  # argparse calls sys.exit
                main()

    @patch("yt_info_extract.cli.YouTubeVideoInfoExtractor")
    @patch("yt_info_extract.cli.export_to_csv")
    def test_main_csv_output(self, mock_export_csv, mock_extractor_class):
        """Test CSV output format"""
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor

        video_info = {"title": "Test Video"}
        mock_extractor.get_video_info.return_value = video_info
        mock_export_csv.return_value = True

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            temp_file = f.name

        try:
            test_args = ["yt-info", "-f", "csv", "-o", temp_file, "jNQXAC9IVRw"]

            with patch.object(sys, "argv", test_args):
                result = main()

            assert result == 0
            mock_export_csv.assert_called_once_with([video_info], temp_file)
        finally:
            os.unlink(temp_file)

    @patch("yt_info_extract.cli.YouTubeVideoInfoExtractor")
    def test_main_test_api_valid(self, mock_extractor_class):
        """Test API key validation success"""
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.test_api_key.return_value = True

        test_args = ["yt-info", "--test-api"]

        with patch.object(sys, "argv", test_args):
            with patch("builtins.print") as mock_print:
                result = main()

        assert result == 0
        mock_print.assert_called_with("✅ API key is valid")

    @patch("yt_info_extract.cli.YouTubeVideoInfoExtractor")
    def test_main_test_api_invalid(self, mock_extractor_class):
        """Test API key validation failure"""
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.test_api_key.return_value = False

        test_args = ["yt-info", "--test-api"]

        with patch.object(sys, "argv", test_args):
            with patch("builtins.print") as mock_print:
                result = main()

        assert result == 1
        mock_print.assert_called_with("❌ API key is invalid or not provided")

    @patch("yt_info_extract.cli.YouTubeVideoInfoExtractor")
    def test_main_list_strategies(self, mock_extractor_class):
        """Test listing available strategies"""
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.get_available_strategies.return_value = ["api", "yt_dlp"]

        test_args = ["yt-info", "--list-strategies"]

        with patch.object(sys, "argv", test_args):
            with patch("builtins.print") as mock_print:
                result = main()

        assert result == 0

        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Available extraction strategies" in call for call in print_calls)
        assert any("api" in call for call in print_calls)
        assert any("yt_dlp" in call for call in print_calls)

    @patch("yt_info_extract.cli.YouTubeVideoInfoExtractor")
    def test_main_list_strategies_empty(self, mock_extractor_class):
        """Test listing strategies when none available"""
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.get_available_strategies.return_value = []

        test_args = ["yt-info", "--list-strategies"]

        with patch.object(sys, "argv", test_args):
            with patch("builtins.print") as mock_print:
                result = main()

        assert result == 0

        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("No strategies available" in call for call in print_calls)

    @patch("yt_info_extract.cli.YouTubeVideoInfoExtractor")
    @patch("yt_info_extract.cli.load_video_ids_from_file")
    def test_main_batch_processing(self, mock_load_ids, mock_extractor_class):
        """Test batch processing"""
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor

        video_ids = ["id1", "id2", "id3"]
        mock_load_ids.return_value = video_ids

        batch_results = [
            {"title": "Video 1", "views": 1000, "extraction_method": "api"},
            {"title": "Video 2", "views": 2000, "extraction_method": "yt_dlp"},
            {"error": "Failed", "video_id": "id3"},
        ]
        mock_extractor.batch_extract.return_value = batch_results

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            batch_file = f.name

        try:
            test_args = ["yt-info", "--batch", batch_file]

            with patch.object(sys, "argv", test_args):
                with patch("builtins.print") as mock_print:
                    result = main()

            assert result == 0
            mock_load_ids.assert_called_once_with(batch_file)
            mock_extractor.batch_extract.assert_called_once()

            # Should print sample results
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any("Sample results" in call for call in print_calls)
        finally:
            os.unlink(batch_file)

    @patch("yt_info_extract.cli.YouTubeVideoInfoExtractor")
    @patch("yt_info_extract.cli.load_video_ids_from_file")
    def test_main_batch_no_ids(self, mock_load_ids, mock_extractor_class):
        """Test batch processing with no video IDs loaded"""
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor
        mock_load_ids.return_value = []

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            batch_file = f.name

        try:
            test_args = ["yt-info", "--batch", batch_file]

            with patch.object(sys, "argv", test_args):
                result = main()

            assert result == 1
        finally:
            os.unlink(batch_file)

    @patch("yt_info_extract.cli.YouTubeVideoInfoExtractor")
    @patch("yt_info_extract.cli.load_video_ids_from_file")
    @patch("yt_info_extract.cli.create_summary_report")
    def test_main_batch_with_summary(
        self, mock_create_summary, mock_load_ids, mock_extractor_class
    ):
        """Test batch processing with summary report"""
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor
        mock_load_ids.return_value = ["id1", "id2"]

        batch_results = [{"title": "Video 1", "views": 1000}, {"title": "Video 2", "views": 2000}]
        mock_extractor.batch_extract.return_value = batch_results

        summary_report = {
            "total_videos_processed": 2,
            "successful_extractions": 2,
            "failed_extractions": 0,
            "success_rate": "100.0%",
            "view_statistics": {"formatted_total": "3.0K views", "formatted_average": "1.5K views"},
            "extraction_methods": {"api": 2},
            "top_channels": {"Channel A": 2},
        }
        mock_create_summary.return_value = summary_report

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            batch_file = f.name

        try:
            test_args = ["yt-info", "--batch", batch_file, "--summary"]

            with patch.object(sys, "argv", test_args):
                with patch("builtins.print") as mock_print:
                    result = main()

            assert result == 0
            mock_create_summary.assert_called_once_with(batch_results)

            # Should print summary report
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any("SUMMARY REPORT" in call for call in print_calls)
            assert any("Total videos processed: 2" in call for call in print_calls)
        finally:
            os.unlink(batch_file)

    def test_main_no_arguments(self):
        """Test CLI with no arguments"""
        test_args = ["yt-info"]

        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit):  # argparse calls sys.exit
                main()

    def test_main_json_no_output_file(self):
        """Test JSON format without output file"""
        test_args = ["yt-info", "-f", "json", "jNQXAC9IVRw"]

        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit):  # argparse calls sys.exit
                main()

    def test_main_csv_no_output_file(self):
        """Test CSV format without output file"""
        test_args = ["yt-info", "-f", "csv", "jNQXAC9IVRw"]

        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit):  # argparse calls sys.exit
                main()

    def test_main_extractor_initialization_failure(self):
        """Test main when extractor initialization fails"""
        test_args = ["yt-info", "jNQXAC9IVRw"]

        with patch(
            "yt_info_extract.cli.YouTubeVideoInfoExtractor", side_effect=Exception("Init failed")
        ):
            with patch.object(sys, "argv", test_args):
                with patch("builtins.print") as mock_print:
                    result = main()

        assert result == 1
        mock_print.assert_called_with("❌ Failed to initialize extractor: Init failed")

    @patch("yt_info_extract.cli.YouTubeVideoInfoExtractor")
    def test_main_with_custom_parameters(self, mock_extractor_class):
        """Test main with custom CLI parameters"""
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.get_video_info.return_value = {"title": "Test"}

        test_args = [
            "yt-info",
            "--api-key",
            "test_key",
            "--strategy",
            "api",
            "--timeout",
            "60",
            "--retries",
            "5",
            "--verbose",
            "jNQXAC9IVRw",
        ]

        with patch.object(sys, "argv", test_args):
            result = main()

        assert result == 0

        # Verify extractor was initialized with custom parameters
        mock_extractor_class.assert_called_once_with(
            api_key="test_key", strategy="api", timeout=60.0, max_retries=5
        )
