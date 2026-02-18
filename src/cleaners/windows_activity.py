"""Windows search history, activity timeline, recent files, jump lists cleaners."""

import os
import shutil


def _safe_env_path(*env_vars):
    for var in env_vars:
        val = os.environ.get(var, "")
        if val and os.path.isabs(val):
            return val
    return None


class WindowsActivityCleaner:
    """Cleans Windows activity traces."""

    def __init__(self, log_callback=None):
        self.log = log_callback or print

    def _delete_dir_contents(self, dirpath):
        count = 0
        if not dirpath or not os.path.isabs(dirpath) or not os.path.exists(dirpath):
            return count
        for item in os.listdir(dirpath):
            full = os.path.join(dirpath, item)
            try:
                if os.path.isfile(full):
                    os.remove(full)
                    count += 1
                elif os.path.isdir(full):
                    shutil.rmtree(full, onerror=lambda fn, p, ei: self.log(f"  [오류] 삭제 실패: {os.path.basename(p)}"))
                    count += 1
            except PermissionError:
                self.log(f"  [건너뜀] 사용 중: {os.path.basename(full)}")
            except Exception as e:
                self.log(f"  [오류] {os.path.basename(full)}: {e}")
        return count

    def _delete_registry_values_by_name(self, hive, key_path, value_names=None):
        """Delete specific values (or all if value_names is None) under a registry key."""
        try:
            import winreg
            with winreg.OpenKey(hive, key_path, 0, winreg.KEY_ALL_ACCESS) as key:
                if value_names:
                    count = 0
                    for name in value_names:
                        try:
                            winreg.DeleteValue(key, name)
                            count += 1
                        except FileNotFoundError:
                            pass
                    return count > 0
                else:
                    while True:
                        try:
                            name, _, _ = winreg.EnumValue(key, 0)
                            winreg.DeleteValue(key, name)
                        except OSError:
                            break
            return True
        except FileNotFoundError:
            return False
        except PermissionError:
            self.log(f"  [건너뜀] 권한 부족: {key_path}")
            return False
        except ImportError:
            self.log("  [건너뜀] winreg 모듈 없음 (Windows 전용)")
            return False

    def clean_search_history(self):
        """Clear Windows Search history (history values only, not settings)."""
        self.log("[Windows] 검색 기록 삭제 중...")
        try:
            import winreg
            # Only delete search history-related values, not configuration settings
            self._delete_registry_values_by_name(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Search\Flighting",
            )

            # Clear search cache data
            localappdata = _safe_env_path("LOCALAPPDATA")
            if localappdata:
                search_data = os.path.join(
                    localappdata,
                    "Packages", "Microsoft.Windows.Search_cw5n1h2txyewy",
                    "LocalState", "DeviceSearchCache"
                )
                if os.path.exists(search_data):
                    self._delete_dir_contents(search_data)

            self.log("  완료: 검색 기록 정리됨")
        except Exception as e:
            self.log(f"  [오류] 검색 기록: {e}")

    def clean_activity_timeline(self):
        """Clear Windows Activity Timeline / Activity History."""
        self.log("[Windows] 활동 타임라인 삭제 중...")
        try:
            localappdata = _safe_env_path("LOCALAPPDATA")
            if not localappdata:
                self.log("  [건너뜀] LOCALAPPDATA 환경변수 없음")
                return
            activity_dir = os.path.join(localappdata, "ConnectedDevicesPlatform")
            count = 0
            if os.path.exists(activity_dir):
                for item in os.listdir(activity_dir):
                    full = os.path.join(activity_dir, item)
                    if os.path.isdir(full):
                        for f in os.listdir(full):
                            if f.startswith("ActivitiesCache") and (
                                f.endswith(".db") or f.endswith(".db-wal") or f.endswith(".db-shm")
                            ):
                                try:
                                    os.remove(os.path.join(full, f))
                                    count += 1
                                except PermissionError:
                                    pass

            self.log(f"  완료: {count}개 항목 삭제됨")
        except Exception as e:
            self.log(f"  [오류] 활동 타임라인: {e}")

    def clean_recent_files(self):
        """Clear Recent files list."""
        self.log("[Windows] 최근 파일 목록 삭제 중...")
        appdata = _safe_env_path("APPDATA")
        if not appdata:
            self.log("  [건너뜀] APPDATA 환경변수 없음")
            return
        recent_dir = os.path.join(appdata, "Microsoft", "Windows", "Recent")
        count = 0
        if os.path.exists(recent_dir):
            for item in os.listdir(recent_dir):
                if item.lower() in ("automaticdestinations", "customdestinations"):
                    continue  # handled separately in clean_jump_lists
                full = os.path.join(recent_dir, item)
                try:
                    if os.path.isfile(full):
                        os.remove(full)
                        count += 1
                    elif os.path.isdir(full):
                        shutil.rmtree(full, onerror=lambda fn, p, ei: None)
                        count += 1
                except PermissionError:
                    pass
        self.log(f"  완료: {count}개 최근 파일 항목 삭제됨")

    def clean_jump_lists(self):
        """Clear Jump Lists (taskbar recent/frequent)."""
        self.log("[Windows] 점프 목록 삭제 중...")
        appdata = _safe_env_path("APPDATA")
        if not appdata:
            self.log("  [건너뜀] APPDATA 환경변수 없음")
            return
        count = 0
        jump_dirs = [
            os.path.join(appdata, "Microsoft", "Windows", "Recent", "AutomaticDestinations"),
            os.path.join(appdata, "Microsoft", "Windows", "Recent", "CustomDestinations"),
        ]
        for jd in jump_dirs:
            count += self._delete_dir_contents(jd)
        self.log(f"  완료: {count}개 점프 목록 삭제됨")

    def clean_run_history(self):
        """Clear Run dialog history from registry."""
        self.log("[Windows] 실행(Run) 기록 삭제 중...")
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU"
            if self._delete_registry_values_by_name(winreg.HKEY_CURRENT_USER, key_path):
                self.log("  완료: 실행 기록 삭제됨")
            else:
                self.log("  완료: 삭제할 기록 없음")
        except Exception as e:
            self.log(f"  [오류] 실행 기록: {e}")

    def clean_explorer_history(self):
        """Clear Explorer address bar history from registry."""
        self.log("[Windows] 탐색기 주소 기록 삭제 중...")
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\TypedPaths"
            if self._delete_registry_values_by_name(winreg.HKEY_CURRENT_USER, key_path):
                self.log("  완료: 탐색기 주소 기록 삭제됨")
            else:
                self.log("  완료: 삭제할 기록 없음")
        except Exception as e:
            self.log(f"  [오류] 탐색기 주소 기록: {e}")

    def run(self, selected_items):
        """Run selected cleanup tasks."""
        method_map = {
            "search_history": self.clean_search_history,
            "activity_timeline": self.clean_activity_timeline,
            "recent_files": self.clean_recent_files,
            "jump_lists": self.clean_jump_lists,
            "run_history": self.clean_run_history,
            "explorer_history": self.clean_explorer_history,
        }
        for item in selected_items:
            if item in method_map:
                method_map[item]()
