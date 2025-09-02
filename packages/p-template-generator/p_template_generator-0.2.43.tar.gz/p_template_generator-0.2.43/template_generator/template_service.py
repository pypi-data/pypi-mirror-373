import sys
import os
import subprocess
import json
import random
import logging
import shutil
import time
from PIL import Image
from pathlib import Path
from threading import Thread, current_thread, Lock
from collections import deque

from template_generator import binary
from template_generator import aigc_input
from template_generator import template
from template_generator.convertor import convertor
from template_res import template as template_res_search

# def video_complate():
#     print("video_complate")

# task_queue = ["task1", "task2", "task3"]
# binary_dir, binary_file = template.getBinary("", False)
# binary_dir = "E:\\template\\template_process_cross_platform\\build\\Release"
# import ctypes
# tp_sdk = ctypes.CDLL(f'{binary_dir}\\TemplateProcess.dll')
# tp_sdk.initSDK()
# tp_sdk.setMesa(True)
# tp_sdk.setSoftware(True)
# callback_type = ctypes.CFUNCTYPE(None)  
# callback = callback_type(video_complate)  
# tp_sdk.setOuterCallback(callback)
# tp_sdk.config2Video.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_int]   
# tp_sdk.config2Video.restype = ctypes.c_bool  
# a = time.time()
# result = tp_sdk.config2Video(b"E:\\template\\template_python\\template_generator\\template_generator\\test\\tp_2023112102\\param.config", 
#                  b'D:\\Program Files (x86)\\anaconda3\\lib\\site-packages\\template_generator\\bin\\subEffect', 
#                  b'D:\\Program Files (x86)\\anaconda3\\lib\\site-packages\\template_generator\\bin\\fonts', 
#                  False, 
#                  False)
# a1 = time.time()
# print(a1-a)

import psutil
class aaaaaaaaaaaa(Thread):
    queue = None
    def __init__(self):
        self.queue = deque(maxlen=20)
        self.start()

    def getCurrentPerformance(self):
        return sum(self.queue) / len(self.queue)

    def start(self, isProduct=False, threadNum=1):
        while (True):
            cpu_count = psutil.cpu_count(logical=False)
            cpu_percentages = psutil.cpu_percent(percpu=True)
            average_cpu_percentage = sum(cpu_percentages) / cpu_count
            self.queue.append(average_cpu_percentage)
            time.sleep(1)
            if random.randint(0, 10) == 3:
                print(self.getCurrentPerformance())
# a = aaaaaaaaaaaa()
# a.join()
    
    

# class KeepTemplateProcessThread(Thread):
#     pipin = None
#     pipout = None
#     process = None
#     def __init__(self):
#         super().__init__()
#         self.pipin = open('E:\\template\\demo\\config_to_video\\in.txt', 'w')
#         self.pipout = open('E:\\template\\demo\\config_to_video\\out.txt', 'r')
#         self.start()
#     def run(self):
#         binary_dir, binary_file = template.getBinary("", False)
#         binary_dir = "E:\\template\\template_process_cross_platform\\build\\Debug"
#         print("start!!!!!!!!")
#         self.process = subprocess.Popen([os.path.join(binary_dir, binary_file), "--service"],
#                                 stdin=subprocess.PIPE,
#                                 stdout=subprocess.PIPE, 
#                                 cwd=binary_dir)
#         self.process.wait()
#         print("end!!!!!!!!")
#         self.pipin.close()
#         output = self.pipout.readlines()
#         print(output)
#         self.pipout.close()
#         print(f"stop")
#     def markStop(self):
#         self.pipin.write(f"--quit".encode())
#     def push(self, task):
#         self.process.stdin.write(task.encode())
#     def readOutput(self):
#         return self.pipout.readlines()

# t=KeepTemplateProcessThread()
# for i in range(0, 100):
#     time.sleep(5)
#     print("send")
#     t.push(f"task {i}")
#     print(t.readOutput())
# t.join()
