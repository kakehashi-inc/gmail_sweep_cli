# Gmail Sweep CLI

A CLI tool that aggregates emails from Gmail's "All Mail" by sender address for a specified period, helps identify unnecessary senders, and bulk-deletes (moves to Trash) their emails.

## Features

- Aggregate emails by sender address with count, frequency, and subject information
- Interactive paginated display sorted by email count
- Period navigation (shift forward/backward)
- Mark senders for deletion and bulk-move their emails to Trash
- Automatically skip starred and important emails during deletion
- JSON cache for collected data (skip re-collection on next run)

## Requirements

- Python 3.10+
- A Google Cloud project with Gmail API enabled

## Quick Start

```bash
uvx gmail_sweep_cli user@gmail.com
```

## Google Cloud Console Setup

### 1. Create a Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project selector at the top of the page
3. Click **New Project**
4. Enter a project name (e.g. `gmail_sweep_cli`) and click **Create**
5. Make sure the new project is selected

### 2. Enable the Gmail API

1. Navigate to **APIs & Services > Library**
2. Search for **Gmail API**
3. Click **Gmail API** in the results
4. Click **Enable**

### 3. Configure the OAuth Consent Screen

1. Navigate to **APIs & Services > OAuth consent screen**
2. Select **External** as the user type and click **Create**
3. Fill in the required fields:
   - **App name**: e.g. `Gmail Sweep CLI`
   - **User support email**: your email address
   - **Developer contact email**: your email address
4. Click **Save and Continue**
5. On the **Scopes** page, click **Add or Remove Scopes** and add:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.modify`
6. Click **Save and Continue**
7. On the **Test users** page, click **Add Users** and add the Gmail address you want to use
8. Click **Save and Continue**

### 4. Create OAuth Client ID

1. Navigate to **APIs & Services > Credentials**
2. Click **Create Credentials > OAuth client ID**
3. Select **Desktop app** as the application type
4. Enter a name (e.g. `Gmail Sweep CLI`)
5. Click **Create**
6. Click **Download JSON** to download the credentials file
7. Rename the downloaded file to `client_secret.json`
8. Place it at `./credentials/client_secret.json` (relative to where you run the tool)

### 5. Important Notes

- **Test mode limitations**: Up to 100 test users; refresh tokens expire after 7 days
- **Production publishing**: Requires Google's verification/review process for broader access

## Usage

### Authentication

Run the authentication flow first (opens a browser):

```bash
uvx gmail_sweep_cli --auth user@gmail.com
```

### Basic Usage

```bash
# Default: collect emails from the past 30 days
uvx gmail_sweep_cli user@gmail.com

# Collect emails from the past 60 days
uvx gmail_sweep_cli user@gmail.com --days 60

# Specify exact date range
uvx gmail_sweep_cli user@gmail.com --start 2025-01-01 --end 2025-01-31

# Custom token directory
uvx gmail_sweep_cli user@gmail.com --token-dir /path/to/tokens/

# Custom credentials file
uvx gmail_sweep_cli user@gmail.com --credentials /path/to/client_secret.json
```

### Command-Line Options

| Option | Short | Description | Default |
|---|---|---|---|
| `email` | - | Target Gmail address (positional, required) | - |
| `--auth` | `-a` | Run OAuth authentication flow | `False` |
| `--days` | `-d` | Collection period in days | `30` |
| `--start` | `-s` | Collection start date (YYYY-MM-DD) | `None` |
| `--end` | `-e` | Collection end date (YYYY-MM-DD) | `None` |
| `--credentials` | `-c` | Path to `client_secret.json` | `./credentials/client_secret.json` |
| `--token-dir` | `-t` | Token storage directory | `./credentials/` |
| `--cache-dir` | - | Cache directory for collected data | `./cache/` |

## Operation Guide

### Main Screen

The main screen displays a paginated table of sender addresses sorted by email count (descending).

| Input | Action | Description |
|---|---|---|
| `r` | Re-collect | Re-fetch emails from Gmail API for the current period |
| `prev` | Previous period | Shift the collection period one interval into the past |
| `next` | Next period | Shift the collection period one interval into the future |
| `<` | Previous page | Show the previous 20 entries |
| `>` | Next page | Show the next 20 entries |
| *number* | Detail | Show detail view for the address at that row number |
| `l` | List marked | Display all addresses marked for deletion |
| `c` | Clear marks | Remove all deletion marks |
| `all-delete` | Execute delete | Move emails from marked addresses to Trash |
| `q` | Quit | Exit the program |

### Detail Screen

Shows full information for a single sender address (received dates, distinct subjects).

| Input | Action | Description |
|---|---|---|
| `Enter` (empty) | Back | Return to the main screen |
| `mark` | Mark | Mark this address for deletion |

### Deletion

- The `all-delete` command moves **all emails** from marked addresses to Trash (across **all** time periods, not just the current view).
- **Starred** and **Important** emails are automatically skipped.
- Only uppercase `Y` confirms the deletion; any other input cancels.

## Development

### Setup

```bash
git clone https://github.com/kakehashi-inc/gmail_sweep_cli.git
cd gmail_sweep_cli
python -m venv venv
source venv/bin/activate      # Linux/macOS
# venv\Scripts\activate       # Windows
pip install -e ".[dev]"
```

### Running from Source

```bash
# Authentication
python -m gmail_sweep_cli --auth user@gmail.com

# Normal execution
python -m gmail_sweep_cli user@gmail.com
```

### VSCode Debug

Create `.vscode/launch.json` in the project root:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "debugpy",
      "request": "launch",
      "name": "Launch CLI",
      "module": "gmail_sweep_cli.main",
      "args": [
        "example@gmail.com"
      ],
      "console": "integratedTerminal",
      "justMyCode": true,
      "cwd": "${workspaceFolder}"
    },
    {
      "type": "debugpy",
      "request": "launch",
      "name": "Launch CLI with Auth",
      "module": "gmail_sweep_cli.main",
      "args": [
        "--auth",
        "example@gmail.com"
      ],
      "console": "integratedTerminal",
      "justMyCode": true,
      "cwd": "${workspaceFolder}"
    }
  ]
}
```

| Name | Description |
|---|---|
| **Launch CLI** | Run the CLI with a target email address (default mode) |
| **Launch CLI with Auth** | Run the OAuth authentication flow for the target email |

> Replace `example@gmail.com` with the actual Gmail address you want to target.

## License

MIT License. See [LICENSE](LICENSE) for details.
