import asyncio
import sys
import os
from pathlib import Path
import pytest

# 添加当前目录到 sys.path 以便导入 builder
sys.path.append(os.getcwd())

from builder.services.shell_service import ShellService

@pytest.mark.asyncio
async def test_maven_build():
    shell = ShellService()
    target_dir = r"E:\code\KDesigner\time-tracking-system"
    command = 'mvn clean install "-DskipTests"'
    
    print(f"--- 开始测试 ---")
    print(f"目标目录: {target_dir}")
    print(f"执行命令: {command}")
    
    try:
        # 在 Windows 上，mvn 实际上是一个 mvn.cmd 文件
        # 我们先尝试直接运行，如果失败，尝试 mvn.cmd
        output = await shell.run_command(command, cwd=target_dir)
        print("\n--- 执行成功 ---")
        # 打印最后 20 行输出，避免太多
        lines = output.splitlines()
        for line in lines[-20:]:
            print(line)
            
    except Exception as e:
        print("\n--- 执行失败 ---")
        print(str(e))
        
        # 如果失败，尝试显式指定 mvn.cmd
        print("\n尝试使用 mvn.cmd 重新执行...")
        try:
            command_v2 = 'mvn.cmd clean install "-DskipTests"'
            output = await shell.run_command(command_v2, cwd=target_dir)
            print("\n--- 执行成功 (使用 mvn.cmd) ---")
            lines = output.splitlines()
            for line in lines[-20:]:
                print(line)
        except Exception as e2:
            print(f"\n再次失败: {e2}")

if __name__ == "__main__":
    asyncio.run(test_maven_build())
