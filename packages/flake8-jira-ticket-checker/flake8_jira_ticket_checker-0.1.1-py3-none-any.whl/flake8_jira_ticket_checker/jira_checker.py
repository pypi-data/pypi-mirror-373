import ast
import os
import re
import configparser
from pathlib import Path
from typing import Generator, Tuple, Optional
from jira import JIRA
from jira.exceptions import JIRAError

from .__version__ import __version__


class JiraTicketChecker:
    """Flake8 plugin for checking JIRA ticket status."""

    name = 'jira-ticket-checker'
    version = __version__

    # Class-level JIRA client cache
    _jira_client_cache: Optional[JIRA] = None
    _connection_checked = False
    _connection_failed = False

    # Flags for tracking warning output in current process
    _warning_shown = False

    # Flag for controlling warning output
    # Can be controlled via JIRA_CHECKER_SILENT environment variable
    _silent_mode = None  # Will be initialized in _get_silent_mode()

    # JIRA server URL
    _jira_base_url = None  # Will be initialized in _get_jira_url()

    # JIRA API timeout
    _timeout = None  # Will be initialized in _get_timeout()

    # Regular expression for finding JIRA ticket links
    # Will be created dynamically based on configured URL
    JIRA_URL_PATTERN = None

    # Error codes
    JTC001 = "JTC001 JIRA ticket {ticket} is in DONE status and should be removed"
    JTC002 = "JTC002 JIRA ticket {ticket} not found"

    @classmethod
    def _get_jira_url(cls) -> str | None:
        """Determines JIRA server URL.

        Priority:
        1. JIRA_BASE_URL environment variable
        2. setup.cfg [flake8] jira_base_url setting
        3. If not found - returns None (checking will be stopped)
        """
        if cls._jira_base_url is not None:
            return cls._jira_base_url

        # Check environment variable (highest priority)
        env_url = os.getenv('JIRA_BASE_URL')
        if env_url:
            cls._jira_base_url = env_url.rstrip('/')
            return cls._jira_base_url

        # Look for setup.cfg in current directory and parents
        current_dir = Path.cwd()
        for parent in [current_dir] + list(current_dir.parents):
            setup_cfg = parent / 'setup.cfg'
            if setup_cfg.exists():
                try:
                    config = configparser.ConfigParser()
                    config.read(setup_cfg)

                    # Check [flake8] section
                    if config.has_section('flake8'):
                        url_value = config.get('flake8', 'jira_base_url', fallback=None)
                        if url_value:
                            cls._jira_base_url = url_value.rstrip('/')
                            return cls._jira_base_url

                except (configparser.Error, OSError):
                    # Ignore configuration reading errors
                    pass

                # Found setup.cfg, stop searching
                break

        # If URL not found, return None
        return None

    def __init__(self, tree: ast.AST, filename: str) -> None:
        self.tree = tree
        self.filename = filename

        # Get JIRA server URL
        jira_url = self._get_jira_url()

        # Only create pattern if URL is configured
        if jira_url:
            # Create regex pattern for finding tickets based on configured URL
            # Extract host from URL to create pattern
            from urllib.parse import urlparse
            parsed_url = urlparse(jira_url)
            jira_host = f"{parsed_url.scheme}://{parsed_url.netloc}"

            # Also look for links without protocol (domain only)
            domain_only = parsed_url.netloc

            self.__class__.JIRA_URL_PATTERN = re.compile(
                rf'(?:{re.escape(jira_host)}|{re.escape(domain_only)})/browse/([A-Z]+-\d+)',
                re.IGNORECASE
            )
        else:
            # If no URL configured, create a pattern that won't match anything
            self.__class__.JIRA_URL_PATTERN = re.compile(r'^$', re.IGNORECASE)

    def run(self) -> Generator[Tuple[int, int, str, type], None, None]:
        """Main file checking method."""
        # Check JIRA connection at the very beginning
        if not self._setup_jira_client():
            # If no connection, just skip checking
            # Warning is already shown in _setup_jira_client()
            return

        # Read file content
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                content = f.read()
        except (IOError, UnicodeDecodeError):
            return

        # Look for JIRA ticket links
        for match in self.JIRA_URL_PATTERN.finditer(content):
            ticket_key = match.group(1)
            line_number = content[:match.start()].count('\n') + 1
            column = match.start() - content.rfind('\n', 0, match.start()) - 1

            # Check ticket status
            status = self._get_ticket_status(ticket_key)

            if status == "DONE":
                yield (
                    line_number,
                    column,
                    self.JTC001.format(ticket=ticket_key),
                    type(self)
                )
            elif status == "NOT_FOUND":
                yield (
                    line_number,
                    column,
                    self.JTC002.format(ticket=ticket_key),
                    type(self)
                )
            elif status == "CONNECTION_ERROR":
                break  # Stop checking on connection problems

    @classmethod
    def _get_silent_mode(cls) -> bool:
        """Determines plugin operation mode (silent or normal).

        Priority:
        1. JIRA_CHECKER_SILENT environment variable
        2. setup.cfg [flake8] jira_checker_silent setting
        3. Default False (normal mode)
        """
        if cls._silent_mode is not None:
            return cls._silent_mode

        # Check environment variable (highest priority)
        env_silent = os.getenv('JIRA_CHECKER_SILENT', '').lower()
        if env_silent in ('1', 'true', 'yes', 'on'):
            cls._silent_mode = True
            return True
        elif env_silent in ('0', 'false', 'no', 'off'):
            cls._silent_mode = False
            return False

        # Look for setup.cfg in current directory and parents
        current_dir = Path.cwd()
        for parent in [current_dir] + list(current_dir.parents):
            setup_cfg = parent / 'setup.cfg'
            if setup_cfg.exists():
                try:
                    config = configparser.ConfigParser()
                    config.read(setup_cfg)

                    # Check [flake8] section
                    if config.has_section('flake8'):
                        silent_value = config.get('flake8', 'jira_checker_silent', fallback=None)
                        if silent_value is not None:
                            cls._silent_mode = silent_value.lower() in ('1', 'true', 'yes', 'on')
                            return cls._silent_mode

                except (configparser.Error, OSError):
                    # Ignore configuration reading errors
                    pass

                # Found setup.cfg, stop searching
                break

        # Default to normal mode (not silent)
        cls._silent_mode = False
        return False

    @classmethod
    def _get_timeout(cls) -> int:
        """Gets the configured timeout value.

        Priority:
        1. JIRA_TIMEOUT environment variable (in seconds)
        2. setup.cfg [flake8] jira_timeout setting (in seconds)
        3. Default 1 second
        """
        if cls._timeout is not None:
            return cls._timeout

        # Check environment variable (highest priority)
        env_timeout = os.getenv('JIRA_TIMEOUT')
        if env_timeout is not None:
            try:
                timeout_value = int(env_timeout)
                cls._timeout = timeout_value
                return cls._timeout
            except ValueError:
                pass  # Ignore invalid integer value

        # Look for setup.cfg in current directory and parents
        current_dir = Path.cwd()
        for parent in [current_dir] + list(current_dir.parents):
            setup_cfg = parent / 'setup.cfg'
            if setup_cfg.exists():
                try:
                    config = configparser.ConfigParser()
                    config.read(setup_cfg)

                    # Check [flake8] section
                    if config.has_section('flake8'):
                        timeout_value = config.getint('flake8', 'jira_timeout', fallback=None)
                        if timeout_value is not None:
                            cls._timeout = timeout_value
                            return cls._timeout

                except (configparser.Error, OSError):
                    # Ignore configuration reading errors
                    pass

                # Found setup.cfg, stop searching
                break

        # Default to 1 second
        cls._timeout = 1
        return cls._timeout

    @classmethod
    def _setup_jira_client(cls) -> bool:
        """Setup client for working with JIRA API."""
        if cls._jira_client_cache is not None:
            return True

        if cls._connection_checked:
            return not cls._connection_failed

        # Get authentication data from environment variables
        jira_username = os.getenv('JIRA_USERNAME')
        jira_password = os.getenv('JIRA_PASSWORD')
        jira_token = os.getenv('JIRA_TOKEN')

        if not jira_username or (not jira_password and not jira_token):
            # Show warning only if not in silent mode
            if not cls._get_silent_mode():
                cls._show_warning_once(
                    "Warning: JIRA credentials not found in environment variables.\n"
                    "Set JIRA_USERNAME and JIRA_PASSWORD or JIRA_TOKEN to enable JIRA ticket checking."
                )
            cls._connection_checked = True
            cls._connection_failed = True
            return False

        # Get JIRA server URL
        jira_url = cls._get_jira_url()
        if not jira_url:
            if not cls._get_silent_mode():
                cls._show_warning_once(
                    "Warning: JIRA_BASE_URL not configured.\n"
                    "Set JIRA_BASE_URL environment variable or jira_base_url in setup.cfg."
                )
            cls._connection_checked = True
            cls._connection_failed = True
            return False

        # Get timeout value
        timeout = cls._get_timeout()

        try:
            # Setup authentication
            auth_options = {'timeout': timeout}  # Use configured timeout

            if jira_token:
                # Use token-based authentication for API tokens
                cls._jira_client_cache = JIRA(
                    server=jira_url,
                    token_auth=jira_token,
                    options=auth_options
                )
            else:
                # Use basic authentication with password
                cls._jira_client_cache = JIRA(
                    server=jira_url,
                    basic_auth=(jira_username, jira_password),
                    options=auth_options
                )

            # Test connection
            cls._jira_client_cache.myself()
            cls._connection_checked = True
            cls._connection_failed = False
            return True

        except JIRAError as e:
            if not cls._get_silent_mode():
                cls._show_warning_once(f"Warning: JIRA error: {e}")
            cls._connection_checked = True
            cls._connection_failed = True
            return False
        except Exception as e:
            if not cls._get_silent_mode():
                cls._show_warning_once(f"Warning: Could not connect to JIRA: {e}")
            cls._connection_checked = True
            cls._connection_failed = True
            return False

    @classmethod
    def _show_warning_once(cls, message: str) -> None:
        """Shows warning only once."""
        if cls._warning_shown:
            return

        print(message)
        cls._warning_shown = True

    def _get_ticket_status(self, ticket_key: str) -> str:
        """Gets ticket status from JIRA.

        Returns:
            "DONE" - ticket is closed
            "OPEN" - ticket is open
            "NOT_FOUND" - ticket not found
            "CONNECTION_ERROR" - connection error
        """
        if self.__class__._jira_client_cache is None:
            return "CONNECTION_ERROR"

        try:
            # Get ticket information
            issue = self.__class__._jira_client_cache.issue(ticket_key, fields='status')
            status_name = issue.fields.status.name.upper()

            # Check if ticket is closed
            return "DONE" if status_name in ["DONE", "CLOSED", "RESOLVED"] else "OPEN"

        except JIRAError as e:
            if e.status_code == 404:
                return "NOT_FOUND"
            elif e.status_code == 401:
                # Show authentication error warning only if not in silent mode
                if not self.__class__._get_silent_mode():
                    print("Warning: JIRA authentication failed. Check your credentials.")
                return "CONNECTION_ERROR"
            else:
                return "CONNECTION_ERROR"
        except Exception:
            return "CONNECTION_ERROR"
