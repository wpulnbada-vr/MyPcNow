"""Desktop shortcut cleaner - moves user-created shortcuts to recovery folder."""

import os
import shutil
import datetime


# System shortcuts that should NEVER be deleted (lowercase)
SYSTEM_SHORTCUTS = {
    "desktop.ini",
    # Windows system
    "this pc.lnk", "이 pc.lnk",
    "recycle bin.lnk", "휴지통.lnk",
    "control panel.lnk", "제어판.lnk",
    "network.lnk", "네트워크.lnk",
    # Microsoft apps
    "microsoft edge.lnk", "microsoft store.lnk",
    "microsoft teams.lnk", "teams.lnk",
    "outlook.lnk", "outlook (new).lnk",
    "onedrive.lnk", "onenote.lnk",
    "word.lnk", "excel.lnk", "powerpoint.lnk",
    "microsoft 365 (office).lnk",
    # Windows features
    "windows security.lnk", "windows 보안.lnk",
    "get started.lnk", "시작.lnk",
    "feedback hub.lnk", "피드백 허브.lnk",
    "xbox.lnk", "xbox game bar.lnk",
    # Common pre-installed
    "adobe acrobat.lnk", "adobe reader.lnk",
}


def _safe_env_path(*env_vars):
    for var in env_vars:
        val = os.environ.get(var, "")
        if val and os.path.isabs(val):
            return val
    return None


class DesktopCleaner:
    """Cleans user-created desktop shortcuts (moves to recovery folder)."""

    def __init__(self, log_callback=None):
        self.log = log_callback or print

    def _is_system_shortcut(self, filename):
        """Check if a shortcut is a system shortcut that should not be deleted."""
        lower = filename.lower()
        if lower in SYSTEM_SHORTCUTS:
            return True
        if not lower.endswith(".lnk") and not lower.endswith(".url"):
            return True
        return False

    def _get_recovery_dir(self):
        """Create and return a timestamped recovery directory."""
        temp = _safe_env_path("TEMP", "TMP")
        if not temp:
            temp = os.path.join(os.path.expanduser("~"), ".MyPcNow_recovery")
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        recovery = os.path.join(temp, "MyPcNow_deleted_shortcuts", ts)
        os.makedirs(recovery, exist_ok=True)
        return recovery

    def clean_user_shortcuts(self):
        """Move user-created shortcuts from desktop to recovery folder."""
        self.log("[바탕화면] 사용자 바로가기 정리 중...")
        userprofile = _safe_env_path("USERPROFILE")
        public = _safe_env_path("PUBLIC") or r"C:\Users\Public"

        desktop_paths = []
        if userprofile:
            desktop_paths.append(os.path.join(userprofile, "Desktop"))
        if public:
            desktop_paths.append(os.path.join(public, "Desktop"))

        if not desktop_paths:
            self.log("  [건너뜀] 바탕화면 경로를 찾을 수 없음")
            return

        recovery_dir = self._get_recovery_dir()
        count = 0
        skipped = 0

        for desktop in desktop_paths:
            if not os.path.exists(desktop) or not os.path.isabs(desktop):
                continue
            for item in os.listdir(desktop):
                full = os.path.join(desktop, item)
                if not os.path.isfile(full):
                    continue
                if self._is_system_shortcut(item):
                    skipped += 1
                    continue
                if item.lower().endswith(".lnk") or item.lower().endswith(".url"):
                    try:
                        shutil.move(full, os.path.join(recovery_dir, item))
                        count += 1
                        self.log(f"  이동: {item}")
                    except PermissionError:
                        self.log(f"  [건너뜀] 권한 부족: {item}")
                    except Exception as e:
                        self.log(f"  [오류] {item}: {e}")

        self.log(f"  완료: {count}개 바로가기 이동됨 (시스템 {skipped}개 보존)")
        if count > 0:
            self.log(f"  [복구] 이동된 바로가기 위치: {recovery_dir}")

    def run(self, selected_items):
        """Run selected cleanup tasks."""
        method_map = {
            "user_shortcuts": self.clean_user_shortcuts,
        }
        for item in selected_items:
            if item in method_map:
                method_map[item]()
