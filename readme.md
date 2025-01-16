# SQL Injection Test Web Demo

## 项目概述
这是一个用于演示SQL注入漏洞的Flask Web应用程序。项目包含登录、搜索和注册功能，每个功能都故意存在SQL注入漏洞，以便学习和测试安全防护措施。

## 主要功能
- **登录功能**：存在SQL注入漏洞，允许攻击者通过构造恶意SQL查询来绕过身份验证。
- **搜索功能**：存在布尔盲注漏洞，允许攻击者通过构造恶意SQL查询来判断数据库中的信息。
- **注册功能**：存在时间盲注漏洞，允许攻击者通过构造恶意SQL查询来延时响应，从而推断数据库中的信息。

## 运行环境
- Python 3.x
- Flask
- SQLite

## 安装依赖
```bash
pip install flask
```

## 运行项目
```bash
python app.py
```

项目将在 http://127.0.0.1:8888 上启动。

代码结构
app.py：主应用程序文件，包含路由和数据库操作。
注意事项
本项目仅用于教育和测试目的，请勿在生产环境中使用。
请确保在安全的环境中运行此项目，以防止潜在的安全风险。
贡献
欢迎贡献代码和改进项目。请遵循以下步骤：

Fork 项目
创建您的特性分支 (git checkout -b feature/AmazingFeature)
提交您的更改 (git commit -m 'Add some AmazingFeature')
推送到分支 (git push origin feature/AmazingFeature)
打开一个 Pull Request
许可证
本项目采用MIT许可证。有关详细信息，请参阅 LICENSE 文件。

