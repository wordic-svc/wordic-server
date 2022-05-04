import math
from concurrent.futures import ThreadPoolExecutor
from kiwipiepy import Kiwi
from googletrans import Translator
import abbreviate
import std_data
from fastapi import Depends, FastAPI, APIRouter
import asyncio
from sqlalchemy import create_engine, text
# from sqlalchemy.orm import sessionmaker
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator, field_validator
# from typing import Optional
# import config
# import logging
# import datetime
# import urllib.parse

app = FastAPI()

# folder_path = config.MF_DATA_PATH
# log_filename = datetime.datetime.now().strftime(f"./sandoll.log")
# logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(message)s')

# passwd = urllib.parse.quote(config.DATABASE_PASSWORD)
# DATABASE_URL = f'postgresql+psycopg2://{config.DATABASE_USER}:{passwd}@{config.DATABASE_HOST}:{config.DATABASE_PORT}/{config.DATABASE_NAME}'
# engine = create_engine(DATABASE_URL)

# SessionLocal = sessionmaker(bind=engine)
# 새 세션 생성
# session = SessionLocal()

class Result(BaseModel):
    kebab_case: str
    camel_case: str
    snake_case_l: str
    snake_case_s: str
    pascal_case: str
    combined_text: list


class Word(BaseModel):
    kor_text: str
    eng_text: str
    attrive_text: str
    pos: str
    code: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIRouter 인스턴스를 생성합니다.
router = APIRouter()


@app.get("/")
async def root():
    return {"message": "Hello World"}


# /text/{name} 엔드포인트
@router.get("/text/{name}", response_model=dict)
async def say_hello(name: str):
    # asyncio 루프를 정의
    loop = asyncio.get_event_loop()

    # 여러 개의 텍스트를 처리하기 위해 ThreadPoolExecutor를 사용
    with ThreadPoolExecutor() as executor:
        # 여러 개의 텍스트를 처리하기 위해 asyncio.gather를 사용
        texts = name.split(',')  # 쉼표로 구분된 여러 개의 텍스트를 리스트로 분리
        # textsSizte check

        for text in texts:
            if len(text) > 8:
                return {'result': 'Too long text'}

        results = await asyncio.gather(
            *[loop.run_in_executor(executor, process_text, text) for text in texts]
        )

        arr = []
        for i, obj in enumerate(results):
            arr.append({
                "kor_name": f"{texts[i]}",
                "eng_name": f"{obj}"
            })
        return {'result': arr}


# /text/{name} 엔드포인트
@router.get("/text2/{name}", response_model=dict)
async def say_hello(name: str):
    obj = split_kor2_eng(name)
    attrive_text = list(map(lambda x: x.attrive_text, obj))
    result = Result(
        kebab_case='',
        camel_case='',
        snake_case_l='',
        snake_case_s='',
        pascal_case='',
        combined_text=[]
    )
    result.pascal_case = list_to_pascal_case(attrive_text)
    result.camel_case = list_to_camel_case(attrive_text)
    result.snake_case_l = list_to_snake_case(attrive_text).upper()
    result.snake_case_s = list_to_snake_case(attrive_text).lower()
    result.kebab_case = list_to_kebab_case(attrive_text)
    result.combined_text = attrive_text  # Assuming you want to add 'attrive_text' to 'combined_text'

    return {'result': {
        "info": result,
        "words": obj
    }}


# 텍스트를 처리할 함수
# /text/{name} 엔드포인트
@router.get("/eng/{name}", response_model=dict)
async def say_hello(name: str):
    data = eng2attrive_list(name)
    return {'result': data}


# 텍스트를 처리할 함수
def process_text(text):
    # 여기에 텍스트 처리 로직을 추가하십시오 (kor2_eng_col 함수 등을 사용)
    result = f"{kor2_eng_col(text)}"  # 예시: kor2_eng_col 함수로 처리
    return result


def snake_to_camel(snake_case):
    words = snake_case.split('_')  # 스네이크 케이스 문자열을 밑줄로 분할하여 단어 목록 생성
    camel_case = words[0] + ''.join(word.capitalize() for word in words[1:])  # 첫 번째 단어는 그대로 두고 나머지 단어는 첫 글자 대문자로 변경
    return camel_case


def list_to_kebab_case(arr):
    return '-'.join(arr)


def list_to_snake_case(arr):
    return '_'.join(arr)


def list_to_camel_case(arr):
    return arr[0] + ''.join(map(lambda x: x[0].upper() + x[1:], arr[1:]))


def list_to_pascal_case(arr):
    return ''.join(map(lambda x: x[0].upper() + x[1:], arr))

def pos_code_to_korean(pos_code):
    pos_mapping = {
        'NNG': '일반 명사',
        'NNP': '고유 명사',
        'SL': '외국어',
        'XSN': '명사파생 접미사',
        'SN': '숫자',
        # 추가적인 품사 코드에 대한 매핑을 진행하려면 여기에 추가하세요.
    }

    return pos_mapping.get(pos_code, '알 수 없는 품사')

def split_kor2_eng(inputTxt):
    kiwi = Kiwi()

    trans = Translator()
    arr = []
    items = kiwi.tokenize(inputTxt)
    for index, item in enumerate(items):
        if item[1] not in ['NNG', 'NNP', 'SL', 'XSN', 'SN']:
            continue
        text = item[0]

        result = trans.translate(text, dest='en', src='ko')
        arr.append(Word(
            kor_text=text,
            eng_text=result.text.lower(),
            attrive_text=eng2attrive(result.text.lower()),
            pos=str(index),
            code=pos_code_to_korean(item[1])
        ))
    return arr


def kor2_eng_col(inputTxt):
    kiwi = Kiwi()

    trans = Translator()
    arr = []
    items = kiwi.tokenize(inputTxt)
    for item in items:
        if item[1] not in ['NNG', 'NNP', 'SL', 'XSN', 'SN']:
            continue
        text = item[0]
        if std_data.word_to_chng.get(text) is not None:
            text = std_data.word_to_chng[text]

        if std_data.word_to_abbrev.get(text) is not None:
            arr.append(std_data.word_to_abbrev[text])
            continue
        result = trans.translate(text, dest='en', src='ko')
        text = result.text.lower()
        if len(text) > 5:
            arr.append(abbreviate.process_string(text, 4))
        elif len(text) > 4:
            arr.append(abbreviate.process_string(text, 3))
        elif len(text) > 3:
            arr.append(abbreviate.process_string(text, 2))
        else:
            arr.append(text)
    print(arr)
    return list_to_snake_case(arr)


def eng2attrive_list(text):
    if std_data.word_to_chng.get(text) is not None:
        text = std_data.word_to_chng[text]

    arr = []
    allSize = len(text) + 1

    for i in range(math.ceil(allSize * 0.2), math.ceil(allSize * 0.7)):
        result = abbreviate.process_string(text, i)
        arr.append({
            'text': result,
            'length': i
        })
    return arr


def eng2attrive(text):
    if std_data.word_to_chng.get(text) is not None:
        text = std_data.word_to_chng[text]

    if len(text) > 5:
        text = abbreviate.process_string(text, 4)
    elif len(text) > 4:
        text = abbreviate.process_string(text, 3)
    elif len(text) > 3:
        text = abbreviate.process_string(text, 2)

    print(text)
    return text


# "/wordic-api" 경로 아래에 라우터를 추가합니다.
app.include_router(router, prefix="/wordic-api")
