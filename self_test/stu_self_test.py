import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import csv

# 定义SDS量表类
class SDSQuestionnaire:
    def __init__(self, parent):
        self.parent = parent

        # 使用 ttk.Style 设置背景颜色
        self.style = ttk.Style()
        self.style.configure("Custom.TFrame", background="#f0f0f0")  # 定义样式
        self.parent.configure(style="Custom.TFrame")  # 应用样式

        # 设置按钮的字体样式
        self.style.configure("Submit.TButton", font=("Arial", 14))

        # 显示量表说明
        self.show_instructions()

        # 创建自测窗口内容
        self.create_widgets()

    def show_instructions(self):
        # 显示量表使用说明
        instructions = (
            "下面有20条文字，请仔细阅读每一条，把意思弄明白，"
            "然后根据您最近一星期的实际情况，在适当的方格里画一勾(√)。",
            "每一条文字后有4个方格，分别代表没有或很少时间，少部分时间，"
            "相当多时间或全部时间。"
        )
        # 使用wraplength属性使文字在窗口内自动换行
        label = ttk.Label(self.parent, text='\n'.join(instructions), justify="left", wraplength=1100, font=("Arial", 12))
        label.grid(row=0, column=0, columnspan=4, pady=10)

    def create_widgets(self):
        # 姓名输入框
        ttk.Label(self.parent, text="请输入姓名:", font=("Arial", 12)).grid(row=1, column=0, pady=10, padx=10,
                                                                            sticky="w")
        self.name_entry = ttk.Entry(self.parent, font=("Arial", 12), width=25)
        self.name_entry.grid(row=1, column=1, pady=10)

        # SDS量表问题列表
        self.questions = [
            "1. 我觉得闷闷不乐，情绪低沉（忧郁）。",
            "2. 我觉得一天中早晨最好（晨重晚轻）。",
            "3. 我一阵阵哭出来或觉得想哭（易哭）。",
            "4．我晚上睡眠不好(睡眠障碍)。",
            "5．我吃得跟平常一样多(食欲减退)。",
            "6.我与异性密切接触时和以往一样感到愉快(性兴趣减退)。",
            "7.我发觉我的体重在下降(体重减轻)。",
            "8.我有便秘的苦恼(便秘)。",
            "9．我心跳比平常快(心悸)。",
            "10.我无缘无故地感到疲乏(易倦)。",
            "11.我的头脑跟平常-一样清楚(思考困难)。",
            "12．我觉得做经常做的事并没有困难(能力减退)。",
            "13．我觉得不安而平静不下来(不安)。",
            "14，我对将来抱有希望(绝望)。",
            "15．我比平常容易生气激动(易激惹)。",
            "16.我觉得做出决定是容易的(决断困难)。",
            "17．我觉得自己是个有用的人,有人需要我(无用感)。",
            "18.我的生活过得很有意思(生活空虚感)。",
            "19．我认为如果我死了,别人会过得好些(无价值感)。",
            "20.平常感兴趣的事我仍然感兴趣(兴趣丧失)。",
        ]

        # 评分数据
        self.scores = {}

        # 为每个问题创建评分按钮
        self.buttons = []  # 存储所有按钮，便于更新颜色
        for i, question in enumerate(self.questions):
            ttk.Label(self.parent, text=question, font=("Arial", 12), anchor="w", width=45).grid(row=i + 2, column=0,
                                                                                                 pady=5, padx=10,
                                                                                                 sticky="w")

            # 使按钮均匀分布在4个列中
            score_buttons = []
            for score in range(1, 5):
                button = ttk.Button(self.parent, text=str(score), width=2,
                                    command=lambda q=i, s=score: self.set_score(q, s))  # 使用 ttk.Button
                score_buttons.append(button)

            # 将每行的按钮均匀分布
            for idx, button in enumerate(score_buttons):
                button.grid(row=i + 2, column=idx + 1, padx=(2, 2), pady=2, sticky="ew")  # 调整 padx 和 pady

            self.scores[i] = None  # 初始化每个问题的分数为None
            self.buttons.append(score_buttons)  # 将按钮保存到列表中

        # 配置列，使得每一列宽度均等
        for col in range(1, 5):
            self.parent.grid_columnconfigure(col, weight=1, uniform="equal")

        # 提交按钮
        submit_button = ttk.Button(self.parent, text="提交", style="Submit.TButton", command=self.submit_test, width=15)
        submit_button.grid(row=22, columnspan=5, pady=30)

    def set_score(self, question_index, score):
        """设置指定问题的得分并改变按钮颜色"""
        # 恢复所有按钮为默认颜色
        for button in self.buttons[question_index]:
            button.configure(style="TButton")  # 恢复默认样式

        # 设置选中按钮为绿色
        self.buttons[question_index][score - 1].configure(style="Green.TButton")

        # 更新分数
        self.scores[question_index] = score

    def submit_test(self):
        """提交测试并计算总分"""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("输入错误", "请输入您的姓名")
            return

        # 确保所有问题都已评分
        if any(score is None for score in self.scores.values()):
            messagebox.showerror("评分错误", "请完成所有问题的评分")
            return

        # 反向评分题的标记
        reverse_questions = [2, 5, 6, 11, 12, 14, 16, 17, 18, 20]

        total_score = 0
        for i, score in self.scores.items():
            if i in reverse_questions:  # 如果是反向评分题
                score = 4 - score  # 反转分数
            total_score += score

        # 显示总分
        messagebox.showinfo("测试完成", f"您的总分是: {total_score}")

        # 保存到CSV文件
        self.save_result(name, total_score)

    def save_result(self, name, total_score):
        """将结果保存到CSV文件"""
        folder_path = "self_test_data"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        file_path = os.path.join(folder_path, f"{name}.csv")

        # 写入CSV文件
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["姓名", "score"])
            writer.writerow([name, total_score])

        messagebox.showinfo("保存成功", f"测试结果已保存至 {file_path}")

# 创建Tkinter窗口并运行SDS量表
if __name__ == "__main__":
    root = tk.Tk()
    app = SDSQuestionnaire(root)
    root.mainloop()