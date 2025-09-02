import click
import json
from pathlib import Path
from .parser import parse_directory
from .build import build_package
from .init import init

@click.group()
def cli():
    """Adam Community CLI 工具"""
    pass

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

# 添加 init 命令
cli.add_command(init)

if __name__ == '__main__':
    cli()
