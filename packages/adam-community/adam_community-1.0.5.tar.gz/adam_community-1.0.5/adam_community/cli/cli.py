import click
import json
from pathlib import Path
from .parser import parse_directory
from .build import build_package
from .init import init
from .updater import check_and_notify_update, update_cli, set_update_disabled
from ..__version__ import __version__

@click.group()
@click.version_option(version=__version__, prog_name='adam-cli')
def cli():
    """Adam Community CLI 工具"""
    # 检查更新（静默执行，不影响正常功能）
    check_and_notify_update()

@cli.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, dir_okay=True), default='.')
def parse(directory):
    """解析指定目录下的所有 Python 文件并生成 functions.json"""
    directory_path = Path(directory)
    all_functions = parse_directory(directory_path)
    
    # 将结果写入 functions.json
    output_file = directory_path / 'functions.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_functions, f, indent=2, ensure_ascii=False)
    
    click.echo(f"已成功解析 {len(all_functions)} 个类，结果保存在 {output_file}")

@cli.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, dir_okay=True), default='.')
def build(directory):
    """构建项目包"""
    directory_path = Path(directory)
    
    # 执行构建
    success, errors, zip_name = build_package(directory_path)
    
    if success:
        click.echo(f"包创建成功: {zip_name}")
    else:
        click.echo("检查未通过，发现以下问题：")
        for error in errors:
            click.echo(f"- {error}")
        raise click.Abort()

@cli.command()
def update():
    """更新 CLI 到最新版本"""
    if update_cli():
        click.echo("\n🎉 更新完成！重新运行命令以使用新版本。")
    else:
        click.echo("\n❌ 更新失败，请手动更新或检查网络连接。")
        click.echo("手动更新命令：pip install --upgrade adam-community")

@cli.command()
@click.option('--disable-update-check', is_flag=True, help='禁用自动更新检查')
@click.option('--enable-update-check', is_flag=True, help='启用自动更新检查')
def config(disable_update_check, enable_update_check):
    """配置 CLI 设置"""
    if disable_update_check and enable_update_check:
        click.echo("错误：不能同时启用和禁用更新检查")
        return
    
    if disable_update_check:
        set_update_disabled(True)
        click.echo("✅ 已禁用自动更新检查")
    elif enable_update_check:
        set_update_disabled(False) 
        click.echo("✅ 已启用自动更新检查")
    else:
        click.echo("请使用 --disable-update-check 或 --enable-update-check 选项")

# 添加 init 命令
cli.add_command(init)

if __name__ == '__main__':
    cli()
