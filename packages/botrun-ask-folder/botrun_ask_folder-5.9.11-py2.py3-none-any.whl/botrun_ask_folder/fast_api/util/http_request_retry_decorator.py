import asyncio
from functools import wraps


def async_retry(attempts=3, delay=1):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == attempts - 1:
                        raise
                    print(f"Attempt {attempt + 1} failed: {str(e)}. Retrying...")
                    await asyncio.sleep(delay * (2**attempt))  # 指數退避

        return wrapper

    return decorator
