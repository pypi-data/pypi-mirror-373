

import os
import json
import os
import json
import uuid
import imagesize
import math
import shutil
from template_generator import of_to_skymedia

def ai_config(inputConfig, outputConfig):
    input_type = inputConfig["type"]
    if input_type == "file":
        input_image_rel_path = inputConfig["local_path"]
        output_image_rel_path = outputConfig["local_path"]
    elif input_type == "text":
        raise Exception("no")
    extra = {}
    if "extras" in inputConfig:
        extra = inputConfig["extras"]
    return input_image_rel_path, output_image_rel_path, extra

def processAigc(input_param, root_dir):
    processSuccess = True
    for it in input_param:
        if "width" not in it:
            continue
        # if math.fabs(int(it["width"]) / int(it["height"]) - 1) > 0.1:
        #     continue
        extra = {}
        if "ai_tasks" in it:
            aitype = it["ai_tasks"][0]["server_input_cfg"]["params"][0]["server_ai_type"]
            input_image_rel_path, output_image_rel_path, extra = ai_config(it["ai_tasks"][0]["server_input_cfg"]["params"][0], it["ai_tasks"][0]["server_output_cfg"]["params"][0])
            # input_type = it["ai_tasks"][0]["server_input_cfg"]["params"][0]["type"]
            # if input_type == "file":
            #     input_image_rel_path = it["ai_tasks"][0]["server_input_cfg"]["params"][0]["local_path"]
            #     output_image_rel_path = it["ai_tasks"][0]["server_output_cfg"]["params"][0]["local_path"]
            # elif input_type == "text":
            #     output_image_rel_path = it["ai_tasks"][0]["server_output_cfg"]["params"][0]["content"]
            # extra = it["ai_tasks"][0]["server_input_cfg"]["params"][0]["extras"]
            del it["ai_tasks"]
        elif "server_ai_type" in it:
            aitype = it["server_ai_type"] 
            input_image_rel_path, output_image_rel_path, extra = ai_config(it["server_input_cfg"]["params"][0], it["server_output_cfg"]["params"][0])
            # input_type = it["server_input_cfg"]["params"][0]["type"]
            # if input_type == "file":
            #     input_image_rel_path = it["server_input_cfg"]["params"][0]["local_path"]
            #     output_image_rel_path = it["server_output_cfg"]["params"][0]["local_path"]
            # elif input_type == "text":
            #     output_image_rel_path = it["server_output_cfg"]["params"][0]["content"]
            # extra = it["server_input_cfg"]["params"][0]["extras"]
            del it["server_ai_type"]
            del it["server_input_cfg"]
            del it["server_output_cfg"]
        else:
            continue
        if aitype not in ['humanstylized','pstyle','face','dctNetStyle','imageRestoration','bigoSilky','bigoFakeSmile',
                          'bigoCartoon','tts','inpainting','bigoBaby','bigoElderly',
                          'bigoHair','transSexual','facefun','ageTransformation','tencentFaceFusion','markiTTS']:
            print(f"========= not found aitype = {aitype}")
            processSuccess = False
            continue
        mecord_aitype = {
            "bigoCartoon": "deploy_cart_DisneyV2",
            "humanstylized": "deploy_cart_PL05",
            # "pstyle": "风格化，有几百个",
            "dctNetStyle": {
                "handdrawn": "deploy_cart_douyin",
                "artstyle": "result_cart_PL05"
            },
            # "imageRestoration": "超分",
            "bigoSilky": "deploy_cart_3DGame",
            # "bigoFakeSmile": "变笑脸",
            # "face": "人脸融合",
            # "tts": "tts",
            # "inpainting": "inpainting",
            # "bigoBaby": "变小",
            # "bigoElderly": "变老",
            # "bigoHair": "换发型",
            # "transSexual": "男变女，女变男",
            # "facefun": "图片驱动视频",
            # "tencentFaceFusion": "腾讯换脸",
            # "markiTTS": "markiTTS",
        }
        if aitype not in mecord_aitype:
            print(f"========= not support aitype = {aitype}")
            processSuccess = False
            continue
        real_output_image_path = ""
        if output_image_rel_path[0:1] == "/":
            real_output_image_path = os.path.join(root_dir, output_image_rel_path[1:])
        else:
            real_output_image_path = os.path.join(root_dir, output_image_rel_path)
        width,height = imagesize.get(real_output_image_path)
        real_era = mecord_aitype[aitype]
        if isinstance(real_era, (dict)):
            if "model" not in extra:
                print(f"========= not support aitype = {aitype}, model is empty")
                processSuccess = False
                continue
            extra_model = extra["model"]
            if extra_model not in extra:
                print(f"========= not support aitype = {aitype}, {extra_model} is empty")
                processSuccess = False
                continue
            real_era = real_era[extra_model]
        extra.update({
                    "era": real_era,
                    "musicUrl": "",
                    "batch_count": 1,
                    "batch_size": 1,
                    "cfg_scale": 7,
                    "creative_strength": 1,
                    "denoising_strength": 1,
                    "negative_prompt": "",
                    "prompt": "",
                    "restore_faces": True,
                    "sampler_index": "DPM++ SDE Karras",
                    "seed": -1,
                    "steps": 25,
                    "text_mark_url": "",
                    "type": "image",
                    "scratch": 1,
                    "user_url": ""
                })
        it["aiTasks"] = [
            {
                "serverAiType": "Light-widget",
                "serverInputCfg": [
                    input_image_rel_path
                ],
                "params": extra,
                "serverOutputCfg": [
                    {
                        "height": height,
                        "path": output_image_rel_path,
                        "width": width
                    }
                ]
            }
        ]
    return processSuccess

def genSkymedia(root, configdata, video_input):
    timeline_width, timeline_height, timeline_framerate, timelineConfig, skyInputConfig = of_to_skymedia.convert(json.dumps(configdata), 
                                                                                                                json.dumps(video_input),
                                                                                                                root, 
                                                                                                                os.path.join(root,'uiinfo.conf'))
    with open(os.path.join(root, "skyinput0.conf"), 'w', encoding='utf-8') as f:
        f.write(json.dumps(skyInputConfig))
    with open(os.path.join(root, "timeline0.sky"), 'w', encoding='utf-8') as f1:
        f1.write(json.dumps(timelineConfig))
    with open(os.path.join(root, "template.proj"), 'w', encoding='utf-8') as f1:
        template_uuid = ''.join(str(uuid.uuid4()).split('-'))
        f1.write(json.dumps({"anchor":"m_o2s","createTimestamp":"0","extra":{},"id":template_uuid,"inputConfig":"","inputList":"inputList.conf","isDebug":"0","lastChangedTimestamp":"1690376015","ofFile":"","remoteId":"","resFile":"","skyFile":"timeline0.sky","summary":"","thumb":"","title":"m_o2s","type":"Timeline","version":"1.0"}))
    with open(os.path.join(root, "output.conf"), 'w', encoding='utf-8') as f1:
        f1.write(json.dumps([{"frameRate":timeline_framerate,"height":timeline_height,"type":"video","width":timeline_width}]))
    with open(os.path.join(root, "preview.conf"), 'w', encoding='utf-8') as f1:
        f1.write(json.dumps([{"frameRate":timeline_framerate,"height":timeline_height,"type":"video","width":timeline_width}]))

def template2To3(old_template_dir, input_param, video_input):
    new_template_dir = f"{old_template_dir}_new"
    if os.path.exists(new_template_dir):
        shutil.rmtree(new_template_dir)
    shutil.copytree(old_template_dir, new_template_dir)
    if processAigc(input_param, new_template_dir) == False:
        shutil.rmtree(new_template_dir)
        raise Exception("translate fail!")
    with open(os.path.join(new_template_dir, "inputList.conf"), "w", encoding="utf-8") as c:
        json.dump(input_param, c)
    genSkymedia(new_template_dir, input_param, video_input)
    return new_template_dir