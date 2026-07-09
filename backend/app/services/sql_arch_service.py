import re
import json
from typing import Dict, List, Optional, Any
from pathlib import Path

class SQLEnhanceService:
    """SQL专项增强服务 - 生成、优化、分析SQL"""

    def __init__(self, model_manager=None):
        self.model_manager = model_manager

    async def chat(self, prompt: str) -> str:
        if self.model_manager is None:
            return json.dumps({"error": "模型未配置"})
        return await self.model_manager.chat(prompt)

    async def _parse_json_response(self, response: str) -> Dict:
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        return {"raw_response": response}

    async def generate_sql_from_description(self, description: str,
                                          db_type: str = "mysql",
                                          db_schema: str = "") -> Dict:
        """从业务描述生成SQL"""
        prompt = f"""根据以下业务描述生成SQL语句。

数据库类型：{db_type}
业务描述：
{description}

数据库结构（可选）：
{db_schema or '未提供，请根据业务描述合理推断'}

要求：
1. 生成可执行的 CREATE TABLE、SELECT、INSERT、UPDATE 或 DELETE 语句
2. 考虑性能和可维护性
3. 添加必要的索引建议
4. 遵循{dp_type}最佳实践

返回JSON格式：
{{
  "sql": "生成的SQL语句",
  "explanation": "SQL说明",
  "indexes": ["索引建议1", "索引建议2"],
  "related_tables": ["涉及的表"]
}}"""

        response = await self.chat(prompt)
        return await self._parse_json_response(response)

    async def analyze_sql_performance(self, sql: str,
                                     db_type: str = "mysql") -> Dict:
        """SQL性能分析"""
        prompt = f"""分析以下{dp_type} SQL的性能问题。

SQL语句：
```sql
{sql}
```

请从以下维度分析：
1. 全表扫描
2. 缺失索引
3. 低效子查询
4. 不当使用函数
5. 连接顺序
6. 数据类型转换

返回JSON格式：
{{
  "issues": [
    {{
      "type": "性能问题类型",
      "severity": "high|medium|low",
      "location": "问题位置",
      "description": "问题描述",
      "suggestion": "优化建议"
    }}
  ],
  "optimized_sql": "优化后的SQL",
  "performance_score": 0-100,
  "estimated_improvement": "预估性能提升"
}}"""

        response = await self.chat(prompt)
        return await self._parse_json_response(response)

    async def generate_crud(self, table_schema: str,
                           language: str = "python",
                           orm: str = "sqlalchemy") -> Dict:
        """根据表结构生成CRUD代码"""
        prompt = f"""根据以下表结构生成{language}的CRUD代码，使用{orm} ORM框架。

表结构：
{table_schema}

要求：
1. 生成完整的Model定义
2. 生成基础的CRUD函数（create, read, update, delete, list）
3. 添加必要的参数验证
4. 遵循{language}和{orm}的最佳实践

返回JSON格式：
{{
  "model_code": "Model定义代码",
  "crud_functions": "CRUD函数代码",
  "api_endpoints": ["API端点列表"],
  "usage_example": "使用示例"
}}"""

        response = await self.chat(prompt)
        return await self._parse_json_response(response)

    async def optimize_schema(self, schema: str,
                            db_type: str = "mysql") -> Dict:
        """数据库schema优化"""
        prompt = f"""分析并优化以下{dp_type}数据库schema。

现有表结构：
{schema}

请从以下维度优化：
1. 规范化/反规范化建议
2. 索引优化
3. 分表建议
4. 字段类型优化
5. 约束优化

返回JSON格式：
{{
  "optimized_schema": "优化后的DDL",
  "changes": [
    {{
      "type": "优化类型",
      "before": "优化前",
      "after": "优化后",
      "reason": "原因"
    }}
  ],
  "warnings": ["注意事项"]
}}"""

        response = await self.chat(prompt)
        return await self._parse_json_response(response)

    async def generate_migration(self, from_schema: str,
                                to_schema: str,
                                db_type: str = "mysql") -> Dict:
        """生成数据库迁移脚本"""
        prompt = f"""生成从旧版本到新版本的数据库迁移脚本。

{dp_type}数据库

旧版本schema：
{from_schema}

新版本schema：
{to_schema}

返回JSON格式：
{{
  "migration_up": "升级脚本",
  "migration_down": "回滚脚本",
  "changes_summary": ["变更1", "变更2"],
  "data_migration_needed": true或false
}}"""

        response = await self.chat(prompt)
        return await self._parse_json_response(response)

    def get_supported_db_types(self) -> List[str]:
        """获取支持的数据库类型"""
        return ["mysql", "postgresql", "sqlite", "oracle", "sqlserver", "mariadb"]

    def get_supported_orms(self) -> List[str]:
        """获取支持的ORM框架"""
        return ["sqlalchemy", "django", "sequelize", "typeorm", "prisma", "gorm"]

class ArchitectureGeneratorService:
    """项目架构图生成服务"""

    def __init__(self, model_manager=None):
        self.model_manager = model_manager

    async def chat(self, prompt: str) -> str:
        if self.model_manager is None:
            return json.dumps({"error": "模型未配置"})
        return await self.model_manager.chat(prompt)

    async def _parse_json_response(self, response: str) -> Dict:
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        return {"raw_response": response}

    async def generate_architecture_diagrams(self, project_info: Dict) -> Dict:
        """生成项目架构图（Mermaid格式）"""
        project_name = project_info.get('name', 'Project')
        tech_stack = project_info.get('tech_stack', [])
        code_units = project_info.get('code_units', [])
        summary = project_info.get('summary', '')

        prompt = f"""根据以下项目信息生成Mermaid格式的架构图。

项目名称：{project_name}
技术栈：{', '.join(tech_stack)}
项目摘要：{summary}

代码单元统计：
- 函数：{len([u for u in code_units if u.get('type') == 'function'])}
- 类：{len([u for u in code_units if u.get('type') == 'class'])}
- 接口：{len([u for u in code_units if u.get('type') in ['interface', 'type']])}
- 其他：{len([u for u in code_units if u.get('type') not in ['function', 'class', 'interface', 'type']])}

请生成以下Mermaid图表：
1. 系统架构图（systemArchitecture）
2. 类图（classDiagram）- 选取主要类
3. 数据流图（ flowchart 或 sequenceDiagram）
4. 目录结构图（erDiagram 或 mindmap）

返回JSON格式：
{{
  "system_architecture": "系统架构图mermaid代码",
  "class_diagram": "类图mermaid代码",
  "data_flow": "数据流图mermaid代码",
  "directory_structure": "目录结构mermaid代码",
  "explanation": "架构说明"
}}"""

        response = await self.chat(prompt)
        return await self._parse_json_response(response)

    async def generate_er_diagram(self, tables: List[Dict]) -> str:
        """根据表结构生成ER图"""
        mermaid_lines = ["erDiagram"]

        for table in tables:
            table_name = table.get('name', 'Unknown')
            columns = table.get('columns', [])

            mermaid_lines.append(f"    {table_name} {{")
            for col in columns:
                col_type = col.get('type', 'VARCHAR')
                col_name = col.get('name', '')
                col_pk = 'PK' if col.get('primary_key') else ''
                col_fk = 'FK' if col.get('foreign_key') else ''
                mermaid_lines.append(f"        {col_type} {col_name} {col_pk} {col_fk}")
            mermaid_lines.append("    }")

        return "\n".join(mermaid_lines)

    async def generate_api_flow_diagram(self, endpoints: List[Dict]) -> str:
        """生成API流程图"""
        mermaid_lines = ["flowchart TD", "    Start[开始] --> CheckAuth{认证?}", "    CheckAuth -->|Yes| QueryKB[查询知识库]", "    CheckAuth -->|No| Return401[返回401]"]

        for i, ep in enumerate(endpoints[:10]):
            ep_id = f"EP{i+1}"
            ep_name = f"{ep.get('method', 'GET')} {ep.get('path', '/')}"
            mermaid_lines.append(f"    QueryKB --> {ep_id}[{ep_name}]")

        mermaid_lines.append(f"    EP1 --> End[结束]")

        return "\n".join(mermaid_lines)

    async def generate_mindmap(self, project_info: Dict) -> str:
        """生成项目技术栈思维导图"""
        tech_stack = project_info.get('tech_stack', [])
        project_name = project_info.get('name', 'Project')

        lines = ["mindmap", f"    root(({project_name}))"]

        categories = {
            "语言": [],
            "框架": [],
            "工具": [],
            "数据库": []
        }

        framework_keywords = ['django', 'flask', 'fastapi', 'express', 'spring', 'vue', 'react', 'angular', 'gin', 'echo']
        db_keywords = ['mysql', 'postgresql', 'redis', 'mongodb', 'sqlite', 'chroma']

        for tech in tech_stack:
            tech_lower = tech.lower()
            if any(k in tech_lower for k in framework_keywords):
                categories["框架"].append(tech)
            elif any(k in tech_lower for k in db_keywords):
                categories["数据库"].append(tech)
            else:
                categories["语言"].append(tech)

        for category, items in categories.items():
            if items:
                lines.append(f"        {category}")
                for item in items:
                    lines.append(f"            {item}")

        return "\n".join(lines)

    async def explain_architecture(self, project_info: Dict) -> str:
        """解释项目架构"""
        prompt = f"""分析并解释以下项目的架构设计。

项目名称：{project_info.get('name', 'Project')}
技术栈：{', '.join(project_info.get('tech_stack', []))}
项目摘要：{project_info.get('summary', '')}

请用简洁的中文解释：
1. 项目整体架构
2. 核心模块和职责
3. 数据流向
4. 技术选型理由

返回JSON格式：
{{
  "overview": "整体概述",
  "core_modules": ["核心模块1", "核心模块2"],
  "data_flow": "数据流向说明",
  "tech_choices": "技术选型说明"
}}"""

        response = await self.chat(prompt)
        return await self._parse_json_response(response)

sql_enhance_service_global: Optional[SQLEnhanceService] = None
arch_generator_service_global: Optional[ArchitectureGeneratorService] = None

def get_sql_enhance_service() -> SQLEnhanceService:
    global sql_enhance_service_global
    if sql_enhance_service_global is None:
        sql_enhance_service_global = SQLEnhanceService()
    return sql_enhance_service_global

def get_architecture_generator() -> ArchitectureGeneratorService:
    global arch_generator_service_global
    if arch_generator_service_global is None:
        arch_generator_service_global = ArchitectureGeneratorService()
    return arch_generator_service_global
