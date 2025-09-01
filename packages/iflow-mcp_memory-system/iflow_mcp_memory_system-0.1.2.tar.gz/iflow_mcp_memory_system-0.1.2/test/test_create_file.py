#!/usr/bin/env python3
"""
标准MCP客户端脚本，用于测试创建教师节文案文件
"""

import asyncio
import json
import subprocess
import sys
import os
from pathlib import Path

class MCPClient:
    def __init__(self, server_command, workspace_path):
        self.server_command = server_command
        self.workspace_path = workspace_path
        self.process = None
        
    async def start_server(self):
        """启动MCP服务器"""
        cmd = self.server_command + ['--workspace-path', self.workspace_path]
        self.process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd='/Users/zhaoguo/Desktop/memory-system/mcp-memory-system'
        )
        print(f"🚀 MCP服务器已启动，PID: {self.process.pid}")
        
    async def send_message(self, message):
        """发送JSON-RPC消息到服务器"""
        message_str = json.dumps(message) + '\n'
        self.process.stdin.write(message_str.encode())
        await self.process.stdin.drain()
        
    async def read_response(self):
        """读取服务器响应"""
        line = await self.process.stdout.readline()
        if line:
            try:
                return json.loads(line.decode().strip())
            except json.JSONDecodeError as e:
                print(f"JSON解码错误: {e}")
                print(f"原始响应: {line.decode()}")
                return None
        return None
        
    async def initialize(self):
        """初始化MCP连接"""
        print("📡 初始化MCP连接...")
        
        # 发送initialize请求
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "教师节文案创建器",
                    "version": "1.0"
                }
            }
        }
        
        await self.send_message(init_message)
        response = await self.read_response()
        
        if response and response.get("id") == 1:
            print("✅ 服务器初始化成功")
            print(f"   服务器信息: {response['result']['serverInfo']}")
        else:
            print("❌ 初始化失败")
            return False
            
        # 发送initialized通知
        initialized_message = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        await self.send_message(initialized_message)
        print("✅ 初始化完成通知已发送")
        
        return True
        
    async def call_tool(self, tool_name, arguments):
        """调用工具"""
        message = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        await self.send_message(message)
        return await self.read_response()
        
    async def close(self):
        """关闭连接"""
        if self.process:
            self.process.stdin.close()
            await self.process.wait()
            print("🔌 MCP连接已关闭")


async def create_teacher_day_file():
    """创建教师节文案文件的主函数"""
    workspace_path = "/Users/zhaoguo/Desktop/memory-system"
    
    # 准备教师节文案内容
    teacher_day_content = """亲爱的老师们，您们是知识的传播者，智慧的启蒙者，心灵的塑造者。您们用粉笔书写人生真理，用爱心浇灌学子心田，用耐心雕琢璞玉成器。春蚕到死丝方尽，蜡炬成灰泪始干，这正是您们无私奉献精神的真实写照。您们不仅传授知识，更是品格的楷模，人生的导师。在这个特殊的日子里，让我们向所有辛勤工作在教育一线的老师们致敬！感谢您们的付出与坚守，您们的恩情如山高海深，将伴随学生们一生。祝愿所有的老师身体健康，工作顺利，桃李满天下！"""
    
    print("📝 准备创建教师节赞颂文案文件...")
    print(f"📁 工作目录: {workspace_path}")
    print(f"📄 文件名: 教师节赞颂文案.txt")
    print(f"📏 内容长度: {len(teacher_day_content)} 字符")
    
    # 创建MCP客户端
    client = MCPClient(['uv', 'run', 'mcp-memory-system'], workspace_path)
    
    try:
        # 启动服务器
        await client.start_server()
        
        # 初始化连接
        if not await client.initialize():
            print("❌ 初始化失败，退出")
            return False
            
        # 调用write_file工具
        print("\n🔧 调用write_file工具...")
        response = await client.call_tool("write_file", {
            "path": "教师节赞颂文案.txt",
            "content": teacher_day_content
        })
        
        # 处理响应
        if response:
            if response.get("id") == 2 and "result" in response:
                result = response["result"]
                if result.get("isError"):
                    print(f"❌ 工具执行出错: {result}")
                    return False
                else:
                    print("✅ 文件创建成功！")
                    content = result.get("content", [])
                    if content:
                        print(f"📤 服务器响应: {content[0].get('text', '')}")
                    
                    # 验证文件是否真的被创建
                    file_path = os.path.join(workspace_path, "教师节赞颂文案.txt")
                    if os.path.exists(file_path):
                        print(f"✅ 文件验证: {file_path} 已成功创建")
                        file_size = os.path.getsize(file_path)
                        print(f"📊 文件大小: {file_size} 字节")
                        
                        # 读取并显示文件内容的前100个字符
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content_preview = f.read()[:100]
                        print(f"📖 内容预览: {content_preview}...")
                        
                        return True
                    else:
                        print("❌ 文件验证失败: 文件未找到")
                        return False
            else:
                print(f"❌ 意外的响应格式: {response}")
                return False
        else:
            print("❌ 未收到服务器响应")
            return False
            
    except Exception as e:
        print(f"❌ 执行过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        await client.close()


async def main():
    """主函数"""
    print("🎓 教师节文案创建器 - MCP客户端测试")
    print("=" * 50)
    
    success = await create_teacher_day_file()
    
    if success:
        print("\n🎉 任务完成！教师节文案文件已成功创建")
        return 0
    else:
        print("\n💥 任务失败！请检查错误信息")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 程序异常: {str(e)}")
        sys.exit(1)