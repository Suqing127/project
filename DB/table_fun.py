import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
from ttkbootstrap import Style

# 数据库连接配置
config = {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "database": "school_system",
    "charset": "utf8mb4"
}

# 全局变量
connection = None
cursor = None

# 初始化数据库连接
def init_db():
    global connection, cursor
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)
    except Error as e:
        messagebox.showerror("数据库错误", f"无法连接数据库: {e}")

# 关闭数据库连接
def close_db():
    if connection and connection.is_connected():
        cursor.close()
        connection.close()

# 创建主界面
class MainApp:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(parent, width=200, bg="#f0f0f0")
        self.frame.pack(side=tk.LEFT, fill=tk.Y)

        self.style = ttk.Style()
        self.style.theme_use('clam')  # 使用 'clam' 主题

        # 右侧功能显示区域
        self.right_frame = tk.Frame(parent, width=600, height=600, bg="#ffffff")
        self.right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        self.right_frame.pack_propagate(False)  # 阻止调整大小

        # 初始化数据库
        init_db()

    # 清空右侧区域
    def clear_right_frame(self):
        for widget in self.right_frame.winfo_children():
            widget.destroy()

    # 显示创建功能
    def show_create(self):
        self.clear_right_frame()

        # 选择学生或教师
        self.user_type = tk.StringVar(value="student")
        student_button = tk.Radiobutton(self.right_frame, text="学生", variable=self.user_type, value="student", command=self.show_create_form)
        teacher_button = tk.Radiobutton(self.right_frame, text="教师", variable=self.user_type, value="teacher", command=self.show_create_form)

        student_button.grid(row=0, column=0, padx=10, pady=10)
        teacher_button.grid(row=0, column=1, padx=10, pady=10)

        # 显示表单
        self.show_create_form()

    def show_create_form(self):
        # 清空表单区域
        for widget in self.right_frame.winfo_children():
            if widget.grid_info()["row"] > 0:
                widget.destroy()

        # 学生表单
        if self.user_type.get() == "student":
            tk.Label(self.right_frame, text="学号:").grid(row=1, column=0, padx=10, pady=10)
            self.stu_id_entry = tk.Entry(self.right_frame)
            self.stu_id_entry.grid(row=1, column=1, padx=10, pady=10)

            tk.Label(self.right_frame, text="姓名:").grid(row=2, column=0, padx=10, pady=10)
            self.stu_name_entry = tk.Entry(self.right_frame)
            self.stu_name_entry.grid(row=2, column=1, padx=10, pady=10)

            tk.Label(self.right_frame, text="性别:").grid(row=3, column=0, padx=10, pady=10)
            self.stu_gender_combobox = ttk.Combobox(self.right_frame, values=["男", "女", "其他"])
            self.stu_gender_combobox.grid(row=3, column=1, padx=10, pady=10)

            tk.Label(self.right_frame, text="年龄:").grid(row=4, column=0, padx=10, pady=10)
            self.stu_age_entry = tk.Entry(self.right_frame)
            self.stu_age_entry.grid(row=4, column=1, padx=10, pady=10)

            tk.Label(self.right_frame, text="班级:").grid(row=5, column=0, padx=10, pady=10)
            self.stu_class_combobox = ttk.Combobox(self.right_frame)
            self.stu_class_combobox.grid(row=5, column=1, padx=10, pady=10)

            tk.Label(self.right_frame, text="绩点:").grid(row=6, column=0, padx=10, pady=10)
            self.stu_gpa_entry = tk.Entry(self.right_frame)
            self.stu_gpa_entry.grid(row=6, column=1, padx=10, pady=10)

            tk.Label(self.right_frame, text="挂科门数:").grid(row=7, column=0, padx=10, pady=10)
            self.stu_failed_courses_entry = tk.Entry(self.right_frame)
            self.stu_failed_courses_entry.grid(row=7, column=1, padx=10, pady=10)

            # 填充班级下拉框
            self.populate_class_combobox(self.stu_class_combobox)

            # 提交按钮
            tk.Button(self.right_frame, text="提交", command=self.create_student).grid(row=8, column=1, padx=10, pady=10)

        # 教师表单
        else:
            tk.Label(self.right_frame, text="工号:").grid(row=1, column=0, padx=10, pady=10)
            self.teacher_id_entry = tk.Entry(self.right_frame)
            self.teacher_id_entry.grid(row=1, column=1, padx=10, pady=10)

            tk.Label(self.right_frame, text="姓名:").grid(row=2, column=0, padx=10, pady=10)
            self.teacher_name_entry = tk.Entry(self.right_frame)
            self.teacher_name_entry.grid(row=2, column=1, padx=10, pady=10)

            tk.Label(self.right_frame, text="性别:").grid(row=3, column=0, padx=10, pady=10)
            self.teacher_gender_combobox = ttk.Combobox(self.right_frame, values=["男", "女", "其他"])
            self.teacher_gender_combobox.grid(row=3, column=1, padx=10, pady=10)

            tk.Label(self.right_frame, text="班级:").grid(row=4, column=0, padx=10, pady=10)
            self.teacher_class_combobox = ttk.Combobox(self.right_frame)
            self.teacher_class_combobox.grid(row=4, column=1, padx=10, pady=10)

            # 填充班级下拉框
            self.populate_class_combobox(self.teacher_class_combobox)

            # 提交按钮
            tk.Button(self.right_frame, text="提交", command=self.create_teacher).grid(row=5, column=1, padx=10, pady=10)

    # 填充班级下拉框
    def populate_class_combobox(self, combobox):
        try:
            cursor.execute("SELECT class_name FROM Class")
            classes = cursor.fetchall()
            class_names = [c["class_name"] for c in classes]
            combobox["values"] = class_names
        except Error as e:
            messagebox.showerror("数据库错误", f"无法获取班级列表: {e}")

    # 创建学生记录
    def create_student(self):
        stu_id = self.stu_id_entry.get()
        name = self.stu_name_entry.get()
        gender = self.stu_gender_combobox.get()
        age = self.stu_age_entry.get()
        class_name = self.stu_class_combobox.get()
        gpa = self.stu_gpa_entry.get()
        failed_courses = self.stu_failed_courses_entry.get()

        if not all([stu_id, name, gender, age, class_name, gpa, failed_courses]):
            messagebox.showwarning("输入错误", "请填写所有字段")
            return

        try:
            # 获取班级 ID
            cursor.execute("SELECT class_id FROM Class WHERE class_name = %s", (class_name,))
            class_id = cursor.fetchone()["class_id"]

            # 插入学生记录
            cursor.execute(
                "INSERT INTO Student (stu_id, name, gender, age, class_id, gpa, failed_courses) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (stu_id, name, gender, age, class_id, gpa, failed_courses)
            )
            connection.commit()
            messagebox.showinfo("成功", "学生记录已创建")
        except Error as e:
            messagebox.showerror("数据库错误", f"无法创建学生记录: {e}")

    # 创建教师记录
    def create_teacher(self):
        teacher_id = self.teacher_id_entry.get()
        name = self.teacher_name_entry.get()
        gender = self.teacher_gender_combobox.get()
        class_name = self.teacher_class_combobox.get()

        if not all([teacher_id, name, gender, class_name]):
            messagebox.showwarning("输入错误", "请填写所有字段")
            return

        try:
            # 获取班级 ID
            cursor.execute("SELECT class_id FROM Class WHERE class_name = %s", (class_name,))
            class_id = cursor.fetchone()["class_id"]

            # 插入教师记录
            cursor.execute(
                "INSERT INTO Teacher (teacher_id, name, gender, class_id) "
                "VALUES (%s, %s, %s, %s)",
                (teacher_id, name, gender, class_id)
            )
            connection.commit()
            messagebox.showinfo("成功", "教师记录已创建")
        except Error as e:
            messagebox.showerror("数据库错误", f"无法创建教师记录: {e}")

    # 显示修改功能
    def show_update(self):
        self.clear_right_frame()

        # 选择学生或教师
        self.update_user_type = tk.StringVar(value="student")
        student_button = tk.Radiobutton(self.right_frame, text="学生", variable=self.update_user_type, value="student", command=self.show_update_form)
        teacher_button = tk.Radiobutton(self.right_frame, text="教师", variable=self.update_user_type, value="teacher", command=self.show_update_form)

        student_button.grid(row=0, column=0, padx=10, pady=10)
        teacher_button.grid(row=0, column=1, padx=10, pady=10)

        # 显示表单
        self.show_update_form()

    def show_update_form(self):
        # 清空表单区域
        for widget in self.right_frame.winfo_children():
            if widget.grid_info()["row"] > 0:
                widget.destroy()

        # 搜索框
        tk.Label(self.right_frame, text="学号/工号:").grid(row=1, column=0, padx=10, pady=10)
        self.search_entry = tk.Entry(self.right_frame)
        self.search_entry.grid(row=1, column=1, padx=10, pady=10)

        # 搜索按钮
        tk.Button(self.right_frame, text="搜索", command=self.search_record).grid(row=1, column=2, padx=10, pady=10)

        # 学生表单
        if self.update_user_type.get() == "student":
            tk.Label(self.right_frame, text="学号:").grid(row=2, column=0, padx=10, pady=10)
            self.stu_id_label = tk.Label(self.right_frame, text="", bg="#f0f0f0")
            self.stu_id_label.grid(row=2, column=1, padx=10, pady=10)

            tk.Label(self.right_frame, text="姓名:").grid(row=3, column=0, padx=10, pady=10)
            self.stu_name_entry = tk.Entry(self.right_frame)
            self.stu_name_entry.grid(row=3, column=1, padx=10, pady=10)

            tk.Label(self.right_frame, text="性别:").grid(row=4, column=0, padx=10, pady=10)
            self.stu_gender_combobox = ttk.Combobox(self.right_frame, values=["男", "女", "其他"])
            self.stu_gender_combobox.grid(row=4, column=1, padx=10, pady=10)

            tk.Label(self.right_frame, text="年龄:").grid(row=5, column=0, padx=10, pady=10)
            self.stu_age_entry = tk.Entry(self.right_frame)
            self.stu_age_entry.grid(row=5, column=1, padx=10, pady=10)

            tk.Label(self.right_frame, text="班级:").grid(row=6, column=0, padx=10, pady=10)
            self.stu_class_combobox = ttk.Combobox(self.right_frame)
            self.stu_class_combobox.grid(row=6, column=1, padx=10, pady=10)

            tk.Label(self.right_frame, text="绩点:").grid(row=7, column=0, padx=10, pady=10)
            self.stu_gpa_entry = tk.Entry(self.right_frame)
            self.stu_gpa_entry.grid(row=7, column=1, padx=10, pady=10)

            tk.Label(self.right_frame, text="挂科门数:").grid(row=8, column=0, padx=10, pady=10)
            self.stu_failed_courses_entry = tk.Entry(self.right_frame)
            self.stu_failed_courses_entry.grid(row=8, column=1, padx=10, pady=10)

            # 权限修改
            tk.Label(self.right_frame, text="权限:").grid(row=9, column=0, padx=10, pady=10)
            self.stu_role_combobox = ttk.Combobox(self.right_frame, values=["管理员", "老师", "学生"])
            self.stu_role_combobox.grid(row=9, column=1, padx=10, pady=10)

            # 填充班级下拉框
            self.populate_class_combobox(self.stu_class_combobox)

            # 提交按钮
            tk.Button(self.right_frame, text="提交修改", command=self.update_student).grid(row=10, column=1, padx=10, pady=10)

        # 教师表单
        else:
            tk.Label(self.right_frame, text="工号:").grid(row=2, column=0, padx=10, pady=10)
            self.teacher_id_label = tk.Label(self.right_frame, text="", bg="#f0f0f0")
            self.teacher_id_label.grid(row=2, column=1, padx=10, pady=10)

            tk.Label(self.right_frame, text="姓名:").grid(row=3, column=0, padx=10, pady=10)
            self.teacher_name_entry = tk.Entry(self.right_frame)
            self.teacher_name_entry.grid(row=3, column=1, padx=10, pady=10)

            tk.Label(self.right_frame, text="性别:").grid(row=4, column=0, padx=10, pady=10)
            self.teacher_gender_combobox = ttk.Combobox(self.right_frame, values=["男", "女", "其他"])
            self.teacher_gender_combobox.grid(row=4, column=1, padx=10, pady=10)

            tk.Label(self.right_frame, text="班级:").grid(row=5, column=0, padx=10, pady=10)
            self.teacher_class_combobox = ttk.Combobox(self.right_frame)
            self.teacher_class_combobox.grid(row=5, column=1, padx=10, pady=10)

            # 权限修改
            tk.Label(self.right_frame, text="权限:").grid(row=6, column=0, padx=10, pady=10)
            self.teacher_role_combobox = ttk.Combobox(self.right_frame, values=["管理员", "老师", "学生"])
            self.teacher_role_combobox.grid(row=6, column=1, padx=10, pady=10)

            # 填充班级下拉框
            self.populate_class_combobox(self.teacher_class_combobox)

            # 提交按钮
            tk.Button(self.right_frame, text="提交修改", command=self.update_teacher).grid(row=7, column=1, padx=10, pady=10)

    def search_record(self):
        search_id = self.search_entry.get()
        if not search_id:
            messagebox.showwarning("输入错误", "请输入学号或工号")
            return

        try:
            if self.update_user_type.get() == "student":
                # 查询学生信息
                cursor.execute("SELECT * FROM Student WHERE stu_id = %s", (search_id,))
                student = cursor.fetchone()
                if student:
                    # 显示学生信息
                    self.stu_id_label.config(text=student["stu_id"])
                    self.stu_name_entry.delete(0, tk.END)
                    self.stu_name_entry.insert(0, student["name"])
                    self.stu_gender_combobox.set(student["gender"])
                    self.stu_age_entry.delete(0, tk.END)
                    self.stu_age_entry.insert(0, student["age"])

                    # 获取班级名称
                    cursor.execute("SELECT class_name FROM Class WHERE class_id = %s", (student["class_id"],))
                    class_name = cursor.fetchone()["class_name"]
                    self.stu_class_combobox.set(class_name)

                    self.stu_gpa_entry.delete(0, tk.END)
                    self.stu_gpa_entry.insert(0, student["gpa"])
                    self.stu_failed_courses_entry.delete(0, tk.END)
                    self.stu_failed_courses_entry.insert(0, student["failed_courses"])

                    # 查询用户权限
                    cursor.execute("SELECT role FROM User WHERE username = %s", (student["stu_id"],))
                    user = cursor.fetchone()
                    if user:
                        role_map = {"0": "管理员", "1": "老师", "2": "学生"}
                        self.stu_role_combobox.set(role_map.get(user["role"], ""))
                else:
                    messagebox.showwarning("提示", "未找到该学生记录")
            else:
                # 查询教师信息
                cursor.execute("SELECT * FROM Teacher WHERE teacher_id = %s", (search_id,))
                teacher = cursor.fetchone()
                if teacher:
                    # 显示教师信息
                    self.teacher_id_label.config(text=teacher["teacher_id"])
                    self.teacher_name_entry.delete(0, tk.END)
                    self.teacher_name_entry.insert(0, teacher["name"])
                    self.teacher_gender_combobox.set(teacher["gender"])

                    # 获取班级名称
                    cursor.execute("SELECT class_name FROM Class WHERE class_id = %s", (teacher["class_id"],))
                    class_name = cursor.fetchone()["class_name"]
                    self.teacher_class_combobox.set(class_name)

                    # 查询用户权限
                    cursor.execute("SELECT role FROM User WHERE username = %s", (teacher["teacher_id"],))
                    user = cursor.fetchone()
                    if user:
                        role_map = {"0": "管理员", "1": "老师", "2": "学生"}
                        self.teacher_role_combobox.set(role_map.get(user["role"], ""))
                else:
                    messagebox.showwarning("提示", "未找到该教师记录")
        except Error as e:
            messagebox.showerror("数据库错误", f"查询失败: {str(e)}")

    def update_student(self):
        # 获取表单数据
        stu_id = self.stu_id_label.cget("text")
        name = self.stu_name_entry.get()
        gender = self.stu_gender_combobox.get()
        age = self.stu_age_entry.get()
        class_name = self.stu_class_combobox.get()
        gpa = self.stu_gpa_entry.get()
        failed_courses = self.stu_failed_courses_entry.get()
        role = {"管理员": "0", "老师": "1", "学生": "2"}[self.stu_role_combobox.get()]

        try:
            # 获取班级ID
            cursor.execute("SELECT class_id FROM Class WHERE class_name = %s", (class_name,))
            class_id = cursor.fetchone()["class_id"]

            # 更新学生表
            cursor.execute("""
                UPDATE Student SET 
                name = %s, 
                gender = %s, 
                age = %s, 
                class_id = %s, 
                gpa = %s, 
                failed_courses = %s 
                WHERE stu_id = %s
            """, (name, gender, age, class_id, gpa, failed_courses, stu_id))

            # 更新用户表
            cursor.execute("""
                UPDATE User SET 
                role = %s 
                WHERE username = %s
            """, (role, stu_id))

            connection.commit()
            messagebox.showinfo("成功", "学生信息更新成功！")
        except Error as e:
            connection.rollback()
            messagebox.showerror("数据库错误", f"更新失败: {str(e)}")

    def update_teacher(self):
        # 获取表单数据
        teacher_id = self.teacher_id_label.cget("text")
        name = self.teacher_name_entry.get()
        gender = self.teacher_gender_combobox.get()
        class_name = self.teacher_class_combobox.get()
        role = {"管理员": "0", "老师": "1", "学生": "2"}[self.teacher_role_combobox.get()]

        try:
            # 获取班级ID
            cursor.execute("SELECT class_id FROM Class WHERE class_name = %s", (class_name,))
            class_id = cursor.fetchone()["class_id"]

            # 更新教师表
            cursor.execute("""
                UPDATE Teacher SET 
                name = %s, 
                gender = %s, 
                class_id = %s 
                WHERE teacher_id = %s
            """, (name, gender, class_id, teacher_id))

            # 更新用户表
            cursor.execute("""
                UPDATE User SET 
                role = %s 
                WHERE username = %s
            """, (role, teacher_id))

            connection.commit()
            messagebox.showinfo("成功", "教师信息更新成功！")
        except Error as e:
            connection.rollback()
            messagebox.showerror("数据库错误", f"更新失败: {str(e)}")

    # 显示查询功能
    def show_delete(self):
        self.clear_right_frame()

        # 选择学生或教师
        self.delete_user_type = tk.StringVar(value="student")
        student_button = tk.Radiobutton(self.right_frame, text="学生", variable=self.delete_user_type, value="student",
                                        command=self.show_delete_form)
        teacher_button = tk.Radiobutton(self.right_frame, text="教师", variable=self.delete_user_type, value="teacher",
                                        command=self.show_delete_form)

        student_button.grid(row=0, column=0, padx=10, pady=10)
        teacher_button.grid(row=0, column=1, padx=10, pady=10)

        # 显示表单
        self.show_delete_form()

    def show_delete_form(self):
        # 清空表单区域
        for widget in self.right_frame.winfo_children():
            if widget.grid_info()["row"] > 0:
                widget.destroy()

        # 搜索条件选择
        tk.Label(self.right_frame, text="搜索条件:").grid(row=1, column=0, padx=10, pady=10)
        self.search_type = ttk.Combobox(self.right_frame, values=["学/工号", "姓名", "班级"])
        self.search_type.grid(row=1, column=1, padx=10, pady=10)
        self.search_type.bind("<<ComboboxSelected>>", self.update_search_input)  # 绑定事件

        # 动态输入控件容器
        self.input_frame = tk.Frame(self.right_frame)
        self.input_frame.grid(row=2, column=0, columnspan=3, sticky="ew")

        # 普通输入框
        self.search_entry = tk.Entry(self.input_frame)
        self.search_entry.pack(fill=tk.X, padx=10)

        # 班级下拉框（初始隐藏）
        self.class_combobox = ttk.Combobox(self.input_frame)
        self.class_combobox.pack(fill=tk.X, padx=10)
        self.class_combobox.pack_forget()

        # 搜索按钮
        tk.Button(self.right_frame, text="搜索", command=self.search_delete_records).grid(row=3, column=1, pady=10)

        # 结果列表
        columns = ["ID", "姓名", "性别", "班级", "年龄", "绩点",
                   "挂科门数"] if self.delete_user_type.get() == "student" else ["ID", "姓名", "性别", "班级"]
        self.result_tree = ttk.Treeview(self.right_frame, columns=columns + ["操作"], show="headings")

        # 设置列
        col_widths = {"ID": 100, "姓名": 80, "性别": 60, "班级": 120, "年龄": 60, "绩点": 60, "挂科门数": 80,
                      "操作": 60}
        for col in columns + ["操作"]:
            self.result_tree.heading(col, text=col)
            self.result_tree.column(col, width=col_widths.get(col, 100))
        self.result_tree.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # 绑定删除按钮事件
        self.result_tree.bind("<Button-1>", self.on_treeview_click)

    def update_search_input(self, event=None):
        """动态切换输入控件"""
        if self.search_type.get() == "班级":
            # 显示班级下拉框
            self.search_entry.pack_forget()
            self.class_combobox.pack(fill=tk.X, padx=10)
            # 填充班级数据
            try:
                cursor.execute("SELECT class_name FROM Class")
                classes = [row["class_name"] for row in cursor.fetchall()]
                self.class_combobox["values"] = classes
            except Error as e:
                messagebox.showerror("数据库错误", f"无法加载班级列表: {str(e)}")
        else:
            # 显示普通输入框
            self.class_combobox.pack_forget()
            self.search_entry.pack(fill=tk.X, padx=10)

    def search_delete_records(self):
        search_type = self.search_type.get()
        keyword = self.class_combobox.get() if search_type == "班级" else self.search_entry.get()

        if not search_type:
            messagebox.showwarning("输入错误", "请先选择搜索条件")
            return
        if not keyword:
            messagebox.showwarning("输入错误", "请输入/选择搜索关键词")
            return

        try:
            # 清空旧数据
            self.result_tree.delete(*self.result_tree.get_children())

            if self.delete_user_type.get() == "student":
                # 学生搜索逻辑
                base_query = """
                    SELECT s.stu_id, s.name, s.gender, c.class_name, 
                           s.age, s.gpa, s.failed_courses 
                    FROM Student s 
                    JOIN Class c ON s.class_id = c.class_id
                """
                if search_type == "学/工号":
                    query = base_query + " WHERE s.stu_id = %s"
                elif search_type == "姓名":
                    query = base_query + " WHERE s.name LIKE %s"
                    keyword = f"%{keyword}%"
                else:  # 班级
                    query = base_query + " WHERE c.class_name = %s"

                cursor.execute(query, (keyword,))
                results = cursor.fetchall()

                # 填充数据
                for row in results:
                    values = [
                        row["stu_id"], row["name"], row["gender"], row["class_name"],
                        row["age"], row["gpa"], row["failed_courses"]
                    ]
                    item = self.result_tree.insert("", tk.END, values=values + ["删除"])
                    self.result_tree.set(item, "操作", "删除")

            else:
                # 教师搜索逻辑
                base_query = """
                    SELECT t.teacher_id, t.name, t.gender, c.class_name 
                    FROM Teacher t 
                    JOIN Class c ON t.class_id = c.class_id
                """
                if search_type == "学/工号":
                    query = base_query + " WHERE t.teacher_id = %s"
                elif search_type == "姓名":
                    query = base_query + " WHERE t.name LIKE %s"
                    keyword = f"%{keyword}%"
                else:  # 班级
                    query = base_query + " WHERE c.class_name = %s"

                cursor.execute(query, (keyword,))
                results = cursor.fetchall()

                # 填充数据
                for row in results:
                    values = [row["teacher_id"], row["name"], row["gender"], row["class_name"]]
                    item = self.result_tree.insert("", tk.END, values=values + ["删除"])
                    self.result_tree.set(item, "操作", "删除")

        except Error as e:
            messagebox.showerror("数据库错误", f"搜索失败: {str(e)}")

    def on_treeview_click(self, event):
        """处理 Treeview 点击事件"""
        region = self.result_tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.result_tree.identify_column(event.x)
            if column == "#8":  # 操作列
                item = self.result_tree.identify_row(event.y)
                target_id = self.result_tree.item(item, "values")[0]  # 获取 ID
                self.confirm_delete(target_id)

    def confirm_delete(self, target_id):
        if messagebox.askyesno("确认删除",
                               f"确定要删除{target_id}吗？\n该操作将同时删除关联账户！"):
            try:
                # 删除主记录
                if self.delete_user_type.get() == "student":
                    cursor.execute("DELETE FROM Student WHERE stu_id = %s", (target_id,))
                else:
                    cursor.execute("DELETE FROM Teacher WHERE teacher_id = %s", (target_id,))

                # 删除关联账户
                cursor.execute("DELETE FROM User WHERE username = %s", (target_id,))

                connection.commit()
                self.search_delete_records()  # 刷新列表
                messagebox.showinfo("成功", "记录删除成功！")
            except Error as e:
                connection.rollback()
                messagebox.showerror("数据库错误", f"删除失败: {str(e)}\n错误代码: {e.errno}")

# 主程序
if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
    close_db()
