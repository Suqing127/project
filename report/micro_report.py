import glob
import os
import tkinter as tk
from datetime import datetime
from tkinter import simpledialog

import chardet
import mysql.connector
import pandas as pd
from mysql.connector import Error
import plotly.express as px

# MySQL 数据库配置
config = {
    "host": "localhost",
    "user": "root",
    "password": "password",
    "database": "school_system",
    "charset": "utf8mb4"
}

def connect_to_db():
    """
    连接到 MySQL 数据库。
    """
    try:
        conn = mysql.connector.connect(**config)
        print("成功连接到 MySQL 数据库")
        return conn
    except Error as e:
        print(f"连接数据库时出错: {e}")
        return None

def query_student_info_by_name(student_name):
    """
    根据学生姓名从数据库中查询学生信息。
    """
    conn = connect_to_db()
    if conn is None:
        print("无法连接到数据库")
        return []

    cursor = conn.cursor()

    query = """
    SELECT 
        name AS 姓名,
        stu_id AS 学号,
        gender AS 性别,
        class_id AS 班级,
        gpa AS 绩点
    FROM Student
    WHERE name LIKE %s
    """
    params = (f"%{student_name}%",)

    print(f"Executing query: {query} with params: {params}")
    cursor.execute(query, params)
    results = cursor.fetchall()

    conn.close()
    return results

def load_students_info(student_name):
    """
    从数据库加载学生信息，处理多个匹配结果。
    """
    student_info = query_student_info_by_name(student_name)

    if not student_info:  # 空结果处理
        print(f"No data found for student '{student_name}'.")
        return None

    # 转换结果时保留原始数据结构
    students_df = pd.DataFrame(student_info, columns=['姓名', '学号', '性别', '班级', '绩点'])

    # 如果有多条结果提示用户
    if len(students_df) > 1:
        print(f"找到{len(students_df)}条匹配记录，将返回所有结果")

    return students_df

def load_emotion_data(student_name):
    """
    通过姓名从micro_data文件夹中加载学生的微表情数据。
    """
    # 获取文件夹的绝对路径
    folder_path = r'E:\AiProject\project\emotion\emotion\micro_data'

    # 根据文件名模式查找文件
    files = glob.glob(os.path.join(folder_path, f'{student_name}_*.csv'))

    if not files:
        raise FileNotFoundError(f"No emotion data found for student: {student_name}")

    # 选择第一个文件进行处理
    emotion_data = pd.read_csv(files[0])
    return emotion_data

def load_sds_data(student_name):
    """
    通过姓名从self_test_data文件夹中加载SDS自测数据。
    """
    # 获取文件夹的绝对路径
    folder_path = r'E:\AiProject\project\self_test\self_test_data'

    # 根据文件名模式查找文件
    sds_file = glob.glob(os.path.join(folder_path, f'{student_name}.csv'))

    if not sds_file:  # 检查列表是否为空
        raise FileNotFoundError(f"No SDS data found for student: {student_name}")

    # 使用第一个匹配到的文件
    sds_file_path = sds_file[0]

    # 使用chardet来检测文件编码
    with open(sds_file_path, 'rb') as f:
        result = chardet.detect(f.read())  # 读取文件的字节并检测编码
    encoding = result['encoding']
    print(f"Detected encoding for {sds_file_path}: {encoding}")  # 打印检测到的编码

    try:
        # 使用自动检测到的编码打开文件
        sds_data = pd.read_csv(sds_file_path, encoding=encoding)
    except Exception as e:
        raise ValueError(f"Error reading SDS file: {e}")

    # 确保文件中包含'姓名'和'score'列，并提取分数
    if '姓名' not in sds_data.columns or 'score' not in sds_data.columns:
        raise ValueError("SDS file must contain '姓名' and 'score' columns.")

    # 查找对应学生的SDS数据
    student_sds = sds_data[sds_data['姓名'] == student_name]

    if student_sds.empty:
        raise ValueError(f"No SDS score found for student: {student_name}")

    return student_sds

def load_action_data(student_name):
    """
    通过姓名从action_data文件夹中加载动作数据。
    """
    # 获取文件夹的绝对路径
    folder_path = r'E:\AiProject\project\action\data'

    # 根据文件名模式查找文件
    action_file = glob.glob(os.path.join(folder_path, f'{student_name}_*.csv'))

    if not action_file:  # 检查列表是否为空
        raise FileNotFoundError(f"No action data found for student: {student_name}")

    # 使用第一个匹配到的文件
    action_file_path = action_file[0]

    # 使用chardet来检测文件编码
    with open(action_file_path, 'rb') as f:
        result = chardet.detect(f.read())  # 读取文件的字节并检测编码
    encoding = result['encoding']
    print(f"Detected encoding for {action_file_path}: {encoding}")  # 打印检测到的编码

    try:
        # 使用自动检测到的编码打开文件
        action_data = pd.read_csv(action_file_path, encoding=encoding)
    except Exception as e:
        raise ValueError(f"Error reading action data file: {e}")

    return action_data

def calculate_emotion_average(emotion_data):
    """
    计算微表情数据中每种情感的平均概率。
    """
    emotion_types = ['angry', 'disgust', 'scared', 'happy', 'sad', 'surprised', 'neutral']
    emotion_avg = {emotion: 0 for emotion in emotion_types}

    # 确保 emotion 列没有额外空格，并且所有字符都是小写（或统一格式）
    emotion_data['emotion'] = emotion_data['emotion'].str.strip().str.lower()

    # 检查 'probability' 列的非空且为数值类型
    emotion_data['probability'] = pd.to_numeric(emotion_data['probability'], errors='coerce')

    # 计算每种情感的平均概率
    for emotion in emotion_types:
        emotion_prob = emotion_data[emotion_data['emotion'] == emotion]['probability']
        if len(emotion_prob) > 0:
            emotion_avg[emotion] = emotion_prob.mean()

    # 标准化负面情绪概率，确保其值在 0 到 1 之间
    max_prob = max(emotion_avg.values())
    if max_prob > 0:
        for emotion in emotion_types:
            emotion_avg[emotion] = emotion_avg[emotion] / max_prob

    return emotion_avg

def calculate_action_score(action_data):
    """
    计算动作数据的综合评分。
    """
    # 标准化动作数据
    action_data['Negative_Emotion_Normalized'] = action_data['Negative Emotion Duration (s)'] / action_data['Total Duration (s)']
    action_data['Arms_Crossed_Normalized'] = action_data['Arms Crossed Duration (s)'] / action_data['Total Duration (s)']
    action_data['Defensive_Normalized'] = action_data['Defensive Duration (s)'] / action_data['Total Duration (s)']
    action_data['Hands_Trembling_Normalized'] = action_data['Hands Trembling Duration (s)'] / action_data['Total Duration (s)']
    action_data['Hands_Clenched_Normalized'] = action_data['Hands Clenched Duration (s)'] / action_data['Total Duration (s)']

    # 计算动作数据的综合评分
    action_score = (
        action_data['Negative_Emotion_Normalized'].mean() +
        action_data['Arms_Crossed_Normalized'].mean() +
        action_data['Defensive_Normalized'].mean() +
        action_data['Hands_Trembling_Normalized'].mean() +
        action_data['Hands_Clenched_Normalized'].mean()
    ) / 5  # 平均所有动作指标

    return action_score

def evaluate_mental_health(sds_score, emotion_data_avg, action_score, gpa):
    """
    评估心理健康状态：综合考虑SDS分数、微表情数据、动作数据和GPA。
    GPA 满分为 5 分，低于 3 分为不合格。
    """
    # 标准化SDS分数
    sds_normalized = sds_score / 80

    # 计算微表情数据中的负面情绪平均概率
    emotion_score = (emotion_data_avg['sad'] + emotion_data_avg['angry'] + emotion_data_avg['scared']) / 3

    # 标准化GPA（满分为5分，低于3分为不合格）
    if gpa < 3:
        gpa_normalized = 0  # GPA不合格，心理压力较大
    else:
        gpa_normalized = gpa / 5.0  # 标准化到0-1范围

    # 计算综合评分
    composite_score = (
        0.5 * sds_normalized +  # 提高SDS分数的权重
        0.2 * emotion_score +   # 降低负面情绪的权重
        0.2 * action_score +   # 动作数据的权重保持不变
        0.1 * (1 - gpa_normalized)  # GPA越低，心理压力可能越大
    )
    print(sds_normalized)
    print(emotion_score)

    # 根据综合评分判断心理状况
    if composite_score < 0.5:
        return 'Normal'
    elif 0.5 <= composite_score < 0.7:
        return 'Need Attention'
    else:
        return 'High Risk'

def save_report(student_info, sds_data, emotion_data_avg, action_score, report_dir):
    """
    保存心理健康评估报告为 HTML 文件，包含学生基本信息、分析结果和建议。
    """
    # 获取当前时间，格式化为年月日小时分钟秒
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 获取学生的GPA
    gpa = student_info['绩点']

    # 进行心理健康评估
    mental_health_status = evaluate_mental_health(sds_data['score'].values[0], emotion_data_avg, action_score, gpa)

    # 根据心理状态生成文件名
    if mental_health_status == 'High Risk':
        report_filename = f"[High Risk] {student_info['姓名']}_{current_time}.html"
    else:
        report_filename = f"[{mental_health_status}] {student_info['姓名']}_{current_time}.html"

    # 合成完整路径
    report_file = os.path.join(report_dir, report_filename)

    # 检查报告目录是否存在
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)  # 创建目录

    # 生成微表情分析的饼状图
    emotion_labels = list(emotion_data_avg.keys())
    emotion_values = list(emotion_data_avg.values())

    # 使用 Plotly 生成饼状图
    fig = px.pie(values=emotion_values, names=emotion_labels, title='微表情分析占比')
    pie_chart_html = fig.to_html(full_html=False)

    # 生成报告内容
    report_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>心理健康评估报告 - {student_info['姓名']}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 20px;
            }}
            h1, h2 {{
                color: #333;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            table, th, td {{
                border: 1px solid #ddd;
            }}
            th, td {{
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            .recommendation {{
                background-color: #f9f9f9;
                padding: 15px;
                border-left: 5px solid #007bff;
                margin-top: 20px;
            }}
            .chart-container {{
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <h1>心理健康评估报告</h1>
        <h2>学生基本信息</h2>
        <table>
            <tr>
                <th>姓名</th>
                <td>{student_info['姓名']}</td>
            </tr>
            <tr>
                <th>学号</th>
                <td>{student_info['学号']}</td>
            </tr>
            <tr>
                <th>性别</th>
                <td>{student_info['性别']}</td>
            </tr>
            <tr>
                <th>班级</th>
                <td>{student_info['班级']}</td>
            </tr>
            <tr>
                <th>绩点 (GPA)</th>
                <td>{gpa:.2f}</td>
            </tr>
        </table>

        <h2>评估结果</h2>
        <table>
            <tr>
                <th>SDS 分数</th>
                <td>{sds_data['score'].values[0]}</td>
            </tr>
            <tr>
                <th>微表情分析</th>
                <td>{str(emotion_data_avg)}</td>
            </tr>
            <tr>
                <th>微动作分析</th>
                <td>{action_score:.2f}</td>
            </tr>
            <tr>
                <th>心理健康评估</th>
                <td>{mental_health_status}</td>
            </tr>
        </table>

        <h2>微表情分析占比</h2>
        <div class="chart-container">
            {pie_chart_html}
        </div>

        <h2>建议</h2>
        <div class="recommendation">
            {generate_recommendation(mental_health_status, emotion_data_avg, action_score, gpa)}
        </div>
    </body>
    </html>
    """

    # 将报告内容写入 HTML 文件
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)

    print(f"Report generated for {student_info['姓名']} and saved to {report_file}")

    # 如果是“High Risk”学生，将文件移动到文件夹的前面
    if mental_health_status == 'High Risk':
        high_risk_dir = os.path.join(report_dir, "High Risk")
        if not os.path.exists(high_risk_dir):
            os.makedirs(high_risk_dir)
        new_report_file = os.path.join(high_risk_dir, report_filename)
        os.rename(report_file, new_report_file)
        print(f"High Risk report moved to {high_risk_dir}")

def generate_recommendation(mental_health_status, emotion_data_avg, action_score, gpa):
    """
    根据心理健康评估结果生成建议。
    """
    if mental_health_status == 'Normal':
        return """
        <p>该学生的心理健康状况正常。建议继续保持良好的生活习惯和积极的心态。</p>
        <ul>
            <li>定期参加体育锻炼，保持身体健康。</li>
            <li>与朋友和家人保持良好的沟通，分享生活中的喜怒哀乐。</li>
            <li>合理安排学习和休息时间，避免过度疲劳。</li>
        </ul>
        """
    elif mental_health_status == 'Need Attention':
        return f"""
        <p>该学生的心理健康状况需要关注。当前绩点为 {gpa:.2f}，可能增加了学业压力。建议采取以下措施：</p>
        <ul>
            <li>定期进行心理健康自测，关注情绪变化。</li>
            <li>参加学校或社区组织的心理健康讲座和活动。</li>
            <li>如果感到压力过大，可以寻求心理咨询师的帮助。</li>
            <li>制定学习计划，提升学业表现，减少学业压力。</li>
        </ul>
        """
    else:
        return f"""
        <p>该学生的心理健康状况存在较高风险。当前绩点为 {gpa:.2f}，学业压力较大。建议立即采取以下措施：</p>
        <ul>
            <li>尽快联系学校心理咨询中心，寻求专业帮助。</li>
            <li>与家人和朋友沟通，寻求情感支持。</li>
            <li>避免独处，尽量参与集体活动，保持积极的心态。</li>
            <li>制定详细的学习计划，必要时寻求学业辅导。</li>
        </ul>
        """

def main():
    """
    主执行流程。
    """
    student_name = get_student_name()
    if student_name:
        analyze_student_data(student_name)
    else:
        print("No student name entered. Exiting.")

# 程序启动
if __name__ == "__main__":
    main()

def get_student_name():
    """
    创建一个弹窗让用户输入学生姓名。
    """
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    student_name = simpledialog.askstring("Input", "Please enter the student's name:")
    return student_name

def analyze_student_data(student_name):
    """
    分析学生的数据，包括SDS自测数据、微表情数据、动作数据和GPA，并生成心理健康评估报告。
    """
    # 加载学生基本信息
    students_info = load_students_info(student_name)

    if students_info is None or students_info.empty:
        print(f"Warning: No data found for student '{student_name}'. Skipping.")
        return

    # 获取学生的具体信息（第一行数据）
    student_info = students_info.iloc[0]  # 获取第一个匹配到的学生数据
    print(f"Student Info: {student_info}")  # 打印学生信息调试

    # 1. 加载SDS自测数据
    try:
        sds_data = load_sds_data(student_name)
    except FileNotFoundError:
        print(f"Warning: No SDS data found for {student_name}. Skipping.")
        return

    # 2. 加载微表情分析数据
    try:
        emotion_data = load_emotion_data(student_name)
    except FileNotFoundError:
        print(f"Warning: No emotion data found for {student_name}. Skipping.")
        return

    # 3. 加载动作数据
    try:
        action_data = load_action_data(student_name)
    except FileNotFoundError:
        print(f"Warning: No action data found for {student_name}. Skipping.")
        return

    # 4. 计算微表情数据的平均值
    emotion_data_avg = calculate_emotion_average(emotion_data)

    # 5. 计算动作数据的综合评分
    action_score = calculate_action_score(action_data)

    # 6. 生成报告
    report_dir = 'report_data'  # 设置报告保存目录
    save_report(student_info, sds_data, emotion_data_avg, action_score, report_dir)
    print(f"Report generated for {student_name} and saved to {report_dir}")