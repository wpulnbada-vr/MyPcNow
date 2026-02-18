"""Browser history and cache cleaners for Chrome, Edge, Firefox, Brave."""

import os
import shutil
import sqlite3

# Allowlist of safe table names for SQL operations
ALLOWED_TABLES = frozenset({
    "urls", "visits", "keyword_search_terms", "downloads",
    "downloads_url_chains", "segments", "segment_usage",
    "cookies", "moz_historyvisits", "moz_inputhistory", "moz_cookies",
    "moz_places",
})


def _safe_env_path(*env_vars):
    """Get an environment variable value, validated as absolute path."""
    for var in env_vars:
        val = os.environ.get(var, "")
        if val and os.path.isabs(val):
            return val
    return None


class BrowserCleaner:
    """Cleans browser data for major browsers on Windows."""

    def __init__(self, log_callback=None):
        self.log = log_callback or print
        self.local = _safe_env_path("LOCALAPPDATA") or ""
        self.appdata = _safe_env_path("APPDATA") or ""

    def _get_chromium_profiles(self, base_path):
        """Find all Chromium-based browser profile directories."""
        profiles = []
        if not os.path.exists(base_path):
            return profiles
        profiles.append(base_path)
        for item in os.listdir(base_path):
            if item.startswith("Profile "):
                profiles.append(os.path.join(base_path, item))
        default = os.path.join(base_path, "Default")
        if os.path.exists(default) and default not in profiles:
            profiles.append(default)
        return profiles

    def _delete_file_safe(self, filepath):
        """Delete a file, handling permission errors gracefully."""
        try:
            if os.path.isfile(filepath):
                os.remove(filepath)
                return True
            elif os.path.isdir(filepath):
                shutil.rmtree(filepath, onerror=lambda fn, p, ei: self.log(f"  [오류] 삭제 실패: {os.path.basename(p)}"))
                return True
        except PermissionError:
            self.log(f"  [건너뜀] 사용 중: {os.path.basename(filepath)}")
        except Exception as e:
            self.log(f"  [오류] {os.path.basename(filepath)}: {e}")
        return False

    def _delete_dir_contents(self, dirpath):
        """Delete all contents inside a directory without deleting the dir itself."""
        count = 0
        if not os.path.exists(dirpath):
            return count
        for item in os.listdir(dirpath):
            full = os.path.join(dirpath, item)
            if self._delete_file_safe(full):
                count += 1
        return count

    def _clean_sqlite_tables(self, db_path, tables):
        """Clear specified tables in a SQLite database (allowlist-validated)."""
        if not os.path.exists(db_path):
            return False
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            for table in tables:
                if table not in ALLOWED_TABLES:
                    self.log(f"  [건너뜀] 허용되지 않은 테이블: {table}")
                    continue
                try:
                    cursor.execute(f"DELETE FROM {table}")
                except sqlite3.OperationalError:
                    pass
            conn.commit()
            cursor.execute("VACUUM")
            conn.close()
            return True
        except (sqlite3.OperationalError, sqlite3.DatabaseError):
            self.log(f"  [건너뜀] DB 잠김: {os.path.basename(db_path)}")
            return False

    # --- Chrome ---
    def _chrome_base(self):
        return os.path.join(self.local, "Google", "Chrome", "User Data")

    def clean_chrome_history(self):
        self.log("[Chrome] 방문 기록 삭제 중...")
        count = 0
        for profile in self._get_chromium_profiles(self._chrome_base()):
            history_db = os.path.join(profile, "History")
            if self._clean_sqlite_tables(history_db, ["urls", "visits", "keyword_search_terms", "downloads", "downloads_url_chains", "segments", "segment_usage"]):
                count += 1
            for f in ["History-journal", "Visited Links", "Top Sites", "Top Sites-journal"]:
                self._delete_file_safe(os.path.join(profile, f))
        self.log(f"  완료: {count}개 프로필 정리됨")

    def clean_chrome_cache(self):
        self.log("[Chrome] 캐시 삭제 중...")
        count = 0
        for profile in self._get_chromium_profiles(self._chrome_base()):
            for cache_dir in ["Cache", "Code Cache", "GPUCache", "Service Worker"]:
                full = os.path.join(profile, cache_dir)
                count += self._delete_dir_contents(full)
        cache_root = os.path.join(self._chrome_base(), "Default", "Cache", "Cache_Data")
        count += self._delete_dir_contents(cache_root)
        self.log(f"  완료: {count}개 항목 삭제됨")

    def clean_chrome_cookies(self):
        self.log("[Chrome] 쿠키 삭제 중...")
        count = 0
        for profile in self._get_chromium_profiles(self._chrome_base()):
            cookies_db = os.path.join(profile, "Cookies")
            if self._clean_sqlite_tables(cookies_db, ["cookies"]):
                count += 1
            self._delete_file_safe(os.path.join(profile, "Cookies-journal"))
        self.log(f"  완료: {count}개 프로필 쿠키 삭제됨")

    def clean_chrome_downloads(self):
        self.log("[Chrome] 다운로드 기록 삭제 중...")
        count = 0
        for profile in self._get_chromium_profiles(self._chrome_base()):
            history_db = os.path.join(profile, "History")
            if self._clean_sqlite_tables(history_db, ["downloads", "downloads_url_chains"]):
                count += 1
        self.log(f"  완료: {count}개 프로필 다운로드 기록 삭제됨")

    # --- Edge ---
    def _edge_base(self):
        return os.path.join(self.local, "Microsoft", "Edge", "User Data")

    def clean_edge_history(self):
        self.log("[Edge] 방문 기록 삭제 중...")
        count = 0
        for profile in self._get_chromium_profiles(self._edge_base()):
            history_db = os.path.join(profile, "History")
            if self._clean_sqlite_tables(history_db, ["urls", "visits", "keyword_search_terms", "downloads", "downloads_url_chains", "segments", "segment_usage"]):
                count += 1
            for f in ["History-journal", "Visited Links", "Top Sites", "Top Sites-journal"]:
                self._delete_file_safe(os.path.join(profile, f))
        self.log(f"  완료: {count}개 프로필 정리됨")

    def clean_edge_cache(self):
        self.log("[Edge] 캐시 삭제 중...")
        count = 0
        for profile in self._get_chromium_profiles(self._edge_base()):
            for cache_dir in ["Cache", "Code Cache", "GPUCache", "Service Worker"]:
                full = os.path.join(profile, cache_dir)
                count += self._delete_dir_contents(full)
        self.log(f"  완료: {count}개 항목 삭제됨")

    def clean_edge_cookies(self):
        self.log("[Edge] 쿠키 삭제 중...")
        count = 0
        for profile in self._get_chromium_profiles(self._edge_base()):
            cookies_db = os.path.join(profile, "Cookies")
            if self._clean_sqlite_tables(cookies_db, ["cookies"]):
                count += 1
            self._delete_file_safe(os.path.join(profile, "Cookies-journal"))
        self.log(f"  완료: {count}개 프로필 쿠키 삭제됨")

    def clean_edge_downloads(self):
        self.log("[Edge] 다운로드 기록 삭제 중...")
        count = 0
        for profile in self._get_chromium_profiles(self._edge_base()):
            history_db = os.path.join(profile, "History")
            if self._clean_sqlite_tables(history_db, ["downloads", "downloads_url_chains"]):
                count += 1
        self.log(f"  완료: {count}개 프로필 다운로드 기록 삭제됨")

    # --- Firefox ---
    def _firefox_profiles(self):
        """Find all Firefox profile directories."""
        profiles = []
        profiles_dir = os.path.join(self.appdata, "Mozilla", "Firefox", "Profiles")
        if not os.path.exists(profiles_dir):
            return profiles
        for item in os.listdir(profiles_dir):
            full = os.path.join(profiles_dir, item)
            if os.path.isdir(full):
                profiles.append(full)
        return profiles

    def clean_firefox_history(self):
        self.log("[Firefox] 방문 기록 삭제 중...")
        count = 0
        for profile in self._firefox_profiles():
            places_db = os.path.join(profile, "places.sqlite")
            if self._clean_sqlite_tables(places_db, ["moz_historyvisits", "moz_inputhistory"]):
                count += 1
            # Clean non-bookmarked URLs from moz_places
            if os.path.exists(places_db):
                try:
                    conn = sqlite3.connect(places_db)
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM moz_places WHERE foreign_count = 0 AND visit_count = 0")
                    conn.commit()
                    conn.close()
                except (sqlite3.OperationalError, sqlite3.DatabaseError):
                    pass
            self._delete_file_safe(os.path.join(profile, "formhistory.sqlite"))
        self.log(f"  완료: {count}개 프로필 정리됨")

    def clean_firefox_cache(self):
        self.log("[Firefox] 캐시 삭제 중...")
        count = 0
        cache_base = os.path.join(self.local, "Mozilla", "Firefox", "Profiles")
        if os.path.exists(cache_base):
            for item in os.listdir(cache_base):
                cache2 = os.path.join(cache_base, item, "cache2")
                count += self._delete_dir_contents(cache2)
        self.log(f"  완료: {count}개 항목 삭제됨")

    def clean_firefox_cookies(self):
        self.log("[Firefox] 쿠키 삭제 중...")
        count = 0
        for profile in self._firefox_profiles():
            cookies_db = os.path.join(profile, "cookies.sqlite")
            if self._clean_sqlite_tables(cookies_db, ["moz_cookies"]):
                count += 1
        self.log(f"  완료: {count}개 프로필 쿠키 삭제됨")

    # --- Brave ---
    def _brave_base(self):
        return os.path.join(self.local, "BraveSoftware", "Brave-Browser", "User Data")

    def clean_brave_history(self):
        self.log("[Brave] 방문 기록 삭제 중...")
        count = 0
        for profile in self._get_chromium_profiles(self._brave_base()):
            history_db = os.path.join(profile, "History")
            if self._clean_sqlite_tables(history_db, ["urls", "visits", "keyword_search_terms"]):
                count += 1
        self.log(f"  완료: {count}개 프로필 정리됨")

    def clean_brave_cache(self):
        self.log("[Brave] 캐시 삭제 중...")
        count = 0
        for profile in self._get_chromium_profiles(self._brave_base()):
            for cache_dir in ["Cache", "Code Cache", "GPUCache"]:
                full = os.path.join(profile, cache_dir)
                count += self._delete_dir_contents(full)
        self.log(f"  완료: {count}개 항목 삭제됨")

    def clean_brave_cookies(self):
        self.log("[Brave] 쿠키 삭제 중...")
        count = 0
        for profile in self._get_chromium_profiles(self._brave_base()):
            cookies_db = os.path.join(profile, "Cookies")
            if self._clean_sqlite_tables(cookies_db, ["cookies"]):
                count += 1
        self.log(f"  완료: {count}개 프로필 쿠키 삭제됨")

    def run(self, selected_items):
        """Run selected cleanup tasks."""
        method_map = {
            "chrome_history": self.clean_chrome_history,
            "chrome_cache": self.clean_chrome_cache,
            "chrome_cookies": self.clean_chrome_cookies,
            "chrome_downloads": self.clean_chrome_downloads,
            "edge_history": self.clean_edge_history,
            "edge_cache": self.clean_edge_cache,
            "edge_cookies": self.clean_edge_cookies,
            "edge_downloads": self.clean_edge_downloads,
            "firefox_history": self.clean_firefox_history,
            "firefox_cache": self.clean_firefox_cache,
            "firefox_cookies": self.clean_firefox_cookies,
            "brave_history": self.clean_brave_history,
            "brave_cache": self.clean_brave_cache,
            "brave_cookies": self.clean_brave_cookies,
        }
        for item in selected_items:
            if item in method_map:
                method_map[item]()
