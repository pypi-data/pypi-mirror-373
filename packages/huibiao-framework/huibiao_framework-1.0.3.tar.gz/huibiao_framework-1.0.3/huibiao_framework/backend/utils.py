from fastapi import Header


async def get_request_id(x_request_id: str = Header(..., alias="x-request-id")):
    return x_request_id
