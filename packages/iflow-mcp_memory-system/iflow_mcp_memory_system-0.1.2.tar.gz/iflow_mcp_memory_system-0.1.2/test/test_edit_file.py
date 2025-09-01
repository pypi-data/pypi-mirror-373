#!/usr/bin/env python3
"""
标准MCP客户端脚本，用于测试编辑文件功能
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
                    "name": "文件编辑测试器",
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
        
    async def call_tool(self, tool_name, arguments, request_id=2):
        """调用工具"""
        message = {
            "jsonrpc": "2.0",
            "id": request_id,
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


async def test_edit_file():
    """测试编辑文件的主函数"""
    workspace_path = "/Users/zhaoguo/Desktop/memory-system"
    test_file_name = "test.txt"
    
    # 原始内容
    original_content = """这是一个测试文件。
第一行内容
第二行内容
第三行内容
文件结束"""
    
    # 编辑后的内容
    edited_content = """这是一个编辑过的测试文件。
第一行内容已修改
第二行内容
第三行内容已修改
新增的第四行内容
文件结束"""
    
    print("📝 准备测试文件编辑功能...")
    print(f"📁 工作目录: {workspace_path}")
    print(f"📄 测试文件: {test_file_name}")
    print(f"📏 原始内容长度: {len(original_content)} 字符")
    print(f"📏 编辑后内容长度: {len(edited_content)} 字符")
    
    # 创建MCP客户端
    client = MCPClient(['uv', 'run', 'mcp-memory-system'], workspace_path)
    
    try:
        # 启动服务器
        await client.start_server()
        
        # 初始化连接
        if not await client.initialize():
            print("❌ 初始化失败，退出")
            return False
            
        # 步骤1: 先创建一个测试文件
        print("\n🔧 步骤1: 创建测试文件...")
        create_response = await client.call_tool("write_file", {
            "path": test_file_name,
            "content": original_content
        }, request_id=2)
        
        if not create_response or create_response.get("id") != 2:
            print("❌ 创建测试文件失败")
            return False
            
        if create_response["result"].get("isError"):
            print(f"❌ 创建文件出错: {create_response['result']}")
            return False
            
        print("✅ 测试文件创建成功")
        
        # 验证文件创建
        file_path = os.path.join(workspace_path, test_file_name)
        if not os.path.exists(file_path):
            print("❌ 测试文件验证失败: 文件未找到")
            return False
            
        # 步骤2: 编辑文件
        print("\n🔧 步骤2: 编辑文件...")
        edit_response = await client.call_tool("edit_file", {
            "path": test_file_name,
            "edits": [
                {
                    "oldText": "这是一个测试文件。",
                    "newText": "这是一个编辑过的测试文件。"
                },
                {
                    "oldText": "第一行内容",
                    "newText": "第一行内容已修改"
                },
                {
                    "oldText": "第三行内容",
                    "newText": "第三行内容已修改"
                },
                {
                    "oldText": "文件结束",
                    "newText": "新增的第四行内容\n文件结束"
                }
            ]
        }, request_id=3)
        
        # 处理编辑响应
        if edit_response:
            if edit_response.get("id") == 3 and "result" in edit_response:
                result = edit_response["result"]
                if result.get("isError"):
                    print(f"❌ 文件编辑出错: {result}")
                    return False
                else:
                    print("✅ 文件编辑成功！")
                    content = result.get("content", [])
                    if content:
                        print(f"📤 服务器响应: {content[0].get('text', '')}")
                    
                    # 验证文件是否被正确编辑
                    if os.path.exists(file_path):
                        print(f"✅ 文件验证: {file_path} 已成功编辑")
                        file_size = os.path.getsize(file_path)
                        print(f"📊 编辑后文件大小: {file_size} 字节")
                        
                        # 读取并显示编辑后的文件内容
                        with open(file_path, 'r', encoding='utf-8') as f:
                            actual_content = f.read()
                        
                        print(f"📖 编辑后内容预览: {actual_content[:100]}...")
                        
                        # 验证内容是否正确
                        if actual_content == edited_content:
                            print("✅ 内容验证成功: 文件内容与预期一致")
                            return True
                        else:
                            print("❌ 内容验证失败: 文件内容与预期不符")
                            print(f"预期长度: {len(edited_content)}, 实际长度: {len(actual_content)}")
                            return False
                    else:
                        print("❌ 文件验证失败: 编辑后文件未找到")
                        return False
            else:
                print(f"❌ 意外的响应格式: {edit_response}")
                return False
        else:
            print("❌ 未收到服务器编辑响应")
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
    print("📝 文件编辑功能测试器 - MCP客户端测试")
    print("=" * 50)
    
    success = await test_edit_file()
    
    if success:
        print("\n🎉 任务完成！文件编辑功能测试成功")
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