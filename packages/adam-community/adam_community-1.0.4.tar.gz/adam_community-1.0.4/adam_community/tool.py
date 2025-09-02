import logging
import os
from .util import markdown_color, markdown_terminal

class Tool:
    logger = logging.getLogger("ADAM-TOOL")

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()

        for key, value in kwargs.items():
            setattr(cls, key, value)
        if not hasattr(cls, "GPU"):
            cls.GPU = 0
        if not hasattr(cls, "CPU"):
            cls.CPU = 1
        if not hasattr(cls, "MEM_PER_CPU"):
            cls.MEM_PER_CPU = 4000
        if not hasattr(cls, "PARTITION"):
            cls.PARTITION = "gpu_3090"
        if not hasattr(cls, "CONDA_ENV"):
            cls.CONDA_ENV = "base"
        if not hasattr(cls, "calltype"):
            cls.calltype = "bash"


    def inputShow(self, **kwargs):
        """
            AI决定使用该工具时调用，用于打印信息告知用户目前调用的工具
            此处的kwargs更改对后续过程无效

            :param dict args: 字典形式的AI产生的输入
            :param list[str] files: 此次用户上传的文件
            :param str message: 此次用户询问的消息
            :param str user: 用户昵称
            :param str task_id: 任务编号
        """
        if self.calltype == "bash":
            os.environ["ADAM_OUTPUT_RAW"] = "true"
            scripts = self.call(self, kwargs)
            os.environ["ADAM_OUTPUT_RAW"] = "false"

            scripts = '\n'.join(['bash -s << EOF', scripts, 'EOF'])
        else:
            scripts = f"""python {self.__name__}.py"""
        return Tool.markdown_terminal(scripts, workdir=kwargs["task_id"],
                user=kwargs["user"], conda_env=self.CONDA_ENV)

    def resAlloc(self, kwargs):
        """
            提交工具任务时调用，用于获取分配的资源量
            此处的kwargs更改只有tool_data和tip对后续过程有效

            kwarg在inputShow的基础之上新增：
            :param any tool_data: 可序列化的任意数据
            :param str tip: 用来给用户显示的提示
            :returns: 一个字典，包括使用的GPU、CPU和MEM_PER_CPU（以MB单位的整数）
        """
        return {"CPU": self.CPU, "MEM_PER_CPU": self.MEM_PER_CPU,
                "GPU": self.GPU, "PARTITION": self.PARTITION}

    def call(self, kwargs):
        """
            实际执行脚本
            此处的kwargs更改只有tool_data，tip和token_usage对后续过程有效

            kwarg同resAlloc
            :returns: calltype=bash时，返回实际运行的bash脚本；
                calltype=python时，return调用值无效
        """
        raise NotImplementedError


    def monitor(self, kwargs):
        """
            任务运行时的监控命令，用于告知用户目前的进度
            只有在return为True时，此处的kwargs更改tool_data、tip和progress对后续过程有效

            kwargs在call的基础之上新增：
            :param int run_time: 以秒为单位的运行时间
            :param float progress: 任务进度，1为任务完成，0.5为50%，以此类推
        """
        pass

    def outputShow(self, kwargs):
        """
            任务结束时调用，用于打印信息告知用户工具结果

            kwargs在monitor的基础上新增：
            :param str stdout: stdout流的结果
            :param str stderr: stderr流的结果
            :param int exit_code: 退出码
            :returns: 一个给用户的文本, 一个包含显示文件的列表
        """
        stdout = kwargs["stdout"]
        if len(stdout) > 10000:
            stdout = stdout[:5000] + "\n...输出太长已省略...\n" + stdout[-5000:]
        
        stderr = kwargs["stderr"]
        if len(stderr) > 10000:
            stderr = stderr[:5000] + "\n...输出太长已省略...\n" + stderr[-5000:]
        return f'''- exit code: {kwargs['exit_code']}
- stdout:
```
{stdout}
```
- stderr:
```
{stderr}
```
''', []

    def summary(self, kwargs):
        """
            任务结束时调用，用于打印信息告知AI结果

            kwargs同outputShow
            :returns: 一个给AI的文本
        """
        stdout = kwargs["stdout"]
        if len(stdout) > 10000:
            stdout = stdout[:5000] + "\n...输出太长已省略...\n" + stdout[-5000:]
        stderr = kwargs["stderr"]
        if len(stderr) > 10000:
            stderr = stderr[:5000] + "\n...输出太长已省略...\n" + stderr[-5000:]
        return f'''- exit code: {kwargs['exit_code']}
- stdout:
```
{stdout}
```
- stderr:
```
{stderr}
```
'''

    @staticmethod
    def markdown_color(content, color):
        return markdown_color(content, color)

    @staticmethod
    def markdown_terminal(content, conda_env="base", user="Adam", workdir=""):
        return markdown_terminal(content, conda_env, user, workdir)
