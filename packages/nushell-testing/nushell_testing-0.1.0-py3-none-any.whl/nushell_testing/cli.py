import os
import sys
import subprocess
from pathlib import Path

def main():
    # 获取EXE文件的路径（在包安装目录下）
    exe_path = Path(__file__).parent / 'data' / 'nushell.exe'
    
    if not exe_path.exists():
        print(f"Error: {exe_path} not found!")
        sys.exit(1)
    
    # 运行EXE并传递所有参数
    result = subprocess.run([str(exe_path)] + sys.argv[1:])
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()