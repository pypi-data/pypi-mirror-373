import os
import json
import uuid
import random
from template_generator import ffmpeg

def json_get(json_data, key, val = None):
    if key in json_data:
        return json_data[key]
    else:
        return val

class VideoEffectType:
    normalEffect = 0
    mergedVideoEffect = 1
    
class MergeVideoRect:
    def __init__(self, x=0, y=0, width=1, height=1):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __str__(self):
        return f"[x={self.x}, y={self.y}, width={self.width}, height={self.height}]"

    @classmethod
    def from_json(cls, json_data):
        return cls(**json_data)

    def to_json(self):
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height
        }

class VideoParams:
    def __init__(self, width=0, height=0, frameRate=30.0, scaleMode="aspectFit"):
        self.width = width
        self.height = height
        self.frameRate = frameRate
        self.scaleMode = scaleMode

    @classmethod
    def from_json(cls, json_data):
        return cls(width=json_data["width"],
            height=json_data["height"],
            frameRate=json_data["frameRate"],
            scaleMode=json_data["scaleMode"])

    def to_json(self):
        return {
            "width": self.width,
            "height": self.height,
            "frameRate": self.frameRate,
            # "scaleMode": self.scaleMode
            "scaleMode": "aspectFit"
        }
    
class TransEffectBean:
    def __init__(self, id, name, type, index, path, duration, ext=None):
        self.id = id
        self.name = name
        self.type = type
        self.index = index
        self.path = path
        self.duration = duration
        self.ext = ext

    @classmethod
    def from_json(cls, json_data):
        return cls(
            id=json_data["id"],
            name=json_data["name"],
            type=json_data["type"],
            index=json_data["index"],
            path=json_data["path"],
            duration=json_data["duration"],
            ext=json_get(json_data, "ext")
        )

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "index": self.index,
            "path": self.path,
            "duration": self.duration,
            "ext": self.ext,
        }

class TrackBean:
    typeVideoMute = 1
    typeAudio = "audio"
    typeVideoNotMute = 3

    def __init__(self, id, name, type, effectList=None, clipList=None, transEffectList=None, ext=None):
        self.id = id
        self.name = name
        if type == self.typeVideoMute or type == self.typeVideoNotMute:
            self.type = "video"
            if type == self.typeVideoNotMute:
                self.volume = 1
            else:
                self.volume = 0
        else:
            self.type = type
        self.effectList = [] if effectList is None else effectList
        self.clipList = [] if clipList is None else clipList
        self.transEffectList = [] if transEffectList is None else transEffectList
        self.ext = ext

    @classmethod
    def from_json(cls, json_data):
        effect_list = [
            EffectBean.from_json(effect) for effect in json_get(json_data, "effectList", [])
        ]
        clip_list = [
            ClipBean.from_json(clip) for clip in json_get(json_data, "clipList", [])
        ]
        trans_effect_list = [
            TransEffectBean.from_json(trans_effect) for trans_effect in json_get(json_data, "transEffectList", [])
        ]
        return cls(
            id=json_data["id"],
            name=json_data["name"],
            type=json_data["type"],
            effectList=effect_list,
            clipList=clip_list,
            transEffectList=trans_effect_list,
            ext=json_get(json_data, "ext")
        )

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "effects": [effect.to_json() for effect in self.effectList],
            "clipList": [clip.to_json() for clip in self.clipList],
            "transEffectList": [trans_effect.to_json() for trans_effect in self.transEffectList],
            "ext": self.ext
        }
    
class TimelineConfig:
    def __init__(self, id=0, videoParams=None, scale=1.0, trackList=None, effectList=None, ext=None, duration=0):
        self.id = id
        self.videoParams = VideoParams() if videoParams is None else videoParams
        self.scale = scale
        self.trackList = [] if trackList is None else trackList
        self.effectList = [] if effectList is None else effectList
        self.ext = ext
        self.duration = duration

    @staticmethod
    def from_string(json_str):
        json_map = json.loads(json_str)
        assert json_map is not None, f"Failed to decode json: {json_str}"
        return TimelineConfig.from_json(json_map)

    @staticmethod
    def from_file(file):
        json_str = file.read_text()
        json_map = json.loads(json_str)
        assert json_map is not None, f"Failed to decode json: {json_str}"
        return TimelineConfig.from_json(json_map)

    @classmethod
    def from_json(cls, json_data):
        video_params = VideoParams.from_json(json_get(json_data, "videoParams", {}))
        track_list = [
            TrackBean.from_json(track) for track in json_get(json_data, "trackList", [])
        ]
        effect_list = [
            EffectBean.from_json(effect) for effect in json_get(json_data, "effectList", [])
        ]
        return cls(
            id=json_get(json_data, "id", 0),
            videoParams=video_params,
            scale=json_get(json_data, "scale", 1.0),
            trackList=track_list,
            effectList=effect_list,
            ext=json_get(json_data, "ext"),
            duration=0
        )

    def to_json(self):
        return {
            "id": self.id,
            "audioDuration":self.duration,
            "audioEffects":[ ],
            "audioParams":{
                "channelCount":2,
                "format":"s16",
                "sampleRate":44100
            },
            "duration": self.duration,
            "effects": [effect.to_json() for effect in self.effectList],
            "trackList": [track.to_json() for track in self.trackList],
            "videoDuration":self.duration,
            "videoParams": self.videoParams.to_json(),
            "scale": self.scale,
            "ext": self.ext
        }
    
class EffectVideoBean:
    def __init__(self, name, videoPath=None, startTime=0, beginTime=0, endTime=-1, audioEnable=True):
        self.name = name
        self.videoPath = videoPath
        self.startTime = startTime
        self.beginTime = beginTime
        self.endTime = endTime
        self.audioEnable = audioEnable

    @classmethod
    def from_json(cls, json_data):
        return cls(
            name=json_data["name"],
            videoPath=json_get(json_data, "videoPath"),
            startTime=json_get(json_data, "startTime", 0),
            beginTime=json_get(json_data, "beginTime", 0),
            endTime=json_get(json_data, "endTime", -1),
            audioEnable=json_get(json_data, "audioEnable", True)
        )

    def to_json(self):
        return {
            "name": self.name,
            "videoPath": self.videoPath,
            "startTime": self.startTime,
            "beginTime": self.beginTime,
            "endTime": self.endTime,
            "audioEnable": self.audioEnable
        }
    
class FaceMeshConfig:
    def __init__(self, avatar_model_path="", avatar_image_path="", avatar_output_file=""):
        self.avatarModelPath = avatar_model_path
        self.avatarImagePath = avatar_image_path
        self.avatarOutputFile = avatar_output_file

    @classmethod
    def from_json(cls, json_data):
        return cls(
            avatar_model_path=json_get(json_data, "avatarModelPath", ""),
            avatar_image_path=json_get(json_data, "avatarImagePath", ""),
            avatar_output_file=json_get(json_data, "avatarOutputFile", "")
        )
    
class EffectBean:
    def __init__(self, id, name, startTimeMs, path, duration, ofParams=None,
                 videoList=None, mergedList=None, faceDetectFiles=None,
                 faceMeshConfig=None, ext=None, editable=False,
                 skyEffectInputConf=None, hasUserInput=False):
        self.id = id
        self.name = name
        self.startTimeMs = startTimeMs
        self.path = path
        self.duration = duration
        self.ofParams = ofParams
        self.videoList = [] if videoList is None else videoList
        self.mergedList = [] if mergedList is None else mergedList
        self.faceDetectFiles = [] if faceDetectFiles is None else faceDetectFiles
        self.faceMeshConfig = faceMeshConfig
        self.ext = ext
        self.editable = editable
        self.skyEffectInputConf = [] if skyEffectInputConf is None else skyEffectInputConf
        self.hasUserInput = hasUserInput

    @classmethod
    def from_json(cls, json_data):
        video_list = [
            EffectVideoBean.from_json(video) for video in json_get(json_data, "videoList", [])
        ]
        merged_list = [
            MergeVideoRect.from_json(merged) for merged in json_get(json_data, "mergedList", [])
        ]
        face_detect_files = json_get(json_data, "faceDetectFiles", [])
        face_mesh_config = FaceMeshConfig.from_json(json_get(json_data, "faceMeshConfig")) if json_get(json_data, "faceMeshConfig") else None
        sky_effect_input_conf = json_get(json_data, "skyEffectInputConf", [])

        return cls(
            id=json_data["id"],
            name=json_data["name"],
            startTimeMs=json_get(json_data, "startTimeMs", 0),
            path=json_data["path"],
            duration=json_data["duration"],
            ofParams=json_get(json_data, "ofParams"),
            videoList=video_list,
            mergedList=merged_list,
            faceDetectFiles=face_detect_files,
            faceMeshConfig=face_mesh_config,
            ext=json_get(json_data, "ext"),
            editable=json_get(json_data, "editable", False),
            skyEffectInputConf=sky_effect_input_conf,
            hasUserInput=json_get(json_data, "hasUserInput", False)
        )

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "filterClassName": "SkyOrangeEffect",
            # "extWrappers": [
            #     {
            #         "key": "SkyOFWrapper",
            #         "params": {
            #             "needsUpdateDuration": True
            #         }
            #     }
            # ],
            # "inputList": [
            #     {
            #         "path": "skymedia://background",
            #         "strategy": "auto"
            #     }
            # ],
            "startTimeMs": self.startTimeMs,
            "params": {
                "effectPath": self.path,
                "ofParams": self.ofParams,
                "type": 4,
                "cropRect": [merged.to_json() for merged in self.mergedList],
            },
            "range": {
                "beginTime": self.startTimeMs,
                "endTime": self.duration,
            },
            "videoList": [video.to_json() for video in self.videoList],
            "faceDetectFiles": self.faceDetectFiles,
            "faceMeshConfig": self.faceMeshConfig.to_json() if self.faceMeshConfig else None,
            "ext": self.ext,
            "editable": self.editable,
            "skyEffectInputConf": self.skyEffectInputConf,
            "hasUserInput": self.hasUserInput
        }

class ClipBean:
    typeVideo = "video"
    typeImage = "image"
    typeAudio = "audio"
    typeBlank = "gap"

    def __init__(self, id, name, type, path=None,
                 speed=1.0, volume=1, startTimeMs=0, trimStartTimeMs=0,
                 trimEndTimeMs=-1, effectList=None, ext=None):
        self.id = id
        self.name = name
        self.type = type
        self.path = path
        self.speed = speed
        self.volume = volume
        self.resourceID = ""
        self.startTimeMs = startTimeMs
        self.trimStartTimeMs = trimStartTimeMs
        self.trimEndTimeMs = trimEndTimeMs
        self.effectList = [] if effectList is None else effectList
        self.ext = ext

    @classmethod
    def from_json(cls, json_data):
        effect_list = [
            EffectBean.from_json(effect) for effect in json_get(json_data, "effectList", [])
        ]
        return cls(
            id=json_data["id"],
            name=json_data["name"],
            type=json_data["type"],
            path=json_get(json_data, "path"),
            speed=json_get(json_data, "speed", 1.0),
            volume=json_get(json_data, "volume", 1),
            startTimeMs=json_get(json_data, "startTimeMs", 0),
            trimStartTimeMs=json_get(json_data, "trimStartTimeMs", 0),
            trimEndTimeMs=json_get(json_data, "trimEndTimeMs", -1),
            effectList=effect_list,
            ext=json_get(json_data, "ext")
        )

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "path": self.path,
            "resourceID": self.resourceID,
            "speed": self.speed,
            "volume": self.volume,
            "startTimeMs": self.startTimeMs,
            "trimRange": {
                "beginTime": self.trimStartTimeMs,
                "endTime": self.trimEndTimeMs
            },
            "effects": [effect.to_json() for effect in self.effectList],
            "ext": self.ext
        }
    
class SkyInputConfig:
    def __init__(self, data=None):
        self.data = data if data is not None else []

    def get_res_bean_count(self):
        return len(self.data)

    @staticmethod
    def from_string(json_str):
        json_data = json.loads(json_str)
        res_list = [ResBean.from_json(data) for data in json_data]
        return SkyInputConfig(data=res_list)

    @staticmethod
    def from_file(file):
        json_str = file.read_text()
        return SkyInputConfig.from_string(json_str)

    def to_json(self):
        return [res_bean.to_json() for res_bean in self.data]


class ResBean:
    def __init__(self, id, type=None, path=None, sky_names=None, max_length=0,
                 sky_effect_track_id=None, effect_item_id=None, effect_path=None,
                 outer=None, inner=None):
        self.id = id
        self.type = type
        self.path = path
        self.skyNames = sky_names
        self.maxLength = max_length
        self.skyEffectTrackId = sky_effect_track_id
        self.effectItemId = effect_item_id
        self.effectPath = effect_path
        self.outer = outer
        self.inner = inner

    @classmethod
    def from_json(cls, json_data):
        return cls(
            id=json_data["id"],
            type=json_get(json_data, "type"),
            path=json_get(json_data, "path"),
            sky_names=json_get(json_data, "sky_names", []),
            max_length=json_get(json_data, "max_length", 0),
            sky_effect_track_id=json_get(json_data, "sky_track_id"),
            effect_item_id=json_get(json_data, "effect_item_id"),
            effect_path=json_get(json_data, "effect_path"),
            outer=json_get(json_data, "outer", []),
            inner=json_get(json_data, "inner", [])
        )

    def to_json(self):
        return {
            "id": self.id,
            "type": self.type,
            "path": self.path,
            "sky_names": self.skyNames,
            "max_length": self.maxLength,
            "sky_track_id": self.skyEffectTrackId,
            "effect_item_id": self.effectItemId,
            "effect_path": self.effectPath,
            "outer": self.outer,
            "inner": self.inner
        }

class InputBean:
    TYPE_EFFECT = "effect"
    TYPE_LYRIC_STRING = "lyric"
    TYPE_STRING = "string"
    TYPE_RESOURCE = "resource"
    TYPE_IMAGE = "image"
    TYPE_SEGMENT_IMAGE = "segmentimage"
    TYPE_HEAD_SEGMENT_IMAGE = "headsegmentimage"
    TYPE_CAT_DOG_SEGMENT_IMAGE = "catdogsegment"
    TYPE_MULTI_IMAGE = "multi_image"
    TYPE_VIDEO = "video"
    TYPE_MULTI_VIDEO = "multi_video"
    TYPE_MUSIC = "music"
    TYPE_CAMERA = "camera"
    TYPE_OPEN_CAMERA = "open_camera"
    TYPE_SMART_VIDEO = "smart_video"
    TYPE_SEQUENCE_FRAME = "sequence_frame"

    ST_NUMBER = "number"
    ST_CHINESE = "chinese"
    ST_ENGLISH = "english"
    ST_REGULAR = "regular"

    ST_DATE = "date"
    ST_TIME = "time"

    MULTILINE_OFF = 0
    MULTILINE_ON = 1

    def __init__(self, id=None, multiDir="", type="", autoSegmenting=False,
                 segmentRelativePath=None, path="", minPathCount=1, uiinfoPath="",
                 fontPath=None, fontName=None, keys=None, maxLength=0,
                 randomTextFromFile=None, title="", tips="", width=0, height=0,
                 mask=None, maskBg=None, hair=None, sky=None, clothes=None,
                 comic=None, cartoon=None, ignoreValid=False, dropdown=None,
                 stringType="string", aspectRatioType=3, multiline=0,
                 autoWrapLength=-1, group=None, autoScaleFit=False, autoScaleType="fillBlur",
                 autoTransition=False, showAd=0, numOfLock=0, needFace=False,
                 serverStyle=None, serverPath=None, needSegmentMask=False,
                 needCatDogMask=False, photoTipsUrl=None, serverAiType=None,
                 serverInputCfg=None, serverOutputCfg=None, useThirdAvatar=0,
                 imageEffect=None, selectData=None, aiTasks=None, inputParams=None):
        self._id = id
        self.multiDir = multiDir
        self.type = type
        self._autoSegmenting = autoSegmenting
        self.segmentRelativePath = segmentRelativePath
        self.path = path
        self._minPathCount = minPathCount
        self.uiinfoPath = uiinfoPath
        self.fontPath = fontPath
        self.fontName = fontName
        self.keys = keys
        self._maxLength = maxLength
        self.randomTextFromFile = randomTextFromFile
        self.title = title
        self.tips = tips
        self._width = width
        self._height = height
        self.mask = mask
        self.maskBg = maskBg
        self.hair = hair
        self.sky = sky
        self.clothes = clothes
        self.comic = comic
        self.cartoon = cartoon
        self._ignoreValid = ignoreValid
        self.dropdown = dropdown
        self.stringType = stringType
        self._aspectRatioType = aspectRatioType
        self._multiline = multiline
        self._autoWrapLength = autoWrapLength
        self.group = group
        self._autoScaleFit = autoScaleFit
        self.autoScaleType = autoScaleType
        self._autoTransition = autoTransition
        self._showAd = showAd
        self._numOfLock = numOfLock
        self._needFace = needFace
        self.serverStyle = serverStyle
        self.serverPath = serverPath
        self._needSegmentMask = needSegmentMask
        self._needCatDogMask = needCatDogMask
        self.photoTipsUrl = photoTipsUrl
        self.serverAiType = serverAiType
        self.serverInputCfg = serverInputCfg
        self._serverOutputCfg = serverOutputCfg
        self._useThirdAvatar = useThirdAvatar
        self.imageEffect = imageEffect
        self.multiPath = []
        self.aiTasks = aiTasks if aiTasks is not None else []
        self.selectData = selectData
        self.selectDataJson = None
        self.needFaceDetection = False
        self.inputParams = inputParams

    @staticmethod
    def fromJson(json):
        input_bean = InputBean()
        input_bean.path = json_get(json, "path", "")
        input_bean.showAd = json_get(json, "showAd", 0)
        input_bean.multiPath = json_get(json, "multiPath", [])
        input_bean.needFace = json_get(json, "needFace", False)
        input_bean.cartoon = json_get(json, "cartoon", None)
        input_bean.numOfLock = json_get(json, "numOfLock", 0)
        return input_bean

    def toJson(self):
        return {
            "path": self.path,
            "showAd": self.showAd,
            "multiPath": self.multiPath,
            "needFace": self.needFace,
            "cartoon": self.cartoon,
            "numOfLock": self.numOfLock
        }

    def pathExtension(self):
        if self.path:
            s = self.path.split('.')
            if len(s) > 1:
                return "." + s[-1]
        return None

    def needShowAd(self):
        return self.showAd == 1

    def multiPathShowAd(self):
        for inputMultiBean in self.multiPath:
            if inputMultiBean.needShowAd():
                return True
        return False

    def getMusicLyric(self, resourcePath):
        return resourcePath + self.path + ".oflrc"

    def getMusicSegmentFilePath(self, resourcePath):
        return resourcePath + self.path + ".segments"

    def needFaceDetect(self):
        return self.needFace or bool(self.cartoon)

    def haveNumLock(self):
        return self.numOfLock == 1
    
class Dropdown(object):
    def __init__(self, randomTextFromFile=None, name=None, path=None, videoPath=None, uiinfoPath=None):
        self.randomTextFromFile = randomTextFromFile
        self.name = name
        self.path = path
        self.videoPath = videoPath
        self.uiinfoPath = uiinfoPath
    
    @staticmethod
    def from_json(json_data):
        data = json.loads(json_data)
        return Dropdown(data.get("random_text_from_file"), data.get("name"), data.get("path"), data.get("video_path"), data.get("uiinfo_path"))
    
    def to_json(self):
        return json.dumps({
            "random_text_from_file": self.randomTextFromFile,
            "name": self.name,
            "path": self.path,
            "video_path": self.videoPath,
            "uiinfo_path": self.uiinfoPath
        })

class TextKey(object):
    def __init__(self, key=None, startIndex=0, endIndex=0, replaceValue=None):
        self.key = key
        self.startIndex = int(startIndex) if isinstance(startIndex, int) else int(startIndex) if startIndex.isdigit() else 0
        self.endIndex = int(endIndex) if isinstance(endIndex, int) else int(endIndex) if endIndex.isdigit() else 0
        self.replaceValue = replaceValue
    
    @staticmethod
    def from_json(json_data):
        data = json.loads(json_data)
        return TextKey(data.get("key"), data.get("start_index", 0), data.get("end_index", 0), data.get("replace_value"))
    
    def to_json(self):
        return json.dumps({
            "key": self.key,
            "start_index": self.startIndex,
            "end_index": self.endIndex,
            "replace_value": self.replaceValue
        })

class ImageEffect(object):
    def __init__(self, effectPath=None, backgroundPath=None, imagePath=None, locusKeyframe=None):
        self.effectPath = effectPath
        self.backgroundPath = backgroundPath
        self.imagePath = imagePath
        self.locusKeyframe = locusKeyframe
    
    @staticmethod
    def from_json(json_data):
        data = json.loads(json_data)
        return ImageEffect(data.get("effectPath"), data.get("background_path"), data.get("image_path"), data.get("locus_keyframe"))
    
    def to_json(self):
        return json.dumps({
            "effectPath": self.effectPath,
            "background_path": self.backgroundPath,
            "image_path": self.imagePath,
            "locus_keyframe": self.locusKeyframe
        })

class InputParam(object):
    def __init__(self, key=None, dataFormat=None):
        self.key = key
        self.dataFormat = dataFormat
    
    @staticmethod
    def from_json(json_data):
        data = json.loads(json_data)
        return InputParam(data.get("key"), data.get("data_format"))
    
    def to_json(self):
        return json.dumps({
            "key": self.key,
            "data_format": self.dataFormat
        })
    
resId = 0
def getResId():
    global resId
    resId += 1
    return resId

def addOtherRes(config, excludePathList, name, path):
    if not path or not path.strip() or path in excludePathList:
        return

    config.data.append(ResBean(id=getResId(), sky_names=[name], path=path, type="other"))

def addEffectRes(config, name, path):
    if not path or not path.strip():
        return

    config.data.append(ResBean(id=getResId(), sky_names=[name], path=path, type="effect"))

def addAudioRes(config, name, path):
    if not path or not path.strip():
        return

    config.data.append(ResBean(id=getResId(), sky_names=[name], path=path, type="audio"))

def addVideoRes(config, name, path):
    if not path or not path.strip():
        return

    config.data.append(ResBean(id=getResId(), sky_names=[name], path=path, type="image"))

def parseMergeRect(rect):
    if not rect:
        return None

    mergeRectList = []
    for it in rect:
        mergeRectList.append(MergeVideoRect(x=it.x, y=it.y, width=it.width, height=it.height))
    
    return mergeRectList

def sGetResAbsolutePath(resource_root_path, resource_relative_path):
    result = None
    if resource_root_path is None or resource_relative_path is None:
        result = None
    elif resource_root_path.endswith("/") and resource_relative_path.startswith("/"):
        result = (
            resource_root_path[: resource_root_path.rindex("/")]
            + resource_relative_path
        )
    elif not resource_root_path.endswith("/") and not resource_relative_path.startswith("/"):
        result = resource_root_path + "/" + resource_relative_path
    else:
        result = resource_root_path + resource_relative_path
    return result


def getEffectVideoList(uiInfoConf, inputResPath, bgVideoPath, skyInputConfig):
    videos = uiInfoConf.videoConfig.videos if uiInfoConf and uiInfoConf.videoConfig else None
    if not videos or len(videos) == 0:
        return None

    bgVideoAbsPath = sGetResAbsolutePath(inputResPath, bgVideoPath)
    result = []
    for video in videos:
        absolutePath = sGetResAbsolutePath(inputResPath, video.filePath)

        if absolutePath and absolutePath != bgVideoAbsPath:
            bean = EffectVideoBean(
                name=generateUUID(),
                videoPath=video.videoPath if video.videoPath else video.filePath,
                startTime=video.startTime,
                beginTime=video.beginTime,
                endTime=video.endTime,
                audioEnable=video.audioEnable
            )

            addVideoRes(skyInputConfig, bean.name, bean.videoPath)
            result.append(bean)
    
    return result

def getVolume(volume):
    return 1 if volume is None else max(0, min(1, volume))

def generateUUID():
    return ''.join(str(uuid.uuid4()).split('-'))

def getMediaInfo(mp4):
    mp4_width,mp4_height,bitrate,frame_rate,duration = ffmpeg.videoInfo(mp4, "")
    if mp4_width > 0:
        return frame_rate, mp4_width, mp4_height
    else:
        return 30, 544, 960

class VideoInputBean(object):
    def __init__(self, videoPath=None, videoEffect=None, multiVideoEffect=None, videoMusic=None):
        self.videoPath = videoPath
        self.videoEffect = videoEffect
        self.multiVideoEffect = multiVideoEffect
        self.videoMusic = videoMusic

    @staticmethod
    def from_json(json_data):
        videoPath = json_data['video_path']
        videoEffect = json_data['video_effect']
        multiVideoEffect = json_get(json_data, 'multi_video_effect', [])
        videoMusic = VideoMusicBean.from_json(json_data['video_music'])
        return VideoInputBean(videoPath, videoEffect, multiVideoEffect, videoMusic)

    def to_json(self):
        return {
            'video_path': self.videoPath,
            'video_effect': self.videoEffect,
            'multi_video_effect': self.multiVideoEffect,
            'video_music': self.videoMusic.to_json() if self.videoMusic is not None else None
        }


class VideoMusicBean(object):
    def __init__(self, bgMusic=None, originalMusic=None):
        self.bgMusic = bgMusic
        self.originalMusic = originalMusic

    @staticmethod
    def from_json(json_data):
        bgMusic = BgMusicBean.from_json(json_get(json_data, 'bg_music'))
        originalMusic = OriginalMusicBean.from_json(json_get(json_data, 'original_music'))
        return VideoMusicBean(bgMusic, originalMusic)

    def to_json(self):
        return {
            'bg_music': self.bgMusic.to_json() if self.bgMusic is not None else None,
            'original_music': self.originalMusic.to_json() if self.originalMusic is not None else None
        }


class BgMusicBean(object):
    def __init__(self, path=None, vol=100):
        self.path = path
        self.vol = int(vol)

    @staticmethod
    def from_json(json_data):
        path = json_get(json_data, 'path')
        vol = json_get(json_data, 'vol', 100)
        return BgMusicBean(path, vol)

    def to_json(self):
        return {
            'path': self.path,
            'vol': self.vol
        }

class OriginalMusicBean(object):
    def __init__(self, vol=100):
        self.vol = int(vol)

    @staticmethod
    def from_json(json_data):
        vol = json_get(json_data, 'vol', 100)
        return OriginalMusicBean(vol)

    def to_json(self):
        return {
            'vol': self.vol
        }
    
class MusicConfig(object):
    def __init__(self, count=0, musics=None):
        self.count = count
        self.musics = musics

    @classmethod
    def from_json(cls, json_data):
        musics = []
        for it in json_get(json_data, 'musics', []):
            musics.append(MusicEffectConfig.from_json(it))
        return cls(count=json_get(json_data, 'count', 0), musics=musics)

class MusicEffectConfig(object):
    def __init__(self, name=None, beginTime=0):
        self.name = name
        self._beginTime = beginTime

    @property
    def beginTime(self):
        return int(self._beginTime) if isinstance(self._beginTime, int) else int(self._beginTime) if self._beginTime.isdigit() else 0

    @classmethod
    def from_json(cls, json_data):
        return cls(name=json_get(json_data, 'name'), beginTime=json_get(json_data, 'beginTime', 0))
    
class VideoConfig(object):
    def __init__(self, count=0, outWidth=0, outHeight=0, videos=[], transitions=[], mergedVideo=None, cliprects=[]):
        self.count = count
        self.outWidth = outWidth
        self.outHeight = outHeight
        self.videos = videos
        self.transitions = transitions
        self.mergedVideo = mergedVideo
        self.cliprects = cliprects

    @staticmethod
    def from_json(json_data):
        count = json_get(json_data, 'count', 0)
        outWidth = json_get(json_data, 'outWidth', 0)
        outHeight = json_get(json_data, 'outHeight', 0)
        videos = json_get(json_data, 'videos', 0)
        transitions = []
        for it in json_get(json_data, 'transitions', []):
            transitions.append(GLTransition.from_json(it))
        mergedVideo = MergedVideo.from_json(json_get(json_data, "mergedVideo", {}))
        cliprects = []
        for it in json_get(json_data, 'cliprects', []):
            cliprects.append(GLRect.from_json(it))
        return VideoConfig(count, outWidth, outHeight, videos,transitions,mergedVideo,cliprects)

class VideoEffectConfig(object):
    def __init__(self, videoPath=None, startTime=0, beginTime=0, endTime=0, audioEnable=False, filePath=None):
        self.videoPath = videoPath
        self._startTime = startTime
        self._beginTime = beginTime
        self._endTime = endTime
        self.audioEnable = audioEnable
        self.filePath = filePath
    
    @property
    def startTime(self):
        return int(self._startTime) if isinstance(self._startTime, int) else int(self._startTime or 0)
    
    @property
    def beginTime(self):
        return int(self._beginTime) if isinstance(self._beginTime, int) else int(self._beginTime or 0)
    
    @property
    def endTime(self):
        return int(self._endTime) if isinstance(self._endTime, int) else int(self._endTime or 0)

class GLTransition(object):
    def __init__(self, name="", path="", duration=0):
        self.name = name
        self.path = path
        self.duration = duration
    @staticmethod
    def from_json(json_data):
        name = json_get(json_data, 'name', "")
        path = json_get(json_data, 'path', "")
        duration = json_get(json_data, 'duration', "")
        return GLTransition(name, path, duration)

class GLRect(object):
    def __init__(self, left=0, right=0, top=0, bottom=0):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom
    @staticmethod
    def from_json(json_data):
        left = json_get(json_data, 'left', 0)
        right = json_get(json_data, 'right', 0)
        top = json_get(json_data, 'top', 0)
        bottom = json_get(json_data, 'bottom', 0)
        return GLRect(left, right, top, bottom)

class MergedVideo(object):
    def __init__(self, url="", videoPath="", videoConfig=None):
        self.url = url
        self.videoPath = videoPath
        self.videoConfig = videoConfig

    @staticmethod
    def from_json(json_data):
        url = json_data['url']
        videoPath = json_get(json_data, 'videoPath', 0)
        videoConfig = MergedVideoConfig.from_json(json_get(json_data, "videoConfig", {}))
        return MergedVideo(url, videoPath, videoConfig)

class MergedVideoConfig(object):
    def __init__(self, count=0, rect=[]):
        self.count = count
        self.rect = rect
        
    @staticmethod
    def from_json(json_data):
        count = json_data['count']
        rect = []
        for it in json_get(json_data, 'rect', []):
            rect.append(MergedVideoRect.from_json(it))
        return MergedVideoConfig(count, rect)

class MergedVideoRect(object):
    def __init__(self, x=0, y=0, width=2, height=2):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @staticmethod
    def from_json(json_data):
        x = json_get(json_data, 'x', 0)
        y = json_get(json_data, 'y', 0)
        width = json_get(json_data, 'width', 0)
        height = json_get(json_data, 'height', 0)
        return MergedVideoRect(x, y, width, height)
    
class UiInfoConf(object):
    def __init__(self, actorList=None, aspect=-1, centerPointX=0.0, centerPointY=0.0, duration=0,
                 freezeDuration=0, editable=False, editableTemplate=None, frames=0, graphicsMemory=0.0,
                 hasSoundEffect=False, internalMemory=0, limitCount=0, rotate=0, textEditable=False,
                 textFilterParams=None, thumbImage=None, videoConfig=None, musicConfig=None, width=0,
                 needFrequency=False, useEffectMapping=False, multiMapping=None, needModeling=False,
                 faceDetectFile=None, faceDetectFiles=None, randomFilterParam=None, randomFilterParams=None,
                 facemeshConfig=None, paramList=None, venus=None):
        self.actorList = actorList
        self.aspect = aspect
        self.centerPointX = centerPointX
        self.centerPointY = centerPointY
        self.duration = duration
        self.freezeDuration = freezeDuration
        self.editable = editable
        self.editableTemplate = editableTemplate
        self.frames = frames
        self.graphicsMemory = graphicsMemory
        self.hasSoundEffect = hasSoundEffect
        self.internalMemory = internalMemory
        self.limitCount = limitCount
        self.rotate = rotate
        self.textEditable = textEditable
        self.textFilterParams = textFilterParams
        self.thumbImage = thumbImage
        self.videoConfig = videoConfig
        self.musicConfig = musicConfig
        self.width = width
        self.needFrequency = needFrequency
        self.useEffectMapping = useEffectMapping
        self.multiMapping = multiMapping
        self.needModeling = needModeling
        self.faceDetectFile = faceDetectFile
        self.faceDetectFiles = faceDetectFiles
        self.randomFilterParam = randomFilterParam
        self.randomFilterParams = randomFilterParams
        self.facemeshConfig = facemeshConfig
        self.paramList = paramList
        self.venus = venus

    @staticmethod
    def from_json(json_str):
        json_data = json.loads(json_str)
        return UiInfoConf(
            actorList=json_get(json_data, "actorList"),
            aspect=json_get(json_data, "aspect", -1),
            centerPointX=json_get(json_data, "centerPointX", 0.0),
            centerPointY=json_get(json_data, "centerPointY", 0.0),
            duration=json_get(json_data, "duration", 0),
            freezeDuration=json_get(json_data, "freezeDuration", 0),
            editable=json_get(json_data, "editable", False),
            editableTemplate=json_get(json_data, "editableTemplate"),
            frames=json_get(json_data, "frames", 0),
            graphicsMemory=json_get(json_data, "graphicsMemory", 0.0),
            hasSoundEffect=json_get(json_data, "hasSoundEffect", False),
            internalMemory=json_get(json_data, "internalMemory", 0),
            limitCount=json_get(json_data, "limitCount", 0),
            rotate=json_get(json_data, "rotate", 0),
            textEditable=json_get(json_data, "textEditable", False),
            textFilterParams=json_get(json_data, "textFilterParams"),
            thumbImage=json_get(json_data, "thumbImage"),
            videoConfig=VideoConfig.from_json(json_get(json_data, "videoConfig", {})),
            musicConfig=MusicConfig.from_json(json_get(json_data, "musicConfig", {})), 
            width=json_get(json_data, "width", 0),
            needFrequency=json_get(json_data, "needFrequency", False),
            useEffectMapping=json_get(json_data, "useEffectMapping", False),
            multiMapping=json_get(json_data, "multiMapping"),
            needModeling=json_get(json_data, "needModeling", False),
            faceDetectFile=json_get(json_data, "faceDetectFile"),
            faceDetectFiles=json_get(json_data, "faceDetectFiles"),
            randomFilterParam=json_get(json_data, "randomFilterParam"),
            randomFilterParams=json_get(json_data, "randomFilterParams"),
            facemeshConfig=json_get(json_data, "facemeshConfig"),
            paramList=json_get(json_data, "paramList"),
            venus=json_get(json_data, "venus")
        )

    @staticmethod
    def from_file(file):
        with open(file, "r") as f:
            json_str = f.read()
        return UiInfoConf.from_json(json_str)
    
def convert(inputList_string, videoInputBean_string, inputResPath, uiInfoConf_path):
    tempInputList = json.loads(inputList_string)
    inputList = []
    for it in tempInputList:
        inputList.append(InputBean.fromJson(it))
    videoInputBean = VideoInputBean.from_json(json.loads(videoInputBean_string))
    uiInfoConf=None
    if os.path.exists(uiInfoConf_path):
        uiInfoConf = UiInfoConf.from_file(uiInfoConf_path)
    timelineConfig = TimelineConfig()
    if uiInfoConf.duration > 0:
        timelineConfig.duration = round(uiInfoConf.duration / 1000.0, 2)
    else:
        #读取videoInputBean中effect中得duration
        with open(os.path.join(inputResPath, videoInputBean.videoEffect if videoInputBean.videoEffect[0:1] != "/" else videoInputBean.videoEffect[1:]), "r") as f:
            effect_config = json.loads(f.read())
        timelineConfig.duration = round(int(effect_config["duration"]) / 1000.0, 2)
    skyInputConfig = SkyInputConfig()

    videoEffectType = VideoEffectType.normalEffect

    mergedVideoConfig = uiInfoConf.videoConfig.mergedVideo.videoConfig if uiInfoConf and uiInfoConf.videoConfig and uiInfoConf.videoConfig.mergedVideo else None
    mergedRectList = None
    if mergedVideoConfig: # and mergedVideoConfig.count >= 2: #可能有配置秀逗，只有一个视频但是也是mergevideo
        videoEffectType = VideoEffectType.mergedVideoEffect
        mergedRectList = parseMergeRect(mergedVideoConfig.rect)

    filterParams = {}
    if uiInfoConf:
        random_value = random.randint(0, 99)
        if uiInfoConf.randomFilterParam:
            filterParams[uiInfoConf.randomFilterParam] = random_value
        if uiInfoConf.randomFilterParams:
            for rds in uiInfoConf.randomFilterParams:
                filterParams[rds] = random_value

    generateId = 0
    effectName = None
    excludePathList = []

    tmpMergedVideo = uiInfoConf.videoConfig.mergedVideo if uiInfoConf and uiInfoConf.videoConfig else None
    if tmpMergedVideo:
        rectList = tmpMergedVideo.videoConfig.rect
        if rectList and len(rectList) > 0:
            timelineConfig.videoParams.width = rectList[0].width
            timelineConfig.videoParams.height = rectList[0].height

            filepath = sGetResAbsolutePath(inputResPath, tmpMergedVideo.url)
            frameRate, width, height = getMediaInfo(filepath)
            timelineConfig.videoParams.frameRate = frameRate

    if timelineConfig.videoParams.width <= 0:
        path = sGetResAbsolutePath(inputResPath, videoInputBean.videoPath)
        frameRate, width, height = getMediaInfo(path)
        timelineConfig.videoParams.width = width
        timelineConfig.videoParams.height = height
        timelineConfig.videoParams.frameRate = frameRate

    bmMusicPath = videoInputBean.videoMusic.bgMusic.path if videoInputBean.videoMusic and videoInputBean.videoMusic.bgMusic else None
    if bmMusicPath and bmMusicPath:
        trackBean = TrackBean(
            id=generateId,
            name=generateUUID(),
            type=TrackBean.typeAudio
        )

        clipBean = ClipBean(
            id=generateId,
            type=ClipBean.typeAudio,
            name=generateUUID(),
            path=bmMusicPath,
            speed=1.0,
            volume=getVolume(videoInputBean.videoMusic.bgMusic.vol/100.0)
        )

        excludePathList.append(clipBean.path)
        addAudioRes(skyInputConfig, clipBean.name, clipBean.path)

        trackBean.clipList.append(clipBean)
        timelineConfig.trackList.append(trackBean)
        generateId += 1

    if uiInfoConf and uiInfoConf.musicConfig and uiInfoConf.musicConfig.musics:
        for musicConfig in uiInfoConf.musicConfig.musics:
            musicPath = musicConfig.name
            if musicPath and (not bmMusicPath or bmMusicPath and bmMusicPath != musicPath):
                trackBean = TrackBean(
                    id=generateId,
                    name=generateUUID(),
                    type=TrackBean.typeAudio
                )

                startTimeMs = musicConfig.beginTime if musicConfig.beginTime > 0 else 0
                clipBean = ClipBean(
                    id=generateId,
                    type=ClipBean.typeAudio,
                    name=generateUUID(),
                    path=musicPath,
                    speed=1.0,
                    volume=1,
                    startTimeMs=startTimeMs,
                    trimEndTimeMs=(timelineConfig.duration-startTimeMs)
                )

                excludePathList.append(clipBean.path)
                addAudioRes(skyInputConfig, clipBean.name, clipBean.path)

                trackBean.clipList.append(clipBean)
                timelineConfig.trackList.append(trackBean)
                generateId += 1

    bgVideoPath = videoInputBean.videoPath if videoInputBean else None
    if bgVideoPath and bgVideoPath.strip():
        trackBean = TrackBean(
            id=generateId,
            name=generateUUID(),
            type=TrackBean.typeVideoNotMute
        )
        clipBean = ClipBean(
            id=generateId,
            type=ClipBean.typeVideo,
            name=generateUUID(),
            path=bgVideoPath,
            speed=1.0,
            volume=getVolume(videoInputBean.videoMusic.originalMusic.vol/100.0)
        )
        clipBean.isLocked = True
        excludePathList.append(clipBean.path)
        addVideoRes(skyInputConfig, clipBean.name, clipBean.path)
        trackBean.clipList.append(clipBean)
        timelineConfig.trackList.append(trackBean)

        if videoEffectType == VideoEffectType.normalEffect:
            effectPath = videoInputBean.videoEffect
            if effectPath and effectPath.strip():
                effectBean = EffectBean(
                    id=generateId,
                    name=generateUUID(),
                    path=effectPath,
                    startTimeMs=0,
                    ofParams=filterParams,
                    faceMeshConfig=uiInfoConf.facemeshConfig,
                    duration=timelineConfig.duration
                )
                if uiInfoConf.faceDetectFile:
                    effectBean.faceDetectFiles = [uiInfoConf.faceDetectFile]
                else:
                    effectBean.faceDetectFiles = uiInfoConf.faceDetectFiles
                effectBean.videoList = getEffectVideoList(uiInfoConf, inputResPath, bgVideoPath, skyInputConfig)
                effectName = effectBean.name
                excludePathList.append(effectBean.path)
                addEffectRes(skyInputConfig, effectBean.name, effectBean.path)
                clipBean.effectList.append(effectBean)

        elif videoEffectType == VideoEffectType.mergedVideoEffect:
            effectPath = videoInputBean.videoEffect
            if effectPath and effectPath.strip():
                effectBean = EffectBean(
                    id=generateId,
                    name=generateUUID(),
                    path=effectPath,
                    startTimeMs=0,
                    mergedList=mergedRectList,
                    ofParams=filterParams,
                    faceMeshConfig=uiInfoConf.facemeshConfig,
                    duration=timelineConfig.duration
                )
                if uiInfoConf.faceDetectFile:
                    effectBean.faceDetectFiles = [uiInfoConf.faceDetectFile]
                else:
                    effectBean.faceDetectFiles = uiInfoConf.faceDetectFiles
                effectName = effectBean.name
                excludePathList.append(effectBean.path)
                addEffectRes(skyInputConfig, effectBean.name, effectBean.path)
                clipBean.effectList.append(effectBean)

    effName = effectName
    skyConfig = skyInputConfig
    excludeList = excludePathList

    
    for inputBean in inputList:
        addOtherRes(skyConfig, excludeList, effName, inputBean.path)
        addOtherRes(skyConfig, excludeList, effName, inputBean.serverPath)
        addOtherRes(skyConfig, excludeList, effName, inputBean.sky)
        addOtherRes(skyConfig, excludeList, effName, inputBean.hair)
        addOtherRes(skyConfig, excludeList, effName, inputBean.clothes)
        addOtherRes(skyConfig, excludeList, effName, inputBean.cartoon)
        addOtherRes(skyConfig, excludeList, effName, inputBean.comic)
        addOtherRes(skyConfig, excludeList, effName, inputBean.uiinfoPath)
        addOtherRes(skyConfig, excludeList, effName, inputBean.path + ".oflrc")

        if inputBean.needFace:
            index = inputBean.path.index('.')
            tmpPath = inputBean.path[:index] + ".landmark"
            addOtherRes(skyConfig, excludeList, effName, tmpPath)

        if inputBean._needSegmentMask or inputBean._needCatDogMask:
            index = inputBean.path.index('.')
            tmpPath = inputBean.path[:index] + "_mask.png"
            addOtherRes(skyConfig, excludeList, effName, tmpPath)

        outParams = None
        if inputBean._serverOutputCfg:
            outParams = inputBean._serverOutputCfg.params
        if outParams:
            for it in outParams:
                addOtherRes(skyConfig, excludeList, effName, it.localPath)

        for it in inputBean.multiPath:
            addOtherRes(skyConfig, excludeList, effName, it.path)
            addOtherRes(skyConfig, excludeList, effName, it.comic)
            addOtherRes(skyConfig, excludeList, effName, it.cartoon)

            if it.needFace:
                index = it.path.index('.')
                tmpPath = it.path[:index] + ".landmark"
                addOtherRes(skyConfig, excludeList, effName, tmpPath)
            
            if it.needSegmentMask:
                index = it.path.index('.')
                tmpPath = it.path[:index] + "_mask.png"
                addOtherRes(skyConfig, excludeList, effName, tmpPath)
   
    resources = []
    for t in timelineConfig.trackList:
        for c in t.clipList:
            finded = False
            for r in resources:
                if c.path == r["path"]:
                    c.resourceID = r["id"]
                    finded = True
                    break
            if finded == False:
                res = {
                    "id" : generateUUID(),
                    "path" : c.path
                }
                c.resourceID = res["id"]
                resources.append(res)

    real_timelineConfig = {
            "buildSDKVersion": "1.2.2.0-[2022-08-03 17:38]",
            "resourceList": resources,
            "skyversion": "1.0",
            "timeUnit": "seconds",
            "timeline": timelineConfig.to_json()
        }
    return timelineConfig.videoParams.width, timelineConfig.videoParams.height, timelineConfig.videoParams.frameRate, real_timelineConfig, skyInputConfig.to_json()



# timeline_width, timeline_height, timeline_framerate, timelineConfig, skyInputConfig = convert('[{"id":"1","width":544,"height":960,"path":"/res/_0014_resize-28229.png","group":"A","auto_scale_fit":true,"need_face":false,"title":"Replace Photo","tips":"Please replace the photo","auto_scale_type":"fillCenter","type":"image"},{"id":"2","width":544,"height":960,"path":"/res/_0019_u4E0Bu8F7D-28329.png","group":"A","auto_scale_fit":true,"need_face":false,"title":"Replace Photo","tips":"Please replace the photo","auto_scale_type":"fillCenter","type":"image"},{"id":"3","width":544,"height":960,"path":"/res/_0015_resize-28129.png","group":"A","auto_scale_fit":true,"need_face":false,"title":"Replace Photo","tips":"Please replace the photo","auto_scale_type":"fillCenter","type":"image"},{"id":"4","width":544,"height":960,"path":"/res/d.png","group":"A","auto_scale_fit":true,"need_face":false,"title":"Replace Photo","tips":"Please replace the photo","auto_scale_type":"fillCenter","type":"image"},{"id":"5","width":544,"height":960,"path":"/res/dd.png","group":"A","auto_scale_fit":true,"need_face":false,"title":"Replace Photo","tips":"Please replace the photo","auto_scale_type":"fillCenter","type":"image"},{"id":"6","width":544,"height":960,"path":"/res/a.png","group":"A","auto_scale_fit":true,"need_face":false,"title":"Replace Photo","tips":"Please replace the photo","auto_scale_type":"fillCenter","type":"image"},{"id":"7","width":544,"height":960,"path":"/res/aa.png","group":"A","auto_scale_fit":true,"need_face":false,"title":"Replace Photo","tips":"Please replace the photo","auto_scale_type":"fillCenter","type":"image"},{"id":"8","width":544,"height":960,"path":"/res/aaa.png","group":"A","auto_scale_fit":true,"need_face":false,"title":"Replace Photo","tips":"Please replace the photo","auto_scale_type":"fillCenter","type":"image"},{"id":"9","width":544,"height":960,"path":"/res/c.png","group":"A","auto_scale_fit":true,"need_face":false,"title":"Replace Photo","tips":"Please replace the photo","auto_scale_type":"fillCenter","type":"image"},{"id":"10","width":544,"height":960,"path":"/res/cc.png","group":"A","auto_scale_fit":true,"need_face":false,"title":"Replace Photo","tips":"Please replace the photo","auto_scale_type":"fillCenter","type":"image"},{"id":"11","width":544,"height":960,"path":"/res/b.png","group":"A","auto_scale_fit":true,"need_face":false,"title":"Replace Photo","tips":"Please replace the photo","auto_scale_type":"fillCenter","type":"image"},{"id":"12","width":544,"height":960,"path":"/res/bb.png","group":"A","auto_scale_fit":true,"need_face":false,"title":"Replace Photo","tips":"Please replace the photo","auto_scale_type":"fillCenter","type":"image"},{"id":"13","width":544,"height":960,"path":"/res/bbb.png","group":"A","auto_scale_fit":true,"need_face":false,"title":"Replace Photo","tips":"Please replace the photo","auto_scale_type":"fillCenter","type":"image"},{"id":"14","width":544,"height":960,"path":"/res/e.png","group":"A","auto_scale_fit":true,"need_face":false,"title":"Replace Photo","tips":"Please replace the photo","auto_scale_type":"fillCenter","type":"image"},{"id":"15","width":544,"height":960,"path":"/res/ee.png","group":"A","auto_scale_fit":true,"need_face":false,"title":"Replace Photo","tips":"Please replace the photo","auto_scale_type":"fillCenter","type":"image"},{"id":"16","width":544,"height":960,"path":"/res/f.png","group":"A","auto_scale_fit":true,"need_face":false,"title":"Replace Photo","tips":"Please replace the photo","auto_scale_type":"fillCenter","type":"image"},{"id":"17","width":544,"height":960,"path":"/res/ff.png","group":"A","auto_scale_fit":true,"need_face":false,"title":"Replace Photo","tips":"Please replace the photo","auto_scale_type":"fillCenter","type":"image"},{"id":"18","width":544,"height":960,"path":"/res/fff.png","group":"A","auto_scale_fit":true,"need_face":false,"title":"Replace Photo","tips":"Please replace the photo","auto_scale_type":"fillCenter","type":"image"},{"id":"19","type":"music","path":"/res/music2.mp3","max_length":10100,"title":"Replace Music","tips":"Using default music","auto_scale_fit":"false"}]','{"video_path":"/res/mergedVideo.mp4","video_effect":"/effect0.ofeffect","video_music":{"bg_music":{"path":"","vol":100},"original_music":{"vol":100}}}','E:\\666666666666666666', 'E:\\666666666666666666\\uiinfo.conf')

# with open(os.path.join('E:\\666666666666666666', "inputList.conf"), 'w', encoding='utf-8') as f:
#     f.write(json.dumps(skyInputConfig))
# with open(os.path.join('E:\\666666666666666666', "timeline0.sky"), 'w', encoding='utf-8') as f1:
#     f1.write(json.dumps(timelineConfig))
# with open(os.path.join('E:\\666666666666666666', "template.proj"), 'w', encoding='utf-8') as f1:
#     template_uuid = ''.join(str(uuid.uuid4()).split('-'))
#     f1.write(json.dumps({"anchor":"m_o2s","createTimestamp":"0","extra":{},"id":template_uuid,"inputConfig":"","inputList":"inputList.conf","isDebug":"0","lastChangedTimestamp":"1690376015","ofFile":"","remoteId":"","resFile":"","skyFile":"timeline0.sky","summary":"","thumb":"","title":"demo","type":"Timeline","version":"1.0"}))
# with open(os.path.join('E:\\666666666666666666', "output.conf"), 'w', encoding='utf-8') as f1:
#     f1.write(json.dumps([{"frameRate":timeline_framerate,"height":timeline_height,"type":"video","width":timeline_width}]))
# with open(os.path.join('E:\\666666666666666666', "preview.conf"), 'w', encoding='utf-8') as f1:
#     f1.write(json.dumps([{"frameRate":timeline_framerate,"height":timeline_height,"type":"video","width":timeline_width}]))