#!/usr/bin/env python3
"""
VSCode 配置文件处理模块
"""

import os
import sys
from typing import Optional


def create_webwps_launch_config(current_dir: str) -> None:
    """创建 webwps 的 launch.json 配置文件"""
    # 构建目标目录路径
    vscode_dir = os.path.join(current_dir, ".vscode")
    
    try:
        # 创建目录（如果不存在）
        os.makedirs(vscode_dir, exist_ok=True)
        
        # 创建launch.json文件
        launch_json_path = os.path.join(vscode_dir, "launch.json")
        launch_json_content = """{
    // 使用 IntelliSense 了解相关属性。 
    // 悬停以查看现有属性的描述。
    // 欲了解更多信息，请访问: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "type": "pwa-chrome",
            "request": "attach",
            "name": "附加到Chrome",
            "port": 9222,
            "webRoot": "${workspaceFolder}",
            "sourceMaps": true,
            "smartStep": true,
            "skipFiles": [
                "**/node_modules/**"
            ],
            "urlFilter": "https://365.kdocs.cn/l/*",
            //"url": "https://www.kdocs.cn",
            "sourceMapPathOverrides": {
                "webpack:///./~/*": "${workspaceFolder}/client/app/node_modules/*",
                "webpack://?:*/*": "${workspaceFolder}/client/app/*"
            }
        }
    ]
}"""
        
        with open(launch_json_path, 'w', encoding='utf-8') as f:
            f.write(launch_json_content)
        
        print(f"已成功创建 webwps launch.json 配置文件:")
        print(f"  - 文件路径: {launch_json_path}")
        print(f"  - 配置类型: Chrome 调试器")
        print(f"  - 调试端口: 9222")
        print(f"  - URL 过滤: https://365.kdocs.cn/l/*")
        
    except Exception as e:
        print(f"创建 webwps launch.json 配置文件失败: {e}", file=sys.stderr)
        sys.exit(1)


def command_code_webwps() -> None:
    """code webwps 命令处理函数"""
    # 获取当前工作目录
    current_dir = os.getcwd()
    
    print(f"当前目录: {current_dir}")
    create_webwps_launch_config(current_dir) 