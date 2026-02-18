"""MyPcNow cleaners - Windows 11 Privacy Cleanup Modules"""

from .browser import BrowserCleaner
from .windows_activity import WindowsActivityCleaner
from .system_traces import SystemTracesCleaner
from .desktop import DesktopCleaner
from .app_traces import AppTracesCleaner

CLEANER_CATEGORIES = {
    "browser": {
        "name": "브라우저 기록",
        "icon": "🌐",
        "cleaner": BrowserCleaner,
        "items": {
            "chrome_history": "Chrome 방문 기록",
            "chrome_cache": "Chrome 캐시",
            "chrome_cookies": "Chrome 쿠키",
            "chrome_downloads": "Chrome 다운로드 기록",
            "edge_history": "Edge 방문 기록",
            "edge_cache": "Edge 캐시",
            "edge_cookies": "Edge 쿠키",
            "edge_downloads": "Edge 다운로드 기록",
            "firefox_history": "Firefox 방문 기록",
            "firefox_cache": "Firefox 캐시",
            "firefox_cookies": "Firefox 쿠키",
            "brave_history": "Brave 방문 기록",
            "brave_cache": "Brave 캐시",
            "brave_cookies": "Brave 쿠키",
        },
    },
    "windows_activity": {
        "name": "Windows 검색/활동",
        "icon": "🔍",
        "cleaner": WindowsActivityCleaner,
        "items": {
            "search_history": "Windows 검색 기록",
            "activity_timeline": "활동 타임라인",
            "recent_files": "최근 사용한 파일",
            "jump_lists": "작업 표시줄 점프 목록",
            "run_history": "실행(Run) 대화상자 기록",
            "explorer_history": "탐색기 주소 기록",
        },
    },
    "system_traces": {
        "name": "시스템 흔적",
        "icon": "🗑️",
        "cleaner": SystemTracesCleaner,
        "items": {
            "temp_files": "임시 파일 (%TEMP%)",
            "windows_temp": "Windows 임시 파일",
            "prefetch": "프리패치 파일 (재부팅 시 일시 느림)",
            "thumbnail_cache": "썸네일 캐시",
            "recycle_bin": "휴지통 비우기",
            "clipboard": "클립보드 내용",
        },
    },
    "desktop": {
        "name": "바탕화면",
        "icon": "🖥️",
        "cleaner": DesktopCleaner,
        "items": {
            "user_shortcuts": "사용자가 만든 바로가기 (복구 가능)",
        },
    },
    "app_traces": {
        "name": "앱 사용 흔적",
        "icon": "📱",
        "cleaner": AppTracesCleaner,
        "items": {
            "recent_docs": "최근 문서 (MRU 목록)",
            "userassist": "프로그램 사용 통계 (UserAssist)",
            "app_event_logs": "애플리케이션 이벤트 로그 (복구 불가)",
        },
    },
}
