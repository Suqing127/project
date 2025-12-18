# 学校管理系统

## 环境要求
```
python=3.8
numpy=1.7.4
tensorflow=2.2.0
cv2=4.6.0
scipy=1.4.1
h5py=2.10.0
pandas=0.25.3
scikit-learn=0.22.1
mysql-connector-python=8.0.33
ttkbootstrap=1.10.1
```

## 安装依赖
```bash
pip install numpy==1.7.4 tensorflow==2.2.0 opencv-python==4.6.0 scipy==1.4.1 h5py==2.10.0 pandas==0.25.3 scikit-learn==0.22.1 mysql-connector-python==8.0.33 ttkbootstrap==1.10.1
```

## 数据库配置
**重要：使用前需要修改数据库密码！**

在 `table_create.py` 和 `table_fun.py` 文件中，修改以下配置：
```python
config = {
    "host": "localhost",
    "user": "root",
    "password": "123456",  # 改为你自己的MySQL密码
    "database": "school_system",
    "charset": "utf8mb4"
}
```

## 启动系统
```bash
python gui.py
```

## 默认管理员账户
- 用户名：admin
- 密码：admin

## 数据集链接
1. C20D8：https://gitcode.com/open-source-toolkit/c20d8/tree/main
2. CASME：http://casme.psych.ac.cn/casme/c2
