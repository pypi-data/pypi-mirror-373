"""
RandGen - Smart Random Data Generator

A command-line tool for generating realistic random test data.
"""

__version__ = "0.1.0"
__author__ = "jikefeng"
__email__ = "1412414664@qq.com"

# 可选：导出主要功能，方便用户导入
from .generator import DataGenerator
from .cli import main

__all__ = ['DataGenerator', 'main']