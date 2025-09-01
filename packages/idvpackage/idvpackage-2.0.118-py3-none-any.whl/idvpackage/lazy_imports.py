"""Module to handle lazy loading of heavy dependencies"""

import psutil
import os

_deepface = None
_face_recognition = None
_pycountry = None
_translator = None

def log_memory_usage(operation):
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"Memory usage after {operation}: {memory_mb:.2f} MB")

def get_deepface():
    global _deepface
    if _deepface is None:
        log_memory_usage("before DeepFace import")
        from deepface import DeepFace
        _deepface = DeepFace
        log_memory_usage("after DeepFace import")
    return _deepface

def get_face_recognition():
    global _face_recognition
    if _face_recognition is None:
        import face_recognition
        _face_recognition = face_recognition
    return _face_recognition

def get_pycountry():
    global _pycountry
    if _pycountry is None:
        import pycountry
        _pycountry = pycountry
    return _pycountry

def get_translator():
    global _translator
    if _translator is None:
        from googletrans import Translator
        _translator = Translator()
    return _translator 