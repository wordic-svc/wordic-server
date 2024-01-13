import os
from decouple import Config, config, RepositoryEnv

ENV_TYPE = config('ENV_TYPE', default='local')  # 'dev' 또는 'production'
# get now folder

if ENV_TYPE == 'local':
    BASE_DIR = os.path.dirname(__file__) + '/.local.env'
    config = Config(RepositoryEnv(BASE_DIR))
elif ENV_TYPE == 'dev':
    BASE_DIR = os.path.dirname(__file__) + '/.dev.env'
    config = Config(RepositoryEnv(BASE_DIR))
else:
    BASE_DIR = os.path.dirname(__file__) + '/.prod.env'
    config = Config(RepositoryEnv(BASE_DIR))


# 환경 변수 가져오기
BASE_DIR = os.path.dirname(__file__)
DEBUG = config('DEBUG', default=False, cast=bool)
DATABASE_NAME = config('DATABASE_NAME')
DATABASE_USER = config('DATABASE_USER')
DATABASE_PASSWORD = config('DATABASE_PASSWORD')
DATABASE_HOST = config('DATABASE_HOST')
DATABASE_PORT = config('DATABASE_PORT')
MF_DATA_PATH = config('MF_DATA_PATH')
LOG_PATH = config('LOG_PATH')
AZURE_KEY = config('AZURE_KEY')
OPENAI_KEY = config('OPENAI_KEY')
PAPAGO_CLIENT_ID = config('PAPAGO_CLIENT_ID')
PAPAGO_CLIENT_SECRET = config('PAPAGO_CLIENT_SECRET')