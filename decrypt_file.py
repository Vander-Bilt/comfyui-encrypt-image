#!/usr/bin/env python3
"""
文件解密工具
用于解密通过comfyui-encrypt-image插件加密的图片文件

使用方法:
    python decrypt_file.py <文件路径> [密码]

参数:
    文件路径: 要解密的图片文件路径
    密码: 解密密码 (可选，默认为 'Bilt8')

示例:
    python decrypt_file.py encrypted_image.png
    python decrypt_file.py encrypted_image.png mypassword
"""

import sys
import os
import hashlib
import numpy as np
from PIL import Image, PngImagePlugin
from io import BytesIO
from pathlib import Path


def get_range(input_str: str, offset: int, range_len=4):
    """获取字符串的指定范围"""
    offset = offset % len(input_str)
    return (input_str * 2)[offset:offset + range_len]


def get_sha256(input_str: str):
    """计算字符串的SHA256哈希值"""
    hash_object = hashlib.sha256()
    hash_object.update(input_str.encode('utf-8'))
    return hash_object.hexdigest()


def shuffle_arr(arr, key):
    """根据密钥打乱数组"""
    sha_key = get_sha256(key)
    key_len = len(sha_key)
    arr_len = len(arr)
    key_offset = 0
    for i in range(arr_len):
        to_index = int(get_range(sha_key, key_offset, range_len=8), 16) % (arr_len - i)
        key_offset += 1
        if key_offset >= key_len:
            key_offset = 0
        arr[i], arr[to_index] = arr[to_index], arr[i]
    return arr


def dencrypt_image(image: Image.Image, psw):
    """解密图片 (v1版本)"""
    width = image.width
    height = image.height
    x_arr = [i for i in range(width)]
    shuffle_arr(x_arr, psw)
    y_arr = [i for i in range(height)]
    shuffle_arr(y_arr, get_sha256(psw))
    pixels = image.load()
    for x in range(width - 1, -1, -1):
        _x = x_arr[x]
        for y in range(height - 1, -1, -1):
            _y = y_arr[y]
            pixels[x, y], pixels[_x, _y] = pixels[_x, _y], pixels[x, y]


def dencrypt_image_v2(image: Image.Image, psw):
    """解密图片 (v2版本)"""
    width = image.width
    height = image.height
    x_arr = [i for i in range(width)]
    shuffle_arr(x_arr, psw)
    y_arr = [i for i in range(height)]
    shuffle_arr(y_arr, get_sha256(psw))
    pixel_array = np.array(image)

    pixel_array = np.transpose(pixel_array, axes=(1, 0, 2))
    for x in range(width - 1, -1, -1):
        _x = x_arr[x]
        temp = pixel_array[x].copy()
        pixel_array[x] = pixel_array[_x]
        pixel_array[_x] = temp
    pixel_array = np.transpose(pixel_array, axes=(1, 0, 2))
    for y in range(height - 1, -1, -1):
        _y = y_arr[y]
        temp = pixel_array[y].copy()
        pixel_array[y] = pixel_array[_y]
        pixel_array[_y] = temp

    image.paste(Image.fromarray(pixel_array))
    return image


def decrypt_file(file_path: str, password: str = 'Bilt8') -> bool:
    """
    解密文件
    
    Args:
        file_path: 文件路径
        password: 解密密码
        
    Returns:
        bool: 解密是否成功
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"错误: 文件不存在 - {file_path}")
            return False
        
        # 打开图片
        image = Image.open(file_path)
        print(f"正在处理文件: {file_path}")
        print(f"图片格式: {image.format}")
        print(f"图片尺寸: {image.size}")
        
        # 检查是否为加密的图片
        pnginfo = image.info or {}
        is_encrypted = False
        encryption_type = None
        
        # 检查PNG格式的加密信息
        if image.format and image.format.lower() == 'png':
            if 'Encrypt' in pnginfo:
                encryption_type = pnginfo['Encrypt']
                is_encrypted = True
                print(f"检测到加密类型: {encryption_type}")
        
        # 检查WEBP格式的加密信息
        elif image.format and image.format.lower() == 'webp':
            if 'encrypt' in pnginfo:
                encryption_type = pnginfo['encrypt']
                is_encrypted = True
                print(f"检测到加密类型: {encryption_type}")
        
        if not is_encrypted:
            print("警告: 该文件不是加密的图片文件")
            return False
        
        # 根据加密类型进行解密
        if encryption_type == 'pixel_shuffle':
            print("使用v1解密算法...")
            dencrypt_image(image, get_sha256(password))
            pnginfo["Encrypt"] = None
        elif encryption_type == 'pixel_shuffle_2':
            print("使用v2解密算法...")
            dencrypt_image_v2(image, get_sha256(password))
            pnginfo["Encrypt"] = None
        else:
            print(f"未知的加密类型: {encryption_type}")
            return False
        
        # 生成输出文件名
        input_path = Path(file_path)
        output_path = input_path.parent / f"decrypted_{input_path.name}"
        
        # 保存解密后的图片
        if image.format and image.format.lower() == 'webp':
            # 处理WEBP动画
            if hasattr(image, 'n_frames') and image.n_frames > 1:
                print("处理WEBP动画...")
                decrypted_frames = []
                for i in range(image.n_frames):
                    image.seek(i)
                    frame = image.copy()
                    dencrypt_image_v2(frame, get_sha256(password))
                    decrypted_frames.append(frame)
                
                output = BytesIO()
                decrypted_frames[0].save(output, format='WEBP', save_all=True, 
                                       append_images=decrypted_frames[1:], 
                                       quality=100, lossless=True, minimize_size=False)
                output.seek(0)
                
                # 保存解密后的动画
                with open(output_path, 'wb') as f:
                    f.write(output.getvalue())
            else:
                # 处理单帧WEBP
                image.save(output_path, format='WEBP', quality=100, lossless=True)
        else:
            # 处理PNG等其他格式
            image.save(output_path, format=image.format)
        
        print(f"解密成功! 输出文件: {output_path}")
        return True
        
    except Exception as e:
        print(f"解密失败: {e}")
        return False


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    file_path = sys.argv[1]
    password = sys.argv[2] if len(sys.argv) > 2 else 'Bilt8'
    
    print(f"文件路径: {file_path}")
    print(f"使用密码: {password}")
    print("-" * 50)
    
    success = decrypt_file(file_path, password)
    
    if success:
        print("解密完成!")
    else:
        print("解密失败!")
        sys.exit(1)


if __name__ == "__main__":
    main() 