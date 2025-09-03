import aiohttp
import asyncio

from huibiao_framework.client.data_model.vllm import HuizeQwen32bAwqVo
from huibiao_framework.client.llm.huize_qwen32b_awq_client import HuiZeQwen32bQwqClient


async def main():
    async with aiohttp.ClientSession() as session:
        client = HuiZeQwen32bQwqClient(session)
        resp1: HuizeQwen32bAwqVo = await client.query("今天天气如何")
        return resp1.result.Output


async def test():
    """
    并行
    """
    result = await asyncio.gather(*[main(), main(), main()])
    print(result)


if __name__ == "__main__":
    asyncio.run(test())
