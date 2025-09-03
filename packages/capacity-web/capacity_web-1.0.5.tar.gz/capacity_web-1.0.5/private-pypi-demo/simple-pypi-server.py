#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最简单的私有 PyPI 服务器演示
运行: python simple-pypi-server.py
"""

# /// script
# dependencies = ["pypiserver>=1.5.0", "passlib>=1.7.0"]
# ///

import os
import subprocess
import sys
from pathlib import Path

def setup_private_pypi():
    """设置私有 PyPI 服务器"""
    
    # 创建包存储目录
    packages_dir = Path("./pypi-packages")
    packages_dir.mkdir(exist_ok=True)
    
    # 创建密码文件 (可选)
    htpasswd_file = Path("./htpasswd")
    if not htpasswd_file.exists():
        print("🔐 创建用户认证...")
        # 创建用户: admin/admin123
        subprocess.run([
            "htpasswd", "-cb", str(htpasswd_file), "admin", "admin123"
        ], check=True)
    
    print("🎉 启动私有 PyPI 服务器...")
    print("📦 包存储目录:", packages_dir.absolute())
    print("🔐 认证文件:", htpasswd_file.absolute() if htpasswd_file.exists() else "无认证")
    print("🌐 Web界面: http://localhost:8080")
    print("📋 API地址: http://localhost:8080/simple/")
    print("👤 用户名/密码: admin/admin123")
    print("\n按 Ctrl+C 停止服务器\n")
    
    # 启动服务器
    cmd = [
        "pypi-server", 
        "-p", "8080",                    # 端口
        "-P", str(htpasswd_file) if htpasswd_file.exists() else ".",  # 密码文件
        "-a", str(htpasswd_file) if htpasswd_file.exists() else ".",  # 上传认证
        str(packages_dir)                # 包存储目录
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except FileNotFoundError:
        print("❌ 请先安装 pypiserver: pip install pypiserver")
        print("💡 或者运行: uv run simple-pypi-server.py")

if __name__ == "__main__":
    setup_private_pypi()
