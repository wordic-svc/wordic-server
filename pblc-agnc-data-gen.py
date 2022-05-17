import time
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import config
import os
# pip install httpx==0.24.1
import pandas as pd
from sqlalchemy.orm import sessionmaker
from model.models import FnWord, FnWording, Base


# 엑셀 파일 경로
def find_rows_with_text(df, column_name, search_text):
    """
    DataFrame에서 특정 컬럼에서 특정 문자를 찾아 해당 열을 반환하는 함수

    Parameters:
        df (pd.DataFrame): 대상 데이터프레임
        column_name (str): 검색할 컬럼의 이름
        search_text (str): 찾을 문자열

    Returns:
        pd.DataFrame: 검색된 행들로 이루어진 새로운 데이터프레임
    """
    # 특정 컬럼에서 특정 문자열을 포함하는 행 찾기
    selected_rows = df[df[column_name].str.contains(search_text, case=False, na=False)]

    return selected_rows


passwd = urllib.parse.quote(config.DATABASE_PASSWORD)
DATABASE_URL = f'postgresql+psycopg2://{config.DATABASE_USER}:{passwd}@{config.DATABASE_HOST}:{config.DATABASE_PORT}/{config.DATABASE_NAME}'
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
# 새 세션 생성
session = SessionLocal()
# font_info = session.query(FnInfo).filter(FnInfo.fn_nm == font_name.lower(), FnInfo.pvsn_st_cd == 'MF').first()
# create table
# Base.metadata.create_all(bind=engine)
'''
표준단어 필드
번호	제정차수	공통표준단어명	공통표준단어영문약어명	공통표준단어 영문명	공통표준단어 설명	"형식단어
여부"	공통표준도메인분류명	이음동의어 목록	"금칙어 
목록"
'''
excel_file_path = './data/2023-11-std-word.xlsx'
df = pd.read_excel(excel_file_path)
for index, row in df.iterrows():
    print(row['공통표준단어명'])
    print(row['공통표준단어영문약어명'])
    print(row['공통표준단어 영문명'])
    print(row['공통표준단어 설명'])
    fnWord = FnWord()
    fnWord.word = row['공통표준단어명']
    fnWord.word_eng = row['공통표준단어 영문명']
    fnWord.word_abbr = row['공통표준단어영문약어명']
    fnWord.word_desc = row['공통표준단어 설명']
    session.add(fnWord)
    session.flush()
    session.commit()


'''
표준용어 필드
번호	제정차수	공통표준용어명	공통표준용어설명	공통표준용어영문약어명	공통표준도메인명	허용값	저장 형식	표현 형식	행정표준코드명	소관기관명	용어 이음동의어 목록
'''

excel_file_path = './data/2023-11.xlsx'
df = pd.read_excel(excel_file_path)
for index, row in df.iterrows():
    print(row['공통표준용어영문약어명'])
    print(row['공통표준용어명'])
    print(row['공통표준용어설명'])
    fnWording = FnWording()
    fnWording.wording = row['공통표준용어명']
    fnWording.wording_abbr = row['공통표준용어영문약어명']
    fnWording.wording_desc = row['공통표준용어설명']
    session.add(fnWording)
    session.flush()
    session.commit()
