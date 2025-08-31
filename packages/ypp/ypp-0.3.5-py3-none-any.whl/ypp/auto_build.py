#!/usr/bin/env python3
import os
import subprocess
import sys


def find_wpsmain_root(current_path: str) -> str:
    """查找 wpsmain 根目录"""
    path = os.path.abspath(current_path)
    
    # 从当前路径开始向上查找，直到找到包含 wpsmain 的目录
    while path != os.path.dirname(path):
        wpsmain_path = os.path.join(path, "wpsmain")
        if os.path.isdir(wpsmain_path):
            return wpsmain_path
        path = os.path.dirname(path)
    
    # 如果当前目录就是 wpsmain
    if os.path.basename(current_path) == "wpsmain":
        return os.path.abspath(current_path)
    
    return ""


def run_docker_command(command: str, cwd: str) -> bool:
    """在 Docker 中执行命令"""
    docker_cmd = ["kdocker", "-r", "qt5"] + command.split()
    
    print(f"执行命令: {' '.join(docker_cmd)}")
    print(f"工作目录: {cwd}")
    
    try:
        # 实时输出到终端
        process = subprocess.Popen(
            docker_cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # 实时读取并打印输出
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.rstrip())
        
        # 等待进程完成并获取返回码
        return_code = process.poll()
        
        if return_code == 0:
            return True
        else:
            print(f"命令执行失败，返回码: {return_code}", file=sys.stderr)
            return False
        
    except Exception as e:
        print(f"命令执行失败: {e}", file=sys.stderr)
        return False


def check_debug_weboffice_exists(wpsmain_path: str) -> bool:
    """检查 debug_weboffice 目录是否存在"""
    debug_path = os.path.join(wpsmain_path, "debug_weboffice")
    return os.path.isdir(debug_path)


def find_wpsweb_build_script(current_path: str) -> str:
    """查找 wpsweb 目录中的 build_server.sh 脚本"""
    path = os.path.abspath(current_path)
    
    # 从当前路径开始向上查找，直到找到包含 wpsweb 的目录
    while path != os.path.dirname(path):
        wpsweb_path = os.path.join(path, "wpsweb")
        if os.path.isdir(wpsweb_path):
            build_script_path = os.path.join(wpsweb_path, "build_server.sh")
            if os.path.isfile(build_script_path) and os.access(build_script_path, os.X_OK):
                return build_script_path
        path = os.path.dirname(path)
    
    # 如果当前目录就是 wpsweb
    if os.path.basename(current_path) == "wpsweb":
        build_script_path = os.path.join(current_path, "build_server.sh")
        if os.path.isfile(build_script_path) and os.access(build_script_path, os.X_OK):
            return build_script_path
    
    return ""


def command_auto_build() -> None:
    """自动编译 wpsmain 命令"""
    # 获取当前工作目录
    current_dir = os.getcwd()
    
    # 查找 wpsmain 根目录
    wpsmain_root = find_wpsmain_root(current_dir)
    
    if not wpsmain_root:
        print("错误: 未找到 wpsmain 目录", file=sys.stderr)
        print("请确保当前目录在 wpsmain 或其父级目录中", file=sys.stderr)
        sys.exit(1)
    
    print(f"找到 wpsmain 目录: {wpsmain_root}")
    
    # 步骤 1: 在 wpsmain 目录中执行 krepo-ng config --new -x weboffice
    print("\n=== 步骤 1: 配置 weboffice ===")
    if not run_docker_command("krepo-ng config --new -x weboffice", wpsmain_root):
        print("配置失败", file=sys.stderr)
        sys.exit(1)
    
    # 步骤 2: 检查是否创建了 debug_weboffice 目录
    print("\n=== 步骤 2: 检查 debug_weboffice 目录 ===")
    if not check_debug_weboffice_exists(current_dir):
        print("错误: 未找到 debug_weboffice 目录", file=sys.stderr)
        print("配置可能失败，请检查 krepo-ng config 命令的输出", file=sys.stderr)
        sys.exit(1)
    
    debug_weboffice_path = os.path.join(current_dir, "debug_weboffice")
    print(f"找到 debug_weboffice 目录: {debug_weboffice_path}")
    
    # 步骤 3: 进入 debug_weboffice 目录执行 krepo-ng build
    print("\n=== 步骤 3: 编译 weboffice ===")
    if not run_docker_command("krepo-ng build", debug_weboffice_path):
        print("编译失败", file=sys.stderr)
        sys.exit(1)
    
    # 步骤 4: 查找并执行 wpsweb 中的 build_server.sh 脚本
    print("\n=== 步骤 4: 执行 wpsweb build_server.sh ===")
    build_script_path = find_wpsweb_build_script(current_dir)
    
    if not build_script_path:
        print("警告: 未找到可执行的 build_server.sh 脚本", file=sys.stderr)
        print("请确保 wpsweb 目录中存在 build_server.sh 文件且具有执行权限", file=sys.stderr)
    else:
        print(f"找到 build_server.sh 脚本: {build_script_path}")
        wpsweb_dir = os.path.dirname(build_script_path)
        
        # 在 Docker 中执行 build_server.sh 脚本
        if not run_docker_command(f"./build_server.sh", wpsweb_dir):
            print("build_server.sh 执行失败", file=sys.stderr)
            sys.exit(1)
    
    print("\n=== 编译完成 ===")
    print("wpsmain 自动编译流程已完成")
    print("完成。") 
    