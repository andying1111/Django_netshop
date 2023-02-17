import datetime
import json
import time

import requests

from polyv.config import UPLOAD_LOG_URL


def upload_driver_log(role, driver):
    console_logs_data = []
    console_logs = driver.get_log('browser')
    for log in console_logs:
        console_data = {"url": driver.current_url,
                        "message": log.get("message"),
                        "time": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        }
        console_logs_data.append(console_data)

    # performance_logs = driver.get_log('performance')
    # request_and_response_dict = {}
    # for log in performance_logs:
    #     message = json.loads(log.get('message')).get("message")
    #     request_id = message.get("params").get("requestId")
    #     if not request_id:
    #         continue
    #
    #     chrome_method = message.get("method")
    #     request_and_response = {}
    #
    #     if chrome_method == 'Network.requestWillBeSent':
    #         request = message.get("params").get("request")
    #         request_and_response["requestId"] = request_id
    #         request_and_response["requestOrignPath"] = message.get("params").get("documentURL")
    #         request_and_response["requestPath"] = request.get("url")
    #         request_and_response["requestHeader"] = request.get("headers")
    #         request_and_response["requestMethod"] = request.get("method")
    #         if request.get("postData"):
    #             request_and_response['requestParam'] = request.get("postData")
    #
    #         request_and_response_dict[request_id] = request_and_response
    #
    # for log in performance_logs:
    #     message = json.loads(log.get('message')).get("message")
    #     request_id = message.get("params").get("requestId")
    #     if not request_id:
    #         continue
    #
    #     chrome_method = message.get("method")
    #     if request_id in request_and_response_dict.keys():
    #         request_and_response = request_and_response_dict[request_id]
    #     else:
    #         request_and_response = {}
    #     request_and_response['requestId'] = request_id
    #
    #     if chrome_method == 'Network.requestWillBeSentExtraInfo':
    #         pass
    #     elif chrome_method == 'Network.responseReceivedExtraInfo':
    #         pass
    #     elif chrome_method == 'Network.responseReceived':
    #
    #         response = message.get("params").get("response")
    #         request_and_response['remoteIPAddress'] = response.get("remoteIPAddress")
    #         request_and_response['remotePort'] = response.get("remotePort", -1)
    #         request_and_response['responseHeader'] = response.get("headers")
    #         request_and_response['responseCode'] = response.get("status")
    #         request_and_response['requestSourceType'] = message.get("params").get("type")
    #         request_and_response['requestFinishTime'] = response.get("responseTime")
    #         request_and_response['requestMimeType'] = response.get("mimeType")
    #
    #     elif chrome_method == 'Network.loadingFinished':
    #         pass
    #     elif chrome_method == 'Page.frameStartedLoading':
    #         pass
    #     elif chrome_method == 'Page.frameNavigated':
    #         pass
    #
    #     elif chrome_method == 'Network.dataReceived':
    #
    #         if (requestSourceType := request_and_response.get("requestSourceType")) == 'Script':
    #             pass
    #         elif requestSourceType == 'Stylesheet':
    #             pass
    #         elif requestSourceType == 'Image':
    #             pass
    #         elif requestSourceType == 'Media':
    #             pass
    #
    #         elif requestSourceType == 'XHR':
    #             params = {"requestId": request_id}
    #             try:
    #                 response_body = driver.execute_cdp_cmd("Network.getResponseBody", params)
    #                 request_and_response["responseBody"] = json.loads(response_body.get("body"))
    #                 if request_and_response.get("requestParam"):
    #                     request_post_data = driver.execute_cdp_cmd("Network.getRequestPostData", params)
    #                     request_and_response["requestPostData"] = json.loads(response_body.get("body"))
    #
    #                 request_and_response_dict[request_id] = request_and_response
    #
    #             except Exception as e:
    #                 print(e)
    #
    # xhr_list = []
    # static_list = []
    # for request_id, request in request_and_response_dict.items():
    #     if request.get("requestSourceType") == 'XHR':
    #         xhr_list.append(request)
    #     else:
    #         static_list.append(request)

    if console_logs_data:
        params = {
            'recordId': role,
            'data': json.dumps(console_logs_data)
        }
        print('上传了console-log')
        requests.post(url=f'{UPLOAD_LOG_URL}/chrome/analysisConsoleLog', data=params)

    # if xhr_list:
    #     params = {
    #         'recordId': role,
    #         'data': json.dumps(xhr_list)
    #     }
    #     print('上传了xhr-log')
    #     requests.post(url=f'{UPLOAD_LOG_URL}/chrome/analysisAPI', data=params)
    #
    # if static_list:
    #     params = {
    #         'recordId': role,
    #         'data': json.dumps(static_list)
    #     }
    #     print('上传了static-log')
    #     resp = requests.post(url=f'{UPLOAD_LOG_URL}/chrome/analysisStaticSource', data=params)

    print('console_data', console_logs_data)
    # print('xhr_list', xhr_list)
    # print("static_list", static_list)
    # print("role", role)
