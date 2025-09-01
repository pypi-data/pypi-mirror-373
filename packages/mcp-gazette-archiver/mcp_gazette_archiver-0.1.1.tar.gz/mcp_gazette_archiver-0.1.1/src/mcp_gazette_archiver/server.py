#!/usr/bin/env python3
"""
FastMCP Server for Gazette Archiver
Uses the auto-installed gztarchiver package with robust dependency management
"""
import subprocess
import yaml
import sys
import os
import datetime
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field

# Add current directory to Python path for reliable imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def ensure_gztarchiver():
    """Ensure gztarchiver is available, install from Git if needed"""
    try:
        import gztarchiver
        print("✅ gztarchiver already available")
        return True
    except ImportError:
        print("📦 gztarchiver not found, installing from Git...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "gztarchiver @ git+https://github.com/LDFLK/gztarchiver.git"
            ])
            print("✅ gztarchiver installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install gztarchiver: {e}")
            return False

try:
    from fastmcp import FastMCP
    print("✅ FastMCP import successful")
except Exception as e:
    print(f"❌ FastMCP import failed: {e}")
    import traceback
    traceback.print_exc()
    raise

# Import new modules (lazy loading to avoid startup issues)
# from .resources import get_gazette_metadata_resource, get_archive_stats_resource
# from .prompts import get_archive_query_prompts, get_classification_prompts

# Initialize FastMCP server
try:
    mcp = FastMCP("Gazette Archiver MCP Server")
    print("✅ FastMCP server initialized successfully")
except Exception as e:
    print(f"❌ FastMCP server initialization failed: {e}")
    import traceback
    traceback.print_exc()
    raise

def get_config_from_env():
    """Get configuration for GitHub repository deployment"""
    return {
        "scrape": {
            "url": "https://documents.gov.lk/view/extra-gazettes/egz.html"
        },
        "output": {
            "years_json": "meta_data/years.json",
            "doc_metadata_json": "meta_data/doc_metadata.json",
            "upload_results_json": "upload_results/upload_results_"
        },
        "archive": {
            "archive_location": "archive",
            "g_drive_parent_folder_id": os.getenv("GOOGLE_DRIVE_FOLDER_ID", ""),
            "archive_base_url": "archive",
            "force_download_base_url": "archive"
        },
        "credentials": {
            "token_path": "credentials/token.json",
            "client_secrets_path": "credentials/credentials.json",
            "deepseek_api_key": os.getenv("DEEPSEEK_API_KEY", "sk-a6f5f5019a6d4fecbb85576d86d4f8a8")
        },
        "db_credentials": {
            "mongo_db_uri": os.getenv("MONGODB_URI", "mongodb+srv://Isuru:1234@data-platform.0ezuyqj.mongodb.net/?retryWrites=true&w=majority&appName=Data-Platform")
        }
    }

def ensure_directories():
    """Ensure required directories exist for GitHub repository"""
    # Create directories in the repository structure
    dirs = [
        "archive",           # Main archive directory
        "meta_data",         # Metadata files
        "upload_results",    # Upload logs
        "credentials"        # Credentials (if needed)
    ]
    for dir_path in dirs:
        try:
            # Force create the directory with full permissions
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {dir_path}")
            
            # Ensure archive directory is writable
            if dir_path == "archive":
                # Create a test file to verify write permissions
                test_file = Path(dir_path) / ".test_write"
                test_file.write_text("test")
                test_file.unlink()
                print(f"✅ Verified write permissions for: {dir_path}")
                
        except PermissionError as e:
            print(f"❌ Permission error creating {dir_path}: {e}")
            # Try to create with sudo-like approach or alternative method
            try:
                import subprocess
                subprocess.run(["mkdir", "-p", dir_path], check=True)
                print(f"✅ Created directory using alternative method: {dir_path}")
            except Exception as sub_e:
                print(f"❌ Failed to create directory {dir_path}: {sub_e}")
        except Exception as e:
            print(f"⚠️  Warning: Could not create directory {dir_path}: {e}")

# Pydantic models for type safety
class GazetteConfig(BaseModel):
    """Configuration model for gztarchiver package"""
    google_drive_folder_id: str = Field(description="Google Drive folder ID for cloud uploads")
    deepseek_api_key: str = Field(description="DeepSeek API key for AI document classification")
    mongo_db_uri: str = Field(description="MongoDB connection URI for storing gazette metadata")
    archive_location: str = Field(default="~/gazette-archive", description="Local directory for storing downloaded gazettes")
    credentials_path: str = Field(default="./credentials", description="Path to Google Cloud credentials directory")

class GazetteRunParams(BaseModel):
    """Parameters for running gazette archiver"""
    year: int = Field(description="Year to archive", ge=2000, le=2030)
    month: int = Field(description="Month to archive", ge=1, le=12)
    day: int = Field(description="Day to archive", ge=1, le=31)
    language: str = Field(description="Language code for gazettes", pattern="^(en|si|ta)$")

class StatusQuery(BaseModel):
    """Query parameters for checking archive status"""
    archive_location: Optional[str] = Field(None, description="Archive directory to analyze")
    year: Optional[int] = Field(None, description="Specific year to check")

# FastMCP Tools
@mcp.tool()
def setup_gztarchiver_config(config: GazetteConfig) -> str:
    """
    Setup configuration file for the gztarchiver package.
    
    Creates a YAML configuration file that gztarchiver will use for:
    - Web scraping gazette metadata
    - Downloading PDF documents  
    - Uploading to Google Drive
    - AI-powered document classification
    """
    try:
        # Use environment-based config for cloud deployment
        gazette_config = get_config_from_env()
        
        # Override with provided config if available
        if config.google_drive_folder_id:
            gazette_config["archive"]["g_drive_parent_folder_id"] = config.google_drive_folder_id
        if config.deepseek_api_key:
            gazette_config["credentials"]["deepseek_api_key"] = config.deepseek_api_key
        if config.mongo_db_uri:
            gazette_config["db_credentials"]["mongo_db_uri"] = config.mongo_db_uri
        if config.archive_location:
            gazette_config["archive"]["archive_location"] = config.archive_location
            gazette_config["archive"]["archive_base_url"] = config.archive_location
            gazette_config["archive"]["force_download_base_url"] = config.archive_location
        
        # Ensure directories exist
        ensure_directories()
        
        # Save configuration file
        config_path = Path("gztarchiver_config.yaml")
        with open(config_path, 'w') as f:
            yaml.dump(gazette_config, f, default_flow_style=False, indent=2)
        
        return f"""Gazette Archiver Configuration Created Successfully!

Config File: {config_path.absolute()}
Archive Location: {gazette_config['archive']['archive_location']}
Google Drive Folder ID: {gazette_config['archive']['g_drive_parent_folder_id']}
MongoDB URI: {gazette_config['db_credentials']['mongo_db_uri']}
DeepSeek API: Configured
Credentials Path: {gazette_config['credentials']['client_secrets_path']}

Ready to run gazette archiver!
Next: Use 'run_gztarchiver' tool to start archiving"""
        
    except Exception as e:
        return f"❌ Failed to create configuration: {str(e)}"


def _execute_gztarchiver(params: GazetteRunParams) -> str:
    """
    Internal callable function to execute gztarchiver using subprocess for cloud compatibility.
    Uses subprocess to avoid relative import issues in cloud environments.
    """
    try:
        # Ensure all required modules are available
        import sys
        import io
        import os
        import subprocess
        from contextlib import redirect_stdout, redirect_stderr
        
        # Verify gztarchiver is installed and working
        try:
            import gztarchiver
            gztarchiver_version = getattr(gztarchiver, '__version__', 'unknown')
            
            # Test if gztarchiver.main exists
            try:
                from gztarchiver import main
                print(f"✅ gztarchiver v{gztarchiver_version} - main module accessible")
            except ImportError as e:
                return f"""❌ gztarchiver main module not accessible

🔍 Error: {e}
🔧 Troubleshooting Steps:
1. Verify installation: pip list | grep gztarchiver
2. Reinstall: pip install --force-reinstall git+https://github.com/LDFLK/gztarchiver.git
3. Check Python path: {sys.path}
4. Verify virtual environment is activated

Current working directory: {os.getcwd()}
Python executable: {sys.executable}"""
                
        except ImportError:
            return f"""❌ gztarchiver module not accessible

🔧 Troubleshooting Steps:
1. Verify installation: pip list | grep gztarchiver
2. Reinstall: pip install --force-reinstall git+https://github.com/LDFLK/gztarchiver.git
3. Check Python path: {sys.path}
4. Verify virtual environment is activated

Current working directory: {os.getcwd()}
Python executable: {sys.executable}
Installed packages: Run 'pip list' to verify gztarchiver installation"""
        
        # Verify configuration file exists - use absolute path to project directory
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        config_path = os.path.join(project_root, "gztarchiver_config.yaml")
        if not os.path.exists(config_path):
            return f""" Configuration file not found: {config_path}

 Create configuration first using 'setup_gztarchiver_config' tool
 Expected location: {config_path}
 Project directory: {project_root}
 Directory contents: {list(os.listdir(project_root))}"""
        
        # Validate and normalize configuration before running
        try:
            with open(config_path, "r") as cfg_f:
                loaded_config = yaml.safe_load(cfg_f) or {}

            # Ensure archive section and archive_location exist
            if "archive" not in loaded_config or not isinstance(loaded_config["archive"], dict):
                loaded_config["archive"] = {}
            if not loaded_config["archive"].get("archive_location"):
                # Default location
                loaded_config["archive"]["archive_location"] = str(Path("~/gazette-archive").expanduser())

            # Normalize output paths to absolute inside project repo if they are relative
            repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            if "output" not in loaded_config or not isinstance(loaded_config["output"], dict):
                loaded_config["output"] = {}
            # Defaults if missing
            loaded_config["output"].setdefault("years_json", "meta_data/years.json")
            loaded_config["output"].setdefault("doc_metadata_json", "meta_data/doc_metadata.json")
            loaded_config["output"].setdefault("upload_results_json", "upload_results/upload_results_")

            # Make absolute if relative
            for key in ("years_json", "doc_metadata_json", "upload_results_json"):
                val = loaded_config["output"].get(key)
                if isinstance(val, str) and not os.path.isabs(val):
                    loaded_config["output"][key] = os.path.join(repo_root, val)

            # Persist any changes
            with open(config_path, "w") as cfg_f:
                yaml.dump(loaded_config, cfg_f, default_flow_style=False, indent=2)
        except Exception as _cfg_err:
            # Continue, but include warning in logs
            print(f"  Config normalization warning: {_cfg_err}")

        # Build command arguments with absolute config path
        cmd_args = [
            "--year", str(params.year),
            "--lang", params.language,
            "--config", config_path
        ]
        
        if params.month:
            cmd_args.extend(["--month", str(params.month)])
        if params.day:
            cmd_args.extend(["--day", str(params.day)])
        
        filter_info = f"Year: {params.year}"
        if params.month:
            filter_info += f", Month: {params.month}"
        if params.day:
            filter_info += f", Day: {params.day}"
        filter_info += f", Language: {params.language}"
        
        # Execute gztarchiver using subprocess for cloud compatibility
        print(f"🔄 Executing gztarchiver with args: {cmd_args}")
        
        # Create a job ID for tracking
        import uuid
        job_id = str(uuid.uuid4())[:8]
        job_file = f"upload_results/job_{job_id}.json"
        
        # Start background process
        try:
            # Start the process in background with better error handling
            process = subprocess.Popen(
                [sys.executable, "-m", "gztarchiver.main"] + cmd_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.getcwd(),
                env=dict(os.environ, PYTHONPATH=os.getcwd())
            )
            
            # Wait a moment to see if process starts successfully
            import time
            time.sleep(2)
            
            # Check if process is still running
            if process.poll() is not None:
                # Process failed to start
                stdout, stderr = process.communicate()
                return f"""❌ Failed to start gztarchiver process

🔍 Process Details:
🆔 Job ID: {job_id}
📅 {filter_info}
📁 Archive Location: archive/

🔍 Error Information:
📤 Stdout: {stdout}
📤 Stderr: {stderr}
📤 Return Code: {process.returncode}

🔧 Troubleshooting:
1. Check if gztarchiver is installed: pip list | grep gztarchiver
2. Verify configuration file: {config_path}
3. Check Python path and dependencies

💡 Try running with a different date or check the configuration."""
            
            # Create job tracking file
            job_info = {
                "job_id": job_id,
                "status": "running",
                "start_time": str(datetime.datetime.now()),
                "parameters": {
                    "year": params.year,
                    "month": params.month,
                    "day": params.day,
                    "language": params.language
                },
                "process_id": process.pid,
                "archive_location": "archive"
            }
            
            # Save job info to file
            try:
                with open(job_file, 'w') as f:
                    import json
                    json.dump(job_info, f, indent=2)
            except Exception as e:
                print(f"Warning: Could not save job file: {e}")
            
            # Return immediate response with job tracking
            return f"""🚀 Gazette Archive Job Started!

📋 Job Details:
🆔 Job ID: {job_id}
📅 {filter_info}
📁 Archive Location: archive/
⏱️  Status: Processing in background
🔄 Process ID: {process.pid}

📊 What's happening:
1. 🔍 Scraping gazette metadata
2. 📥 Downloading PDF files
3. 🤖 AI classification with DeepSeek
4. ☁️  Uploading to Google Drive
5. 💾 Storing in MongoDB

📋 To check progress:
- Use 'check_archive_status' tool
- Job file: {job_file}
- Archive location: archive/

⏰ Note: This process may take 5-15 minutes depending on the number of gazettes."""
                
        except Exception as e:
            return f"""💥 Failed to start gztarchiver: {str(e)}

🔍 Error Details: {e}
🔧 This is a subprocess call to gztarchiver."""
        
        # Log output for debugging
        print(f"📤 Stdout length: {len(stdout_output)} chars")
        print(f"📤 Stderr length: {len(stderr_output)} chars")
        
        # Detect crawler errors printed to stdout
        had_crawl_error = "Error during crawling" in stdout_output or "Error during post-processing" in stdout_output

        status_emoji = "✅" if not had_crawl_error else "⚠️"
        title = "Gazette Archive Complete!" if not had_crawl_error else "Gazette Archive Completed with Issues"

        return f"""{status_emoji} {title}

📊 Archive Details:
🔧 gztarchiver v{gztarchiver_version}
📅 {filter_info}

📋 Archive Output:
{stdout_output}

{('🎉 Successfully archived gazettes!\n' + '📁 Files saved to: ' + (loaded_config['archive']['archive_location'] if 'loaded_config' in locals() else '/home/isuru/Desktop/doc-archive/') + '\n☁️  Uploaded to Google Drive\n🤖 AI classification completed') if not had_crawl_error else 'Some steps failed. Please check the above log for details.'}"""

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"""💥 Archive Error: {str(e)}

🔍 Detailed Error:
{error_details}

🔧 This is a subprocess call to gztarchiver.

📋 Troubleshooting:
1. Check if gztarchiver is installed: pip list | grep gztarchiver
2. Try manual execution: python -m gztarchiver.main --help
3. Check configuration file: not available

🐍 Environment Info:
- Python: {sys.executable}
- Working dir: {os.getcwd()}"""


@mcp.tool()
def run_gztarchiver(params: GazetteRunParams) -> str:
    """
    Execute the gztarchiver package with specified parameters.
    
    Runs the complete gazette archiving pipeline:
    1. Scrapes gazette metadata from Sri Lankan government website
    2. Downloads PDF documents based on filters
    3. Uploads documents to Google Drive
    4. Performs AI classification using DeepSeek
    5. Generates comprehensive logs and reports
    """
    return _execute_gztarchiver(params)


@mcp.tool()
def check_job_status(job_id: str) -> str:
    """
    Check the status of a specific archive job by job ID.
    
    Returns detailed information about the job including:
    - Current status (running, completed, failed)
    - Progress information
    - Error details if any
    """
    try:
        job_file = f"upload_results/job_{job_id}.json"
        if not Path(job_file).exists():
            return f"❌ Job not found: {job_id}"
        
        with open(job_file, 'r') as f:
            import json
            job_info = json.load(f)
        
        # Check if process is still running
        try:
            import psutil
            process = psutil.Process(job_info.get("process_id", 0))
            if process.is_running():
                status = "🔄 Running"
            else:
                status = "✅ Completed"
        except:
            status = "❓ Unknown"
        
        return f"""📋 Job Status Report

🆔 Job ID: {job_id}
⏱️  Status: {status}
📅 Started: {job_info.get('start_time', 'Unknown')}
📊 Parameters: {job_info.get('parameters', {})}
📁 Archive Location: {job_info.get('archive_location', 'Unknown')}

🔍 To check archive results, use 'check_archive_status' tool."""
        
    except Exception as e:
        return f"❌ Error checking job status: {str(e)}"

@mcp.tool()
def check_archive_status(query: StatusQuery) -> str:
    """
    Check the status of gazette archiving by analyzing log files and archive structure.
    
    Provides detailed statistics on:
    - Successfully archived documents
    - Failed downloads with reasons
    - AI classification results
    - Archive organization by year/month/day
    """
    try:
        # Use the archive directory in the repository
        archive_path = Path(query.archive_location or "archive")
        
        if not archive_path.exists():
            return f"""📁 Archive Location Not Found: {archive_path}

 The archive directory doesn't exist yet.
Run the gazette archiver first to create the archive structure.
📝 Use 'setup_gztarchiver_config' and 'run_gztarchiver' tools."""
        
        # Initialize status tracking
        status_lines = ["📊 Gazette Archive Status Report", "=" * 60]
        total_archived = 0
        total_failed = 0
        total_classified = 0
        total_unavailable = 0
        
        # Get year folders
        year_folders = [f for f in archive_path.iterdir() 
                       if f.is_dir() and f.name.isdigit()]
        
        if not year_folders:
            return f"""📁 No Archive Data Found in {archive_path}

📂 The archive directory exists but contains no year folders.
🚀 Run the gazette archiver to populate the archive.
💡 Use the 'run_gztarchiver' tool with your desired parameters."""
        
        # Analyze each year
        for year_folder in sorted(year_folders):
            year = year_folder.name
            
            # Skip if filtering by specific year
            if query.year and int(year) != query.year:
                continue
            
            # Check for log files
            archived_log = year_folder / "archived_logs.csv"
            failed_log = year_folder / "failed_logs.csv"
            classified_log = year_folder / "classified_metadata.csv"
            unavailable_log = year_folder / "unavailable_logs.csv"
            
            # Count entries in each log
            year_archived = 0
            year_failed = 0
            year_classified = 0
            year_unavailable = 0
            
            if archived_log.exists():
                with open(archived_log, 'r') as f:
                    year_archived = max(0, len(f.readlines()) - 1)  # Subtract header
            
            if failed_log.exists():
                with open(failed_log, 'r') as f:
                    year_failed = max(0, len(f.readlines()) - 1)
            
            if classified_log.exists():
                with open(classified_log, 'r') as f:
                    year_classified = max(0, len(f.readlines()) - 1)
                    
            if unavailable_log.exists():
                with open(unavailable_log, 'r') as f:
                    year_unavailable = max(0, len(f.readlines()) - 1)
            
            # Add to totals
            total_archived += year_archived
            total_failed += year_failed
            total_classified += year_classified
            total_unavailable += year_unavailable
            
            # Year summary
            status_lines.append(
                f"📅 {year}: "
                f"✅ {year_archived} archived | "
                f"❌ {year_failed} failed | "
                f"⚠️  {year_unavailable} unavailable | "
                f"🤖 {year_classified} classified"
            )
        
        # Overall summary
        status_lines.extend([
            "",
            "📈 Overall Summary:",
            f"✅ Total Successfully Archived: {total_archived}",
            f"❌ Total Failed Downloads: {total_failed}",
            f"⚠️  Total Unavailable Documents: {total_unavailable}",
            f"🤖 Total AI Classified: {total_classified}",
            f"📁 Archive Location: {archive_path}",
            "",
            "📋 Log Files Available:",
            "   • archived_logs.csv - Successfully downloaded documents",
            "   • failed_logs.csv - Failed downloads with error details", 
            "   • unavailable_logs.csv - Documents not available on website",
            "   • classified_metadata.csv - AI classification results"
        ])
        
        return "\n".join(status_lines)
        
    except Exception as e:
        return f"💥 Error checking archive status: {str(e)}"

def main():
    """Main entry point for the FastMCP server"""
    print("🚀 Starting Gazette Archiver MCP Server...")
    print("📦 Using auto-installed gztarchiver package")
    
    # Ensure gztarchiver is available
    if not ensure_gztarchiver():
        print("⚠️  Warning: gztarchiver installation failed, some features may not work")
    
    # Ensure required directories exist for cloud deployment
    try:
        ensure_directories()
        print("✅ Directories created successfully")
    except Exception as e:
        print(f"⚠️  Warning: Could not create directories: {e}")
    
    print("🌐 Server ready for basic operations...")
    
    # Note: Resources and prompts are disabled for cloud deployment
    # to avoid import issues. The core tools (setup, run, check) are available.
    
    print("✅ Core tools registered successfully!")
    print("🌐 Ready to serve MCP requests...")
    
    # Add a simple test to verify the server can start
    try:
        print("🔧 Testing server startup...")
        # Test that we can access the mcp object
        print(f"📋 Server name: {mcp.name}")
        print("✅ Server startup test passed!")
    except Exception as e:
        print(f"❌ Server startup test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # For cloud deployment, return the server instance instead of running it
    print("🚀 Server ready for cloud deployment...")
    
    # In cloud environments, FastMCP expects the server instance to be returned
    # rather than calling mcp.run() which tries to start its own event loop
    return mcp

if __name__ == "__main__":
    # For local development, run the server directly
    try:
        import asyncio
        import nest_asyncio
        
        # Apply nest_asyncio for local development
        try:
            nest_asyncio.apply()
            print("✅ Applied nest_asyncio for local development")
        except ImportError:
            print("⚠️  nest_asyncio not available")
        
        # Run the server locally
        server = main()
        if server:
            server.run()
    except Exception as e:
        print(f"❌ Local server run failed: {e}")
        import traceback
        traceback.print_exc()
