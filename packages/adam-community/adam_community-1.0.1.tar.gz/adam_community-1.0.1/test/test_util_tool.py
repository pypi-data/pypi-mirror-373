import unittest
from unittest.mock import patch, MagicMock, PropertyMock
import sys
import os

# 设置环境变量
os.environ['ADAM_API_TOKEN'] = 'test_token'
os.environ['ADAM_API_HOST'] = 'https://test.com'

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock OpenAI client before importing util
with patch('openai.OpenAI'):
    from adam_community.util import knowledgeSearch, completionCreate, runCmd
    from adam_community.tool import Tool

class TestUtil(unittest.TestCase):
    def setUp(self):
        self.test_params = {
            "project": "test_project",
            "name": "test_collection",
            "query": "test query",
            "limit": 10
        }
        
    @patch('urllib.request.urlopen')
    def test_knowledgeSearch(self, mock_urlopen):
        """测试knowledgeSearch函数"""
        mock_response = MagicMock()
        # 设置status属性为整数
        type(mock_response).status = PropertyMock(return_value=200)
        mock_response.read.return_value = b'{"result": "success"}'
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = knowledgeSearch(
            query_info="test query",
            messages_prev=[{"role": "user", "content": "test"}],
            project_name="test_project",
            collection_name="test_collection"
        )
        
        self.assertEqual(result, '{"result": "success"}')
        mock_urlopen.assert_called_once()

    @patch('subprocess.Popen')
    @patch.dict(os.environ, {'ADAM_OUTPUT_RAW': ''}, clear=True)
    def test_runCmd_success(self, mock_popen):
        """测试runCmd函数成功执行命令的情况"""
        mock_process = MagicMock()
        mock_process.poll.return_value = 0
        mock_process.returncode = 0
        mock_process.stdout.readline.return_value = "test output"
        mock_process.stderr.readline.return_value = ""
        mock_popen.return_value = mock_process
        
        process = runCmd('echo "test output"')
        self.assertEqual(process.returncode, 0)
        mock_popen.assert_called_once()

    @patch('subprocess.Popen')
    @patch.dict(os.environ, {'ADAM_OUTPUT_RAW': ''}, clear=True)
    def test_runCmd_failure(self, mock_popen):
        """测试runCmd函数执行失败的情况"""
        mock_process = MagicMock()
        mock_process.poll.return_value = 1
        mock_process.returncode = 1
        mock_process.stdout.readline.return_value = ""
        mock_process.stderr.readline.return_value = "command not found"
        mock_popen.return_value = mock_process
        
        with self.assertRaises(SystemExit) as cm:
            runCmd('nonexistent_command_123456')
        self.assertEqual(cm.exception.code, 1)

    @patch.dict(os.environ, {'ADAM_OUTPUT_RAW': 'true'}, clear=True)
    def test_runCmd_with_raw_output(self):
        """测试runCmd函数在ADAM_OUTPUT_RAW环境变量设置时的情况"""
        cmd = 'echo "test output"'
        result = runCmd(cmd)
        self.assertEqual(result, cmd)

class TestTool(unittest.TestCase):
    def setUp(self):
        class TestToolImpl(Tool):
            def call(self, kwargs):
                return "test command"
        
        self.tool = TestToolImpl()
        
    def test_inputShow(self):
        """测试inputShow方法"""
        kwargs = {
            "task_id": "test_task",
            "user": "test_user",
            "message": "test message"
        }
        
        with patch.object(self.tool, 'call', return_value="test command"):
            result = self.tool.inputShow(**kwargs)
            self.assertIn("test_user@Adam", result)
            self.assertIn("test_task", result)
        
    def test_resAlloc(self):
        """测试resAlloc方法"""
        kwargs = {
            "tool_data": "test_data",
            "tip": "test tip"
        }
        
        result = self.tool.resAlloc(kwargs)
        self.assertIn("CPU", result)
        self.assertIn("MEM_PER_CPU", result)
        self.assertIn("GPU", result)
        self.assertIn("PARTITION", result)
        
    def test_outputShow(self):
        """测试outputShow方法"""
        kwargs = {
            "stdout": "test stdout",
            "stderr": "test stderr",
            "exit_code": 0
        }
        
        result, files = self.tool.outputShow(kwargs)
        self.assertIn("test stdout", result)
        self.assertIn("test stderr", result)
        self.assertEqual(files, [])
        
    def test_markdown_color(self):
        """测试markdown_color静态方法"""
        result = Tool.markdown_color("test", "red")
        self.assertEqual(result, '<span style="color: red">test</span>')
        
    def test_markdown_terminal(self):
        """测试markdown_terminal静态方法"""
        result = Tool.markdown_terminal("test command", "test_env", "test_user", "test_dir")
        self.assertIn("test_user@Adam", result)
        self.assertIn("test_dir", result)
        self.assertIn("test command", result)

if __name__ == '__main__':
    unittest.main() 