"""
Configuration management for IvyBloom CLI
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
import appdirs

class Config:
    """Configuration manager for IvyBloom CLI"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.app_name = "ivybloom"
        self.app_author = "IvyBiosciences"
        
        # Determine config file location
        if config_file:
            self.config_path = Path(config_file)
        else:
            config_dir = Path(appdirs.user_config_dir(self.app_name, self.app_author))
            config_dir.mkdir(parents=True, exist_ok=True)
            self.config_path = config_dir / "config.json"
        # Expose config directory for other utilities that persist files
        self.config_dir = self.config_path.parent
        
        # Default configuration
        self.defaults = {
            # Use frontend domain for API calls to avoid SSL issues and enable Clerk auth
            "api_url": "https://www.ivybiosciences.com/api/v1",
            "frontend_url": "https://www.ivybiosciences.com",
            "timeout": 30,
            "output_format": "json",
            "theme": "light",
            "show_welcome": True,
            "debug": False,
            "retries": 3,
            "tui_refresh_interval_secs": 30,
            # Test gating preview lengths
            "tui_test_preview_max_chars": 4000,
            "cli_test_preview_max_chars": 2000,
            # Visualization preferences
            "visualization": {
                "prefer_flatprot": True,
                "flatprot_output_format": "svg",  # svg | png
                "flatprot_auto_open": False,
                "viewer_command": ""  # optional custom opener
            },
            # Optional structured env overrides stored in config.json
            # Example:
            #   "env": {
            #       "IVY_ORCHESTRATOR_URL": "https://api.example.com/api/v1",
            #       "IVY_FRONTEND_URL": "https://app.example.com",
            #       "ENVIRONMENT": "staging"
            #   }
            "env": {}
        }
        
        # Load existing config; if no file existed, persist defaults to config.json
        existed = self.config_path.exists()
        self.config = self.load()
        if not existed:
            # Write out defaults to config.json for user visibility
            self.save()
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                merged = self.defaults.copy()
                merged.update(config)
                return merged
            except (json.JSONDecodeError, IOError):
                pass
        
        return self.defaults.copy()
    
    def save(self) -> None:
        """Save configuration to file"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.config[key] = value
        self.save()
    
    def reset(self) -> None:
        """Reset configuration to defaults"""
        self.config = self.defaults.copy()
        self.save()
    
    def show_config(self) -> Dict[str, Any]:
        """Return current configuration"""
        return self.config.copy()
    
    def get_auth_token_path(self) -> Path:
        """Get path for storing authentication token"""
        config_dir = Path(appdirs.user_config_dir(self.app_name, self.app_author))
        return config_dir / "auth_token"
    
    def get_api_key_path(self) -> Path:
        """Get path for storing API key"""
        config_dir = Path(appdirs.user_config_dir(self.app_name, self.app_author))
        return config_dir / "api_key"

    # --- API URL resolution helpers ---
    ENVIRONMENT_URLS: Dict[str, str] = {
        "prod": "https://api.ivybiosciences.com/api/v1",
        "staging": "https://staging-api.ivybiosciences.com/api/v1",
        "dev": "https://dev-api.ivybiosciences.com/api/v1",
    }

    def get_api_url(self) -> str:
        """Resolve the effective API base URL with the following precedence (config-driven):
        1) OS env var IVY_ORCHESTRATOR_URL
        2) Legacy OS env var IVYBLOOM_API_URL
        3) config.env["IVY_ORCHESTRATOR_URL"]
        4) config["api_url"]
        5) config.env["ENVIRONMENT"] mapped via ENVIRONMENT_URLS
        6) defaults
        Returns a normalized URL without a trailing slash.
        """
        env_map = self.config.get("env", {}) or {}
        # 1) OS environment override
        api_url_os = os.getenv("IVY_ORCHESTRATOR_URL")
        if api_url_os:
            return self._normalize_base_url(api_url_os)
        # 2) Legacy OS env override
        api_url_legacy = os.getenv("IVYBLOOM_API_URL")
        if api_url_legacy:
            return self._normalize_base_url(api_url_legacy)
        # 3) Config-driven env map
        api_url_env = env_map.get("IVY_ORCHESTRATOR_URL")
        if api_url_env:
            return self._normalize_base_url(api_url_env)
        # 4) Config value
        configured = self.config.get("api_url")
        if configured:
            return self._normalize_base_url(configured)
        # 5) Environment selection from config (ENVIRONMENT)
        env_name = (env_map.get("ENVIRONMENT") or "").lower()
        if env_name:
            mapped = self.ENVIRONMENT_URLS.get(env_name)
            if mapped:
                return self._normalize_base_url(mapped)
        # 6) Default
        return self._normalize_base_url(self.defaults["api_url"])

    @staticmethod
    def _normalize_base_url(url: str) -> str:
        # Strip trailing slashes to simplify joining
        return url.rstrip("/")

    # --- Frontend URL helpers ---
    def get_frontend_url(self) -> str:
        """Resolve the frontend URL (Clerk-powered app) using config only.
        Precedence: config.env["IVY_FRONTEND_URL"] > config["frontend_url"] > default.
        """
        env_map = self.config.get("env", {}) or {}
        # 1) OS environment override
        fe_os = os.getenv("IVY_FRONTEND_URL")
        if fe_os:
            return fe_os.rstrip("/")
        # 2) Config-driven env map
        fe_env = env_map.get("IVY_FRONTEND_URL")
        if fe_env:
            return fe_env.rstrip("/")
        # 3) Config value
        fe_cfg = self.get("frontend_url", self.defaults["frontend_url"])
        return fe_cfg.rstrip("/")

    # --- Client ID helpers ---
    def get_client_id_path(self) -> Path:
        """Path to persist a machine-unique CLI client UUID (legacy fallback file)."""
        config_dir = Path(appdirs.user_config_dir(self.app_name, self.app_author))
        return config_dir / "client_id"

    def get_or_create_client_id(self) -> str:
        """Return a stable per-installation client UUID, creating and persisting it in config.json if missing.
        Also supports legacy file location for backward compatibility.
        """
        # 1) OS env override for client ID
        client_env = os.getenv("IVY_CLIENT_ID")
        if client_env:
            return client_env
        # 2) Prefer the value stored in config.json
        stored = self.config.get("client_id")
        if stored:
            return stored

        # 2) Fallback to legacy file if present
        try:
            path = self.get_client_id_path()
            if path.exists():
                with open(path, "r") as f:
                    data = json.load(f)
                    cid = data.get("client_id")
                    if cid:
                        # migrate into config.json
                        self.set("client_id", cid)
                        return cid
        except Exception:
            pass

        # 3) Generate and persist
        import uuid
        client_id = str(uuid.uuid4())
        try:
            self.set("client_id", client_id)
        except Exception:
            # Last resort: do not fail using the new ID
            return client_id
        return client_id