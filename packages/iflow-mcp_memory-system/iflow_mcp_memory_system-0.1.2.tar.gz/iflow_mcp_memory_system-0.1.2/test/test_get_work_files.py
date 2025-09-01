#!/usr/bin/env python3
"""
测试 get_work_files 工具的脚本
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
            cwd='/Users/zhaoguo/Desktop/memory-system/mcp-memory-system',
            limit=1024*1024  # 增加缓冲区到1MB
        )
        print(f"🚀 MCP服务器已启动，PID: {self.process.pid}")
        
    async def send_message(self, message):
        """发送JSON-RPC消息到服务器"""
        message_str = json.dumps(message) + '\n'
        self.process.stdin.write(message_str.encode())
        await self.process.stdin.drain()
        
    async def read_response(self):
        """读取服务器响应"""
        try:
            # 增加缓冲区大小以处理大输出
            line = await asyncio.wait_for(self.process.stdout.readline(), timeout=30.0)
            if line:
                try:
                    return json.loads(line.decode().strip())
                except json.JSONDecodeError as e:
                    print(f"JSON解码错误: {e}")
                    print(f"原始响应: {line.decode()[:500]}...")  # 只显示前500个字符
                    return None
            return None
        except asyncio.TimeoutError:
            print("⏰ 读取响应超时")
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
                    "name": "get_work_files测试器",
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


async def test_get_work_files():
    """测试 get_work_files 工具的主函数"""
    workspace_path = "/Users/zhaoguo/Desktop/memory-system"
    
    print("🔧 准备测试 get_work_files 工具...")
    print(f"📁 工作目录: {workspace_path}")
    
    # 创建MCP客户端
    client = MCPClient(['uv', 'run', 'mcp-memory-system'], workspace_path)
    
    try:
        # 启动服务器
        await client.start_server()
        
        # 初始化连接
        if not await client.initialize():
            print("❌ 初始化失败，退出")
            return False
            
        # 测试1: 基本用法（限制深度为1避免输出过大）
        print("\n📝 测试1: 基本用法（深度限制为1）")
        print("=" * 60)
        response = await client.call_tool("get_work_files", {"max_depth": 1})
        
        if response and response.get("id") == 2 and "result" in response:
            result = response["result"]
            if result.get("isError"):
                print(f"❌ 工具执行出错: {result}")
            else:
                content = result.get("content", [])
                if content:
                    print("✅ 获取文件列表成功！")
                    print(content[0].get('text', ''))
                else:
                    print("❌ 未收到内容")
        else:
            print(f"❌ 意外的响应格式: {response}")
        
        # 测试2: 包含隐藏文件
        print("\n📝 测试2: 包含隐藏文件")
        print("=" * 60)
        response = await client.call_tool("get_work_files", {
            "include_hidden": True
        })
        
        if response and response.get("id") == 2 and "result" in response:
            result = response["result"]
            if result.get("isError"):
                print(f"❌ 工具执行出错: {result}")
            else:
                content = result.get("content", [])
                if content:
                    print("✅ 获取文件列表成功（包含隐藏文件）！")
                    text_content = content[0].get('text', '')
                    # 只显示前500个字符，避免输出过长
                    if len(text_content) > 500:
                        print(text_content[:500] + "...")
                        print(f"\n（输出已截断，总长度: {len(text_content)} 字符）")
                    else:
                        print(text_content)
                else:
                    print("❌ 未收到内容")
        else:
            print(f"❌ 意外的响应格式: {response}")
        
        # 测试3: 限制深度为1
        print("\n📝 测试3: 限制深度为1（只显示第一层）")
        print("=" * 60)
        response = await client.call_tool("get_work_files", {
            "max_depth": 1
        })
        
        if response and response.get("id") == 2 and "result" in response:
            result = response["result"]
            if result.get("isError"):
                print(f"❌ 工具执行出错: {result}")
            else:
                content = result.get("content", [])
                if content:
                    print("✅ 获取文件列表成功（深度限制为1）！")
                    print(content[0].get('text', ''))
                else:
                    print("❌ 未收到内容")
        else:
            print(f"❌ 意外的响应格式: {response}")
        
        # 测试4: 包含隐藏文件且限制深度
        print("\n📝 测试4: 包含隐藏文件且限制深度为2")
        print("=" * 60)
        response = await client.call_tool("get_work_files", {
            "include_hidden": True,
            "max_depth": 2
        })
        
        if response and response.get("id") == 2 and "result" in response:
            result = response["result"]
            if result.get("isError"):
                print(f"❌ 工具执行出错: {result}")
            else:
                content = result.get("content", [])
                if content:
                    print("✅ 获取文件列表成功（包含隐藏文件，深度限制为2）！")
                    text_content = content[0].get('text', '')
                    # 只显示前800个字符
                    if len(text_content) > 800:
                        print(text_content[:800] + "...")
                        print(f"\n（输出已截断，总长度: {len(text_content)} 字符）")
                    else:
                        print(text_content)
                else:
                    print("❌ 未收到内容")
        else:
            print(f"❌ 意外的响应格式: {response}")
        
        return True
            
    except Exception as e:
        print(f"❌ 执行过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        await client.close()


async def main():
    """主函数"""
    print("🔧 get_work_files 工具测试器 - MCP客户端")
    print("=" * 50)
    
    success = await test_get_work_files()
    
    if success:
        print("\n🎉 所有测试完成！")
        return 0
    else:
        print("\n💥 测试失败！请检查错误信息")
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