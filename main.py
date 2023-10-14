from concurrent.futures import ThreadPoolExecutor

from kiwipiepy import Kiwi
from googletrans import Translator
import abbreviate
import std_data
from fastapi import Depends, FastAPI
import asyncio

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
async def root():
    return {"message": "Hello World"}

# /text/{name} 엔드포인트
@app.get("/text/{name}", response_model=dict)
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
# 텍스트를 처리할 함수
def process_text(text):
    # 여기에 텍스트 처리 로직을 추가하십시오 (kor2_eng_col 함수 등을 사용)
    result = f"{kor2_eng_col(text)}"  # 예시: kor2_eng_col 함수로 처리
    return result

def snake_to_camel(snake_case):
    words = snake_case.split('_')  # 스네이크 케이스 문자열을 밑줄로 분할하여 단어 목록 생성
    camel_case = words[0] + ''.join(word.capitalize() for word in words[1:])  # 첫 번째 단어는 그대로 두고 나머지 단어는 첫 글자 대문자로 변경
    return camel_case
def list_to_snake_case(arr):
    snake_case_str = '_'.join(str(item).upper() for item in arr)
    return snake_case_str
def list_to_camel_case(arr):
    camel_case_str = ''.join(str(item) for item in arr)
    # 첫 번째 문자열은 그대로 두고 나머지 문자열의 첫 글자를 대문자로 변경
    camel_case_str = camel_case_str[0].lower() + camel_case_str[1:]
    return camel_case_str
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

