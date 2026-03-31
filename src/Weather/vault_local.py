"""
Simple local Vault implementation for development
Stores secrets in a JSON file instead of using Docker
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class LocalVault:
    """Lightweight Vault alternative for local development"""
    
    def __init__(self, vault_file: str = '.vault_secrets.json'):
        self.vault_file = Path(vault_file)
        self.secrets: Dict[str, Any] = {}
        self._load_secrets()
    
    def _load_secrets(self):
        """Load secrets from JSON file"""
        if self.vault_file.exists():
            try:
                with open(self.vault_file, 'r') as f:
                    self.secrets = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load vault file ({e}), starting with empty vault")
                self.secrets = {}
        else:
            self.secrets = {}
    
    def _save_secrets(self):
        """Save secrets to JSON file"""
        with open(self.vault_file, 'w') as f:
            json.dump(self.secrets, f, indent=2)
        # Set restrictive permissions on Windows
        os.chmod(self.vault_file, 0o600)
    
    def set_secret(self, path: str, key: str, value: str):
        """Store a secret"""
        if path not in self.secrets:
            self.secrets[path] = {}
        self.secrets[path][key] = value
        self._save_secrets()
        print(f"✅ Secret stored at {path}/{key}")
    
    def get_secret(self, path: str, key: str) -> Optional[str]:
        """Retrieve a secret"""
        if path in self.secrets and key in self.secrets[path]:
            return self.secrets[path][key]
        return None
    
    def read_secret_version(self, path: str) -> Dict[str, Any]:
        """Mimics Vault API for compatibility"""
        # Removes 'data/' prefix if present for internal use
        clean_path = path.replace('data/', '')
        
        if clean_path not in self.secrets:
            raise Exception(f"Secret not found at path: {clean_path}")
        
        return {
            'data': {
                'data': self.secrets[clean_path]
            }
        }
    
    def list_secrets(self, path: str) -> list:
        """List all secrets under a path"""
        prefix = path.rstrip('/')
        matching = [key for key in self.secrets.keys() if key.startswith(prefix)]
        return matching
    
    def delete_secret(self, path: str):
        """Delete a secret"""
        if path in self.secrets:
            del self.secrets[path]
            self._save_secrets()
            print(f"✅ Secret deleted at {path}")
    
    def is_available(self) -> bool:
        """Check if vault is available"""
        return True

# Global vault instance
_vault_instance = None

def get_vault() -> LocalVault:
    """Get the global vault instance"""
    global _vault_instance
    if _vault_instance is None:
        _vault_instance = LocalVault()
    return _vault_instance
