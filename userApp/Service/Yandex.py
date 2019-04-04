# -*- coding: utf-8 -*-
from urllib2 import urlopen
import urllib2
import json, os, hashlib
import config, Silence
from pydub import AudioSegment

#Перевод аудио в текст при помощи Yandex.Speech
def recognize(FILENAME, pacient = True):
    channel = -1.0
    if(pacient == "False" or pacient == False):
        channel = 1.0
    sound = AudioSegment.from_file(FILENAME)
    sound = Silence.remove(sound.pan(channel))
    sound = sound.set_channels(1)
    n = 0
    length = int(round((len(sound) / 50000) + 0.5))
    FOLDER_ID = config.FOLDER_ID
    IAM_TOKEN = getIam()

    result = ""

    for i in range(length):
        first_half = sound[n:n + 50000]
        n += 50000

        m = hashlib.md5()
        m.update(str(first_half))
        tmp_file = str(m.hexdigest()) + ".opus"

        first_half.export(config.TMP_PATH + tmp_file, format="opus")

        with open(config.TMP_PATH + tmp_file, "rb") as f:
            data = f.read()

        params = "&".join([
            "topic=general",
            "folderId=%s" % FOLDER_ID,
            "lang=ru-RU"
        ])
        url = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize/?%s" % params
        req = urllib2.Request(url.encode('UTF-8'), data=data)
        req.add_header("Authorization", "Bearer %s" % IAM_TOKEN)
        # req.add_header("Transfer-Encoding", "chunked")
        # url.add_header("Content-Type", "audio/x-mpeg-3")

        responseData = urlopen(req).read().decode('UTF-8')
        decodedData = json.loads(responseData)

        if decodedData.get("error_code") is None:
            result += decodedData.get("result") + " "
        else:
            result += ""
        os.remove(config.TMP_PATH + tmp_file)

    return result

#Получение Iam токена для Yandex
def getIam():
    data = '{\"yandexPassportOauthToken\":\"'+config.OAUTH+'\"}'.encode("utf-8")
    url = urllib2.Request("https://iam.api.cloud.yandex.net/iam/v1/tokens", data=data)
    url.add_header("Content-Type", "application/json")
    responseData = urlopen(url).read().decode('UTF-8')
    decodedData = json.loads(responseData)
    return (decodedData['iamToken'])

