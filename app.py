from flask import Flask, render_template, request, jsonify
import os
import csv
from datetime import datetime

app = Flask(__name__)

# SDS 量表问题列表
QUESTIONS = [
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

# 反向评分题的索引（问题编号从 0 开始）
REVERSE_QUESTIONS = [1, 4, 5, 10, 11, 13, 15, 16, 17, 19]

@app.route('/')
def index():
    return render_template('index.html', questions=QUESTIONS)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    name = data.get('name')
    scores = data.get('scores')

    if not name or not scores or len(scores) != len(QUESTIONS):
        return jsonify({"error": "请输入姓名并完成所有问题的评分"}), 400

    # 计算总分
    total_score = 0
    for i, score in enumerate(scores):
        if i in REVERSE_QUESTIONS:  # 如果是反向评分题
            score = 4 - int(score)  # 反转分数
        total_score += int(score)

    # 保存结果到 CSV 文件
    save_result(name, total_score)

    return jsonify({"success": True, "total_score": total_score})

def save_result(name, total_score):
    folder = 'self_test_data'
    if not os.path.exists(folder):
        os.makedirs(folder)

    filename = f"{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    filepath = os.path.join(folder, filename)

    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["姓名", "总分"])
        writer.writerow([name, total_score])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)