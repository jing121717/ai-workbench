import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
import json
import tempfile
import shutil

SUPPORTED_EXTENSIONS = {
    '.py': 'python',
    '.java': 'java',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.tsx': 'typescript',
    '.vue': 'vue',
    '.sql': 'sql',
    '.go': 'go',
    '.rs': 'rust',
    '.cpp': 'cpp',
    '.c': 'c',
    '.h': 'c',
    '.hpp': 'cpp',
    '.rb': 'ruby',
    '.php': 'php',
    '.sh': 'bash',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.json': 'json',
    '.xml': 'xml',
    '.md': 'markdown',
    '.css': 'css',
    '.scss': 'scss',
    '.less': 'less',
    '.html': 'html',
    '.jsx': 'javascript',
    '.kt': 'kotlin',
    '.swift': 'swift',
    '.cs': 'csharp',
    '.r': 'r',
    '.scala': 'scala',
}

IGNORE_DIRS = {
    '.git', '__pycache__', 'node_modules', 'venv', '.venv',
    'env', '.env', 'dist', 'build', 'target', 'bin', 'obj',
    '.idea', '.vscode', 'vendor', 'packages', '.egg-info',
    'coverage', '.tox', '.pytest_cache', '.mypy_cache',
    ' typings', 'staticfiles', 'public', 'assets'
}

IGNORE_EXTENSIONS = {
    '.pyc', '.pyo', '.so', '.dll', '.exe', '.bin', '.jpg',
    '.jpeg', '.png', '.gif', '.ico', '.svg', '.woff', '.woff2',
    '.ttf', '.eot', '.otf', '.lock', '.map', '.min.js', '.min.css'
}

@dataclass
class CodeUnit:
    type: str
    name: str
    file_path: str
    start_line: int
    end_line: int
    content: str
    signature: str = ""
    doc_comment: str = ""
    dependencies: List[str] = field(default_factory=list)
    return_type: str = ""
    parameters: List[Dict] = field(default_factory=list)

@dataclass
class ProjectInfo:
    name: str
    local_path: str
    is_git_repo: bool
    git_info: Dict
    tech_stack: List[str]
    summary: str
    total_files: int
    total_units: int
    project_tree: Dict
    code_units: List[Dict]
    dependencies: Dict
    languages_stats: Dict

class CodeRepositoryParser:
    """代码仓库解析器 - 支持本地文件夹和Git仓库"""

    def __init__(self):
        self.temp_dirs: List[str] = []

    def __del__(self):
        for temp_dir in self.temp_dirs:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    def parse_repository(self, path: str, is_git: bool = False) -> ProjectInfo:
        repo_path = Path(path)

        if is_git_repo(repo_path) or is_git:
            code_path, git_info = self._handle_git_repo(repo_path)
        else:
            code_path = repo_path
            git_info = {}

        code_files = self._scan_code_files(code_path)
        tech_stack = self._detect_tech_stack(code_files)
        project_tree = self._build_project_tree(code_files)

        all_units = []
        language_stats = {}

        for file_path in code_files:
            ext = Path(file_path).suffix.lower()
            lang = SUPPORTED_EXTENSIONS.get(ext, 'unknown')

            language_stats[lang] = language_stats.get(lang, 0) + 1

            units = self._parse_file(file_path, lang)
            all_units.extend(units)

        dependency_graph = self._analyze_dependencies(all_units)

        summary = self._generate_summary(
            repo_path.name,
            tech_stack,
            len(code_files),
            len(all_units),
            language_stats
        )

        return ProjectInfo(
            name=repo_path.name,
            local_path=str(code_path),
            is_git_repo=is_git_repo(repo_path) or is_git,
            git_info=git_info,
            tech_stack=tech_stack,
            summary=summary,
            total_files=len(code_files),
            total_units=len(all_units),
            project_tree=project_tree,
            code_units=[self._unit_to_dict(u) for u in all_units],
            dependencies=dependency_graph,
            languages_stats=language_stats
        )

    def parse_code_string(self, code: str, language: str, filename: str = "snippet") -> List[CodeUnit]:
        with tempfile.NamedTemporaryFile(mode='w', suffix=filename, delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            units = self._parse_file(temp_path, language)
            for u in units:
                u.file_path = filename
            return units
        finally:
            os.unlink(temp_path)

    def _handle_git_repo(self, repo_path: Path) -> tuple:
        temp_dir = tempfile.mkdtemp(prefix='ai_workbench_git_')
        self.temp_dirs.append(temp_dir)

        target_path = Path(temp_dir) / repo_path.name

        git_info = self._parse_git_info(repo_path)

        try:
            subprocess.run(
                ['git', 'clone', '--depth', '1', str(repo_path), str(target_path)],
                capture_output=True,
                check=True,
                timeout=300
            )
            return target_path, git_info
        except subprocess.CalledProcessError:
            try:
                if git_info.get('git_url'):
                    subprocess.run(
                        ['git', 'clone', '--depth', '1', git_info['git_url'], str(target_path)],
                        capture_output=True,
                        check=True,
                        timeout=300
                    )
                    return target_path, git_info
            except Exception:
                pass

            shutil.copytree(repo_path, target_path, ignore=shutil.ignore_patterns('.git'))
            return target_path, git_info

    def _parse_git_info(self, repo_path: Path) -> Dict:
        info = {}

        if not (repo_path / '.git').exists():
            return info

        try:
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                cwd=repo_path, capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                info['git_url'] = result.stdout.strip()

            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=repo_path, capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                info['current_branch'] = result.stdout.strip()

            result = subprocess.run(
                ['git', 'log', '-1', '--pretty=format:%H|%an|%ae|%s|%ct'],
                cwd=repo_path, capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                parts = result.stdout.strip().split('|')
                if len(parts) >= 5:
                    info['latest_commit'] = {
                        'hash': parts[0],
                        'short_hash': parts[0][:7],
                        'author': parts[1],
                        'email': parts[2],
                        'message': parts[3],
                        'timestamp': int(parts[4])
                    }

            result = subprocess.run(
                ['git', 'branch', '-a'],
                cwd=repo_path, capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                info['branches'] = [b.strip().replace('* ', '') for b in result.stdout.strip().split('\n') if b.strip()]

        except Exception:
            pass

        return info

    def _scan_code_files(self, repo_path: Path) -> List[str]:
        code_files = []

        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith('.')]

            for file in files:
                file_path = Path(root) / file

                if file.startswith('.') and file.count('.') == 1:
                    continue

                ext = file_path.suffix.lower()
                if ext in IGNORE_EXTENSIONS:
                    continue

                if ext in SUPPORTED_EXTENSIONS or file_path.name in {'Makefile', 'Dockerfile', 'Vagrantfile', 'Gemfile', 'Rakefile', 'CMakeLists.txt'}:
                    code_files.append(str(file_path))

        return code_files

    def _parse_file(self, file_path: str, language: str) -> List[CodeUnit]:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            return []

        if not content.strip():
            return []

        units = []
        lines = content.split('\n')

        if language == 'python':
            units = self._parse_python(content, file_path)
        elif language == 'javascript':
            units = self._parse_javascript(content, file_path)
        elif language == 'typescript':
            units = self._parse_typescript(content, file_path)
        elif language == 'java':
            units = self._parse_java(content, file_path)
        elif language == 'sql':
            units = self._parse_sql(content, file_path)
        elif language == 'go':
            units = self._parse_go(content, file_path)
        elif language == 'vue':
            units = self._parse_vue(content, file_path)
        else:
            units = self._parse_generic(content, file_path, language)

        return units

    def _parse_python(self, content: str, file_path: str) -> List[CodeUnit]:
        units = []

        class_match = re.finditer(r'^class\s+(\w+)(?:\([^)]*\))?\s*:', content, re.MULTILINE)
        for match in class_match:
            start_line = content[:match.start()].count('\n') + 1
            name = match.group(1)

            bracket_count = 0
            end_pos = match.end()
            for i, c in enumerate(content[match.end():], start=match.end()):
                if c == ':':
                    bracket_count += 1
                elif c == '\n' and bracket_count == 1:
                    end_pos = i + match.end() + 1
                    break
                elif c == '\n':
                    bracket_count = 0

            class_body = content[match.start():end_pos]
            doc_match = re.search(r'^\s*"""(.*?)"""', class_body, re.DOTALL | re.MULTILINE)
            doc_comment = doc_match.group(1).strip() if doc_match else ""

            units.append(CodeUnit(
                type='class',
                name=name,
                file_path=file_path,
                start_line=start_line,
                end_line=end_pos.count('\n') + start_line,
                content=class_body.strip(),
                doc_comment=doc_comment
            ))

        func_match = re.finditer(r'^(?:async\s+)?def\s+(\w+)\s*\(([^)]*)\)(?:\s*->\s*([^:]+))?\s*:', content, re.MULTILINE)
        for match in func_match:
            start_line = content[:match.start()].count('\n') + 1
            name = match.group(1)
            params_str = match.group(2)
            return_type = match.group(3) or ""

            params = []
            for p in params_str.split(','):
                p = p.strip()
                if p:
                    parts = p.split(':')
                    param_name = parts[0].strip()
                    param_type = parts[1].strip() if len(parts) > 1 else "Any"
                    params.append({"name": param_name, "type": param_type})

            bracket_count = 0
            end_pos = match.end()
            for i, c in enumerate(content[match.end():], start=match.end()):
                if c == ':':
                    bracket_count += 1
                elif c == '\n' and bracket_count == 1:
                    end_pos = i + match.end() + 1
                    break
                elif c == '\n':
                    bracket_count = 0

            func_body = content[match.start():end_pos]
            doc_match = re.search(r'^\s+"""(.*?)"""', func_body, re.DOTALL | re.MULTILINE)
            doc_comment = doc_match.group(1).strip() if doc_match else ""

            units.append(CodeUnit(
                type='function',
                name=name,
                file_path=file_path,
                start_line=start_line,
                end_line=end_pos.count('\n') + start_line,
                content=func_body.strip(),
                signature=f"def {name}({params_str})" + (f" -> {return_type}" if return_type else ""),
                doc_comment=doc_comment,
                parameters=params,
                return_type=return_type
            ))

        const_match = re.finditer(r'^([A-Z][A-Z0-9_]*)\s*=\s*(.+)', content, re.MULTILINE)
        for match in const_match:
            if 'import' not in match.group(2)[:20]:
                start_line = content[:match.start()].count('\n') + 1
                units.append(CodeUnit(
                    type='constant',
                    name=match.group(1),
                    file_path=file_path,
                    start_line=start_line,
                    end_line=start_line,
                    content=match.group(0).strip()
                ))

        return units

    def _parse_javascript(self, content: str, file_path: str) -> List[CodeUnit]:
        units = []

        func_patterns = [
            r'(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)\s*\{',
            r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)\s*=>',
            r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?function\s*\(([^)]*)\)',
        ]

        for pattern in func_patterns:
            for match in re.finditer(pattern, content):
                start_line = content[:match.start()].count('\n') + 1
                name = match.group(1)
                params = match.group(2) if match.lastindex >= 2 else ""

                units.append(CodeUnit(
                    type='function',
                    name=name,
                    file_path=file_path,
                    start_line=start_line,
                    end_line=start_line + 10,
                    content=match.group(0)[:200],
                    signature=f"{name}({params})"
                ))

        class_pattern = r'class\s+(\w+)(?:\s+extends\s+\w+)?\s*\{'
        for match in re.finditer(class_pattern, content):
            start_line = content[:match.start()].count('\n') + 1
            units.append(CodeUnit(
                type='class',
                name=match.group(1),
                file_path=file_path,
                start_line=start_line,
                end_line=start_line + 20,
                content=match.group(0)[:300]
            ))

        return units

    def _parse_typescript(self, content: str, file_path: str) -> List[CodeUnit]:
        units = []

        interface_pattern = r'interface\s+(\w+)(?:\s*<[^>]+>)?\s*\{([^}]*)\}'
        for match in re.finditer(interface_pattern, content, re.DOTALL):
            start_line = content[:match.start()].count('\n') + 1
            props = re.findall(r'(\w+)[\??]:\s*([^;]+);', match.group(2))
            units.append(CodeUnit(
                type='interface',
                name=match.group(1),
                file_path=file_path,
                start_line=start_line,
                end_line=start_line + match.group(2).count('\n'),
                content=match.group(0),
                signature=str([{"name": p[0], "type": p[1]} for p in props])
            ))

        type_alias = r'type\s+(\w+)\s*=\s*([^;]+);'
        for match in re.finditer(type_alias, content):
            start_line = content[:match.start()].count('\n') + 1
            units.append(CodeUnit(
                type='type',
                name=match.group(1),
                file_path=file_path,
                start_line=start_line,
                end_line=start_line,
                content=match.group(0)
            ))

        units.extend(self._parse_javascript(content, file_path))

        return units

    def _parse_java(self, content: str, file_path: str) -> List[CodeUnit]:
        units = []

        class_pattern = r'(?:public|private|protected)?\s*(?:abstract|final)?\s*class\s+(\w+)(?:\s+extends\s+\w+)?(?:\s+implements\s+[^\\{]+)?\s*\{'
        for match in re.finditer(class_pattern, content):
            start_line = content[:match.start()].count('\n') + 1
            units.append(CodeUnit(
                type='class',
                name=match.group(1),
                file_path=file_path,
                start_line=start_line,
                end_line=start_line + 50,
                content=match.group(0)[:300]
            ))

        method_pattern = r'(?:public|private|protected)?\s*(?:static)?\s*(?:\w+(?:\[\])?\s+)+(\w+)\s*\(([^)]*)\)\s*(?:throws\s+[^;]+)?\s*\{'
        for match in re.finditer(method_pattern, content):
            start_line = content[:match.start()].count('\n') + 1
            return_type = match.group(0).split()[0]
            if return_type in ['public', 'private', 'protected', 'static']:
                return_type = content[match.start():].split()[2] if len(content[match.start():].split()) > 2 else "void"

            units.append(CodeUnit(
                type='method',
                name=match.group(1),
                file_path=file_path,
                start_line=start_line,
                end_line=start_line + 10,
                content=match.group(0)[:200],
                signature=f"{return_type} {match.group(1)}({match.group(2)})",
                return_type=return_type
            ))

        return units

    def _parse_sql(self, content: str, file_path: str) -> List[CodeUnit]:
        units = []

        create_table = re.finditer(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?\s*\(([\s\S]*?)\)\s*;', content, re.IGNORECASE)
        for match in create_table:
            start_line = content[:match.start()].count('\n') + 1
            columns = re.findall(r'`?(\w+)`?\s+(\w+(?:\([^)]+\))?)', match.group(2))

            units.append(CodeUnit(
                type='table',
                name=match.group(1),
                file_path=file_path,
                start_line=start_line,
                end_line=start_line + match.group(2).count('\n') + 2,
                content=match.group(0),
                signature=str([{"column": c[0], "type": c[1]} for c in columns[:10]])
            ))

        create_index = re.finditer(r'CREATE\s+(?:UNIQUE\s+)?INDEX\s+`?(\w+)`?\s+ON\s+`?(\w+)`?\s*\(([^)]+)\)', content, re.IGNORECASE)
        for match in create_index:
            start_line = content[:match.start()].count('\n') + 1
            units.append(CodeUnit(
                type='index',
                name=match.group(1),
                file_path=file_path,
                start_line=start_line,
                end_line=start_line,
                content=match.group(0)
            ))

        proc_pattern = r'CREATE\s+(?:DEFINER[^\s]+\s+)?(?:PROCEDURE|FUNCTION)\s+`?(\w+)`?\s*\(([\s\S]*?)\)\s*(?:RETURNS\s+\w+\s+)?BEGIN([\s\S]*?)END\s*//'
        for match in re.finditer(proc_pattern, content, re.IGNORECASE):
            start_line = content[:match.start()].count('\n') + 1
            units.append(CodeUnit(
                type='procedure',
                name=match.group(1),
                file_path=file_path,
                start_line=start_line,
                end_line=start_line + match.group(3).count('\n') + 5,
                content=match.group(0)[:500]
            ))

        return units

    def _parse_go(self, content: str, file_path: str) -> List[CodeUnit]:
        units = []

        func_pattern = r'func\s+(?:\([^)]+\)\s+)?(\w+)\s*\(([^)]*)\)(?:\s+(\w+))?\s*\{'
        for match in re.finditer(func_pattern, content):
            start_line = content[:match.start()].count('\n') + 1
            name = match.group(1)
            params = match.group(2)
            return_type = match.group(3) or ""

            units.append(CodeUnit(
                type='function',
                name=name,
                file_path=file_path,
                start_line=start_line,
                end_line=start_line + 10,
                content=match.group(0)[:200],
                signature=f"func {name}({params})" + (f" {return_type}" if return_type else ""),
                return_type=return_type
            ))

        struct_pattern = r'type\s+(\w+)\s+struct\s*\{([^}]*)\}'
        for match in re.finditer(struct_pattern, content, re.DOTALL):
            start_line = content[:match.start()].count('\n') + 1
            fields = re.findall(r'(\w+)\s+(\w+)', match.group(2))

            units.append(CodeUnit(
                type='struct',
                name=match.group(1),
                file_path=file_path,
                start_line=start_line,
                end_line=start_line + match.group(2).count('\n') + 1,
                content=match.group(0),
                signature=str([{"field": f[0], "type": f[1]} for f in fields])
            ))

        interface_pattern = r'type\s+(\w+)\s+interface\s*\{([^}]*)\}'
        for match in re.finditer(interface_pattern, content, re.DOTALL):
            start_line = content[:match.start()].count('\n') + 1
            methods = re.findall(r'(\w+)\s*\(([^)]*)\)(?:\s+(\w+))?', match.group(2))

            units.append(CodeUnit(
                type='interface',
                name=match.group(1),
                file_path=file_path,
                start_line=start_line,
                end_line=start_line + match.group(2).count('\n') + 1,
                content=match.group(0),
                signature=str([{"method": m[0], "params": m[1], "returns": m[2] or ""} for m in methods])
            ))

        return units

    def _parse_vue(self, content: str, file_path: str) -> List[CodeUnit]:
        units = []

        template_match = re.search(r'<template>([\s\S]*)</template>', content)
        if template_match:
            units.append(CodeUnit(
                type='template',
                name='template',
                file_path=file_path,
                start_line=1,
                end_line=template_match.group(1).count('\n') + 1,
                content=template_match.group(1)[:500]
            ))

        script_match = re.search(r'<script[^>]*>([\s\S]*)</script>', content)
        if script_match:
            script_content = script_match.group(1)

            export_default = re.search(r'export\s+default\s*\{([\s\S]*)\}', script_content)
            if export_default:
                data_match = re.search(r'data\s*\(\)\s*\{([\s\S]*?)return\s*\{', export_default.group(1), re.DOTALL)
                if data_match:
                    units.append(CodeUnit(
                        type='data',
                        name='data',
                        file_path=file_path,
                        start_line=10,
                        end_line=20,
                        content=data_match.group(1)[:300]
                    ))

            methods = re.findall(r'(\w+)\s*\([^)]*\)\s*\{', export_default.group(1) if export_default else script_content)
            for i, method_name in enumerate(methods[:20]):
                units.append(CodeUnit(
                    type='method',
                    name=method_name,
                    file_path=file_path,
                    start_line=15 + i * 3,
                    end_line=20 + i * 3,
                    content=f"{method_name}() {{...}}"
                ))

        style_match = re.search(r'<style[^>]*>([\s\S]*)</style>', content)
        if style_match:
            units.append(CodeUnit(
                type='style',
                name='styles',
                file_path=file_path,
                start_line=1,
                end_line=style_match.group(1).count('\n') + 1,
                content=style_match.group(1)[:300]
            ))

        return units

    def _parse_generic(self, content: str, file_path: str, language: str) -> List[CodeUnit]:
        units = []

        if len(content) > 5000:
            chunks = [content[i:i+2000] for i in range(0, min(len(content), 10000), 2000)]
            for i, chunk in enumerate(chunks):
                units.append(CodeUnit(
                    type='block',
                    name=f'block_{i+1}',
                    file_path=file_path,
                    start_line=i * 50 + 1,
                    end_line=(i + 1) * 50,
                    content=chunk
                ))

        return units

    def _detect_tech_stack(self, code_files: List[str]) -> List[str]:
        tech_stack = set()

        frameworks = {
            'django': ['django', 'models.py', 'views.py', 'urls.py'],
            'flask': ['flask', 'app.route', '@app.route'],
            'fastapi': ['fastapi', 'app.get', '@app'],
            'express': ['express', 'router.get', 'app.use'],
            'spring': ['spring', '@Controller', '@Service', '@Repository'],
            'react': ['react', 'useState', 'useEffect', 'React.Component'],
            'vue': ['vue', 'vue-router', 'createApp'],
            'angular': ['@Component', '@NgModule', 'angular'],
            'springboot': ['springboot', '@SpringBootApplication'],
            'laravel': ['laravel', 'Route::', 'app/Http/Controllers'],
            'rails': ['rails', 'application.rb', 'config/routes'],
            'gin': ['gin-gonic', 'gin.Default', 'r.GET'],
            'echo': ['labstack/echo', 'e.GET', 'echo.Context'],
            'fiber': ['gofiber', 'fiber.NewApp', 'app.Get'],
            'nextjs': ['nextjs', 'getServerSideProps', 'getStaticProps'],
            'nuxt': ['nuxt', 'pages/', 'layouts/'],
            'svelte': ['svelte', '<script>', '<style>'],
            'solid': ['solid-js', 'createSignal', 'createEffect'],
        }

        for file_path in code_files[:50]:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(5000)

                for framework, patterns in frameworks.items():
                    for pattern in patterns:
                        if pattern in content:
                            tech_stack.add(framework)
                            break

                ext = Path(file_path).suffix.lower()
                if ext in SUPPORTED_EXTENSIONS:
                    lang = SUPPORTED_EXTENSIONS[ext]
                    tech_stack.add(lang)

            except Exception:
                continue

        return sorted(list(tech_stack))

    def _build_project_tree(self, code_files: List[str]) -> Dict:
        tree = {"name": "root", "type": "dir", "children": []}

        file_nodes = {}
        dir_nodes = {}

        for file_path in sorted(code_files):
            parts = Path(file_path).parts
            parent_path = ""

            for i, part in enumerate(parts[:-1]):
                current_path = "/".join(parts[:i+1])
                if current_path not in dir_nodes:
                    dir_node = {
                        "name": part,
                        "type": "dir",
                        "path": current_path,
                        "children": []
                    }
                    dir_nodes[current_path] = dir_node

                    if parent_path and parent_path in dir_nodes:
                        dir_nodes[parent_path]["children"].append(dir_node)
                    elif i == 0:
                        tree["children"].append(dir_node)

                parent_path = current_path

            file_node = {
                "name": parts[-1],
                "type": "file",
                "path": file_path,
                "ext": Path(file_path).suffix.lower()
            }
            file_nodes[file_path] = file_node

            if parent_path and parent_path in dir_nodes:
                dir_nodes[parent_path]["children"].append(file_node)
            elif parent_path:
                tree["children"].append(file_node)

        return tree

    def _analyze_dependencies(self, units: List[CodeUnit]) -> Dict:
        graph = {}

        for unit in units:
            if unit.dependencies:
                graph[unit.name] = {
                    "file": unit.file_path,
                    "type": unit.type,
                    "imports": unit.dependencies[:10]
                }

        return graph

    def _generate_summary(self, project_name: str, tech_stack: List[str],
                          file_count: int, unit_count: int, lang_stats: Dict) -> str:
        top_langs = sorted(lang_stats.items(), key=lambda x: -x[1])[:5]
        lang_str = ", ".join([f"{lang}({count})" for lang, count in top_langs])

        framework = ""
        if 'django' in tech_stack:
            framework = "Django"
        elif 'flask' in tech_stack:
            framework = "Flask"
        elif 'fastapi' in tech_stack:
            framework = "FastAPI"
        elif 'express' in tech_stack:
            framework = "Express.js"
        elif 'springboot' in tech_stack:
            framework = "Spring Boot"
        elif 'gin' in tech_stack:
            framework = "Gin"
        elif 'react' in tech_stack:
            framework = "React"
        elif 'vue' in tech_stack:
            framework = "Vue.js"
        elif 'angular' in tech_stack:
            framework = "Angular"

        summary = f"""## {project_name}

**技术栈**: {', '.join(tech_stack[:6]) or '未识别'}
**框架**: {framework or '通用'}
**代码统计**: {file_count} 个文件, {unit_count} 个代码单元
**语言分布**: {lang_str}

这是一个 **{framework or '多语言'}** 项目。"""

        return summary

    def _unit_to_dict(self, unit: CodeUnit) -> Dict:
        return {
            "type": unit.type,
            "name": unit.name,
            "file_path": unit.file_path,
            "start_line": unit.start_line,
            "end_line": unit.end_line,
            "content": unit.content[:5000],
            "signature": unit.signature,
            "doc_comment": unit.doc_comment,
            "dependencies": unit.dependencies or [],
            "return_type": unit.return_type,
            "parameters": unit.parameters or []
        }

def is_git_repo(path: Path) -> bool:
    return (path / '.git').exists()
