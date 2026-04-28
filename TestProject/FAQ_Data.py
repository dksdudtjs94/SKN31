import csv
import os
import pandas as pd
import pymysql
from dotenv import load_dotenv


"""
DB 연결
- MySQL 데이터베이스에 CSV 데이터를 삽입
- DB에서 데이터를 조회하여 DataFrame으로 반환
"""

CSV_FILE1 = "data/kia_faq.csv"      # category, question, answer, site
CSV_FILE2 = "data/hyundai_faq.csv"  # category, question, answer, site

# 데이터베이스 설정 (MYSQL)
load_dotenv()
db_config = {
    'user': os.getenv("DB_USER"),           # MySQL 사용자 이름
    'password': os.getenv("DB_PASSWORD"),   # MySQL 비밀번호
    'host': os.getenv("DB_HOST"),           # MySQL 호스트
    'database': os.getenv("DB_NAME")        # 사용할 데이터베이스 이름
}


# FAQ 데이터 삽입
def insert_faq_data_to_db():

    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()

    # kia_faq.csv 파일 읽기 및 데이터 삽입
    print("KIA FAQ data inserting...")
    with open(CSV_FILE1, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute(
                "INSERT INTO car_faq (category, question, answer, site) VALUES (%s, %s, %s, %s)",
                (row['Category'], row['Question'], row['Answer'], row.get('Site'))  # site 컬럼은 없을 수 있으니 get 사용
            )

    # hyundai_faq.csv 파일 읽기 및 데이터 삽입
    print("Hyundai FAQ data inserting...")
    with open(CSV_FILE2, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            category = row['Category'].strip()
            question = row['Question'].strip()

            # question이 category로 시작하면 제거
            if question.startswith(category):
                question = question[len(category):].strip()

            cursor.execute(
                "INSERT INTO car_faq (category, question, answer, site) VALUES (%s, %s, %s, %s)",
                (category, question, row['Answer'], row.get('Site'))  # site 컬럼은 없을 수 있으니 get 사용
            )

    conn.commit()
    cursor.close()
    conn.close()
    print("FAQ data inserted successfully.")

# DB에서 데이터 조회하여 DataFrame으로 반환
def load_data_to_db(query):
    # MySQL 데이터베이스 연결
    conn = pymysql.connect(**db_config)

    df = pd.read_sql(query, conn)

    conn.close()
    return df

if __name__ == "__main__":
    insert_faq_data_to_db()