#!/bin/bash

# VW2PX - Скрипт для быстрого запуска
# Использование: ./run_converter.sh [путь_к_проекту] [viewport] [dry_run]

echo "🚀 VW2PX - Быстрый запуск"
echo "========================================"

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Ошибка: Python3 не найден!"
    exit 1
fi

# Проверяем наличие основного файла
if [ ! -f "vw2px/converter.py" ]; then
    echo "❌ Ошибка: Файл vw2px/converter.py не найден!"
    exit 1
fi

# Устанавливаем значения по умолчанию
PROJECT_PATH=${1:-"."}
VIEWPORT=${2:-1920}
DRY_RUN=${3:-"--dry-run"}

# Если передан путь к проекту, убираем dry-run
if [ "$1" != "" ]; then
    DRY_RUN=""
fi

echo "📁 Проект: $PROJECT_PATH"
echo "🖥️  Viewport: ${VIEWPORT}px"
echo "🔍 Режим: $([ -z "$DRY_RUN" ] && echo "Выполнение замен" || echo "Предварительный просмотр")"
echo ""

# Запускаем конвертер
python3 vw2px/converter.py --path "$PROJECT_PATH" --viewport "$VIEWPORT" $DRY_RUN

echo ""
echo "✅ Скрипт завершен!"
