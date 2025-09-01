#!/usr/bin/env python3
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys

try:
    from .makefile_modifier import command_modify_makefile
    from .auto_build import command_auto_build
    from .init_commands import init_wpsmain, init_wpsweb
    from .vscode_config import command_code_webwps
    from .ppt_attributes import command_pptattr
    from .wsl_port_forward import command_wsl_port
    from .common import (
        run_command, ensure_directory, path_exists_and_not_empty,
        get_config_path, load_config, save_config, get_workspace_dir
    )
except ImportError:
    from makefile_modifier import command_modify_makefile
    from auto_build import command_auto_build
    from init_commands import init_wpsmain, init_wpsweb
    from vscode_config import command_code_webwps
    from ppt_attributes import command_pptattr
    from wsl_port_forward import command_wsl_port
    from common import (
        run_command, ensure_directory, path_exists_and_not_empty,
        get_config_path, load_config, save_config, get_workspace_dir
    )





def is_linux_system() -> bool:
    """检查是否为 Linux 系统"""
    return platform.system().lower() == "linux"


def ng_sync(master_repo_path: str) -> None:
    if shutil.which("krepo-ng") is None:
        print("找不到 krepo-ng 命令，请先安装或配置 PATH。", file=sys.stderr)
        sys.exit(2)
    print(f"[krepo-ng] 同步仓库: {master_repo_path}")
    rc = run_command(["krepo-ng", "sync"], cwd_path=master_repo_path)
    if rc != 0:
        print("krepo-ng sync 失败", file=sys.stderr)
        sys.exit(rc)


def ng_worktree_add(master_repo_path: str, target_path: str, branch: str) -> None:
    if shutil.which("krepo-ng") is None:
        print("找不到 krepo-ng 命令，请先安装或配置 PATH。", file=sys.stderr)
        sys.exit(2)
    print(f"[krepo-ng] 创建 worktree -> {target_path} @ {branch}")
    rc = run_command(["krepo-ng", "worktree", "add", target_path, branch], cwd_path=master_repo_path)
    if rc != 0:
        sys.exit(rc)


def git_sync(master_repo_path: str) -> None:
    if shutil.which("git") is None:
        print("找不到 git 命令，请先安装或配置 PATH。", file=sys.stderr)
        sys.exit(2)
    print(f"[git] 同步仓库: {master_repo_path}")
    rc = run_command(["git", "pull"], cwd_path=master_repo_path)
    if rc != 0:
        print("git pull 失败", file=sys.stderr)
        sys.exit(rc)


def git_branch_exists(master_repo_path: str, branch: str) -> bool:
    has_local = run_command(["git", "show-ref", "--verify", f"refs/heads/{branch}"], cwd_path=master_repo_path) == 0
    return has_local


def git_worktree_add(master_repo_path: str, target_path: str, branch: str) -> None:
    if shutil.which("git") is None:
        print("找不到 git 命令，请先安装或配置 PATH。", file=sys.stderr)
        sys.exit(2)
    print(f"[git] 创建 worktree -> {target_path} @ {branch}")
    rc = run_command(["git", "worktree", "add", target_path, branch], cwd_path=master_repo_path)
    if rc != 0:
        sys.exit(rc)


def git_worktree_list(master_repo_path: str) -> None:
    if shutil.which("git") is None:
        print("找不到 git 命令，请先安装或配置 PATH。", file=sys.stderr)
        sys.exit(2)
    print(f"[git] worktree list @ {master_repo_path}")
    rc = run_command(["git", "worktree", "list"], cwd_path=master_repo_path)
    if rc != 0:
        sys.exit(rc)


def ng_worktree_remove(master_repo_path: str, target_path: str) -> None:
    if shutil.which("krepo-ng") is None:
        print("找不到 krepo-ng 命令，请先安装或配置 PATH。", file=sys.stderr)
        sys.exit(2)
    print(f"[krepo-ng] 移除 worktree -> {target_path}")
    rc = run_command(["krepo-ng", "worktree", "remove", target_path], cwd_path=master_repo_path)
    if rc != 0:
        sys.exit(rc)


def git_worktree_remove(master_repo_path: str, target_path: str) -> None:
    if shutil.which("git") is None:
        print("找不到 git 命令，请先安装或配置 PATH。", file=sys.stderr)
        sys.exit(2)
    print(f"[git] 移除 worktree -> {target_path}")
    rc = run_command(["git", "worktree", "remove", target_path], cwd_path=master_repo_path)
    if rc != 0:
        sys.exit(rc)


def command_add(path_value: str, branch_value: str) -> None:
    home_dir = get_workspace_dir()
    # wpsmain via krepo-ng
    master_wpsmain_path = os.path.join(home_dir, "master", "wpsmain")
    if not os.path.isdir(master_wpsmain_path):
        print(f"未找到主仓库目录: {master_wpsmain_path}", file=sys.stderr)
        sys.exit(1)

    target_root = os.path.join(home_dir, path_value)
    target_wpsmain_path = os.path.join(target_root, "wpsmain")
    if not path_exists_and_not_empty(target_wpsmain_path):
        ensure_directory(target_wpsmain_path)
        ng_sync(master_wpsmain_path)
        ng_worktree_add(master_wpsmain_path, target_wpsmain_path, branch_value)

    # wpsweb via git
    master_wpsweb_path = os.path.join(home_dir, "master", "wpsweb")
    if not os.path.isdir(master_wpsweb_path):
        print(f"未找到主仓库目录: {master_wpsweb_path}", file=sys.stderr)
        sys.exit(1)

    target_wpsweb_path = os.path.join(target_root, "wpsweb")
    if not path_exists_and_not_empty(target_wpsweb_path):
        ensure_directory(target_wpsweb_path)
        git_sync(master_wpsweb_path)
        git_worktree_add(master_wpsweb_path, target_wpsweb_path, branch_value)

    print("完成。")


def command_list() -> None:
    home_dir = get_workspace_dir()
    master_wpsmain_path = os.path.join(home_dir, "master", "wpsmain")
    master_wpsweb_path = os.path.join(home_dir, "master", "wpsweb")

    if not os.path.isdir(master_wpsmain_path):
        print(f"未找到主仓库目录: {master_wpsmain_path}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isdir(master_wpsweb_path):
        print(f"未找到主仓库目录: {master_wpsweb_path}", file=sys.stderr)
        sys.exit(1)

    print("=== wpsmain worktrees ===")
    git_worktree_list(master_wpsmain_path)
    print("\n=== wpsweb worktrees ===")
    git_worktree_list(master_wpsweb_path)


def command_remove(path_value: str) -> None:
    home_dir = get_workspace_dir()
    
    # wpsmain via krepo-ng
    master_wpsmain_path = os.path.join(home_dir, "master", "wpsmain")
    if not os.path.isdir(master_wpsmain_path):
        print(f"未找到主仓库目录: {master_wpsmain_path}", file=sys.stderr)
        sys.exit(1)

    remove_wpsmain_path = os.path.join(path_value, "wpsmain")
    if os.path.exists(remove_wpsmain_path):
        ng_worktree_remove(master_wpsmain_path, remove_wpsmain_path)
    else:
        print(f"wpsmain worktree 不存在: {remove_wpsmain_path}")

    # wpsweb via git
    master_wpsweb_path = os.path.join(home_dir, "master", "wpsweb")
    if not os.path.isdir(master_wpsweb_path):
        print(f"未找到主仓库目录: {master_wpsweb_path}", file=sys.stderr)
        sys.exit(1)

    remove_wpsweb_path = os.path.join(path_value, "wpsweb")
    if os.path.exists(remove_wpsweb_path):
        git_worktree_remove(master_wpsweb_path, remove_wpsweb_path)
    else:
        print(f"wpsweb worktree 不存在: {remove_wpsweb_path}")

    # 删除整个路径目录
    if os.path.exists(path_value):
        try:
            shutil.rmtree(path_value)
            print(f"已删除目录: {path_value}")
        except OSError as e:
            print(f"删除目录失败: {path_value}, 错误: {e}", file=sys.stderr)
    else:
        print(f"目录不存在: {path_value}")
    
    print("完成。")


def command_set(key_value: str) -> None:
    """设置配置项。用法: set <key>=<value>"""
    # 解析 key=value 格式
    if '=' not in key_value:
        print("错误: 请使用 'key=value' 格式", file=sys.stderr)
        print("示例: ypp set work_dir=~/workspace", file=sys.stderr)
        sys.exit(1)
    
    parts = key_value.split('=', 1)
    if len(parts) != 2:
        print("错误: 请使用 'key=value' 格式", file=sys.stderr)
        sys.exit(1)
    
    key = parts[0].strip()
    value = parts[1].strip()
    
    if not key:
        print("错误: 配置项名称不能为空", file=sys.stderr)
        sys.exit(1)
    
    config = load_config()
    
    # 处理不同类型的配置项
    if key == 'work_dir':
        # 展开用户路径
        expanded_value = os.path.expanduser(value)
        if not os.path.isdir(expanded_value):
            print(f"错误: 指定的路径不存在: {expanded_value}", file=sys.stderr)
            sys.exit(1)
        
        config[key] = value  # 保存原始值（包含 ~）
        print(f"已设置 {key} 为: {value}")
    
    else:
        # 通用配置项
        config[key] = value
        print(f"已设置 {key} 为: {value}")
    
    save_config(config)
    print(f"配置文件位置: {get_config_path()}")


def command_show_config() -> None:
    """显示当前配置"""
    config = load_config()
    workspace_dir = get_workspace_dir()
    
    print("当前配置:")
    print(f"  Workspace 路径: {workspace_dir}")
    
    # 显示所有配置项
    if config:
        print("\n配置项详情:")
        for key, value in config.items():
            print(f"  {key}: {value}")
        print(f"\n配置文件: {get_config_path()}")
    else:
        print("  使用默认配置（未配置任何项）")
        print(f"  配置文件: {get_config_path()}")








def main() -> None:
    parser = argparse.ArgumentParser(description="多分支 worktree 管理工具（子命令版）")
    subparsers = parser.add_subparsers(dest="command", metavar="command")

    # add 子命令：添加 wpsmain 与 wpsweb 的 worktree
    add_parser = subparsers.add_parser("add", help="创建 worktree。用法: add <path> <branch>")
    add_parser.add_argument("path", help="目标路径名（对应 ~/<path>/...）")
    add_parser.add_argument("branch", help="要创建/切换的分支名")

    # list 子命令：列出 wpsmain 与 wpsweb 的 worktree
    subparsers.add_parser("list", help="列出 master 下 wpsmain 和 wpsweb 的 worktree")

    # remove 子命令：移除 wpsmain 与 wpsweb 的 worktree
    remove_parser = subparsers.add_parser("remove", help="移除 worktree。用法: remove <path>")
    remove_parser.add_argument("path", help="要移除的路径名（对应 ~/<path>/...）")

    # set 子命令：设置配置项
    set_parser = subparsers.add_parser("set", help="设置配置项。用法: set <key>=<value>")
    set_parser.add_argument("key_value", help="配置项，格式: key=value")

    # config 子命令：显示当前配置
    subparsers.add_parser("config", aliases=["cfg"], help="显示当前配置")

    # modify 子命令：修改 wpsweb/server/Makefile 修改 wpsweb/build_server.sh
    modify_parser = subparsers.add_parser("modify", aliases=["m"], help="修改 wpsweb/server/Makefile 和生成 build_server.sh（仅限 Linux） , 为Coding模式创建VSCode配置文件")
    modify_parser.add_argument("--force", action="store_true", help="强制在非 Linux 系统上运行（不推荐）")
    modify_parser.add_argument("mode", nargs="?", choices=["coding"], help="模式选择：coding模式创建VSCode配置文件")

    # build 子命令：自动编译 wpsmain
    subparsers.add_parser("build", help="自动编译 wpsmain（在 Docker 中执行）,并编译wpsweb")

    # code 子命令：创建VSCode配置文件
    code_parser = subparsers.add_parser("code", help="创建VSCode配置文件")
    code_parser.add_argument("type", choices=["wpsweb"], help="配置文件类型")

    # init 子命令：初始化仓库
    init_parser = subparsers.add_parser("init", help="初始化仓库。用法: init [type]")
    init_parser.add_argument("type", nargs="?", choices=["wpsmain", "wpsweb"], help="要初始化的仓库类型（可选，为空时依次执行 wpsmain 和 wpsweb）")

    # pptattr 子命令：读取 PPTX 文件属性
    pptattr_parser = subparsers.add_parser("pptattr", help="读取 PPTX 文件的自定义属性。用法: pptattr <filepath> [--clean]")
    pptattr_parser.add_argument("filepath", help="PPTX 文件路径")
    pptattr_parser.add_argument("--clean", action="store_true", help="清除指定属性（lastModifiedBy 和 ICV）并保存到原文件")

    # wsl 子命令：WSL 相关操作
    wsl_parser = subparsers.add_parser("wsl", help="WSL 相关操作")
    wsl_subparsers = wsl_parser.add_subparsers(dest="wsl_command", metavar="wsl_command")
    
    # wsl port 子命令：端口转发
    wsl_port_parser = wsl_subparsers.add_parser("port", help="WSL 端口转发管理")
    wsl_port_parser.add_argument("action", nargs="?", choices=["add", "remove", "list"], default="add", 
                                help="操作类型：add(添加), remove(移除), list(列出)")
    wsl_port_parser.add_argument("host_port", nargs="?", type=int, help="本机端口")
    wsl_port_parser.add_argument("wsl_port", nargs="?", type=int, help="WSL 端口")

    args = parser.parse_args()

    if args.command == "add":
        command_add(args.path, args.branch)
        return
    if args.command == "list":
        command_list()
        return
    if args.command == "remove":
        command_remove(args.path)
        return
    if args.command == "set":
        command_set(args.key_value)
        return
    if args.command == "config":
        command_show_config()
        return
    if args.command == "modify":
        if not is_linux_system() and not getattr(args, 'force', False):
            print("错误: modify 命令仅在 Linux 系统上支持", file=sys.stderr)
            print(f"当前系统: {platform.system()}", file=sys.stderr)
            print("提示: 可以使用 --force 参数强制运行（不推荐）", file=sys.stderr)
            sys.exit(1)
        if not is_linux_system() and getattr(args, 'force', False):
            print(f"警告: 在 {platform.system()} 系统上强制运行 modify 命令", file=sys.stderr)
        command_modify_makefile(mode=getattr(args, 'mode', None))
        return
    if args.command == "build":
        command_auto_build()
        return
    if args.command == "code":
        if args.type == "wpsweb":
            command_code_webwps()
        return
    if args.command == "init":
        if args.type == "wpsmain":
            init_wpsmain()
        elif args.type == "wpsweb":
            init_wpsweb()
        else:
            # 如果 type 为空，依次执行 wpsmain 和 wpsweb
            print("未指定仓库类型，将依次初始化 wpsmain 和 wpsweb...")
            init_wpsmain()
            init_wpsweb()
        return
    if args.command == "pptattr":
        command_pptattr(args.filepath, args.clean)
        return
    if args.command == "wsl":
        if hasattr(args, 'wsl_command') and args.wsl_command == "port":
            # 处理端口转发命令
            if args.action == "list":
                command_wsl_port(action="list")
            elif args.action == "remove":
                if args.host_port is None:
                    print("错误: 移除端口转发需要指定本机端口", file=sys.stderr)
                    print("用法: ypp wsl port remove <本机端口>", file=sys.stderr)
                    sys.exit(1)
                command_wsl_port(host_port=args.host_port, action="remove")
            else:  # add
                if args.host_port is None or args.wsl_port is None:
                    print("错误: 添加端口转发需要指定本机端口和 WSL 端口", file=sys.stderr)
                    print("用法: ypp wsl port <本机端口> <WSL端口>", file=sys.stderr)
                    sys.exit(1)
                command_wsl_port(host_port=args.host_port, wsl_port=args.wsl_port, action="add")
        else:
            wsl_parser.print_help()
        return

    parser.print_help()
    sys.exit(2)


if __name__ == "__main__":
    main()

