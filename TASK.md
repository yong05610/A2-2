# TASKS: 단계별 개발 작업 목록

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
- [ ] CHECKLIST.md 작성

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
- [ ] reports, exports, charts 디렉터리 생성

---

## Phase 2. CLI 뼈대 구현

- [ ] argparse 기반 CLI 구현
- [ ] fetch 서브커맨드 추가
- [ ] clean 서브커맨드 추가
- [ ] summarize 서브커맨드 추가
- [ ] analyze 서브커맨드 추가
- [ ] report 서브커맨드 추가
- [ ] export 서브커맨드 추가
- [ ] 각 서브커맨드 help 메시지 확인

검증 명령어:

```bash
python main.py --help
python main.py fetch --help
python main.py clean --help
python main.py summarize --help
python main.py analyze --help
python main.py report --help
python main.py export --help
