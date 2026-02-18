<p align="center">
  <img src="assets/icon.ico" width="80" alt="MyPcNow logo"/>
</p>

<h1 align="center">MyPcNow</h1>

<p align="center">
  <strong>클릭 한 번으로 PC 흔적을 깨끗하게.</strong><br/>
  Windows 11 전용 프라이버시 클리너
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-Windows%2011-0078D6?logo=windows11" alt="Windows 11"/>
  <img src="https://img.shields.io/badge/python-3.11+-3776AB?logo=python&logoColor=white" alt="Python 3.11+"/>
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License"/>
  <img src="https://img.shields.io/badge/version-1.0.0-blue" alt="v1.0.0"/>
</p>

---

## 왜 MyPcNow인가?

누군가 내 PC를 잠깐 쓸 때, 검색 기록이나 최근 파일 목록이 신경 쓰인 적 있나요?

**MyPcNow**는 브라우저 기록, 검색 흔적, 최근 파일, 바탕화면 바로가기까지 — 선택한 항목만 골라서 한 번에 정리합니다. 설치된 프로그램은 절대 건드리지 않습니다.

## 주요 기능

| 카테고리 | 정리 항목 | 개수 |
|---------|----------|:----:|
| **브라우저** | Chrome · Edge · Firefox · Brave 방문기록, 캐시, 쿠키, 다운로드 기록 | 14 |
| **Windows 활동** | 검색 기록, 활동 타임라인, 최근 파일, 점프 목록, 실행 기록, 탐색기 주소 | 6 |
| **시스템** | 임시 파일, 프리패치, 썸네일 캐시, 휴지통, 클립보드 | 6 |
| **바탕화면** | 사용자 바로가기 정리 (시스템 바로가기 보존, 복구 가능) | 1 |
| **앱 흔적** | 최근 문서 MRU, 프로그램 사용 통계, 이벤트 로그 | 3 |

> 총 **30개 항목**을 카테고리별 체크박스로 선택하거나, **전체 선택** 한 번이면 끝.

## 안전 설계

- **프로그램 삭제 금지** — 설치된 앱은 절대 건드리지 않습니다
- **시스템 레지스트리 보호** — HKEY_CURRENT_USER만 접근, 시스템 키 수정 없음
- **복구 가능한 삭제** — 바탕화면 바로가기는 임시 폴더로 이동 (영구 삭제 아님)
- **사용 중 파일 건너뜀** — PermissionError 자동 처리
- **SQL Injection 방지** — 테이블명 allowlist 검증
- **관리자 권한 사전 체크** — 권한 필요 작업은 미리 확인 후 안내

## 빠른 시작

### 설치 프로그램 사용 (권장)
[Releases](https://github.com/wpulnbada-vr/MyPcNow/releases)에서 `MyPcNow_setup.exe`를 다운로드하고 실행하세요.

### 직접 빌드
```batch
git clone https://github.com/wpulnbada-vr/MyPcNow.git
cd MyPcNow
pip install -r requirements.txt
python create_icon.py
build.bat
```

빌드 결과물:
- `dist\MyPcNow.exe` — 단일 실행 파일
- `dist\installer\MyPcNow_setup_v1.0.0.exe` — 설치 프로그램 ([Inno Setup 6](https://jrsoftware.org/isdl.php) 필요)

### 요구사항
- Windows 11
- Python 3.11+ (빌드 시)

## 기술 스택

- **GUI**: [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (다크 모드 모던 UI)
- **패키징**: [PyInstaller](https://pyinstaller.org/) (단일 .exe)
- **설치**: [Inno Setup](https://jrsoftware.org/) (전문 설치 프로그램)
- **보안**: SQL allowlist, 환경변수 경로 검증, 관리자 권한 체크

## 프로젝트 구조

```
MyPcNow/
├── src/
│   ├── app.py                      # GUI 애플리케이션
│   └── cleaners/                   # 정리 모듈
│       ├── browser.py              # 4개 브라우저 지원
│       ├── windows_activity.py     # Windows 검색/활동
│       ├── system_traces.py        # 시스템 흔적
│       ├── desktop.py              # 바탕화면 (복구 가능)
│       └── app_traces.py           # 앱 사용 흔적
├── installer/setup.iss             # Inno Setup 스크립트
├── build.bat                       # 원클릭 빌드
└── requirements.txt
```

## Contributing

이슈와 PR을 환영합니다. 새로운 클리너 모듈을 추가하려면 `src/cleaners/` 디렉토리에 클래스를 만들고 `__init__.py`에 등록하세요.

## License

[MIT](LICENSE)

---

<p align="center">
  <sub>MyPcNow — 내 PC는 지금부터 깨끗하게</sub>
</p>
