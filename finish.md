# finish.md

> 项目关键上下文（精简版）。后续变更将同步更新。

## 当前状态
- 后端已完成：用户/酒馆/酒单 CRUD，登录鉴权，头像上传，按酒款查询酒馆，按酒款+GPS距离排序查询。
- FastAPI 启动入口与路由已接入。
- MySQL ORM 建表脚本已完成；Redis GEO 用于附近搜索。
- 高德地理编码：酒馆创建/更新时由结构化地址获取经纬度。
- 前端新增酒馆详情页，可查看酒馆信息与酒单。
- 前端已调整为用户端：以“酒款搜索 + 附近酒馆”为核心流程，首页支持搜索与定位。

## 核心接口
- 用户：POST /api/users，PUT /api/users/{id}，GET /api/users
- 鉴权：POST /api/auth/login，GET /api/me（返回 `managed_pubs`：管理员→全部酒馆，商家→自己的酒馆，普通用户→[]）
- 头像上传：POST /api/users/me/avatar（JPG/PNG，<2MB，存储到 storage/avatars/，返回 /api/avatars/{filename}）
- 头像静态文件挂载于 /api/avatars/，前端通过该路径直接加载
- 酒馆：POST/GET/PUT/DELETE /api/pubs
- 酒款：POST/GET/PUT/DELETE /api/beers
- 酒款找酒馆：GET /api/pubs/by-beer
- 酒款+附近：GET /api/pubs/by-beer-nearby?beer_name&lat&lng&radius_km
- 附近所有酒馆：GET /api/pubs/nearby?lat&lng&radius_km（默认 20km，按距离排序，返回 {items: [{pub, distance_km}], total}）
- AI 推荐：POST /api/ai/recommend
- AI 推荐日志：prompt_tags/ai_response 以 JSON 字符串入库
- 步行路线：GET /api/pubs/{pub_id}/walking?origin_lng&origin_lat（返回 duration_min）
- 驾车路线：GET /api/pubs/{pub_id}/route?origin_lng&origin_lat（返回 duration_min）
- 社区帖子：POST/GET/PUT/DELETE /api/posts（用户发帖与社区讨论）
- 帖子评论：POST/GET /api/posts/{post_id}/comments
- 帖子点赞：POST /api/posts/{post_id}/likes/toggle，GET /api/posts/{post_id}/likes/status，GET /api/posts/liked（我赞过的帖子）
- 反向地理编码：GET /api/location/reverse-geocode?lng=&lat=
- 短信验证码发送：POST /api/auth/send-code（body: {phone}）
- 用户注册（需验证码）：POST /api/users（body: {phone, secret, code, nickname?}）

## 权限说明
- role=0 普通用户
- role=1 商家
- role=2 管理员（最高权限，可执行所有权限相关操作）

## 关键配置
- .env：MYSQL_URL，JWT_SECRET，TOKEN_EXPIRE_MINUTES，STORAGE_PATH，REDIS_URL，REDIS_GEO_KEY，AMAP_KEY
- 短信配置：SMS_MOCK，ALI_ACCESS_KEY_ID，ALI_ACCESS_KEY_SECRET，ALI_SMS_SIGN_NAME，ALI_SMS_TEMPLATE_CODE，ALI_SMS_SCHEME_NAME，ALI_SMS_CODE_LENGTH，ALI_SMS_VALID_TIME

## 关键文件
- 入口：src/main.py
- 配置：src/configs/settings.py
- 用户：src/api/users.py、src/services/users_service.py、src/repositories/users_repository.py
- 鉴权：src/api/auth.py、src/utils/jwt_utils.py、src/api/deps.py
- LLM：src/ai/client.py、src/ai/prompt.py、src/ai/parser.py、src/ai/model.py、src/ai/retriever.py（RAG）
- AI 侍酒师使用 DeepSeek v4 API，默认模型 `deepseek-v4-flash`，已关闭思考模式（`thinking:disabled`）+ JSON 输出约束 + max_tokens 限长，确保快速响应
- 酒馆：src/api/pubs.py、src/services/pubs_service.py、src/repositories/pubs_repository.py
- 酒单：src/api/beer_inventory.py、src/services/beer_inventory_service.py、src/repositories/beer_inventory_repository.py
- 社区帖子：src/api/posts.py、src/services/posts_service.py、src/repositories/posts_repository.py、src/models/post.py、src/dtos/posts.py、src/schema/posts.py
- 帖子评论：src/api/comments.py、src/models/post_comment.py
- 帖子点赞：src/api/likes.py、src/models/post_like.py
- 地理编码：src/api/location.py
- Redis：src/db/redis_client.py
- 数据库迁移：scripts/migrate_posts.py
- 头像工具：src/utils/avatar_url.py
- 高德：src/utils/amap_geocode.py
- 短信服务：src/utils/sms.py（阿里云号码认证 SendSmsVerifyCode）
- 前端入口：frontend/src/main.ts
- 前端路由：frontend/src/router/index.ts
- 前端搜索页：frontend/src/views/Home.vue
- 前端用户页：frontend/src/views/UserProfile.vue
- 前端接口：frontend/src/api/pubs.ts
- 前端社区接口：frontend/src/api/posts.ts、frontend/src/types/posts.ts
- 前端社区页面：frontend/src/views/Community.vue、frontend/src/views/PostDetail.vue、frontend/src/views/PostEditor.vue
- 前端酒单管理：frontend/src/views/MyPubs.vue、frontend/src/api/beer.ts、frontend/src/types/beer.ts

## 注意事项
- /api/me 需要 Authorization: Bearer <token>
- 头像上传仅 JPG/PNG，<2MB，存储到 storage/avatars/，URL 格式为 /api/avatars/{filename}，前端可直接通过该 URL 加载
- 头像 URL 通过 normalize_avatar_url() 统一规范化，兼容旧格式的绝对/相对路径
- Redis GEO 需要酒馆经纬度
- 附近搜索会跳过 Redis GEO 中非数字成员，避免解析报错
- 酒款搜索默认不强制 in_stock_only（传 true 才过滤在售）
- 短信验证码使用阿里云号码认证 SendSmsVerifyCode API，开发环境（SMS_MOCK=true）本地生成验证码并打印到控制台，生产环境（SMS_MOCK=false）由阿里云生成并下发短信
- SendSmsVerifyCode 强制要求使用号码认证控制台的赠送签名+赠送模板（不支持自定义签名），签名和模板需属于同一个方案
- 验证码存储在 Redis（key: sms:code:{phone}），TTL 由 ALI_SMS_VALID_TIME 控制（默认 300 秒），校验通过后立即删除
- 用户注册流程：先 POST /api/auth/send-code 获取验证码 → 再 POST /api/users 携带 code 完成注册
- cryptography 版本必须与编译的 .pyd 文件一致，否则 JWT 签名会报版本不匹配错误（Loaded python version vs shared object version）

## 变更记录

### 2026-06-17 — 精酿大全前端暂时下架
- **目的**：将精酿大全功能在前端暂时隐藏，后端 API 和组件代码保留不动，方便后续恢复。
- **修改文件**：
  - `frontend/src/layouts/MainLayout.vue`：注释掉导航栏 `<el-menu-item index="/beer-wiki">精酿大全</el-menu-item>`，添加"暂时下架"注释。
  - `frontend/src/router/index.ts`：注释掉 3 条精酿大全路由（`/beer-wiki`、`/beer-wiki/style/:id`、`/beer-wiki/beer/:id`），添加"暂时下架"注释。
- **未修改**：后端 `src/api/beer_wiki.py`、前端组件（`Encyclopedia.vue`、`BeerStyleDetail.vue`、`BeerItemDetail.vue`）、前端 API 层（`frontend/src/api/beerWiki.ts`）、类型定义（`frontend/src/types/beerWiki.ts`）均保持原样。

### 2026-06-17 — 注册流程增加短信验证码
- **目的**：用户注册时需先获取手机验证码，防止恶意注册。
- **技术方案**：阿里云号码认证 SendSmsVerifyCode API，开发环境 mock 模式。
- **后端修改**：
  - `requirements.txt`：新增 `alibabacloud-dypnsapi20170525>=3.0`、`alibabacloud-tea-openapi>=0.4`
  - `src/configs/settings.py`：新增 8 个短信配置项（SMS_MOCK、ALI_ACCESS_KEY_ID、ALI_ACCESS_KEY_SECRET、ALI_SMS_SIGN_NAME、ALI_SMS_TEMPLATE_CODE、ALI_SMS_SCHEME_NAME、ALI_SMS_CODE_LENGTH、ALI_SMS_VALID_TIME）
  - `src/utils/sms.py`（新建）：封装阿里云号码认证客户端，实现 send_verification_code() / verify_code()
  - `src/schema/schemas.py`：新增 `SendCodeRequest`（phone），`UserCreateRequest` 增加 `code` 必填字段
  - `src/api/auth.py`：新增 `POST /api/auth/send-code` 发送验证码接口
  - `src/api/users.py`：`create_user` 增加 verify_code() 校验，校验通过后才创建用户
- **前端修改**：
  - `frontend/src/types/user.ts`：新增 `SendCodePayload`，`RegisterPayload` 增加 `code` 字段
  - `frontend/src/api/user.ts`：新增 `sendCode()` API 调用
  - `frontend/src/views/Register.vue`：新增验证码输入框 + "发送验证码"按钮（含 60 秒倒计时、手机号格式实时校验），删除角色选择
- **依赖安装**：`alibabacloud-dypnsapi20170525` 替换了旧 `alibabacloud-dysmsapi20170525`（普通短信 → 号码认证）
- **注意事项**：
  - SendSmsVerifyCode 强制使用号码认证控制台赠送签名+赠送模板，不支持自定义签名
  - 签名和模板必须属于同一个"方案"（默认方案或指定 SCHEME_NAME）
  - `template_param` 使用 `{"code":"##code##"}` 由阿里云自动生成验证码，通过 `return_verify_code=True` 获取
  - 验证码存入 Redis（key: `sms:code:{phone}`），TTL=300 秒，校验后删除
  - 开发环境设置 `SMS_MOCK=true` 可在控制台看到验证码日志
  - 安装 SDK 后出现过 cryptography 版本冲突（46.0.7 vs 48.0.0），已通过手动重装 cryptography==48.0.0 修复
- **恢复方式**：取消上述两处注释即可恢复功能。

### 2026-06-17 — 找酒页未搜索时默认展示 20km 内全部酒馆
- **目的**：复用搜索结果区的「附近酒馆」卡片列表。页面打开且未输入酒款搜索时，自动展示当前定位 20 公里内所有酒馆（按距离排序，不含酒款信息）；用户输入酒款并搜索后，切换为原来的酒款过滤结果。
- **后端新增**：
  - `src/repositories/pubs_repository.py`：新增 `get_pubs_by_ids()` 按 ID 批量查询酒馆。
  - `src/services/pubs_service.py`：新增 `search_nearby_pubs()`，通过 Redis GEOSEARCH 获取半径内 pub_id 并按距离排序，再批量查 MySQL 补齐酒馆信息。
  - `src/api/pubs.py`：新增 `GET /api/pubs/nearby?lat=&lng=&radius_km=&offset=&limit=`，返回 `{ items: [{pub, distance_km}], total }`。
  - `src/schema/pubs.py`：新增 `PubNearbyItem`、`PubNearbyResponse`。
- **前端修改**：
  - `frontend/src/types/pubs.ts`：新增 `PubNearbyItem`、`PubNearbyResponse`、`PubNearbyQuery`。
  - `frontend/src/api/pubs.ts`：新增 `fetchNearbyPubs()`。
  - `frontend/src/views/Home.vue`：
    - 新增 `hasSearched` 状态，区分「未搜索」（展示全部附近酒馆）与「已搜索」（展示酒款过滤结果）。
    - `onMounted` 自动定位 → 延时 1.5s 等待定位回调 → 调 `/api/pubs/nearby` 填入 `nearbyPubs`。
    - 未搜索卡片只展示距离/营业/电话，已搜索卡片额外展示酒款/酒厂/风格/价格。
    - `el-empty` 文案分别对应两种状态。

### 2026-06-17 — 搜索结果为合并展示（同一酒馆只出现一次）
- **目的**：搜索一个大类时（如"IPA"），同一酒馆的不同酒款不再被拆分为多张卡片，而是合并为一张酒馆卡片，卡片内以表格子列表展示该酒馆匹配的全部酒款。
- **修改文件**：`frontend/src/views/Home.vue`
  - 新增本地 `GroupedPubItem` 接口：`{ pub, distance_km, beers[] }`。
  - 新增 `groupedResults` computed：将后端返回的 `BeerPubItem[]` 按 `pub.id` 分组合并，保持原始距离排序；按 `priceAsc/priceDesc` 排序时按该酒馆最便宜/最贵的酒款排序。
  - 已搜索模板改为纵向卡片列表：左侧封面 140px 方形、右侧酒馆名+距离+元信息 + `<el-table>` 展示酒款/酒厂/风格/价格。
  - 封面和酒馆名称可点击跳转酒馆详情。
  - 移动端自适应：封面和内容上下排列。

### 2026-06-17 — /api/me 补充 managed_pubs（按角色展示管理的酒馆）
- **目的**：`GET /api/me` 返回用户管理的酒馆列表：管理员（role=2）显示全部酒馆，商家（role=1）显示自己名下的酒馆，普通用户（role=0）返回空数组。
- **后端修改**：
  - `src/schema/schemas_auth.py`：`CurrentUserResponse` 新增 `managed_pubs: List[PubResponse] = []`。
  - `src/repositories/pubs_repository.py`：新增 `list_by_merchant(merchant_user_id)` 和 `list_all_pubs()`。
  - `src/services/pubs_service.py`：新增 `get_managed_pubs(role, user_id)` 按角色分发。
  - `src/api/auth.py`：`/me` 端点注入 `db` 依赖，调用 `PubsService.get_managed_pubs()` 并返回 `managed_pubs`。
- **前端修改**：
  - `frontend/src/types/user.ts`：`UserProfile` 新增 `managed_pubs: PubInfo[]`。
  - `frontend/src/views/UserProfile.vue`：新增「管理的酒馆」el-table 区块，每行含"编辑"按钮，点击弹出浮动编辑弹窗（名称/地址/电话/营业时间/封面URL/营业状态），保存调用 `PUT /api/pubs/{id}` 后自动刷新用户信息。

### 2026-06-17 — 管理酒馆新增浮动编辑弹窗
- **目的**：在用户信息页的管理酒馆表格中，点击"编辑"不再跳转详情页，而是弹出 `el-dialog` 浮层表单直接修改酒馆信息。
- **前端修改**：
  - `frontend/src/types/pubs.ts`：新增 `PubUpdatePayload`（pub_name/address/contact_phone/business_hours/cover_url/status）。
  - `frontend/src/api/pubs.ts`：新增 `updatePub(pubId, payload)`，调用 `PUT /api/pubs/{pubId}`。
  - `frontend/src/views/UserProfile.vue`：
    - 新增编辑弹窗 `el-dialog` + `el-form`（名称/地址/电话/营业时间/封面URL/营业状态 switch）。
    - `openEditDialog(pub)` 将选中酒馆数据填入表单。
    - `handleEditSubmit` 调 `updatePub` → 成功后关闭弹窗并刷新 `store.fetchProfile()` 更新表格。`managed_pubs: List[PubResponse] = []`。

- Redis GEO 成员已改为 pub.id
- 启动时自动同步酒馆坐标到 Redis GEO
- 帖子 CRUD：仅作者或 role=2 管理员可修改/删除；所有用户可创建、搜索、查看帖子
- 帖子搜索支持按关键词、用户 ID、状态筛选，按创建时间倒序排列
- 帖子列表/详情接口对未登录用户公开，登录用户额外返回 liked 点赞状态
- 评论接口附带作者昵称（user_nickname）与头像（user_avatar）
- 前端路由守卫：meta.public: true 免登录直接访问，meta.requiresAuth: true 强制跳转登录页
- 数据库表 posts 如缺少列（title 等），运行 scripts/migrate_posts.py 补充

## 前端变更记录
- 用户端信息架构：导航改为“找酒/我的”，首页对外开放，用户信息页需登录。
- 首页功能：支持输入酒款、经纬度、范围与是否在售，并调用 /api/pubs/by-beer-nearby。
- 新增前端模块：frontend/src/api/pubs.ts、frontend/src/types/pubs.ts。
- 搜索结果支持排序：价格升序/降序、距离从近到远。
- 首页改为单卡片布局：搜索表单与结果列表合并展示，移除价格/距离/在售筛选项。
- 排序控件移至搜索右侧，并在结果区显示当前排序。
- 酒馆详情页不再展示经纬度。
- 酒款搜索结果新增展示酒款风格字段。
- 酒馆详情页新增到店路径提示（步行/驾车、距离与时间）。
- 前端整体升级为精酿主题：新增首页 Hero 与搜索面板布局、深色材质风格、登录/注册双栏布局与详情页信息卡优化。
- 主题细化为高端精酿酒馆：暖棕/琥珀/深咖主色，卡片玻璃拟态与柔和阴影，表单/表格/标签/按钮统一暗色与动效。
- 主题切换为“清新轻奢”浅色系：CSS 变量 --brew-bg: #F8F7F4（暖灰底），--brew-surface: #FFFFFF，--brew-accent: #C2A87A（香槟金），全局覆盖 Element Plus 组件配色。
- 注册页新增角色选择（普通用户/商家），注册时传入 role 字段。
- 首页重构：移除 Hero 操作按钮与搜索提示面板，搜索/定位按钮内联到表单内，搜索区改为单列布局。
- 位置显示改为物理地址：前端调用后端 /api/location/reverse-geocode 将经纬度转为地址文本展示。
- 新增社区功能（完整前后端）：
  - 后端：帖子 CRUD、评论 CRUD、点赞切换/状态查询；评论/帖子响应附带作者昵称与头像。
  - 新增 get_optional_user 依赖注入：公开接口无 Token 时返回匿名视图，有 Token 时自动附带当前用户的点赞状态。
  - 前端页面：社区列表页 Community.vue（Hero 横幅 + 搜索 + 帖子卡片）、帖子详情页 PostDetail.vue（内容 + 点赞 + 评论列表/发表评论 + 作者可编辑删除）、发帖/编辑页 PostEditor.vue（创建/编辑复用同一组件）。
  - 社区列表页新增 Tab 切换：全部帖子 / 我的帖子 / 我赞过的，后两者需登录后可见。
  - 路由：/community（公开）、/community/create（需登录）、/community/:id（公开）、/community/:id/edit（需登录）。
  - 路由守卫约定：meta.public: true 免登录，meta.requiresAuth: true 强制登录。
  - 导航菜单新增「社区」入口。
- 修复头像显示：后端新增 StaticFiles 挂载 /api/avatars，上传改为存储相对 URL，所有接口响应统一通过 normalize_avatar_url() 规范化；Vite 添加 /api 代理确保开发环境下 <img> 标签也能正常加载头像。
- AI 侍酒师 LLM 调用优化：关闭 DeepSeek thinking 思考模式（`thinking:disabled`，速度提升主要手段）、启用 JSON 模式输出（`response_format:json_object`）、max_tokens=2048 限长、超时从 100s 缩短至 30s。

### 2026-06-17 — 新增「我的酒馆」导航入口与酒单管理
- **目的**：在顶部「···」下拉菜单中补充「我的酒馆」栏目，管理员可查看全部酒馆并管理酒单，商家可管理自有酒馆的酒单。
- **前端修改**：
  - `frontend/src/layouts/MainLayout.vue`：移除顶部导航栏独立的「我的」菜单项，新增「···」三点下拉按钮（el-dropdown），下拉菜单包含「我的」（→ /profile）和「我的酒馆」（→ /my-pubs，仅 role=1/2 可见）。新增 `canManagePubs` computed + 下拉按钮样式。
  - `frontend/src/router/index.ts`：新增 `/my-pubs` 路由（name: myPubs, meta.requiresAuth: true）。
  - `frontend/src/types/beer.ts`（新建）：定义 `BeerItem`、`BeerListResponse`、`BeerCreatePayload`、`BeerUpdatePayload`。
  - `frontend/src/api/beer.ts`（新建）：封装 `fetchBeersByPub`、`createBeer`、`updateBeer`、`deleteBeer` API 调用。
  - `frontend/src/types/pubs.ts`：新增 `PubListResponse`。
  - `frontend/src/api/pubs.ts`：新增 `fetchAllPubs()`，调用 `GET /pubs?limit=999`。
  - `frontend/src/views/MyPubs.vue`（新建）：我的酒馆页面，包含：
    - 角色标签（管理员/商家视图）。
    - 管理员：调用 `fetchAllPubs()` 展示全部酒馆；商家：使用 `store.profile.managed_pubs`。
    - 酒馆卡片点击展开/折叠，展开后加载该酒馆的酒单（`fetchBeersByPub`）。
    - 酒单以 `el-table` 展示（酒款名/酒厂/风格/ABV/容量/价格/状态），含「编辑」「删除」操作按钮。
    - 每张酒单上方有「+ 添加酒款」按钮。
    - 编辑/添加共用 `el-dialog` 弹窗表单（名称/酒厂/风格/ABV/容量/价格/状态 switch），提交后自动刷新酒单。
    - 删除酒款需二次确认（`ElMessageBox.confirm`）。
