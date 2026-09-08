# PRD: CLI 기반 AI 뉴스 수집·분석 애플리케이션

## 1. 프로젝트 개요

이 프로젝트는 CLI 기반 Python 애플리케이션이다.  
뉴스 데이터를 RSS/API와 크롤링 방식으로 수집하고, raw/clean 저장소를 분리하여 관리한다.  
이후 AI API를 활용해 뉴스 요약과 인사이트 분석을 수행하며, matplotlib 시각화와 리포트 생성, 데이터 내보내기 기능을 제공한다.

웹 UI는 구현하지 않는다.

---

## 2. 목표 사용자

- Python 입문/초급 학습자
- AI Native 과정 수강생
- CLI, 데이터 수집, AI API, SQLite, 시각화를 학습하려는 사용자

---

## 3. 핵심 목표

사용자는 이 프로젝트를 통해 다음을 학습한다.

1. API/RSS 방식과 크롤링 방식의 차이
2. HTTP 요청 오류 처리 방법
3. raw 데이터와 clean 데이터 분리 저장의 이유
4. AI API를 이용한 텍스트 요약/분석 흐름
5. SQLite 기반 데이터 저장
6. matplotlib 시각화
7. argparse 기반 CLI 설계
8. CSV/JSONL/Excel 데이터 내보내기

---

## 4. 필수 기능

### 4.1 CLI 설계

argparse를 사용해 서브커맨드 기반 CLI를 구현한다.

필수 서브커맨드:

- fetch
- clean
- summarize
- analyze
- report
- export

보너스 서브커맨드:

- list
- show

---

### 4.2 뉴스 수집

뉴스 수집은 두 가지 방식을 모두 지원한다.

1. RSS 또는 공개 뉴스 API
2. BeautifulSoup 또는 Selenium 기반 크롤링

필수 조건:

- HTTP timeout 설정
- 오류 처리
- 수집 시각 저장
- 소스 정보 저장
- 수집 방법 저장
- raw 저장소에 저장

---

### 4.3 데이터 정제

정제 규칙:

- 필수 필드 검증
- 텍스트 정규화
- 날짜 형식 통일
- 결측값 처리
- 중복 처리 정책 적용

중복 처리 정책:

- skip
- upsert

정제 데이터는 clean 저장소에 별도 저장한다.

---

### 4.4 AI 뉴스 요약

AI API를 호출해 뉴스 본문 요약을 생성한다.

지원 옵션:

- `--all`
- `--id`
- `--unsummarized`
- `--limit`

정책:

- 이미 요약된 뉴스는 기본 스킵
- API 실패 시 로그 기록 후 다음 뉴스 처리
- 요약 결과 저장

---

### 4.5 AI 인사이트 분석

조건별 뉴스를 종합하여 AI 분석을 요청한다.

조건:

- 기간
- 카테고리

분석 항목은 최소 2개 이상 포함한다.

예:

- 주요 트렌드
- 핵심 키워드
- 공통점/차이점
- 시사점

분석 결과는 별도 저장한다.

---

### 4.6 시각화

matplotlib을 사용한다.

필수 차트:

1. 카테고리별 뉴스 수
2. 일자별 수집 추이

조건:

- 한글 폰트 적용
- PNG 파일로 저장

---

### 4.7 리포트 생성

리포트는 콘솔 출력과 파일 저장을 지원한다.

지원 파일 형식:

- TXT
- MD

포함 내용:

- 품질 지표 2개 이상
- TOP N 집계 1개 이상
- AI 인사이트 분석 결과
- 생성된 차트 경로

---

### 4.8 데이터 내보내기

지원 포맷은 최소 2개 이상 구현한다.

필수 후보:

- CSV
- JSONL
- Excel

필터링 옵션:

- `--status {all,cleaned,summarized}`
- 기본값은 `all`
- 요약 완료 뉴스만 내보낼 때는 `--status summarized`를 사용한다.
- 선택적으로 `--summarized`는 `--status summarized`의 별칭으로 지원할 수 있다.

---

### 4.9 설정 및 로깅

설정은 `config.json`에서 관리한다.

포함 설정:

- API 키 환경변수명
- 뉴스 소스 URL
- 중복 정책
- 요청 timeout
- 요청 delay
- DB 경로

로그는 Python `logging` 모듈을 사용한다.

로그 레벨:

- INFO
- WARNING
- ERROR

---

### 4.10 데이터 저장

반드시 영구 저장소를 사용한다.

추천 저장소:

- SQLite

주의:

- 메모리 List/Dict만으로 데이터 관리 금지

---

### 4.11 코드 구조

모든 코드를 단일 파일에 작성하지 않는다.

최소 4개 이상의 모듈로 분리한다.

추천 모듈:

- cli.py
- database.py
- fetcher.py
- crawler.py
- cleaner.py
- summarizer.py
- analyzer.py
- reporter.py
- visualizer.py
- exporter.py

---

## 5. 제외 범위

- 웹 UI 구현
- 대규모 크롤링
- 상용 수준의 배포
- 복잡한 인증 시스템
- 실시간 대시보드

---

## 6. 성공 기준

아래 명령어들이 정상 동작하면 성공으로 본다.

```bash
python main.py fetch --method rss --limit 10


python main.py fetch --method crawl --limit 5
python main.py clean --policy skip
python main.py summarize --unsummarized --limit 3
python main.py analyze --date-from 2025-01-01 --date-to 2025-12-31 --category IT
python main.py report --format md
python main.py export --format csv --status summarized
python main.py export --format excel --status summarized
