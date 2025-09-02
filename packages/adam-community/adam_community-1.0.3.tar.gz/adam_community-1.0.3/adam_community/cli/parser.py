import ast
from pathlib import Path
from typing import List, Dict, Any
from docstring_parser import parse as dsp
import jsonschema

def convert_python_type_to_json_schema(python_type: str) -> Dict[str, Any]:
    """将 Python 类型转换为 JSON Schema 类型
    
    Args:
        python_type: Python 类型字符串
        
    Returns:
        Dict[str, Any]: JSON Schema 类型定义
        
    Raises:
        ValueError: 当无法转换类型或生成的 schema 不符合规范时抛出异常
    """
    python_type = python_type.lower().strip()
    
    # 基本类型映射
    basic_types = {
        'str': 'string',
        'string': 'string',
        'int': 'integer',
        'integer': 'integer',
        'float': 'number',
        'number': 'number',
        'bool': 'boolean',
        'boolean': 'boolean',
        'list': 'array',
        'array': 'array',
        'dict': 'object',
        'object': 'object',
        'tuple': 'array',
        'set': 'array',
        'none': 'null',
        'null': 'null',
        'any': 'object'  # 添加对 any 类型的支持
    }
    
    # 处理基本类型
    if python_type in basic_types:
        schema_type = basic_types[python_type]
        if schema_type == "array":
            # 对于没有指定元素类型的数组，应该报错要求明确指定
            raise ValueError(f"数组类型 '{python_type}' 缺少元素类型定义，请使用 List[ElementType] 格式明确指定元素类型")
        else:
            schema = {"type": schema_type}
        return _create_and_validate_schema(schema, python_type)
    
    # 处理 Literal[T1, T2, ...] 格式
    if python_type.startswith('literal[') and python_type.endswith(']'):
        content = python_type[8:-1]  # 提取 Literal[ 和 ] 之间的内容
        values = [v.strip().strip('"\'') for v in content.split(',')]
        
        # 尝试推断类型
        if all(v.isdigit() or (v.startswith('-') and v[1:].isdigit()) for v in values):
            # 所有值都是整数
            return _create_and_validate_schema({
                "type": "integer",
                "enum": [int(v) for v in values]
            }, python_type)
        elif all(v.replace('.', '').replace('-', '').isdigit() for v in values):
            # 所有值都是数字
            return _create_and_validate_schema({
                "type": "number",
                "enum": [float(v) for v in values]
            }, python_type)
        else:
            # 字符串类型
            return _create_and_validate_schema({
                "type": "string",
                "enum": values
            }, python_type)
    
    # 处理 Union[T1, T2, ...] 或 T1 | T2 格式
    if python_type.startswith('union[') and python_type.endswith(']'):
        content = python_type[6:-1]
        types = [t.strip() for t in content.split(',')]
        return convert_union_types(types)
    
    # 处理 T1 | T2 格式（Python 3.10+ 的联合类型语法）
    if '|' in python_type and not python_type.startswith('literal['):
        types = [t.strip() for t in python_type.split('|')]
        return convert_union_types(types)
    
    # 处理 Optional[T] 格式
    if python_type.startswith('optional[') and python_type.endswith(']'):
        inner_type = python_type[9:-1].strip()
        try:
            inner_schema = convert_python_type_to_json_schema(inner_type)
            return _create_and_validate_schema({
                "oneOf": [
                    inner_schema,
                    {"type": "null"}
                ]
            }, python_type)
        except ValueError as e:
            raise ValueError(f"无法转换Optional类型 '{python_type}': {str(e)}")
    
    # 处理 List[T] 格式
    if python_type.startswith('list[') and python_type.endswith(']'):
        inner_type = python_type[5:-1]  # 提取 List[ 和 ] 之间的内容
        try:
            items_schema = convert_python_type_to_json_schema(inner_type)
            return _create_and_validate_schema({
                "type": "array",
                "items": items_schema
            }, python_type)
        except ValueError as e:
            raise ValueError(f"无法转换列表元素类型 '{inner_type}': {str(e)}")
    
    # 处理 List[T] 格式（大写）
    if python_type.startswith('list[') and python_type.endswith(']'):
        inner_type = python_type[5:-1]
        try:
            items_schema = convert_python_type_to_json_schema(inner_type)
            return _create_and_validate_schema({
                "type": "array",
                "items": items_schema
            }, python_type)
        except ValueError as e:
            raise ValueError(f"无法转换列表元素类型 '{inner_type}': {str(e)}")
    
    # 处理 Dict[K, V] 格式
    if python_type.startswith('dict[') and python_type.endswith(']'):
        # 提取键值类型
        content = python_type[5:-1]
        if ',' in content:
            key_type, value_type = content.split(',', 1)
            key_type = key_type.strip()
            value_type = value_type.strip()
            
            try:
                key_schema = convert_python_type_to_json_schema(key_type)
                value_schema = convert_python_type_to_json_schema(value_type)
                return _create_and_validate_schema({
                    "type": "object",
                    "additionalProperties": value_schema
                }, python_type)
            except ValueError as e:
                raise ValueError(f"无法转换字典类型 '{python_type}': {str(e)}")
        else:
            # 只有值类型的情况
            try:
                value_schema = convert_python_type_to_json_schema(content.strip())
                return _create_and_validate_schema({
                    "type": "object",
                    "additionalProperties": value_schema
                }, python_type)
            except ValueError as e:
                raise ValueError(f"无法转换字典值类型 '{content}': {str(e)}")
    
    # 处理枚举类型
    if python_type == 'enum':
        return _create_and_validate_schema({"type": "string"}, python_type)
    
    # 如果无法识别，返回基本的 object 类型
    schema = {"type": "object"}
    
    # 验证生成的 schema
    try:
        validate_json_schema(schema)
        return schema
    except ValueError as e:
        raise ValueError(f"生成的 JSON Schema 不符合规范 (类型: '{python_type}'): {str(e)}")
    
def _create_and_validate_schema(schema: Dict[str, Any], python_type: str) -> Dict[str, Any]:
    """创建并验证 JSON Schema
    
    Args:
        schema: 要验证的 schema
        python_type: 原始 Python 类型（用于错误信息）
        
    Returns:
        Dict[str, Any]: 验证通过的 schema
        
    Raises:
        ValueError: 当 schema 不符合规范时抛出异常
    """
    try:
        validate_json_schema(schema)
        return schema
    except ValueError as e:
        raise ValueError(f"生成的 JSON Schema 不符合规范 (类型: '{python_type}'): {str(e)}")

def validate_json_schema(schema: Dict[str, Any], context: str = "") -> None:
    """验证生成的 JSON Schema 是否符合规范
    
    Args:
        schema: 要验证的 JSON Schema
        context: 上下文信息，用于错误报告
        
    Raises:
        ValueError: 当 schema 不符合规范时抛出异常
    """
    try:
        # 使用 JSON Schema Draft 7 验证器
        jsonschema.Draft7Validator.check_schema(schema)
        
        # 额外的自定义验证
        if schema.get("type") == "array" and "items" not in schema:
            raise ValueError(f"array schema missing items{f' in {context}' if context else ''}")
            
        if schema.get("type") == "object":
            if "properties" in schema:
                for prop_name, prop_schema in schema["properties"].items():
                    validate_json_schema(prop_schema, f"{context}.{prop_name}" if context else prop_name)
            if "additionalProperties" in schema and isinstance(schema["additionalProperties"], dict):
                validate_json_schema(schema["additionalProperties"], f"{context}.additionalProperties" if context else "additionalProperties")
                
        if "oneOf" in schema:
            for i, sub_schema in enumerate(schema["oneOf"]):
                validate_json_schema(sub_schema, f"{context}.oneOf[{i}]" if context else f"oneOf[{i}]")
                
        if "items" in schema:
            validate_json_schema(schema["items"], f"{context}.items" if context else "items")
            
    except jsonschema.SchemaError as e:
        raise ValueError(f"Invalid JSON Schema{f' in {context}' if context else ''}: {str(e)}")

def convert_union_types(types: List[str]) -> Dict[str, Any]:
    """转换联合类型为 JSON Schema
    
    Args:
        types: 类型列表
        
    Returns:
        Dict[str, Any]: JSON Schema 联合类型定义
    """
    schemas = []
    for t in types:
        try:
            if t.lower() == 'none':
                schemas.append({"type": "null"})
            else:
                schemas.append(convert_python_type_to_json_schema(t))
        except ValueError as e:
            raise ValueError(f"无法转换联合类型中的类型 '{t}': {str(e)}")
    
    if len(schemas) == 1:
        return schemas[0]
    else:
        result_schema = {"oneOf": schemas}
        validate_json_schema(result_schema)
        return result_schema

def validate_description_length(description: str, function_name: str, file_path: str) -> None:
    """验证函数描述长度
    
    Args:
        description: 函数描述
        function_name: 函数名称
        file_path: 文件路径
        
    Raises:
        ValueError: 当描述长度超过1024字符时抛出异常
    """
    if len(description) > 1024:
        raise ValueError(
            f"函数 '{function_name}' 在文件 '{file_path}' 中的描述长度 ({len(description)}) "
            f"超过了1024字符限制。请缩短描述长度。"
        )

def parse_python_file(file_path: Path) -> List[Dict[str, Any]]:
    """解析单个 Python 文件，提取类信息
    
    Args:
        file_path: Python 文件路径
        
    Returns:
        List[Dict[str, Any]]: 类信息列表
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 获取类的文档字符串
                docstring = ast.get_docstring(node) or ""
                
                # 获取类的静态变量
                sif_var = None
                network_var = None
                gpu = 0
                cpu = 1
                mem_per_cpu = 4000
                partition = "gpu"
                conda_env = "base"
                display_name = None
                
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                if target.id == 'SIF':
                                    if isinstance(item.value, ast.Constant):
                                        sif_var = item.value.value
                                elif target.id == 'NETWORK':
                                    if isinstance(item.value, ast.Constant):
                                        network_var = item.value.value
                                elif target.id == 'GPU':
                                    if isinstance(item.value, ast.Constant):
                                        gpu = item.value.value
                                elif target.id == 'CPU':
                                    if isinstance(item.value, ast.Constant):
                                        cpu = item.value.value
                                elif target.id == 'MEM_PER_CPU':
                                    if isinstance(item.value, ast.Constant):
                                        mem_per_cpu = item.value.value
                                elif target.id == 'PARTITION':
                                    if isinstance(item.value, ast.Constant):
                                        partition = item.value.value
                                elif target.id == 'CONDA_ENV':
                                    if isinstance(item.value, ast.Constant):
                                        conda_env = item.value.value
                                elif target.id == 'DISPLAY_NAME':
                                    if isinstance(item.value, ast.Constant):    
                                        display_name = item.value.value
                
                # 获取类的参数信息
                parameters = {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
                
                # 使用 docstring_parser 解析类的文档字符串
                docs = dsp(docstring)
                if docs:
                    # 验证描述长度
                    if docs.short_description:
                        validate_description_length(docs.short_description, node.name, str(file_path))
                    
                    for p in docs.params:
                        try:
                            # 转换Python类型为JSON Schema类型
                            json_schema_type = convert_python_type_to_json_schema(p.type_name or "string")
                            
                            parameters["properties"][p.arg_name] = {
                                "description": p.description or "",
                                **json_schema_type
                            }
                            
                            if not p.is_optional:
                                parameters["required"].append(p.arg_name)
                        except ValueError as e:
                            raise ValueError(
                                f"在文件 '{file_path}' 的函数 '{node.name}' 中，"
                                f"参数 '{p.arg_name}' 的类型转换失败: {str(e)}"
                            )
                
                # 验证最终的 parameters schema
                try:
                    validate_json_schema(parameters, f"function '{node.name}' parameters")
                except ValueError as e:
                    raise ValueError(
                        f"在文件 '{file_path}' 的函数 '{node.name}' 中，"
                        f"生成的参数 schema 不符合规范: {str(e)}"
                    )
                
                class_info = {
                    "function": {
                        "name": f"{file_path.stem}.{node.name}",
                        "description": docs.short_description if docs else "",
                        "parameters": parameters,
                        "file": str(file_path),
                        "sif": sif_var,
                        "network": network_var,
                        "gpu": gpu,
                        "cpu": cpu,
                        "mem_per_cpu": mem_per_cpu,
                        "partition": partition,
                        "conda_env": conda_env,
                        "display_name": display_name
                    }
                }
                classes.append(class_info)
        
        return classes
    except Exception as e:
        print(f"解析文件 {file_path.name} 时出错: {str(e)}")
        raise  # 重新抛出异常，让上层处理

def parse_directory(directory: Path) -> List[Dict[str, Any]]:
    """解析目录下的所有 Python 文件
    
    Args:
        directory: 目录路径
        
    Returns:
        List[Dict[str, Any]]: 所有类信息列表
    """
    all_classes = []
    # 排除 config 目录
    for py_file in directory.rglob('*.py'):
        if not py_file.name.startswith('_') and 'config' not in py_file.parts:
            classes = parse_python_file(py_file)
            all_classes.extend(classes)
    return all_classes
