import sys
import os
import subprocess
import json
import shutil
import zipfile
import time
from template_generator import template
from template_generator import binary

def updateRes(rootDir):
    for root,dirs,files in os.walk(rootDir):
        for file in files:
            if file.find(".") <= 0:
                continue
            name = file[0:file.index(".")]
            ext = file[file.index("."):]
            if ext == ".zip.py" and os.path.exists(os.path.join(root, name)) == False:
                for dir in dirs:
                    shutil.rmtree(os.path.join(root, dir))
                with zipfile.ZipFile(os.path.join(root, file), "r") as zipf:
                    zipf.extractall(os.path.join(root, name))
                return
        if root != files:
            break

def test(searchPath):
    rootDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test")
    updateRes(rootDir)
    for s in ["res", "tp", "tp_20231121", "tp_2023112101"]:
        if os.path.exists(os.path.join(rootDir, s)):
            shutil.rmtree(os.path.join(rootDir, s))
    test_template_dir = os.path.join(rootDir, "tp_2023112102")
    img_output = os.path.join(test_template_dir, "out.png")
    video_output = os.path.join(test_template_dir, "out.mp4")
    tp_dir = os.path.join(test_template_dir, "gen_template")
    tp_output = os.path.join(test_template_dir, "tp_out.mp4")
    noizz_output = os.path.join(test_template_dir, "noizz_out.mp4")
    tmp_file = []
    tmp_file.append(img_output)
    tmp_file.append(video_output)
    tmp_file.append(tp_output)
    tmp_file.append(noizz_output)
    #1024 picture
    img_start_pts = time.time()
    config = {
        "input":[
            os.path.join(test_template_dir, "1.png"),
            os.path.join(test_template_dir, "2.png"),
            os.path.join(test_template_dir, "3.png"),
            os.path.join(test_template_dir, "4.png"),
            ],
        "template":os.path.join(test_template_dir, "gen_img"),
        "params":{},
        "output":img_output
        }
    template.executeTemplate(config, searchPath, useAdaptiveDuration=False, useAdaptiveSize=False, printLog=False)
    img_success = False
    if os.path.exists(img_output):
        img_success = True
    img_end_pts = time.time()
    #1024 video
    config["template"] = os.path.join(test_template_dir, "gen_video")
    config["output"] = video_output
    template.executeTemplate(config, searchPath, useAdaptiveDuration=False, useAdaptiveSize=False, printLog=False)
    video_end_pts = time.time()
    video_success = False
    if os.path.exists(video_output):
        video_success = True
    #txt to video
    tp_config = {
        "width": 1024,
        "height": 1024,
        "layer": [ [ ],[ ],[ ] ]
    }
    clip_duration = 3
    for i in range(1, 4):
        tp_config["layer"][0].append({
                "res": f"hello every one, i'm template-generator with pj {i}",
                "type": "text",
                "startTime":clip_duration*(i-1),
                "duration":clip_duration,
                "positionType": "relative",
                "positionX": 0,
                "positionY": 0.8,
                "params": {
                    "animation": 0,
                    "enterAnimationDuration": 0.3,
                    "exitAnimationDuration": 0.3,
                    "textColor": "#ffffffff",
                    "stroke": 1,
                    "alignment": 2,
                    "fontSize": 3
                }
            })
        tp_config["layer"][1].append({
                "res":os.path.join(test_template_dir, f"{i}.png"),
                "type":"video",
                "startTime":clip_duration*(i-1),
                "duration":clip_duration,
				"positionType":"relative",
                "positionX":0,
                "positionY":0,
                "params": {
                    "trimStartTime":0,
                    "width": 1024,
                    "height": 1024,
					"animation":0
                }
            })
        tp_config["layer"][2].append({
                "res":os.path.join(test_template_dir, f"{i}.mp3"),
                "type":"audio",
                "startTime":clip_duration*(i-1),
                "duration":clip_duration,
                "params": {  
                    "volume": 1
                }
            })    
    with open(os.path.join(test_template_dir, "param.config"), 'w') as f:
        json.dump(tp_config, f)
    template.generateTemplate(os.path.join(test_template_dir, "param.config"), tp_dir, searchPath, printLog=False)
    config["template"] = tp_dir
    config["output"] = tp_output
    template.executeTemplate(config, searchPath, useAdaptiveDuration=False, useAdaptiveSize=False, printLog=False)
    tp_end_pts = time.time()
    tp_success = False
    if os.path.exists(tp_output):
        tp_success = True
    #noizz video
    config["template"] = os.path.join(test_template_dir, "noizz_tp")
    config["output"] = noizz_output
    template.executeTemplate(config, searchPath, useAdaptiveDuration=False, useAdaptiveSize=False, printLog=False)
    noizz_end_pts = time.time()
    noizz_success = False
    if os.path.exists(noizz_output):
        noizz_success = True

    if video_success and img_success and tp_success and noizz_success:
        print(f"[1024x1024                      Picture] Generate time is {round(img_end_pts-img_start_pts,2)}s")
        print(f"[1024x1024, 16.7s, 30 fps         Video] Generate time is {round(video_end_pts-img_end_pts,2)}s")
        print(f"[1024x1024, 9s             TXT to Video] Generate time is {round(tp_end_pts-video_end_pts,2)}s")
        print(f"[544 x 960, 14.93s          Noizz Video] Generate time is {round(noizz_end_pts-tp_end_pts,2)}s")
        if (video_end_pts-video_end_pts) < 5:
            print(f"your device is greate!")
        elif (video_end_pts-video_end_pts) < 15:
            print(f"your device is ordinary")
        else:
            print(f"your device performance is very low")
    else:
        print(f"test fail")
    for s in tmp_file:
        os.remove(s)
    shutil.rmtree(tp_dir)

if __name__ == '__main__':
    test("")
# def testAigc(cnt):
#     for i in range(0,cnt):
#         try:
#             inputs = []
#             output_width = 100
#             output_height = 100
#             fn_name = "aicamera"
#             params = {"batch_count":1,"batch_size":1,"cfg_scale":7,"creative_strength":1,"denoising_strength":1,"era":"spaceSuit","face_index":1,"fn_name":"aicamera","func":"d849eff2cfb2d09a0bb7ae573e69b1cc.png","height":1536,"musicUrl":"","negative_prompt":"","package_url":"https://m-beta-yesdesktop.2tianxin.com/upload/beta/undefined/6079/2763/607947D9CFD52763.zip","prompt":"","restore_faces":True,"sampler_index":"DPM++ SDE Karras","scratch":1,"seed":-1,"steps":25,"text_mark_url":"","type":"image","user_file_name":"d59e9302-f17f-4468-aa23-5b3fd3d44685.png","user_url":"","width":1152}
#             server_generator.MecordAIGC().testTask(378 , inputs, fn_name, params, output_width, output_height)
#             print("pushed one!")
#         except:
#             print("")

# server_generator.MecordAIGC().testTask(386 , [], "test fnname", {}, 100, 100)
            
# testAigc(1)
# def testToon():
#     try:
#         inputs = []
#         output_width = 100
#         output_height = 100
#         fn_name = "Toon"
#         params = {"batch_count":1,"batch_size":1,"cfg_scale":8,"creative_strength":1,"denoising_strength":1,"fn_name":"Toon","height":1024,"model_name":"toonyou_beta6.safetensors","musicUrl":"","negative_prompt":"","package_url":"https://m.mecordai.com/upload/prod/background_img/6065/4068/6065116F5E8E9104068.zip","prompt":"","restore_faces":False,"sampler_index":"DPM++ 2M Karras","seed":-1,"steps":30,"text_mark_url":"","type":"image","user_file_name":"resize_6cc1dbabdec15875b221275e02f30e50_exif.jpg","user_url":"","width":1024}
#         MecordAIGC().testTask(200, inputs, fn_name, params, output_width, output_height)
#         print("pushed one!")
#     except:
#         print("")

# def psnr(target, ref, scale):
#     target_data = np.array(target)
#     target_data = target_data[scale:-scale,scale:-scale]
 
#     ref_data = np.array(ref)
#     ref_data = ref_data[scale:-scale,scale:-scale]
 
#     diff = ref_data - target_data
#     diff = diff.flatten('C')
#     rmse = math.sqrt(np.mean(diff ** 2.) )
#     return 20*math.log10(1.0/rmse)

# import cv2
# import numpy as np
# import math
# def calculate_psnr(original_img, compressed_img):
#     img1 = cv2.imread(original_img)
#     img2 = cv2.imread(compressed_img)

#     gray_img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
#     gray_img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

#     mse = np.mean((gray_img1 - gray_img2) ** 2)

#     if mse == 0:
#         return float('inf')

#     max_pixel = 255.0
#     psnr = 20 * math.log10(max_pixel / math.sqrt(mse))
#     return psnr

# from skimage.metrics import structural_similarity as compare_ssim
# def calculate_ssim(original_img, compressed_img):
#     img1 = cv2.imread(original_img)
#     img2 = cv2.imread(compressed_img)
#     gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
#     gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

#     score, diff = compare_ssim(gray1, gray2, full=True)
#     return score

# psnr_score = calculate_psnr("C:\\Users\\123\\Downloads\\3333\\heidao-shu_video-cover.jpg",
#                              "C:\\Users\\123\\Downloads\\3333\\mohu.jpg")
# print(f"================== PSNR分数为：{psnr_score:.2f}")
# psnr_score = calculate_psnr("C:\\Users\\123\\Downloads\\3333\\heidao-shu_video-cover.jpg",
#                              "E:\\template\\111111111111111111111111111111111111111111package\\test\\out.png")
# print(f"================== PSNR分数为：{psnr_score:.2f}")
# psnr_score = calculate_psnr("C:\\Users\\123\\Downloads\\3333\\heidao-shu_video-cover.jpg",
#                              "E:\\template\\111111111111111111111111111111111111111111package\\test\\out_stb.png")
# print(f"================== PSNR分数为：{psnr_score:.2f}")

# ssim_score = calculate_ssim("C:\\Users\\123\\Downloads\\3333\\heidao-shu_video-cover.jpg",
#                              "C:\\Users\\123\\Downloads\\3333\\mohu.jpg")
# print(f"================== SSIM分数为：{ssim_score:.2f}")
# ssim_score = calculate_ssim("C:\\Users\\123\\Downloads\\3333\\heidao-shu_video-cover.jpg",
#                              "E:\\template\\111111111111111111111111111111111111111111package\\test\\out.png")
# print(f"================== SSIM分数为：{ssim_score:.2f}")
# ssim_score = calculate_ssim("C:\\Users\\123\\Downloads\\3333\\heidao-shu_video-cover.jpg",
#                              "E:\\template\\111111111111111111111111111111111111111111package\\test\\out_stb.png")
# print(f"================== SSIM分数为：{ssim_score:.2f}")


# from facebook_scraper import get_posts
# #credentials=("dajidali.dev@gmail.com","dajidalidajidali"), 
# for post in get_posts('nintendo',start_url="https://mbasic.facebook.com/nintendo?v=timeline", pages=10, cookies='/Users/pengjun/Desktop/template_python/template_generator/template_generator/cookie.txt'):
#     print(post)
#     exit(-1)

# #import Facebook_scraper class from facebook_page_scraper
# from facebook_page_scraper import Facebook_scraper

# #instantiate the Facebook_scraper class

# page_or_group_name = "Meta"
# posts_count = 10
# browser = "chrome"
# proxy = "IP:PORT" #if proxy requires authentication then user:password@IP:PORT
# timeout = 600
# headless = True
# fb_password = "dajidalidajidali"
# fb_email = "dajidali.dev@gmail.com"
# isGroup= False
# meta_ai = Facebook_scraper(page_or_group_name, posts_count, browser, proxy=proxy, timeout=timeout, headless=headless, isGroup=isGroup)