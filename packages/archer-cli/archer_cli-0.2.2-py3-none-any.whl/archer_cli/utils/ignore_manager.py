"""
Manages file ignore patterns from .gitignore and .archerignore files
"""

import os
import re
from pathlib import Path
from typing import List, Set, Optional
import fnmatch
import logging

class IgnoreManager:
    """Manages ignore patterns from .gitignore and .archerignore files"""
    
    def __init__(self, root_path: Optional[Path] = None):
        """
        Initialize the ignore manager.
        
        Args:
            root_path: Root directory to search for ignore files. Defaults to current working directory.
        """
        self.root_path = Path(root_path) if root_path else Path.cwd()
        self.ignore_patterns: List[str] = []
        self.ignore_dirs: Set[str] = set()
        self.allow_patterns: List[str] = []  # Patterns that start with ! to allow files
        
        # Default ignore patterns (always applied for safety)
        self.default_ignores = [
            '.git/',
            '.env',
            '*.key',
            '*.pem',
            '*.pfx',
            '*.p12',
            'id_rsa*',
            'id_dsa*',
            'id_ecdsa*',
            'id_ed25519*',
            '.ssh/',
            'secrets/',
            'credentials/',
            '.aws/',
            '.gcp/',
            '.azure/',
            'node_modules/',
            '__pycache__/',
            '.venv/',
            'venv/',
            'env/',
            '.devenv/',
        ]
        
        self.load_ignore_files()
    
    def load_ignore_files(self):
        """Load patterns from .gitignore and .archerignore files"""
        # Reset patterns
        self.ignore_patterns = self.default_ignores.copy()
        self.ignore_dirs = set()
        self.allow_patterns = []
        
        # Load .gitignore
        gitignore_path = self.root_path / '.gitignore'
        if gitignore_path.exists():
            self._parse_ignore_file(gitignore_path)
            logging.info(f"Loaded {len(self.ignore_patterns)} patterns from .gitignore")
        
        # Load .archerignore (takes precedence)
        archerignore_path = self.root_path / '.archerignore'
        if archerignore_path.exists():
            self._parse_ignore_file(archerignore_path)
            logging.info(f"Loaded patterns from .archerignore")
    
    def _parse_ignore_file(self, file_path: Path):
        """Parse an ignore file and add patterns to the list"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Handle negation patterns (lines starting with !)
                    if line.startswith('!'):
                        self.allow_patterns.append(line[1:])
                    else:
                        self.ignore_patterns.append(line)
                        
                        # If it's a directory pattern, add to dir set for optimization
                        if line.endswith('/'):
                            self.ignore_dirs.add(line.rstrip('/'))
        except Exception as e:
            logging.warning(f"Failed to parse ignore file {file_path}: {e}")
    
    def should_ignore(self, path: str) -> bool:
        """
        Check if a path should be ignored based on ignore patterns.
        
        Args:
            path: Path to check (relative or absolute)
            
        Returns:
            True if the path should be ignored, False otherwise
        """
        # Convert to Path object and make relative to root
        try:
            path_obj = Path(path)
            if path_obj.is_absolute():
                try:
                    rel_path = path_obj.relative_to(self.root_path)
                except ValueError:
                    # Path is outside root, allow it (but log warning)
                    logging.warning(f"Path {path} is outside project root")
                    return False
            else:
                rel_path = path_obj
            
            # Convert to string with forward slashes for pattern matching
            path_str = str(rel_path).replace('\\', '/')
            
        except Exception as e:
            logging.warning(f"Error processing path {path}: {e}")
            return False
        
        # Check if any parent directory is in ignore_dirs (optimization)
        parts = path_str.split('/')
        for i in range(len(parts)):
            parent = '/'.join(parts[:i+1])
            if parent in self.ignore_dirs:
                # Check if it's explicitly allowed
                if not self._is_allowed(path_str):
                    return True
        
        # Check against ignore patterns
        for pattern in self.ignore_patterns:
            if self._matches_pattern(path_str, pattern):
                # Check if it's explicitly allowed
                if not self._is_allowed(path_str):
                    return True
        
        return False
    
    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """
        Check if a path matches a gitignore-style pattern.
        
        Args:
            path: Path to check
            pattern: Gitignore-style pattern
            
        Returns:
            True if the path matches the pattern
        """
        # Handle directory patterns (ending with /)
        if pattern.endswith('/'):
            pattern = pattern.rstrip('/')
            # Check if path is or is within this directory
            if path == pattern or path.startswith(pattern + '/'):
                return True
        
        # Handle patterns starting with /
        if pattern.startswith('/'):
            # Pattern is relative to root only
            pattern = pattern.lstrip('/')
            if fnmatch.fnmatch(path, pattern):
                return True
        else:
            # Pattern can match at any level
            # Check full path
            if fnmatch.fnmatch(path, pattern):
                return True
            # Check basename
            if fnmatch.fnmatch(os.path.basename(path), pattern):
                return True
            # Check if any parent directory matches
            parts = path.split('/')
            for i in range(len(parts)):
                subpath = '/'.join(parts[i:])
                if fnmatch.fnmatch(subpath, pattern):
                    return True
        
        return False
    
    def _is_allowed(self, path: str) -> bool:
        """
        Check if a path is explicitly allowed by negation patterns.
        
        Args:
            path: Path to check
            
        Returns:
            True if the path is explicitly allowed
        """
        for pattern in self.allow_patterns:
            if self._matches_pattern(path, pattern):
                return True
        return False
    
    def filter_paths(self, paths: List[str]) -> List[str]:
        """
        Filter a list of paths, removing ignored ones.
        
        Args:
            paths: List of paths to filter
            
        Returns:
            Filtered list with ignored paths removed
        """
        return [p for p in paths if not self.should_ignore(p)]
    
    def get_status(self) -> dict:
        """Get status information about loaded ignore patterns"""
        return {
            'root_path': str(self.root_path),
            'total_patterns': len(self.ignore_patterns),
            'allow_patterns': len(self.allow_patterns),
            'ignored_dirs': len(self.ignore_dirs),
            'has_gitignore': (self.root_path / '.gitignore').exists(),
            'has_archerignore': (self.root_path / '.archerignore').exists(),
        }


# Global instance for easy access
_ignore_manager: Optional[IgnoreManager] = None

def get_ignore_manager() -> IgnoreManager:
    """Get or create the global ignore manager instance"""
    global _ignore_manager
    if _ignore_manager is None:
        _ignore_manager = IgnoreManager()
    return _ignore_manager

def should_ignore_path(path: str) -> bool:
    """Convenience function to check if a path should be ignored"""
    return get_ignore_manager().should_ignore(path)