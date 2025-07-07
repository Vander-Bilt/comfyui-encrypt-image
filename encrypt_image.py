import base64
import io
import json
import os
from pathlib import Path
from urllib.parse import unquote
from .core.core import get_sha256,dencrypt_image,dencrypt_image_v2,encrypt_image_v2
from PIL import PngImagePlugin,_util,ImagePalette
from PIL import Image as PILImage
from io import BytesIO
from typing import Optional
import sys
import folder_paths
from comfy.cli_args import args

from PIL import Image
from PIL.PngImagePlugin import PngInfo

import numpy as np

_password = 'Bilt8'

            
if PILImage.Image.__name__ != 'EncryptedImage':
    
    super_open = PILImage.open
    
    class EncryptedImage(PILImage.Image):
        __name__ = "EncryptedImage"
        @staticmethod
        def from_image(image:PILImage.Image):
            print("from_image handled in EncryptedImage")
            image = image.copy()
            img = EncryptedImage()
            img.im = image.im
            img._mode = image.im.mode
            if image.im.mode:
                try:
                    img.mode = image.im.mode
                except Exception as e:
                    ''
            img._size = image.size
            img.format = image.format
            if image.mode in ("P", "PA"):
                if image.palette:
                    img.palette = image.palette.copy()
                else:
                    img.palette = ImagePalette.ImagePalette()
            img.info = image.info.copy()
            return img
            
        def save(self, fp, format=None, **params):
            filename = ""
            if isinstance(fp, Path):
                filename = str(fp)
            elif _util.is_path(fp):
                filename = fp
            elif fp == sys.stdout:
                try:
                    fp = sys.stdout.buffer
                except AttributeError:
                    pass
            if not filename and hasattr(fp, "name") and _util.is_path(fp.name):
                # only set the name for metadata purposes
                filename = fp.name
            
            if not filename or not _password:
                # 如果没有密码或不保存到硬盘，直接保存
                super().save(fp, format = format, **params)
                return
            
            if 'Encrypt' in self.info and (self.info['Encrypt'] == 'pixel_shuffle' or self.info['Encrypt'] == 'pixel_shuffle_2'):
                super().save(fp, format = format, **params)
                return
            
            
            encrypt_image_v2(self, get_sha256(_password))
            self.format = PngImagePlugin.PngImageFile.format
            pnginfo = params.get('pnginfo', PngImagePlugin.PngInfo())
            if not pnginfo:
                pnginfo = PngImagePlugin.PngInfo()
                for key in (self.info or {}).keys():
                    if self.info[key]:
                        pnginfo.add_text(key,str(self.info[key]))
            pnginfo.add_text('Encrypt', 'pixel_shuffle_2')
            pnginfo.add_text('EncryptPwdSha', get_sha256(f'{get_sha256(_password)}Encrypt'))
            params.update(pnginfo=pnginfo)
            super().save(fp, format=self.format, **params)
            print("save handled in EncryptedImage")
            # 保存到文件后解密内存内的图片，让直接在内存内使用时图片正常
            dencrypt_image_v2(self, get_sha256(_password)) 
            
    def open(fp,*args, **kwargs):
        try:
            image = super_open(fp,*args, **kwargs)
        except Exception as e:
            # 如果文件不是图片或无法识别，可以选择以下处理方式：
            # 1. 记录警告并重新抛出异常（当前行为）
            # 2. 记录警告并返回一个默认的空图像
            # 3. 静默忽略错误
            
            # 当前实现：记录警告并重新抛出异常
            # print(f"Warning: Failed to open file as image: {fp}, error: {e}")
            # raise e
            
            # 可选实现1：返回一个1x1的透明图像
            # print(f"Warning: Failed to open file as image: {fp}, error: {e}")
            # return EncryptedImage.from_image(PILImage.new('RGBA', (1, 1), (0, 0, 0, 0)))
            
            # 可选实现2：静默忽略错误
            # print(f"Warning: Failed to open file as image: {fp}, error: {e}")
            return None

        print("open Handled in EncryptedImage")

        if _password and image.format.lower() == PngImagePlugin.PngImageFile.format.lower():
            pnginfo = image.info or {}
            if 'Encrypt' in pnginfo and pnginfo["Encrypt"] == 'pixel_shuffle':
                dencrypt_image(image, get_sha256(_password))
                pnginfo["Encrypt"] = None
                image = EncryptedImage.from_image(image=image)
                return image
            if 'Encrypt' in pnginfo and pnginfo["Encrypt"] == 'pixel_shuffle_2':
                dencrypt_image_v2(image, get_sha256(_password))
                pnginfo["Encrypt"] = None
                image = EncryptedImage.from_image(image=image)
                return image

        return EncryptedImage.from_image(image=image)

    # if _password:
    PILImage.Image = EncryptedImage
    PILImage.open = open
    
    print('图片加密插件加载成功')

# 这是一个节点，用于设置密码，即使不设置，也有默认密码 123qwe
class EncryptImage:
    def __init__(self):
        self.output_dir = os.path.join(folder_paths.get_output_directory(),'encryptd')
        self.type = "output"
        self.prefix_append = ""
        self.compress_level = 4
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "password":  ("STRING", {"default": "Bilt8"}),
                "filename_prefix": ("STRING", {"default": "ComfyUI"}),
                },
        "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }
        
    RETURN_TYPES = ()
    FUNCTION = 'set_password'
    
    OUTPUT_NODE = True

    CATEGORY = "utils"
    
    def set_password(self,images,password,filename_prefix="ComfyUI", prompt=None, extra_pnginfo=None):
        global _password
        _password = password
        filename_prefix += self.prefix_append
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0])
        results = list()
        for image in images:
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            metadata = None
            if not args.disable_metadata:
                metadata = PngInfo()
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))

            file = f"{filename}_{counter:05}_.png"
            img.save(os.path.join(full_output_folder, file), pnginfo=metadata, compress_level=self.compress_level)
            results.append({
                "filename": file,
                "subfolder": os.path.join('encryptd',subfolder),
                "type": self.type,
                'channel':'rgb'
            })
            counter += 1

        return { "ui": { "images": results} }
    
NODE_CLASS_MAPPINGS = {
    "EncryptImage": EncryptImage
}