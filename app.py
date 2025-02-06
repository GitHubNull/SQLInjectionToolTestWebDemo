import logging
from flask import Flask, request, render_template_string, g
import sqlite3
import time

app = Flask(__name__)

# 数据库连接和初始化
DATABASE = 'test_sql_injection.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        db.commit()
        # 初始化一些数据
        cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES ('admin', 'password123')")
        cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES ('test', 'test123')")
        db.commit()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# 设置日志记录
def setup_logging():
    # 创建日志记录器
    logger = logging.getLogger('flask_sql_injection')
    logger.setLevel(logging.DEBUG)

    # 日志格式
    formatter = logging.Formatter("\r[%(asctime)s] [%(levelname)s] [%(module)s] [%(filename)s] [Line: %(lineno)d] %(message)s", "%Y-%m-%d %H:%M:%S")

    # 输出到控制台的日志处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 输出到文件的日志处理器
    file_handler = logging.FileHandler('app.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = setup_logging()


# 首页模板
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>SQL Injection Test</title>
</head>
<body>
    <h1>SQL Injection Test</h1>
    <h2>Select Injection Difficulty Level</h2>
    <form action="/set_difficulty" method="post">
        <select name="difficulty">
            <option value="0">Level 0</option>
            <option value="1">Level 1</option>
            <option value="2">Level 2</option>
            <option value="3">Level 3</option>
            <option value="4">Level 4</option>
            <option value="5">Level 5</option>
            <option value="6">Level 6</option>
            <option value="7">Level 7</option>
            <option value="8">Level 8</option>
            <option value="9">Level 9</option>
        </select>
        <input type="submit" value="Set Difficulty">
    </form>

    <h2>Login Form</h2>
    <form action="/login" method="post">
        Username: <input type="text" name="username"><br>
        Password: <input type="text" name="password"><br>
        <input type="submit" value="Login">
    </form>

    <h2>Search Users</h2>
    <form action="/search" method="get">
        Username: <input type="text" name="query"><br>
        <input type="submit" value="Search">
    </form>

    <h2>Register User</h2>
    <form action="/register" method="post">
        Username: <input type="text" name="username"><br>
        Password: <input type="text" name="password"><br>
        <input type="submit" value="Register">
    </form>
</body>
'''

# 设置难度级别
@app.route('/set_difficulty', methods=['POST'])
def set_difficulty():
    global difficulty_level
    difficulty_level = int(request.form.get('difficulty', 0))
    logger.info(f"Difficulty level set to: {difficulty_level}")
    return "Difficulty level set successfully."

# 登录页面（存在SQL注入漏洞）
@app.route('/')
def home():
    logger.info("Accessed home page")
    return render_template_string(HOME_TEMPLATE)

# 添加全局变量来存储难度级别
difficulty_level = 1

def add_random_conditions(query, level):
    import random
    conditions = {
        0: [],
        1: ["id > 0"],
        2: ["id > 0", "username != ''"],
        3: ["id > 0", "username != ''", "password != ''"],
        4: ["id > 0", "username != ''", "password != ''", "id % 2 = 0"],
        5: ["id > 0", "username != ''", "password != ''", "id % 2 = 0", "length(username) > 3"],
        6: ["id > 0", "username != ''", "password != ''", "id % 2 = 0", "length(username) > 3", "length(password) > 5"],
        7: ["id > 0", "username != ''", "password != ''", "id % 2 = 0", "length(username) > 3", "length(password) > 5", "username LIKE 'a%'"],
        8: ["id > 0", "username != ''", "password != ''", "id % 2 = 0", "length(username) > 3", "length(password) > 5", "username LIKE 'a%'", "password LIKE 'p%'"],
        9: ["id > 0", "username != ''", "password != ''", "id % 2 = 0", "length(username) > 3", "length(password) > 5", "username LIKE 'a%'", "password LIKE 'p%'", "id > 5"]
    }
    if level in conditions:
        return query + " AND " + " AND ".join(random.sample(conditions[level], random.randint(1, len(conditions[level]))))
    else:
        return query

# 字符过滤函数
def sanitize_input(input_string):
    # 过滤掉一些危险字符
    dangerous_chars = ["'", "\"", ";", "--", "/*", "*/", "@@", "CHAR", "NCHAR", "NVARCHAR", "VARCHAR", "ALTER", "CREATE", "DELETE", "DROP", "EXEC", "INSERT", "MERGE", "SELECT", "UPDATE", "UNION"]
    for char in dangerous_chars:
        input_string = input_string.replace(char, "")
    return input_string

@app.route('/login', methods=['POST'])
def login():
    username = sanitize_input(request.form.get('username', ''))
    password = sanitize_input(request.form.get('password', ''))
    db = get_db()
    cursor = db.cursor()
    # 存在SQL注入漏洞的查询
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    query = add_random_conditions(query, difficulty_level)
    logger.info(f"Login attempt with query: {query}")
    try:
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            logger.info(f"Login successful for user: {username}")
            return f"Welcome, {result[1]}!"
        else:
            logger.warning(f"Login failed for user: {username}")
            return "Invalid username or password."
    except Exception as e:
        logger.error(f"Error during login: {e}")
        return f"An error occurred: {e}"

@app.route('/search', methods=['GET'])
def search():
    query = sanitize_input(request.args.get('query', ''))
    db = get_db()
    cursor = db.cursor()
    # 存在SQL注入漏洞的查询
    sql_query = f"SELECT username FROM users WHERE username LIKE '%{query}%'"
    sql_query = add_random_conditions(sql_query, difficulty_level)
    logger.info(f"Search query: {sql_query}")
    try:
        cursor.execute(sql_query)
        results = cursor.fetchall()
        if results:
            logger.info(f"Search results: {[row[0] for row in results]}")
            return f"Search results: {[row[0] for row in results]}"
        else:
            logger.info("No search results found.")
            return "No results found."
    except Exception as e:
        logger.error(f"Error during search: {e}")
        return f"An error occurred: {e}"

@app.route('/register', methods=['POST'])
def register():
    username = sanitize_input(request.form.get('username', ''))
    password = sanitize_input(request.form.get('password', ''))
    db = get_db()
    cursor = db.cursor()
    # 存在SQL注入漏洞的插入
    query = f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')"
    query = add_random_conditions(query, difficulty_level)
    logger.info(f"Registration attempt with query: {query}")
    try:
        # 模拟时间盲注
        if "sleep" in username.lower():
            logger.warning("Potential time-based SQL injection detected.")
            time.sleep(5)
        cursor.execute(query)
        db.commit()
        logger.info(f"User {username} registered successfully.")
        return "User registered successfully."
    except Exception as e:
        logger.error(f"Error during registration: {e}")
        return f"An error occurred: {e}"


if __name__ == '__main__':
    init_db()
    logger.info("Starting Flask app...")
    app.run(host='127.0.0.1', port=8888, debug=True)
