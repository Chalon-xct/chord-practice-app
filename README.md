# 和弦练习应用

基于 Vue + Flask 的吉他每日和弦练习应用，使用 DeepSeek AI 生成个性化练习内容。

## 功能特点

- 🎵 **听音辨和弦** - 通过聆听音频识别和弦名称
- 📝 **和弦构成** - 根据和弦名写出构成音
- 🎯 **循序渐进** - AI 根据表现调整难度（1-10 级）
- 📊 **智能总结** - DeepSeek 生成详细练习反馈
- 🎸 **吉他和弦图** - 每次练习后显示所有和弦按法
- 🔥 **每日打卡** - 记录连续练习天数

## 技术栈

- **前端**: Vue 3 + Vite + Pinia + Vue Router
- **后端**: Flask + SQLAlchemy
- **数据库**: SQLite
- **音频**: midiutil
- **AI**: DeepSeek API

## 快速开始

### 1. 配置 DeepSeek API Key

```bash
cd backend
cp .env.example .env
# 编辑 .env 文件，填入你的 DeepSeek API Key
```

### 2. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 启动后端服务

```bash
cd backend
python app.py
# 服务运行在 http://localhost:5000
```

### 4. 安装前端依赖

```bash
cd frontend
npm install
```

### 5. 启动前端开发服务器

```bash
cd frontend
npm run dev
# 应用运行在 http://localhost:3000
```

## 项目结构

```
chord-practice-app/
├── backend/
│   ├── app.py              # Flask 主应用
│   ├── models.py           # 数据库模型
│   ├── midi_generator.py   # MIDI 音频生成
│   ├── guitar_chords.py    # 吉他和弦指法数据
│   ├── deepseek_service.py # DeepSeek API 集成
│   └── requirements.txt    # Python 依赖
└── frontend/
    ├── src/
    │   ├── views/          # 页面组件
    │   ├── components/     # 通用组件
    │   ├── stores/         # Pinia 状态管理
    │   └── router/         # 路由配置
    └── package.json        # Node 依赖
```

## API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| /api/auth/register | POST | 用户注册 |
| /api/auth/login | POST | 用户登录 |
| /api/auth/me | GET | 获取当前用户 |
| /api/practice/start | POST | 开始练习 |
| /api/practice/submit | POST | 提交练习 |
| /api/practice/history | GET | 练习历史 |
| /api/user/stats | GET | 用户统计 |

## 难度级别

| 级别 | 内容 |
|------|------|
| 1-2 | 基础三和弦：C, D, E, G, A, Am, Em, Dm |
| 3-4 | 更多调式和弦：F, Bm 等 |
| 5-6 | 七和弦：Cmaj7, Dm7, G7 等 |
| 7-8 | 延伸和弦、变化和弦 |
| 9-10 | 复杂爵士和弦 |

## 注意事项

1. 首次运行时会自动创建 SQLite 数据库
2. 密码使用 Werkzeug 进行哈希加密
3. JWT token 有效期为 7 天
4. 建议在生产环境中更换 JWT_SECRET_KEY
