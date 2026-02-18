# mypcnow - Windows 11 PC Privacy Cleaner

Windows 11 환경에서 프라이버시 보호를 위한 흔적 삭제 도구입니다.

## 기능

### 브라우저 기록
- Chrome, Edge, Firefox, Brave 방문기록/캐시/쿠키/다운로드 기록

### Windows 검색/활동
- Windows 검색 기록, 활동 타임라인, 최근 파일
- 점프 목록, 실행(Run) 기록, 탐색기 주소 기록

### 시스템 흔적
- 임시 파일, 프리패치, 썸네일 캐시
- 휴지통 비우기, 클립보드 초기화

### 바탕화면
- 사용자가 만든 바로가기만 삭제 (시스템 바로가기 보존)

### 앱 사용 흔적
- 최근 문서 목록 (MRU), 프로그램 사용 통계 (UserAssist)
- 애플리케이션 이벤트 로그

## 안전 보장
- 설치된 프로그램은 절대 삭제하지 않습니다
- 시스템 중요 레지스트리 키는 수정하지 않습니다
- 사용 중인 파일은 건너뜁니다
- PC 운영에 영향을 주지 않습니다

## 빌드 방법

### 요구사항
- Python 3.11+
- Windows 11

### 설치 및 빌드
```batch
pip install -r requirements.txt
python create_icon.py
build.bat
```

### 설치 프로그램 생성
[Inno Setup 6](https://jrsoftware.org/isdl.php) 설치 후 `build.bat` 실행

## 프로젝트 구조
```
mypcnow/
├── src/
│   ├── app.py              # 메인 GUI 애플리케이션
│   └── cleaners/
│       ├── __init__.py      # 클리너 카테고리 정의
│       ├── browser.py       # 브라우저 기록 삭제
│       ├── windows_activity.py  # Windows 활동 삭제
│       ├── system_traces.py # 시스템 흔적 삭제
│       ├── desktop.py       # 바탕화면 정리
│       └── app_traces.py    # 앱 사용 흔적 삭제
├── assets/
│   └── icon.ico            # 앱 아이콘
├── installer/
│   └── setup.iss           # Inno Setup 설치 스크립트
├── requirements.txt
├── build.bat               # 빌드 스크립트
├── mypcnow.spec           # PyInstaller spec
└── version_info.txt       # 버전 정보
```
