#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
仓库初始化命令模块
包含 wpsmain 和 wpsweb 仓库的初始化功能
"""

import os
import shutil
import sys
from typing import Optional

try:
    from .common import run_command
except ImportError:
    from common import run_command


def init_wpsmain() -> None:
    """初始化 wpsmain 仓库"""
    print("正在初始化 wpsmain 仓库...")
    
    # 在当前目录执行 krepo-ng init 命令
    print("正在执行 krepo-ng init 命令...")
    if shutil.which("krepo-ng") is None:
        print("找不到 krepo-ng 命令，请先安装或配置 PATH。", file=sys.stderr)
        sys.exit(2)
    
    rc = run_command(["krepo-ng", "init", "-b", "master_kso_v12", "--bundle", "all"], interactive=True)
    if rc == 0:
        print("wpsmain 仓库初始化完成！")
    else:
        print("wpsmain 仓库初始化失败！", file=sys.stderr)
        sys.exit(rc)


def init_wpsweb() -> None:
    """初始化 wpsweb 仓库"""
    print("正在初始化 wpsweb 仓库...")
        
    # 执行 git clone 命令
    print("正在克隆 wpsweb 仓库...")
    if shutil.which("git") is None:
        print("找不到 git 命令，请先安装或配置 PATH。", file=sys.stderr)
        sys.exit(2)
    
    rc = run_command(["git", "clone", "git@ksogit.kingsoft.net:wow/wpsweb.git"], interactive=True)
    if rc == 0:
        print("wpsweb 仓库初始化完成！")
    else:
        print("wpsweb 仓库初始化失败！", file=sys.stderr)
        sys.exit(rc)
