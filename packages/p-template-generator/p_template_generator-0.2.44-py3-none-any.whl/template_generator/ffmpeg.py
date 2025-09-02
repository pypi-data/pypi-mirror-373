import sys
import os
import subprocess, re
import platform

from template_generator import binary

def ffmpegBinary(searchPath):        
    binaryFile = ""
    if sys.platform == "win32":
        binaryFile = os.path.join(binary.ffmpegPath(searchPath), "win", "ffmpeg.exe")
    elif sys.platform == "linux":
        machine = platform.machine().lower()
        if machine == "x86_64" or machine == "amd64":
            machine = "amd64"
        else:
            machine = "arm64"
        binaryFile = os.path.join(binary.ffmpegPath(searchPath), "linux", machine, "ffmpeg")
    elif sys.platform == "darwin":
        machine = platform.machine().lower()
        if machine == "x86_64" or machine == "amd64":
            machine = "X86"
        else:
            machine = "arm64"
        binaryFile = os.path.join(binary.ffmpegPath(searchPath), "darwin", machine, "ffmpeg")
    
    if len(binaryFile) > 0 and sys.platform != "win32":
        cmd = subprocess.Popen(f"chmod 755 {binaryFile}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        while cmd.poll() is None:
            print(cmd.stdout.readline().rstrip().decode('utf-8'))
            
    if os.path.exists(binaryFile):
        return os.path.dirname(binaryFile), os.path.basename(binaryFile)
    else:
        return "", ""

def realCommand(binary_dir, cmd):
    if sys.platform == "linux":
        cmd[0] = "./" + cmd[0]
        return cmd
    if sys.platform == "darwin":
        cmd[0] = os.path.join(binary_dir, cmd[0])
        # return "./" + " ".join(cmd)
        return cmd
    else:
        return cmd
    
def videoInfo(file,searchPath):
    w = 0
    h = 0
    bitrate = 0
    fps = 0
    duration = 0

    binary_dir, binary_file = ffmpegBinary(searchPath)
    command = [binary_file,"-i",file]
    command = realCommand(binary_dir, command)
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, cwd=binary_dir, timeout=10)
        str = ""
        if result.returncode == 0:
            str = result.stdout.decode(encoding="utf8", errors="ignore")
        else:
            str = result.stderr.decode(encoding="utf8", errors="ignore")
        if str.find("yuv420p") > 0 and str.find("fps,") > 0:
            s1 = str[str.find("yuv420p"):str.find("fps,")+3].replace(' ', "")
            s1_split = s1.split(",")
            for s1_it in s1_split:
                s2 = s1_it
                if s2.find("[") > 0:
                    s2 = s2[0:s2.find("[")]
                if s2.find("(") > 0:
                    s2 = s2[0:s2.find("[")]
                if s2.find("x") > 0:
                    sizes = s2.split("x")
                    if len(sizes) > 1:
                        w = sizes[0]
                        h = sizes[1]
                if s2.find("kb/s") > 0:
                    bitrate = s2[0:s2.find("kb/s")]
                if s2.find("fps") > 0:
                    fps = s2[0:s2.find("fps")]
        if str.find("Duration:") > 0 and str.find(", start:") > 0:
            s2 = str[str.find("Duration:")+9:str.find(", start:")].replace(' ', "")
            s2_split = s2.split(":")
            if len(s2_split) > 2:
                hour = float(s2_split[0])
                min = float(s2_split[1])
                second  = float(s2_split[2])
                duration = hour*3600 + min*60 + second
    except subprocess.CalledProcessError as e:
        print("====================== process error ======================")
        print(e)
        print("======================      end      ======================")
    return float(w),float(h),float(bitrate),float(fps),float(duration)

def audioInfo(file,searchPath=""):
    sample = 0
    duration = 0
    bitrate = 0

    binary_dir, binary_file = ffmpegBinary(searchPath)
    command = [binary_file,"-i",file]
    command = realCommand(binary_dir, command)
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, cwd=binary_dir)
        str = ""
        if result.returncode == 0:
            str = result.stdout.decode(encoding="utf8", errors="ignore")
        else:
            str = result.stderr.decode(encoding="utf8", errors="ignore")
            
        duration_match = re.search(r"Duration: (\d{2}:\d{2}:\d{2}\.\d{2})", str)
        if duration_match:
            s2 = duration_match.group(1)
            s2_split = s2.split(":")
            if len(s2_split) > 2:
                hour = float(s2_split[0])
                min = float(s2_split[1])
                second  = float(s2_split[2])
                duration = hour*3600 + min*60 + second

        # Extract sample rate
        sample_rate_match = re.search(r"(\d+) Hz", str)
        if sample_rate_match:
            sample = int(sample_rate_match.group(1))

        # Extract bitrate
        bitrate_match = re.search(r"bitrate: (\d+) kb/s", str)
        if bitrate_match:
            bitrate = int(bitrate_match.group(1))
    except subprocess.CalledProcessError as e:
        print("====================== process error ======================")
        print(e)
        print("======================      end      ======================")
    return float(sample),float(bitrate),float(duration)

def process(args, searchPath):
    binary_dir, binary_file = ffmpegBinary(searchPath)
    command = [binary_file] + args
    command = realCommand(binary_dir, command)
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, cwd=binary_dir)
        if result.returncode == 0:
            print(result.stdout.decode(encoding="utf8", errors="ignore"))
            return True
        else:
            print("====================== ffmpeg error ======================")
            print(result.stderr.decode(encoding="utf8", errors="ignore"))
            print("======================     end      ======================")
    except subprocess.CalledProcessError as e:
        print("====================== process error ======================")
        print(e)
        print("======================      end      ======================")
    return False