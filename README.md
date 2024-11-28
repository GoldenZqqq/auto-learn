<!--
 * @Description: 在线学习自动化脚本
 * @Author: Huang Zhaoqi
 * @LastEditors: Huang Zhaoqi
 * @Date: 2024-11-28 15:52:58
 * @LastEditTime: 2024-11-28 15:53:04
-->
# 在线学习自动化脚本

这是一个用于自动化在线学习的Python脚本，支持多用户并发学习，自动记录学习进度。

## 功能特点

- 支持多用户同时学习
- 自动获取未完成课程
- 智能进度更新
- 自动跳过已完成章节
- 详细的学习进度显示

## 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/你的用户名/online-learning-automation.git
cd online-learning-automation
```

2. 创建并激活虚拟环境（推荐）
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

## 配置说明

在 `config.py` 中配置用户信息：

```python
USERS = [
    {
        "username": "用户名",
        "password": "密码",
        "auth_token": None,  # 可选，如果有token则直接使用token
        "domain": "yygfeduuser.bkehs.com"  # 域名
    }
]
```

其他配置项：
```python
# API配置
BASE_URL = "https://eduapi.bkehs.com"  # API基础地址

# 学习配置
MIN_UPDATE_INTERVAL = 3    # 最小更新间隔（秒）
MAX_UPDATE_INTERVAL = 8    # 最大更新间隔（秒）
PROGRESS_CHUNK_SIZE = 60   # 每次更新的进度时长（秒）
```

## 使用方法

1. 配置用户信息
2. 运行脚本
```bash
python auto_learn.py
```

## 项目结构

```
online-learning-automation/
├── README.md
├── requirements.txt
├── auto_learn.py
└── config.py
```

## 注意事项

- 请合理使用，不要对服务器造成过大压力
- 建议在虚拟环境中运行脚本
- 如果使用token登录，确保token是有效的

## License

MIT License