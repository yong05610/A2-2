# CHECKLIST: 미션 요구사항 최종 검증표

## 1. CLI 설계

- [X] argparse를 사용했는가?
- [X] fetch 서브커맨드가 있는가?
- [X] clean 서브커맨드가 있는가?
- [X] summarize 서브커맨드가 있는가?
- [X] analyze 서브커맨드가 있는가?
- [X] report 서브커맨드가 있는가?
- [X] export 서브커맨드가 있는가?
- [X] 각 서브커맨드에 필요한 옵션이 있는가?

---

## 2. 뉴스 수집

- [X] RSS 또는 공개 뉴스 API 방식이 구현되었는가?
- [X] 크롤링 방식이 구현되었는가?
- [X] BeautifulSoup 또는 Selenium을 사용했는가?
- [X] HTTP timeout을 설정했는가?
- [X] HTTP 오류 처리를 구현했는가?
- [X] 수집 시각을 저장하는가?
- [X] 소스 정보를 저장하는가?
- [X] 수집 방법을 저장하는가?
- [X] raw 저장소에 저장하는가?

---

## 3. 데이터 정제

- [X] 필수 필드 검증을 하는가?
- [X] 텍스트 정규화를 하는가?
- [X] 날짜 형식을 통일하는가?
- [X] 결측값을 처리하는가?
- [X] 중복 skip 정책을 지원하는가?
- [X] 중복 upsert 정책을 지원하는가?
- [X] clean 저장소에 별도 저장하는가?

---

## 4. AI 요약

- [X] AI API를 호출하는가?
- [X] 뉴스 본문을 요약하는가?
- [X] --all 옵션이 있는가?
- [X] --id 옵션이 있는가?
- [X] --unsummarized 옵션이 있는가?
- [X] 이미 요약된 뉴스는 기본 스킵하는가?
- [X] API 실패 시 로그 기록 후 스킵하는가?
- [X] 요약 결과를 저장하는가?

---

## 5. AI 인사이트 분석

- [X] 기간 조건으로 분석할 수 있는가?
- [X] 카테고리 조건으로 분석할 수 있는가?
- [X] 여러 뉴스를 종합 분석하는가?
- [X] 주요 트렌드가 포함되는가?
- [X] 핵심 키워드가 포함되는가?
- [X] 공통점/차이점 또는 시사점이 포함되는가?
- [X] 분석 결과가 저장되는가?
- [X] 리포트에서 분석 결과를 활용하는가?

---

## 6. 시각화

- [X] matplotlib을 사용하는가?
- [X] 카테고리별 뉴스 수 차트를 생성하는가?
- [X] 일자별 수집 추이 차트를 생성하는가?
- [X] 한글 폰트 설정을 적용했는가?
- [X] PNG 파일로 차트를 저장하는가?

---

## 7. 리포트 생성

- [X] 콘솔 출력 리포트를 지원하는가?
- [X] TXT 파일 저장을 지원하는가?
- [X] MD 파일 저장을 지원하는가?
- [X] 품질 지표 2개 이상이 포함되는가?
- [X] TOP N 집계 1개 이상이 포함되는가?
- [X] AI 인사이트 결과가 포함되는가?
- [X] 생성된 차트 경로가 포함되는가?

---

## 8. 데이터 내보내기

- [X] CSV 내보내기를 지원하는가?
- [X] JSON 내보내기를 지원하는가?
- [X] clean_news, summaries, analyses 대상 선택을 지원하는가?
- [X] CSV와 JSON 2개 형식을 구현했는가?
- [X] --status summarized 필터링 옵션을 지원하는가?

---

## 9. 설정 및 로깅

- [X] config.json으로 설정을 관리하는가?
- [X] API Key를 코드에 직접 작성하지 않았는가?
- [X] API Key를 환경변수에서 읽는가?
- [X] 뉴스 소스 URL을 config.json에서 관리하는가?
- [X] 중복 정책을 config.json에서 관리하는가?
- [X] request timeout을 config.json에서 관리하는가?
- [X] request delay를 config.json에서 관리하는가?
- [X] logging 모듈을 사용하는가?
- [X] INFO 로그를 기록하는가?
- [X] WARNING 로그를 기록하는가?
- [X] ERROR 로그를 기록하는가?

---

## 10. 데이터 저장

- [X] SQLite 또는 JSONL 파일을 영구 저장소로 사용하는가?
- [X] 메모리 List/Dict만으로 데이터를 관리하지 않는가?
- [X] raw 데이터 저장소가 있는가?
- [X] clean 데이터 저장소가 있는가?
- [X] 요약 결과 저장소가 있는가?
- [X] 분석 결과 저장소가 있는가?

---

## 11. 코드 구조

- [X] 모든 코드를 단일 파일에 작성하지 않았는가?
- [X] 최소 4개 이상의 모듈로 분리했는가?
- [X] main.py가 진입점 역할을 하는가?
- [X] app/cli.py가 CLI 처리를 담당하는가?
- [X] app/database.py가 DB 처리를 담당하는가?
- [X] 수집, 정제, 요약, 분석, 리포트, 내보내기 기능이 적절히 분리되었는가?

---

## 12. 보너스 기능

- [ ] list 서브커맨드를 구현했는가?
- [ ] show 서브커맨드를 구현했는가?
- [ ] 카테고리 필터링을 지원하는가?
- [ ] 날짜 필터링을 지원하는가?
- [ ] 키워드 필터링을 지원하는가?
- [ ] 페이지네이션을 지원하는가?
- [ ] README.md에 cron 또는 작업 스케줄러 안내를 작성했는가?

---

## 13. 최종 실행 검증

아래 명령어가 정상 실행되는지 확인한다.

```bash
python main.py --help
python main.py fetch --method rss --limit 10
python main.py fetch --method crawl --limit 5
python main.py clean --policy skip
python main.py clean --policy upsert
python main.py summarize --unsummarized --limit 3
python main.py summarize --id 1
python main.py analyze --date-from 2025-01-01 --date-to 2025-12-31 --category IT
python main.py report --format md
python main.py report --format txt
python main.py export --table clean_news --format csv
python main.py export --table summaries --format json
python main.py export --table analyses --format json
