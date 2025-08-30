"""
@Time   :  17:20
@Author : JFS
@File   : cli.py
"""
from .core import serve

def main():
    import asyncio
    asyncio.run(serve())