# TipsyNote · 酒馆项目

精酿啤酒爱好者社区平台，帮助用户发现附近的精酿酒馆、搜索酒款、管理酒单，并提供 AI 侍酒师推荐。

## 技术栈

| 层 | 技术 |
|---|------|
| 后端框架 | Python FastAPI |
| 数据库 | MySQL 8.0 + SQLAlchemy ORM |
| 缓存/地理 | Redis（GEO 附近搜索） |
| 前端 | Vue 3 + TypeScript + Element Plus |
| 构建 | Vite |
| 短信 | 阿里云号码认证（Dypnsapi） |
| 地图 | 高德地理编码 + 步行/驾车路径规划 |
| AI | DeepSeek v4（侍酒师推荐） |

## 目录结构

```
├── src/              # 后端源码
│   ├── main.py       # FastAPI 入口
│   ├── api/          # 路由
│   ├── services/     # 业务逻辑
│   ├── repositories/ # 数据访问
│   ├── models/       # SQLAlchemy 模型
│   ├── schema/       # Pydantic 模型
│   ├── configs/      # 配置
│   ├── utils/        # 工具（短信、JWT、高德等）
│   └── db/           # 数据库初始化 & Redis
├── frontend/         # Vue 3 前端
│   └── src/
│       ├── views/    # 页面组件
│       ├── api/      # API 调用层
│       ├── types/    # TypeScript 类型
│       ├── stores/   # Pinia 状态管理
│       └── router/   # 路由配置
├── docs/             # 架构与决策文档
├── scripts/          # 数据库迁移等脚本
├── storage/          # 上传文件（不入库）
└── requirements.txt  # Python 依赖
```

## 本地开发

```bash
# 1. 后端
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # 编辑 .env 填写配置
python src/db/create_db.py
uvicorn src.main:app --reload

# 2. 前端
cd frontend
npm install
npm run dev
```

## 环境变量

参考 `.env.example`，关键配置项：

- `MYSQL_URL` / `REDIS_URL` — 数据库连接
- `JWT_SECRET` — JWT 签名密钥
- `AMAP_KEY` — 高德地图 API Key
- `ALI_ACCESS_KEY_ID` / `ALI_ACCESS_KEY_SECRET` — 阿里云短信
- `SMS_MOCK=true` — 开发环境跳过真实短信发送

## 核心功能

- 🔍 **找酒** — 按酒款搜索附近酒馆，GPS 距离排序
- 🍺 **酒单管理** — 商家/管理员管理酒馆酒款（增删改）
- 🤖 **AI 侍酒师** — DeepSeek 驱动的精酿推荐
- 💬 **社区** — 帖子发布、评论、点赞
- 📍 **路径规划** — 步行/驾车到店路线
- 👤 **商家认证** — 商家身份认证（即将上线）

## 部署

见 [部署说明](deploy/README.md)，推荐使用 Docker Compose 一键部署。详细步骤见 `finish.md`。

