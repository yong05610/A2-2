# A2-2

AI뉴스 트랜드 및 종합분석리포트

## 요약 결과 확인 쿼리

```bash
python -c "import sqlite3; conn=sqlite3.connect('data/news.db'); print(conn.execute('select clean_news_id, model, length(summary) from summaries order by id desc limit 5').fetchall())"
```
