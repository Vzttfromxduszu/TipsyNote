# 源代码

本项目采用传统后端三层架构（Controller / Service / Repository / Model），并包含 AI 模块。

## 目录结构
- controllers/：接口层（HTTP 控制器）
- services/：业务层（业务逻辑编排）
- repositories/：数据访问层（数据库读写）
- models/：数据模型（与表结构对应）
- routes/：路由与 API 聚合
- dtos/：请求/响应对象
- middlewares/：鉴权、限流、异常处理等
- ai/：大模型管理与调用
- configs/：配置
- utils/：通用工具
- storage/：统一资源存储占位（图片、封面等）

## 约定
- Controller 只做参数校验与调用 Service
- Service 不直接访问数据库，统一经 Repository
- AI 能力由 Service 调用，日志入库
