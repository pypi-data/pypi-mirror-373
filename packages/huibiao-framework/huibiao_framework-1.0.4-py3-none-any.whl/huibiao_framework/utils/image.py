import base64

import aiofiles


class ImageUtils:
    @classmethod
    async def encode_base64(cls, image_path) -> str:
        """
        异步读取图片文件并转换为Base64编码字符串（urlsafe格式）

        参数:
            image_path: 图片文件的路径

        返回:
            编码后的Base64字符串
        """
        # 使用aiofiles进行异步文件读取
        async with aiofiles.open(image_path, "rb") as f:
            # 异步读取文件内容
            file_content = await f.read()

        # 进行url安全的Base64编码并转换为字符串
        encoded_bytes = base64.urlsafe_b64encode(file_content)
        encoded_string = encoded_bytes.decode("utf-8")

        return encoded_string
