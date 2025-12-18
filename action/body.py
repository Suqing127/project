import cv2
import mediapipe as mp
import time
import csv
import os
import math
from datetime import datetime

class BodyRecognition:
    def __init__(self):
        # 初始化 MediaPipe 姿态检测模型
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils

        # 用于追踪负面情绪持续时间的变量
        self.negative_emotion_start_time = None
        self.total_negative_duration = 0
        self.total_duration = 0

        # 用于追踪特定手势持续时间的变量
        self.arms_crossed_start_time = None
        self.arms_crossed_duration = 0

        self.defensive_start_time = None
        self.defensive_duration = 0

        self.hands_trembling_start_time = None
        self.hands_trembling_duration = 0

        self.hands_clenched_start_time = None
        self.hands_clenched_duration = 0

    def calculate_angle(self, a, b, c):
        """计算三点之间的角度"""
        ang = math.degrees(math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0]))
        return ang + 360 if ang < 0 else ang

    def calculate_distance(self, a, b):
        """计算两点之间的距离"""
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    def save_to_csv(self, file_path, total_duration, total_negative_duration, negative_emotion_percentage,
                   arms_crossed_duration, defensive_duration, hands_trembling_duration, hands_clenched_duration):
        """将结果保存到 CSV 文件"""
        try:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    "Total Duration (s)",
                    "Negative Emotion Duration (s)",
                    "Negative Emotion Percentage (%)",
                    "Arms Crossed Duration (s)",
                    "Defensive Duration (s)",
                    "Hands Trembling Duration (s)",
                    "Hands Clenched Duration (s)"
                ])
                writer.writerow([
                    total_duration,
                    total_negative_duration,
                    negative_emotion_percentage,
                    arms_crossed_duration,
                    defensive_duration,
                    hands_trembling_duration,
                    hands_clenched_duration
                ])
            print(f"Results saved to {file_path}")
        except Exception as e:
            print(f"Failed to save data to {file_path}. Error: {e}")

    def process_frame(self, frame):
        """处理每一帧视频并返回处理后的帧"""
        # 将帧水平翻转，进行自拍模式显示
        frame = cv2.flip(frame, 1)

        # 将图像转换为 RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)

        # 如果检测到姿势
        if results.pose_landmarks:
            # 绘制关键点连接线
            self.mp_drawing.draw_landmarks(frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

            # 获取关键点坐标（使用姿势关键点）
            landmarks = results.pose_landmarks.landmark

            # 获取左右肩膀、肘部、手腕的坐标（x, y）
            right_shoulder = (int(landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].x * frame.shape[1]),
                             int(landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].y * frame.shape[0]))
            right_elbow = (int(landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW].x * frame.shape[1]),
                          int(landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW].y * frame.shape[0]))
            right_wrist = (int(landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST].x * frame.shape[1]),
                          int(landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST].y * frame.shape[0]))

            left_shoulder = (int(landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER].x * frame.shape[1]),
                            int(landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER].y * frame.shape[0]))
            left_elbow = (int(landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW].x * frame.shape[1]),
                         int(landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW].y * frame.shape[0]))
            left_wrist = (int(landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST].x * frame.shape[1]),
                         int(landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST].y * frame.shape[0]))

            # 计算肩膀、肘部和手腕之间的角度
            right_arm_angle = self.calculate_angle(right_shoulder, right_elbow, right_wrist)
            left_arm_angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)

            # 计算手腕与肩膀之间的距离
            right_wrist_shoulder_distance = self.calculate_distance(right_wrist, right_shoulder)
            left_wrist_shoulder_distance = self.calculate_distance(left_wrist, left_shoulder)

            # 定义不同焦虑相关手势的规则
            is_arms_crossed = (right_arm_angle < 90 and left_arm_angle < 90)  # 双臂交叉
            is_defensive = (right_wrist_shoulder_distance < 50 and left_wrist_shoulder_distance < 50)  # 防御手势
            is_hands_trembling = (abs(right_wrist[0] - left_wrist[0]) > 20)  # 手颤抖
            is_hands_clenched = (self.calculate_distance(right_wrist, left_wrist) < 30)  # 握紧双拳

            # 记录每个手势的持续时间
            if is_arms_crossed:
                if self.arms_crossed_start_time is None:
                    self.arms_crossed_start_time = time.time()
                else:
                    self.arms_crossed_duration += time.time() - self.arms_crossed_start_time
                    self.arms_crossed_start_time = None

            if is_defensive:
                if self.defensive_start_time is None:
                    self.defensive_start_time = time.time()
                else:
                    self.defensive_duration += time.time() - self.defensive_start_time
                    self.defensive_start_time = None

            if is_hands_trembling:
                if self.hands_trembling_start_time is None:
                    self.hands_trembling_start_time = time.time()
                else:
                    self.hands_trembling_duration += time.time() - self.hands_trembling_start_time
                    self.hands_trembling_start_time = None

            if is_hands_clenched:
                if self.hands_clenched_start_time is None:
                    self.hands_clenched_start_time = time.time()
                else:
                    self.hands_clenched_duration += time.time() - self.hands_clenched_start_time
                    self.hands_clenched_start_time = None

            # 综合所有规则来检测负面情绪
            is_negative_emotion = is_arms_crossed or is_defensive or is_hands_trembling or is_hands_clenched

            # 记录负面情绪的持续时间
            if is_negative_emotion:
                if self.negative_emotion_start_time is None:
                    self.negative_emotion_start_time = time.time()
            else:
                if self.negative_emotion_start_time is not None:
                    self.total_negative_duration += time.time() - self.negative_emotion_start_time
                    self.negative_emotion_start_time = None

            # 绘制双臂的矩形框（蓝色）
            cv2.rectangle(frame, right_shoulder, right_wrist, (255, 0, 0), 2)  # 蓝色
            cv2.rectangle(frame, left_shoulder, left_wrist, (255, 0, 0), 2)  # 蓝色

        # 更新总持续时间
        self.total_duration += 1 / 30  # 假设视频帧率为 30 FPS

        return frame

    def run(self, user_name):
        """运行视频捕获和处理逻辑"""
        # 获取当前时间并格式化
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 生成文件名
        output_dir = r"E:\AiProject\project\action\data"
        csv_file_name = f"{user_name}_{current_time}.csv"
        csv_file_path = os.path.join(output_dir, csv_file_name)

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 打开摄像头
        cap = cv2.VideoCapture(0)
        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                # 处理帧
                frame = self.process_frame(frame)

                # 显示帧
                cv2.imshow("Pose Estimation", frame)

                # 按 'q' 键退出程序
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        finally:
            # 释放视频捕获设备并关闭窗口
            cap.release()
            cv2.destroyAllWindows()

            # 计算负面情绪所占的百分比
            if self.total_duration > 0:
                negative_emotion_percentage = (self.total_negative_duration / self.total_duration) * 100
                print(f"Total Duration: {self.total_duration:.2f} seconds")
                print(f"Negative Emotion Duration: {self.total_negative_duration:.2f} seconds")
                print(f"Negative Emotion Percentage: {negative_emotion_percentage:.2f}%")
                print(f"Arms Crossed Duration: {self.arms_crossed_duration:.2f} seconds")
                print(f"Defensive Duration: {self.defensive_duration:.2f} seconds")
                print(f"Hands Trembling Duration: {self.hands_trembling_duration:.2f} seconds")
                print(f"Hands Clenched Duration: {self.hands_clenched_duration:.2f} seconds")

                # 保存结果到 CSV 文件
                self.save_to_csv(
                    csv_file_path,
                    self.total_duration,
                    self.total_negative_duration,
                    negative_emotion_percentage,
                    self.arms_crossed_duration,
                    self.defensive_duration,
                    self.hands_trembling_duration,
                    self.hands_clenched_duration
                )
            else:
                print("No data recorded.")