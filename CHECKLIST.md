
---

# 7단계: `CHECKLIST.md` 초안

아래 내용을 `CHECKLIST.md`에 붙여넣으세요.

```markdown
# CHECKLIST: 미션 요구사항 최종 검증표

## 1. CLI 설계

- [ ] argparse를 사용했는가?
- [ ] fetch 서브커맨드가 있는가?
- [ ] clean 서브커맨드가 있는가?
- [ ] summarize 서브커맨드가 있는가?
- [ ] analyze 서브커맨드가 있는가?
- [ ] report 서브커맨드가 있는가?
- [ ] export 서브커맨드가 있는가?
- [ ] 각 서브커맨드에 필요한 옵션이 있는가?

---

## 2. 뉴스 수집

- [ ] RSS 또는 공개 뉴스 API 방식이 구현되었는가?
- [ ] 크롤링 방식이 구현되었는가?
- [ ] BeautifulSoup 또는 Selenium을 사용했는가?
- [ ] HTTP timeout을 설정했는가?
- [ ] HTTP 오류 처리를 구현했는가?
- [ ] 수집 시각을 저장하는가?
- [ ] 소스 정보를 저장하는가?
- [ ] 수집 방법을 저장하는가?
- [ ] raw 저장소에 저장하는가?

---

## 3. 데이터 정제

- [ ] 필수 필드 검증을 하는가?
- [ ] 텍스트 정규화를 하는가?
- [ ] 날짜 형식을 통일하는가?
- [ ] 결측값을 처리하는가?
- [ ] 중복 skip 정책을 지원하는가?
- [ ] 중복 upsert 정책을 지원하는가?
- [ ] clean 저장소에 별도 저장하는가?

---

## 4. AI 요약

- [ ] AI API를 호출하는가?
- [ ] 뉴스 본문을 요약하는가?
- [ ] --all 옵션이 있는가?
- [ ] --id 옵션이 있는가?
- [ ] --unsummarized 옵션이 있는가?
- [ ] 이미 요약된 뉴스는 기본 스킵하는가?
- [ ] API 실패 시 로그 기록 후 스킵하는가?
- [ ] 요약 결과를 저장하는가?

---

## 5. AI 인사이트 분석

- [ ] 기간 조건으로 분석할 수 있는가?
- [ ] 카테고리 조건으로 분석할 수 있는가?
- [ ] 여러 뉴스를 종합 분석하는가?
- [ ] 주요 트렌드가 포함되는가?
- [ ] 핵심 키워드가 포함되는가?
- [ ] 공통점/차이점 또는 시사점이 포함되는가?
- [ ] 분석 결과가 저장되는가?
- [ ] 리포트에서 분석 결과를 활용하는가?

---

## 6. 시각화

- [ ] matplotlib을 사용하는가?
- [ ] 카테고리별 뉴스 수 차트를 생성하는가?
- [ ] 일자별 수집 추이 차트를 생성하는가?
- [ ] 한글 폰트 설정을 적용했는가?
- [ ] PNG 파일로 차트를 저장하는가?

---

## 7. 리포트 생성

- [ ] 콘솔 출력 리포트를 지원하는가?
- [ ] TXT 파일 저장을 지원하는가?
- [ ] MD 파일 저장을 지원하는가?
- [ ] 품질 지표 2개 이상이 포함되는가?
- [ ] TOP N 집계 1개 이상이 포함되는가?
- [ ] AI 인사이트 결과가 포함되는가?
- [ ] 생성된 차트 경로가 포함되는가?

---

## 8. 데이터 내보내기

- [ ] CSV 내보내기를 지원하는가?
- [ ] JSONL 내보내기를 지원하는가?
- [ ] Excel 내보내기를 지원하는가?
- [ ] CSV, JSONL, Excel 중 최소 2개 이상 구현했는가?
- [ ] --status summarized 필터링 옵션을 지원하는가?

---

## 9. 설정 및 로깅

- [ ] config.json으로 설정을 관리하는가?
- [ ] API Key를 코드에 직접 작성하지 않았는가?
- [ ] API Key를 환경변수에서 읽는가?
- [ ] 뉴스 소스 URL을 config.json에서 관리하는가?
- [ ] 중복 정책을 config.json에서 관리하는가?
- [ ] request timeout을 config.json에서 관리하는가?
- [ ] request delay를 config.json에서 관리하는가?
- [ ] logging 모듈을 사용하는가?
- [ ] INFO 로그를 기록하는가?
- [ ] WARNING 로그를 기록하는가?
- [ ] ERROR 로그를 기록하는가?

---

## 10. 데이터 저장

- [ ] SQLite 또는 JSONL 파일을 영구 저장소로 사용하는가?
- [ ] 메모리 List/Dict만으로 데이터를 관리하지 않는가?
- [ ] raw 데이터 저장소가 있는가?
- [ ] clean 데이터 저장소가 있는가?
- [ ] 요약 결과 저장소가 있는가?
- [ ] 분석 결과 저장소가 있는가?

---

## 11. 코드 구조

- [ ] 모든 코드를 단일 파일에 작성하지 않았는가?
- [ ] 최소 4개 이상의 모듈로 분리했는가?
- [ ] main.py가 진입점 역할을 하는가?
- [ ] app/cli.py가 CLI 처리를 담당하는가?
- [ ] app/database.py가 DB 처리를 담당하는가?
- [ ] 수집, 정제, 요약, 분석, 리포트, 내보내기 기능이 적절히 분리되었는가?

---

## 12. 보너스 기능

- [ ] list 서브커맨드를 구현했는가?
- [ ] show 서브커맨드를 구현했는가?
- [ ] 카테고리 필터링을 지원하는가?
- [ ] 날짜 필터링을 지원하는가?
- [ ] 키워드 필터링을 지원하는가?
- [ ] 페이지네이션을 지원하는가?
- [ ] 감성 분석을 구현했는가?
- [ ] 감성 분석 결과를 시각화했는가?
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
python main.py export --format csv --status summarized
python main.py export --format jsonl --status summarized
python main.py export --format excel --status summarized
