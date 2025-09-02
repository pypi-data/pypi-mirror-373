# JIRA Ticket Checker Plugin for Flake8

A Flake8 plugin for checking JIRA ticket status in your codebase.

## Features

- Find JIRA ticket links anywhere in code (not just in TODO comments)
- Check ticket status via JIRA API
- Authentication via environment variables
- Configurable timeout (default 1 second)
- Proper connection error handling

## Environment Variables

The plugin requires the following environment variables:

- `JIRA_USERNAME` - your JIRA username
- `JIRA_TOKEN` - JIRA API token (recommended)
- `JIRA_PASSWORD` - JIRA password (alternative to token, less secure)
- `JIRA_BASE_URL` - your JIRA server URL (e.g., `https://your-company.atlassian.net`)
- `JIRA_TIMEOUT` - connection timeout in seconds (optional, default: 1)

## Usage in CI

```bash
export JIRA_USERNAME="your.username@company.com"
export JIRA_TOKEN="your_api_token"
export JIRA_BASE_URL="https://your-company.atlassian.net"
export JIRA_TIMEOUT="3"  # Optional: 3 seconds timeout
flake8 --select=JTC path/to/your/code
```

## Configuration

You can also configure the plugin via `setup.cfg`:

```ini
[flake8]
jira_base_url = https://your-company.atlassian.net
jira_checker_silent = false
jira_timeout = 3
```

## Error Codes

- `JTC001` - JIRA ticket is in DONE/CLOSED/RESOLVED status and should be removed
- `JTC002` - JIRA ticket not found

## Supported Link Formats

The plugin finds links like:
- `https://your-company.atlassian.net/browse/PROJ-12345`
- `your-company.atlassian.net/browse/TEST-123`
- In comments, strings, URLs, etc.

## Ticket Status

Tickets are considered closed if their status is: DONE, CLOSED, RESOLVED

## Configuration Options

### Silent Mode

You can suppress warnings by setting:
- Environment variable: `JIRA_CHECKER_SILENT=true`
- In setup.cfg: `jira_checker_silent = true`

### Timeout

You can configure the JIRA API connection timeout:
- Environment variable: `JIRA_TIMEOUT=5` (in seconds)
- In setup.cfg: `jira_timeout = 5` (in seconds)
- Default: 1 second
