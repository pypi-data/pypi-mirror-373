import os
import subprocess
from pathlib import Path

def run_script_in_venv(venv_path, script_path, params=''):
    """在虚拟环境中运行脚本并传递参数"""
    python_exec = os.path.join(
        venv_path,
        'Scripts' if os.name == 'nt' else 'bin',
        'python.exe' if os.name == 'nt' else 'python'
    )
    if params == '':
        cmd = [python_exec, script_path]
    else:
        cmd = [python_exec, script_path, '-p', params]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False
    )

    return {
        'success': result.returncode == 0,
        'returncode': result.returncode,
        'stdout': result.stdout,
        'stderr': result.stderr
    }

def get_files_in_dir(dir_path):
    """使用pathlib获取目录下一层的所有文件全路径"""
    path = Path(dir_path)
    return [str(file) for file in path.iterdir() if file.is_file()]

if __name__ == '__main__':
    venv_env = ''
    code_str = '<tool_call>Terminate</tool_call>'
    print(code_str.find('<tool_call>'))
    print(code_str.find('</tool_call>'))
    print(code_str.find('Terminate'))