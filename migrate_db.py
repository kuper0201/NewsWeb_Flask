# 외부 DB 파일을 내부 SQLite 파일로 변환하는 유틸

# To do
# 크롤링과 연계하여 실시간으로 데이터 DB에 저장해야함
# (해당 코드는 크롤링과 별개로 수동 마이그레이션 방식임)

from app import app, db

from app.models import News
from datetime import datetime
import sqlite3

# 마이그레이션 할 원본 DB 파일 경로와 쿼리문 지정
EXTERNAL_DB_PATH = '03_03/World.db'
query = "SELECT id, category, url, title, press, author, date_time, image_url, original_text, summary, original_caption, generated_caption FROM World_articles"

def fetch_external_data():
    """외부 데이터베이스에서 데이터를 가져와 내부 DB에 저장"""
    connection = sqlite3.connect(EXTERNAL_DB_PATH)
    cursor = connection.cursor()

    cursor.execute(query)
    rows = cursor.fetchall()

    for row in rows:
        # date_time이 문자열일 경우 datetime 객체로 변환
        if isinstance(row[6], str):
            try:
                # 날짜 형식이 'Wed, February 26, 2025 at 9:48 PM UTC'와 같은 형식이라고 가정
                date_time = datetime.strptime(row[6].strip(), "%a, %B %d, %Y at %I:%M %p %Z")
            except ValueError as e:
                print(f"Error parsing date for news {row[0]}: {e}")
                date_time = None  # 날짜 형식이 잘못된 경우 None 처리
        else:
            date_time = row[6]

        news = News(
            id=row[0],
            category=row[1],
            url=row[2],
            title=row[3],
            press=row[4],
            author=row[5],
            date_time=date_time,  # 변환된 datetime 값 사용
            image_url=row[7],
            original_text=row[8],
            summary=row[9],
            original_caption=row[10],
            generated_caption=row[11]
        )
        db.session.merge(news)  # 동일 ID 존재 시 업데이트, 없으면 추가

    db.session.commit()
    connection.close()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        fetch_external_data()
    print('DB migrate success!')