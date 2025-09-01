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


def run_command_as_admin(command: list) -> bool:
    """以管理员权限执行命令"""
    try:
        if not is_windows_system():
            return False
            
        import ctypes
        import subprocess
        
        # 构建完整的命令
        if command[0] == 'netsh':
            # 对于 netsh 命令，直接使用 runas
            full_cmd = ['runas', '/user:Administrator'] + command
        else:
            # 其他命令使用 PowerShell 以管理员权限执行
            ps_cmd = f'Start-Process -FilePath "{command[0]}" -ArgumentList {command[1:]} -Verb RunAs -Wait'
            full_cmd = ['powershell', '-Command', ps_cmd]
        
        # 执行命令
        result = subprocess.run(full_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True
        else:
            print(f"命令执行失败: {result.stderr}", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"以管理员权限执行命令失败: {e}", file=sys.stderr)
        return False


def run_netsh_as_admin(command: list) -> bool:
    """以管理员权限执行 netsh 命令"""
    try:
        if not is_windows_system():
            return False
            
        import subprocess
        
        # 使用 PowerShell 以管理员权限执行 netsh 命令
        # 移除第一个 "netsh" 参数，因为 -FilePath 已经指定了程序
        netsh_args = command[1:] if command[0] == "netsh" else command
        # 构建参数列表字符串
        args_str = ",".join([f'"{arg}"' for arg in netsh_args])
        ps_cmd = f'Start-Process -FilePath "netsh" -ArgumentList {args_str} -Verb RunAs -Wait'
        
        result = subprocess.run(['powershell', '-Command', ps_cmd], capture_output=True, text=True)
        
        if result.returncode == 0:
            return True
        else:
            print(f"netsh 命令执行失败: {result.stderr}", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"以管理员权限执行 netsh 命令失败: {e}", file=sys.stderr)
        return False


def get_wsl_ip() -> Optional[str]:
    """获取 WSL 的 IP 地址"""
    try:
        # 使用 wsl hostname -I 获取 WSL IP
        result = subprocess.run(
            ["wsl", "hostname", "-I"], 
            capture_output=True, 
            text=True, 
            encoding='utf-8',
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
        
        # 尝试直接执行，如果失败则使用管理员权限
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', check=True)
            if result.returncode == 0:
                print(f"✓ 端口转发规则添加成功")
                return True
        except subprocess.CalledProcessError:
            # 直接执行失败，尝试使用管理员权限
            print("需要管理员权限，正在请求...")
            if run_netsh_as_admin(cmd):
                print(f"✓ 端口转发规则添加成功")
                return True
            else:
                print(f"✗ 添加端口转发失败", file=sys.stderr)
                return False
        
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
        
        # 尝试直接执行，如果失败则使用管理员权限
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', check=True)
            if result.returncode == 0:
                print(f"✓ 端口转发规则移除成功")
                return True
        except subprocess.CalledProcessError:
            # 直接执行失败，尝试使用管理员权限
            print("需要管理员权限，正在请求...")
            if run_netsh_as_admin(cmd):
                print(f"✓ 端口转发规则移除成功")
                return True
            else:
                print(f"✗ 移除端口转发失败", file=sys.stderr)
                return False
        
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
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', check=True)
        
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
            # 添加端口转发规则
            if host_port is None or wsl_port is None:
                print("错误: 添加端口转发需要指定本机端口和 WSL 端口", file=sys.stderr)
                print("用法: ypp wsl port <本机端口> <WSL端口>", file=sys.stderr)
                sys.exit(1)
            
            if not add_port_forward(host_port, wsl_port):
                sys.exit(1)
                
        elif action == "remove":
            # 移除端口转发规则
            if host_port is None:
                print("错误: 移除端口转发需要指定本机端口", file=sys.stderr)
                print("用法: ypp wsl port remove <本机端口>", file=sys.stderr)
                sys.exit(1)
            
            if not remove_port_forward(host_port):
                sys.exit(1)
        
    except Exception as e:
        print(f"执行端口转发命令时发生错误: {e}", file=sys.stderr)
        sys.exit(1)
