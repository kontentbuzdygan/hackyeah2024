import cv2 
from deepface import DeepFace

def get_facial_frame_facial_expression(path):
    return DeepFace.analyze(cv2.imread(path), actions = ['emotion'])[0]["dominant_emotion"]

