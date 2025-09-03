import os
import dill
from typing import Any, Dict, List, Optional, overload
from dataclasses import dataclass
STORAGE_FILENAME = "storage.dill"

@dataclass
class UserQuestion:
    question: str
    attachments: List[str]

@dataclass
class ToolCallResult:
    status: str # Literal["success", "error", "failed", "end"]
    content: str
    additional_outputs: Optional[List[str]] = None
    additional_context: Optional[str] = None
    additional_images: Optional[List[str]] = None
    next: Optional[str] = None

@dataclass
class ActItem:
    index: int
    reasoning: str
    tool_result: Optional[ToolCallResult] = None

@dataclass
class UserMessageItem:
    message: str

class State:
    def __init__(
        self,
        workspace: str,
        history: list[ActItem | UserMessageItem],
    ):
        self.workspace = workspace
        self.working_dir = os.path.join(self.workspace, "working")
        self.log_dir = os.path.join(self.workspace, "log")
        self.index = 0
        self.history = history
        self.context: str = ""
        self.__storage: Dict[str, Any] = {}
        if os.path.exists(self.get_log_file_path(STORAGE_FILENAME)):
            with open(self.get_log_file_path(STORAGE_FILENAME), "rb") as f:
                self.__storage = dill.load(f)

    def get_working_file_path(self, filename: str):
        return os.path.join(self.working_dir, filename)

    def get_log_file_path(self, filename: str):
        return os.path.join(self.log_dir, filename)

    def set_storage(self, key: str, value: Any):
        self.__storage.update({key: value})
        with open(self.get_log_file_path(STORAGE_FILENAME), "wb") as f:
            dill.dump(self.__storage, f)
    
    def get_user_question(self) -> str:
        question = ""
        if len(self.history) > 0 and isinstance(self.history[0], UserMessageItem):
            question = self.history[0].message
        return question

    def get_working_tree(self) -> str:
        if not os.path.exists(self.working_dir):
            return "No working directory"
        
        SKIP_DIRS = {
            'venv', 'env', '.venv', '.env',  # Python 虚拟环境
            'node_modules', '.node_modules',  # Node.js 依赖
            '__pycache__', '.pytest_cache',  # Python 缓存
            '.git', '.svn', '.hg',  # 版本控制
            'dist', 'build', 'target',  # 构建输出
            '.idea', '.vscode',  # IDE 配置
            'coverage', '.coverage',  # 测试覆盖率
            'logs', '.logs',  # 日志文件
            'tmp', 'temp', '.tmp', '.temp',  # 临时文件
            'cache', '.cache',  # 缓存文件
        }

        SKIP_FILES = {
            ".DS_Store"
        }
        
        def _list_files_recursive(path: str, level: int = 0, max_depth: int = 2) -> str:
            content = ""

            if level >= max_depth:
                return content

            try:
                entries = os.listdir(path)

                files = []
                dirs = []
                for entry in entries:
                    full_path = os.path.join(path, entry)
                    if os.path.isdir(full_path):
                        if entry not in SKIP_DIRS:
                            dirs.append(entry)
                    elif entry not in SKIP_FILES:
                        files.append(entry)
                
                for entry in sorted(files):
                    file_path = os.path.join(path, entry)
                    try:
                        file_size = os.path.getsize(file_path)
                        if file_size >= 1024 * 1024:  # 大于等于 1 MB
                            size_mb = file_size / (1024 * 1024)
                            content += f"{'  ' * level}- {entry} ({size_mb:.2f} MB)\n"
                        else:  # 小于 1 MB，显示为 KB
                            size_kb = file_size / 1024
                            content += f"{'  ' * level}- {entry} ({size_kb:.2f} KB)\n"
                    except Exception:
                        content += f"{'  ' * level}- {entry} (Can't get size)\n"
                
                for dir_entry in sorted(dirs):
                    content += f"{'  ' * level}- {dir_entry}/\n"
                    content += _list_files_recursive(
                        os.path.join(path, dir_entry), level + 1, max_depth
                    )
            except Exception as e:
                content += f"{'  ' * level}- Error accessing directory\n"
            
            return content
        
        def _count_files_recursive(path: str, level: int = 0, max_depth: int = 2) -> int:
            total = 0

            if level >= max_depth:
                return total

            try:
                entries = os.listdir(path)
                for entry in entries:
                    full_path = os.path.join(path, entry)
                    if os.path.isdir(full_path) and entry not in SKIP_DIRS:
                        total += _count_files_recursive(full_path, level + 1, max_depth)
                    elif entry not in SKIP_FILES:
                        total += 1
            except Exception:
                return 0
            return total
        
        file_list = _list_files_recursive(self.working_dir)
        total_files = _count_files_recursive(self.working_dir)
        header = f"<!-- File count: {total_files} -->\n"
        return header + file_list

    @overload
    def get_storage(self, key: str) -> Any: ...
    @overload
    def get_storage[T](self, key: str, default: T) -> T: ...
    def get_storage(self, key: str, default=None):
        return self.__storage.get(key, default)

    @property
    def _storage_snapshot(self) -> Dict[str, Any]:
        return self.__storage.copy()
