"""
Smart Caching System
==================

Memory-efficient caching system for compute-intensive operations.
Automatically manages cache size and improves performance on low-end systems.
"""

import numpy as np
import json
import hashlib
from pathlib import Path
import pickle
from typing import Any, Dict, Optional
import time

class SmartCache:
    """
    Smart caching system for compute-intensive operations.
    
    Handles automatic cache invalidation and size management
    to optimize memory usage while maximizing performance gains.
    """
    def __init__(self, cache_dir: str = ".astrolib_cache", max_size_mb: int = 500):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_size_mb = max_size_mb
        self.cache_index: Dict[str, Dict] = self._load_index()
        
    def _load_index(self) -> Dict:
        index_path = self.cache_dir / "index.json"
        if index_path.exists():
            with open(index_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_index(self):
        with open(self.cache_dir / "index.json", 'w') as f:
            json.dump(self.cache_index, f)
    
    def _get_hash(self, data: Any) -> str:
        """Generiert einen Hash für die Eingabedaten."""
        return hashlib.md5(pickle.dumps(data)).hexdigest()
    
    def get(self, key: str, data: Any) -> Optional[Any]:
        """Holt Ergebnisse aus dem Cache oder berechnet sie neu."""
        data_hash = self._get_hash(data)
        cache_key = f"{key}_{data_hash}"
        
        if cache_key in self.cache_index:
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            if cache_file.exists():
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
        return None
    
    def set(self, key: str, data: Any, result: Any):
        """Speichert Ergebnisse im Cache."""
        data_hash = self._get_hash(data)
        cache_key = f"{key}_{data_hash}"
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        # Prüfe und verwalte Cache-Größe
        self._manage_cache_size()
        
        with open(cache_file, 'wb') as f:
            pickle.dump(result, f)
        
        self.cache_index[cache_key] = {
            'timestamp': time.time(),
            'size': cache_file.stat().st_size
        }
        self._save_index()
    
    def _manage_cache_size(self):
        """Verwaltet die Cache-Größe durch Entfernen alter Einträge."""
        total_size = sum(entry['size'] for entry in self.cache_index.values())
        
        if total_size > self.max_size_mb * 1024 * 1024:
            # Sortiere nach Zeitstempel und entferne alte Einträge
            sorted_entries = sorted(
                self.cache_index.items(),
                key=lambda x: x[1]['timestamp']
            )
            
            while total_size > self.max_size_mb * 1024 * 1024 and sorted_entries:
                key, entry = sorted_entries.pop(0)
                cache_file = self.cache_dir / f"{key}.pkl"
                if cache_file.exists():
                    cache_file.unlink()
                total_size -= entry['size']
                del self.cache_index[key]
            
            self._save_index()
