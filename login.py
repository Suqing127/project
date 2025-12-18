import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error

# MySQL 数据库配置
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "database": "school_system",
    "charset": "utf8mb4"
}

def validate_user(username, password):
    """验证用户登录信息"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)

        # 使用参数化查询防止SQL注入
        query = "SELECT * FROM User WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user:
            return user["role"]  # 返回用户角色 '0','1','2'
        return None

    except Error as e:
        messagebox.showerror("数据库错误", f"数据库连接失败: {str(e)}")
        return None

class LoginFrame(ttk.Frame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent)
        self.parent = parent
        self.on_login_success = on_login_success
        self.create_login_form()

    def create_login_form(self):
        # 网格布局配置
        self.grid_columnconfigure(0, weight=1, minsize=150)
        self.grid_columnconfigure(1, weight=2, minsize=150)

        # 用户名输入
        ttk.Label(self, text="用户名:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.username_entry = ttk.Entry(self)
        self.username_entry.grid(row=0, column=1, padx=10, pady=5, sticky='ew')
        self.username_entry.focus()

        # 密码输入
        ttk.Label(self, text="密码:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=5, sticky='ew')

        # 登录按钮
        ttk.Button(self, text="登录", command=self.check_login).grid(
            row=2, column=0, columnspan=2, pady=20, sticky='n'
        )

    def check_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("输入错误", "用户名和密码不能为空")
            return

        user_role = validate_user(username, password)

        if user_role is not None:
            self.on_login_success(username, user_role)
        else:
            messagebox.showerror("登录失败", "用户名或密码错误")