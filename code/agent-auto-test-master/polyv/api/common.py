import platform

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from polyv.common import ImageTool
from polyv.common.data_format import DataFormat
from polyv.common.file_util import FileUtils
from polyv.scripts.common import Service, HostUtils

router = APIRouter()
df = DataFormat()
service = Service()


# 创建数据模型
class Item(BaseModel):
    type: str
    projectSign: str
    data: dict


@router.get('/status', name='获取服务状态')
def status():
    return service.status()


@router.post('/set_work_status', name='设置服务状态')
def status(state: bool = True):
    return service.set_status(state)


@router.get("/report", name='查看测试报告')
def see_report(id: str = None):
    return service.get_report(id)


@router.get("/image", name='查看图片')
def see_image(image_id: str = None):
    return service.get_image(image_id)


@router.get("/delete/image", name='删除测试报告')
def delete_image(days: int = 7, path: str = None):
    """移除N天以前的图片文件"""
    import os
    if path is None:
        root_path = os.getcwd()
        image_path = "/image.temp" if platform.system() != "Windows" else '\\image.temp'
        path = root_path + image_path
        path = path.replace('agent/api/', '').replace('agent\\api\\', '')
    return FileUtils().remove_files(breday=days, path=path)


@router.post("/send_results", name="发送测试结果")
def send_results(item: Item):
    json_compatible_item_data = jsonable_encoder(item)
    return service.send_results(json_compatible_item_data)


@router.get('/host_data', name="获取host数据")
def read_host():
    host_obj = HostUtils()
    return host_obj.get_host()


@router.get('/get_network_info', name='查询网速记录')
def get_network_info(cycle=1200):
    return service.get_network_info(cycle)


@router.post('/host_data', name="以json形式覆盖写入host")
def overwrite_host(host_dict: dict):
    """
                覆盖写入host配置(字典形式)
                {
                "host_dict":{
                    "183.61.83.227": [
                        "",
                        "live.polyv.net",
                        "",
                        "live.polyv.cn",
                        "api.polyv.net",
                        "console.polyv.net"
                    ],
                    "192.168.201.117": [
                        "chat.polyv.net",
                        "apichat.polyv.net",
                        "chat-d.polyv.net"
                    ]
            }}
            """

    host_dict = host_dict.get('host_dict')
    host_obj = HostUtils()
    return host_obj.overwrite_host(host_dict)


@router.post('/host_str', name="以字符串形式写入host")
def overwrite_host_str(host_str: dict):
    host_str = host_str.get("host_str")
    host_obj = HostUtils()
    return host_obj.write_text_host(host_str)


@router.get("/cmd", name="agent机器执行cmd")
def cmd(command):
    return service.cmd(command)


@router.get("/push_flow/start", name="指定频道号推流（仅该web_live_test测试账号下频道可用）")
def push_flow_start(channel):
    return service.push_flow_start(channel)


@router.get("/push_flow/stop", name="停止推流")
def push_flow_stop(channel):
    return service.push_flow_stop(channel)


@router.get("/push_flow/status", name="推流服务状态")
def push_flow_status(channel):
    return service.push_flow_status(channel)


@router.get('/get_download_file', name='获取下载的文件')
def get_download_file():
    return service.get_download_file()


@router.post('/delete_download_file', name='获取下载的文件')
def delete_download_file(filename=None):
    return service.delete_download_file(filename)


@router.get('/get_resource_file', name='获取资源的文件路径')
def get_download_file(filename):
    return service.get_resource_file(filename)


@router.post('/image_compare', name='图片对比，返回相似度')
def image_compare(image1, image2):
    from polyv.scripts.android_bak import AndroidAgent
    return AndroidAgent().classify_hist_with_split(image1, image2)


@router.post('/image_difference', name='图片对比，返回差值[差值越大，相似度越低]')
def image_difference(image1, image2):
    return ImageTool.compare(image1, image2)


@router.post('/image_is_similar', name='图片比对是否极度相似，返回True或False')
def image_is_similar(image1, image2):
    return ImageTool.is_img_similar(image1, image2)


@router.post('/delete_pc_process_by_name', name='PC删除指定应用的所有进程')
def delete_pc_process_by_name(application_name):
    return service.delete_pc_process_by_name(application_name)
