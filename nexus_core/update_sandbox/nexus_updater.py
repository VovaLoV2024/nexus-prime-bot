#!/usr/bin/env python3
"""
Nexus Prime Bot Updater
Скрипт для обновления лаунчера и бота
Автор: Вова (VovaLoV)
Помощница: Рокси 🐺
"""

import os
import sys
import json
import shutil
import urllib.request
import tempfile
import time
import subprocess
from pathlib import Path

# Цвета для консоли
class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"

def print_banner():
    """Выводит приветственный баннер с версией из файла"""
    # Читаем версию из VERSION.txt
    version_path = Path(__file__).parent / "VERSION.txt"
    launcher_ver = "unknown"
    if version_path.exists():
        with open(version_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('launcher_version='):
                    launcher_ver = line.split('=')[1].strip()
                    break
    
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("╔══════════════════════════════════════════════════════╗")
    print(f"║      NEXUS PRIME UPDATER v{launcher_ver:<8}              ║")
    print("║           Система обновления файлов                  ║")
    print("║                                                      ║")
    print("║  🤖 Создатель: Вова (VovaLoV)                        ║")
    print("║  🐺 Помощница: Рокси                                 ║")
    print("╚══════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")

def check_running_processes():
    """Проверяет, запущены ли launcher.py или nexus_bot.py"""
    print(f"{Colors.BLUE}[1/6] Проверка активных процессов...{Colors.RESET}")
    
    import subprocess
    try:
        # Проверяем запущенные процессы Python
        result = subprocess.run(
            ['tasklist' if os.name == 'nt' else 'ps', '-f'],
            capture_output=True,
            text=True,
            timeout=5
        )
        output = result.stdout.lower()
        
        running_processes = []
        if 'launcher.py' in output:
            running_processes.append('launcher.py')
        if 'nexus_bot.py' in output:
            running_processes.append('nexus_bot.py')
        
        if running_processes:
            print(f"  {Colors.YELLOW}⚠️  Обнаружены активные процессы: {', '.join(running_processes)}{Colors.RESET}")
            print(f"  Ожидание завершения (5 секунд)...")
            time.sleep(5)
            print(f"  Продолжаем обновление...")
        else:
            print(f"  {Colors.GREEN}✓ Активные процессы не обнаружены{Colors.RESET}")
    except Exception as e:
        print(f"  {Colors.YELLOW}~ Не удалось проверить процессы: {e}{Colors.RESET}")
    
    print(f"  {Colors.GREEN}✓ Проверка процессов завершена{Colors.RESET}\n")

def create_sandbox():
    """Создает временную папку-песочницу"""
    print(f"{Colors.BLUE}[2/6] Создание песочницы...{Colors.RESET}")
    
    # Путь к nexus_core
    nexus_core_dir = Path(__file__).parent
    
    # Создаем песочницу внутри nexus_core
    sandbox_dir = nexus_core_dir / "update_sandbox"
    
    # Если уже существует - удаляем
    if sandbox_dir.exists():
        shutil.rmtree(sandbox_dir)
        print(f"  Удалена старая песочница")
    
    # Создаем новую
    sandbox_dir.mkdir(parents=True, exist_ok=True)
    print(f"  ✓ Песочница создана: {sandbox_dir}")
    print(f"  {Colors.GREEN}✓ Песочница готова{Colors.RESET}\n")
    
    return sandbox_dir

def download_files_to_sandbox(sandbox_dir):
    """Скачивает свежие файлы с GitHub в песочницу"""
    print(f"{Colors.BLUE}[3/6] Скачивание файлов с GitHub...{Colors.RESET}")

    # Читаем website_enabled из локального VERSION.txt
    version_path = Path(__file__).parent / "VERSION.txt"
    website_enabled = '0'
    if version_path.exists():
        with open(version_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('website_enabled='):
                    website_enabled = line.split('=')[1].strip()
                    break

    # Файлы для скачивания (основные)
    files_to_download = [
        ("VERSION.txt", "https://raw.githubusercontent.com/VovaLoV2024/nexus-prime-bot/main/nexus_core/VERSION.txt"),
        ("launcher.py", "https://raw.githubusercontent.com/VovaLoV2024/nexus-prime-bot/main/launcher.py"),
        ("nexus_bot.py", "https://raw.githubusercontent.com/VovaLoV2024/nexus-prime-bot/main/nexus_core/nexus_bot.py"),
        ("nexus_setup.py", "https://raw.githubusercontent.com/VovaLoV2024/nexus-prime-bot/main/nexus_core/nexus_setup.py"),
        ("requirements.txt", "https://raw.githubusercontent.com/VovaLoV2024/nexus-prime-bot/main/nexus_core/requirements.txt"),
        ("nexus_config.example.json", "https://raw.githubusercontent.com/VovaLoV2024/nexus-prime-bot/main/nexus_core/nexus_config.example.json"),
    ]

    # Если сайт включен, добавляем файлы сайта
    if website_enabled == '1':
        print(f"  {Colors.CYAN}Сайт включен, скачиваем файлы сайта...{Colors.RESET}")
        # Здесь можно добавить URL файлов сайта
        # files_to_download.append(("index.html", "..."))

    downloaded_files = []

    for filename, url in files_to_download:
        try:
            print(f"  Скачиваю {filename}...")
            file_path = sandbox_dir / filename

            with urllib.request.urlopen(url, timeout=30) as response:
                content = response.read()

                # Сохраняем файл
                with open(file_path, 'wb') as f:
                    f.write(content)

            # Проверяем размер файла
            file_size = len(content)
            if file_size == 0:
                raise Exception(f"Файл {filename} пустой!")

            print(f"    ✓ {filename} ({file_size} байт)")
            downloaded_files.append(filename)

        except Exception as e:
            print(f"    {Colors.RED}✗ Ошибка скачивания {filename}: {e}{Colors.RESET}")
            raise

    # Скачиваем файлы конфигурации сервера
    print(f"  Скачиваю nexus_server_config/...")
    server_config_dir = sandbox_dir / "nexus_server_config"
    server_config_dir.mkdir(exist_ok=True)

    server_files = [
        ("nexus_roles.json", "https://raw.githubusercontent.com/VovaLoV2024/nexus-prime-bot/main/nexus_core/nexus_server_config/nexus_roles.json"),
        ("nexus_channels.json", "https://raw.githubusercontent.com/VovaLoV2024/nexus-prime-bot/main/nexus_core/nexus_server_config/nexus_channels.json"),
    ]

    for filename, url in server_files:
        try:
            print(f"    Скачиваю {filename}...")
            file_path = server_config_dir / filename

            with urllib.request.urlopen(url, timeout=30) as response:
                content = response.read()

                with open(file_path, 'wb') as f:
                    f.write(content)

            file_size = len(content)
            if file_size == 0:
                raise Exception(f"Файл {filename} пустой!")

            print(f"      ✓ {filename} ({file_size} байт)")
            downloaded_files.append(f"nexus_server_config/{filename}")

        except Exception as e:
            print(f"      {Colors.YELLOW}~ Ошибка скачивания {filename}: {e}{Colors.RESET}")
            # Не прерываем процесс, если файлы конфига не критичны

    print(f"  {Colors.GREEN}✓ Скачано файлов: {len(downloaded_files)}{Colors.RESET}\n")
    return downloaded_files


if __name__ == "__main__":
    """Основная функция updater'а"""
    print_banner()
    
    # 1. Проверяем активные процессы
    check_running_processes()
    
    # 2. Создаем песочницу
    sandbox_dir = create_sandbox()
    
    # 3. Создаем папку истории
    history_dir = Path(__file__).parent / "update_sandbox" / "history"
    history_dir.mkdir(parents=True, exist_ok=True)
    
    # 4. Создаем папку для текущего обновления с датой/временем
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    current_update_dir = history_dir / f"updater-{timestamp}"
    current_update_dir.mkdir(exist_ok=True)
    
    # 5. Скачиваем файлы в песочницу
    try:
        downloaded_files = download_files_to_sandbox(sandbox_dir)
        
        # 6. Копируем скачанные файлы в историю
        for filename in downloaded_files:
            src = sandbox_dir / filename
            dst = current_update_dir / filename
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
        
        # 7. Создаем backup текущих файлов
        print(f"{Colors.BLUE}[4/6] Создание резервной копии...{Colors.RESET}")
        backup_dir = sandbox_dir / "backup"
        backup_dir.mkdir(exist_ok=True)
        
        files_to_backup = [
            "launcher.py",
            "nexus_bot.py",
            "nexus_setup.py",
            "requirements.txt",
            "VERSION.txt"
        ]
        
        nexus_core_dir = Path(__file__).parent
        for filename in files_to_backup:
            src = nexus_core_dir / filename
            if src.exists():
                shutil.copy2(src, backup_dir / filename)
                print(f"  ✓ Скопирован {filename}")
        
        print(f"{Colors.GREEN}✓ Backup создан{Colors.RESET}\n")
        
        # 8. Заменяем старые файлы новыми
        print(f"{Colors.BLUE}[5/6] Замена файлов...{Colors.RESET}")
        for filename in downloaded_files:
            if filename.startswith("nexus_server_config/"):
                # Файлы из подпапки
                src = sandbox_dir / filename
                dst = nexus_core_dir / filename
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                print(f"  ✓ Обновлен {filename}")
            else:
                # Обычные файлы
                src = sandbox_dir / filename
                dst = nexus_core_dir / filename
                shutil.copy2(src, dst)
                print(f"  ✓ Обновлен {filename}")
        
        print(f"{Colors.GREEN}✓ Файлы заменены{Colors.RESET}\n")
        
        # 9. Проверяем что файлы заменились
        print(f"{Colors.BLUE}[6/6] Проверка обновления...{Colors.RESET}")
        for filename in downloaded_files:
            if not filename.startswith("nexus_server_config/"):
                dst = nexus_core_dir / filename
                if dst.exists() and dst.stat().st_size > 0:
                    print(f"  ✓ {filename} ({dst.stat().st_size} байт)")
                else:
                    print(f"  {Colors.RED}✗ {filename} не найден или пустой!{Colors.RESET}")
                    raise Exception(f"Файл {filename} не обновился!")
        
        print(f"{Colors.GREEN}✓ Все файлы проверены{Colors.RESET}\n")
        
        # 10. Удаляем старую историю (оставляем только 3 последние)
        history_folders = sorted([d for d in history_dir.iterdir() if d.is_dir()], 
                                 key=lambda x: x.name, reverse=True)
        if len(history_folders) > 3:
            print(f"{Colors.YELLOW}~ Удаляем старую историю...{Colors.RESET}")
            for old_folder in history_folders[3:]:
                shutil.rmtree(old_folder)
                print(f"  Удалена {old_folder.name}")
        
        # 11. Очищаем песочницу (но оставляем историю)
        for item in sandbox_dir.iterdir():
            if item.name != "history":
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
        
        print(f"{Colors.GREEN}✓ Обновление завершено успешно!{Colors.RESET}\n")
        
        # 12. Запускаем обновленный launcher.py
        print(f"{Colors.CYAN}Запускаю обновленный лаунчер...{Colors.RESET}")
        launcher_path = nexus_core_dir.parent / "launcher.py"
        subprocess.Popen([sys.executable, str(launcher_path)])
        
        # 13. Ждем немного и завершаемся
        time.sleep(2)
        sys.exit(0)
        
    except Exception as e:
        print(f"{Colors.RED} Ошибка обновления: {e}{Colors.RESET}")
        print(f"{Colors.YELLOW}~ Делаем откат...{Colors.RESET}")
        
        # Откат: восстанавливаем из backup
        backup_dir = sandbox_dir / "backup"
        if backup_dir.exists():
            nexus_core_dir = Path(__file__).parent
            for backup_file in backup_dir.iterdir():
                src = backup_file
                dst = nexus_core_dir / backup_file.name
                shutil.copy2(src, dst)
                print(f"  ✓ Восстановлен {backup_file.name}")
        
        print(f"{Colors.GREEN}✓ Откат завершен{Colors.RESET}")
        sys.exit(1)

