import os,sys
import hashlib

def main():
    rootDir = os.path.dirname(os.path.abspath(__file__))
    for root,dirs,files in os.walk(rootDir):
        for file in files:
            if file.find(".") <= 0:
                continue
            name = file[0:file.index(".")]
            ext = file[file.index("."):]
            if ext == ".zip.py":
                fpath = os.path.join(root, file)
                with open(fpath, 'rb') as fp:
                        file_data = fp.read()
                file_md5 = hashlib.md5(file_data).hexdigest()
                print(f"{fpath} -> {file_md5}")
        if root != files:
            break
    
if __name__ == '__main__':
    main()
