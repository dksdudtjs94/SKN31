import csv
import os
import pandas as pd
import pymysql
from dotenv import load_dotenv


"""
DB 연결
- MySQL 데이터베이스에 CSV 데이터를 삽입
- DB에서 데이터를 조회하여 DataFrame으로 반환
- DataFrame에서 가성비 점수 계산
"""

CSV_FILE5 = "data/kia_faq.csv"      # category, question, answer, site
CSV_FILE6 = "data/hyundai_faq.csv"  # category, question, answer, site

# 데이터베이스 설정 (MYSQL)
load_dotenv()
db_config = {
    'user': os.getenv("DB_USER"),           # MySQL 사용자 이름
    'password': os.getenv("DB_PASSWORD"),   # MySQL 비밀번호
    'host': os.getenv("DB_HOST"),           # MySQL 호스트
    'database': os.getenv("DB_NAME")        # 사용할 데이터베이스 이름
}


# FAQ 데이터 삽입
### 실행 안되면 encoding 방식 'cp949'로 바꿔보기 ###
def insert_faq_data_to_db():

    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()

    # kia_faq.csv 파일 읽기 및 데이터 삽입
    print("KIA FAQ data inserting...")
    with open(CSV_FILE5, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute(
                "INSERT INTO car_faq (category, question, answer, site) VALUES (%s, %s, %s, %s)",
                # (row['category'], row['question'], row['answer'], row.get('site'))  # site 컬럼은 없을 수 있으니 get 사용
                (row['Category'], row['Question'], row['Answer'], row.get('Site'))  # site 컬럼은 없을 수 있으니 get 사용
            )

    # hyundai_faq.csv 파일 읽기 및 데이터 삽입
    print("Hyundai FAQ data inserting...")
    with open(CSV_FILE6, mode='r', encoding='utf-8-sig') as file:
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

# 가성비 점수 계산
# def calculate_value_score(df: pd.DataFrame,
#     w_price=0.4, w_year=0.2, w_mileage=0.3, w_count=0.1) -> pd.DataFrame:
#     """
#     CarName + CarInfo JOIN 결과 DataFrame에서 가성비 점수를 계산하고 반환합니다.
    
#     df 컬럼:
#     - 'car_name', 'full_name', 'price', 'model_year', 'mileage', 'newcar_price'
    
#     반환:
#     - 기존 컬럼 + 'model_count', 'price_saving', 'year_score', 'mileage_score', 'count_score', 'value_score'
#     """
    
#     df = df.copy()
    
#     # 동일 모델 등록 대수
#     df['model_count'] = df.groupby('car_name')['car_name'].transform('count')
    
#     # 정규화 점수 계산
#     df['price_saving'] = (df['newcar_price'] - df['price']) / df['newcar_price']
#     df['year_score'] = (df['model_year'] - df['model_year'].min()) / (df['model_year'].max() - df['model_year'].min())
#     df['mileage_score'] = 1 - (df['mileage'] - df['mileage'].min()) / (df['mileage'].max() - df['mileage'].min())
#     df['count_score'] = (df['model_count'] - df['model_count'].min()) / (df['model_count'].max() - df['model_count'].min())
    
#     # 종합 가성비 점수
#     df['value_score'] = ((
#         w_price * df['price_saving'] +
#         w_year * df['year_score'] +
#         w_mileage * df['mileage_score'] +
#         w_count * df['count_score']
#     )*100)
    
#     # 점수 내림차순 정렬
#     df = df.sort_values(by='value_score', ascending=False).reset_index(drop=True)
    
#     return df


if __name__ == "__main__":
    insert_faq_data_to_db()