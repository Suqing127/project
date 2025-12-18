import os
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser

def load_reports(report_dir):
    """
    加载所有报告文件。
    """
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

def filter_reports(reports, filter_type, filter_value):
    """
    根据筛选条件过滤报告。
    """
    filtered_reports = []
    for report in reports:
        if filter_type == "姓名" and filter_value.lower() in report["name"].lower():
            filtered_reports.append(report)
        elif filter_type == "风险程度" and filter_value == report["risk_level"]:
            filtered_reports.append(report)
    return filtered_reports

def open_report(report_path):
    """
    打开选中的报告。
    """
    webbrowser.open(report_path)

def view_reports():
    """
    查看报告的主界面。
    """
    report_dir = r'E:\AiProject\project\report_data'  # 修改为 E:\ai\report_data

    # 加载所有报告
    reports = load_reports(report_dir)

    # 创建主窗口
    root = tk.Tk()
    root.title("查看报告")
    root.geometry("600x400")

    # 筛选条件框架
    filter_frame = ttk.LabelFrame(root, text="筛选条件")
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
            filter_value_combobox = ttk.Combobox(filter_frame, textvariable=filter_value_var, values=["Normal", "Need Attention", "High Risk"])
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
            messagebox.showwarning("警告", "请输入筛选值！")
            return

        filtered_reports = filter_reports(reports, filter_type, filter_value)
        update_report_list(filtered_reports)

    filter_button = ttk.Button(filter_frame, text="筛选", command=on_filter)
    filter_button.grid(row=0, column=4, padx=5, pady=5)

    # 报告列表框架
    report_list_frame = ttk.LabelFrame(root, text="报告列表")
    report_list_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # 报告列表
    report_listbox = tk.Listbox(report_list_frame)
    report_listbox.pack(fill="both", expand=True, padx=5, pady=5)

    # 更新报告列表
    def update_report_list(reports):
        report_listbox.delete(0, tk.END)
        for report in reports:
            report_listbox.insert(tk.END, f"{report['filename']} - {report['risk_level']}")

    # 初始加载所有报告
    update_report_list(reports)

    # 打开报告按钮
    def on_open_report():
        selected_index = report_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("警告", "请选择一个报告！")
            return

        selected_report = reports[selected_index[0]]
        open_report(selected_report["path"])

    open_button = ttk.Button(root, text="打开报告", command=on_open_report)
    open_button.pack(pady=10)

    # 运行主循环
    root.mainloop()

if __name__ == "__main__":
    view_reports()