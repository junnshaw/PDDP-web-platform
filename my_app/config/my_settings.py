import os
from pathlib import Path
from flask import Flask
from datetime import timedelta

class BaseConfig(object):
    '''
    flask环境配置
    '''
    SECRET_KEY="1ae29386hjbxcvgg"
    DEBUG=True
    # print(os.getenv())
    # SQLALCHEMY_DATABASE_URI = 'mysql://root:S20070001@localhost:3306/login'
    # SQLALCHEMY_TRACK_MODIFICATIONS=False
    SESSION_COOKIE_NAME='session_key'
    MAIL_SERVER='smtp.exmail.qq.com'
    MAIL_PORT=587
    MAIL_USE_TLS=True
    MAIL_USERNAME='s20070001@s.upc.edu.cn'
    MAIL_PASSWORD='Xfknk5trHd3RXQtC'
    MAIL_SUBJECT_PREFIX='AITA'
    MAIL_SENDER='s20070001@s.upc.edu.cn'
    ADMIN_EMAIL='s20070001@s.upc.edu.cn'
    BASE_PATH = os.environ.get(
        "WEBSITE_CLIENT_BASE_PATH",
        str(Path(__file__).resolve().parents[2]),
    )
    # auto: use Slurm when available; mock: create local demo outputs for UI testing.
    TASK_RUNNER = os.environ.get("WEBSITE_CLIENT_TASK_RUNNER", "auto").lower()
