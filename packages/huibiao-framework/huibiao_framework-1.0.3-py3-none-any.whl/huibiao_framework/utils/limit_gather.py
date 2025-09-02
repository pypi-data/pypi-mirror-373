import asyncio
import time
from collections.abc import Coroutine
from typing import List, Optional

from loguru import logger


async def limit_batch_gather(task: List[Coroutine], *, batch: int = 4, log_tag: Optional[str] = ""):
    """
    将task列表按照batch尺寸拆开，串行执行每个batch
    返回结果的顺序和输入任务的顺序对应
    使用示例
    async def mytask(idx: int):
        await asyncio.sleep(1)
        logger.info(f"mytask done {idx}")
        return idx

    async def main():
        all_result = await limit_batch_gather([mytask(idx) for idx in range(34)], batch=5, log_tag=None)
        logger.info(all_result)

    asyncio.run(main())
    """
    log_tag = log_tag + " " if log_tag else ""

    batch_list = [task[i : i + batch] for i in range(0, len(task), batch)]
    batch_result = []
    start_time = time.perf_counter()
    logger.debug(f"{log_tag}Batch task start, total {len(task)} task")
    for idx, b_task in enumerate(batch_list):
        b_start_time = time.perf_counter()
        batch_result.append(await asyncio.gather(*b_task))
        logger.debug(f"{log_tag}[{idx + 1}/{len(batch_list)}]-[{len(b_task)}] Batch task done, "
                     f"cost={time.perf_counter() - b_start_time:.6f}s")

    logger.debug(f"{log_tag}All batch task done, cost={time.perf_counter() - start_time:.6f}")
    # 结果合并，保留原顺序
    result = [item for sublist in batch_result for item in sublist]

    return result