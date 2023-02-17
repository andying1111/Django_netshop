import platform

import requests
import uvicorn
from fastapi import FastAPI, Request, Response
from requests import codes

from polyv import config
from polyv.config import Config

app = FastAPI()

from polyv.api import android
from polyv.api import ios
from polyv.api import web
from polyv.api import common


# app.add_middleware(
#     TrustedHostMiddleware,
#     allowed_hosts=["polyv.autotest.cn", "10.10.102.10"]  # 允许的 hosts 列表
# )

def de(func):
    async def wrapper():
        return func

    return wrapper


async def set_body(request: Request):
    receive_ = await request._receive()

    async def receive():
        return receive_

    request._receive = receive


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """将所有请求进行拦截"""
    token = request.headers.get('token')
    redirect = request.headers.get('redirect')
    if redirect:
        method = request.method
        api = request.url.path
        # query_params_items = request.query_params._dict
        para = str(((await request._receive())['body']), 'UTF-8').split("\r\n")
        key = None
        params = {}
        for line in para:
            if 'form-data;' not in str(para):
                key = line.split('=')[0]
                value = line.split('=')[1]
                params.setdefault(key, value)
            else:
                if 'name' in line:
                    key = str(line.split('=')[1]).replace("\"", "")
                    continue
                if line and key and ('------' not in line):
                    params.setdefault(key, line)
                    key = None
        if method == 'GET':
            data = requests.get(url=f'{redirect}{api}', data=params)
            return Response(data.content)
        elif method == 'POST':
            data = requests.post(url=f'{redirect}{api}', data=params)
            return Response(data.content)
        else:
            return Response(f'请求转发失败（{redirect}）！')
    elif config.IS_WORK and token != str(config.TOKEN) and request.base_url.hostname != 'localhost':
        return Response(f'当前代理服务正在被其他用户使用，请联系当前暂用用户（{config.TOKEN}）！')
    else:
        return await call_next(request)


# (request.url.path != '/api/common/set_work_status' and request.url.path != '/api/common/status')


app.include_router(
    common.router,
    prefix="/api/common",
    tags=["common"]
)

app.include_router(
    android.router,
    prefix="/api/android",
    tags=["android"]
)

try:
    from polyv.api import android2

    app.include_router(
        android2.router,
        prefix="/api/android2",
        tags=["android2"]
    )
except:
    pass
app.include_router(
    ios.router,
    prefix="/api/ios",
    tags=["IOS"]
)
app.include_router(
    web.router,
    prefix="/api/web",
    tags=["web"]
)

if platform.system() == 'Windows':
    from polyv.api import windows

    app.include_router(
        windows.router,
        prefix="/api/windows",
        tags=["windows"]
    )

    from polyv.api import intelligent

    app.include_router(
        intelligent.router,
        prefix='/api/intelligent',
        tags=['intelligent']
    )

if __name__ == "__main__":
    uvicorn.run(
        app=app,
        host=Config.Host,
        port=Config.Port,
        workers=1)
