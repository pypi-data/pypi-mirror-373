#!/usr/bin/env python3
"""
End-to-End tests for YouTube Video Information Extractor
These tests make real network calls to YouTube and require internet connection.
Run with: pytest tests/test_e2e.py -m e2e
"""

import pytest
import os
import time
import tempfile
import json
import csv
from pathlib import Path

from yt_info_extract import (
    YouTubeVideoInfoExtractor,
    get_video_info,
    get_video_info_batch,
    get_video_stats,
    export_video_info,
    test_extraction_methods,
)
from yt_info_extract.cli import main
import sys


# Test videos with known stable content
TEST_VIDEOS = {
    "first_youtube": {
        "id": "jNQXAC9IVRw",
        "url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
        "title_contains": "Me at the zoo",
        "channel": "jawed",
        "min_views": 100000,  # Should have at least 100k views
        "year": 2005
    },
    "rick_roll": {
        "id": "dQw4w9WgXcQ",
        "url": "https://youtu.be/dQw4w9WgXcQ", 
        "title_contains": "Never Gonna Give You Up",
        "channel": "Rick Astley",
        "min_views": 1000000,  # Should have at least 1M views
        "year": 2009
    },
    "gangnam": {
        "id": "9bZkp7q19f0",
        "url": "https://www.youtube.com/watch?v=9bZkp7q19f0",
        "title_contains": "GANGNAM STYLE",
        "channel_contains": "officialpsy",
        "min_views": 1000000000,  # Over 1B views
        "year": 2012
    }
}


@pytest.mark.e2e
class TestE2EAPIStrategy:
    """End-to-end tests using YouTube Data API v3"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for API tests"""
        self.api_key = os.environ.get("YOUTUBE_API_KEY")
        if not self.api_key:
            pytest.skip("YOUTUBE_API_KEY not set, skipping API tests")
    
    def test_api_single_video_by_id(self):
        """Test API extraction with video ID"""
        extractor = YouTubeVideoInfoExtractor(
            api_key=self.api_key,
            strategy="api"
        )
        
        video_data = TEST_VIDEOS["first_youtube"]
        result = extractor.get_video_info(video_data["id"])
        
        assert result is not None, "Should return video info"
        assert video_data["title_contains"] in result["title"]
        assert result["channel_name"] == video_data["channel"]
        assert result["views"] >= video_data["min_views"]
        assert str(video_data["year"]) in result["publication_date"]
        assert result["extraction_method"] == "youtube_api"
    
    def test_api_single_video_by_url(self):
        """Test API extraction with full URL"""
        extractor = YouTubeVideoInfoExtractor(
            api_key=self.api_key,
            strategy="api"
        )
        
        video_data = TEST_VIDEOS["rick_roll"]
        result = extractor.get_video_info(video_data["url"])
        
        assert result is not None
        assert video_data["title_contains"] in result["title"]
        assert result["channel_name"] == video_data["channel"]
        assert result["views"] >= video_data["min_views"]
    
    def test_api_batch_extraction(self):
        """Test API batch extraction"""
        extractor = YouTubeVideoInfoExtractor(
            api_key=self.api_key,
            strategy="api"
        )
        
        video_ids = [v["id"] for v in TEST_VIDEOS.values()]
        results = extractor.batch_extract(video_ids, delay_between_requests=0.2)
        
        assert len(results) == len(video_ids)
        
        # All should succeed
        for result in results:
            assert "error" not in result
            assert result["title"] is not None
            assert result["views"] is not None
    
    def test_api_key_validation(self):
        """Test API key validation"""
        extractor = YouTubeVideoInfoExtractor(
            api_key=self.api_key,
            strategy="api"
        )
        
        assert extractor.test_api_key() is True
    
    def test_api_invalid_video_id(self):
        """Test API with invalid video ID"""
        extractor = YouTubeVideoInfoExtractor(
            api_key=self.api_key,
            strategy="api"
        )
        
        result = extractor.get_video_info("INVALID_VIDEO_ID_123")
        assert result is None


@pytest.mark.e2e
class TestE2EYtDlpStrategy:
    """End-to-end tests using yt-dlp"""
    
    def test_yt_dlp_single_video(self):
        """Test yt-dlp extraction"""
        extractor = YouTubeVideoInfoExtractor(strategy="yt_dlp")
        
        # Check if yt-dlp is available
        if "yt_dlp" not in extractor.get_available_strategies():
            pytest.skip("yt-dlp not available")
        
        video_data = TEST_VIDEOS["first_youtube"]
        result = extractor.get_video_info(video_data["id"])
        
        assert result is not None
        assert video_data["title_contains"] in result["title"]
        assert result["channel_name"] == video_data["channel"]
        assert result["views"] >= video_data["min_views"]
        assert result["extraction_method"] == "yt_dlp"
    
    def test_yt_dlp_url_formats(self):
        """Test yt-dlp with different URL formats"""
        extractor = YouTubeVideoInfoExtractor(strategy="yt_dlp")
        
        if "yt_dlp" not in extractor.get_available_strategies():
            pytest.skip("yt-dlp not available")
        
        # Test different URL formats
        urls = [
            "https://www.youtube.com/watch?v=jNQXAC9IVRw",
            "https://youtu.be/jNQXAC9IVRw",
            "jNQXAC9IVRw"
        ]
        
        for url in urls:
            result = extractor.get_video_info(url)
            assert result is not None
            assert "Me at the zoo" in result["title"]
    
    def test_yt_dlp_high_view_count_video(self):
        """Test yt-dlp with high view count video"""
        extractor = YouTubeVideoInfoExtractor(strategy="yt_dlp")
        
        if "yt_dlp" not in extractor.get_available_strategies():
            pytest.skip("yt-dlp not available")
        
        video_data = TEST_VIDEOS["gangnam"]
        result = extractor.get_video_info(video_data["id"])
        
        assert result is not None
        assert video_data["title_contains"] in result["title"]
        assert result["views"] >= video_data["min_views"]


@pytest.mark.e2e
class TestE2EPytubefixStrategy:
    """End-to-end tests using pytubefix"""
    
    def test_pytubefix_single_video(self):
        """Test pytubefix extraction"""
        extractor = YouTubeVideoInfoExtractor(strategy="pytubefix")
        
        # Check if pytubefix is available
        if "pytubefix" not in extractor.get_available_strategies():
            pytest.skip("pytubefix not available")
        
        video_data = TEST_VIDEOS["rick_roll"]
        result = extractor.get_video_info(video_data["id"])
        
        assert result is not None
        assert video_data["title_contains"] in result["title"]
        assert result["channel_name"] == video_data["channel"]
        assert result["extraction_method"] == "pytubefix"
    
    def test_pytubefix_with_delay(self):
        """Test pytubefix with rate limiting"""
        extractor = YouTubeVideoInfoExtractor(
            strategy="pytubefix",
            rate_limit_delay=1.0
        )
        
        if "pytubefix" not in extractor.get_available_strategies():
            pytest.skip("pytubefix not available")
        
        start_time = time.time()
        result = extractor.get_video_info("jNQXAC9IVRw")
        elapsed = time.time() - start_time
        
        assert result is not None
        assert elapsed >= 1.0  # Should have rate limit delay


@pytest.mark.e2e
class TestE2EAutoStrategy:
    """End-to-end tests using auto strategy selection"""
    
    def test_auto_strategy_selection(self):
        """Test automatic strategy selection"""
        extractor = YouTubeVideoInfoExtractor(strategy="auto")
        
        # Should use whatever is available
        result = extractor.get_video_info("jNQXAC9IVRw")
        
        assert result is not None
        assert result["title"] is not None
        assert result["extraction_method"] in ["youtube_api", "yt_dlp", "pytubefix"]
    
    def test_auto_with_api_key(self):
        """Test auto strategy prefers API when key available"""
        api_key = os.environ.get("YOUTUBE_API_KEY")
        if not api_key:
            pytest.skip("YOUTUBE_API_KEY not set")
        
        extractor = YouTubeVideoInfoExtractor(
            api_key=api_key,
            strategy="auto"
        )
        
        result = extractor.get_video_info("jNQXAC9IVRw")
        
        assert result is not None
        # Should prefer API when available
        assert result["extraction_method"] == "youtube_api"


@pytest.mark.e2e
class TestE2EConvenienceFunctions:
    """End-to-end tests for convenience functions"""
    
    def test_get_video_info_function(self):
        """Test get_video_info convenience function"""
        result = get_video_info("jNQXAC9IVRw")
        
        assert result is not None
        assert "Me at the zoo" in result["title"]
        assert result["channel_name"] == "jawed"
    
    def test_get_video_info_batch_function(self):
        """Test get_video_info_batch convenience function"""
        video_ids = ["jNQXAC9IVRw", "dQw4w9WgXcQ"]
        results = get_video_info_batch(video_ids, delay_between_requests=0.5)
        
        assert len(results) == 2
        assert all(r["title"] is not None for r in results if "error" not in r)
    
    def test_get_video_stats_function(self):
        """Test get_video_stats convenience function"""
        stats = get_video_stats("jNQXAC9IVRw")
        
        assert stats is not None
        assert stats["title"] == "Me at the zoo"
        assert "formatted_views" in stats
        assert stats["has_description"] is True
    
    def test_test_extraction_methods_function(self):
        """Test extraction methods availability check"""
        methods = test_extraction_methods()
        
        assert isinstance(methods, dict)
        assert "youtube_api" in methods
        assert "yt_dlp" in methods
        assert "pytubefix" in methods
        
        # At least one method should be available
        assert any(methods.values())


@pytest.mark.e2e
class TestE2EExportFunctions:
    """End-to-end tests for export functionality"""
    
    def test_export_single_video_json(self):
        """Test exporting single video to JSON"""
        result = get_video_info("jNQXAC9IVRw")
        assert result is not None
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            success = export_video_info(result, temp_file, "json")
            assert success is True
            
            # Verify file contents
            with open(temp_file, 'r') as f:
                data = json.load(f)
                assert data["title"] == result["title"]
                assert data["channel_name"] == result["channel_name"]
        finally:
            os.unlink(temp_file)
    
    def test_export_batch_csv(self):
        """Test exporting batch results to CSV"""
        results = get_video_info_batch(["jNQXAC9IVRw", "dQw4w9WgXcQ"])
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_file = f.name
        
        try:
            success = export_video_info(results, temp_file, "csv")
            assert success is True
            
            # Verify file contents
            with open(temp_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                assert len(rows) == 2
                assert all('title' in row for row in rows)
        finally:
            os.unlink(temp_file)


@pytest.mark.e2e
class TestE2ECLI:
    """End-to-end tests for CLI functionality"""
    
    def test_cli_single_video(self, capsys):
        """Test CLI with single video"""
        test_args = ["yt-info", "jNQXAC9IVRw"]
        
        with pytest.MonkeyPatch.context() as m:
            m.setattr(sys, 'argv', test_args)
            result = main()
        
        assert result == 0
        
        captured = capsys.readouterr()
        assert "Me at the zoo" in captured.out
        assert "jawed" in captured.out
    
    def test_cli_json_output(self):
        """Test CLI JSON output"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            test_args = ["yt-info", "-f", "json", "-o", temp_file, "jNQXAC9IVRw"]
            
            with pytest.MonkeyPatch.context() as m:
                m.setattr(sys, 'argv', test_args)
                result = main()
            
            assert result == 0
            
            # Verify JSON file
            with open(temp_file, 'r') as f:
                data = json.load(f)
                assert "Me at the zoo" in data["title"]
        finally:
            os.unlink(temp_file)
    
    def test_cli_batch_processing(self):
        """Test CLI batch processing"""
        # Create batch file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            batch_file = f.name
            f.write("jNQXAC9IVRw\n")
            f.write("dQw4w9WgXcQ\n")
        
        with tempfile.TemporaryDirectory() as output_dir:
            try:
                test_args = [
                    "yt-info",
                    "--batch", batch_file,
                    "--output-dir", output_dir,
                    "--delay", "0.3"
                ]
                
                with pytest.MonkeyPatch.context() as m:
                    m.setattr(sys, 'argv', test_args)
                    result = main()
                
                assert result == 0
                
                # Check output files were created
                json_file = Path(output_dir) / "batch_results.json"
                csv_file = Path(output_dir) / "batch_results.csv"
                assert json_file.exists()
                assert csv_file.exists()
            finally:
                os.unlink(batch_file)
    
    def test_cli_different_strategies(self, capsys):
        """Test CLI with different strategies"""
        strategies = ["auto"]
        
        # Add API if available
        if os.environ.get("YOUTUBE_API_KEY"):
            strategies.append("api")
        
        # Add yt-dlp if available
        try:
            import yt_dlp
            strategies.append("yt_dlp")
        except ImportError:
            pass
        
        # Add pytubefix if available
        try:
            from pytubefix import YouTube
            strategies.append("pytubefix")
        except ImportError:
            pass
        
        for strategy in strategies:
            test_args = ["yt-info", "-s", strategy, "jNQXAC9IVRw"]
            
            with pytest.MonkeyPatch.context() as m:
                m.setattr(sys, 'argv', test_args)
                result = main()
            
            assert result == 0
            
            captured = capsys.readouterr()
            assert "Me at the zoo" in captured.out


@pytest.mark.e2e
class TestE2EErrorHandling:
    """End-to-end tests for error handling"""
    
    def test_invalid_video_id(self):
        """Test with completely invalid video ID"""
        result = get_video_info("NOTAVALIDVIDEOID123456")
        assert result is None
    
    def test_private_video(self):
        """Test with private/deleted video"""
        # This video ID is likely deleted/private
        result = get_video_info("aaaaaaaaaa1")
        
        # Should either return None or have limited info
        if result is not None:
            # Some strategies might return partial info
            assert result.get("title") is None or len(result.get("title", "")) > 0
    
    def test_network_resilience(self):
        """Test retry mechanism with rate limiting"""
        extractor = YouTubeVideoInfoExtractor(
            max_retries=3,
            backoff_factor=0.5
        )
        
        # Should handle temporary issues gracefully
        result = extractor.get_video_info("jNQXAC9IVRw")
        assert result is not None


@pytest.mark.e2e
class TestE2EPerformance:
    """End-to-end performance tests"""
    
    def test_batch_performance(self):
        """Test batch extraction performance"""
        video_ids = ["jNQXAC9IVRw", "dQw4w9WgXcQ", "9bZkp7q19f0"]
        
        start_time = time.time()
        results = get_video_info_batch(video_ids, delay_between_requests=0.1)
        elapsed = time.time() - start_time
        
        assert len(results) == 3
        
        # Should complete within reasonable time (30 seconds for 3 videos)
        assert elapsed < 30
        
        # All should have results
        assert all(r is not None for r in results)
    
    def test_concurrent_requests_handling(self):
        """Test handling of multiple extractors"""
        # Create multiple extractors
        extractors = [
            YouTubeVideoInfoExtractor(strategy="auto")
            for _ in range(3)
        ]
        
        # Each should work independently
        results = []
        for extractor in extractors:
            result = extractor.get_video_info("jNQXAC9IVRw")
            results.append(result)
            time.sleep(0.2)  # Small delay to avoid rate limiting
        
        assert all(r is not None for r in results)
        assert all(r["title"] == results[0]["title"] for r in results)


# Run specific test groups with:
# pytest tests/test_e2e.py -m e2e -k "API"  # Run only API tests
# pytest tests/test_e2e.py -m e2e -k "CLI"  # Run only CLI tests
# pytest tests/test_e2e.py -m e2e -v        # Run all E2E tests verbosely