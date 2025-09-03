#!/usr/bin/env python3
"""
Tests for utility functions
"""

import pytest
import json
import csv
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open

from yt_info_extract.utils import (
    format_views,
    format_publication_date,
    clean_description,
    extract_video_stats,
    export_to_json,
    export_to_csv,
    load_video_ids_from_file,
    validate_video_info,
    create_summary_report,
)


class TestFormatFunctions:
    """Test formatting utility functions"""
    
    def test_format_views(self):
        """Test view count formatting"""
        test_cases = [
            (None, "Unknown views"),
            (0, "0 views"),
            (123, "123 views"),
            (999, "999 views"),
            (1000, "1.0K views"),
            (1234, "1.2K views"),
            (1500, "1.5K views"),
            (1000000, "1.0M views"),
            (1234567, "1.2M views"),
            (1000000000, "1.0B views"),
            (1234567890, "1.2B views"),
            (2500000000, "2.5B views"),
        ]
        
        for input_views, expected in test_cases:
            result = format_views(input_views)
            assert result == expected, f"Failed for input: {input_views}"
    
    def test_format_publication_date_valid(self):
        """Test publication date formatting with valid inputs"""
        test_cases = [
            ("2005-04-23T00:00:00Z", "April 23, 2005"),
            ("2005-04-23", "April 23, 2005"),
            ("2020-12-25T15:30:45Z", "December 25, 2020"),
            ("2020-12-25T15:30:45+00:00", "December 25, 2020"),
        ]
        
        for input_date, expected in test_cases:
            result = format_publication_date(input_date)
            assert result == expected, f"Failed for input: {input_date}"
    
    def test_format_publication_date_invalid(self):
        """Test publication date formatting with invalid inputs"""
        test_cases = [
            (None, "Unknown date"),
            ("", "Unknown date"),
            ("invalid-date", "invalid-date"),  # Returns original on parse failure
            ("not-a-date-at-all", "not-a-date-at-all"),
        ]
        
        for input_date, expected in test_cases:
            result = format_publication_date(input_date)
            assert result == expected, f"Failed for input: {input_date}"
    
    def test_clean_description(self):
        """Test description cleaning"""
        test_cases = [
            (None, "No description available"),
            ("", "No description available"),
            ("Simple description", "Simple description"),
            ("Description with\n\nmultiple\n\nlines", "Description with multiple lines"),
            ("   Description   with   extra   spaces   ", "Description with extra spaces"),
            ("A" * 600, "A" * 500 + "..."),  # Test truncation
            ("Short\n\n\n\nwith many   spaces", "Short with many spaces"),
        ]
        
        for input_desc, expected in test_cases:
            result = clean_description(input_desc)
            assert result == expected, f"Failed for input: {repr(input_desc)}"
    
    def test_clean_description_custom_length(self):
        """Test description cleaning with custom max length"""
        long_desc = "A" * 1000
        result = clean_description(long_desc, max_length=100)
        
        assert len(result) == 103  # 100 + "..."
        assert result.endswith("...")
        assert result.startswith("A" * 100)


class TestExtractVideoStats:
    """Test video statistics extraction"""
    
    def test_extract_video_stats_complete(self):
        """Test stats extraction with complete video info"""
        video_info = {
            "title": "Test Video",
            "channel_name": "Test Channel", 
            "views": 1000000,
            "publication_date": "2005-04-23T00:00:00Z",
            "description": "This is a test description with some content.",
            "extraction_method": "youtube_api"
        }
        
        stats = extract_video_stats(video_info)
        
        assert stats["title"] == "Test Video"
        assert stats["channel"] == "Test Channel"
        assert stats["formatted_views"] == "1.0M views"
        assert stats["raw_views"] == 1000000
        assert stats["formatted_date"] == "April 23, 2005"
        assert stats["raw_date"] == "2005-04-23T00:00:00Z"
        assert stats["extraction_method"] == "youtube_api"
        assert stats["has_description"] is True
        assert stats["description_length"] == len(video_info["description"])
        assert "test description" in stats["description_preview"].lower()
    
    def test_extract_video_stats_minimal(self):
        """Test stats extraction with minimal video info"""
        video_info = {}
        
        stats = extract_video_stats(video_info)
        
        assert stats["title"] == "Unknown"
        assert stats["channel"] == "Unknown"
        assert stats["formatted_views"] == "Unknown views"
        assert stats["raw_views"] is None
        assert stats["formatted_date"] == "Unknown date"
        assert stats["raw_date"] is None
        assert stats["extraction_method"] == "Unknown"
        assert stats["has_description"] is False
        assert stats["description_length"] == 0


class TestExportFunctions:
    """Test export functionality"""
    
    def test_export_to_json_single_video(self):
        """Test JSON export with single video"""
        video_data = {
            "title": "Test Video",
            "channel_name": "Test Channel",
            "views": 1000000
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            result = export_to_json(video_data, temp_file, pretty=True)
            assert result is True
            
            # Verify file contents
            with open(temp_file, 'r') as f:
                loaded_data = json.load(f)
                assert loaded_data == video_data
        finally:
            os.unlink(temp_file)
    
    def test_export_to_json_multiple_videos(self):
        """Test JSON export with multiple videos"""
        video_data = [
            {"title": "Video 1", "views": 1000},
            {"title": "Video 2", "views": 2000}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            result = export_to_json(video_data, temp_file, pretty=False)
            assert result is True
            
            # Verify file contents
            with open(temp_file, 'r') as f:
                loaded_data = json.load(f)
                assert loaded_data == video_data
        finally:
            os.unlink(temp_file)
    
    def test_export_to_json_failure(self):
        """Test JSON export failure handling"""
        video_data = {"title": "Test"}
        invalid_path = "/invalid/path/file.json"
        
        result = export_to_json(video_data, invalid_path)
        assert result is False
    
    def test_export_to_csv_success(self):
        """Test CSV export success"""
        video_data = [
            {
                "title": "Video 1",
                "channel_name": "Channel 1",
                "views": 1000,
                "publication_date": "2005-04-23T00:00:00Z",
                "description": "Description 1",
                "extraction_method": "api"
            },
            {
                "title": "Video 2",
                "channel_name": "Channel 2",
                "views": 2000,
                "publication_date": "2006-05-24T00:00:00Z", 
                "description": "Description 2\nWith newlines",
                "extraction_method": "yt_dlp"
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_file = f.name
        
        try:
            result = export_to_csv(video_data, temp_file)
            assert result is True
            
            # Verify file contents
            with open(temp_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                assert len(rows) == 2
                assert rows[0]['title'] == "Video 1"
                assert rows[0]['views'] == "1000"
                assert rows[1]['title'] == "Video 2"
                # Check that newlines were cleaned
                assert '\n' not in rows[1]['description']
        finally:
            os.unlink(temp_file)
    
    def test_export_to_csv_empty_data(self):
        """Test CSV export with empty data"""
        result = export_to_csv([], "/tmp/test.csv")
        assert result is False
    
    def test_export_to_csv_failure(self):
        """Test CSV export failure handling"""
        video_data = [{"title": "Test"}]
        invalid_path = "/invalid/path/file.csv"
        
        result = export_to_csv(video_data, invalid_path)
        assert result is False


class TestLoadVideoIds:
    """Test video ID loading from file"""
    
    def test_load_video_ids_success(self):
        """Test successful loading of video IDs"""
        video_ids = ["jNQXAC9IVRw", "dQw4w9WgXcQ", "https://youtu.be/kJQP7kiw5Fk"]
        content = "\n".join(video_ids)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_file = f.name
        
        try:
            result = load_video_ids_from_file(temp_file)
            assert result == video_ids
        finally:
            os.unlink(temp_file)
    
    def test_load_video_ids_with_empty_lines(self):
        """Test loading video IDs with empty lines"""
        content = "jNQXAC9IVRw\n\ndQw4w9WgXcQ\n\n\nkJQP7kiw5Fk\n"
        expected = ["jNQXAC9IVRw", "dQw4w9WgXcQ", "kJQP7kiw5Fk"]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_file = f.name
        
        try:
            result = load_video_ids_from_file(temp_file)
            assert result == expected
        finally:
            os.unlink(temp_file)
    
    def test_load_video_ids_file_not_found(self):
        """Test loading video IDs from non-existent file"""
        result = load_video_ids_from_file("/non/existent/file.txt")
        assert result == []
    
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_load_video_ids_permission_error(self, mock_open_error):
        """Test loading video IDs with permission error"""
        result = load_video_ids_from_file("/some/file.txt")
        assert result == []


class TestValidateVideoInfo:
    """Test video info validation"""
    
    def test_validate_video_info_complete(self):
        """Test validation with complete video info"""
        video_info = {
            "title": "Test Video",
            "channel_name": "Test Channel",
            "views": 1000000,
            "publication_date": "2005-04-23T00:00:00Z",
            "description": "Test description"
        }
        
        result = validate_video_info(video_info)
        
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0
        assert len(result["warnings"]) == 0
        assert result["normalized_data"]["title"] == "Test Video"
        assert result["normalized_data"]["views"] == 1000000
    
    def test_validate_video_info_missing_required(self):
        """Test validation with missing required fields"""
        video_info = {
            "views": 1000000,
            "description": "Test description"
        }
        
        result = validate_video_info(video_info)
        
        assert result["is_valid"] is False
        assert len(result["errors"]) == 2  # Missing title and channel_name
        assert any("title" in error for error in result["errors"])
        assert any("channel_name" in error for error in result["errors"])
    
    def test_validate_video_info_with_warnings(self):
        """Test validation with warning conditions"""
        video_info = {
            "title": "Test Video",
            "channel_name": "Test Channel"
            # Missing views, publication_date, description
        }
        
        result = validate_video_info(video_info)
        
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0
        assert len(result["warnings"]) == 3
        assert any("view count" in warning.lower() for warning in result["warnings"])
        assert any("publication date" in warning.lower() for warning in result["warnings"])
        assert any("description" in warning.lower() for warning in result["warnings"])
    
    def test_validate_video_info_normalization(self):
        """Test data normalization during validation"""
        video_info = {
            "title": "  Test Video  ",
            "channel_name": "  Test Channel  ",
            "views": "not_an_int",  # Invalid views
            "description": "  Test description  "
        }
        
        result = validate_video_info(video_info)
        
        normalized = result["normalized_data"]
        assert normalized["title"] == "Test Video"  # Stripped
        assert normalized["channel_name"] == "Test Channel"  # Stripped
        assert normalized["views"] is None  # Invalid int converted to None
        assert normalized["description"] == "Test description"  # Stripped


class TestCreateSummaryReport:
    """Test summary report generation"""
    
    def test_create_summary_report_success(self):
        """Test summary report with successful data"""
        video_data = [
            {
                "title": "Video 1",
                "channel_name": "Channel A",
                "views": 1000,
                "publication_date": "2005-04-23T00:00:00Z",
                "extraction_method": "api"
            },
            {
                "title": "Video 2", 
                "channel_name": "Channel A",
                "views": 2000,
                "publication_date": "2006-05-24T00:00:00Z",
                "extraction_method": "yt_dlp"
            },
            {
                "title": "Video 3",
                "channel_name": "Channel B", 
                "views": 3000,
                "publication_date": "2007-06-25T00:00:00Z",
                "extraction_method": "api"
            }
        ]
        
        report = create_summary_report(video_data)
        
        assert report["total_videos_processed"] == 3
        assert report["successful_extractions"] == 3
        assert report["failed_extractions"] == 0
        assert report["success_rate"] == "100.0%"
        
        view_stats = report["view_statistics"]
        assert view_stats["total_views"] == 6000
        assert view_stats["average_views"] == 2000
        assert view_stats["max_views"] == 3000
        assert view_stats["min_views"] == 1000
        
        assert report["extraction_methods"]["api"] == 2
        assert report["extraction_methods"]["yt_dlp"] == 1
        
        assert report["top_channels"]["Channel A"] == 2
        assert report["top_channels"]["Channel B"] == 1
        
        date_range = report["date_range"]
        assert date_range["earliest"] == "2005-04-23T00:00:00Z"
        assert date_range["latest"] == "2007-06-25T00:00:00Z"
        assert date_range["total_videos_with_dates"] == 3
    
    def test_create_summary_report_with_failures(self):
        """Test summary report with some failures"""
        video_data = [
            {
                "title": "Video 1",
                "views": 1000,
                "extraction_method": "api"
            },
            {
                "error": "Extraction failed",
                "video_id": "invalid_id"
            },
            {
                "title": "Video 3",
                "views": 3000,
                "extraction_method": "yt_dlp"
            }
        ]
        
        report = create_summary_report(video_data)
        
        assert report["total_videos_processed"] == 3
        assert report["successful_extractions"] == 2
        assert report["failed_extractions"] == 1
        assert report["success_rate"] == "66.7%"
        
        view_stats = report["view_statistics"]
        assert view_stats["total_views"] == 4000
        assert view_stats["average_views"] == 2000
    
    def test_create_summary_report_empty_data(self):
        """Test summary report with empty data"""
        report = create_summary_report([])
        
        assert "error" in report
        assert report["error"] == "No video data provided"
    
    def test_create_summary_report_no_view_data(self):
        """Test summary report with no view data"""
        video_data = [
            {"title": "Video 1", "extraction_method": "api"},
            {"title": "Video 2", "extraction_method": "yt_dlp"}
        ]
        
        report = create_summary_report(video_data)
        
        view_stats = report["view_statistics"]
        assert view_stats["total_views"] == 0
        assert view_stats["average_views"] == 0
        assert view_stats["max_views"] == 0
        assert view_stats["min_views"] == 0