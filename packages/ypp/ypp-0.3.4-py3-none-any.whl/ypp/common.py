#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公共函数模块
包含 ypp 包中所有模块共用的函数
"""

import os
import json
import subprocess
import sys


def run_command(command_args, cwd_path=None, interactive=False) -> int:
    """执行命令并返回结果
    
    Args:
        command_args: 命令参数列表
        cwd_path: 工作目录
        interactive: 是否启用交互式模式（支持实时输出和用户输入）
    """
    if interactive:
        # 交互式模式：实时显示输出，支持用户输入
        process = subprocess.Popen(
            command_args,
            cwd=cwd_path,
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True,
        )
        process.wait()
        return process.returncode
    else:
        # 非交互式模式：捕获输出到管道
        process = subprocess.Popen(
            command_args,
            cwd=cwd_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        assert process.stdout is not None
        for line in process.stdout:
            sys.stdout.write(line)
        process.wait()
        return process.returncode


def ensure_directory(path: str) -> None:
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)


def path_exists_and_not_empty(path: str) -> bool:
    """检查路径是否存在且不为空"""
    return os.path.exists(path) and any(True for _ in os.scandir(path))


def get_config_path() -> str:
    """获取配置文件路径"""
    return os.path.expanduser("~/.ypp.json")


def load_config() -> dict:
    """加载配置文件"""
    config_path = get_config_path()
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def save_config(config: dict) -> None:
    """保存配置文件"""
    config_path = get_config_path()
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"保存配置文件失败: {e}", file=sys.stderr)
        sys.exit(1)


def get_workspace_dir() -> str:
    """获取配置的 workspace 路径，如果没有配置则使用默认路径"""
    config = load_config()
    workspace_path = config.get('work_dir')
    
    if workspace_path:
        return os.path.expanduser(workspace_path)
    
    # 默认逻辑：如果 ~/workspace 存在，使用它，否则使用 ~
    default_workspace = os.path.expanduser("~/workspace")
    return default_workspace if os.path.isdir(default_workspace) else os.path.expanduser("~")
