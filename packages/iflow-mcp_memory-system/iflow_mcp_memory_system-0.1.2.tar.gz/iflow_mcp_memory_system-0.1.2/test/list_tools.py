#!/usr/bin/env python3
"""
标准MCP客户端脚本，用于列出服务器下面所有的工具内容
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
                    "name": "工具列表查看器",
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
        
    async def list_tools(self):
        """列出所有可用工具"""
        message = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/list"
        }
        
        await self.send_message(message)
        return await self.read_response()
        
    async def close(self):
        """关闭连接"""
        if self.process:
            self.process.stdin.close()
            await self.process.wait()
            print("🔌 MCP连接已关闭")


async def list_all_tools():
    """列出所有工具的主函数"""
    workspace_path = "/Users/zhaoguo/Desktop/memory-system"
    
    print("🔧 准备列出服务器所有工具...")
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
            
        # 列出所有工具
        print("\n🔧 获取工具列表...")
        response = await client.list_tools()
        
        # 处理响应
        if response:
            if response.get("id") == 3 and "result" in response:
                result = response["result"]
                tools = result.get("tools", [])
                
                if tools:
                    print(f"\n📋 找到 {len(tools)} 个工具:")
                    print("=" * 60)
                    
                    for i, tool in enumerate(tools, 1):
                        print(f"\n{i}. 工具名称: {tool.get('name', 'N/A')}")
                        print(f"   描述: {tool.get('description', 'N/A')}")
                        
                        # 打印参数信息
                        input_schema = tool.get('inputSchema', {})
                        if input_schema:
                            properties = input_schema.get('properties', {})
                            required = input_schema.get('required', [])
                            
                            if properties:
                                print("   参数:")
                                for param_name, param_info in properties.items():
                                    required_marker = " (必需)" if param_name in required else " (可选)"
                                    param_type = param_info.get('type', 'unknown')
                                    param_desc = param_info.get('description', 'N/A')
                                    print(f"     • {param_name}{required_marker}: {param_type}")
                                    print(f"       描述: {param_desc}")
                            else:
                                print("   参数: 无")
                        else:
                            print("   参数: 无")
                        
                        print("-" * 40)
                    
                    print(f"\n✅ 工具列表获取完成！共 {len(tools)} 个工具")
                    return True
                else:
                    print("❌ 未找到任何工具")
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
    print("🔧 工具列表查看器 - MCP客户端")
    print("=" * 50)
    
    success = await list_all_tools()
    
    if success:
        print("\n🎉 任务完成！工具列表已成功获取")
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