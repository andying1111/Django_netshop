from pathlib import Path


class Config:
    Host = "0.0.0.0"
    Port = 8081
    ClientServer = "10.10.102.101"
    ClientPort = "6633"
    Server = "http://10.10.102.101"
    Version = 'v1.0'
    BASE_DIR = Path(__file__).resolve().parent.parent
    AIRTEST_IMG_DIR = BASE_DIR / '.airtest_images'
    AIRTEST_SNAPSHOT_DIR = BASE_DIR / '.snapshots'


# 钉钉群通知token配置
DingTalkToken = {
    "COM": '55b29404483764f5d3317c917065a9aab62006ac640a2872801954ba1fbe775a',
    "LIVE": '8c49c7c1e764b02b88602693063722272b2f7d108990d6525f47f3135071b1ac',
    "HI": '5513f80a6de253b404a908beb221b8ef95e77e03370a629e39fd741699947c5',
    "VOD": '5513f80a6de253b404a908beb221b8ef95e77e03370a629e39fd741699947c5',
    "DEBUG": '6e0ad73c63d5632aba7c84bf51e812bab2afe8aab36404b574ed84da84054c5d',
}

# 人员触发者
QA_INFO = {
    "caolipin": "13802430850",
    "lihongbo": "18520589284",
    "admin": "18520589284",
    "zhangpeifeng": "13051528719",
    "liangyaohui": "15521200407",

    'guanjianfeng': "13560049916",
    "liangjinwen": "15099961552",
    "xiexiuzhu": "18702013610",
    "oupeisi": "18620748010",
    "lizhikang": "13750314723",
    "litian": "18312851463",
    "zhoumin": "13716432161",
    "jiangjialin": "18823158983",
    "lileiming": "18630036313",
    "panrui": "18719003106",
    "laizefei": "13592984391",
    "lijianhao": "13729032822",
    "chenfa": "13129344489",
    "chenweijun": "13725132270",
    "chenqingjie": "18814127438",
    "huangyuxing": "13659777910",
    "huoruibin": "15692186171",
    "xumin": "13524337737",
}

# 推流地址
STREAM_PUSHER_INFO = 'http://172.18.204.130:8332'

UPLOAD_LOG_URL = 'http://192.168.21.246:8989'

IS_UPLOAD_LOG = False

IS_RUNNER = False

IS_NEW_RUNNER = True

IS_WORK = False

TOKEN = None
