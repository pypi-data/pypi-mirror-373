"""
VW2PX - Конвертер размеров из VW в PX
Конвертер размеров из VW в PX для проектов Vue, React, Next.js и других веб-проектов
"""

__version__ = "1.0.0"
__author__ = "Bluesuma"
__email__ = "v1tuze@yandex.ru"

from .converter import VWToPXConverter, main

__all__ = ["VWToPXConverter", "main"]
