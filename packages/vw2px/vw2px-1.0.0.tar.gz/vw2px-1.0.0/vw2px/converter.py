#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VW2PX - Конвертер размеров из VW в PX
Конвертер размеров из VW в PX для проектов Vue, React, Next.js и других
"""

__version__ = "1.0.0"

import os
import re
import click
from pathlib import Path
from colorama import init, Fore, Style
from typing import List, Tuple, Dict

# Инициализация colorama для цветного вывода
init(autoreset=True)

class VWToPXConverter:
    def __init__(self, viewport_width: int):
        self.viewport_width = viewport_width
        self.vw_pattern = re.compile(r'(\d+(?:\.\d+)?)vw', re.IGNORECASE)
        self.px_pattern = re.compile(r'(\d+(?:\.\d+)?)px', re.IGNORECASE)
        
        # Расширения файлов для поиска
        self.supported_extensions = {
            '.js', '.jsx', '.ts', '.tsx', '.vue', '.html', '.css', '.scss', 
            '.sass', '.less', '.styl', '.json', '.md', '.txt'
        }
        
        # Исключаемые директории
        self.exclude_dirs = {
            'node_modules', '.git', '.next', 'dist', 'build', 
            '.nuxt', '.cache', 'coverage', '.vscode', '.idea'
        }
    
    def find_vw_values(self, project_path: str) -> List[Tuple[str, str, int, str]]:
        """
        Находит все VW значения в проекте
        
        Returns:
            List[Tuple[file_path, line_content, line_number, vw_value]]
        """
        results = []
        project_path = Path(project_path)
        
        if not project_path.exists():
            click.echo(f"{Fore.RED}Ошибка: Путь {project_path} не существует!")
            return results
        
        click.echo(f"{Fore.CYAN}🔍 Поиск VW значений в проекте: {project_path}")
        
        for file_path in project_path.rglob('*'):
            if file_path.is_file():
                # Пропускаем исключаемые директории
                if any(exclude_dir in file_path.parts for exclude_dir in self.exclude_dirs):
                    continue
                
                # Проверяем расширение файла
                if file_path.suffix.lower() not in self.supported_extensions:
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            matches = self.vw_pattern.findall(line)
                            for match in matches:
                                results.append((
                                    str(file_path),
                                    line.strip(),
                                    line_num,
                                    match
                                ))
                except Exception as e:
                    click.echo(f"{Fore.YELLOW}⚠️  Не удалось прочитать файл {file_path}: {e}")
        
        return results
    
    def convert_vw_to_px(self, vw_value: str) -> float:
        """
        Конвертирует VW значение в PX
        
        Args:
            vw_value: VW значение (например, "10.5")
            
        Returns:
            float: PX значение
        """
        try:
            vw_float = float(vw_value)
            px_value = (vw_float * self.viewport_width) / 100
            return round(px_value, 2)
        except ValueError:
            return 0.0
    
    def replace_vw_in_file(self, file_path: str, replacements: List[Tuple[str, str, int]]) -> bool:
        """
        Заменяет VW значения на PX в файле
        
        Args:
            file_path: Путь к файлу
            replacements: Список замен [(старое_значение, новое_значение, номер_строки)]
            
        Returns:
            bool: True если замена прошла успешно
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Группируем замены по строкам
            line_replacements = {}
            for old_value, new_value, line_num in replacements:
                if line_num not in line_replacements:
                    line_replacements[line_num] = []
                line_replacements[line_num].append((old_value, new_value))
            
            # Обрабатываем каждую строку
            for line_num, line_reps in line_replacements.items():
                if 0 < line_num <= len(lines):
                    line = lines[line_num - 1]
                    
                    # Сортируем замены по длине (от длинных к коротким), чтобы избежать проблем с частичными совпадениями
                    line_reps.sort(key=lambda x: len(x[0]), reverse=True)
                    
                    # Выполняем замены в строке
                    for old_value, new_value in line_reps:
                        # Используем точное совпадение для замены
                        pattern = re.compile(rf'\b{re.escape(old_value)}vw\b', re.IGNORECASE)
                        line = pattern.sub(f'{new_value}px', line)
                    
                    lines[line_num - 1] = line
            
            # Записываем изменения обратно в файл
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            return True
            
        except Exception as e:
            click.echo(f"{Fore.RED}❌ Ошибка при замене в файле {file_path}: {e}")
            return False
    
    def process_project(self, project_path: str, dry_run: bool = False) -> Dict[str, int]:
        """
        Обрабатывает весь проект
        
        Args:
            project_path: Путь к проекту
            dry_run: Если True, только показывает что будет изменено
            
        Returns:
            Dict[str, int]: Статистика обработки
        """
        stats = {
            'files_processed': 0,
            'replacements_made': 0,
            'errors': 0
        }
        
        # Находим все VW значения
        vw_values = self.find_vw_values(project_path)
        
        if not vw_values:
            click.echo(f"{Fore.YELLOW}📭 VW значения не найдены в проекте!")
            return stats
        
        click.echo(f"{Fore.GREEN}✅ Найдено {len(vw_values)} VW значений")
        
        # Группируем замены по файлам
        file_replacements = {}
        for file_path, line_content, line_num, vw_value in vw_values:
            if file_path not in file_replacements:
                file_replacements[file_path] = []
            
            px_value = self.convert_vw_to_px(vw_value)
            file_replacements[file_path].append((vw_value, px_value, line_num))
            
            # Показываем информацию о замене
            status = f"{Fore.YELLOW}[ПРЕДПРОСМОТР]" if dry_run else f"{Fore.GREEN}[ЗАМЕНА]"
            click.echo(f"{status} {file_path}:{line_num} | {vw_value}vw → {px_value}px")
        
        if dry_run:
            click.echo(f"\n{Fore.CYAN}📋 Предварительный просмотр завершен. Найдено {len(vw_values)} замен в {len(file_replacements)} файлах.")
            return stats
        
        # Выполняем замены
        click.echo(f"\n{Fore.CYAN}🔄 Выполняем замены...")
        
        for file_path, replacements in file_replacements.items():
            if self.replace_vw_in_file(file_path, replacements):
                stats['files_processed'] += 1
                stats['replacements_made'] += len(replacements)
                click.echo(f"{Fore.GREEN}✅ Обработан файл: {file_path}")
            else:
                stats['errors'] += 1
        
        return stats

@click.command()
@click.option('--path', '-p', required=True, help='Путь к проекту')
@click.option('--viewport', '-v', default=1920, type=int, 
              help='Ширина viewport для конвертации (по умолчанию: 1920)')
@click.option('--dry-run', '-d', is_flag=True, 
              help='Только показать что будет изменено, без внесения изменений')
@click.option('--type', '-t', default='vw-to-px', 
              type=click.Choice(['vw-to-px', 'px-to-vw']), 
              help='Тип конвертации (пока поддерживается только vw-to-px)')
def main(path: str, viewport: int, dry_run: bool, type: str):
    """
    vw2px Converter - Конвертер размеров для веб-проектов
    
    Поддерживаемые типы конвертации:
    - vw-to-px: Конвертация из VW в PX
    - px-to-vw: Конвертация из PX в VW (пока не реализовано)
    """
    click.echo(f"{Fore.CYAN}🚀 VW2PX - Конвертер VW в PX")
    click.echo(f"{Fore.CYAN}=" * 50)
    click.echo(f"📁 Проект: {path}")
    click.echo(f"🖥️  Viewport: {viewport}px")
    click.echo(f"🔄 Тип конвертации: {type}")
    click.echo(f"🔍 Режим: {'Предварительный просмотр' if dry_run else 'Выполнение замен'}")
    click.echo(f"{Fore.CYAN}=" * 50)
    
    if type == 'px-to-vw':
        click.echo(f"{Fore.YELLOW}⚠️  Конвертация PX в VW пока не реализована!")
        return
    
    # Создаем конвертер
    converter = VWToPXConverter(viewport)
    
    # Обрабатываем проект
    stats = converter.process_project(path, dry_run)
    
    # Выводим статистику
    click.echo(f"\n{Fore.CYAN}📊 Статистика:")
    click.echo(f"   📁 Файлов обработано: {stats['files_processed']}")
    click.echo(f"   🔄 Замен выполнено: {stats['replacements_made']}")
    if stats['errors'] > 0:
        click.echo(f"   ❌ Ошибок: {stats['errors']}")
    
    if not dry_run and stats['replacements_made'] > 0:
        click.echo(f"\n{Fore.GREEN}🎉 Конвертация завершена успешно!")
    elif dry_run:
        click.echo(f"\n{Fore.YELLOW}💡 Для выполнения замен запустите команду без флага --dry-run")

if __name__ == '__main__':
    main()
