"""
全栈 AI 智能代码工作台 · 预置知识库
200+ 条常见编程问答，覆盖 Git/Docker/SQL/Python/系统设计/前端/网络
所有内容已脱敏，仅供 RAG 检索和离线回答使用
"""
from typing import TypedDict

class KnowledgeEntry(TypedDict):
    title: str
    category: str
    content: str

KNOWLEDGE_BASE: list[KnowledgeEntry] = [
    # ── Git ──────────────────────────────────────────────────────────────────
    {
        "title": "Git 常用命令速查",
        "category": "git",
        "content": (
            "git init                          # 初始化本地仓库\n"
            "git clone <url>                   # 克隆远程仓库\n"
            "git add .                         # 添加所有文件到暂存区\n"
            "git commit -m 'message'           # 提交并写注释\n"
            "git push origin main              # 推送到远程 main 分支\n"
            "git pull origin main              # 拉取并合并远程更新\n"
            "git status                        # 查看当前工作区状态\n"
            "git log --oneline                 # 查看简洁提交历史\n"
            "git branch                        # 查看本地所有分支\n"
            "git checkout -b dev               # 创建并切换到 dev 分支\n"
            "git merge dev                     # 把 dev 合并到当前分支\n"
            "git stash                         # 暂存当前修改（不提交）\n"
            "git stash pop                     # 恢复暂存的修改\n"
            "git reset --hard HEAD~1           # 撤销最后一次提交\n"
            "git remote -v                     # 查看远程仓库地址\n"
            "git fetch                         # 拉取远程更新但不合并"
        ),
    },
    {
        "title": "Git 冲突解决方法",
        "category": "git",
        "content": (
            "Git 冲突产生原因：两个分支对同一文件的同一处做了不同修改，合并时 Git 无法自动决定保留哪个。\n\n"
            "解决步骤：\n"
            "1. git status 查看哪些文件冲突\n"
            "2. 打开冲突文件，找到<<<<<<< HEAD、=======、>>>>>>>标记\n"
            "3. 手动编辑，删除标记，保留想要的代码\n"
            "4. git add <file> 标记为已解决\n"
            "5. git commit 完成合并提交\n\n"
            "建议：冲突前先 git pull --rebase 或使用 Git GUI 工具可视化解决。"
        ),
    },
    {
        "title": "Git SSH Key 配置",
        "category": "git",
        "content": (
            "1. ssh-keygen -t ed25519 -C 'your_email@example.com'  # 生成密钥对\n"
            "2. 回车默认路径，建议设密码保护\n"
            "3. cat ~/.ssh/id_ed25519.pub  # 复制公钥内容\n"
            "4. 打开 GitHub → Settings → SSH Keys → New SSH Key → 粘贴\n"
            "5. ssh -T git@github.com  # 验证是否成功\n\n"
            "常见错误：Permission denied (publickey) 通常是公钥未添加或 SSH agent 未启动。\n"
            "解决：eval \"$(ssh-agent -s)\" && ssh-add ~/.ssh/id_ed25519"
        ),
    },
    {
        "title": "Git 工作流与分支管理",
        "category": "git",
        "content": (
            "常用 Git 工作流：Git Flow\n\n"
            "main（主分支）：稳定版本，始终可发布\n"
            "develop（开发分支）：集成交互，下一版本基准\n"
            "feature/*（功能分支）：从 develop 拉取，开发完成后合并回 develop\n"
            "release/*（发布分支）：从 develop 拉取，修复 bug 后合并回 develop 和 main\n"
            "hotfix/*（热修复分支）：从 main 拉取，修复后合并回 main 和 develop\n\n"
            "GitHub Flow（更轻量）：\n"
            "main 分支始终可部署，功能开发在 feature 分支，完成后 pull request 合并到 main。"
        ),
    },
    {
        "title": "Git 撤销修改操作汇总",
        "category": "git",
        "content": (
            "场景1：工作区修改未提交，想全部撤销\n"
            "git checkout -- <file> 或 git restore <file>\n\n"
            "场景2：文件已 add 到暂存区，想撤销\n"
            "git reset HEAD <file>  # 撤销 add，文件回到工作区\n\n"
            "场景3：已 commit，想撤销提交但保留修改\n"
            "git reset --soft HEAD~1  # 撤销提交，修改保留在暂存区\n\n"
            "场景4：已 commit，想完全撤销（包括修改）\n"
            "git reset --hard HEAD~1  # 彻底撤销，修改也消失，慎用\n\n"
            "场景5：想丢弃某个文件的所有本地修改\n"
            "git checkout -- that_file 或 git restore that_file"
        ),
    },
    # ── Docker ───────────────────────────────────────────────────────────────
    {
        "title": "Docker 常用命令",
        "category": "docker",
        "content": (
            "# 镜像操作\n"
            "docker images                    # 查看本地镜像\n"
            "docker pull nginx:latest         # 拉取镜像\n"
            "docker rmi <image_id>            # 删除镜像\n"
            "docker build -t myapp:1.0 .      # 从 Dockerfile 构建镜像\n\n"
            "# 容器操作\n"
            "docker ps -a                     # 查看所有容器（含停止的）\n"
            "docker run -d -p 8080:80 --name web nginx  # 后台运行并映射端口\n"
            "docker start <container_id>       # 启动已停止的容器\n"
            "docker stop <container_id>        # 停止容器\n"
            "docker restart <container_id>     # 重启容器\n"
            "docker rm <container_id>          # 删除容器\n\n"
            "# 进入容器 & 日志\n"
            "docker exec -it <container_id> /bin/bash  # 进入容器终端\n"
            "docker logs -f <container_id>    # 查看实时日志\n\n"
            "# 清理\n"
            "docker system prune -a           # 删除所有未使用的镜像、容器、网络"
        ),
    },
    {
        "title": "Dockerfile 最佳实践",
        "category": "docker",
        "content": (
            "# 使用多阶段构建，减小镜像体积\n"
            "FROM python:3.11-slim AS builder\n"
            "WORKDIR /app\n"
            "COPY requirements.txt .\n"
            "RUN pip install --no-cache-dir -r requirements.txt\n\n"
            "FROM python:3.11-slim\n"
            "WORKDIR /app\n"
            "COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages\n"
            "COPY . .\n"
            "EXPOSE 8000\n"
            "CMD ['python', 'main.py']\n\n"
            "要点：\n"
            "- 基础镜像选 slim 或 alpine 减小体积\n"
            "- .dockerignore 文件排除不需要的文件（如 node_modules）\n"
            "- COPY 和 RUN 尽量合并减少层数\n"
            "- 不使用 root 运行容器（USER instruction）\n"
            "- 标签指定版本，不用 latest"
        ),
    },
    {
        "title": "Docker Compose 编排多个服务",
        "category": "docker",
        "content": (
            "version: '3.8'\n"
            "services:\n"
            "  app:\n"
            "    build: .\n"
            "    ports:\n"
            "      - '8000:8000'\n"
            "    environment:\n"
            "      - DB_HOST=db\n"
            "      - REDIS_HOST=redis\n"
            "    depends_on:\n"
            "      - db\n"
            "      - redis\n\n"
            "  db:\n"
            "    image: mysql:8.0\n"
            "    environment:\n"
            "      MYSQL_ROOT_PASSWORD: secret\n"
            "      MYSQL_DATABASE: myapp\n"
            "    volumes:\n"
            "      - db_data:/var/lib/mysql\n\n"
            "  redis:\n"
            "    image: redis:7-alpine\n\n"
            "volumes:\n"
            "  db_data:\n\n"
            "常用命令：\n"
            "docker compose up -d              # 后台启动所有服务\n"
            "docker compose down              # 停止并移除容器\n"
            "docker compose logs -f app       # 查看 app 日志\n"
            "docker compose exec app bash     # 进入 app 容器"
        ),
    },
    {
        "title": "Docker 网络与数据持久化",
        "category": "docker",
        "content": (
            "# Docker 网络模式\n"
            "- bridge（默认）：容器间通过 IP 通信\n"
            "- host：容器直接使用宿主机网络\n"
            "- overlay：跨主机容器通信（Swarm 模式）\n\n"
            "# 创建自定义网络（容器互联）\n"
            "docker network create mynet\n"
            "docker run --network mynet --name app app_image\n"
            "docker run --network mynet --name db db_image\n"
            "# app 和 db 可以通过容器名互相访问\n\n"
            "# 数据持久化 - 数据卷 Volume\n"
            "docker volume create mydata\n"
            "docker run -v mydata:/app/data --name app app_image\n"
            "# 即使容器删除，数据依然保存在 mydata 卷中\n\n"
            "# 绑定宿主机目录（测试用，生产推荐用 Volume）\n"
            "docker run -v /host/path:/container/path --name app app_image"
        ),
    },
    # ── SQL ──────────────────────────────────────────────────────────────────
    {
        "title": "SQL 常用查询语句",
        "category": "sql",
        "content": (
            "-- 基础查询\n"
            "SELECT * FROM users WHERE age > 18 ORDER BY created_at DESC LIMIT 10;\n\n"
            "-- 聚合统计\n"
            "SELECT department, COUNT(*) as cnt, AVG(salary) as avg_sal\n"
            "FROM employees\n"
            "GROUP BY department\n"
            "HAVING COUNT(*) > 5\n"
            "ORDER BY avg_sal DESC;\n\n"
            "-- 多表连接\n"
            "SELECT u.name, o.order_id, o.total\n"
            "FROM users u\n"
            "INNER JOIN orders o ON u.id = o.user_id\n"
            "WHERE u.status = 'active';\n\n"
            "-- 子查询\n"
            "SELECT name FROM users\n"
            "WHERE id IN (SELECT user_id FROM orders WHERE total > 1000);\n\n"
            "-- 窗口函数\n"
            "SELECT name, salary,\n"
            "  RANK() OVER (ORDER BY salary DESC) as rank\n"
            "FROM employees;"
        ),
    },
    {
        "title": "SQL 索引优化与慢查询分析",
        "category": "sql",
        "content": (
            "-- 创建索引（加速查询）\n"
            "CREATE INDEX idx_users_email ON users(email);\n"
            "CREATE INDEX idx_orders_user_date ON orders(user_id, created_at);\n\n"
            "-- 复合索引遵循最左前缀原则\n"
            "-- idx_orders_user_date 可以加速：WHERE user_id = ? / WHERE user_id = ? AND created_at > ?\n"
            "-- 但无法加速 WHERE created_at > ?\n\n"
            "-- 慢查询分析\n"
            "SHOW VARIABLES LIKE 'slow_query_log';\n"
            "SET GLOBAL slow_query_log = 'ON';\n"
            "SET GLOBAL long_query_time = 1;  -- 超过1秒记录\n\n"
            "-- EXPLAIN 分析执行计划\n"
            "EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';\n"
            "-- 关注 type（最好到 ref/range）、key（使用了哪个索引）、rows（扫描行数）"
        ),
    },
    {
        "title": "SQL 事务与锁机制",
        "category": "sql",
        "content": (
            "-- 事务基本操作\n"
            "START TRANSACTION;\n"
            "UPDATE accounts SET balance = balance - 100 WHERE user_id = 1;\n"
            "UPDATE accounts SET balance = balance + 100 WHERE user_id = 2;\n"
            "COMMIT;  -- 提交事务\n"
            "-- ROLLBACK;  -- 出错时回滚\n\n"
            "-- 事务隔离级别\n"
            "SET TRANSACTION ISOLATION LEVEL READ COMMITTED;\n\n"
            "READ COMMITTED：只能读取已提交的数据（防止脏读）\n"
            "REPEATABLE READ：同一事务内多次读取结果一致（MySQL 默认，防止脏读和不可重复读）\n"
            "SERIALIZABLE：完全串行化，最高隔离但性能最差\n\n"
            "-- 行锁与表锁\n"
            "SELECT * FROM users WHERE id = 1 FOR UPDATE;  -- 行锁，阻止其他事务修改\n"
            "LOCK TABLE users WRITE;  -- 表锁\n\n"
            "-- 死锁处理\n"
            "MySQL 会自动检测死锁并回滚代价最小的事务。\n"
            "避免死锁：按固定顺序访问资源、减少事务时长、减少锁粒度。"
        ),
    },
    {
        "title": "SQL 常见面试题精选",
        "category": "sql",
        "content": (
            "Q1：删除表中重复记录，只保留最新一条\n"
            "DELETE FROM orders\n"
            "WHERE id NOT IN (\n"
            "  SELECT max_id FROM (\n"
            "    SELECT MAX(id) as max_id FROM orders GROUP BY user_id, product_id\n"
            "  ) t\n"
            ");\n\n"
            "Q2：查找各部门工资最高的员工\n"
            "SELECT e.name, e.salary, e.department\n"
            "FROM employees e\n"
            "INNER JOIN (\n"
            "  SELECT department, MAX(salary) as max_sal\n"
            "  FROM employees GROUP BY department\n"
            ") m ON e.department = m.department AND e.salary = m.max_sal;\n\n"
            "Q3：连续登录天数计算\n"
            "SELECT user_id, COUNT(DISTINCT login_date) as days\n"
            "FROM login_records\n"
            "GROUP BY user_id\n"
            "HAVING COUNT(DISTINCT login_date) >= 7;\n\n"
            "Q4：分页查询优化（大数据量）\n"
            "-- 禁止：SELECT * FROM orders LIMIT 100000, 20  -- 扫描10万行\n"
            "-- 推荐：SELECT * FROM orders WHERE id > 100000 ORDER BY id LIMIT 20"
        ),
    },
    # ── Python ───────────────────────────────────────────────────────────────
    {
        "title": "Python 装饰器与高阶函数",
        "category": "python",
        "content": (
            "# 基础装饰器\n"
            "def log_calls(func):\n"
            "    def wrapper(*args, **kwargs):\n"
            "        print(f'调用 {func.__name__}')\n"
            "        result = func(*args, **kwargs)\n"
            "        print(f'{func.__name__} 执行完毕')\n"
            "        return result\n"
            "    wrapper.__name__ = func.__name__\n"
            "    return wrapper\n\n"
            "@log_calls\n"
            "def add(a, b):\n"
            "    return a + b\n\n"
            "# 带参数的装饰器\n"
            "def retry(max_times=3):\n"
            "    def decorator(func):\n"
            "        def wrapper(*args, **kwargs):\n"
            "            for _ in range(max_times):\n"
            "                try:\n"
            "                    return func(*args, **kwargs)\n"
            "                except Exception:\n"
            "                    continue\n"
            "        return wrapper\n"
            "    return decorator\n\n"
            "@retry(max_times=5)\n"
            "def call_api(): ..."
        ),
    },
    {
        "title": "Python 异步编程 async/await",
        "category": "python",
        "content": (
            "import asyncio\n\n"
            "async def fetch(url):\n"
            "    async with aiohttp.ClientSession() as session:\n"
            "        async with session.get(url) as resp:\n"
            "            return await resp.json()\n\n"
            "async def main():\n"
            "    # 并发执行多个请求\n"
            "    tasks = [fetch(url) for url in urls]\n"
            "    results = await asyncio.gather(*tasks)\n\n"
            "    # 顺序执行\n"
            "    for url in urls:\n"
            "        result = await fetch(url)\n\n"
            "asyncio.run(main())\n\n"
            "# 与 FastAPI 结合\n"
            "@app.get('/items/{item_id}')\n"
            "async def read_item(item_id: int):\n"
            "    item = await fetch_item_from_db(item_id)\n"
            "    return item\n\n"
            "# 关键点：\n"
            "- async def 定义协程函数\n"
            "- await 等待另一个协程完成（不阻塞事件循环）\n"
            "- asyncio.gather 并发等待多个协程\n"
            "- asyncio.create_task 后台调度协程"
        ),
    },
    {
        "title": "Python 常见报错与处理",
        "category": "python",
        "content": (
            "1. TypeError: 'NoneType' object is not callable\n"
            "原因：变量为 None 时调用了它。\n"
            "解决：if obj is not None: obj()\n\n"
            "2. IndexError: list index out of range\n"
            "原因：访问了不存在的索引。\n"
            "解决：if len(lst) > index: item = lst[index]\n\n"
            "3. KeyError: 'some_key'\n"
            "原因：字典中没有该键。\n"
            "解决：dict.get('key', default) 或 collections.defaultdict\n\n"
            "4. ImportError: No module named 'xxx'\n"
            "原因：模块未安装或路径不对。\n"
            "解决：pip install xxx 或检查 PYTHONPATH\n\n"
            "5. RecursionError: maximum recursion depth exceeded\n"
            "原因：递归没有终止条件或层次过深。\n"
            "解决：加递归深度限制 sys.setrecursionlimit(10000)\n\n"
            "6. AttributeError: 'xxx' object has no attribute 'yyy'\n"
            "原因：对象没有该属性。\n"
            "解决：hasattr(obj, 'attr') 或 getattr(obj, 'attr', None)"
        ),
    },
    {
        "title": "Python 内存管理与性能优化",
        "category": "python",
        "content": (
            "# 避免内存泄漏：及时释放大对象\n"
            "large_list = None  # 解除引用\n\n"
            "# 生成器代替列表（省内存）\n"
            "def get_lines(path):\n"
            "    with open(path) as f:\n"
            "        for line in f:\n"
            "            yield line  # 不一次性读入内存\n\n"
            "# 使用 __slots__ 减少对象内存开销\n"
            "class Point:\n"
            "    __slots__ = ('x', 'y')  # 限制实例属性，省内存\n\n"
            "# 字符串拼接优化\n"
            "parts = ['hello', 'world', 'python']\n"
            "result = ''.join(parts)  # 比 + 拼接快\n\n"
            "# 列表推导式 vs for 循环\n"
            "squares = [x**2 for x in range(10000)]  # 比 for 循环快\n\n"
            "# 善用缓存（lru_cache）\n"
            "from functools import lru_cache\n\n"
            "@lru_cache(maxsize=128)\n"
            "def fib(n): return n if n < 2 else fib(n-1) + fib(n-2)"
        ),
    },
    {
        "title": "Python 面向对象设计模式",
        "category": "python",
        "content": (
            "# 单例模式\n"
            "class Database:\n"
            "    _instance = None\n"
            "    def __new__(cls):\n"
            "        if cls._instance is None:\n"
            "            cls._instance = super().__new__(cls)\n"
            "        return cls._instance\n\n"
            "# 工厂模式\n"
            "class Factory:\n"
            "    @staticmethod\n"
            "    def create_product(kind: str):\n"
            "        if kind == 'A': return ProductA()\n"
            "        if kind == 'B': return ProductB()\n"
            "        raise ValueError(f'Unknown kind: {kind}')\n\n"
            "# 观察者模式\n"
            "class Observable:\n"
            "    def __init__(self):\n"
            "        self._observers = []\n"
            "    def add_observer(self, obs): self._observers.append(obs)\n"
            "    def notify(self, *args):\n"
            "        for obs in self._observers: obs.update(*args)\n\n"
            "# 策略模式\n"
            "class SortStrategy:\n"
            "    def sort(self, data): raise NotImplementedError\n\n"
            "class QuickSort(SortStrategy):\n"
            "    def sort(self, data): ... # 快速排序实现"
        ),
    },
    # ── 系统设计 ─────────────────────────────────────────────────────────────
    {
        "title": "系统设计：高并发架构要点",
        "category": "system_design",
        "content": (
            "高并发三板斧：缓存、异步、拆分\n\n"
            "1. 缓存层\n"
            "- 客户端缓存（LocalStorage / CDN）\n"
            "- 接入层缓存（Nginx 缓存、Redis）\n"
            "- 应用层缓存（Redis Cluster、Memcached）\n"
            "- 数据库缓存（Query Cache、Buffer Pool）\n\n"
            "2. 异步处理\n"
            "- 消息队列解耦（Kafka / RabbitMQ / Redis Stream）\n"
            "- 削峰填谷：写入先入队列，异步处理\n"
            "- 用户体验：先返回成功，后台慢慢处理\n\n"
            "3. 水平拆分\n"
            "- 分库分表：用户表按 user_id 分片\n"
            "- 微服务拆分：用户服务、订单服务、支付服务独立部署\n"
            "- 读写分离：主库写、从库读\n\n"
            "4. 限流与降级\n"
            "- 令牌桶算法限流（Redis + Lua）\n"
            "- 非核心功能降级：关闭评论、推荐等功能\n"
            "- 熔断机制：Hystrix / Sentinel"
        ),
    },
    {
        "title": "系统设计：RESTful API 设计规范",
        "category": "system_design",
        "content": (
            "RESTful 设计原则：\n\n"
            "GET    /users          # 获取用户列表\n"
            "GET    /users/{id}     # 获取单个用户\n"
            "POST   /users          # 创建用户\n"
            "PUT    /users/{id}     # 更新用户（完整）\n"
            "PATCH  /users/{id}     # 部分更新\n"
            "DELETE /users/{id}     # 删除用户\n\n"
            "状态码规范：\n"
            "200 OK - 成功\n"
            "201 Created - 资源创建成功\n"
            "400 Bad Request - 请求参数错误\n"
            "401 Unauthorized - 未认证\n"
            "403 Forbidden - 无权限\n"
            "404 Not Found - 资源不存在\n"
            "429 Too Many Requests - 请求过于频繁\n"
            "500 Internal Server Error - 服务器内部错误\n\n"
            "响应格式：\n"
            '{"code": 0, "message": "success", "data": {...}}\n\n'
            "分页查询：\n"
            "GET /users?page=1&page_size=20&sort=created_at&order=desc"
        ),
    },
    {
        "title": "系统设计：微服务与分布式事务",
        "category": "system_design",
        "content": (
            "微服务拆分原则：\n"
            "- 高内聚低耦合：一个服务完成一个业务领域\n"
            "- 独立部署：每个服务独立打包、部署、扩容\n"
            "- API 通信：服务间通过 HTTP/gRPC 或消息队列通信\n\n"
            "分布式事务解决方案：\n\n"
            "1. 两阶段提交（2PC）\n"
            "- Prepare 阶段：所有参与者 prepare\n"
            "- Commit 阶段：全部提交或全部回滚\n"
            "- 缺点：同步阻塞、单点故障\n\n"
            "2. Saga 模式（异步补偿）\n"
            "- 每个子事务有对应的补偿事务\n"
            "- 失败时逆向执行补偿事务\n"
            "- 适用于长事务场景\n\n"
            "3. 本地消息表 + 消息队列\n"
            "- 业务表和消息表在同一数据库\n"
            "- 消息队列异步处理\n"
            "- 最终一致性，CAP 优先 A（可用性）\n\n"
            "4. TCC（Try-Confirm-Cancel）\n"
            "- Try：预留资源 / Confirm：确认执行 / Cancel：取消释放"
        ),
    },
    {
        "title": "系统设计：消息队列对比与选型",
        "category": "system_design",
        "content": (
            "Kafka（高吞吐日志场景）：\n"
            "- 优点：百万级 TPS、持久化、分布式天然支持\n"
            "- 缺点：延迟较高、配置复杂\n"
            "- 适用：日志采集、大数据分析、实时流处理\n\n"
            "RabbitMQ（可靠消息、灵活路由）：\n"
            "- 优点：支持多种交换器、延迟队列、死信队列\n"
            "- 缺点：吞吐量一般（万级 TPS）\n"
            "- 适用：订单处理、异步任务、Webhooks\n\n"
            "Redis Stream（轻量实时场景）：\n"
            "- 优点：低延迟、与 Redis 生态整合简单\n"
            "- 缺点：数据不能持久化（需配合 AOF/RDB）\n"
            "- 适用：实时通知、轻量级异步队列\n\n"
            "选型建议：\n"
            "- 日志/大数据/流处理 → Kafka\n"
            "- 企业级可靠消息/复杂路由 → RabbitMQ\n"
            "- 低延迟轻量队列/Redis 已有生态 → Redis Stream"
        ),
    },
    # ── 网络 / HTTP ──────────────────────────────────────────────────────────
    {
        "title": "HTTP 状态码速查",
        "category": "network",
        "content": (
            "1xx 信息性：\n"
            "100 Continue - 可继续发送请求\n"
            "101 Switching Protocols - 协议升级（如 HTTP → WebSocket）\n\n"
            "2xx 成功：\n"
            "200 OK - 请求成功\n"
            "201 Created - 资源创建成功\n"
            "204 No Content - 成功但无返回内容（如 DELETE）\n\n"
            "3xx 重定向：\n"
            "301 Moved Permanently - 永久重定向（缓存）\n"
            "302 Found - 临时重定向（不缓存）\n"
            "304 Not Modified - 走缓存（协商缓存）\n\n"
            "4xx 客户端错误：\n"
            "400 Bad Request - 请求语法错误\n"
            "401 Unauthorized - 需要认证\n"
            "403 Forbidden - 无权限\n"
            "404 Not Found - 资源不存在\n"
            "429 Too Many Requests - 请求频率超限\n\n"
            "5xx 服务端错误：\n"
            "500 Internal Server Error - 服务器内部错误\n"
            "502 Bad Gateway - 上游服务挂了\n"
            "503 Service Unavailable - 服务不可用（过载维护）\n"
            "504 Gateway Timeout - 上游超时"
        ),
    },
    {
        "title": "HTTP 与 WebSocket 区别",
        "category": "network",
        "content": (
            "HTTP：\n"
            "- 客户端发起请求，服务端响应后断开\n"
            "- 单向通信：只有客户端能主动发请求\n"
            "- 无状态：每个请求互相独立\n"
            "- 实时性差：想获取新数据只能轮询\n"
            "- 缓存支持好：有完善的协商缓存机制\n\n"
            "WebSocket：\n"
            "- 长连接：建立一次 TCP 连接后持续保持\n"
            "- 双向通信：客户端和服务端都能主动发消息\n"
            "- 有状态：连接建立后可携带身份信息\n"
            "- 实时性强：消息可实时推送\n"
            "- 无原生缓存支持\n\n"
            "选型建议：\n"
            "- 聊天/实时协作/游戏/推送 → WebSocket\n"
            "- REST API/文件上传/查询 → HTTP\n\n"
            "WebSocket 建立过程：\n"
            "1. 客户端发送 HTTP 请求，带 Upgrade: websocket 头\n"
            "2. 服务端响应 101 Switching Protocols\n"
            "3. TCP 连接升级为 WebSocket，开始双向通信"
        ),
    },
    {
        "title": "HTTPS 工作原理与 TLS 握手",
        "category": "network",
        "content": (
            "HTTPS = HTTP + TLS（SSL）\n\n"
            "TLS 1.2 握手过程（ RSA 密钥交换）：\n\n"
            "1. 客户端 → 服务端：ClientHello\n"
            "   （发送支持的 TLS 版本、加密套件列表、随机数A）\n\n"
            "2. 服务端 → 客户端：ServerHello + 证书 + ServerKeyExchange\n"
            "   （发送证书链（含公钥）、随机数B）\n\n"
            "3. 客户端验证证书：\n"
            "   - 验证证书链是否可信\n"
            "   - 用 CA 公钥验证签名\n"
            "   - 检查域名、有效期\n\n"
            "4. 客户端 → 服务端：Premaster Secret\n"
            "   - 用服务端公钥加密随机数C，发送给服务端\n\n"
            "5. 双方用 Premaster Secret + 随机数A/B 导出主密钥\n\n"
            "6. 切换到加密通信，后续数据用主密钥加解密\n\n"
            "TLS 1.3 改进：\n"
            "- 握手从 2-RTT 降为 1-RTT\n"
            "- 0-RTT 快速打开（首次连接后可缓存 session）\n"
            "- 废除 RSA 密钥交换（前向安全）"
        ),
    },
    # ── 前端 ─────────────────────────────────────────────────────────────────
    {
        "title": "JavaScript ES6+ 核心语法",
        "category": "frontend",
        "content": (
            "// 解构赋值\n"
            "const { name, age } = user;\n"
            "const [first, second] = items;\n\n"
            "// 箭头函数\n"
            "const add = (a, b) => a + b;\n"
            "const fetchData = async () => { ... };\n\n"
            "// 展开运算符\n"
            "const merged = { ...obj1, ...obj2 };\n"
            "const sum = (...nums) => nums.reduce((a, b) => a + b, 0);\n\n"
            "// Promise 与 async/await\n"
            "const result = await fetch('/api/data').then(r => r.json());\n"
            "try {\n"
            "  const data = await fetchData();\n"
            "} catch (err) {\n"
            "  console.error(err);\n"
            "}\n\n"
            "// 数组方法\n"
            "items.map(i => i.name);        // 映射\n"
            "items.filter(i => i.active);   // 过滤\n"
            "items.reduce((sum, i) => sum + i.price, 0); // 累计\n"
            "items.find(i => i.id === 1);  // 查找\n\n"
            "// 可选链与空值合并\n"
            "const city = user?.profile?.address?.city;\n"
            "const name = value ?? 'default';"
        ),
    },
    {
        "title": "Vue3 组合式 API 与响应式原理",
        "category": "frontend",
        "content": (
            "// setup() 组合式 API\n"
            "<script setup>\n"
            "import { ref, reactive, computed, watch, onMounted } from 'vue';\n\n"
            "const count = ref(0);  // 响应式 ref\n"
            "const state = reactive({ name: 'Tom', age: 20 });  // 响应式对象\n\n"
            "const doubled = computed(() => count.value * 2);  // 计算属性\n\n"
            "watch(count, (newVal, oldVal) => {\n"
            "  console.log(`count changed: ${oldVal} -> ${newVal}`);\n"
            "});\n\n"
            "onMounted(() => {\n"
            "  console.log('组件挂载完成');\n"
            "});\n\n"
            "function increment() {\n"
            "  count.value++;  // 修改 ref 的值要用 .value\n"
            "}\n"
            "</script>\n\n"
            "// Vue3 响应式原理（Proxy）\n"
            "// ref → get/set 拦截 → .value\n"
            "// reactive → Proxy 深度劫持对象\n\n"
            "// 生命周期钩子（组合式）\n"
            "// onMounted / onUpdated / onUnmounted\n"
            "// onBeforeMount / onBeforeUpdate / onBeforeUnmount"
        ),
    },
    {
        "title": "TypeScript 类型系统详解",
        "category": "frontend",
        "content": (
            "// 基础类型\n"
            "let name: string = 'Tom';\n"
            "let age: number = 25;\n"
            "let active: boolean = true;\n"
            "let arr: string[] = ['a', 'b'];\n"
            "let tuple: [string, number] = ['hello', 42];\n\n"
            "// 接口与类型别名\n"
            "interface User { id: number; name: string; age?: number; }\n"
            "type Status = 'pending' | 'success' | 'error';\n\n"
            "// 泛型\n"
            "function identity<T>(arg: T): T { return arg; }\n"
            "interface ApiResponse<T> { code: number; data: T; }\n\n"
            "// keyof 与类型约束\n"
            "function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {\n"
            "  return obj[key];\n"
            "}\n\n"
            "// 工具类型\n"
            "Partial<User>      // 所有属性变为可选\n"
            "Required<User>     // 所有属性变为必需\n"
            "Pick<User, 'id' | 'name'>  // 选取部分属性\n"
            "Omit<User, 'age'>  // 去掉部分属性\n"
            "Record<string, number>  // 键值对类型"
        ),
    },
    {
        "title": "前端性能优化策略",
        "category": "frontend",
        "content": (
            "1. 减少请求数量\n"
            "- 资源合并（CSS/JS 打包）\n"
            "- 图片合并（Sprite / SVG Inline）\n"
            "- HTTP/2 多路复用减少连接数\n\n"
            "2. 减少请求体积\n"
            "- 代码压缩（terser / cssnano）\n"
            "- Tree Shaking 消除死代码\n"
            "- 图片压缩（WebP / AVIF）\n"
            "- Gzip / Brotli 压缩\n\n"
            "3. 缓存策略\n"
            "- 强缓存：Cache-Control / Expires\n"
            "- 协商缓存：ETag / Last-Modified\n"
            "- CDN 加速静态资源\n\n"
            "4. 渲染优化\n"
            "- CSS 放 <head>，JS 放 </body>前\n"
            "- 避免重排（reflow）与重绘（repaint）\n"
            "- 使用 transform/opacity 做动画（GPU 加速）\n"
            "- 虚拟列表处理长列表\n"
            "- 懒加载图片：loading='lazy'\n\n"
            "5. 代码分割与按需加载\n"
            "const Comp = () => import('./Comp.vue');  // 路由懒加载"
        ),
    },
    # ── Redis ────────────────────────────────────────────────────────────────
    {
        "title": "Redis 常用命令与数据结构",
        "category": "redis",
        "content": (
            "# 字符串 String\n"
            "SET name 'Tom' EX 3600    # 设置值并 1 小时过期\n"
            "GET name                   # 获取值\n"
            "INCR page_views            # 原子递增\n"
            "MSET key1 val1 key2 val2  # 批量设置\n\n"
            "# 哈希 Hash（适合存对象）\n"
            "HSET user:1 name 'Tom' age 25\n"
            "HGET user:1 name\n"
            "HGETALL user:1\n"
            "HINCRBY user:1 age 1       # 字段原子递增\n\n"
            "# 列表 List（队列/栈）\n"
            "LPUSH tasks 'task1'         # 左边入队\n"
            "RPOP tasks                 # 右边出队（FIFO 队列）\n"
            "LRANGE tasks 0 -1          # 查看所有元素\n\n"
            "# 集合 Set（去重）\n"
            "SADD tags python java js\n"
            "SMEMBERS tags\n"
            "SISMEMBER tags python      # 是否存在\n\n"
            "# 有序集合 ZSet（排行榜）\n"
            "ZADD leaderboard 100 'Alice' 200 'Bob'\n"
            "ZRANGE leaderboard 0 -1 WITHSCORES\n"
            "ZREVRANGE leaderboard 0 9   # 从高到低前10名"
        ),
    },
    {
        "title": "Redis 缓存策略与分布式锁",
        "category": "redis",
        "content": (
            "# 缓存策略\n\n"
            "1. Cache-Aside（旁路缓存，最常用）\n"
            "读：cache miss → 查 DB → 写入缓存\n"
            "写：更新 DB → 删除缓存（下一次读会回填）\n\n"
            "2. Read-Through / Write-Through\n"
            "读写全部经过缓存层，缓存自己管理 DB\n\n"
            "3. 缓存过期策略\n"
            "- LRU（最近最少使用）：淘汰最久未访问\n"
            "- LFU（最不经常使用）：淘汰访问频率最低\n"
            "- TTL：设置键的存活时间\n\n"
            "# 分布式锁（Redis 实现）\n"
            "SET lock_key request_id NX EX 30  # NX 不存在才设，EX 30秒过期\n"
            "if redis.call('get', KEYS[1]) == ARGV[1] then\n"
            "  return redis.call('del', KEYS[1])\n"
            "else return 0 end\n\n"
            "注意：释放锁时用 Lua 脚本保证原子性，避免误删他人锁。\n"
            "推荐用 Redisson 或 RedLock 算法实现更可靠的分布式锁。"
        ),
    },
    # ── FastAPI / 后端 ───────────────────────────────────────────────────────
    {
        "title": "FastAPI 请求参数与响应模型",
        "category": "fastapi",
        "content": (
            "from fastapi import FastAPI, Query, Path, Body, Header, HTTPException\n"
            "from pydantic import BaseModel, Field\n\n"
            "app = FastAPI()\n\n"
            "# 路径参数\n"
            "@app.get('/items/{item_id}')\n"
            "async def get_item(item_id: int = Path(..., gt=0)):\n"
            "    return {'item_id': item_id}\n\n"
            "# 查询参数\n"
            "@app.get('/search')\n"
            "async def search(q: str = Query(..., min_length=2), page: int = 1):\n"
            "    return {'q': q, 'page': page}\n\n"
            "# 请求体\n"
            "class Item(BaseModel):\n"
            "    name: str = Field(..., min_length=1)\n"
            "    price: float = Field(..., gt=0)\n"
            "    tags: list[str] = []\n\n"
            "@app.post('/items')\n"
            "async def create_item(item: Item):\n"
            "    return item\n\n"
            "# 响应模型\n"
            "class Response(BaseModel):\n"
            "    code: int\n"
            "    data: Item\n\n"
            "@app.post('/items', response_model=Response)"
        ),
    },
    {
        "title": "FastAPI 中间件与依赖注入",
        "category": "fastapi",
        "content": (
            "# 中间件（在每个请求前后执行）\n\n"
            "from fastapi import FastAPI, Request\n"
            "from starlette.middleware.base import BaseHTTPMiddleware\n\n"
            "app = FastAPI()\n\n"
            "class LogMiddleware(BaseHTTPMiddleware):\n"
            "    async def dispatch(self, request: Request, call_next):\n"
            "        print(f'请求: {request.method} {request.url}')\n"
            "        response = await call_next(request)\n"
            "        print(f'响应: {response.status_code}')\n"
            "        return response\n\n"
            "app.add_middleware(LogMiddleware)\n\n"
            "# 依赖注入（可复用逻辑）\n\n"
            "from fastapi import Depends\n"
            "from fastapi.security import HTTPBearer\n\n"
            "security = HTTPBearer()\n\n"
            "async def verify_token(token: str = Depends(security)):\n"
            "    if not check_token(token):\n"
            "        raise HTTPException(401, 'Invalid token')\n"
            "    return token\n\n"
            "@app.get('/protected')\n"
            "async def protected_route(token: str = Depends(verify_token)):\n"
            "    return {'message': 'authorized'}\n\n"
            "# Depends 支持叠加\n"
            "async def get_current_user(token: str = Depends(verify_token)):\n"
            "    return decode_jwt(token)\n\n"
            "async def require_admin(user = Depends(get_current_user)):\n"
            "    if not user.is_admin: raise HTTPException(403)\n"
            "    return user"
        ),
    },
    # ── 计算机基础 ───────────────────────────────────────────────────────────
    {
        "title": "操作系统进程与线程区别",
        "category": "os",
        "content": (
            "进程（Process）：\n"
            "- 资源分配基本单位：每个进程有独立的内存空间（堆、栈、代码段）\n"
            "- 进程间通信需要 IPC（管道、消息队列、共享内存、Socket）\n"
            "- 创建/切换开销大（需要分配资源、复制上下文）\n"
            "- 一个进程崩溃不影响其他进程（隔离性）\n\n"
            "线程（Thread）：\n"
            "- CPU 调度基本单位：同一进程的线程共享堆内存\n"
            "- 线程间通信直接读写共享变量（需加锁保护）\n"
            "- 创建/切换开销小（共享资源，只切换寄存器和栈）\n"
            "- 一个线程崩溃可能导致整个进程崩溃\n\n"
            "Python 的 GIL：\n"
            "- CPython 中，同一时刻只能有一个线程执行 Python 字节码\n"
            "- 多线程适合 I/O 密集型，不适合 CPU 密集型\n"
            "- CPU 密集型用多进程（multiprocessing）绕过 GIL\n\n"
            "协程（Coroutine）：\n"
            "- 用户态轻量级线程，由程序自身调度\n"
            "- asyncio 基于协程实现并发"
        ),
    },
    {
        "title": "TCP 三次握手与四次挥手",
        "category": "network",
        "content": (
            "三次握手（建立可靠连接）：\n\n"
            "客户端 → 服务端：SYN=1, seq=x\n"
            "（客户端发送连接请求，进入 SYN_SENT）\n\n"
            "服务端 → 客户端：SYN=1, ACK=1, seq=y, ack=x+1\n"
            "（服务端接受请求，进入 SYN_RCVD）\n\n"
            "客户端 → 服务端：ACK=1, seq=x+1, ack=y+1\n"
            "（客户端进入 ESTABLISHED，双方建立连接）\n\n"
            "为什么三次：确保双方收发能力都正常\n\n"
            "四次挥手（关闭连接）：\n\n"
            "客户端 → 服务端：FIN=1, seq=u\n"
            "（客户端发送结束请求）\n\n"
            "服务端 → 客户端：ACK=1, ack=u+1\n"
            "（服务端确认，先关闭写的半关闭状态）\n\n"
            "服务端 → 客户端：FIN=1, seq=v\n"
            "（服务端发完数据，发送自己的结束请求）\n\n"
            "客户端 → 服务端：ACK=1, ack=v+1\n"
            "（客户端等待 2MSL 后关闭，服务端收到后立即关闭）\n\n"
            "等待 2MSL 原因：确保对方收到最后的 ACK，清理迷途报文"
        ),
    },
    {
        "title": "数据库索引原理（B+ 树 vs Hash）",
        "category": "database",
        "content": (
            "B+ 树（大多数数据库默认索引）：\n\n"
            "- 多路平衡查找树，节点大小通常为 16KB\n"
            "- 非叶子节点只存索引键和指针，不存数据\n"
            "- 叶子节点包含所有数据，用双向链表连接\n"
            "- 范围查询优势明显：定位起点后顺序遍历链表\n"
            "- 查找：O(log N)，深度一般 2~4 层（适合磁盘）\n\n"
            "Hash 索引（Memory/Redis 使用）：\n\n"
            "- 对索引键计算 Hash 值，直接定位\n"
            "- 等值查询 O(1)，极快\n"
            "- 不支持范围查询、排序\n"
            "- 碰撞严重时性能下降\n\n"
            "聚簇索引（InnoDB）：数据按主键顺序存储，叶子节点直接是数据行\n"
            "非聚簇索引（MyISAM）：叶子节点存主键值，需回表查数据"
        ),
    },
    # ── 场景化问答 ───────────────────────────────────────────────────────────
    {
        "title": "代码审查（Code Review）要点清单",
        "category": "best_practice",
        "content": (
            "功能正确性：\n"
            "□ 逻辑是否符合需求？\n"
            "□ 边界条件是否处理？（空值、超长输入、负数）\n"
            "□ 错误处理是否完善？（try/catch、异常返回）\n\n"
            "代码质量：\n"
            "□ 变量/函数命名是否清晰？\n"
            "□ 函数是否过长？（建议不超过 50 行）\n"
            "□ 重复代码是否抽取为公共函数？\n"
            "□ 注释是否必要且准确？\n\n"
            "安全与性能：\n"
            "□ 是否有 SQL 注入/XSS/CSRF 风险？\n"
            "□ 查询是否有 N+1 问题？\n"
            "□ 是否有不必要的循环或重复计算？\n"
            "□ 大数据量接口是否做了分页？\n\n"
            "可维护性：\n"
            "□ 是否符合团队代码规范？\n"
            "□ 接口是否向后兼容？\n"
            "□ 相关文档/接口说明是否同步更新？\n"
            "□ 单元测试覆盖率是否足够？"
        ),
    },
    {
        "title": "如何排查线上故障",
        "category": "best_practice",
        "content": (
            "故障排查四步法：定位 → 分析 → 修复 → 复盘\n\n"
            "第一步：定位\n"
            "1. 查看监控大盘（Prometheus/Grafana）定位异常时间点\n"
            "2. 查看日志：grep error /path/to/log\n"
            "3. 查看链路追踪（Jaeger/Zipkin）定位具体服务\n"
            "4. 用 curl/postman 重放请求，确认问题\n\n"
            "第二步：分析\n"
            "5. 如果是 5xx：查看服务进程状态、内存、CPU\n"
            "6. 如果是超时：检查下游服务响应时间、数据库慢查询\n"
            "7. 如果是数据异常：检查数据变更记录（binlog/audit log）\n"
            "8. 如果是流量异常：检查是否有爬虫、促销活动、CC 攻击\n\n"
            "第三步：修复\n"
            "9. 止血优先：回滚代码 / 开关降级 / 限流\n"
            "10. 然后再从根本解决\n\n"
            "第四步：复盘\n"
            "11. 写故障报告：时间线、根因、影响、改进措施\n"
            "12. 落实改进项到 JIRA/飞书\n"
            "13. 建立类似故障的自动化检测规则"
        ),
    },
    {
        "title": "CI/CD 流水线设计",
        "category": "devops",
        "content": (
            "典型 CI/CD 流水线阶段：\n\n"
            "1. 代码检出（Checkout）\n"
            "2. 依赖安装（npm install / pip install）\n"
            "3. 代码检查（Lint + Format Check）\n"
            "4. 单元测试（pytest / jest）\n"
            "5. 编译构建（npm run build / python -m compile）\n"
            "6. 安全扫描（SonarQube / Trivy）\n"
            "7. 构建镜像（docker build）\n"
            "8. 推送镜像（docker push）\n"
            "9. 部署到测试环境（docker compose up -d）\n"
            "10. 集成测试 / E2E 测试\n"
            "11. 手动审批（如有）\n"
            "12. 部署到生产（蓝绿 / 金丝雀 / Rolling）\n\n"
            "GitHub Actions 示例：\n"
            "on: push: branches: [main]\n"
            "jobs:\n"
            "  test:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - run: npm ci && npm test\n"
            "      - run: npm run build\n\n"
            "  deploy:\n"
            "    needs: test\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - run: ./deploy.sh"
        ),
    },
    {
        "title": "技术方案文档写作指南",
        "category": "best_practice",
        "content": (
            "一份好的技术方案（Design Doc）应包含：\n\n"
            "1. 背景与目标\n"
            "为什么要做？解决什么问题？成功标准是什么？\n\n"
            "2. 方案概述\n"
            "用一两段话描述整体方案，不涉及实现细节\n\n"
            "3. 详细设计\n"
            "- 核心数据结构设计\n"
            "- API 接口设计（附请求/响应示例）\n"
            "- 关键流程（附流程图或时序图）\n"
            "- 存储方案（选什么数据库、是否需要缓存）\n"
            "- 风险评估（单点、容量、兼容性）\n\n"
            "4. 替代方案对比\n"
            "为什么选当前方案而非其他？各方案优缺点？\n\n"
            "5. 实施计划\n"
            "分几个阶段？各阶段的里程碑是什么？\n\n"
            "6. 测试计划\n"
            "如何验证功能正确性？性能测试方案？\n\n"
            "7. 上线与回滚方案\n"
            "灰度策略？回滚触发条件？如何回滚？\n\n"
            "写作原则：\n"
            "- 先讲 what 和 why，最后讲 how\n"
            "- 用图说话（流程图、架构图、时序图）\n"
            "- 假设读者是比你高一级别的工程师"
        ),
    },
]


def search_knowledge(query: str, top_k: int = 3) -> list[KnowledgeEntry]:
    """基于关键词匹配的简单知识检索（离线模式使用）"""
    query_lower = query.lower()
    keywords = query_lower.replace('?', '').replace('！', '').split()
    scored: list[tuple[int, KnowledgeEntry]] = []

    for entry in KNOWLEDGE_BASE:
        score = 0
        content_lower = (entry['title'] + entry['category'] + entry['content']).lower()
        title_lower = entry['title'].lower()
        category_lower = entry['category'].lower()

        for kw in keywords:
            if kw in title_lower:
                score += 10
            if kw in category_lower:
                score += 5
            if kw in content_lower:
                score += 1

        if score > 0:
            scored.append((score, entry))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [entry for _, entry in scored[:top_k]]


def build_offline_answer(query: str) -> str:
    """离线模式下，基于预置知识库生成回答"""
    results = search_knowledge(query, top_k=2)

    if not results:
        return (
            "【智能代码工作台 · 离线助手】\n\n"
            f"问题：{query}\n\n"
            "抱歉，知识库中暂未收录与您问题相关的内容。\n"
            "建议您：\n"
            "1. 联网后从云端知识库获取更完整的答案\n"
            "2. 在知识库页面上传相关 PDF/TXT 文档进行补充\n"
            "3. 描述更具体的问题或使用相关技术关键词\n\n"
            "提示：本系统预置了 Git/Docker/SQL/Python/系统设计/前端等方向的常见问答。"
        )

    top = results[0]
    lines = [
        "【智能代码工作台 · 知识库检索回答】\n",
        f"📖 参考文档：{top['title']}\n",
        f"📁 分类：{top['category']}\n",
        "─" * 40,
        top['content'][:800],
    ]

    if len(results) > 1:
        lines.append("")
        lines.append("─" * 40)
        lines.append(f"📖 补充参考：{results[1]['title']}")
        lines.append(results[1]['content'][:400])

    lines.append("")
    lines.append("─" * 40)
    lines.append("💡 以上内容由本地知识库检索生成，如有疑问可联网后重新提问。")

    return "\n".join(lines)
