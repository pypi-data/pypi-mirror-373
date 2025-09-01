#!/usr/bin/env python3
"""
配置文件 - 管理API endpoints和其他配置信息
"""

import os


class Config:
    """配置类"""

    def __init__(self):
        # 飞书应用配置
        self.lark_app_id = os.getenv("LARK_APP_ID", "")
        self.lark_app_secret = os.getenv("LARK_APP_SECRET", "")

    def validate_config(self) -> list:
        """验证配置是否完整"""
        errors = []

        if not self.lark_app_id:
            errors.append("LARK_APP_ID 环境变量是必需的")

        if not self.lark_app_secret:
            errors.append("LARK_APP_SECRET 环境变量是必需的")

        return errors

    def ensure_required_config(self):
        """确保必需的配置存在，否则抛出异常"""
        errors = self.validate_config()
        if errors:
            raise ValueError("配置错误：\n" + "\n".join(f"- {error}" for error in errors))


# 创建全局配置实例
config = Config()
