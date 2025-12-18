import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog  # 导入 simpledialog 用于输入学生姓名
import os
import webbrowser

import cv2
import numpy as np
from PIL import Image, ImageTk
import threading
from action.body import BodyRecognition  # 导入 BodyRecognition 类
from emotion.emotion.real_time_video import emotionrecognition
from login import LoginFrame
from ttkbootstrap import Style
from DB.table_fun import MainApp as TableApp
from self_test.stu_self_test import SDSQuestionnaire

# 导入 micro_report.py 中的 analyze_student_data 函数
from report.micro_report import analyze_student_data

class MainWindow:
    def __init__(self, root, username=None, user_type=None):
        self.root = root
        self.root.title("学业预警学生心理状态评估与预警系统")
        self.root.geometry("1200x800")

        # 配置样式
        self.style = ttk.Style()
        self.style.theme_use('clam')  # 使用 'clam' 主题

        self.username = username
        self.user_type = user_type

        if not self.username or not self.user_type:
            self.show_login_frame()
        else:
            self.show_main_interface()

    def show_login_frame(self):
        # 清除现有内容
        for widget in self.root.winfo_children():
            widget.destroy()

        # 创建登录界面并居中
        login_frame = LoginFrame(self.root, self.on_login_success)
        login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def show_main_interface(self):
        # 清除现有内容
        for widget in self.root.winfo_children():
            widget.destroy()

        self.create_top_navbar()
        self.create_left_sidebar()
        self.create_right_content_area()

    def on_login_success(self, username, user_type):
        self.username = username
        self.user_type = user_type
        self.show_main_interface()

    def create_top_navbar(self):
        navbar = ttk.Frame(self.root, padding="3 3 12 12", relief=tk.RAISED)
        navbar.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        system_name = ttk.Label(navbar, text="学业预警学生心理状态评估与预警系统", font=("微软雅黑", 18))
        system_name.pack(side=tk.LEFT, padx=20)

        btn_relogin = ttk.Button(navbar, text="重新登录", command=self.relogin)
        btn_relogin.pack(side=tk.LEFT, padx=5)

        btn_exit = ttk.Button(navbar, text="退出", command=self.exit_program)
        btn_exit.pack(side=tk.LEFT, padx=5)

        user_label = ttk.Label(navbar, text=f"登录用户: {self.username}", font=("Arial", 12))
        user_label.pack(side=tk.RIGHT, padx=20)

    def create_left_sidebar(self):
        sidebar = ttk.Frame(self.root, padding="3 3 12 12", relief=tk.RAISED)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, expand=True, padx=10, pady=10, anchor='w')

        # 创建树状结构的框架
        treeview_frame = ttk.Frame(sidebar)
        treeview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建 Treeview
        self.treeview = ttk.Treeview(treeview_frame, show="tree")
        self.treeview.pack(fill=tk.BOTH, expand=True)

        # 根据用户类型添加树节点
        if self.user_type == '0':
            self.create_info_management_treeview()
        elif self.user_type == '2':
            self.create_student_self_test_treeview()
        else:
            self.create_teacher_treeview()

    def create_info_management_treeview(self):
        # 添加信息管理节点
        info_management = self.treeview.insert('', 'end', text='信息管理', open=True)
        self.treeview.insert(info_management, 'end', text='创建', tags=('create',))
        self.treeview.insert(info_management, 'end', text='修改', tags=('modify',))
        self.treeview.insert(info_management, 'end', text='查询', tags=('query',))

        # 绑定树节点的选择事件
        self.treeview.tag_bind('create', '<ButtonRelease-1>', lambda e: self.open_create())
        self.treeview.tag_bind('modify', '<ButtonRelease-1>', lambda e: self.open_modify())
        self.treeview.tag_bind('query', '<ButtonRelease-1>', lambda e: self.open_query())

    def create_student_self_test_treeview(self):
        # 添加学生心理自测节点
        self_test = self.treeview.insert('', 'end', text='学生心理自测', tags=('self_test',))
        self.treeview.tag_bind('self_test', '<ButtonRelease-1>', lambda e: self.open_psychological_ttest())

    def create_teacher_treeview(self):
        # 添加教师功能节点
        teacher_functions = self.treeview.insert('', 'end', text='微表情模块', open=True)
        self.treeview.insert(teacher_functions, 'end', text='微表情识别', tags=('psychological_assessment',))

        psychological_functions = self.treeview.insert('', 'end', text='心理状态模块', open=True)
        self.treeview.insert(psychological_functions, 'end', text='心理状态评估', tags=('psychological_report',))
        self.treeview.insert(psychological_functions, 'end', text='心理状态预警', tags=('psychological_alert',))

        action_functions = self.treeview.insert('', 'end', text='行为预警模块', open=True)
        self.treeview.insert(action_functions, 'end', text='危险行为识别', tags=('student_behavior_data',))
        self.treeview.insert(action_functions, 'end', text='危险行为预警', tags=('dangerous_behavior_alert',))

        # 绑定树节点的选择事件
        self.treeview.tag_bind('psychological_assessment', '<ButtonRelease-1>', lambda e: self.open_recognition_assessment())
        self.treeview.tag_bind('psychological_report', '<ButtonRelease-1>', lambda e: self.open_psychological_report())
        self.treeview.tag_bind('psychological_alert', '<ButtonRelease-1>', lambda e: self.open_psychological_alert())
        self.treeview.tag_bind('student_behavior_data', '<ButtonRelease-1>', lambda e: self.open_student_behavior_data())
        self.treeview.tag_bind('dangerous_behavior_alert', '<ButtonRelease-1>', lambda e: self.open_dangerous_behavior_alert())

    def create_right_content_area(self):
        self.right_frame = ttk.Frame(self.root, padding="3 3 12 12", relief=tk.RAISED, width=600)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.display_welcome_message(self.right_frame)

    def clear_right_frame(self):
        """清空右侧区域"""
        for widget in self.right_frame.winfo_children():
            widget.destroy()
        self.right_frame.configure(style="Custom.TFrame")

    def add_close_button(self):
        """在右侧区域添加关闭按钮"""
        close_button = ttk.Button(self.right_frame, text="关闭", command=self.show_main_interface)
        close_button.pack(side=tk.BOTTOM, pady=10)

    def open_create(self):
        """打开创建功能"""
        self.clear_right_frame()
        # 在右侧区域显示创建功能
        self.table_app = TableApp(self.right_frame)
        self.table_app.show_create()
        self.add_close_button()  # 添加关闭按钮

    def open_modify(self):
        """打开修改功能"""
        self.clear_right_frame()
        # 在右侧区域显示修改功能
        self.table_app = TableApp(self.right_frame)
        self.table_app.show_update()
        self.add_close_button()  # 添加关闭按钮

    def open_query(self):
        """打开查询功能"""
        self.clear_right_frame()
        # 在右侧区域显示查询功能
        self.table_app = TableApp(self.right_frame)
        self.table_app.show_delete()
        self.add_close_button()  # 添加关闭按钮

    def display_welcome_message(self, parent):
        """显示欢迎信息"""
        welcome_label = ttk.Label(parent, text="欢迎使用学业预警学生心理状态评估与预警系统", font=("Arial", 24))
        welcome_label.pack(pady=70, padx=50)

        description_label = ttk.Label(parent, text="请选择左侧菜单中的功能模块进行操作", font=("Arial", 14))
        description_label.pack()

    def open_recognition_assessment(self):
        """打开微表情识别功能"""
        self.clear_right_frame()

        # 创建输入姓名的区域
        self.name_frame = ttk.Frame(self.right_frame)
        self.name_frame.pack(pady=10)

        name_label = ttk.Label(self.name_frame, text="请输入姓名:", font=("Arial", 12))
        name_label.pack(side=tk.LEFT, padx=5)

        self.name_entry = ttk.Entry(self.name_frame, width=20)
        self.name_entry.pack(side=tk.LEFT, padx=5)

        submit_button = ttk.Button(self.name_frame, text="提交", command=self.start_video_capture)
        submit_button.pack(side=tk.LEFT, padx=5)

        self.add_close_button()  # 添加关闭按钮

    def start_video_capture(self):
        """启动视频捕获"""
        user_name = self.name_entry.get()
        if not user_name:
            return  # 如果用户没有输入姓名，直接返回

        # 隐藏输入姓名的区域
        self.name_frame.pack_forget()

        # 创建视频显示区域
        self.video_label = ttk.Label(self.right_frame)
        self.video_label.pack(fill=tk.BOTH, expand=True)

        # 启动视频捕获和识别功能
        self.body_recognition = BodyRecognition()
        self.emotion_recognition = emotionrecognition(user_name)  # 创建情感识别实例
        self.stop_thread = False
        self.thread = threading.Thread(target=self.update_video, args=(user_name,))
        self.thread.start()

    def update_video(self, user_name):
        """更新视频帧并显示在右侧区域"""
        cap = cv2.VideoCapture(0)  # 打开摄像头
        try:
            while not self.stop_thread:
                ret, frame = cap.read()  # 读取视频帧
                if not ret:
                    break  # 如果读取失败，退出循环

                # Step 1: 处理帧以进行行为识别（身体动作）
                frame = self.body_recognition.process_frame(frame)

                # Step 2: 处理帧以进行情绪识别（面部表情）
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # 将帧转换为灰度图像
                faces = self.emotion_recognition.face_detection.detectMultiScale(gray_frame, scaleFactor=1.1,
                                                                                 minNeighbors=5, minSize=(30, 30),
                                                                                 flags=cv2.CASCADE_SCALE_IMAGE)  # 检测人脸

                if len(faces) > 0:
                    # 提取最大的人脸区域
                    faces = sorted(faces, reverse=True, key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))[0]
                    (fX, fY, fW, fH) = faces
                    roi = gray_frame[fY:fY + fH, fX:fX + fW]  # 提取人脸区域
                    roi = cv2.resize(roi, (64, 64))  # 调整大小为模型输入尺寸
                    roi = roi.astype("float") / 255.0  # 归一化到 [0, 1] 范围

                    # 增加通道维度，使其形状为 (1, 64, 64, 1)
                    roi = np.expand_dims(roi, axis=-1)  # 增加通道维度
                    roi = np.expand_dims(roi, axis=0)  # 增加 batch 维度

                    # 情绪预测
                    with self.emotion_recognition.graph.as_default():  # 使用模型加载时的图
                        emotion_preds = self.emotion_recognition.emotion_classifier.predict(roi)[0]
                    emotion_label = self.emotion_recognition.EMOTIONS[np.argmax(emotion_preds)]  # 获取最高概率的情绪标签
                    emotion_prob = np.max(emotion_preds) * 100  # 获取最高概率值

                    # 在帧上绘制检测到的情绪标签
                    cv2.putText(frame, emotion_label, (fX, fY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
                    cv2.rectangle(frame, (fX, fY), (fX + fW, fY + fH), (0, 0, 255), 2)  # 绘制人脸框

                # Step 3: 将帧转换为 RGB 格式并更新 Tkinter 中的视频标签
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # 将帧从 BGR 转换为 RGB
                img = Image.fromarray(frame)  # 将帧转换为 PIL 图像
                imgtk = ImageTk.PhotoImage(image=img)  # 将 PIL 图像转换为 Tkinter 兼容的图像

                # 使用 Tkinter 的 after 方法更新视频显示
                if self.video_label.winfo_exists():
                    self.video_label.after(0, self.update_video_label, imgtk)

        finally:
            # 释放摄像头资源
            cap.release()

    def update_video_label(self, imgtk):
        """更新 video_label 的图像"""
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)

    def stop_video(self):
        """停止视频捕获"""
        self.stop_thread = True
        if hasattr(self, 'thread'):
            self.thread.join()

        if hasattr(self, 'video_label') and self.video_label.winfo_exists():
            self.video_label.destroy()

    def open_psychological_report(self):
        """打开心理状态报告功能"""
        self.clear_right_frame()

        # 创建一个输入框供用户输入学生姓名
        self.name_frame = ttk.Frame(self.right_frame)
        self.name_frame.pack(pady=10)

        name_label = ttk.Label(self.name_frame, text="请输入学生姓名:", font=("Arial", 12))
        name_label.pack(side=tk.LEFT, padx=5)

        self.name_entry = ttk.Entry(self.name_frame, width=20)
        self.name_entry.pack(side=tk.LEFT, padx=5)

        submit_button = ttk.Button(self.name_frame, text="提交", command=self.generate_psychological_alert_report)
        submit_button.pack(side=tk.LEFT, padx=5)

        self.add_close_button()  # 添加关闭按钮

    def generate_psychological_alert_report(self):
        """生成心理状态预警报告"""
        student_name = self.name_entry.get()
        if not student_name:
            return  # 如果用户没有输入姓名，直接返回

        # 调用 analyze_student_data 函数生成报告
        analyze_student_data(student_name)

        # 显示报告生成成功的提示
        success_label = ttk.Label(self.right_frame, text=f"已生成 {student_name} 的心理状态预警报告", font=("Arial", 14))
        success_label.pack(pady=20)

    def open_student_behavior_data(self):
        """打开学生行为数据功能"""
        self.clear_right_frame()
        # 在这里添加学生行为数据功能的实现
        self.add_close_button()  # 添加关闭按钮

    def open_psychological_alert(self):
        """打开心理状态预警功能"""
        self.clear_right_frame()

        # 加载报告
        # 在 gui.py 中修改路径
        report_dir = r'E:\AiProject\project\report_data'
        self.reports = self.load_reports(report_dir)

        # 筛选条件框架
        filter_frame = ttk.LabelFrame(self.right_frame, text="筛选条件")
        filter_frame.pack(fill="x", padx=10, pady=10)

        # 筛选类型选择
        filter_type_label = ttk.Label(filter_frame, text="筛选类型:")
        filter_type_label.grid(row=0, column=0, padx=5, pady=5)

        filter_type_var = tk.StringVar()
        filter_type_combobox = ttk.Combobox(filter_frame, textvariable=filter_type_var, values=["姓名", "风险程度"])
        filter_type_combobox.grid(row=0, column=1, padx=5, pady=5)
        filter_type_combobox.current(0)

        # 筛选值输入
        filter_value_label = ttk.Label(filter_frame, text="筛选值:")
        filter_value_label.grid(row=0, column=2, padx=5, pady=5)

        filter_value_var = tk.StringVar()
        filter_value_entry = ttk.Entry(filter_frame, textvariable=filter_value_var)  # 默认使用 Entry
        filter_value_entry.grid(row=0, column=3, padx=5, pady=5)

        # 动态更新筛选值输入方式
        def update_filter_values(*args):
            filter_type = filter_type_var.get()
            if filter_type == "风险程度":
                # 如果是风险程度，使用 Combobox 并填充预定义值
                if hasattr(filter_frame, 'filter_value_entry'):
                    filter_frame.filter_value_entry.destroy()  # 销毁 Entry
                filter_value_combobox = ttk.Combobox(filter_frame, textvariable=filter_value_var,
                                                     values=["Normal", "Need Attention", "High Risk"])
                filter_value_combobox.grid(row=0, column=3, padx=5, pady=5)
                filter_value_combobox.current(0)  # 默认选择第一个值
                filter_frame.filter_value_combobox = filter_value_combobox  # 保存 Combobox 引用
            elif filter_type == "姓名":
                # 如果是姓名，使用 Entry 组件
                if hasattr(filter_frame, 'filter_value_combobox'):
                    filter_frame.filter_value_combobox.destroy()  # 销毁 Combobox
                filter_value_entry = ttk.Entry(filter_frame, textvariable=filter_value_var)
                filter_value_entry.grid(row=0, column=3, padx=5, pady=5)
                filter_frame.filter_value_entry = filter_value_entry  # 保存 Entry 引用

        filter_type_var.trace_add("write", update_filter_values)  # 监听筛选类型变化

        # 筛选按钮
        def on_filter():
            filter_type = filter_type_var.get()
            filter_value = filter_value_var.get()

            if not filter_value:
                tk.messagebox.showwarning("警告", "请输入筛选值！")
                return

            filtered_reports = self.filter_reports(self.reports, filter_type, filter_value)
            self.update_report_list(filtered_reports)

        filter_button = ttk.Button(filter_frame, text="筛选", command=on_filter)
        filter_button.grid(row=0, column=4, padx=5, pady=5)

        # 报告列表框架
        report_list_frame = ttk.LabelFrame(self.right_frame, text="报告列表")
        report_list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 报告列表
        self.report_listbox = tk.Listbox(report_list_frame)
        self.report_listbox.pack(fill="both", expand=True, padx=5, pady=5)

        # 初始加载所有报告
        self.update_report_list(self.reports)

        # 打开报告按钮
        def on_open_report():
            selected_index = self.report_listbox.curselection()
            if not selected_index:
                tk.messagebox.showwarning("警告", "请选择一个报告！")
                return

            selected_report = self.reports[selected_index[0]]
            self.open_report(selected_report["path"])

        open_button = ttk.Button(self.right_frame, text="打开报告", command=on_open_report)
        open_button.pack(pady=10)

    def update_report_list(self, reports):
        """更新报告列表"""
        self.report_listbox.delete(0, tk.END)
        for report in reports:
            self.report_listbox.insert(tk.END, f"{report['filename']} - {report['risk_level']}")

    def load_reports(self, report_dir):
        """加载所有报告文件。"""
        reports = []
        for root, dirs, files in os.walk(report_dir):
            for file in files:
                if file.endswith(".html"):
                    report_path = os.path.join(root, file)
                    # 提取姓名和风险等级
                    try:
                        # 处理文件名中的空格
                        file_parts = file.replace("]", "_").split("_")  # 将 "] " 替换为 "_"，然后按 "_" 分割
                        risk_level = file_parts[0].strip("[")  # 提取风险等级
                        name = file_parts[1]  # 提取姓名
                        reports.append({
                            "path": report_path,
                            "filename": file,
                            "name": name,
                            "risk_level": risk_level
                        })
                    except IndexError:
                        print(f"警告：报告文件名格式不正确，跳过文件: {file}")
        return reports

    def filter_reports(self, reports, filter_type, filter_value):
        """根据筛选条件过滤报告。"""
        filtered_reports = []
        for report in reports:
            if filter_type == "姓名" and filter_value.lower() in report["name"].lower():
                filtered_reports.append(report)
            elif filter_type == "风险程度" and filter_value == report["risk_level"]:
                filtered_reports.append(report)
        return filtered_reports

    def open_report(self, report_path):
        """打开选中的报告。"""
        webbrowser.open(report_path)

    def open_dangerous_behavior_alert(self):
        """打开危险行为预警功能"""
        self.clear_right_frame()
        # 在这里添加危险行为预警功能的实现
        self.add_close_button()  # 添加关闭按钮

    def open_psychological_ttest(self):
        """打开心理自测功能"""
        self.clear_right_frame()

        # 创建 Canvas 和 Scrollbar
        self.canvas = tk.Canvas(self.right_frame, bg="#f0f0f0")
        self.scrollbar = ttk.Scrollbar(self.right_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        # 绑定滚动事件
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # 将 Canvas 和 Scrollbar 放置到右侧区域
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # 设置 scrollable_frame 的宽度
        self.scrollable_frame.update_idletasks()  # 更新布局
        self.canvas.config(width=self.right_frame.winfo_width())  # 设置 Canvas 的宽度为右侧区域的宽度

        # 调用 SDSQuestionnaire 并嵌入到 scrollable_frame 中
        self.sds_questionnaire = SDSQuestionnaire(self.scrollable_frame)

        self.add_close_button()  # 添加关闭按钮

    def relogin(self):
        self.show_login_frame()

    def exit_program(self):
        self.stop_video()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()