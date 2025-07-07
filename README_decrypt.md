# 文件解密工具

这个工具包用于解密通过 `comfyui-encrypt-image` 插件加密的图片文件。

## 文件说明

- `decrypt_file.py` - 单个文件解密工具
- `batch_decrypt.py` - 批量文件解密工具

## 安装依赖

```bash
pip install pillow numpy
```

## 使用方法

### 1. 单个文件解密

```bash
# 使用默认密码 'Bilt8'
python decrypt_file.py encrypted_image.png

# 使用自定义密码
python decrypt_file.py encrypted_image.png mypassword
```

### 2. 批量文件解密

```bash
# 解密目录中的所有图片文件
python batch_decrypt.py ./encrypted_images/

# 使用自定义密码批量解密
python batch_decrypt.py ./encrypted_images/ mypassword
```

## 功能特性

- 支持 PNG 和 WEBP 格式的加密图片
- 支持 v1 和 v2 加密算法
- 支持 WEBP 动画解密
- 自动检测加密类型
- 批量处理功能
- 详细的处理日志

## 输出文件

解密后的文件会保存在原文件同目录下，文件名前缀为 `decrypted_`。

例如：
- 原文件：`image.png`
- 解密后：`decrypted_image.png`

## 支持的加密类型

- `pixel_shuffle` - v1 加密算法
- `pixel_shuffle_2` - v2 加密算法

## 错误处理

- 如果文件不是加密的图片，会显示警告信息
- 如果密码错误，解密会失败
- 如果文件损坏，会显示错误信息

## 示例输出

```
文件路径: encrypted_image.png
使用密码: Bilt8
--------------------------------------------------
正在处理文件: encrypted_image.png
图片格式: PNG
图片尺寸: (512, 512)
检测到加密类型: pixel_shuffle_2
使用v2解密算法...
解密成功! 输出文件: decrypted_encrypted_image.png
解密完成!
```

## 注意事项

1. 确保有足够的磁盘空间存储解密后的文件
2. 原始加密文件不会被修改
3. 如果输出文件已存在，会被覆盖
4. 默认密码是 'Bilt8'，如果使用其他密码请指定 