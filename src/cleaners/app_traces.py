"""Application usage traces cleaner - MRU lists, UserAssist, Event Logs."""

import os
import subprocess


class AppTracesCleaner:
    """Cleans application usage traces from Windows."""

    def __init__(self, log_callback=None):
        self.log = log_callback or print

    def _delete_registry_key_values(self, hive, key_path):
        """Delete all values under a registry key."""
        try:
            import winreg
            with winreg.OpenKey(hive, key_path, 0, winreg.KEY_ALL_ACCESS) as key:
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
            return False

    def _delete_registry_subkeys_recursive(self, hive, key_path):
        """Recursively delete all subkeys under a registry key."""
        try:
            import winreg
            with winreg.OpenKey(hive, key_path, 0, winreg.KEY_ALL_ACCESS) as key:
                subkeys = []
                i = 0
                while True:
                    try:
                        subkeys.append(winreg.EnumKey(key, i))
                        i += 1
                    except OSError:
                        break

            count = 0
            for sk in subkeys:
                child_path = f"{key_path}\\{sk}"
                # Recurse into child first
                count += self._delete_registry_subkeys_recursive(hive, child_path)
                # Now delete child values and the key itself
                self._delete_registry_key_values(hive, child_path)
                try:
                    with winreg.OpenKey(hive, key_path, 0, winreg.KEY_ALL_ACCESS) as parent:
                        winreg.DeleteKey(parent, sk)
                        count += 1
                except OSError:
                    pass

            return count
        except (FileNotFoundError, PermissionError, ImportError):
            return 0

    def clean_recent_docs(self):
        """Clear Recent Documents MRU lists from registry."""
        self.log("[앱 흔적] 최근 문서 목록 삭제 중...")
        try:
            import winreg
            mru_keys = [
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs",
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\OpenSavePidlMRU",
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\LastVisitedPidlMRU",
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\LastVisitedPidlMRULegacy",
            ]
            count = 0
            for key_path in mru_keys:
                if self._delete_registry_key_values(winreg.HKEY_CURRENT_USER, key_path):
                    count += 1
                count += self._delete_registry_subkeys_recursive(winreg.HKEY_CURRENT_USER, key_path)

            self.log(f"  완료: {count}개 MRU 항목 정리됨")
        except Exception as e:
            self.log(f"  [오류] 최근 문서: {e}")

    def clean_userassist(self):
        """Clear UserAssist data (program usage statistics)."""
        self.log("[앱 흔적] UserAssist (프로그램 사용 통계) 삭제 중...")
        try:
            import winreg
            userassist_base = r"Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist"
            count = 0
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, userassist_base) as base_key:
                i = 0
                guids = []
                while True:
                    try:
                        guids.append(winreg.EnumKey(base_key, i))
                        i += 1
                    except OSError:
                        break

                for guid in guids:
                    count_key = f"{userassist_base}\\{guid}\\Count"
                    if self._delete_registry_key_values(winreg.HKEY_CURRENT_USER, count_key):
                        count += 1

            self.log(f"  완료: {count}개 UserAssist GUID 정리됨")
        except FileNotFoundError:
            self.log("  완료: UserAssist 데이터 없음")
        except Exception as e:
            self.log(f"  [오류] UserAssist: {e}")

    def clean_app_event_logs(self):
        """Clear Application event logs."""
        self.log("[앱 흔적] 애플리케이션 이벤트 로그 삭제 중...")
        self.log("  [주의] 이 작업은 시스템 문제 진단에 필요한 기록을 삭제합니다 (복구 불가)")
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                self.log("  [건너뜀] 관리자 권한이 필요합니다")
                return
        except Exception:
            pass

        try:
            result = subprocess.run(
                ["wevtutil", "cl", "Application"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                self.log("  완료: 애플리케이션 이벤트 로그 삭제됨")
            else:
                self.log("  [참고] 이벤트 로그 삭제 실패")
        except FileNotFoundError:
            self.log("  [건너뜀] wevtutil 명령을 찾을 수 없음")
        except subprocess.TimeoutExpired:
            self.log("  [오류] 시간 초과")
        except Exception as e:
            self.log(f"  [오류] 이벤트 로그: {e}")

    def run(self, selected_items):
        """Run selected cleanup tasks."""
        method_map = {
            "recent_docs": self.clean_recent_docs,
            "userassist": self.clean_userassist,
            "app_event_logs": self.clean_app_event_logs,
        }
        for item in selected_items:
            if item in method_map:
                method_map[item]()
