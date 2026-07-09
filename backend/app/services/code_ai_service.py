import json
import re
from typing import Dict, List, Optional, Any
from enum import Enum

class CodeAnalysisType(str, Enum):
    DEFECT = "defect"
    CONVERT = "convert"
    TEST = "test"
    DOC = "doc"
    REFACTOR = "refactor"
    LOG_ANALYZE = "log_analyze"
    CROSS_LANG = "cross_lang"

class CodeAIService:
    """代码专项 AI 服务 - 缺陷扫描、转换、测试生成等"""

    PROMPTS = {
        "defect": """你是一个专业的代码审查员。请分析以下代码，识别：
1. 安全漏洞（SQL注入、XSS、命令注入、密码硬编码等）
2. 性能问题（内存泄漏、循环效率、低效查询等）
3. 代码规范（命名、注释、复杂度等）
4. 潜在Bug（空指针、边界条件、异常处理等）
5. 依赖安全问题（已知漏洞依赖）

代码语言：{language}
代码内容：
```{language}
{code}
```

请以JSON格式输出：
{{
  "issues": [
    {{
      "severity": "high|medium|low",
      "type": "security|performance|bug|style|dependency",
      "location": "行号或描述",
      "description": "问题描述",
      "suggestion": "修复建议",
      "code_snippet": "问题代码片段"
    }}
  ],
  "summary": "总体评价一段话",
  "score": 0-100的整数分数,
  "security_score": 0-100安全评分,
  "maintainability": "可维护性评价"
}}""",

        "cross_convert": """你是一个多语言代码转换专家。请将以下代码从 {source_lang} 转换为 {target_lang}。

{source_lang} 代码：
```{source_lang}
{code}
```

要求：
1. 保持功能完全一致
2. 遵循 {target_lang} 最佳实践和代码风格
3. 添加必要的类型注解
4. 处理语言特有的API差异
5. 添加适当的错误处理

请以JSON格式输出：
{{
  "converted_code": "转换后的完整代码",
  "compatibility_notes": ["兼容性说明1", "说明2"],
  "alternative_approaches": ["其他可行方案"],
  "potential_issues": ["需要注意的问题"]
}}""",

        "unit_test": """你是一个测试工程师。请为以下{language}代码生成全面的单元测试。

代码：
```{language}
{code}
```

测试框架偏好：{framework}
要求：
1. 使用 {framework} 框架
2. 覆盖主要功能和边界条件
3. 添加有意义的测试用例名称（使用中文描述测试目的）
4. 包含Setup和Teardown（如需要）
5. 测试用例应包含：正常输入、边界值、异常输入

请以JSON格式输出：
{{
  "test_code": "完整的测试代码",
  "test_framework": "实际使用的框架",
  "test_cases": [
    {{
      "name": "测试用例名称",
      "description": "测试目的",
      "input": "输入值",
      "expected": "期望结果"
    }}
  ],
  "coverage_notes": "覆盖率说明"
}}""",

        "api_doc": """你是一个技术文档工程师。请为以下API代码生成专业的接口文档。

代码语言：{language}
代码：
```{language}
{code}
```

请以JSON格式输出：
{{
  "api_name": "接口名称",
  "endpoint": "请求路径",
  "method": "GET|POST|PUT|DELETE|PATCH",
  "description": "接口功能描述",
  "parameters": [
    {{
      "name": "参数名",
      "type": "参数类型",
      "required": true|false,
      "description": "参数说明",
      "default": "默认值（如果有）"
    }}
  ],
  "request_example": "请求示例代码",
  "response_example": "响应示例JSON",
  "error_codes": [
    {{
      "code": "错误码",
      "message": "错误信息",
      "solution": "解决方案"
    }}
  ]
}}""",

        "log_analyze": """你是一个资深的DevOps工程师。请分析以下错误日志，定位问题原因并给出完整解决方案。

错误类型：{error_type}
相关代码（可选）：
```{language}
{code}
```

日志内容：
```
{log_content}
```

请以JSON格式输出：
{{
  "root_cause": "根本原因一句话描述",
  "error_location": "错误位置（文件:行号或函数名）",
  "stack_trace_analysis": [
    {{
      "file": "文件名",
      "line": "行号",
      "function": "函数名",
      "meaning": "这行代码的作用"
    }}
  ],
  "solution": {{
    "steps": ["解决步骤1", "步骤2"],
    "code_fix": "修复代码（如适用）",
    "workaround": "临时解决方案（如有）"
  }},
  "prevention": "预防措施建议",
  "related_documentation": "相关文档链接（如有）"
}}""",

        "refactor": """你是一个代码重构专家。请对以下{language}代码进行重构优化。

重构目标：{refactor_type}
代码：
```{language}
{code}
```

{refactor_type}对应的具体要求：
- readability: 优化代码可读性，重命名变量，增强注释，拆分过长函数
- performance: 优化性能和内存使用，减少不必要的计算，优化算法复杂度
- security: 增强安全性，添加输入验证，防止注入攻击，使用安全API
- modularity: 拆分大函数为小函数，提高模块化程度，降低耦合度

请以JSON格式输出：
{{
  "refactored_code": "重构后的完整代码",
  "changes": [
    {{
      "type": "改动类型",
      "location": "改动位置",
      "before": "改动前",
      "after": "改动后",
      "reason": "改动原因"
    }}
  ],
  "benefits": ["收益1", "收益2"],
  "metrics": {{
    "complexity_reduction": "复杂度降低百分比",
    "lines_added": "新增行数",
    "lines_removed": "删除行数"
  }}
}}""",

        "comment_generate": """你是一个代码文档专家。请为以下{language}代码批量生成专业的中文注释。

代码：
```{language}
{code}
```

要求：
1. 为每个函数/方法添加文档字符串
2. 为复杂的逻辑块添加行内注释
3. 注释使用中文，简洁明了
4. 遵循对应语言的文档规范

请以JSON格式输出：
{{
  "commented_code": "添加注释后的完整代码",
  "functions_documented": ["函数1", "函数2"],
  "complex_blocks_documented": ["复杂逻辑块1的位置和说明"]
}}""",

        "code_review": """你是一个资深代码审查专家。请对以下{language}代码进行全面的代码审查。

代码：
```{language}
{code}
```

审查维度：
1. 代码正确性
2. 安全性
3. 性能
4. 可读性
5. 可维护性
6. 测试覆盖

请以JSON格式输出：
{{
  "overall_rating": "A/B/C/D评分",
  "summary": "总体评价",
  "strengths": ["优点1", "优点2"],
  "issues": [
    {{
      "severity": "critical/major/minor",
      "category": "分类",
      "title": "问题标题",
      "description": "详细描述",
      "line": "行号",
      "suggestion": "修改建议"
    }}
  ],
  "detailed_feedback": {{
    "correctness": "正确性评价",
    "security": "安全性评价",
    "performance": "性能评价",
    "readability": "可读性评价",
    "maintainability": "可维护性评价"
  }}
}}"""
    }

    def __init__(self, model_manager=None):
        self.model_manager = model_manager

    async def chat(self, prompt: str) -> str:
        """调用LLM生成响应"""
        if self.model_manager is None:
            return await self._call_default_model(prompt)
        return await self.model_manager.chat(prompt)

    async def _call_default_model(self, prompt: str) -> str:
        """调用默认模型（当没有配置模型管理器时）"""
        return json.dumps({
            "error": "模型未配置，请先在设置中配置AI模型",
            "raw_prompt": prompt[:500]
        })

    async def analyze_defect(self, code: str, language: str) -> Dict:
        """代码缺陷扫描"""
        prompt = self.PROMPTS["defect"].format(language=language, code=code[:8000])
        response = await self.chat(prompt)
        return self._parse_json_response(response)

    async def convert_code(self, code: str, source_lang: str,
                          target_lang: str, framework: str = "") -> Dict:
        """跨语言代码转换"""
        prompt = self.PROMPTS["cross_convert"].format(
            source_lang=source_lang,
            target_lang=target_lang,
            code=code[:8000]
        )
        response = await self.chat(prompt)
        return self._parse_json_response(response)

    async def generate_unit_test(self, code: str, language: str,
                                framework: str = "pytest/unittest") -> Dict:
        """生成单元测试"""
        prompt = self.PROMPTS["unit_test"].format(
            language=language,
            code=code[:6000],
            framework=framework
        )
        response = await self.chat(prompt)
        return self._parse_json_response(response)

    async def generate_api_doc(self, code: str, language: str) -> Dict:
        """生成接口文档"""
        prompt = self.PROMPTS["api_doc"].format(
            language=language,
            code=code[:6000]
        )
        response = await self.chat(prompt)
        return self._parse_json_response(response)

    async def analyze_error_log(self, log_content: str,
                               error_type: str = "runtime",
                               code: str = "") -> Dict:
        """分析错误日志"""
        prompt = self.PROMPTS["log_analyze"].format(
            error_type=error_type,
            code=code[:4000] if code else "",
            log_content=log_content[:3000]
        )
        response = await self.chat(prompt)
        return self._parse_json_response(response)

    async def refactor_code(self, code: str, language: str,
                           refactor_type: str = "readability") -> Dict:
        """代码重构"""
        valid_types = ["readability", "performance", "security", "modularity"]
        if refactor_type not in valid_types:
            refactor_type = "readability"

        prompt = self.PROMPTS["refactor"].format(
            language=language,
            code=code[:8000],
            refactor_type=refactor_type
        )
        response = await self.chat(prompt)
        return self._parse_json_response(response)

    async def generate_comments(self, code: str, language: str) -> Dict:
        """批量生成代码注释"""
        prompt = self.PROMPTS["comment_generate"].format(
            language=language,
            code=code[:6000]
        )
        response = await self.chat(prompt)
        return self._parse_json_response(response)

    async def code_review(self, code: str, language: str) -> Dict:
        """代码审查"""
        prompt = self.PROMPTS["code_review"].format(
            language=language,
            code=code[:8000]
        )
        response = await self.chat(prompt)
        return self._parse_json_response(response)

    def _parse_json_response(self, response: str) -> Dict:
        """解析 JSON 响应"""
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

        return {
            "raw_response": response,
            "error": "响应解析失败"
        }

    def detect_language(self, code: str, filename: str = "") -> str:
        """自动检测代码语言"""
        if filename:
            ext = filename.split('.')[-1].lower()
            lang_map = {
                'py': 'python', 'js': 'javascript', 'ts': 'typescript',
                'java': 'java', 'go': 'go', 'rs': 'rust', 'rb': 'ruby',
                'php': 'php', 'c': 'c', 'cpp': 'cpp', 'cs': 'csharp',
                'swift': 'swift', 'kt': 'kotlin', 'scala': 'scala',
                'sql': 'sql', 'sh': 'bash', 'vue': 'vue', 'jsx': 'javascript',
                'tsx': 'typescript', 'html': 'html', 'css': 'css', 'scss': 'scss'
            }
            if ext in lang_map:
                return lang_map[ext]

        patterns = {
            'python': [r'def \w+\(', r'import \w+', r'from \w+ import', r'if __name__'],
            'javascript': [r'const \w+\s*=', r'let \w+\s*=', r'function \w+\(', r'=>'],
            'java': [r'public class', r'private \w+', r'System\.out\.println'],
            'go': [r'func \w+\(', r'package \w+', r'import\s+"\w+"'],
            'rust': [r'fn \w+\(', r'let mut', r'impl \w+', r'use \w+::'],
            'sql': [r'SELECT\s+.*\s+FROM', r'CREATE\s+TABLE', r'INSERT\s+INTO'],
        }

        for lang, lang_patterns in patterns.items():
            matches = sum(1 for p in lang_patterns if re.search(p, code, re.IGNORECASE))
            if matches >= 2:
                return lang

        return 'unknown'

    def get_supported_analysis_types(self) -> List[Dict]:
        """获取支持的分析类型列表"""
        return [
            {"id": "defect", "name": "🔍 缺陷扫描", "description": "识别代码安全漏洞、性能问题、潜在Bug"},
            {"id": "cross_convert", "name": "🔄 跨语言转换", "description": "Python/Java/JS/Go等语言互转"},
            {"id": "test", "name": "✅ 单元测试", "description": "自动生成单元测试用例"},
            {"id": "doc", "name": "📄 接口文档", "description": "生成API接口文档"},
            {"id": "refactor", "name": "🔧 代码重构", "description": "优化代码结构、可读性、性能"},
            {"id": "log_analyze", "name": "📋 日志解析", "description": "分析错误日志定位问题"},
            {"id": "comment", "name": "💬 注释生成", "description": "批量生成代码注释"},
            {"id": "review", "name": "⭐ 代码审查", "description": "全面代码质量审查"},
        ]

code_ai_service_global: Optional[CodeAIService] = None

def get_code_ai_service() -> CodeAIService:
    global code_ai_service_global
    if code_ai_service_global is None:
        code_ai_service_global = CodeAIService()
    return code_ai_service_global
