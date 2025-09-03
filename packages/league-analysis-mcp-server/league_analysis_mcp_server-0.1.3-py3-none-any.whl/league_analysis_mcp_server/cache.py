"""
Caching Layer for League Analysis MCP Server
"""

import json
import time
import hashlib
import logging
from typing import Any, Optional, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class SimpleCache:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self, default_ttl: int = 300):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from prefix and parameters."""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        if entry['ttl'] > 0 and time.time() > entry['expires']:
            del self._cache[key]
            return None
        
        logger.debug(f"Cache hit: {key}")
        return entry['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL."""
        if ttl is None:
            ttl = self.default_ttl
        
        expires = time.time() + ttl if ttl > 0 else 0
        self._cache[key] = {
            'value': value,
            'ttl': ttl,
            'expires': expires,
            'created': time.time()
        }
        logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
    
    def delete(self, key: str) -> None:
        """Remove key from cache."""
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Cache delete: {key}")
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        logger.debug("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        current_time = time.time()
        active_entries = 0
        expired_entries = 0
        permanent_entries = 0
        
        for entry in self._cache.values():
            if entry['ttl'] == -1:  # Permanent
                permanent_entries += 1
            elif entry['ttl'] > 0 and current_time <= entry['expires']:
                active_entries += 1
            else:
                expired_entries += 1
        
        return {
            'total_entries': len(self._cache),
            'active_entries': active_entries,
            'expired_entries': expired_entries,
            'permanent_entries': permanent_entries
        }


class CacheManager:
    """Manages different cache strategies for different data types."""
    
    def __init__(self, historical_ttl: int = -1, current_ttl: int = 300):
        self.cache = SimpleCache()
        self.historical_ttl = historical_ttl  # -1 means permanent
        self.current_ttl = current_ttl
    
    def get_historical_data(self, sport: str, season: str, league_id: str, 
                          endpoint: str, **params) -> Optional[Any]:
        """Get cached historical data."""
        key = self._get_historical_key(sport, season, league_id, endpoint, **params)
        return self.cache.get(key)
    
    def set_historical_data(self, sport: str, season: str, league_id: str, 
                          endpoint: str, data: Any, **params) -> None:
        """Cache historical data (permanent by default)."""
        key = self._get_historical_key(sport, season, league_id, endpoint, **params)
        self.cache.set(key, data, self.historical_ttl)
    
    def get_current_data(self, sport: str, league_id: str, 
                        endpoint: str, **params) -> Optional[Any]:
        """Get cached current season data."""
        key = self._get_current_key(sport, league_id, endpoint, **params)
        return self.cache.get(key)
    
    def set_current_data(self, sport: str, league_id: str, 
                        endpoint: str, data: Any, **params) -> None:
        """Cache current season data with TTL."""
        key = self._get_current_key(sport, league_id, endpoint, **params)
        self.cache.set(key, data, self.current_ttl)
    
    def _get_historical_key(self, sport: str, season: str, league_id: str, 
                          endpoint: str, **params) -> str:
        """Generate cache key for historical data."""
        return self.cache._generate_key(
            f"hist_{sport}_{season}_{league_id}_{endpoint}", **params
        )
    
    def _get_current_key(self, sport: str, league_id: str, 
                        endpoint: str, **params) -> str:
        """Generate cache key for current data."""
        return self.cache._generate_key(
            f"curr_{sport}_{league_id}_{endpoint}", **params
        )
    
    def invalidate_current_season(self, sport: str, league_id: str) -> None:
        """Invalidate all current season cache entries for a league."""
        keys_to_delete = []
        prefix = f"curr_{sport}_{league_id}_"
        
        for key in self.cache._cache.keys():
            if key.startswith(prefix):
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            self.cache.delete(key)
        
        logger.info(f"Invalidated {len(keys_to_delete)} current season cache entries")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        return self.cache.get_stats()


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager