# MCP Gazette Archiver

FastMCP Server for Sri Lankan Gazette Archiver using the `gztarchiver` package.

## Prerequisites

- Python 3.8+ (3.10+ recommended)
- Git
- Internet access
- Google Drive credentials (you will create these in Step 4)
- DeepSeek API key (optional, for AI classification)

## Step-by-step Setup 

### Step 1: Clone the repository

```bash
git clone https://github.com/Isuru-rangana/mcp_DataPlatform.git
cd mcp_DataPlatform/gazette-archiver-mcp
```

### Step 2: Prepare environment

```bash
# Navigate to the project directory
cd gazette-archiver-mcp

# Create and activate a virtual environment
python3 -m venv venv-mcp
source venv-mcp/bin/activate
python -m pip install --upgrade pip

# Install the package and dependencies
pip install -e .
pip install -r requirements.txt

### Step 3: Create local directories

mkdir -p credentials upload_results
# Place your OAuth client secrets as: credentials/credentials.json 
# token.json will be generated on first auth and stored in credentials/token.json

Add these entries to `.gitignore` to avoid committing secrets and local outputs:

```gitignore
gztarchiver_config.yaml
credentials/
upload_results/
*.key
*.json
```

### Step 4: Setup Cloud Archive (Google Drive) 🌐

Set up Google Cloud credentials to enable uploads to Google Drive.

- Create a Google Cloud project
- Enable the Google Drive API
- Download your `credentials.json`
- Save it inside a dedicated `credentials/` folder (do not commit it)
- You will add these paths in Step 2

Detailed steps:
1. Open Google Cloud Console: https://console.cloud.google.com/
2. Create a new project
3. Enable the Google Drive API in that project
4. Go to APIs & Services → Credentials
5. Click "Create Credentials" → "OAuth Client ID"
6. Choose Desktop App
7. Download the credentials file (`credentials.json`)
8. Create a folder named `credentials`
9. Place `credentials.json` inside the `credentials/` folder
10. Copy the full path; you will reference it in `gztarchiver_config.yaml`


### Step 5: Create your configuration file 
```
Then edit `gztarchiver_config.yaml` to match your environment. Recommended minimal fields:

```yaml
archive:
  archive_location: /absolute/path/to/doc-archive
  g_drive_parent_folder_id: YOUR_GOOGLE_DRIVE_FOLDER_ID
credentials:
  client_secrets_path: ${PWD}/credentials/credentials.json
  token_path: ${PWD}/credentials/token.json
  deepseek_api_key: YOUR_DEEPSEEK_API_KEY
output:
  doc_metadata_json: ${PWD}/meta_data/doc_metadata.json
  upload_results_json: ${PWD}/upload_results/upload_results_
  years_json: ${PWD}/meta_data/years.json
scrape:
  url: https://documents.gov.lk/view/extra-gazettes/egz.html
```

Edit `gztarchiver_config.yaml` to specify:
- Download location(s)
- Google Drive folder ID
- Credentials paths
- DeepSeek API key

This YAML file acts as the control center for your archiving operations.

### Step 6: Run the Program 🏃‍♂️

With your virtual environment active and config ready:

```bash
python3 -m mcp_gazette_archiver.server
```

Note: Run the server at least once before configuring VS Code chat clients. The first run completes Google Drive authorization and creates `credentials/token.json`.

### Terminal Usage
```bash
# Start MCP server
cd gazette-archiver-mcp
source venv-mcp/bin/activate
python3 -m mcp_gazette_archiver.server
```

### Step 7: VS Code chat clients configuration setup (e.g., Cline)

Prerequisite: You have started the server once and completed the Google auth flow above.

If you use a VS Code chat bot that supports MCP (like Cline or Claude Dev), add this server to your MCP configuration.
#### Example: Cline 

check this path in vs code   (e.g., `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`), use this template and replace placeholders with your paths:

```json
{
  "mcpServers": {
    "gazette-archiver": {
      "disabled": false,
      "timeout": 60,
      "type": "stdio",
      "command": "/absolute/path/to/gazette-archiver-mcp/venv-mcp/bin/python3",
      "args": [
        "-m",
        "mcp_gazette_archiver.server"
      ],
      "env": {
        "PYTHONPATH": "/absolute/path/to/gazette-archiver-mcp/src"
      }
    }
  }
}
```

Replace `/absolute/path/to/gazette-archiver-mcp` with the real location on your machine.

#### Cline setup (VS Code) — step-by-step

1. Make sure you have completed Steps 1–6 above (venv created, package installed).
2. Open or create the Cline settings file:
   - Linux/macOS: `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
   - Windows: `%APPDATA%/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
3. Add the JSON shown above, replacing placeholders with your absolute paths.
4. Save the file and reload VS Code (Developer: Reload Window).
5. Open the Cline panel; it should auto-discover the `gazette-archiver` MCP server.
6. Test by invoking tools like `setup_gztarchiver_config` or `check_archive_status`.

### Available MCP Tools

1. **setup_gztarchiver_config** - Setup configuration for archiving
2. **run_gztarchiver** - Execute the gazette archiving process
3. **check_archive_status** - Monitor archive progress and statistics

### Example Workflow

1. **Setup Configuration:**
   ```json
   {
     "tool": "setup_gztarchiver_config",
     "arguments": {
       "google_drive_folder_id": "your_folder_id",
       "deepseek_api_key": "your_api_key",
       "archive_location": "~/gazette-archive"
     }
   }
   ```

2. **Run Archiver:**
   ```json
   {
     "tool": "run_gztarchiver", 
     "arguments": {
       "year": 2024,
       "month": 6,
       "day": 10,
       "language": "en"
     }
   }
   ```

3. **Check Status:**
   ```json
   {
     "tool": "check_archive_status",
     "arguments": {
       "archive_location": "~/gazette-archive"
     }
   }
   ```

## Language Codes

- `en` - English
- `si` - Sinhala  
- `ta` - Tamil

## Requirements

- Python 3.8+
- Google Drive API credentials
- DeepSeek API key for AI classification
- Internet connection for scraping and downloading

## Dependencies

This MCP server automatically installs:
- `gztarchiver` - The core gazette archiving package
- `fastmcp` - FastMCP framework
- `pydantic` - Data validation
- `pyyaml` - YAML configuration support

## Output Structure

Downloaded gazettes are organized as:
```
archive_location/
├── YYYY/
│   ├── MM/
│   │   ├── DD/
│   │   │   └── gazette_id/
│   │   │       └── gazette_id_language.pdf
│   ├── archived_logs.csv
│   ├── failed_logs.csv
│   ├── classified_metadata.csv
│   └── unavailable_logs.csv
```

## New MCP Resources & Prompts

### Available Resources
- `gazette://metadata/latest` - Latest gazette metadata
- `gazette://metadata/by-date/{year}/{month}/{day}` - Metadata by specific date
- `gazette://config/current` - Current configuration
- `gazette://stats/summary` - Archive statistics
- `gazette://stats/failures` - Failure analysis

### Available Prompts
- `gazette-query` - Structured archive queries
- `gazette-analysis` - Trend and pattern analysis
- `gazette-classifier` - Document classification prompts
- `batch-classifier` - Batch processing prompts

## Support

For issues with the core archiving functionality, refer to the gztarchiver project:
https://github.com/LDFLK/gztarchiver
# archiver
# archiver_choreo
