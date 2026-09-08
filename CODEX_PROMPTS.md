# CODEX_PROMPTS: VSCode Codex 작업 지시문 모음

이 문서는 CLI 기반 AI 뉴스 수집·분석 애플리케이션을 개발할 때 Codex에게 전달할 프롬프트를 모아두는 문서다.

주의:
개발 단계와 작업 범위는 진행 중 변경될 수 있다.
그러나 Codex는 사용자의 명시적 지시 없이 Phase, TASK.md, PRD.md, 구조 설계를 임의로 변경하지 않는다.

작업 중 변경이 필요해 보이면 직접 수정하지 말고,
"변경 제안"으로만 보고한다.

현재 작업은 사용자가 지정한 Phase 또는 CURRENT_TASK.md 범위만 수행한다.
미래 Phase 기능을 미리 구현하지 않는다.
문서와 코드가 충돌하면 임의 판단하지 말고 사용자에게 확인한다.


---

## 1. 공통 개발 원칙

모든 Codex 작업 요청에는 아래 원칙을 적용한다.

```text
너는 Python CLI 애플리케이션 개발을 돕는 시니어 개발자다.

다음 문서를 기준으로 구현하라.

- MISSION.md
- PRD.md
- TASK.md
- CHECKLIST.md

공통 규칙:
1. Python 3.10 이상 기준으로 작성한다.
2. argparse 기반 CLI를 사용한다.
3. 모든 기능을 main.py 하나에 작성하지 말고 app 패키지 내부 모듈로 분리한다.
4. 데이터는 SQLite에 영구 저장한다.
5. API Key는 코드에 직접 작성하지 않는다.
6. config.json과 환경변수를 사용한다.
7. logging 모듈로 INFO/WARNING/ERROR 로그를 남긴다.
8. 오류가 발생해도 가능한 한 프로그램이 비정상 종료되지 않도록 처리한다.
9. 구현 후 실행 방법과 검증 명령어를 함께 알려준다.
10. 기존 코드 구조를 깨지 말고 필요한 부분만 수정한다.
```

---

## 2. Phase 1 기본 구조 생성 프롬프트

```text
MISSION.md, PRD.md, TASK.md를 기준으로 프로젝트 기본 구조를 생성해줘.

요구사항:
- main.py 생성
- app 패키지 생성
- app/__init__.py 생성
- app/cli.py 생성
- app/config.py 생성
- app/logger.py 생성
- app/database.py 생성
- data 디렉터리 생성
- logs 디렉터리 생성
- data/reports 디렉터리 생성
- data/exports 디렉터리 생성
- data/charts 디렉터리 생성

주의사항:
- 아직 실제 기능 구현은 최소화한다.
- 실행 가능한 뼈대만 만든다.
- python main.py --help 명령이 실행될 수 있는 구조로 준비한다.
```

---

## 3. Phase 2 CLI 뼈대 구현 프롬프트

```text
argparse 기반 CLI 뼈대를 구현해줘.

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

각 명령어에는 최소한 help 메시지와 기본 옵션을 추가해줘.

필수 옵션 예시:
- fetch: --method, --source, --limit, --category
- clean: --policy, --limit
- summarize: --all, --id, --unsummarized, --limit
- analyze: --date-from, --date-to, --category, --limit
- report: --format, --top-n
- export: --format, --status, --summarized, --category, --date-from, --date-to

검증 명령어:
python main.py --help
python main.py fetch --help
python main.py clean --help
python main.py summarize --help
python main.py analyze --help
python main.py report --help
python main.py export --help
```

---

## 4. Phase 3 SQLite 데이터베이스 구현 프롬프트

```text
SQLite 데이터베이스 기능을 구현해줘.

요구사항:
- config.json에서 DB 경로를 읽는다.
- DB 파일이 없으면 자동 생성한다.
- 별도의 init-db 명령어는 만들지 않는다.
- 프로그램 실행 시 필요한 테이블이 자동 생성되도록 한다.

필수 테이블:
- raw_news
- clean_news
- summaries
- analyses

필수 구현:
- DB 연결 함수
- 테이블 초기화 함수
- raw 뉴스 저장 함수
- clean 뉴스 저장 함수
- 요약 결과 저장 함수
- 분석 결과 저장 함수
- 뉴스 조회 함수
- URL 중복 방지를 위한 UNIQUE 제약 또는 중복 검사

검증:
python main.py --help 실행 시 data/news.db가 생성되는지 확인한다.
```

---

## 5. Phase 4 뉴스 수집 구현 프롬프트

```text
뉴스 수집 기능을 구현해줘.

수집 방식:
1. RSS 수집
2. BeautifulSoup 기반 크롤링

요구사항:
- feedparser 사용
- requests 사용
- BeautifulSoup 사용
- User-Agent 설정
- timeout 설정
- 요청 delay 적용
- 요청 실패 예외 처리
- HTTP 상태 코드 오류 처리
- 수집 시각 저장
- 소스 정보 저장
- 수집 방법 저장
- raw_news 테이블에 저장

CLI 연결:
- python main.py fetch --method rss --limit 10
- python main.py fetch --method crawl --limit 5

주의:
- 크롤링 대상 사이트에 과도한 요청을 보내지 않는다.
- 네트워크 오류 발생 시 프로그램이 비정상 종료되지 않게 한다.
```

---

## 6. Phase 5 데이터 정제 구현 프롬프트

```text
raw_news 데이터를 정제하여 clean_news에 저장하는 기능을 구현해줘.

정제 규칙:
- 필수 필드 검증
- 제목 정제
- URL 정제
- 본문 또는 설명 텍스트 정제
- HTML 태그 제거
- 불필요한 공백 제거
- 날짜 형식 통일
- 결측값 처리
- 카테고리가 없으면 기타로 처리
- content_length 계산

중복 처리:
- skip
- upsert

CLI 연결:
- python main.py clean --policy skip
- python main.py clean --policy upsert

clean_news.status 기본값은 cleaned로 설정해줘.
```

---

## 7. Phase 6 Gemini 요약 구현 프롬프트

```text
Gemini API를 사용한 뉴스 요약 기능을 구현해줘.

요구사항:
- GEMINI_API_KEY 환경변수에서 API Key를 읽는다.
- API Key를 코드에 직접 작성하지 않는다.
- config.json에서 Gemini 모델명을 읽는다.
- clean_news에서 요약 대상 뉴스를 조회한다.
- 이미 요약된 뉴스는 기본적으로 스킵한다.
- 요약 결과를 summaries 테이블에 저장한다.
- 요약 완료 후 clean_news.status를 summarized로 변경한다.
- API 호출 실패 시 ERROR 로그를 남기고 다음 뉴스로 넘어간다.

CLI 옵션:
- --id
- --all
- --unsummarized
- --limit

요약 프롬프트:
한국어로 3~5문장 요약을 생성한다.

검증:
python main.py summarize --unsummarized --limit 3
python main.py summarize --id 1
```

---

## 8. Phase 7 Gemini 인사이트 분석 구현 프롬프트

```text
Gemini API를 사용한 뉴스 인사이트 분석 기능을 구현해줘.

요구사항:
- 조건에 맞는 clean_news와 summaries 데이터를 조회한다.
- 여러 뉴스의 제목, 본문, 요약을 하나의 분석 입력으로 구성한다.
- 한국어 분석 프롬프트를 작성한다.
- 분석 결과를 analyses 테이블에 저장한다.
- 분석 결과를 콘솔에 출력한다.
- API 호출 실패 시 ERROR 로그를 남긴다.

분석 항목:
- 주요 트렌드
- 핵심 키워드
- 시사점
- 공통점과 차이점

최소 2개 이상의 분석 항목이 포함되어야 한다.

CLI 옵션:
- --date-from
- --date-to
- --category
- --limit

검증:
python main.py analyze --date-from 2025-01-01 --date-to 2025-12-31 --category IT
python main.py analyze --limit 20
```

---

## 9. Phase 8 시각화 구현 프롬프트

```text
matplotlib 기반 시각화 기능을 구현해줘.

필수 차트:
1. 카테고리별 뉴스 수
2. 일자별 수집 추이

요구사항:
- 한글 폰트 설정
- PNG 파일로 저장
- 저장 위치는 data/charts
- report 명령어에서 차트 생성 함수가 호출되도록 연결

검증:
python main.py report --format md
```

---

## 10. Phase 9 리포트 구현 프롬프트

```text
리포트 생성 기능을 구현해줘.

요구사항:
- 콘솔 출력 지원
- 파일 저장 지원
- TXT 형식 지원
- MD 형식 지원
- 저장 위치는 data/reports

포함 내용:
- 총 뉴스 수
- 요약 완료 뉴스 수
- 요약 완료 비율
- 평균 본문 길이
- 카테고리별 TOP N 집계
- 소스별 TOP N 집계
- 최신 AI 분석 결과
- 생성된 차트 경로

CLI 옵션:
- --format txt 또는 md
- --top-n

검증:
python main.py report --format txt --top-n 5
python main.py report --format md --top-n 5
```

---

## 11. Phase 10 데이터 내보내기 구현 프롬프트

```text
데이터 내보내기 기능을 구현해줘.

필수 포맷:
- CSV
- Excel

선택 포맷:
- JSONL

요구사항:
- pandas 사용
- openpyxl 사용
- summaries 테이블과 조인하여 요약 포함
- 결과 파일을 data/exports에 저장
- 파일명에 생성 날짜와 시간 포함

CLI 옵션:
- --format csv
- --format excel
- --format jsonl 선택
- --status
- --summarized
- --category
- --date-from
- --date-to

필수 검증:
python main.py export --format csv --status summarized
python main.py export --format excel --status summarized
python main.py export --format csv --summarized

선택 검증:
python main.py export --format jsonl --status summarized
```

---

## 12. Phase 11 보너스 기능 구현 프롬프트

```text
보너스 기능 중 데이터 조회 CLI를 구현해줘.

구현 대상:
- list 서브커맨드
- show 서브커맨드

list 옵션:
- --category
- --date-from
- --date-to
- --keyword
- --page
- --page-size

show 옵션:
- --id

요구사항:
- list는 뉴스 목록을 페이지네이션하여 출력한다.
- show는 특정 뉴스의 상세 정보와 요약 결과를 함께 출력한다.

검증:
python main.py list --page 1 --page-size 10
python main.py list --category IT --keyword AI --page 1 --page-size 10
python main.py show --id 1
```

---

## 13. Phase 12 설정과 로깅 정리 프롬프트

```text
config.json 설정 관리와 logging 구성을 정리해줘.

config.json 포함 항목:
- API 키 환경변수명
- DB 경로
- RSS URL
- 크롤링 대상 URL
- 중복 처리 정책
- 요청 timeout
- 요청 delay
- Gemini 모델명
- reports 경로
- exports 경로
- charts 경로

logging 요구사항:
- INFO 로그 기록
- WARNING 로그 기록
- ERROR 로그 기록
- logs 디렉터리에 로그 파일 저장
- 주요 작업 시작/종료 로그 기록
- 오류 발생 시 ERROR 로그 기록

주의:
print만 사용하지 말고 logging을 함께 사용한다.
```

---

## 14. Phase 13 README 작성 프롬프트

```text
README.md를 작성해줘.

포함 내용:
- 프로젝트 소개
- 주요 기능
- 폴더 구조
- 설치 방법
- requirements.txt 설치 방법
- config.json 설정 방법
- GEMINI_API_KEY 환경변수 설정 방법
- CLI 명령어 사용 예시
- RSS/API 방식과 크롤링 방식의 장단점 비교
- HTTP 오류 처리 설명
- raw 데이터와 clean 데이터 분리 저장 이유
- AI 요약/분석 흐름 설명
- matplotlib 시각화 설명
- export 사용 방법
- cron 정기 실행 예시
- Windows 작업 스케줄러 정기 실행 예시
- API Key를 GitHub에 올리지 말라는 주의사항
- 크롤링 정책 준수 안내

주의:
감성