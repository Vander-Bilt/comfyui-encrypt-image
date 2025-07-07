#!/usr/bin/env python3
"""
批量文件解密工具
用于批量解密通过comfyui-encrypt-image插件加密的图片文件

使用方法:
    python batch_decrypt.py <目录路径> [密码]

参数:
    目录路径: 包含加密图片的目录路径
    密码: 解密密码 (可选，默认为 'Bilt8')

示例:
    python batch_decrypt.py ./encrypted_images/
    python batch_decrypt.py ./encrypted_images/ mypassword
"""

import sys
import os
import glob
from pathlib import Path
from decrypt_file import decrypt_file


def batch_decrypt(directory: str, password: str = 'Bilt8') -> dict:
    """
    批量解密目录中的图片文件
    
    Args:
        directory: 目录路径
        password: 解密密码
        
    Returns:
        dict: 解密结果统计
    """
    if not os.path.exists(directory):
        print(f"错误: 目录不存在 - {directory}")
        return {"success": 0, "failed": 0, "skipped": 0}
    
    # 支持的图片格式
    image_extensions = ['*.png', '*.webp', '*.jpg', '*.jpeg']
    
    # 查找所有图片文件
    image_files = []
    for ext in image_extensions:
        pattern = os.path.join(directory, ext)
        image_files.extend(glob.glob(pattern))
        # 也查找子目录
        pattern = os.path.join(directory, '**', ext)
        image_files.extend(glob.glob(pattern, recursive=True))
    
    if not image_files:
        print(f"在目录 {directory} 中未找到图片文件")
        return {"success": 0, "failed": 0, "skipped": 0}
    
    print(f"找到 {len(image_files)} 个图片文件")
    print("-" * 50)
    
    results = {"success": 0, "failed": 0, "skipped": 0}
    
    for i, file_path in enumerate(image_files, 1):
        print(f"[{i}/{len(image_files)}] 处理: {file_path}")
        
        try:
            success = decrypt_file(file_path, password)
            if success:
                results["success"] += 1
                print(f"✓ 解密成功")
            else:
                results["failed"] += 1
                print(f"✗ 解密失败")
        except Exception as e:
            results["failed"] += 1
            print(f"✗ 处理失败: {e}")
        
        print()
    
    return results


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    directory = sys.argv[1]
    password = sys.argv[2] if len(sys.argv) > 2 else 'Bilt8'
    
    print(f"目录路径: {directory}")
    print(f"使用密码: {password}")
    print("-" * 50)
    
    results = batch_decrypt(directory, password)
    
    print("=" * 50)
    print("批量解密完成!")
    print(f"成功: {results['success']}")
    print(f"失败: {results['failed']}")
    print(f"跳过: {results['skipped']}")
    
    if results['failed'] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main() 