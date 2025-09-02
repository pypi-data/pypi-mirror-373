import time
import urllib.request
import urllib.error
import json
import subprocess
import sys
import os
import select
import logging
import ssl
from functools import wraps
from subprocess import run, CalledProcessError

logger = logging.getLogger(__name__)

ADAM_API_HOST = os.getenv('ADAM_API_HOST', 'https://sidereus-ai.com')
ADAM_API_TOKEN = os.getenv('ADAM_API_TOKEN')
ADAM_TASK_ID = os.getenv('ADAM_TASK_ID')
ADAM_USER_ID = os.getenv('ADAM_USER_ID')
CONDA_ENV = os.getenv('CONDA_ENV')

# 定义可用的知识库集合
collections = ["DSDP","MPNN","PySCF","RFdiffusion","gaussian","protenix","GPU4PySCF","MolecularDynamics","RDkit","OpenBabel", "SPONGE", "Xponge", "MDAnalysis", "ABACUS"]

class RAG:
    """
    搜寻RAG知识

    :param str query: 需要运行的命令
    :param str collection: 搜寻的知识库名称。必须是下面之一："DSDP","MPNN","PySCF","RFdiffusion","gaussian","protenix","GPU4PySCF","MolecularDynamics","RDkit","OpenBabel"
    """

    def call(self, query: str, collection: str):

        if collection not in collections:
            raise ValueError(f"知识库名称必须是下面之一：{collections}")

        cmd = f"""akb simple-query \
    -i /share/programs/akb/database/{collection}/{collection}.index \
    -m /share/programs/BAAI/bge-m3 \
    -p /share/programs/akb/database/{collection}/{collection}.parquet \
    -l 5 \
    -f json -q \"{query}\""""
        logger.info(f"搜索知识库 {collection}: {query}")
        try:
            result = run(cmd, shell='/bin/bash', check=True, text=True, capture_output=True)
        except CalledProcessError as e:
            logger.error(e.stderr.strip())
            return e.stderr.strip()

        try:
            return "\n".join(json.loads(result.stdout))
        except Exception as e:
            logger.error(e)
            return result.stdout


def retry_on_exception(max_retries=3, delay=5):
    """
    重试装饰器，在发生异常时最多重试指定次数
    
    Args:
        max_retries: 最大重试次数
        delay: 重试间隔时间（秒）
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay)
                        continue
                    raise last_exception
            return None
        return wrapper
    return decorator


def _make_http_request(url, data, return_json=True):
    """
    通用的 HTTP POST 请求函数
    
    Args:
        url: 请求的 URL
        data: 请求数据（字典格式）
        return_json: 是否将响应解析为 JSON，False 则返回文本
    
    Returns:
        响应数据（JSON 或文本）
    """
    if not ADAM_API_TOKEN:
        raise ValueError("ADAM_API_TOKEN environment variable is not set")
    
    headers = {
        "Authorization": f"Bearer {ADAM_API_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        # 将请求数据转换为JSON字符串并编码
        json_data = json.dumps(data).encode('utf-8')
        
        # 创建请求对象
        req = urllib.request.Request(url, data=json_data, headers=headers, method='POST')
        
        context = ssl._create_unverified_context()

        # 发送请求
        with urllib.request.urlopen(req, context=context) as response:
            # 检查响应状态码
            if response.status >= 400:
                raise Exception(f"HTTP错误: {response.status}")
            
            # 读取响应
            response_data = response.read().decode('utf-8')
            
            # 根据需要返回 JSON 或文本
            if return_json:
                return json.loads(response_data)
            else:
                return response_data
                
    except urllib.error.HTTPError as e:
        raise Exception(f"HTTP请求失败 - HTTP错误 {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        raise Exception(f"HTTP请求失败 - 网络错误: {str(e)}")
    except json.JSONDecodeError as e:
        if return_json:
            raise Exception(f"HTTP请求失败 - JSON解析错误: {str(e)}")
        else:
            raise Exception(f"HTTP请求失败 - 响应解码错误: {str(e)}")
    except Exception as e:
        raise Exception(f"HTTP请求失败: {str(e)}")


def messageSend(message):
    """
    发送消息给用户
    """
    if not ADAM_API_HOST:
        raise ValueError("ADAM_API_HOST environment variable is not set")
    if not ADAM_TASK_ID:
        raise ValueError("ADAM_TASK_ID environment variable is not set")

    url = f"{ADAM_API_HOST}/api/task/create_message"
    
    request_data = {
        "task_id": ADAM_TASK_ID,
        "message": message,
        "role": "tool"
    }

    try:
        return _make_http_request(url, request_data, return_json=True)
    except Exception as e:
        raise Exception(f"发送消息失败: {str(e)}")


@retry_on_exception(max_retries=3)
def knowledgeSearch(query_info, messages_prev, project_name, collection_name, max_messages=4):
    """
    知识库检索函数
    """
    if not collection_name:
        raise ValueError("collection_name 参数是必需的")

    if collection_name not in collections:
        raise ValueError(f"知识库名称必须是下面之一：{collections}")

    try:
        # 使用本地RAG实现
        rag = RAG()
        result = rag.call(query_info, collection_name)

        # 构造返回格式，保持与原有API格式一致
        response_data = {
            "code": 0,
            "data": {
                "collection_name": collection_name,
                "count": 1,
                "result_list": [{
                    "chunk_id": 0,
                    "chunk_source": "document",
                    "chunk_title": result.split("\n")[0] if result else "",
                    "chunk_type": "text",
                    "content": result,
                    "doc_info": {
                        "create_time": 0,
                        "doc_id": "local_doc",
                        "doc_name": f"{collection_name}_knowledge",
                        "doc_type": "text",
                        "source": "local"
                    },
                    "score": 1.0
                }],
                "token_usage": {
                    "embedding_token_usage": {
                        "completion_tokens": 0,
                        "prompt_tokens": 0,
                        "total_tokens": 0
                    },
                    "rerank_token_usage": 0
                }
            },
            "message": "success",
            "request_id": "local_request"
        }

        return json.dumps(response_data, ensure_ascii=False)
    except Exception as e:
        error_response = {
            "code": 1,
            "message": f"知识库搜索失败: {str(e)}"
        }
        return json.dumps(error_response, ensure_ascii=False)


class DynamicObject:
    """
    动态对象类，用于处理 JSON 响应
    
    这个类可以动态地将字典转换为对象属性，支持嵌套的字典结构
    同时保持原始数据的访问能力
    """
    def __init__(self, data):
        self._raw_data = data
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    setattr(self, key, self._convert_value(value))
                else:
                    setattr(self, key, value)
    
    def _convert_value(self, value):
        """递归转换嵌套的数据结构"""
        if isinstance(value, dict):
            return DynamicObject(value)
        elif isinstance(value, list):
            return [self._convert_value(item) for item in value]
        return value
    
    def __getattr__(self, name):
        """处理未定义的属性访问"""
        return self._raw_data.get(name)
    
    def __getitem__(self, key):
        """支持字典式访问"""
        return self._raw_data.get(key)
    
    def __str__(self):
        """返回可读的字符串表示"""
        return f"DynamicObject({self._raw_data})"
    
    def __repr__(self):
        return self.__str__()
    
    def to_dict(self):
        """将对象转换回字典"""
        return self._raw_data


@retry_on_exception(max_retries=3)
def completionCreate(request_params):
    """
    创建 openai 的代理函数
    
    Returns:
        DynamicObject: 一个动态对象，可以像访问属性一样访问 API 响应的所有字段
    """
    if not ADAM_API_HOST:
        raise ValueError("ADAM_API_HOST environment variable is not set")

    url = f"{ADAM_API_HOST}/api/chat/completions"
    
    try:
        response = _make_http_request(url, request_params, return_json=True)
        return DynamicObject(response)
    except Exception as e:
        raise Exception(f"调用聊天补全接口失败: {str(e)}")

def runCmd(cmd):
    """
    执行命令，实时输出执行结果

    修复了原实现中可能存在的阻塞和内容丢失问题
    """
    if os.getenv("ADAM_OUTPUT_RAW"):
        return cmd

    process = subprocess.Popen(
        cmd,
        shell=True,
	executable='/bin/bash',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        bufsize=1
    )

    try:
        # 使用 select 来同时监控 stdout 和 stderr，避免阻塞
        while True:
            # 检查进程是否已结束
            if process.poll() is not None:
                break

            # 使用 select 来检查是否有可读的数据
            rlist, _, _ = select.select([process.stdout, process.stderr], [], [], 0.1)

            for stream in rlist:
                line = stream.readline()
                if line:
                    if stream == process.stdout:
                        print(line.strip())
                    else:
                        print(line.strip(), file=sys.stderr)

        # 读取剩余的输出（如果有）
        for line in process.stdout:
            print(line.strip())
        for line in process.stderr:
            print(line.strip(), file=sys.stderr)

        # 检查返回码
        if process.returncode != 0:
            sys.exit(process.returncode)

        return process
    finally:
        # 确保所有文件描述符都被关闭
        process.stdout.close()
        process.stderr.close()

def markdown_color(content, color):
    return f'<span style="color: {color}">{content}</span>'

def markdown_terminal(content, conda_env="base", user="Adam", workdir=""):
    user = markdown_color(f"{user}@Adam", "green")
    workdir = markdown_color(f":~/{workdir}", "blue")
    return f'({conda_env}) {user}{workdir}$ {content}'
