import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock

from mcp_gazette_archiver.server import (
    SetupConfigArgs,
    RunArchiverArgs,
    CheckStatusArgs,
    setup_gztarchiver_config,
    run_gztarchiver,
    check_archive_status
)


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        config = {
            'google_drive': {'folder_id': 'test_folder', 'credentials_file': 'test_creds.json'},
            'deepseek': {'api_key': 'test_key'},
            'archive': {'location': '~/test-archive'}
        }
        yaml.dump(config, f)
        yield f.name
    Path(f.name).unlink(missing_ok=True)


class TestServerFunctions:
    """Test the main server functions."""
    
    def test_setup_config_args_validation(self):
        """Test that SetupConfigArgs validates correctly."""
        # Valid args
        args = SetupConfigArgs(
            google_drive_folder_id="test_folder",
            deepseek_api_key="test_key",
            archive_location="~/test"
        )
        assert args.google_drive_folder_id == "test_folder"
        assert args.deepseek_api_key == "test_key"
        assert args.archive_location == "~/test"
        
        # Test optional parameters
        args_with_optional = SetupConfigArgs(
            google_drive_folder_id="test_folder",
            deepseek_api_key="test_key",
            archive_location="~/test",
            config_path="custom_config.yaml",
            credentials_file="custom_creds.json"
        )
        assert args_with_optional.config_path == "custom_config.yaml"
        assert args_with_optional.credentials_file == "custom_creds.json"
    
    def test_run_archiver_args_validation(self):
        """Test that RunArchiverArgs validates correctly."""
        # Valid args
        args = RunArchiverArgs(year=2024, month=6, day=10)
        assert args.year == 2024
        assert args.month == 6
        assert args.day == 10
        assert args.language == "en"  # default
        
        # Test with custom language
        args_custom = RunArchiverArgs(year=2024, month=6, day=10, language="si")
        assert args_custom.language == "si"
        
        # Test validation errors
        with pytest.raises(ValueError):
            RunArchiverArgs(year=2024, month=13, day=10)  # Invalid month
        
        with pytest.raises(ValueError):
            RunArchiverArgs(year=2024, month=6, day=32)  # Invalid day
    
    def test_check_status_args_validation(self):
        """Test that CheckStatusArgs validates correctly."""
        args = CheckStatusArgs(archive_location="~/test")
        assert args.archive_location == "~/test"
    
    @patch('mcp_gazette_archiver.server.Path')
    def test_setup_gztarchiver_config(self, mock_path):
        """Test the setup_gztarchiver_config function."""
        # Mock file operations
        mock_config_path = MagicMock()
        mock_path.return_value = mock_config_path
        mock_config_path.parent.mkdir = MagicMock()
        mock_config_path.write_text = MagicMock()
        
        args = SetupConfigArgs(
            google_drive_folder_id="test_folder",
            deepseek_api_key="test_key",
            archive_location="~/test"
        )
        
        result = setup_gztarchiver_config(args)
        
        assert result[0] == "Configuration setup completed successfully"
        mock_config_path.parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_config_path.write_text.assert_called_once()
    
    @patch('mcp_gazette_archiver.server.subprocess.run')
    @patch('mcp_gazette_archiver.server.Path')
    def test_run_gztarchiver_success(self, mock_path, mock_subprocess):
        """Test successful gztarchiver execution."""
        # Mock config file exists
        mock_config_path = MagicMock()
        mock_path.return_value = mock_config_path
        mock_config_path.exists.return_value = True
        
        # Mock successful subprocess execution
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Archive completed successfully"
        mock_subprocess.return_value = mock_result
        
        args = RunArchiverArgs(year=2024, month=6, day=10)
        result = run_gztarchiver(args)
        
        assert "successfully started" in result[0].lower()
        mock_subprocess.assert_called_once()
    
    @patch('mcp_gazette_archiver.server.Path')
    def test_run_gztarchiver_no_config(self, mock_path):
        """Test gztarchiver execution when config doesn't exist."""
        # Mock config file doesn't exist
        mock_config_path = MagicMock()
        mock_path.return_value = mock_config_path
        mock_config_path.exists.return_value = False
        
        args = RunArchiverArgs(year=2024, month=6, day=10)
        result = run_gztarchiver(args)
        
        assert "Configuration file not found" in result[0]
    
    @patch('mcp_gazette_archiver.server.subprocess.run')
    @patch('mcp_gazette_archiver.server.Path')
    def test_run_gztarchiver_failure(self, mock_path, mock_subprocess):
        """Test gztarchiver execution failure."""
        # Mock config file exists
        mock_config_path = MagicMock()
        mock_path.return_value = mock_config_path
        mock_config_path.exists.return_value = True
        
        # Mock failed subprocess execution
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Error occurred"
        mock_subprocess.return_value = mock_result
        
        args = RunArchiverArgs(year=2024, month=6, day=10)
        result = run_gztarchiver(args)
        
        assert "Failed to run gztarchiver" in result[0]
    
    @patch('mcp_gazette_archiver.server.Path')
    def test_check_archive_status_with_data(self, mock_path):
        """Test checking archive status when files exist."""
        # Mock archive directory and files
        mock_archive_path = MagicMock()
        mock_path.return_value = mock_archive_path
        mock_archive_path.exists.return_value = True
        mock_archive_path.is_dir.return_value = True
        
        # Mock CSV files
        mock_archived_csv = MagicMock()
        mock_failed_csv = MagicMock()
        mock_classified_csv = MagicMock()
        
        mock_archive_path.glob.side_effect = [
            [mock_archived_csv],  # archived_logs.csv
            [mock_failed_csv],    # failed_logs.csv  
            [mock_classified_csv] # classified_metadata.csv
        ]
        
        # Mock file reading
        mock_archived_csv.read_text.return_value = "id,file\n1,test1.pdf\n2,test2.pdf"
        mock_failed_csv.read_text.return_value = "id,error\n3,download_failed"
        mock_classified_csv.read_text.return_value = "id,category\n1,legal\n2,economic"
        
        args = CheckStatusArgs(archive_location="~/test")
        result = check_archive_status(args)
        
        assert "Archive Status Summary" in result[0]
        assert "Total archived: 2" in result[0]
        assert "Failed downloads: 1" in result[0]
        assert "Classified documents: 2" in result[0]
    
    @patch('mcp_gazette_archiver.server.Path')
    def test_check_archive_status_no_directory(self, mock_path):
        """Test checking archive status when directory doesn't exist."""
        mock_archive_path = MagicMock()
        mock_path.return_value = mock_archive_path
        mock_archive_path.exists.return_value = False
        
        args = CheckStatusArgs(archive_location="~/test")
        result = check_archive_status(args)
        
        assert "Archive directory not found" in result[0]


if __name__ == "__main__":
    pytest.main([__file__])
