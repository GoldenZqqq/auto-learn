
# 多用户配置
USERS = [
    {
        "auth_token": 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJ1c2VyX2lkIjo3MjcxLCJmcm9tLXNvdXJjZSI6bnVsbCwidXNlcl9rZXkiOiI4NTMyYTY5My1hMDk2LTQ1ZDctOGM3Mi1hNTg0Nzk2M2QzYjYiLCJ1c2VybmFtZSI6IumDrea1qembqCJ9.y0hPX1Pzn-FfUt_yiMzMukEIbpTH39r3TswaIEG3OPCvdGuSs44xwIMg1JNpiLmuu9nEwnsc0xR9zZA6BjRSVg',
        "domain": ""
    },
    {
        "auth_token": 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJ1c2VyX2lkIjo3MjcyLCJmcm9tLXNvdXJjZSI6bnVsbCwidXNlcl9rZXkiOiJhZjZhZTQ2YS1jNDg0LTQzZDAtODllMi01OGQzODA1ZjVhYzMiLCJ1c2VybmFtZSI6IueOi-mUpuWNjiJ9.hZRKWL83raVjPf-nddYkyua2L_ml-lXtmnH55vDIVSBge2gdp4eAkIIpd12e3NNLGmgvFKUn1wKQbrbdb_yxcQ',
        "domain": ""
    },
    {
        "auth_token": 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJ1c2VyX2lkIjo3MjczLCJmcm9tLXNvdXJjZSI6bnVsbCwidXNlcl9rZXkiOiJlZGM2NGJmOC02YzMwLTRiMGQtOTJiOS05MzliNWI5ZjA3YTUiLCJ1c2VybmFtZSI6IuWImOS9s-aZqCJ9.sOyEU7CHZiE3BT12rBwsO5JKrd0VYsmPkCOfeIE3fQkWOuSZ0ErUzMjkbltnbhLPobZkKVYs3dJiutptvwAPNQ',
        "domain": ""
    }
]

# API配置
BASE_URL = "https://eduapi.bkehs.com"
AUTH_URL = BASE_URL

# 学习配置
MIN_UPDATE_INTERVAL = 3  # 最小更新间隔（秒）
MAX_UPDATE_INTERVAL = 8  # 最大更新间隔（秒）
PROGRESS_CHUNK_SIZE = 60  # 每次更新的进度时长（秒）