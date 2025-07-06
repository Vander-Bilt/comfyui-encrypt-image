
This is a ComfyUI image encryption extension that will encrypt all images generated in ComfyUI for storage and decrypt them for preview.

---

## Usage Instructions

- In the `custom_nodes` folder:

  `git clone https://github.com/Vander-Bilt/comfyui-encrypt-image.git`

- After image encryption, the images will be in RGBA mode. To ensure correct decryption during preview, you need to modify the `view_image` method in the `server.py` file of your ComfyUI project:

  Change from:

  `if channel == 'rgb':`

  To:

  `if channel == 'rgb' or channel == 'rgba':`

- Default password: `Bilt8`. You can modify it by adding an EncryptImage node in the ComfyUI interface.


<br><br><br>

这是一个comfyUI的图片加密扩展，将会对comfyUI中生成的所有图片进行加密储存、解密预览。

## 使用说明

- 在custom_nodes文件夹中：

  `git clone https://github.com/Vander-Bilt/comfyui-encrypt-image.git`

- 图片加密存储后，为rgba模式，为了确保预览时正确的解密，需要对comfyUI项目中的`server.py`文件`view_image`方法进行修改：

  从
  
  `if channel == 'rgb':`
  
  修改为:
  
  `if channel == 'rgb' or channel == 'rgba':`
  

- 默认密码: `Bilt8`。可以在comfyUI界面添加EncryptImage节点，进行修改。
