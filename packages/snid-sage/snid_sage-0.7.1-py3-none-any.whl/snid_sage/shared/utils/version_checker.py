"""
SNID SAGE Version Checker
========================

Module for checking if newer versions of SNID SAGE are available on PyPI.
Provides utilities for version comparison and update notifications.
"""

import requests
import threading
import time
from typing import Optional, Tuple, Dict, Any
from packaging import version

try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('version_checker')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('version_checker')


class VersionChecker:
    """Handles version checking against PyPI"""
    
    def __init__(self, package_name: str = "snid-sage", timeout: float = 5.0):
        """
        Initialize version checker
        
        Args:
            package_name: Name of the package on PyPI
            timeout: Timeout for PyPI requests in seconds
        """
        self.package_name = package_name
        self.timeout = timeout
        self.pypi_url = f"https://pypi.org/pypi/{package_name}/json"
        
        # Cache for version info
        self._latest_version = None
        self._last_check_time = 0
        self._cache_duration = 3600  # Cache for 1 hour
    
    def get_current_version(self) -> str:
        """Get the currently installed version"""
        try:
            from snid_sage import __version__
            return __version__
        except ImportError:
            return "unknown"
    
    def get_latest_version_from_pypi(self) -> Optional[str]:
        """
        Query PyPI for the latest version
        
        Returns:
            Latest version string if successful, None if failed
        """
        try:
            _LOGGER.debug(f"Querying PyPI for latest version of {self.package_name}")
            response = requests.get(self.pypi_url, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            latest_version = data['info']['version']
            
            _LOGGER.debug(f"Latest version on PyPI: {latest_version}")
            return latest_version
            
        except requests.exceptions.RequestException as e:
            _LOGGER.debug(f"Network error checking PyPI: {e}")
            return None
        except (KeyError, ValueError) as e:
            _LOGGER.debug(f"Error parsing PyPI response: {e}")
            return None
        except Exception as e:
            _LOGGER.debug(f"Unexpected error checking PyPI: {e}")
            return None
    
    def get_latest_version_cached(self) -> Optional[str]:
        """
        Get latest version with caching to avoid repeated API calls
        
        Returns:
            Latest version string if available, None if not cached or failed
        """
        current_time = time.time()
        
        # Return cached version if still valid
        if (self._latest_version and 
            current_time - self._last_check_time < self._cache_duration):
            return self._latest_version
        
        # Query PyPI for fresh data
        latest = self.get_latest_version_from_pypi()
        if latest:
            self._latest_version = latest
            self._last_check_time = current_time
        
        return self._latest_version
    
    def compare_versions(self, current: str, latest: str) -> int:
        """
        Compare two version strings
        
        Args:
            current: Current version string
            latest: Latest version string
            
        Returns:
            -1 if current < latest (update available)
             0 if current == latest (up to date)
             1 if current > latest (development version)
        """
        try:
            if current == "unknown":
                return -1  # Assume update needed if version unknown
            
            # Clean version strings (remove 'v' prefix if present)
            current_clean = current.lstrip('v')
            latest_clean = latest.lstrip('v')
            
            current_ver = version.parse(current_clean)
            latest_ver = version.parse(latest_clean)
            
            if current_ver < latest_ver:
                return -1
            elif current_ver > latest_ver:
                return 1
            else:
                return 0
                
        except Exception as e:
            _LOGGER.debug(f"Error comparing versions {current} vs {latest}: {e}")
            return 0  # Assume up to date if comparison fails
    
    def check_for_updates(self) -> Dict[str, Any]:
        """
        Check for updates and return comprehensive info
        
        Returns:
            Dictionary with update information:
            {
                'current_version': str,
                'latest_version': str or None,
                'update_available': bool,
                'comparison': int,
                'error': str or None
            }
        """
        current = self.get_current_version()
        
        try:
            latest = self.get_latest_version_cached()
            
            if latest is None:
                return {
                    'current_version': current,
                    'latest_version': None,
                    'update_available': False,
                    'comparison': 0,
                    'error': 'Could not connect to PyPI'
                }
            
            comparison = self.compare_versions(current, latest)
            update_available = comparison < 0
            
            return {
                'current_version': current,
                'latest_version': latest,
                'update_available': update_available,
                'comparison': comparison,
                'error': None
            }
            
        except Exception as e:
            _LOGGER.debug(f"Error in check_for_updates: {e}")
            return {
                'current_version': current,
                'latest_version': None,
                'update_available': False,
                'comparison': 0,
                'error': str(e)
            }
    
    def check_for_updates_async(self, callback: callable, *args, **kwargs):
        """
        Check for updates asynchronously and call callback with results
        
        Args:
            callback: Function to call with results
            *args, **kwargs: Additional arguments for callback
        """
        def worker():
            try:
                result = self.check_for_updates()
                callback(result, *args, **kwargs)
            except Exception as e:
                _LOGGER.debug(f"Error in async version check: {e}")
                # Call callback with error result
                error_result = {
                    'current_version': self.get_current_version(),
                    'latest_version': None,
                    'update_available': False,
                    'comparison': 0,
                    'error': str(e)
                }
                callback(error_result, *args, **kwargs)
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()


def format_update_message(version_info: Dict[str, Any]) -> str:
    """
    Format a user-friendly update message
    
    Args:
        version_info: Version information from check_for_updates()
        
    Returns:
        Formatted message string
    """
    if version_info.get('error'):
        return f"Could not check for updates: {version_info['error']}"
    
    current = version_info['current_version']
    latest = version_info.get('latest_version')
    
    if not latest:
        return "Could not determine latest version"
    
    if version_info['update_available']:
        return (f"🔄 Update Available!\n\n"
                f"Current version: {current}\n"
                f"Latest version: {latest}\n\n"
                f"Update with: pip install --upgrade snid-sage")
    elif version_info['comparison'] > 0:
        return (f"🚀 Development Version\n\n"
                f"Current version: {current}\n"
                f"Latest stable: {latest}\n\n"
                f"You're running a development version!")
    else:
        return (f"✅ Up to Date\n\n"
                f"Current version: {current}\n"
                f"You have the latest version!")


# Convenience function for quick checks
def quick_update_check() -> Optional[Dict[str, Any]]:
    """
    Perform a quick update check with default settings
    
    Returns:
        Version information or None if check fails
    """
    checker = VersionChecker()
    return checker.check_for_updates()


# Example usage and testing
if __name__ == "__main__":
    print("SNID SAGE Version Checker Test")
    print("=" * 40)
    
    checker = VersionChecker()
    
    # Test current version
    current = checker.get_current_version()
    print(f"Current version: {current}")
    
    # Test PyPI query
    print("Checking PyPI...")
    latest = checker.get_latest_version_from_pypi()
    print(f"Latest on PyPI: {latest}")
    
    # Test full check
    print("\nFull update check:")
    result = checker.check_for_updates()
    print(format_update_message(result)) 