#!/usr/bin/env python3
"""
Tests for __init__.py convenience functions
"""

import pytest
from unittest.mock import patch, MagicMock

import yt_info_extract
from yt_info_extract import (
    get_video_info,
    get_video_info_batch,
    get_video_stats,
    export_video_info,
    test_extraction_methods,
    __version__,
    __author__,
    __email__,
    __description__,
)


class TestConvenienceFunctions:
    """Test convenience functions in __init__.py"""
    
    @patch('yt_info_extract.YouTubeVideoInfoExtractor')
    def test_get_video_info_success(self, mock_extractor_class):
        """Test get_video_info convenience function"""
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor
        
        expected_result = {
            "title": "Test Video",
            "channel_name": "Test Channel",
            "views": 1000000
        }
        mock_extractor.get_video_info.return_value = expected_result
        
        result = get_video_info("jNQXAC9IVRw")
        
        assert result == expected_result
        mock_extractor_class.assert_called_once_with(
            api_key=None, 
            strategy="auto"
        )
        mock_extractor.get_video_info.assert_called_once_with("jNQXAC9IVRw")
    
    @patch('yt_info_extract.YouTubeVideoInfoExtractor')
    def test_get_video_info_with_parameters(self, mock_extractor_class):
        """Test get_video_info with custom parameters"""
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.get_video_info.return_value = {"title": "Test"}
        
        result = get_video_info(
            "jNQXAC9IVRw",
            api_key="test_key",
            strategy="api",
            timeout=60,
            max_retries=5
        )
        
        mock_extractor_class.assert_called_once_with(
            api_key="test_key",
            strategy="api", 
            timeout=60,
            max_retries=5
        )
    
    @patch('yt_info_extract.YouTubeVideoInfoExtractor')
    def test_get_video_info_none_result(self, mock_extractor_class):
        """Test get_video_info when extractor returns None"""
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.get_video_info.return_value = None
        
        result = get_video_info("invalid_id")
        
        assert result is None
    
    @patch('yt_info_extract.YouTubeVideoInfoExtractor')
    def test_get_video_info_batch_success(self, mock_extractor_class):
        """Test get_video_info_batch convenience function"""
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor
        
        expected_results = [
            {"title": "Video 1", "views": 1000},
            {"title": "Video 2", "views": 2000}
        ]
        mock_extractor.batch_extract.return_value = expected_results
        
        video_list = ["id1", "id2"]
        result = get_video_info_batch(video_list)
        
        assert result == expected_results
        mock_extractor_class.assert_called_once_with(
            api_key=None,
            strategy="auto"
        )
        mock_extractor.batch_extract.assert_called_once_with(
            video_list, "auto", 0.5
        )
    
    @patch('yt_info_extract.YouTubeVideoInfoExtractor')
    def test_get_video_info_batch_with_parameters(self, mock_extractor_class):
        """Test get_video_info_batch with custom parameters"""
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.batch_extract.return_value = []
        
        video_list = ["id1", "id2"]
        result = get_video_info_batch(
            video_list,
            api_key="test_key",
            strategy="api",
            delay_between_requests=1.0,
            timeout=60
        )
        
        mock_extractor_class.assert_called_once_with(
            api_key="test_key",
            strategy="api",
            timeout=60
        )
        mock_extractor.batch_extract.assert_called_once_with(
            video_list, "api", 1.0
        )
    
    @patch('yt_info_extract.get_video_info')
    @patch('yt_info_extract.extract_video_stats')
    def test_get_video_stats_success(self, mock_extract_stats, mock_get_info):
        """Test get_video_stats convenience function"""
        video_info = {"title": "Test Video", "views": 1000000}
        expected_stats = {
            "title": "Test Video",
            "formatted_views": "1.0M views",
            "raw_views": 1000000
        }
        
        mock_get_info.return_value = video_info
        mock_extract_stats.return_value = expected_stats
        
        result = get_video_stats("jNQXAC9IVRw")
        
        assert result == expected_stats
        mock_get_info.assert_called_once_with(
            "jNQXAC9IVRw", None, "auto"
        )
        mock_extract_stats.assert_called_once_with(video_info)
    
    @patch('yt_info_extract.get_video_info')
    def test_get_video_stats_no_video_info(self, mock_get_info):
        """Test get_video_stats when get_video_info returns None"""
        mock_get_info.return_value = None
        
        result = get_video_stats("invalid_id")
        
        assert result is None
    
    @patch('yt_info_extract.get_video_info')
    @patch('yt_info_extract.extract_video_stats')
    def test_get_video_stats_with_parameters(self, mock_extract_stats, mock_get_info):
        """Test get_video_stats with custom parameters"""
        mock_get_info.return_value = {"title": "Test"}
        mock_extract_stats.return_value = {"title": "Test"}
        
        result = get_video_stats(
            "jNQXAC9IVRw",
            api_key="test_key",
            strategy="api",
            timeout=60
        )
        
        mock_get_info.assert_called_once_with(
            "jNQXAC9IVRw", "test_key", "api", timeout=60
        )
    
    @patch('yt_info_extract.export_to_json')
    def test_export_video_info_json(self, mock_export_json):
        """Test export_video_info with JSON format"""
        video_data = {"title": "Test Video"}
        mock_export_json.return_value = True
        
        result = export_video_info(video_data, "test.json", "json")
        
        assert result is True
        mock_export_json.assert_called_once_with(video_data, "test.json", True)
    
    @patch('yt_info_extract.export_to_json')
    def test_export_video_info_json_no_pretty(self, mock_export_json):
        """Test export_video_info with JSON format, no pretty printing"""
        video_data = {"title": "Test Video"}
        mock_export_json.return_value = True
        
        result = export_video_info(video_data, "test.json", "json", pretty=False)
        
        assert result is True
        mock_export_json.assert_called_once_with(video_data, "test.json", False)
    
    @patch('yt_info_extract.export_to_csv')
    def test_export_video_info_csv(self, mock_export_csv):
        """Test export_video_info with CSV format"""
        video_data = [{"title": "Video 1"}, {"title": "Video 2"}]
        mock_export_csv.return_value = True
        
        result = export_video_info(video_data, "test.csv", "csv")
        
        assert result is True
        mock_export_csv.assert_called_once_with(video_data, "test.csv")
    
    @patch('yt_info_extract.export_to_csv')
    def test_export_video_info_csv_single_dict(self, mock_export_csv):
        """Test export_video_info with CSV format and single dict"""
        video_data = {"title": "Test Video"}
        mock_export_csv.return_value = True
        
        result = export_video_info(video_data, "test.csv", "csv")
        
        assert result is True
        mock_export_csv.assert_called_once_with([video_data], "test.csv")
    
    def test_export_video_info_invalid_format(self):
        """Test export_video_info with invalid format"""
        video_data = {"title": "Test Video"}
        
        with pytest.raises(ValueError, match="format_type must be 'json' or 'csv'"):
            export_video_info(video_data, "test.txt", "invalid")
    
    @patch('yt_info_extract.YouTubeVideoInfoExtractor')
    def test_test_extraction_methods(self, mock_extractor_class):
        """Test test_extraction_methods convenience function"""
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor
        
        # Mock service availability
        mock_extractor.youtube_service = MagicMock()  # API available
        mock_extractor.get_available_strategies.return_value = ["api", "yt_dlp"]
        
        result = test_extraction_methods()
        
        expected = {
            "youtube_api": True,
            "yt_dlp": True,
            "pytubefix": False
        }
        
        assert result == expected
        mock_extractor_class.assert_called_once_with()
    
    @patch('yt_info_extract.YouTubeVideoInfoExtractor')
    def test_test_extraction_methods_no_api(self, mock_extractor_class):
        """Test test_extraction_methods when API is not available"""
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor
        
        # Mock no API service
        mock_extractor.youtube_service = None
        mock_extractor.get_available_strategies.return_value = ["yt_dlp", "pytubefix"]
        
        result = test_extraction_methods()
        
        expected = {
            "youtube_api": False,
            "yt_dlp": True,
            "pytubefix": True
        }
        
        assert result == expected


class TestModuleMetadata:
    """Test module metadata and constants"""
    
    def test_version_exists(self):
        """Test that version is defined"""
        assert hasattr(yt_info_extract, '__version__')
        assert isinstance(__version__, str)
        assert len(__version__) > 0
    
    def test_author_exists(self):
        """Test that author is defined"""
        assert hasattr(yt_info_extract, '__author__')
        assert isinstance(__author__, str)
        assert len(__author__) > 0
    
    def test_email_exists(self):
        """Test that email is defined"""
        assert hasattr(yt_info_extract, '__email__')
        assert isinstance(__email__, str)
        assert "@" in __email__
    
    def test_description_exists(self):
        """Test that description is defined"""
        assert hasattr(yt_info_extract, '__description__')
        assert isinstance(__description__, str)
        assert len(__description__) > 0
    
    def test_all_exports(self):
        """Test that __all__ contains expected exports"""
        expected_exports = [
            "YouTubeVideoInfoExtractor",
            "export_to_json",
            "export_to_csv", 
            "load_video_ids_from_file",
            "format_views",
            "format_publication_date",
            "clean_description",
            "extract_video_stats",
            "create_summary_report",
            "validate_video_info",
            "get_video_info",
            "get_video_info_batch",
            "get_video_stats",
            "export_video_info",
            "test_extraction_methods",
        ]
        
        for export in expected_exports:
            assert export in yt_info_extract.__all__
    
    def test_imports_available(self):
        """Test that main imports are available"""
        # Test that we can import the main class
        assert hasattr(yt_info_extract, 'YouTubeVideoInfoExtractor')
        
        # Test that we can import utility functions
        assert hasattr(yt_info_extract, 'format_views')
        assert hasattr(yt_info_extract, 'export_to_json')
        
        # Test that we can import convenience functions
        assert hasattr(yt_info_extract, 'get_video_info')
        assert hasattr(yt_info_extract, 'get_video_info_batch')


class TestFunctionSignatures:
    """Test that function signatures are as expected"""
    
    def test_get_video_info_signature(self):
        """Test get_video_info function signature"""
        import inspect
        
        sig = inspect.signature(get_video_info)
        params = list(sig.parameters.keys())
        
        assert 'video_input' in params
        assert 'api_key' in params
        assert 'strategy' in params
        
        # Check default values
        assert sig.parameters['api_key'].default is None
        assert sig.parameters['strategy'].default == "auto"
    
    def test_get_video_info_batch_signature(self):
        """Test get_video_info_batch function signature"""
        import inspect
        
        sig = inspect.signature(get_video_info_batch)
        params = list(sig.parameters.keys())
        
        assert 'video_inputs' in params
        assert 'api_key' in params
        assert 'strategy' in params
        assert 'delay_between_requests' in params
        
        # Check default values
        assert sig.parameters['api_key'].default is None
        assert sig.parameters['strategy'].default == "auto"
        assert sig.parameters['delay_between_requests'].default == 0.5
    
    def test_export_video_info_signature(self):
        """Test export_video_info function signature"""
        import inspect
        
        sig = inspect.signature(export_video_info)
        params = list(sig.parameters.keys())
        
        assert 'video_data' in params
        assert 'output_file' in params
        assert 'format_type' in params
        
        # Check default values
        assert sig.parameters['format_type'].default == "json"