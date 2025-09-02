import json
import os
from typing import Optional, Dict, Any

from openai import OpenAI


class SiliconCloudBatchTool:
    def __init__(self, api_key: str):
        """
        初始化批量推理工具类
        :param api_key: SiliconCloud API密钥
        """
        self.client = OpenAI(api_key=api_key, base_url="https://api.siliconflow.cn/v1")

    @staticmethod
    def validate_file_format(file_path: str, check_model_uniform: bool = False) -> Dict:
        """
        验证输入文件格式是否符合规范
        :param file_path: 文件路径
        :param check_model_uniform: 是否检查模型一致性
        :return: 验证结果字典
        """
        errors = []
        custom_ids = set()
        models = set()
        line_num = 0

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line_num += 1
                    line = line.strip()
                    if not line:
                        continue

                    # 解析JSON
                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError as e:
                        errors.append(f"行 {line_num}: JSON解析失败 - {str(e)}")
                        continue

                    # 检查必需字段
                    if "custom_id" not in record:
                        errors.append(f"行 {line_num}: 缺少 required 'custom_id' 字段")
                        continue

                    # 检查custom_id唯一性
                    custom_id = record["custom_id"]
                    if custom_id in custom_ids:
                        errors.append(f"行 {line_num}: custom_id '{custom_id}' 重复")
                    custom_ids.add(custom_id)

                    # 检查请求体
                    body = record.get("body", {})
                    if "messages" not in body:
                        errors.append(
                            f"行 {line_num}: body中缺少 required 'messages' 字段"
                        )
                        continue

                    messages = body["messages"]
                    if not isinstance(messages, list) or len(messages) == 0:
                        errors.append(
                            f"行 {line_num}: messages必须是至少包含一条消息的数组"
                        )
                        continue

                    # 检查消息格式
                    last_role = None
                    for idx, msg in enumerate(messages):
                        if "role" not in msg or "content" not in msg:
                            errors.append(
                                f"行 {line_num}: 消息 {idx+1} 缺少role或content字段"
                            )
                            continue
                        if msg["role"] not in ["system", "user", "assistant"]:
                            errors.append(
                                f"行 {line_num}: 消息 {idx+1} 包含非法role值 '{msg['role']}'"
                            )
                        last_role = msg["role"]

                    # 检查最后一条消息角色
                    if last_role != "user":
                        errors.append(f"行 {line_num}: 最后一条消息的role必须是'user'")

                    # 收集模型信息
                    if check_model_uniform:
                        model = body.get("model")
                        if model:
                            models.add(model)

                # 检查模型一致性
                if check_model_uniform and len(models) > 1:
                    errors.append(f"检测到多个不同模型: {', '.join(models)}")

            return {
                "is_valid": len(errors) == 0,
                "error_count": len(errors),
                "errors": errors,
                "total_records": line_num,
                "unique_custom_ids": len(custom_ids),
            }

        except Exception as e:
            raise RuntimeError(f"文件验证异常: {str(e)}")

    def upload_file(self, file_path: str, validate: bool = True) -> FileObject:
        """
        上传文件并可选执行验证
        :param file_path: 文件路径
        :param validate: 是否执行前置验证
        """
        if validate:
            validation = self.validate_file_format(file_path)
            if not validation["is_valid"]:
                error_msg = "\n".join(validation["errors"][:3])  # 显示前三个错误
                raise ValueError(
                    f"文件验证失败（共{validation['error_count']}个错误）:\n{error_msg}"
                )

        try:
            with open(file_path, "rb") as f:
                return self.client.files.create(file=f, purpose="batch")
        except Exception as e:
            raise RuntimeError(f"文件上传失败: {str(e)}")

    def get_file_list(self) -> Any:
        """获取所有文件列表"""
        try:
            return self.client.files.list()
        except Exception as e:
            raise RuntimeError(f"获取文件列表失败: {str(e)}")

    def create_batch_job(
        self,
        input_file_id: str,
        endpoint: str = "/v1/chat/completions",
        completion_window: str = "24h",
        metadata: Optional[Dict] = None,
        replace_model: Optional[str] = None,
    ) -> Any:
        """
        创建批量推理任务
        :param input_file_id: 输入文件ID
        :param endpoint: API端点，默认为对话接口
        :param completion_window: 完成时间窗口
        :param metadata: 元数据信息
        :param replace_model: 要替换的模型名称
        :return: 批量任务对象
        """
        try:
            extra_body = (
                {"replace": {"model": replace_model}} if replace_model else None
            )

            return self.client.batches.create(
                input_file_id=input_file_id,
                endpoint=endpoint,
                completion_window=completion_window,
                metadata=metadata or {},
                extra_body=extra_body,
            )
        except Exception as e:
            raise RuntimeError(f"创建批量任务失败: {str(e)}")

    def get_batch_job(self, batch_id: str) -> Any:
        """获取单个任务详情"""
        try:
            return self.client.batches.retrieve(batch_id)
        except Exception as e:
            raise RuntimeError(f"获取任务详情失败: {str(e)}")

    def get_batch_job_list(self) -> Any:
        """获取所有批量任务列表"""
        try:
            return self.client.batches.list()
        except Exception as e:
            raise RuntimeError(f"获取任务列表失败: {str(e)}")

    def cancel_batch_job(self, batch_id: str) -> Any:
        """取消批量任务"""
        try:
            return self.client.batches.cancel(batch_id)
        except Exception as e:
            raise RuntimeError(f"取消任务失败: {str(e)}")


# 示例用法
if __name__ == "__main__":
    # 初始化工具
    tool = SiliconCloudBatchTool(api_key="YOUR_API_KEY")

    # 上传文件示例
    try:
        uploaded_file = tool.upload_file("batch_input.jsonl")
        print(f"文件上传成功，ID: {uploaded_file.id}")
    except Exception as e:
        print(e)

    # 创建批量任务示例
    try:
        batch_job = tool.create_batch_job(
            input_file_id="file-abc123",
            replace_model="deepseek-ai/DeepSeek-V3",
            metadata={"description": "测试任务"},
        )
        print(f"任务创建成功，ID: {batch_job.id}")
    except Exception as e:
        print(e)

    # 获取任务状态示例
    try:
        job_status = tool.get_batch_job("batch_abc123")
        print(f"任务状态: {job_status.status}")
    except Exception as e:
        print(e)
