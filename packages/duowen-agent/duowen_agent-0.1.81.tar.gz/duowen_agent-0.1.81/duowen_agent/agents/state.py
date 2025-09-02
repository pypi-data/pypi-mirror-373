from typing import Optional, Dict

from pydantic import BaseModel, Field


class FileParams(BaseModel):
    file_path: str
    content: str | bytes
    permissions: Optional[str] = Field(default="644")
    description: Optional[str] = Field(default="")

    @property
    def is_bytes(self):
        return isinstance(self.content, bytes)


class Resources(BaseModel):
    files: Optional[Dict[str, FileParams]] = {}

    def file_add(
        self,
        file_path: str,
        content: str | bytes,
        permissions: Optional[str] = "644",
        description: Optional[str] = "",
    ):
        self.files[file_path] = FileParams(
            file_path=file_path,
            content=content,
            permissions=permissions,
            description=description,
        )

    def file_str_replace(self, file_path: str, old_str: str, new_str: str):
        _file = self.files[file_path]
        if _file.is_bytes:
            raise ValueError("file is bytes, can not replace")

        if old_str in self.files[file_path].content:
            self.files[file_path].content = self.files[file_path].content.replace(
                old_str, new_str
            )
            return True
        else:
            return False

    def file_full_rewrite(
        self,
        file_path: str,
        content: str | bytes,
        permissions: Optional[str] = "644",
        description: Optional[str] = "",
    ):
        self.files[file_path] = FileParams(
            file_path=file_path,
            content=content,
            permissions=permissions,
            description=description,
        )

    def file_delete(self, file_path: str):
        if file_path in self.files[file_path]:
            del self.files[file_path]

    def file_exists(self, file_path: str):
        return file_path in self.files

    def read_file(self, file_path: str, start_line: int, end_line: int):
        # 通过路径判断文件是否可读,例如 .txt .csv等
        _file = self.files[file_path]
        if _file.is_bytes:
            raise ValueError("file is bytes, can not read")

        _lines = self.files[file_path].content.split("\n")
        return {
            "content": "\n".join(_lines[start_line:end_line]),
            "start_line": start_line,
            "end_line": end_line if end_line is not None else len(_lines),
            "total_lines": len(_lines),
        }

    def read_all_file(self, file_path: str):
        return self.files[file_path].content
