import json
import os
import subprocess
import sys
from datetime import datetime, timedelta

import speech_recognition as sr

from ..logging import setup_logging

logger = setup_logging(__file__)

def convert_to_wav(file_path):
    new_file_path = file_path + ".wav"
    wav_cmd = 'ffmpeg -y -i "' + file_path + '" -ar 48000 "' + new_file_path + '"'
    subprocess.call(wav_cmd, shell=True)
    return new_file_path

def get_recognized_text(file_path):
    r = sr.Recognizer()
    wav_converted_file_path = convert_to_wav(file_path)
    r_file = sr.AudioFile(wav_converted_file_path)
    with r_file as source:
        audio = r.record(source)
    try:
        return r.recognize_google(audio, language="de-DE"), wav_converted_file_path
    except sr.UnknownValueError as e:
        return None, wav_converted_file_path
