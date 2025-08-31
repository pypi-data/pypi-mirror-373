#!/usr/bin/env python3
"""
WSL 端口转发工具
"""

import os
import sys
import subprocess
import platform
from typing import Optional


def is_windows_system() -> bool:
    """检查是否为 Windows 系统"""
    return platform.system().lower() == "windows"


def is_admin() -> bool:
    """检查是否具有管理员权限"""
    try:
        if is_windows_system():
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        else:
            return os.geteuid() == 0
    except:
        return False


def run_as_admin() -> bool:
    """以管理员权限重新运行程序"""
    try:
        if not is_windows_system():
            return False
            
        import ctypes
        import sys
        
        # 获取当前脚本路径
        script_path = sys.argv[0]
        
        # 如果是从模块运行的，需要特殊处理
        if script_path.endswith('__main__.py'):
            # 使用 python -m ypp 的方式重新启动
            cmd = ['python', '-m', 'ypp'] + sys.argv[1:]
        else:
            cmd = [sys.executable, script_path] + sys.argv[1:]
        
        # 使用 ShellExecuteW 以管理员权限运行
        result = ctypes.windll.shell32.ShellExecuteW(
            None,  # hwnd
            "runas",  # operation (runas = 以管理员身份运行)
            cmd[0],  # file
            " ".join(cmd[1:]),  # parameters
            None,  # directory
            1  # show command (1 = SW_SHOWNORMAL)
        )
        
        if result > 32:  # 成功
            print("已请求管理员权限，请在弹出的 UAC 对话框中确认...")
            return True
        else:
            print(f"请求管理员权限失败，错误代码: {result}", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"自动提权失败: {e}", file=sys.stderr)
        return False


def get_wsl_ip() -> Optional[str]:
    """获取 WSL 的 IP 地址"""
    try:
        # 使用 wsl hostname -I 获取 WSL IP
        result = subprocess.run(
            ["wsl", "hostname", "-I"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        # 取第一个 IP 地址
        ip = result.stdout.strip().split()[0]
        return ip
    except subprocess.CalledProcessError:
        print("错误: 无法获取 WSL IP 地址", file=sys.stderr)
        return None
    except FileNotFoundError:
        print("错误: 找不到 wsl 命令，请确保已安装 WSL", file=sys.stderr)
        return None


def add_port_forward(host_port: int, wsl_port: int) -> bool:
    """添加端口转发规则"""
    try:
        wsl_ip = get_wsl_ip()
        if not wsl_ip:
            return False
        
        # 使用 netsh 添加端口转发规则
        cmd = [
            "netsh", "interface", "portproxy", "add", "v4tov4",
            f"listenport={host_port}",
            f"listenaddress=0.0.0.0",
            f"connectport={wsl_port}",
            f"connectaddress={wsl_ip}"
        ]
        
        print(f"添加端口转发: 本机 {host_port} -> WSL {wsl_ip}:{wsl_port}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            print(f"✓ 端口转发规则添加成功")
            return True
        else:
            print(f"✗ 端口转发规则添加失败: {result.stderr}", file=sys.stderr)
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"✗ 添加端口转发失败: {e.stderr}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"✗ 添加端口转发时发生错误: {e}", file=sys.stderr)
        return False


def remove_port_forward(host_port: int) -> bool:
    """移除端口转发规则"""
    try:
        cmd = [
            "netsh", "interface", "portproxy", "delete", "v4tov4",
            f"listenport={host_port}",
            f"listenaddress=0.0.0.0"
        ]
        
        print(f"移除端口转发: 本机 {host_port}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            print(f"✓ 端口转发规则移除成功")
            return True
        else:
            print(f"✗ 端口转发规则移除失败: {result.stderr}", file=sys.stderr)
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"✗ 移除端口转发失败: {e.stderr}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"✗ 移除端口转发时发生错误: {e}", file=sys.stderr)
        return False


def list_port_forwards() -> bool:
    """列出所有端口转发规则"""
    try:
        cmd = ["netsh", "interface", "portproxy", "show", "v4tov4"]
        
        print("当前端口转发规则:")
        print("=" * 60)
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        if result.stdout.strip():
            print(result.stdout)
        else:
            print("暂无端口转发规则")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ 获取端口转发规则失败: {e.stderr}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"✗ 获取端口转发规则时发生错误: {e}", file=sys.stderr)
        return False


def command_wsl_port(host_port: Optional[int] = None, wsl_port: Optional[int] = None, action: str = "add") -> None:
    """
    执行 WSL 端口转发命令
    
    Args:
        host_port: 本机端口
        wsl_port: WSL 端口
        action: 操作类型 (add/remove/list)
    """
    # 检查系统
    if not is_windows_system():
        print("错误: 此命令仅在 Windows 系统上支持", file=sys.stderr)
        sys.exit(1)
    
    try:
        if action == "list":
            # 列出所有端口转发规则
            if not list_port_forwards():
                sys.exit(1)
                
        elif action == "add":
            # 添加端口转发规则需要管理员权限
            if not is_admin():
                print("需要管理员权限来添加端口转发规则...")
                if not run_as_admin():
                    print("错误: 无法获取管理员权限", file=sys.stderr)
                    sys.exit(1)
                return  # 重新启动后会自动继续执行
            
            if host_port is None or wsl_port is None:
                print("错误: 添加端口转发需要指定本机端口和 WSL 端口", file=sys.stderr)
                print("用法: ypp wsl port <本机端口> <WSL端口>", file=sys.stderr)
                sys.exit(1)
            
            if not add_port_forward(host_port, wsl_port):
                sys.exit(1)
                
        elif action == "remove":
            # 移除端口转发规则需要管理员权限
            if not is_admin():
                print("需要管理员权限来移除端口转发规则...")
                if not run_as_admin():
                    print("错误: 无法获取管理员权限", file=sys.stderr)
                    sys.exit(1)
                return  # 重新启动后会自动继续执行
            
            if host_port is None:
                print("错误: 移除端口转发需要指定本机端口", file=sys.stderr)
                print("用法: ypp wsl port remove <本机端口>", file=sys.stderr)
                sys.exit(1)
            
            if not remove_port_forward(host_port):
                sys.exit(1)
        
    except Exception as e:
        print(f"执行端口转发命令时发生错误: {e}", file=sys.stderr)
        sys.exit(1)
