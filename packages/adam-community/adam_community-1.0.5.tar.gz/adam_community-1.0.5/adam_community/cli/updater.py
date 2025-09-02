import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple
import requests
from packaging import version
import click
from rich.console import Console
from rich.panel import Panel

console = Console()

def get_cache_dir() -> Path:
    """获取缓存目录"""
    cache_dir = Path.home() / ".adam_cli" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir

def get_current_version() -> str:
    """获取当前版本"""
    try:
        # 尝试从 setup.py 或 __version__ 获取版本
        from adam_community import __version__
        return __version__
    except ImportError:
        # 如果无法导入，尝试从 pip 获取
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", "adam-community"], 
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        return line.split(':', 1)[1].strip()
        except:
            pass
        return "unknown"

def get_latest_version_from_pypi() -> Optional[str]:
    """从 PyPI 获取最新版本"""
    try:
        response = requests.get(
            "https://pypi.org/pypi/adam-community/json", 
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return data['info']['version']
    except:
        pass
    return None

def should_check_update() -> bool:
    """检查是否需要检查更新（基于缓存时间）"""
    cache_file = get_cache_dir() / "last_update_check.json"
    
    if not cache_file.exists():
        return True
    
    try:
        with open(cache_file, 'r') as f:
            data = json.load(f)
        
        last_check = datetime.fromisoformat(data['last_check'])
        # 24小时检查一次
        return datetime.now() - last_check > timedelta(hours=24)
    except:
        return True

def save_check_time():
    """保存检查时间"""
    cache_file = get_cache_dir() / "last_update_check.json"
    
    try:
        with open(cache_file, 'w') as f:
            json.dump({
                'last_check': datetime.now().isoformat()
            }, f)
    except:
        pass

def is_update_disabled() -> bool:
    """检查是否禁用了自动更新检查"""
    config_file = get_cache_dir() / "config.json"
    
    if not config_file.exists():
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config.get('disable_update_check', False)
    except:
        return False

def set_update_disabled(disabled: bool):
    """设置是否禁用自动更新检查"""
    config_file = get_cache_dir() / "config.json"
    
    try:
        config = {}
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
        
        config['disable_update_check'] = disabled
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    except:
        pass

def check_for_update() -> Tuple[bool, Optional[str], Optional[str]]:
    """检查更新，返回(有更新, 当前版本, 最新版本)"""
    if is_update_disabled():
        return False, None, None
    
    if not should_check_update():
        return False, None, None
    
    current_ver = get_current_version()
    latest_ver = get_latest_version_from_pypi()
    
    save_check_time()
    
    if current_ver == "unknown" or latest_ver is None:
        return False, current_ver, latest_ver
    
    try:
        has_update = version.parse(latest_ver) > version.parse(current_ver)
        return has_update, current_ver, latest_ver
    except:
        return False, current_ver, latest_ver

def show_update_notification(current_ver: str, latest_ver: str):
    """显示更新通知"""
    console.print()
    console.print(Panel.fit(
        f"[yellow]📦 发现新版本！[/yellow]\n"
        f"当前版本: [red]{current_ver}[/red]\n"
        f"最新版本: [green]{latest_ver}[/green]\n\n"
        f"[dim]运行以下命令更新：[/dim]\n"
        f"[cyan]adam-cli update[/cyan]\n\n"
        f"[dim]或运行以下命令禁用更新检查：[/dim]\n"
        f"[cyan]adam-cli config --disable-update-check[/cyan]",
        border_style="yellow",
        title="[yellow]🚀 更新提醒[/yellow]"
    ))
    console.print()

def update_cli():
    """更新 CLI 到最新版本"""
    console.print("🔍 检查最新版本...")
    
    latest_ver = get_latest_version_from_pypi()
    if latest_ver is None:
        console.print("[red]❌ 无法获取最新版本信息，请检查网络连接[/red]")
        return False
    
    current_ver = get_current_version()
    
    if current_ver != "unknown":
        try:
            if version.parse(current_ver) >= version.parse(latest_ver):
                console.print(f"[green]✅ 已是最新版本 {current_ver}[/green]")
                return True
        except:
            pass
    
    console.print(f"📦 开始更新到版本 {latest_ver}...")
    
    try:
        # 使用 pip 更新
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", "adam-community"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print(f"[green]✅ 更新成功！[/green]")
            console.print(f"[green]当前版本: {latest_ver}[/green]")
            return True
        else:
            console.print(f"[red]❌ 更新失败：[/red]")
            console.print(f"[red]{result.stderr}[/red]")
            return False
    except Exception as e:
        console.print(f"[red]❌ 更新过程中出错：{str(e)}[/red]")
        return False

def check_and_notify_update():
    """检查并通知更新（在 CLI 启动时调用）"""
    try:
        has_update, current_ver, latest_ver = check_for_update()
        if has_update and current_ver and latest_ver:
            show_update_notification(current_ver, latest_ver)
    except:
        # 静默处理错误，不影响正常功能
        pass