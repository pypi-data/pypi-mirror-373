#!/usr/bin/env python3
"""
测试附件下载功能的脚本
"""

import asyncio
import json
from typing import Dict, Any
import sys
from pathlib import Path
import os

# 添加源代码路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from emails_mcp.config import config_manager
from emails_mcp.services import EmailService
from emails_mcp.backends import FileBackend


def test_attachment_download():
    """测试附件下载功能"""
    
    print("=== 附件下载功能测试 ===\n")
    
    # 加载配置
    config_path = "/homes/junlong/junlong/projects/mcpbench_dev_infra/tasks/debug/debug-task/email_config.json"
    
    # 初始化配置管理器
    config_manager.load_workspace_config(
        config_file=config_path,
        attachment_download_path="./"
    )
    
    email_config = config_manager.load_email_config(config_path)
    if not email_config:
        print("配置加载失败")
        return
    
    # 创建邮件服务
    email_service = EmailService(email_config)
    
    print("1. 连接状态检查...")
    try:
        imap_ok, smtp_ok = email_service.check_connection()
        print(f"   IMAP: {'✓ 已连接' if imap_ok else '✗ 连接失败'}")
        print(f"   SMTP: {'✓ 已连接' if smtp_ok else '✗ 连接失败'}")
        
        if not imap_ok:
            print("   错误: IMAP连接失败，无法继续测试")
            return
    except Exception as e:
        print(f"   连接检查失败: {e}")
        return
    
    print("\n2. 获取邮件列表...")
    try:
        result = email_service.get_emails("INBOX", page=1, page_size=10)
        print(f"   找到 {len(result.emails)} 封邮件")
        
        # 寻找带附件的邮件
        emails_with_attachments = []
        for email in result.emails:
            if email.attachments and len(email.attachments) > 0:
                emails_with_attachments.append(email)
        
        print(f"   其中 {len(emails_with_attachments)} 封邮件包含附件")
        
        if not emails_with_attachments:
            print("   没有找到带附件的邮件，测试结束")
            return
            
    except Exception as e:
        print(f"   获取邮件失败: {e}")
        return
    
    print("\n3. 测试附件下载...")
    test_email = emails_with_attachments[0]
    print(f"   测试邮件: {test_email.email_id}")
    print(f"   主题: {test_email.subject}")
    print(f"   附件数量: {len(test_email.attachments)}")
    
    # 显示附件信息
    print("   附件列表:")
    for i, attachment in enumerate(test_email.attachments, 1):
        print(f"     {i}. {attachment.filename} ({attachment.content_type}, {attachment.size} bytes)")
    
    # 测试下载第一个附件
    if test_email.attachments:
        test_attachment = test_email.attachments[0]
        download_path = "/tmp"  # 使用临时目录
        
        print(f"\n   尝试下载附件: {test_attachment.filename}")
        try:
            # 直接从IMAP获取原始邮件数据
            email_service.imap_backend.ensure_connected()
            status, data = email_service.imap_backend.connection.fetch(test_email.email_id, '(RFC822)')
            
            if status != 'OK' or not data:
                print("   错误: 无法获取邮件数据")
                return
            
            # 解析原始邮件
            import email as email_module
            raw_email = None
            for item in data:
                if isinstance(item, tuple) and len(item) == 2:
                    if isinstance(item[1], bytes) and len(item[1]) > 0:
                        raw_email = item[1]
                        break
            
            if not raw_email:
                print("   错误: 无法获取原始邮件内容")
                return
                
            msg = email_module.message_from_bytes(raw_email)
            
            # 确保临时目录存在
            os.makedirs("/tmp/attachments", exist_ok=True)
            
            # 提取附件数据
            attachment_data = None
            for part in msg.walk():
                filename = part.get_filename()
                if filename == test_attachment.filename:
                    attachment_data = part.get_payload(decode=True)
                    print(f"   找到附件: {filename}")
                    break
            
            if attachment_data:
                # 保存附件
                file_backend = FileBackend(
                    email_export_path=None,
                    attachment_download_path="./"
                )
                
                saved_path = file_backend.save_attachment(attachment_data, test_attachment.filename)
                print(f"   下载成功: {saved_path}")
                
                # 验证文件是否存在并显示文件信息
                if os.path.exists(saved_path):
                    file_size = os.path.getsize(saved_path)
                    print(f"   文件大小: {file_size} bytes")
                    print(f"   原始大小: {test_attachment.size} bytes")
                else:
                    print("   警告: 文件保存路径不存在")
            else:
                print("   错误: 无法提取附件数据")
                # 调试信息：显示所有部分的文件名
                print("   调试：邮件中的所有文件名:")
                for part in msg.walk():
                    filename = part.get_filename()
                    if filename:
                        print(f"     - {filename}")
            
        except Exception as e:
            print(f"   下载失败: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_attachment_download()