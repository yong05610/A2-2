# TASKS: 단계별 개발 작업 목록

이 문서는 CLI 기반 AI 뉴스 수집·분석 애플리케이션을 단계별로 구현하기 위한 작업 목록이다.  
모든 작업은 `MISSION.md`와 `PRD.md`를 기준으로 진행한다.

---

## Phase 0. 프로젝트 준비

- [ ] GitHub 저장소 생성
- [ ] VSCode에서 저장소 열기
- [ ] Python 3.10 이상 확인
- [ ] 가상환경 생성
- [ ] requirements.txt 생성
- [ ] config.json 생성
- [ ] .gitignore 생성
- [ ] MISSION.md 작성
- [ ] PRD.md 작성
- [ ] TASK.md 작성
- [ ] CHECKLIST.md 작성
- [ ] CODEX_PROMPTS.md 생성

확인할 점:

- [ ] 저장소가 정상 생성되었는가?
- [ ] VSCode에서 프로젝트가 열리는가?
- [ ] Python 버전이 3.10 이상인가?
- [ ] 가상환경이 생성되었는가?
- [ ] 기본 문서 파일이 준비되었는가?

---

## Phase 1. 기본 구조 생성

- [ ] main.py 생성
- [ ] app 패키지 생성
- [ ] app/__init__.py 생성
- [ ] app/cli.py 생성
- [ ] app/config.py 생성
- [ ] app/logger.py 생성
- [ ] app/database.py 생성
- [ ] data 디렉터리 생성
- [ ] logs 디렉터리 생성
- [ ] data/reports 디렉터리 생성
- [ ] data/exports 디렉터리 생성
- [ ] data/charts 디렉터리 생성

추천 프로젝트 구조:

```text
news-ai-cli/
├── main.py
├── config.json
├── requirements.txt
├── .gitignore
├── MISSION.md
├── PRD.md
├── TASK.md
├── CHECKLIST.md
├── CODEX_PROMPTS.md
├── README.md
├── app/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── logger.py
│   ├── database.py
│   ├── fetcher.py
│   ├── crawler.py
│   ├── cleaner.py
│   ├── summarizer.py
│   ├── analyzer.py
│   ├── visualizer.py
│   ├── reporter.py
│   └── exporter.py
├── data/
│   ├── news.db
│   ├── reports/
│   ├── exports/
│   └── charts/
└── logs/
```

확인할 점:

- [ ] 모든 코드가 main.py 하나에 몰려 있지 않은가?
- [ ] app 패키지 내부에 기능별 모듈을 둘 준비가 되었는가?
- [ ] data, logs 관련 디렉터리가 준비되었는가?

---

## Phase 2. CLI 뼈대 구현

- [ ] argparse 기반 CLI 구현
- [ ] fetch 서브커맨드 추가
- [ ] clean 서브커맨드 추가
- [ ] summarize 서브커맨드 추가
- [ ] analyze 서브커맨드 추가
- [ ] report 서브커맨드 추가
- [ ] export 서브커맨드 추가
- [ ] 보너스용 list 서브커맨드 추가
- [ ] 보너스용 show 서브커맨드 추가
- [ ] 각 서브커맨드 help 메시지 확인

필수 서브커맨드:

```text
fetch
clean
summarize
analyze
report
export
```

보너스 서브커맨드:

```text
list
show
```

검증 명령어:

```bash
python main.py --help
python main.py fetch --help
python main.py clean --help
python main.py summarize --help
python main.py analyze --help
python main.py report --help
python main.py export --help
python main.py list --help
python main.py show --help
```

확인할 점:

- [ ] `python main.py --help`가 정상 출력되는가?
- [ ] 필수 서브커맨드 6개가 모두 보이는가?
- [ ] 각 서브커맨드별 옵션 설명이 출력되는가?

---

## Phase 3. SQLite 데이터베이스 구현

- [ ] app/database.py에 DB 연결 함수 구현
- [ ] config.json에서 DB 경로 읽기
- [ ] DB 파일이 없으면 자동 생성
- [ ] 기존 데이터는 삭제하지 않고 유지
- [ ] 테이블이 없을 때만 생성하는 init_db 함수 구현
- [ ] CREATE TABLE IF NOT EXISTS 방식 사용
- [ ] 프로그램 실행 시 init_db를 호출하되 기존 데이터는 보존
- [ ] raw_news 테이블 생성
- [ ] clean_news 테이블 생성
- [ ] summaries 테이블 생성
- [ ] analyses 테이블 생성
- [ ] 테이블 초기화 함수 구현
- [ ] raw 뉴스 저장 함수 구현
- [ ] clean 뉴스 저장 함수 구현
- [ ] 요약 결과 저장 함수 구현
- [ ] 분석 결과 저장 함수 구현
- [ ] 뉴스 조회 함수 구현
- [ ] URL 중복 방지를 위한 UNIQUE 제약 또는 중복 검사 구현

중요 정책:

```text
- DB 초기화는 데이터 삭제가 아니다.
- init_db는 DB 파일과 테이블이 없을 때만 생성한다.
- 기존 raw_news, clean_news, summaries, analyses 데이터는 보존한다.
- DROP TABLE, DELETE FROM을 프로그램 시작 시 실행하지 않는다.

필수 테이블:

```text
raw_news
clean_news
summaries
analyses
```

검증 명령어:

```bash
python main.py --help
python -c "from app.database import init_db; init_db(); print('DB ready')"
```

확인할 점:

- [ ] DB 파일이 없을 때 자동 생성되는가?
- [ ] data/news.db 파일이 생성되는가?
- [ ] raw_news 테이블이 생성되는가?
- [ ] clean_news 테이블이 생성되는가?
- [ ] summaries 테이블이 생성되는가?
- [ ] analyses 테이블이 생성되는가?
- [ ] init-db 명령어 없이도 DB가 준비되는가?
- [ ] 프로그램 실행 시 DB와 테이블이 자동 준비되는가?
- [ ] 기존 DB 데이터는 삭제되지 않는가?


---

## Phase 4. 뉴스 수집 기능 구현

- [ ] app/fetcher.py 생성 또는 구현
- [ ] RSS 수집 기능 구현
- [ ] feedparser 사용
- [ ] app/crawler.py 생성 또는 구현
- [ ] requests 사용
- [ ] BeautifulSoup 사용
- [ ] User-Agent 설정
- [ ] timeout 설정
- [ ] 요청 delay 적용
- [ ] 요청 실패 예외 처리
- [ ] HTTP 상태 코드 오류 처리
- [ ] 수집 시각 저장
- [ ] 소스 정보 저장
- [ ] 수집 방법 저장
- [ ] 수집 결과를 raw_news 테이블에 저장
- [ ] fetch --method rss 옵션 연결
- [ ] fetch --method crawl 옵션 연결
- [ ] fetch --limit 옵션 연결
- [ ] fetch --source 옵션 연결
- [ ] fetch --category 옵션 연결
- [ ] logging으로 수집 결과 기록

수집 방식:

```text
1. RSS 또는 공개 뉴스 API
2. BeautifulSoup 기반 크롤링
```

검증 명령어:

```bash
python main.py fetch --method rss --limit 10
python main.py fetch --method crawl --limit 5
```

확인할 점:

- [ ] raw_news 테이블에 데이터가 저장되는가?
- [ ] RSS 방식 수집이 동작하는가?
- [ ] 크롤링 방식 수집이 동작하는가?
- [ ] 수집 시각이 저장되는가?
- [ ] 소스 정보가 저장되는가?
- [ ] 수집 방법이 저장되는가?
- [ ] 네트워크 오류 발생 시 프로그램이 비정상 종료되지 않는가?
- [ ] timeout과 delay 설정이 적용되는가?
- [ ] 크롤링 대상에 과도한 요청을 보내지 않는가?

---

## Phase 5. 데이터 정제 기능 구현

- [ ] app/cleaner.py 생성 또는 구현
- [ ] raw_news에서 정제 대상 데이터 조회
- [ ] 필수 필드 검증
- [ ] 제목 정제
- [ ] URL 정제
- [ ] 본문 또는 설명 텍스트 정제
- [ ] HTML 태그 제거
- [ ] 불필요한 공백 제거
- [ ] 날짜 형식 통일
- [ ] 결측값 처리
- [ ] 카테고리가 없으면 기본값 기타로 처리
- [ ] content_length 계산
- [ ] 중복 URL 검사
- [ ] 중복 처리 정책 skip 구현
- [ ] 중복 처리 정책 upsert 구현
- [ ] 정제 결과를 clean_news 테이블에 저장
- [ ] clean_news.status 기본값을 cleaned로 설정
- [ ] clean --policy 옵션 연결
- [ ] clean --limit 옵션 연결

중복 처리 정책:

```text
skip   : 이미 존재하는 URL이면 저장하지 않음
upsert : 이미 존재하는 URL이면 기존 데이터를 갱신함
```

검증 명령어:

```bash
python main.py clean --policy skip
python main.py clean --policy upsert
```

확인할 점:

- [ ] clean_news 테이블에 데이터가 저장되는가?
- [ ] raw_news와 clean_news가 분리되어 있는가?
- [ ] 필수 필드가 없는 데이터가 적절히 처리되는가?
- [ ] HTML 태그가 제거되는가?
- [ ] 불필요한 공백이 제거되는가?
- [ ] 날짜 형식이 통일되는가?
- [ ] 중복 데이터가 정책에 따라 처리되는가?

---

## Phase 6. Gemini AI 요약 기능 구현

- [ ] app/summarizer.py 생성 또는 구현
- [ ] Gemini API 호출 패키지 사용
- [ ] GEMINI_API_KEY 환경변수에서 API Key 읽기
- [ ] API Key를 코드에 직접 작성하지 않기
- [ ] config.json에서 Gemini 모델명 읽기
- [ ] 요약 대상 뉴스 조회
- [ ] summarize --id 옵션 구현
- [ ] summarize --all 옵션 구현
- [ ] summarize --unsummarized 옵션 구현
- [ ] summarize --limit 옵션 구현
- [ ] 한국어 요약 프롬프트 작성
- [ ] 3~5문장 요약 생성
- [ ] 요약 결과를 summaries 테이블에 저장
- [ ] 요약 완료 후 clean_news.status를 summarized로 변경
- [ ] 이미 요약된 뉴스는 기본 스킵 처리
- [ ] API 호출 실패 시 logging으로 오류 기록 후 다음 뉴스 처리

요약 정책:

```text
- 이미 요약된 뉴스는 기본적으로 다시 요약하지 않는다.
- API 호출 실패 시 전체 프로그램을 중단하지 않는다.
- 실패한 뉴스는 로그를 남기고 다음 뉴스로 넘어간다.
```

검증 명령어:

```bash
python main.py summarize --unsummarized --limit 3
python main.py summarize --id 1
```

확인할 점:

- [ ] summaries 테이블에 요약 결과가 저장되는가?
- [ ] 이미 요약된 뉴스는 중복 요약되지 않는가?
- [ ] 요약 완료 후 clean_news.status가 summarized로 변경되는가?
- [ ] API 실패 시 전체 프로그램이 중단되지 않는가?
- [ ] API Key가 코드나 GitHub에 노출되지 않는가?

---

## Phase 7. Gemini AI 인사이트 분석 기능 구현

- [ ] app/analyzer.py 생성 또는 구현
- [ ] 분석 대상 뉴스 조회
- [ ] analyze --date-from 옵션 구현
- [ ] analyze --date-to 옵션 구현
- [ ] analyze --category 옵션 구현
- [ ] analyze --limit 옵션 구현
- [ ] 여러 뉴스의 제목, 본문, 요약을 분석 입력으로 구성
- [ ] 한국어 분석 프롬프트 작성
- [ ] 주요 트렌드 분석
- [ ] 핵심 키워드 분석
- [ ] 시사점 분석
- [ ] 공통점과 차이점 분석
- [ ] 분석 항목을 최소 2개 이상 포함
- [ ] 분석 결과를 analyses 테이블에 저장
- [ ] 분석 결과를 콘솔에 출력
- [ ] API 호출 실패 시 logging으로 오류 기록

분석 항목 후보:

```text
- 주요 트렌드
- 핵심 키워드
- 주요 이슈
- 공통점/차이점
- 시사점
```

검증 명령어:

```bash
python main.py analyze --date-from 2025-01-01 --date-to 2025-12-31 --category IT
python main.py analyze --limit 20
```

확인할 점:

- [ ] analyses 테이블에 분석 결과가 저장되는가?
- [ ] 분석 결과에 트렌드, 키워드, 시사점 중 2개 이상이 포함되는가?
- [ ] 분석 대상 데이터가 없을 때 안내 메시지가 출력되는가?
- [ ] API 실패 시 오류 로그가 남는가?

---

## Phase 8. 시각화 기능 구현

- [ ] app/visualizer.py 생성 또는 구현
- [ ] matplotlib 사용
- [ ] 한글 폰트 설정
- [ ] 카테고리별 뉴스 수 집계
- [ ] 카테고리별 뉴스 수 차트 생성
- [ ] 날짜별 뉴스 수 집계
- [ ] 날짜별 뉴스 수 차트 생성
- [ ] 차트를 PNG 파일로 저장
- [ ] 차트 저장 위치를 data/charts로 설정
- [ ] report 명령어에서 차트 생성 함수 호출

필수 차트:

```text
1. 카테고리별 뉴스 수
2. 일자별 수집 추이
```

검증 명령어:

```bash
python main.py report --format md
```

확인할 점:

- [ ] data/charts 디렉터리에 PNG 파일이 생성되는가?
- [ ] 카테고리별 차트가 생성되는가?
- [ ] 날짜별 차트가 생성되는가?
- [ ] 차트의 한글이 깨지지 않는가?

---

## Phase 9. 리포트 생성 기능 구현

- [ ] app/reporter.py 생성 또는 구현
- [ ] report --format txt 옵션 구현
- [ ] report --format md 옵션 구현
- [ ] report --top-n 옵션 구현
- [ ] 총 뉴스 수 계산
- [ ] 요약 완료 뉴스 수 계산
- [ ] 요약 완료 비율 계산
- [ ] 평균 본문 길이 계산
- [ ] 카테고리별 TOP N 집계
- [ ] 소스별 TOP N 집계
- [ ] 최신 AI 분석 결과 포함
- [ ] 생성된 차트 경로 포함
- [ ] 리포트를 콘솔에 출력
- [ ] 리포트 파일을 data/reports에 저장

리포트 포함 내용:

```text
- 품질 지표 2개 이상
- TOP N 집계 1개 이상
- AI 인사이트 분석 결과
- 생성된 차트 경로
```

검증 명령어:

```bash
python main.py report --format txt --top-n 5
python main.py report --format md --top-n 5
```

확인할 점:

- [ ] 리포트가 콘솔에 출력되는가?
- [ ] data/reports 디렉터리에 리포트 파일이 저장되는가?
- [ ] 품질 지표가 2개 이상 포함되는가?
- [ ] TOP N 집계가 1개 이상 포함되는가?
- [ ] AI 분석 결과가 포함되는가?
- [ ] 생성된 차트 경로가 포함되는가?

---

## Phase 10. 데이터 내보내기 기능 구현

- [ ] app/exporter.py 생성 또는 구현
- [ ] pandas 사용
- [ ] openpyxl 사용
- [ ] export --format csv 구현
- [ ] export --format excel 구현
- [ ] export --format jsonl 구현
- [ ] export --status 옵션 구현
- [ ] --status 값으로 all, cleaned, summarized 지원
- [ ] --status 기본값을 all로 설정
- [ ] --status summarized 입력 시 요약 완료 뉴스만 내보내기
- [ ] export --category 옵션 구현
- [ ] export --date-from 옵션 구현
- [ ] export --date-to 옵션 구현
- [ ] summaries 테이블과 조인하여 요약 포함
- [ ] 결과 파일을 data/exports에 저장
- [ ] 파일명에 생성 날짜와 시간 포함

필수 지원 포맷:

```text
csv
jsonl
excel
```

선택 지원 포맷:

```text
JSONL
```

필터링 옵션:

```text
--status
--summarized
--category
--date-from
--date-to
```

검증 명령어:

```bash
python main.py export --format csv --status summarized
python main.py export --format jsonl --status summarized
python main.py export --format excel --status summarized
python main.py export --format csv --status all

```

선택 검증 명령어:

```bash
python main.py export --format jsonl --status summarized
```

확인할 점:

- [ ] CSV 파일이 생성되는가?
- [ ] Excel 파일이 생성되는가?
- [ ] 선택 구현 시 JSONL 파일이 생성되는가?
- [ ] 요약 데이터가 포함되는가?
- [ ] `--status` 필터가 정상 동작하는가?
- [ ] `--summarized` 필터가 정상 동작하는가?
- [ ] 결과 파일이 data/exports에 저장되는가?

---

## Phase 11. 보너스 조회 기능 구현

- [ ] list 서브커맨드 구현
- [ ] show 서브커맨드 구현
- [ ] list --category 옵션 구현
- [ ] list --date-from 옵션 구현
- [ ] list --date-to 옵션 구현
- [ ] list --keyword 옵션 구현
- [ ] list --page 옵션 구현
- [ ] list --page-size 옵션 구현
- [ ] show --id 옵션 구현
- [ ] 뉴스 상세 조회 시 요약 결과 함께 출력

보너스 구현 대상:

```text
list
show
```

감성 분석은 이번 구현 범위에서 제외한다.

검증 명령어:

```bash
python main.py list --page 1 --page-size 10
python main.py list --category IT --keyword AI --page 1 --page-size 10
python main.py show --id 1
```

확인할 점:

- [ ] 뉴스 목록이 출력되는가?
- [ ] 페이지네이션이 동작하는가?
- [ ] 카테고리 필터가 동작하는가?
- [ ] 날짜 필터가 동작하는가?
- [ ] 키워드 검색이 동작하는가?
- [ ] 상세 조회 시 요약 결과도 함께 출력되는가?

---

## Phase 12. 설정과 로깅 정리

- [ ] app/config.py에서 config.json 읽기 구현
- [ ] config.json에 API 키 환경변수명 설정
- [ ] config.json에 DB 경로 설정
- [ ] config.json에 RSS URL 설정
- [ ] config.json에 크롤링 대상 URL 설정
- [ ] config.json에 중복 처리 정책 설정
- [ ] config.json에 요청 timeout 설정
- [ ] config.json에 요청 delay 설정
- [ ] config.json에 Gemini 모델명 설정
- [ ] config.json에 reports 경로 설정
- [ ] config.json에 exports 경로 설정
- [ ] config.json에 charts 경로 설정
- [ ] app/logger.py에서 logging 설정
- [ ] INFO 로그 기록
- [ ] WARNING 로그 기록
- [ ] ERROR 로그 기록
- [ ] logs 디렉터리에 로그 파일 저장
- [ ] 주요 작업 시작/종료 로그 기록
- [ ] 오류 발생 시 ERROR 로그 기록
- [ ] print만 사용하지 않고 logging 함께 사용

config.json 필수 항목 예시:

```json
{
  "database": {
    "path": "data/news.db"
  },
  "ai": {
    "provider": "gemini",
    "api_key_env": "GEMINI_API_KEY",
    "model": "gemini-1.5-flash"
  },
  "news_sources": {
    "rss_url": "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko",
    "crawl_url": "https://example.com"
  },
  "fetch": {
    "timeout": 10,
    "delay": 1.0,
    "user_agent": "Mozilla/5.0"
  },
  "clean": {
    "duplicate_policy": "skip"
  },
  "paths": {
    "reports": "data/reports",
    "exports": "data/exports",
    "charts": "data/charts",
    "logs": "logs"
  }
}
```

확인할 점:

- [ ] config.json 값을 바꾸면 프로그램 동작에 반영되는가?
- [ ] API Key가 코드에 직접 작성되어 있지 않은가?
- [ ] logs 디렉터리에 로그 파일이 생성되는가?
- [ ] INFO 로그가 기록되는가?
- [ ] WARNING 로그가 기록되는가?
- [ ] ERROR 로그가 기록되는가?
- [ ] 오류 상황이 로그에 기록되는가?

---

## Phase 13. README 작성

- [ ] 프로젝트 소개 작성
- [ ] 주요 기능 작성
- [ ] 폴더 구조 작성
- [ ] 설치 방법 작성
- [ ] requirements.txt 설치 방법 작성
- [ ] config.json 설정 방법 작성
- [ ] GEMINI_API_KEY 환경변수 설정 방법 작성
- [ ] CLI 명령어 사용 예시 작성
- [ ] RSS/API 방식과 크롤링 방식의 장단점 비교 작성
- [ ] HTTP 오류 처리 설명 작성
- [ ] raw 데이터와 clean 데이터 분리 저장 이유 작성
- [ ] AI 요약/분석 흐름 설명 작성
- [ ] matplotlib 시각화 설명 작성
- [ ] report 사용 방법 작성
- [ ] export 사용 방법 작성
- [ ] cron을 이용한 정기 실행 방법 작성
- [ ] Windows 작업 스케줄러를 이용한 정기 실행 방법 작성
- [ ] API Key를 GitHub에 올리지 말라는 주의사항 작성
- [ ] 크롤링 정책 준수 안내 작성

README에 포함할 정기 실행 예시:

```bash
# 예시: 매일 오전 9시에 RSS 뉴스 수집
0 9 * * * cd /path/to/news-ai-cli && /path/to/venv/bin/python main.py fetch --method rss --limit 20
```

Windows 작업 스케줄러에는 아래 실행 예시를 문서화한다.

```bash
python main.py fetch --method rss --limit 20
```

주의:

```text
감성 분석은 이번 프로젝트 구현 범위에서 제외한다.
```

확인할 점:

- [ ] README만 보고 설치할 수 있는가?
- [ ] README만 보고 실행할 수 있는가?
- [ ] 프로젝트의 핵심 개념이 설명되어 있는가?
- [ ] RSS/API 방식과 크롤링 방식의 차이가 설명되어 있는가?
- [ ] raw/clean 분리 저장 이유가 설명되어 있는가?
- [ ] 보안 주의사항이 포함되어 있는가?
- [ ] 정기 실행 방법이 포함되어 있는가?

---

## Phase 14. 최종 점검

- [ ] CHECKLIST.md 기준으로 전체 요구사항 점검
- [ ] MISSION.md 요구사항 누락 여부 확인
- [ ] PRD.md 기능 요구사항 충족 여부 확인
- [ ] TASK.md 작업 완료 여부 확인
- [ ] CODEX_PROMPTS.md 작성 여부 확인
- [ ] 필수 CLI 명령어 6개 동작 확인
- [ ] 보너스 CLI 명령어 list/show 동작 확인
- [ ] DB 4개 테이블 생성 확인
- [ ] raw 데이터와 clean 데이터 분리 확인
- [ ] RSS 수집 동작 확인
- [ ] 크롤링 수집 동작 확인
- [ ] Gemini 요약 동작 확인
- [ ] Gemini 분석 동작 확인
- [ ] matplotlib 차트 생성 확인
- [ ] report 파일 생성 확인
- [ ] export CSV 파일 생성 확인
- [ ] export Excel 파일 생성 확인
- [ ] README 작성 확인
- [ ] requirements.txt 최신화
- [ ] .gitignore 확인
- [ ] .env 또는 API Key가 GitHub에 올라가지 않았는지 확인
- [ ] 불필요한 테스트 파일 정리
- [ ] 최종 실행 로그 확인

최종 검증 명령어:

```bash
python main.py --help
python main.py fetch --method rss --limit 10
python main.py fetch --method crawl --limit 5
python main.py clean --policy skip
python main.py summarize --unsummarized --limit 3
python main.py analyze --limit 10
python main.py report --format md --top-n 5
python main.py export --format csv --status summarized
python main.py export --format excel --status summarized
python main.py list --page 1 --page-size 10
python main.py show --id 1
```

최종 확인할 점:

- [ ] 프로그램이 처음부터 끝까지 실행 가능한가?
- [ ] 외부 데이터 수집이 가능한가?
- [ ] raw 저장소와 clean 저장소가 분리되어 있는가?
- [ ] AI 요약과 분석이 가능한가?
- [ ] 분석 결과가 저장되고 조회 가능한가?
- [ ] 차트 PNG 파일이 생성되는가?
- [ ] 리포트 파일이 생성되는가?
- [ ] CSV/Excel export가 가능한가?
- [ ] 로그 파일이 생성되는가?
- [ ] README에 실행 방법과 학습 개념이 정리되어 있는가?
- [ ] 제출 전에 API Key가 노출되지 않았는가?