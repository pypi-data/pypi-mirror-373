import json
import sys
import zipfile
from pathlib import Path
from typing import Tuple, List
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
from .parser import parse_directory

console = Console()

def check_python_files(directory: Path) -> Tuple[bool, List[str]]:
    """检查所有 Python 文件是否都有参数定义"""
    tree = Tree("📦 Python 文件检查")
    errors = []
    warnings = []
    
    # 解析 Python 文件，如果出现错误则退出
    try:
        functions = parse_directory(directory)
    except Exception as e:
        console.print(Panel.fit(
            f"[bold red]❌ 解析 Python 文件时出错[/bold red]\n{str(e)}",
            border_style="red"
        ))
        console.print("[red]构建失败，请检查并修复上述错误后重试。[/red]")
        sys.exit(1)
    
    # 统计信息
    total_functions = len(functions)
    functions_with_desc = 0
    functions_with_params = 0
    
    for func in functions:
        func_info = func["function"]
        
        # 检查描述长度
        description = func_info.get("description")
        if description is None or not description:
            warning_msg = f"⚠️ {func_info['name']} 没有描述"
            warnings.append(warning_msg)
        elif len(description) > 1024:
            error_msg = f"❌ {func_info['name']} 描述长度超过1024字符 ({len(description)})"
            errors.append(error_msg)
        else:
            functions_with_desc += 1

        # 检查参数定义
        if not func_info["parameters"]["properties"]:
            warning_msg = f"⚠️ {func_info['name']} 没有参数定义"
            warnings.append(warning_msg)
        else:
            # 检查参数类型是否都是有效的JSON Schema类型
            param_errors = []
            for param_name, param_info in func_info["parameters"]["properties"].items():
                if "type" not in param_info:
                    param_errors.append(f"参数 '{param_name}' 缺少类型定义")
                elif param_info["type"] not in ["string", "integer", "number", "boolean", "array", "object", "null"]:
                    param_errors.append(f"参数 '{param_name}' 类型 '{param_info['type']}' 不是有效的JSON Schema类型")
            
            if param_errors:
                for param_error in param_errors:
                    error_msg = f"❌ {func_info['name']} - {param_error}"
                    errors.append(error_msg)
            else:
                functions_with_params += 1
    
    # 显示简化的统计信息
    console.print(f"📦 Python 文件检查: 找到 {total_functions} 个类定义")
    console.print(f"   ✓ 描述完整: {functions_with_desc}/{total_functions}")
    console.print(f"   ✓ 参数完整: {functions_with_params}/{total_functions}")
    
    # 显示错误和警告
    if errors:
        console.print(f"   ❌ {len(errors)} 个错误:")
        for error in errors[:5]:  # 只显示前5个错误
            console.print(f"      {error}")
        if len(errors) > 5:
            console.print(f"      ... 还有 {len(errors) - 5} 个错误")
    
    if warnings:
        console.print(f"   ⚠️ {len(warnings)} 个警告 (不影响构建)")
        if len(warnings) <= 3:
            for warning in warnings:
                console.print(f"      {warning}")
        else:
            console.print(f"      {warnings[0]}")
            console.print(f"      ... 还有 {len(warnings) - 1} 个警告")
    return len(errors) == 0, errors

def check_configuration(directory: Path) -> Tuple[bool, List[str]]:
    """检查 configure.json 文件"""
    errors = []
    config_path = directory / "config" / "configure.json"
    
    console.print("📄 配置文件检查:")
    
    if not config_path.exists():
        console.print("   ❌ 未找到 configure.json 文件")
        return False, ["configure.json 文件不存在"]
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        required_fields = ["name", "version", "display_name"]
        valid_fields = 0
        
        for field in required_fields:
            if field not in config:
                errors.append(f"configure.json 缺少必要字段: {field}")
            else:
                valid_fields += 1
        
        console.print(f"   ✓ 字段完整: {valid_fields}/{len(required_fields)}")
        
        if errors:
            console.print(f"   ❌ {len(errors)} 个错误:")
            for error in errors:
                console.print(f"      {error}")
        else:
            console.print(f"   ✓ 包信息: {config['name']} v{config['version']}")
        
        return len(errors) == 0, errors
    except json.JSONDecodeError:
        console.print("   ❌ 配置文件格式错误")
        return False, ["configure.json 文件格式错误"]

def check_markdown_files(directory: Path) -> Tuple[bool, List[str]]:
    """检查必要的 Markdown 文件"""
    errors = []
    
    # 先读取配置文件中的 type 字段
    config_path = directory / "config" / "configure.json"
    config_type = "agent"  # 默认值
    
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                config_type = config.get("type", "agent")
        except json.JSONDecodeError:
            pass  # 配置文件格式错误时使用默认值
    
    # 根据 type 设置不同的 required_files
    if config_type == "kit":
        required_files = [
            "configure.json", 
            "long_description.md",
            "input.json"
        ]
    else:  # type=agent 或空值
        required_files = [
            "initial_assistant_message.md",
            "initial_system_prompt.md", 
            "long_description.md"
        ]
    
    console.print(f"📑 文档文件检查 ({config_type} 类型):")
    
    valid_files = 0
    for file in required_files:
        file_path = directory / "config" / file
        if not file_path.exists():
            errors.append(f"缺少必要文件: {file}")
        else:
            # 对于 input.json，额外检查 JSON 格式
            if file == "input.json":
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json.load(f)
                    valid_files += 1
                except json.JSONDecodeError:
                    errors.append(f"{file} JSON 格式错误")
            else:
                valid_files += 1
    
    console.print(f"   ✓ 文件完整: {valid_files}/{len(required_files)}")
    
    if errors:
        console.print(f"   ❌ {len(errors)} 个错误:")
        for error in errors:
            console.print(f"      {error}")
    
    return len(errors) == 0, errors

def create_zip_package(directory: Path) -> str:
    """创建 zip 包"""
    with open(directory / "config" / "configure.json", 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    zip_name = f"{config['name']}_{config['version']}.zip"
    zip_path = directory / zip_name
    
    console.print("📦 创建压缩包:")
    console.print(f"   包名: {zip_name}")
    
    # 获取配置类型
    config_type = config.get("type", "agent")
    file_count = 0
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 添加所有 Python 文件
        py_files = [f for f in directory.rglob('*.py') if not f.name.startswith('_')]
        for py_file in py_files:
            zipf.write(py_file, py_file.relative_to(directory))
            file_count += 1
        
        # 添加配置文件
        zipf.write(directory / "config" / "configure.json", "config/configure.json")
        file_count += 1
        
        # 添加 demos 目录
        demos_dir = directory / "demos"
        demos_files = 0
        if demos_dir.exists() and demos_dir.is_dir():
            for demos_file in demos_dir.rglob('*'):
                if demos_file.is_file():
                    zipf.write(demos_file, demos_file.relative_to(directory))
                    file_count += 1
                    demos_files += 1
        
        # 根据类型添加不同的文件
        if config_type == "kit":
            other_files = ["long_description.md", "input.json"]
        else:
            other_files = ["initial_assistant_message.md", "initial_system_prompt.md", "long_description.md"]
        
        for file in other_files:
            file_path = directory / "config" / file
            if file_path.exists():
                zipf.write(file_path, f"config/{file}")
                file_count += 1
    
    console.print(f"   ✓ Python 文件: {len(py_files)} 个")
    console.print(f"   ✓ 配置文件: 1 个")
    if demos_files > 0:
        console.print(f"   ✓ 演示文件: {demos_files} 个")
    console.print(f"   ✓ 总计: {file_count} 个文件")
    
    return zip_name

def build_package(directory: Path) -> Tuple[bool, List[str], str]:
    """构建项目包
    
    Returns:
        Tuple[bool, List[str], str]: (是否成功, 错误信息列表, zip包名称)
    """
    console.print(Panel.fit(
        "[bold blue]🚀 开始构建项目包[/bold blue]",
        border_style="blue"
    ))
    
    all_passed = True
    all_errors = []
    
    # 1. 检查 Python 文件
    py_passed, py_errors = check_python_files(directory)
    if not py_passed:
        all_passed = False
        all_errors.extend(py_errors)
    console.print()  # 添加空行
    
    # 2. 检查配置文件
    config_passed, config_errors = check_configuration(directory)
    if not config_passed:
        all_passed = False
        all_errors.extend(config_errors)
    console.print()  # 添加空行
    
    # 3. 检查 Markdown 文件
    md_passed, md_errors = check_markdown_files(directory)
    if not md_passed:
        all_passed = False
        all_errors.extend(md_errors)
    console.print()  # 添加空行
    
    # 如果所有检查都通过，创建 zip 包
    zip_name = ""
    if all_passed:
        zip_name = create_zip_package(directory)
    
    if all_passed:
        console.print(Panel.fit(
            f"[bold green]✅ 构建成功！[/bold green]\n"
            f"压缩包: {zip_name}",
            border_style="green"
        ))
    else:
        console.print(Panel.fit(
            f"[bold red]❌ 构建失败！[/bold red]\n"
            f"共发现 {len(all_errors)} 个错误，请修复后重试。",
            border_style="red"
        ))
    
    return all_passed, all_errors, zip_name 