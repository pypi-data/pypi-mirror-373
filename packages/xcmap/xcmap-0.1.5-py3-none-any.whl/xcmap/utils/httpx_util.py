import httpx


# 自定义异常
class UnauthorizedError(Exception):
    """自定义异常：表示 401 Unauthorized 错误"""
    pass


async def post_data(url, data, headers=None):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:  # 捕获 401 错误
                raise UnauthorizedError("Unauthorized: Token may be expired")
            raise SystemError(f'HTTP error: {e}')
        except httpx.HTTPError as e:
            raise SystemError(f'Network error: {e}')
        except ValueError as e:
            raise SystemError(f'JSON parsing error: {e}')
        except Exception as e:
            raise SystemError(f'Unexpected error: {e}')
