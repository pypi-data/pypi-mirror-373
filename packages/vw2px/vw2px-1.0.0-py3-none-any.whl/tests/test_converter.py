#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import tempfile
import os
from pathlib import Path
from vw2px.converter import VWToPXConverter


class TestVWToPXConverter:
    def setup_method(self):
        self.converter = VWToPXConverter(1920)
    
    def test_convert_vw_to_px(self):
        """Тест конвертации VW в PX"""
        assert self.converter.convert_vw_to_px("1") == 19.2
        assert self.converter.convert_vw_to_px("10") == 192.0
        assert self.converter.convert_vw_to_px("50") == 960.0
        assert self.converter.convert_vw_to_px("100") == 1920.0
        assert self.converter.convert_vw_to_px("5.5") == 105.6
    
    def test_convert_vw_to_px_different_viewport(self):
        """Тест конвертации с разным viewport"""
        converter_1440 = VWToPXConverter(1440)
        assert converter_1440.convert_vw_to_px("1") == 14.4
        assert converter_1440.convert_vw_to_px("10") == 144.0
        assert converter_1440.convert_vw_to_px("50") == 720.0
    
    def test_find_vw_values(self):
        """Тест поиска VW значений в файле"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.css', delete=False) as f:
            f.write("""
            .test {
                width: 10vw;
                height: 5.5vw;
                margin: 1vw 2vw;
            }
            """)
            temp_file = f.name
        
        try:
            results = self.converter.find_vw_values(temp_file)
            assert len(results) == 4
            vw_values = [result[3] for result in results]
            assert "10" in vw_values
            assert "5.5" in vw_values
            assert "1" in vw_values
            assert "2" in vw_values
        finally:
            os.unlink(temp_file)
    
    def test_replace_vw_in_file(self):
        """Тест замены VW значений в файле"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.css', delete=False) as f:
            f.write("""
            .test {
                width: 10vw;
                height: 5.5vw;
            }
            """)
            temp_file = f.name
        
        try:
            replacements = [
                ("10", "192.0", 3),
                ("5.5", "105.6", 4)
            ]
            
            success = self.converter.replace_vw_in_file(temp_file, replacements)
            assert success
            
            with open(temp_file, 'r') as f:
                content = f.read()
                assert "192.0px" in content
                assert "105.6px" in content
                assert "10vw" not in content
                assert "5.5vw" not in content
        finally:
            os.unlink(temp_file)
    
    def test_multiple_vw_on_same_line(self):
        """Тест множественных VW значений на одной строке"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.vue', delete=False) as f:
            f.write('''
            <div class="w-[1.563vw] h-[1.563vw] top-[1.563vw] right-[1.563vw] rounded-[1.563vw]">
            </div>
            ''')
            temp_file = f.name
        
        try:
            results = self.converter.find_vw_values(temp_file)
            assert len(results) == 5  # 5 значений 1.563vw
            
            # Проверяем, что все значения одинаковые
            vw_values = [result[3] for result in results]
            assert all(v == "1.563" for v in vw_values)
            
            # Тестируем замену
            replacements = [(result[3], "30.01", result[2]) for result in results]
            success = self.converter.replace_vw_in_file(temp_file, replacements)
            assert success
            
            with open(temp_file, 'r') as f:
                content = f.read()
                assert content.count("30.01px") == 5
                assert "1.563vw" not in content
        finally:
            os.unlink(temp_file)
    
    def test_invalid_vw_value(self):
        """Тест обработки некорректных VW значений"""
        assert self.converter.convert_vw_to_px("invalid") == 0.0
        assert self.converter.convert_vw_to_px("") == 0.0
    
    def test_excluded_directories(self):
        """Тест исключения директорий"""
        # Создаем временную структуру с исключаемыми директориями
        with tempfile.TemporaryDirectory() as temp_dir:
            # Создаем node_modules директорию
            node_modules_dir = os.path.join(temp_dir, "node_modules")
            os.makedirs(node_modules_dir)
            
            # Создаем файл в node_modules
            with open(os.path.join(node_modules_dir, "test.css"), 'w') as f:
                f.write(".test { width: 10vw; }")
            
            # Создаем обычный файл
            with open(os.path.join(temp_dir, "test.css"), 'w') as f:
                f.write(".test { width: 10vw; }")
            
            results = self.converter.find_vw_values(temp_dir)
            # Должен найти только один файл (не в node_modules)
            assert len(results) == 1
