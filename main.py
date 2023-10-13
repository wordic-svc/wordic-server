from kiwipiepy import Kiwi
from googletrans import Translator
import abbreviate
import std_data
from fastapi import Depends, FastAPI


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/text/{name}")
async def say_hello(name: str):
    return {"message": f"{kor2_eng_col(name)}"}

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
    print(inputTxt)
    kiwi = Kiwi()

    trans = Translator()
    arr = []
    items = kiwi.tokenize(inputTxt)
    for item in items:
        if item[1] not in ['NNG', 'NNP', 'SL']:
            continue
        if std_data.word_to_abbrev.get(item[0]) is not None:
            arr.append(std_data.word_to_abbrev[item[0]])
            continue
        result = trans.translate(item[0], dest='en', src='ko')
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

