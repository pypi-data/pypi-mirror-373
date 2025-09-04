"""
Mixpanel tracking utilities for code-loader.
"""
import os
import getpass
from typing import Optional
import mixpanel


class MixpanelTracker:
    """Handles Mixpanel event tracking for code-loader."""
    
    def __init__(self, token: str = "f1bf46fb339d8c2930cde8c1acf65491"):
        """
        Initialize the Mixpanel tracker.
        
        Args:
            token: Mixpanel project token
        """
        self.token = token
        self.mp = mixpanel.Mixpanel(token)
        self._user_id = None
    
    def _get_user_id(self) -> str:
        """Get the current user ID (whoami)."""
        if self._user_id is None:
            try:
                self._user_id = getpass.getuser()
            except Exception:
                # Fallback to environment variables or default
                self._user_id = os.environ.get('USER', os.environ.get('USERNAME', 'unknown'))
        return self._user_id
    
    def _get_tensorleap_user_id(self) -> Optional[str]:
        """Get the TensorLeap user ID from ~/.tensorleap/user_id if it exists."""
        try:
            user_id_path = os.path.expanduser("~/.tensorleap/user_id")
            if os.path.exists(user_id_path):
                with open(user_id_path, 'r') as f:
                    user_id = f.read().strip()
                    if user_id:
                        return user_id
        except Exception:
            pass
        return None
    
    def _get_distinct_id(self) -> str:
        """Get the distinct ID for Mixpanel tracking.
        
        Priority order:
        1. TensorLeap user ID (from ~/.tensorleap/user_id)
        2. System username (whoami)
        3. 'unknown' as fallback
        """
        tensorleap_user_id = self._get_tensorleap_user_id()
        if tensorleap_user_id:
            return tensorleap_user_id
        
        try:
            return getpass.getuser()
        except Exception:
            # Final fallback
            return os.environ.get('USER', os.environ.get('USERNAME', 'unknown'))
    
    def track_code_loader_loaded(self, event_properties: Optional[dict] = None) -> None:
        """
        Track when code-loader is loaded.
        
        Args:
            event_properties: Additional properties to include with the event
        """
        try:
            distinct_id = self._get_distinct_id()
            
            tensorleap_user_id = self._get_tensorleap_user_id()
            whoami = self._get_user_id()
            
            properties = {
                'whoami': whoami,
                'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
                'platform': os.name,
            }
            
            if tensorleap_user_id:
                properties['user_id'] = tensorleap_user_id
            
            if event_properties:
                properties.update(event_properties)
            
            self.mp.track(distinct_id, 'code_loader_loaded', properties)
        except Exception as e:
            pass


# Global tracker instance
_tracker = None


def get_tracker() -> MixpanelTracker:
    """Get the global Mixpanel tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = MixpanelTracker()
    return _tracker


def track_code_loader_loaded(event_properties: Optional[dict] = None) -> None:
    """
    Convenience function to track code-loader loaded event.
    
    Args:
        event_properties: Additional properties to include with the event
    """
    get_tracker().track_code_loader_loaded(event_properties)
