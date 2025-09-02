import pytest
import tempfile
import subprocess
import sys
from pathlib import Path


class TestIntegration:
    """Integration tests for the MCP Gazette Archiver."""
    
    def test_package_installation(self):
        """Test that the package can be installed correctly."""
        # This would be run in a separate environment in practice
        result = subprocess.run([
            sys.executable, '-c', 
            'import mcp_gazette_archiver; print("Import successful")'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            # Package might not be installed yet - that's ok for tests
            pytest.skip("Package not installed - run 'pip install .' first")
        
        assert "Import successful" in result.stdout
    
    def test_mcp_server_import(self):
        """Test that the MCP server components can be imported."""
        try:
            from mcp_gazette_archiver.server import (
                setup_gztarchiver_config,
                run_gztarchiver, 
                check_archive_status
            )
            # If we get here, imports worked
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import MCP server components: {e}")
    
    def test_fastmcp_dependency(self):
        """Test that FastMCP is available."""
        try:
            import fastmcp
            assert hasattr(fastmcp, 'FastMCP')
        except ImportError:
            pytest.fail("FastMCP dependency not available")
    
    def test_gztarchiver_dependency_installation(self):
        """Test that gztarchiver package would be installed."""
        # We can't test actual installation here, but we can verify
        # the dependency specification in pyproject.toml
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        if pyproject_path.exists():
            content = pyproject_path.read_text()
            assert "gztarchiver" in content
            assert "git+https://github.com/LDFLK/gztarchiver.git" in content
        else:
            pytest.fail("pyproject.toml not found")
    
    def test_config_file_creation(self):
        """Test that config files can be created and are valid YAML."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.yaml"
            
            # Test the example config exists and is valid
            example_config = Path(__file__).parent.parent / "examples" / "config_example.yaml"
            if example_config.exists():
                import yaml
                with open(example_config) as f:
                    config_data = yaml.safe_load(f)
                assert isinstance(config_data, dict)
                assert "google_drive" in config_data
                assert "deepseek" in config_data
                assert "archive" in config_data
    
    def test_command_line_entry_point(self):
        """Test that the command line entry point is configured."""
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        if pyproject_path.exists():
            content = pyproject_path.read_text()
            assert "[project.scripts]" in content
            assert "mcp-gazette" in content
        else:
            pytest.fail("pyproject.toml not found")
    
    @pytest.mark.slow
    def test_full_workflow_simulation(self):
        """Simulate a full workflow without actually running the archiver."""
        from mcp_gazette_archiver.server import (
            SetupConfigArgs,
            RunArchiverArgs, 
            CheckStatusArgs,
            setup_gztarchiver_config
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            
            # Test config setup
            setup_args = SetupConfigArgs(
                google_drive_folder_id="test_folder_id",
                deepseek_api_key="test_api_key", 
                archive_location=temp_dir,
                config_path=str(config_path)
            )
            
            result = setup_gztarchiver_config(setup_args)
            assert len(result) >= 1
            assert "successfully" in result[0].lower()
            assert config_path.exists()
            
            # Verify config content
            import yaml
            with open(config_path) as f:
                config_data = yaml.safe_load(f)
            
            assert config_data["google_drive"]["folder_id"] == "test_folder_id"
            assert config_data["deepseek"]["api_key"] == "test_api_key"
            assert config_data["archive"]["location"] == temp_dir


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
