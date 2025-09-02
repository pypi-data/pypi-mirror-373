import sys
import os
import subprocess
import json
import random
import logging
import shutil
from PIL import Image
from pathlib import Path

from template_generator import binary
from template_generator import aigc_input
from template_generator import convertor

def getCommandResult(cmd):
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, timeout=300)
        if result.returncode == 0:
            return result.stdout.decode(encoding="utf8", errors="ignore").replace("\n","").strip()
        else:
            return ""
    except subprocess.CalledProcessError as e:
        logging.info(f"getCommandResult fail {e}")
        return ""
    
def getBinary(searchPath, useHardwareEncode=True):
    binaryPath = ""
    if sys.platform == "win32":
        binaryPath = os.path.join(binary.skymediaPath(searchPath), "TemplateProcess.exe")
    elif sys.platform == "linux":
        binaryPath = os.path.join(binary.skymediaPath(searchPath), "TemplateProcess")
        if os.path.exists(binaryPath):
            cmd = subprocess.Popen(f"chmod 755 {binaryPath}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            while cmd.poll() is None:
                print(cmd.stdout.readline().rstrip().decode('utf-8'))
        #check env
        if os.path.exists("/usr/lib/libskycore.so") == False:
            print(f"=== begin setup env")
            setupShell = os.path.join(binary.skymediaPath(searchPath), "setup.sh")
            if os.path.exists(setupShell):
                print(f"=== sh {setupShell}")
                getCommandResult(f"sh {setupShell}")
            if os.path.exists("/usr/lib/libskycore.so") == False:
                raise Exception("linux environment error")
        if len(getCommandResult("echo $XDG_SESSION_TYPE")) <= 0 and len(getCommandResult("echo $DISPLAY")) <= 0 and useHardwareEncode:
            #no x11 or wayland , check Xvfb
            displayShell = os.path.join(binary.skymediaPath(searchPath), "display.sh")
            if os.path.exists(displayShell):
                print(f"=== sh {displayShell}")
                cmd1 = subprocess.Popen(f"sh {displayShell}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                while cmd1.poll() is None:
                    print(cmd1.stdout.readline().rstrip().decode('utf-8'))
    elif sys.platform == "darwin":
        binaryPath = os.path.join(binary.skymediaPath(searchPath), "TemplateProcess")
        if os.path.exists(binaryPath):
            cmd = subprocess.Popen(f"chmod 755 {binaryPath}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            while cmd.poll() is None:
                print(cmd.stdout.readline().rstrip().decode('utf-8'))
            
    if os.path.exists(binaryPath):
        return os.path.dirname(binaryPath), os.path.basename(binaryPath)
    else:
        return "", ""
    
# def transcode(f):
#     try:
#         file_name = Path(f).name
#         ext = file_name[file_name.index("."):].lower()
#         if ext in [".webp"]:
#             image = Image.open(f, "r")
#             format = image.format
#             if format.lower() == "webp":
#                 newFile = f"{f}.png"
#                 image.save(newFile, "png")
#                 image.close()
#                 return True, newFile
#     except:
#         return False, f
#     return False, f
    
# def resetInput(data, tmp_file_cache):
#     newInput = []
#     for s in data["input"]:
#         needDeleteSrc, newSrc = transcode(s)
#         if needDeleteSrc:
#             tmp_file_cache.append(newSrc)
#         newInput.append(newSrc)
#     data["input"] = newInput
    
def checkTemplateIs30(tid_dir):
    finded = False
    projFile = os.path.join(tid_dir, "template.proj")
    if os.path.exists(projFile) == True:
        for root,dirs,files in os.walk(tid_dir):
            for file in files:
                name, ext = os.path.splitext(file)
                if ext == ".sky":
                    finded = True
                    break
            if root != files:
                break
    return finded

def mediaType(path):
    file_name = Path(path).name
    ext = file_name[file_name.index("."):].lower()
    if ext in [".jpg", ".png", ".jpeg", ".bmp", ".webp", ".gif"]:
        return "image"
    elif ext in [".mp4",".mov",".avi",".wmv",".mpg",".mpeg",".rm",".ram",".flv",".swf",".ts"]:
        return "video"
    elif ext in [".mp3",".aac",".wav",".wma",".cda",".flac",".m4a",".mid",".mka",".mp2",".mpa",".mpc",".ape",".ofr",".ogg",".ra",".wv",".tta",".ac3",".dts"]:
        return "music"
    else:
        return "image"
    
def resByType(inputs, type, begin_idx=0):
    for p in inputs[begin_idx:]:
        if mediaType(p) == type:
            begin_idx+=1
            return p
        begin_idx+=1

def copyInputFile(src, dst):
    file_type = mediaType(dst)
    if file_type == "image":
        image1 = Image.open(src)
        image2 = Image.open(dst)
        width1, height1 = image1.size
        width2, height2 = image2.size
        scale_ratio = min(width2/width1, height2/height1)
        new_width = int(width1 * scale_ratio)
        new_height = int(height1 * scale_ratio)
        resized_image1 = image1.resize((new_width, new_height))
        left = (new_width - width2) // 2
        top = (new_height - height2) // 2
        right = left + width2
        bottom = top + height2
        cropped_image1 = resized_image1.crop((left, top, right, bottom))
        image1.close()
        image2.close()
        cropped_image1.save(dst)
        cropped_image1.close()
    elif file_type == "video":
        return 
    elif file_type == "music":
        return 
    else:
        return 
    
def findInputList(dir, name=None):
    if name:
        input_list_path0 = os.path.join(dir, name)
        if os.path.exists(input_list_path0):
            with open(input_list_path0, 'r', encoding='utf-8') as f:
                return json.loads(f.read())
    input_list_path = os.path.join(dir, "inputList.conf")
    if os.path.exists(input_list_path):
        with open(input_list_path, 'r', encoding='utf-8') as f:
            return json.loads(f.read())
    input_list_path1 = os.path.join(dir, "skyinput0.conf")
    if os.path.exists(input_list_path1):
        with open(input_list_path1, 'r', encoding='utf-8') as f:
            return json.loads(f.read())
    return None

def resetTemplate(data, searchPath):
    templateNameToPath(data, searchPath)
    if checkTemplateIs30(data["template"]) == False and len(data["input"])>0 and data.get("input_param",None):
        #create 3.0 template with 2.0 template
        new_template = convertor.template2To3(data["template"], data["input_param"], data["video_input"])
        data["template"] = new_template
        input_config = findInputList(new_template, "")
        for item in input_config:
            if item.get("need_face", False) == True or item["type"] not in ["image","music"] or item.get("need_segment_mask", False) == True:
                raise Exception("cannot process vnn input")
            real_path = item["path"]
            if real_path[0:1] == "/":
                real_path = real_path[1:]
            dst_file = os.path.join(new_template, real_path)
            src_file = resByType(data["input"], item["type"])
            if src_file:
                copyInputFile(src_file, dst_file)
        data["input"] = []


def templateNameToPath(data, searchPath):
    template_path = data["template"]
    if os.path.exists(template_path):
        return
    #template info with server
    from template_res import template as template_res_search
    server_templates = template_res_search.listTemplate(searchPath, template_path)
    if len(server_templates) > 0:
        data["template"] = server_templates[0]["path"]
        data.update(server_templates[0])
        return
    raise Exception(f"template {template_path} not found")
    
def isAdaptiveSize(data):
    template_path = data["template"]
    templateName = os.path.basename(template_path)
    if "template" in templateName or templateName == "AIGC_1":
        return True
    return False

def isAdaptiveDuration(data):
    template_path = data["template"]
    templateName = os.path.basename(template_path)
    if "template" in templateName or templateName == "AIGC_1":
        return True
    return False

def maybeMesa(useHardwareEncode=True, useHardwareDecode=True):
    if sys.platform == "linux":
        if len(getCommandResult("echo $XDG_SESSION_TYPE")) <= 0 and len(getCommandResult("echo $DISPLAY")) <= 0:
            #no (x11 or wayland) and (xvfb not found)
            return True
        elif useHardwareEncode:
            return False
        else:
            return True
    else:
        return False

def maybeSoftWare(useHardwareEncode=True, useHardwareDecode=True):
    if sys.platform == "linux":
        if os.path.exists("/usr/lib/x86_64-linux-gnu/libnvcuvid.so") and os.path.exists("/usr/lib/x86_64-linux-gnu/libnvidia-encode.so") and useHardwareEncode:
            return False
        else:
            return True
    else:
        return False
    
def realCommand(cmd):
    if sys.platform == "linux":
        return "./" + " ".join(cmd)
    if sys.platform == "darwin":
        return "./" + " ".join(cmd)
    else:
        return cmd
    
def executeTemplate(data, searchPath="", useAdaptiveSize=False, useAdaptiveDuration=False, useHardware=False, printLog=True, oneVideoTimeout=240, useHardwareEncode=True, useHardwareDecode=True):
    binary_dir, binary_file = getBinary(searchPath, useHardwareEncode)
    if len(binary_dir) <= 0:
        raise Exception("binary not found")

    tmp_file_cache = []
    tmp_dir_cache = []
    output_path = ""
    output_cnt = 1
    if isinstance(data, (dict)):
        output_path = data["output"]
        # resetInput(data, tmp_file_cache)
        resetTemplate(data, searchPath)
        useAdaptiveSize = useAdaptiveSize or isAdaptiveSize(data)
        useAdaptiveDuration = useAdaptiveDuration or isAdaptiveDuration(data)
        aigc_input.preProcessAIGC(data,tmp_file_cache,tmp_dir_cache)
    elif isinstance(data, (list)):
        for it in data:
            output_path = it["output"]
            # resetInput(it, tmp_file_cache)
            resetTemplate(it, searchPath)
            useAdaptiveSize = useAdaptiveSize or isAdaptiveSize(it)
            useAdaptiveDuration = useAdaptiveDuration or isAdaptiveDuration(it)
            aigc_input.preProcessAIGC(it,tmp_file_cache,tmp_dir_cache)
            output_cnt+=1

    tempDir = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(tempDir) == False:
        os.makedirs(tempDir)
    inputArgs = os.path.join(tempDir, f"{random.randint(100,99999999)}.in")
    tmp_file_cache.append(inputArgs)
    if os.path.exists(inputArgs):
        os.remove(inputArgs)
    with open(inputArgs, 'w') as f:
        json.dump(data, f)

    extArgs = []
    #--adaptiveSize
    if useAdaptiveSize:
        extArgs += ["--adaptiveSize", "true"]
    #--adaptiveDuration
    if useAdaptiveDuration:
        extArgs += ["--adaptiveDuration", "true"]
    #--fontDir
    fontPath = binary.fontPath(searchPath)
    if os.path.exists(fontPath):
        extArgs += ["--fontDir", fontPath]
    #--subEffectDir
    subPath = binary.subEffectPath(searchPath)
    if os.path.exists(subPath):
        extArgs += ["--subEffectDir", subPath]
    #--gpu
    if sys.platform == "linux" and maybeMesa(useHardwareEncode, useHardwareDecode):
        extArgs += ["--call_mesa"]
    if sys.platform == "linux":
        #linux校验一下nvidia在不在，不在的话忽略入参强制软解软编码
        if maybeSoftWare(useHardwareEncode, useHardwareDecode):
            extArgs += ["--call_software_encoder"]
            extArgs += ["--call_software_decoder"]
    else:
        if useHardwareEncode == False:
            extArgs += ["--call_software_encoder"]
        if useHardwareDecode == False:
            extArgs += ["--call_software_decoder"]

    command = [binary_file, "--config", inputArgs] + extArgs
    command = realCommand(command)
    if printLog:
        print(f"=== executeTemplate => {command}")
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=binary_dir, timeout=oneVideoTimeout*output_cnt)
    if result.returncode == 0:
        for t in tmp_file_cache:
            os.remove(t)
        for t in tmp_dir_cache:
            shutil.rmtree(t)
        if printLog:
            print(result.stdout.decode(encoding="utf8", errors="ignore"))
        #check one output
        if os.path.exists(output_path) == False:
            logging.info(f"output file not found")
            raise Exception("output file not found")
    else:
        for t in tmp_file_cache:
            os.remove(t)
        for t in tmp_dir_cache:
            shutil.rmtree(t)
        err_msg = result.stdout.decode(encoding="utf8", errors="ignore")
        logging.info(f"executeTemplate err {err_msg}")
        if printLog:
            print(err_msg)
        raise Exception(f"template process exception!")
    
def generateTemplate(config, output, searchPath, useHardware=False, printLog=True, useHardwareEncode=True, useHardwareDecode=True): 
    binary_dir, binary_file = getBinary(searchPath, useHardwareEncode)
    if len(binary_dir) <= 0:
        raise Exception("binary not found")
    
    if os.path.exists(config) == False:
        raise Exception("input config not exist")

    if os.path.exists(output) == False:
        os.makedirs(output)

    command = [binary_file, "--project", config ,"-y", output]
    command = realCommand(command)
    if printLog:
        print(f"=== generateTemplate => {command}")
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=binary_dir, timeout=120)
    if result.returncode != 0:
        err_msg = result.stdout.decode(encoding="utf8", errors="ignore")
        logging.info(f"generateTemplate err {err_msg}")
        if printLog:
            print(err_msg)
        raise Exception(f"generate template exception!")
    else:
        if printLog:
            print(result.stdout.decode(encoding="utf8", errors="ignore"))
  
def templateToVideo(path):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    temp_dir = os.path.join(current_dir, ".temp")
    
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    try:
        if os.path.isdir(path):
            template_dir = path
        else:
            import zipfile
            if not os.path.exists(path):
                raise Exception(f"Template file not found: {path}")
            
            extract_dir = os.path.join(temp_dir, "extracted_template")
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir)
            os.makedirs(extract_dir)
            
            # 解压zip文件
            with zipfile.ZipFile(path, "r") as zipf:
                zipf.extractall(extract_dir)
            
            template_dir = extract_dir
        
        output_file = os.path.join(current_dir, "output.mp4")
        if os.path.exists(output_file):
            os.remove(output_file)
        executeTemplate( {
            "input":[ ],
            "template":template_dir,
            "params":{},
            "output":output_file,
            }, searchPath="", useAdaptiveSize=False,
                        useAdaptiveDuration=False, useHardware=False, printLog=False, 
                        oneVideoTimeout=240, useHardwareEncode=True, useHardwareDecode=True)
        return output_file
    except Exception as e:
        raise e
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
def decrypt(path, searchPath):
    binary_dir, binary_file = getBinary(searchPath)
    if len(binary_dir) <= 0:
        raise Exception("binary not found")

    command = [binary_file, "--decrypt", path]
    command = realCommand(command)
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=binary_dir)
    if result.returncode == 0:
        return 
    else:
        raise Exception(f"decrypt process exception!")
