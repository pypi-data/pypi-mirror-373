"""
@Time   :  17:20
@Author : JFS
@File   : __main__.py.py
"""
from .core import serve

if __name__ == "__main__":
    import asyncio
    asyncio.run(serve())