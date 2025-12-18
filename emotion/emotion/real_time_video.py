import tkinter as tk
from tkinter import simpledialog, messagebox
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
import imutils
import tensorflow as tf
from keras.models import load_model
import cv2
import numpy as np
import csv
import time
import os

class emotionrecognition:
    def __init__(self, user_name):
        # 定义全局图
        self.graph = tf.Graph()

        # 在全局图中加载模型
        with self.graph.as_default():
            # 加载数据和图像的相关路径
            self.detection_model_path = r'E:\AiProject\project\emotion\emotion\haarcascade_files\haarcascade_frontalface_default.xml'
            self.emotion_model_path = r'E:\AiProject\project\emotion\emotion\models\_mini_XCEPTION.102-0.66.hdf5'

            # 加载模型
            self.face_detection = cv2.CascadeClassifier(self.detection_model_path)  # 人脸检测模型
            self.emotion_classifier = load_model(self.emotion_model_path, compile=False)  # 表情识别模型
            self.EMOTIONS = ["angry", "disgust", "scared", "happy", "sad", "surprised", "neutral"]  # 表情分类

        # 初始化保存CSV文件的目录
        self.output_dir = r'E:\AiProject\project\emotion\emotion\micro_data'
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # 调用弹窗获取用户姓名
        self.name = user_name

        # 获取当前时间戳，为每次会话创建新的CSV文件
        self.timestamp = time.strftime('%Y-%m-%d_%H-%M-%S')
        self.csv_file_path = os.path.join(self.output_dir, f'{self.name}_{self.timestamp}.csv')

        # 以追加模式打开CSV文件
        self.csv_file = open(self.csv_file_path, mode='a', newline='')
        self.fieldnames = ['timestamp', 'emotion', 'probability']
        self.writer = csv.DictWriter(self.csv_file, fieldnames=self.fieldnames)

        # 检查CSV文件是否为空，如果为空，则写入表头
        self.csv_file.seek(0, 2)  # 移动到文件末尾
        if self.csv_file.tell() == 0:
            self.writer.writeheader()

