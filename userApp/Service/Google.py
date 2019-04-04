# -*- coding: utf-8 -*-
import os, hashlib
from pydub import AudioSegment
import pydub.scipy_effects
import Silence
import config


def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)

#Перевод аудио в текст при помощи Google.Speech
def recognize_v1p1beta1(FILENAME, pacient = True):
    channel = -1.0
    if(pacient == "False" or pacient == False):
        channel = 1.0
    sound = AudioSegment.from_file(FILENAME)
    sound = Silence.remove(sound.pan(channel))
    sound = sound.set_channels(1)
    n = 0
    section=30000
    length = int(round((len(sound) / section) + 0.5))
    result = ""
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/cloud/google_key.json"
    from google.cloud import speech_v1p1beta1 as speech
    client = speech.SpeechClient()
    for i in range(length):
        print("Google process...")
        first_half = sound[n:n + section]
        first_half = first_half.high_pass_filter(500, order=1)
        first_half = first_half.low_pass_filter(700, order=1)
        first_half = first_half + 10
        first_half = match_target_amplitude(first_half, -20.0)
        n += section
        m = hashlib.md5()
        m.update(str(first_half))
        tmp_file = str(m.hexdigest()) + ".flac"

        first_half.export(config.TMP_PATH + tmp_file, format="flac")

        with open(config.TMP_PATH + tmp_file, "rb") as f:
            data = f.read()

        audio = speech.types.RecognitionAudio(content=data)
        config_ = speech.types.RecognitionConfig(
            encoding=speech.enums.RecognitionConfig.AudioEncoding.FLAC,
            language_code='ru-RU',
            enable_automatic_punctuation=True,
            model='Default')

        response = client.recognize(config_, audio)

        for item in response.results:
            result += item.alternatives[0].transcript + " "
        os.remove(config.TMP_PATH + tmp_file)
    return result
