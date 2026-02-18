"""System traces cleaners: temp files, prefetch, thumbnails, recycle bin, clipboard."""

import os
import shutil
import ctypes


def _safe_env_path(*env_vars):
    for var in env_vars:
        val = os.environ.get(var, "")
        if val and os.path.isabs(val):
            return val
    return None


def _is_admin():
    """Check if the current process has admin privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


class SystemTracesCleaner:
    """Cleans system-level traces on Windows."""

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
                    shutil.rmtree(full, onerror=lambda fn, p, ei: None)
                    count += 1
            except PermissionError:
                pass
            except Exception:
                pass
        return count

    def clean_temp_files(self):
        """Clear user temp directory (%TEMP%)."""
        self.log("[시스템] 사용자 임시 파일 삭제 중...")
        temp_dir = _safe_env_path("TEMP", "TMP")
        if not temp_dir:
            self.log("  [건너뜀] TEMP 환경변수 없음")
            return
        count = self._delete_dir_contents(temp_dir)
        self.log(f"  완료: {count}개 임시 파일 삭제됨")

    def clean_windows_temp(self):
        """Clear Windows temp directory."""
        self.log("[시스템] Windows 임시 파일 삭제 중...")
        sysroot = _safe_env_path("SYSTEMROOT") or r"C:\Windows"
        win_temp = os.path.join(sysroot, "Temp")
        count = self._delete_dir_contents(win_temp)
        self.log(f"  완료: {count}개 Windows 임시 파일 삭제됨")

    def clean_prefetch(self):
        """Clear Prefetch files (requires admin)."""
        self.log("[시스템] 프리패치 파일 삭제 중...")
        self.log("  [주의] 프리패치 삭제 후 다음 재부팅 및 앱 실행이 일시적으로 느릴 수 있습니다")
        if not _is_admin():
            self.log("  [건너뜀] 관리자 권한이 필요합니다")
            return
        sysroot = _safe_env_path("SYSTEMROOT") or r"C:\Windows"
        prefetch_dir = os.path.join(sysroot, "Prefetch")
        count = self._delete_dir_contents(prefetch_dir)
        self.log(f"  완료: {count}개 프리패치 파일 삭제됨")

    def clean_thumbnail_cache(self):
        """Clear Windows thumbnail cache."""
        self.log("[시스템] 썸네일 캐시 삭제 중...")
        localappdata = _safe_env_path("LOCALAPPDATA")
        if not localappdata:
            self.log("  [건너뜀] LOCALAPPDATA 환경변수 없음")
            return
        thumb_dir = os.path.join(localappdata, "Microsoft", "Windows", "Explorer")
        count = 0
        if os.path.exists(thumb_dir):
            for item in os.listdir(thumb_dir):
                if item.startswith("thumbcache_") or item.startswith("iconcache_"):
                    full = os.path.join(thumb_dir, item)
                    try:
                        os.remove(full)
                        count += 1
                    except PermissionError:
                        pass
        self.log(f"  완료: {count}개 썸네일 캐시 삭제됨")

    def clean_recycle_bin(self):
        """Empty the Recycle Bin."""
        self.log("[시스템] 휴지통 비우는 중...")
        try:
            ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x0007)
            self.log("  완료: 휴지통 비워짐")
        except Exception as e:
            self.log(f"  [오류] 휴지통: {e}")

    def clean_clipboard(self):
        """Clear clipboard contents."""
        self.log("[시스템] 클립보드 내용 삭제 중...")
        try:
            ctypes.windll.user32.OpenClipboard(0)
            ctypes.windll.user32.EmptyClipboard()
            ctypes.windll.user32.CloseClipboard()
            self.log("  완료: 클립보드 비워짐")
        except Exception as e:
            self.log(f"  [오류] 클립보드: {e}")

    def run(self, selected_items):
        """Run selected cleanup tasks."""
        method_map = {
            "temp_files": self.clean_temp_files,
            "windows_temp": self.clean_windows_temp,
            "prefetch": self.clean_prefetch,
            "thumbnail_cache": self.clean_thumbnail_cache,
            "recycle_bin": self.clean_recycle_bin,
            "clipboard": self.clean_clipboard,
        }
        for item in selected_items:
            if item in method_map:
                method_map[item]()
