import sys
import os
import time
import json
import threading
from urllib.parse import urlparse
import shutil
import zipfile
import stat
import logging
import requests
from PIL import Image
from pathlib import Path

from template_generator import binary

def get_uuid():
    import uuid
    return str(uuid.uuid4()).replace("{","").replace("}","")
   
def mediaType(path):
    file_name = Path(path).name
    ext = file_name[file_name.index("."):].lower()
    if ext in [".jpg", ".png", ".jpeg", ".bmp", ".webp", ".gif"]:
        return "image"
    elif ext in [".mp4",".mov",".avi",".wmv",".mpg",".mpeg",".rm",".ram",".flv",".swf",".ts"]:
        return "video"
    elif ext in [".mp3",".aac",".wav",".wma",".cda",".flac",".m4a",".mid",".mka",".mp2",".mpa",".mpc",".ape",".ofr",".ogg",".ra",".wv",".tta",".ac3",".dts"]:
        return "audio"
    else:
        return "image"
    
def resize_and_crop(image_path, target_resolution):
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{get_uuid()}.jpg")
    image = Image.open(image_path)
    original_width, original_height = image.size
    target_width, target_height = target_resolution
    target_width = int(target_width)
    target_height = int(target_height)
    width_ratio = target_width / original_width
    height_ratio = target_height / original_height
    scale_ratio = max(width_ratio, height_ratio)
    final_width = int(scale_ratio * original_width)
    final_height = int(scale_ratio * original_height)
    resized_image = image.resize((final_width, final_height))
    canvas = Image.new('RGB', (target_width, target_height), (255, 255, 255))
    x = (target_width - final_width) // 2
    y = (target_height - final_height) // 2
    canvas.paste(resized_image, (x, y))
    canvas.save(output_path)
    return output_path

def needAIGC(inputList):
    finded = False
    for it in inputList:
        if "aiTasks" in it:
            for task in it["aiTasks"]:
                fn_name = task["serverAiType"]
                if len(fn_name) > 0:
                    finded = True
    return finded

def preProcessAIGC(config,tmp_file_cache,tmp_dir_cache):
    #暂不支持
    return
    # template_path = config["template"]
    # if os.path.exists(template_path) == False:
    #     return
    # input_list_path = os.path.join(template_path, "inputList.conf")
    # input_list_path1 = os.path.join(template_path, "skyinput0.conf")
    # inputList = None
    # if os.path.exists(input_list_path):
    #     with open(input_list_path, 'r', encoding='utf-8') as f:
    #         inputList = json.loads(f.read())
    # if os.path.exists(input_list_path1):
    #     with open(input_list_path1, 'r', encoding='utf-8') as f:
    #         inputList = json.loads(f.read())
    # if inputList == None or needAIGC(inputList) == False:
    #     return
    
    # copy_template_tmp = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{get_uuid()}")
    # shutil.copytree(template_path, copy_template_tmp)
    # tmp_dir_cache.append(copy_template_tmp)
    # template_path = copy_template_tmp
    # config["template"] = template_path
                
    # #input_res map to inputList
    # mapInput = {}
    # it_idx = 0
    # input_res = config["input"]
    # if len(input_res) > 0:
    #     for it in inputList:
    #         err_found_cnt = 0
    #         found = True
    #         res_idx = 0
    #         while mediaType(input_res[res_idx]) != it["type"].lower():
    #             res_idx+=1
    #             if res_idx >= len(input_res):
    #                 res_idx = 0
    #             err_found_cnt+=1
    #             if err_found_cnt > len(input_res):
    #                 found = False
    #                 break
    #         if found:
    #             mapInput[it["path"]] = input_res[res_idx]
    #         it_idx+=1
    # for it in inputList:
    #     if "aiTasks" in it:
    #         for task in it["aiTasks"]:
    #             fn_name = task["serverAiType"]
    #             params = task["params"]
    #             inputCfgs = task["serverInputCfg"]
    #             outCfg = task["serverOutputCfg"]

    #             real_inputs = []
    #             for cfg in inputCfgs:
    #                 new_input = ""
    #                 if cfg in mapInput:
    #                     new_input = mapInput[cfg]
    #                 if len(new_input) > 0:
    #                     tmpImage = resize_and_crop(new_input, (it["width"],it["height"]))
    #                     real_inputs.append(tmpImage)
    #                     tmp_file_cache.append(tmpImage)
    #                     # #remove input res 
    #                     # del config["input"][config["input"].index(new_input)]
    #                 else:
    #                     if cfg[0:1] == "/":
    #                         normal_input = os.path.join(template_path, cfg[1:])
    #                     else:
    #                         normal_input = os.path.join(template_path, cfg)
    #                     real_inputs.append(normal_input)
    #             local_path = server_generator.process(real_inputs, fn_name, params, outCfg[0]["width"], outCfg[0]["height"])
    #             for cfg in outCfg:
    #                 cfg_path = cfg["path"]
    #                 cfg_width = cfg["width"]
    #                 cfg_height = cfg["height"]
    #                 if cfg_path[0:1] == "/":
    #                     cfg_path = cfg_path[1:]
    #                 save_out = os.path.join(template_path, cfg_path)
    #                 target_type, target_width, target_height = server_generator.mediaInfo(local_path)
    #                 if target_width != cfg_width or target_height != cfg_height:
    #                     tmpImage = resize_and_crop(local_path, (target_width,target_height))
    #                     shutil.copyfile(tmpImage, save_out)
    #                     tmp_file_cache.append(tmpImage)
    #                 else:
    #                     shutil.copyfile(local_path, save_out)
    #                 tmp_file_cache.append(local_path)