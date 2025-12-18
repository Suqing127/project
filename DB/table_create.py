import mysql.connector
from mysql.connector import Error

config = {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "charset": "utf8mb4"
}

def create_tables():
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS school_system")
        cursor.execute("USE school_system")

        # 创建 Class 表（必须先创建，因为其他表依赖它）
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Class (
            class_id INT AUTO_INCREMENT PRIMARY KEY,
            class_name VARCHAR(50) NOT NULL UNIQUE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 创建 Student 表（关联 Class 表）
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Student (
            stu_id VARCHAR(20) PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            gender ENUM('男', '女', '其他'),
            age INT CHECK (age >= 0),
            class_id INT,  -- 改为关联 class_id
            gpa DOUBLE CHECK (gpa >= 0 AND gpa <= 4.0),
            failed_courses INT DEFAULT 0,
            FOREIGN KEY (class_id) REFERENCES Class(class_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 创建 Teacher 表（关联 Class 表）
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Teacher (
            teacher_id VARCHAR(20) PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            gender ENUM('男', '女', '其他'),
            class_id INT,  -- 改为关联 class_id
            FOREIGN KEY (class_id) REFERENCES Class(class_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 创建 User 表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS User (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            role ENUM('0', '1', '2') DEFAULT '0'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 创建触发器：插入学生时自动创建账户
        cursor.execute("""
        CREATE TRIGGER after_student_insert
        AFTER INSERT ON Student
        FOR EACH ROW
        BEGIN
            INSERT INTO User (username, password, role)
            VALUES (NEW.stu_id, '111111', '2');
        END;
        """)

        # 创建触发器：插入教师时自动创建账户
        cursor.execute("""
        CREATE TRIGGER after_teacher_insert
        AFTER INSERT ON Teacher
        FOR EACH ROW
        BEGIN
            INSERT INTO User (username, password, role)
            VALUES (NEW.teacher_id, '111111', '1');
        END;
        """)

        # 创建 admin 用户
        cursor.execute("""
                    INSERT INTO User (username, password, role) 
                    VALUES ('admin', 'admin', '0')
                    ON DUPLICATE KEY UPDATE password = 'admin', role = '0';
                """)

        print("所有表和触发器已成功创建！")

    except Error as e:
        print(f"数据库操作错误: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("数据库连接已关闭")

if __name__ == "__main__":
    create_tables()
