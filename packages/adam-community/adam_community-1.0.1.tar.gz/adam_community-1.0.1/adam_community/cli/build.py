import json
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
    functions = parse_directory(directory)
    
    tree.add(f"找到 {len(functions)} 个类定义")
    for func in functions:
        func_info = func["function"]
        
        # 检查描述长度
        description = func_info.get("description")
        if description is None or not description:
            warning_msg = f"⚠️ {func_info['file']}: {func_info['name']} 没有描述"
            tree.add(warning_msg)
            warnings.append(warning_msg)
        elif len(description) > 1024:
            error_msg = f"❌ {func_info['file']}: {func_info['name']} 描述长度超过1024字符 ({len(description)})"
            tree.add(error_msg)
            errors.append(error_msg)
        else:
            tree.add(f"✓ {func_info['file']}: {func_info['name']} 描述长度: {len(description)}")

        # 检查参数定义
        if not func_info["parameters"]["properties"]:
            warning_msg = f"⚠️ {func_info['file']}: {func_info['name']} 没有参数定义"
            tree.add(warning_msg)
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
                    error_msg = f"❌ {func_info['file']}: {func_info['name']} - {param_error}"
                    tree.add(error_msg)
                    errors.append(error_msg)
            else:
                tree.add(f"✓ {func_info['file']}: {func_info['name']} 参数类型验证通过")
    
    if errors:
        tree.add("❌ 检查未通过")
    else:
        tree.add("✅ 检查通过")
    
    # 显示警告信息
    if warnings:
        tree.add(f"⚠️ 发现 {len(warnings)} 个警告（不影响构建）")
    
    console.print(tree)
    return len(errors) == 0, errors

def check_configuration(directory: Path) -> Tuple[bool, List[str]]:
    """检查 configure.json 文件"""
    tree = Tree("📄 配置文件检查")
    errors = []
    config_path = directory / "config" / "configure.json"
    
    if not config_path.exists():
        tree.add("❌ 未找到 configure.json 文件")
        console.print(tree)
        return False, ["configure.json 文件不存在"]
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        required_fields = ["name", "version", "display_name"]
        for field in required_fields:
            if field not in config:
                errors.append(f"configure.json 缺少必要字段: {field}")
                tree.add(f"❌ 缺少字段: {field}")
            else:
                tree.add(f"✓ {field}: {config[field]}")
        
        if errors:
            tree.add("❌ 检查未通过")
        else:
            tree.add("✅ 检查通过")
        
        console.print(tree)
        return len(errors) == 0, errors
    except json.JSONDecodeError:
        tree.add("❌ 配置文件格式错误")
        console.print(tree)
        return False, ["configure.json 文件格式错误"]

def check_markdown_files(directory: Path) -> Tuple[bool, List[str]]:
    """检查必要的 Markdown 文件"""
    tree = Tree("📑 Markdown 文件检查")
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
    
    tree.add(f"检查类型: {config_type}")
    
    for file in required_files:
        file_path = directory / "config" / file
        if not file_path.exists():
            errors.append(f"缺少必要文件: {file}")
            tree.add(f"❌ {file}")
        else:
            # 对于 input.json，额外检查 JSON 格式
            if file == "input.json":
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json.load(f)
                    tree.add(f"✓ {file} (JSON 格式正确)")
                except json.JSONDecodeError:
                    errors.append(f"{file} JSON 格式错误")
                    tree.add(f"❌ {file} (JSON 格式错误)")
            else:
                tree.add(f"✓ {file}")
    
    if errors:
        tree.add("❌ 检查未通过")
    else:
        tree.add("✅ 检查通过")
    
    console.print(tree)
    return len(errors) == 0, errors

def create_zip_package(directory: Path) -> str:
    """创建 zip 包"""
    tree = Tree("📦 创建压缩包")
    with open(directory / "config" / "configure.json", 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    zip_name = f"{config['name']}_{config['version']}.zip"
    zip_path = directory / zip_name
    
    tree.add(f"包名: {zip_name}")
    
    # 获取配置类型
    config_type = config.get("type", "agent")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 添加所有 Python 文件
        py_files = list(directory.rglob('*.py'))
        py_tree = tree.add("Python 文件")
        for py_file in py_files:
            if not py_file.name.startswith('_'):
                zipf.write(py_file, py_file.relative_to(directory))
                py_tree.add(f"+ {py_file.relative_to(directory)}")
        
        # 添加配置文件
        config_tree = tree.add("配置文件")
        zipf.write(directory / "config" / "configure.json", "config/configure.json")
        config_tree.add("+ config/configure.json")
        
        # 添加 demos 目录
        demos_tree = tree.add("Demos 文件")
        demos_dir = directory / "demos"
        if demos_dir.exists() and demos_dir.is_dir():
            for demos_file in demos_dir.rglob('*'):
                if demos_file.is_file():
                    zipf.write(demos_file, demos_file.relative_to(directory))
                    demos_tree.add(f"+ {demos_file.relative_to(directory)}")
        
        # 根据类型添加不同的文件
        md_tree = tree.add("其他文件")
        if config_type == "kit":
            # kit 类型需要添加的文件
            other_files = ["long_description.md", "input.json"]
        else:
            # agent 类型需要添加的文件
            other_files = ["initial_assistant_message.md", "initial_system_prompt.md", "long_description.md"]
        
        for file in other_files:
            file_path = directory / "config" / file
            if file_path.exists():
                zipf.write(file_path, f"config/{file}")
                md_tree.add(f"+ config/{file}")
    
    tree.add("✅ 压缩包创建完成")
    console.print(tree)
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
    
    # 2. 检查配置文件
    config_passed, config_errors = check_configuration(directory)
    if not config_passed:
        all_passed = False
        all_errors.extend(config_errors)
    
    # 3. 检查 Markdown 文件
    md_passed, md_errors = check_markdown_files(directory)
    if not md_passed:
        all_passed = False
        all_errors.extend(md_errors)
    
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
            "[bold red]❌ 构建失败！[/bold red]\n" + "\n".join(all_errors),
            border_style="red"
        ))
    
    return all_passed, all_errors, zip_name 