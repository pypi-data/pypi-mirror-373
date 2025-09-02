# Adam Community

Adam Community 是一个 Python 工具包，提供了 CLI 命令行工具和 Python 模块，用于解析和构建 Python 项目包。

## 安装

```bash
pip install -e .
```

## 使用方式

### CLI 命令行

查看帮助：
```bash
adam-cli --help
```

初始化新项目：
```bash
adam-cli init
```

解析 Python 文件生成 functions.json：
```bash
adam-cli parse .
```

构建项目包：
```bash
adam-cli build .
```

更新 CLI 到最新版本：
```bash
adam-cli update
```

### Python 模块导入

```python
from adam_community.cli.parser import parse_directory, parse_python_file
from adam_community.cli.build import build_package

# 解析目录下的 Python 文件
classes = parse_directory(Path("./"))

# 构建项目包
success, errors, zip_name = build_package(Path("./"))
```

## 功能特性

- **Python 文件解析**: 自动解析 Python 类和函数的文档字符串
- **JSON Schema 验证**: 将 Python 类型转换为 JSON Schema 并验证
- **项目构建**: 检查配置文件、文档文件并创建 zip 包
- **类型检查**: 支持多种 Python 类型注解格式
- **自动更新**: 智能检查和更新到最新版本，支持用户配置

## 开发

安装依赖：
```bash
make install
```

运行测试：
```bash
make test
```

构建包：
```bash
make build
```
