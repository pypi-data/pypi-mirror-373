

import json
import time
import uuid
import requests
import base64
from ..recorder import RECORDER
import pyperclip
import pyautogui
import keyboard

class DBASR(object):

    def auc(self):
        # 实例化一个录音类 用于录音 
        recorder = RECORDER()
        audio_path = recorder.record("temp_recording")
        self.__recognizeMode(file_path=audio_path)
        # 录音完成之后 会返回一个文件路径
        # 将录音文件提交给 火山 并返回识别结果
        pass

    # 辅助函数：将本地文件转换为Base64
    def __file_to_base64(self, file_path):
        with open(file_path, 'rb') as file:
            file_data = file.read()  # 读取文件内容
            base64_data = base64.b64encode(file_data).decode('utf-8')  # Base64 编码
        return base64_data

    # recognize_task 函数
    def __recognize_task(self, file_url=None, file_path=None):
        recognize_url = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/recognize/flash"
        # 填入控制台获取的app id和access token
        appid = "2106894061"
        token = "-xs1nVLpnF_nBvxjv0lEYeFWIRDNy6cH"
        
        headers = {
            "X-Api-App-Key": appid,
            "X-Api-Access-Key": token,
            "X-Api-Resource-Id": "volc.bigasr.auc_turbo", 
            "X-Api-Request-Id": str(uuid.uuid4()),
            "X-Api-Sequence": "-1", 
        }

        # 检查是使用文件URL还是直接上传数据
        audio_data = None
        if file_url:
            audio_data = {"url": file_url}
        elif file_path:
            base64_data = self.__file_to_base64(file_path)  # 转换文件为 Base64
            audio_data = {"data": base64_data}  # 使用Base64编码后的数据

        if not audio_data:
            raise ValueError("必须提供 file_url 或 file_path 其中之一")

        request = {
            "user": {
                "uid": appid
            },
            "audio": audio_data,
            "request": {
                "model_name": "bigmodel",
                # "enable_itn": True,
                # "enable_punc": True,
                # "enable_ddc": True,
                # "enable_speaker_info": False,

            },
        }

        response = requests.post(recognize_url, json=request, headers=headers)
        if 'X-Api-Status-Code' in response.headers:
            # print(f'recognize task response header X-Api-Status-Code: {response.headers["X-Api-Status-Code"]}')
            # print(f'recognize task response header X-Api-Message: {response.headers["X-Api-Message"]}')
            # print(time.asctime() + " recognize task response header X-Tt-Logid: {}".format(response.headers["X-Tt-Logid"]))
            # print(f'recognize task response content is: {response.json()}\n')
            pass 
        else:
            print(f'recognize task failed and the response headers are:: {response.headers}\n')
            exit(1)
        return response

    # recognizeMode 不变
    def __recognizeMode(self, file_url=None, file_path=None):
        start_time = time.time()
        # print(time.asctime() + " START!")
        recognize_response = self.__recognize_task(file_url=file_url, file_path=file_path)
        code = recognize_response.headers['X-Api-Status-Code']
        logid = recognize_response.headers['X-Tt-Logid']
        if code == '20000000':  # task finished
            result = recognize_response.json()
            # 获取 并打印  recongnize_response 当中 的  result.text 内容 
            restext = result.get('result', {}).get('text', '')
            print(f"识别结果:\n\n {restext}\n")
            pyperclip.copy(restext)

            # pyautogui.hotkey('ctrl', 'v')
            keyboard.press_and_release('ctrl+v')


            # print(json.dumps(result, indent=4, ensure_ascii=False))
            # print(time.asctime() + " SUCCESS! \n")
            # print(f"程序运行耗时: {time.time() - start_time:.6f} 秒")
        elif code != '20000001' and code != '20000002':  # task failed
            print(time.asctime() + " FAILED! code: {}, logid: {}".format(code, logid))
            print("headers:")
            print(recognize_response.content)


    def sauc(self):
        pass 

        