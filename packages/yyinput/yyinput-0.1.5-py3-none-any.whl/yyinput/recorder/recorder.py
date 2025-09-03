
import pyaudio
import wave
import os 
import platform
import threading
import sys
import select


class RECORDER(object):

    __linux_audio_path = os.path.expanduser("~/.ayyinput/audio/")
    __windows_audio_path = os.path.expanduser("~\\.ayyinput\\audio\\")

    def __init__(self):
        self.__audio_path = self.__linux_audio_path
        if os.name == "nt":
            self.__audio_path = self.__windows_audio_path
        if not os.path.exists(self.__audio_path):
            os.makedirs(self.__audio_path)


    def record(self, filename):
        """
        Record audio from the microphone and save it to a file.
        Recording stops when user presses Enter.

        Args:
            filename (str): The name of the file to save the audio to.
        """
        p = pyaudio.PyAudio()

        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=44100,
                        input=True,
                        frames_per_buffer=1024)

        print("* 开始录音，按 Enter 键停止录音...")
        
        frames = []
        recording = True
        
        # 创建一个线程来监听全局快捷键
        def listen_for_hotkey():
            nonlocal recording
            import keyboard
            keyboard.wait('ctrl+shift+space')  # 等待用户按Ctrl+Shift+Space
            recording = False
        
        # 启动监听线程
        listener_thread = threading.Thread(target=listen_for_hotkey)
        listener_thread.daemon = True
        listener_thread.start()

        # 录音循环
        while recording:
            try:
                data = stream.read(1024, exception_on_overflow=False)
                frames.append(data)
            except Exception as e:
                print(f"录音过程中出现错误: {e}")
                break

        print("* 录音结束")

        stream.stop_stream()
        stream.close()
        p.terminate()

        # 保存音频文件
        wf = wave.open(self.__audio_path + filename + ".wav", 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        # print(f"* 音频已保存到: {self.__audio_path + filename + '.wav'}")
        return self.__audio_path + filename + ".wav"



if __name__=="__main__":
    recorder = RECORDER()
    recorder.record("test")




