#!/usr/bin/env python3
import os
import re
import sys


def find_wpsweb_root(current_path: str) -> str:
    """查找 wpsweb 根目录"""
    path = os.path.abspath(current_path)
    
    # 从当前路径开始向上查找，直到找到包含 wpsweb 的目录
    while path != os.path.dirname(path):
        wpsweb_path = os.path.join(path, "wpsweb")
        if os.path.isdir(wpsweb_path):
            return wpsweb_path
        path = os.path.dirname(path)
    
    # 如果当前目录就是 wpsweb
    if os.path.basename(current_path) == "wpsweb":
        return os.path.abspath(current_path)
    
    return ""


def modify_makefile(makefile_path: str) -> bool:
    """修改 Makefile 文件内容"""
    if not os.path.exists(makefile_path):
        print(f"Makefile 不存在: {makefile_path}", file=sys.stderr)
        return False
    
    try:
        # 读取文件内容
        with open(makefile_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 1. 去掉 -Wl,-s 参数
        content = re.sub(r'-Wl,-s', '', content)
        
        # 2. 修改 -O2 为 -g
        content = re.sub(r'-O2\b', '-g', content)
        
        # 检查是否有修改
        if content == original_content:
            print("Makefile 内容无需修改")
            return True
        
        # 写回文件
        with open(makefile_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"已成功修改 Makefile: {makefile_path}")
        print("修改内容:")
        print("  - 移除了 -Wl,-s 参数")
        print("  - 将 -O2 修改为 -g")
        
        return True
        
    except Exception as e:
        print(f"修改 Makefile 失败: {e}", file=sys.stderr)
        return False


def command_modify_makefile(mode: str = None) -> None:
    """修改 wpsweb/server/Makefile 命令"""
    # 获取当前工作目录
    current_dir = os.getcwd()
    
    if mode == "coding":
        # coding模式：创建VSCode配置文件
        create_vscode_configs(current_dir)
        return
    
    # 默认模式：执行原有逻辑
    # 查找 wpsweb 根目录
    wpsweb_root = find_wpsweb_root(current_dir)
    
    if not wpsweb_root:
        print("错误: 未找到 wpsweb 目录", file=sys.stderr)
        print("请确保当前目录在 wpsweb 或其父级目录中", file=sys.stderr)
        sys.exit(1)
    
    print(f"找到 wpsweb 目录: {wpsweb_root}")
    
    # 构建 Makefile 路径
    makefile_path = os.path.join(wpsweb_root, "server", "Makefile")
    
    # 修改 Makefile
    if modify_makefile(makefile_path):
        print("完成。modify_makefile")
    else:
        sys.exit(1) 

    if modify_build_server_script(wpsweb_root):
        print("完成。modify_build_server_script")
    else:
        sys.exit(1) 


def modify_build_server_script(wpsweb_root: str) -> bool:
    """修改 wpsweb/build_server.sh 文件内容"""
    build_server_path = os.path.join(wpsweb_root, "build_server.sh")
    
    # 获取当前工作目录作为基础路径
    current_dir = os.getcwd()
    
    # 构建脚本内容，动态替换路径
    script_content = f"""#!/bin/bash
export LD_LIBRARY_PATH={current_dir}/debug_weboffice/wps_build/WPSOffice/office6
SERVER_PATH={current_dir}/wpsweb/server
if [ -e $SERVER_PATH/lib ]
then
    rm -rf $SERVER_PATH/lib
fi
ln -s $LD_LIBRARY_PATH $SERVER_PATH/lib
cd $SERVER_PATH
make clean
make webwpp LOCAL_LIB=1
"""
    
    try:
        # 写入文件
        with open(build_server_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # 设置执行权限
        os.chmod(build_server_path, 0o755)
        
        print(f"已成功修改 build_server.sh: {build_server_path}")
        print("脚本内容:")
        print(f"  - LD_LIBRARY_PATH: {current_dir}/debug_weboffice/wps_build/WPSOffice/office6")
        print(f"  - SERVER_PATH: {current_dir}/wpsweb/server")
        print("  - 已设置执行权限")
        
        return True
        
    except Exception as e:
        print(f"修改 build_server.sh 失败: {e}", file=sys.stderr)
        return False


def create_vscode_configs(current_dir: str) -> None:
    """创建VSCode配置文件"""
    # 构建目标目录路径
    vscode_dir = os.path.join(current_dir, "wpsmain", "Coding", ".vscode")
    
    try:
        # 创建目录（如果不存在）
        os.makedirs(vscode_dir, exist_ok=True)
        
        # 创建launch.json文件
        launch_json_path = os.path.join(vscode_dir, "launch.json")
        launch_json_content = f"""{{
    // 使用 IntelliSense 了解相关属性。 
    // 悬停以查看现有属性的描述。
    // 欲了解更多信息，请访问: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {{
            "type": "lldb",
            "request": "launch",
            "name": "(lldb)启动",
            "program": "{current_dir}/debug_weboffice/wps_build/WPSOffice/office6/webwpp",
            "args": ["--port=9040","--debug"],
            "cwd": "{current_dir}/debug_weboffice/wps_build/WPSOffice/office6",
            "env": {{"LD_LIBRARY_PATH":"{current_dir}/debug_weboffice/wps_build/WPSOffice/office6","DEBUG":"1","CRASH_LOG_DIR":"{current_dir}/weboffice_crash_log"}},
            "initCommands": ["setting set target.x86-disassembly-flavor intel"],
            "sourceMap": {{
                "/build/data/master_kso_v12/wo_x64_N/wpsenv/qt/source/qtbase/src/gui/text/":"{current_dir}/debug_weboffice/xwares/3rd/source/qtbase/src/gui/text/"
            }}
        }}
    ]
}}"""
        
        with open(launch_json_path, 'w', encoding='utf-8') as f:
            f.write(launch_json_content)
        
        # 创建settings.json文件
        settings_json_path = os.path.join(vscode_dir, "settings.json")
        settings_json_content = f"""{{
    "clangd.arguments": [
        "--compile-commands-dir={current_dir}/debug_weboffice/wps_build"
    ],
    "git.ignoreLimitWarning": true
}}"""
        
        with open(settings_json_path, 'w', encoding='utf-8') as f:
            f.write(settings_json_content)
        
        print(f"已成功创建VSCode配置文件:")
        print(f"  - launch.json: {launch_json_path}")
        print(f"  - settings.json: {settings_json_path}")
        print(f"  基础路径: {current_dir}")
        
    except Exception as e:
        print(f"创建VSCode配置文件失败: {e}", file=sys.stderr)
        sys.exit(1)
