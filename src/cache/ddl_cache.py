import os
import json
from datetime import datetime, timedelta

class DDLCache:
    def __init__(self, cache_dir='cache_data', cache_duration=24):
        self.cache_dir = cache_dir
        self.cache_duration = timedelta(hours=cache_duration)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def _get_cache_file_path(self, database_hash):
        return os.path.join(self.cache_dir, f"{database_hash}_cache.text")

    def _is_cache_valid(self, cache_file):
        if not os.path.exists(cache_file):
            return False
        cache_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        return datetime.now() - cache_time < self.cache_duration

    def get_cached_ddl(self, database_hash):
        cache_file = self._get_cache_file_path(database_hash)
        if self._is_cache_valid(cache_file):
            with open(cache_file, 'r') as file:
                return file.read()
        return None

    def cache_ddl(self, database_hash, ddl_data):
        cache_file = self._get_cache_file_path(database_hash)
        with open(cache_file, 'w') as file:
            file.write(ddl_data)

    def invalidate_cache(self, database_hash):
        cache_file = self._get_cache_file_path(database_hash)
        if os.path.exists(cache_file):
            os.remove(cache_file)
