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
    
    # Файлы для скачивания
    files_to_download = [
        ("VERSION.txt", "https://raw.githubusercontent.com/VovaLoV2024/nexus-prime-bot/main/nexus_core/VERSION.txt"),
        ("launcher.py", "https://raw.githubusercontent.com/VovaLoV2024/nexus-prime-bot/main/launcher.py"),
        ("nexus_bot.py", "https://raw.githubusercontent.com/VovaLoV2024/nexus-prime-bot/main/nexus_core/nexus_bot.py"),
        ("requirements.txt", "https://raw.githubusercontent.com/VovaLoV2024/nexus-prime-bot/main/nexus_core/requirements.txt"),
    ]
    
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
    
    print(f"  {Colors.GREEN}✓ Скачано файлов: {len(downloaded_files)}{Colors.RESET}\n")
    return downloaded_files

def verify_downloaded_files(sandbox_dir, downloaded_files):
    """Проверяет целостность скачанных файлов"""
    print(f"{Colors.BLUE}[4/6] Проверка целостности файлов...{Colors.RESET}")
    
    for filename in downloaded_files:
        file_path = sandbox_dir / filename
        
        if not file_path.exists():
            raise Exception(f"Файл {filename} не найден в песочнице!")
        
        # Проверяем размер
        file_size = file_path.stat().st_size
        if file_size == 0:
            raise Exception(f"Файл {filename} пустой!")
        
        # Для Python файлов проверяем синтаксис
        if filename.endswith('.py'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    source = f.read()
                compile(source, str(file_path), 'exec')
                print(f"  ✓ {filename}: синтаксис корректен")
            except SyntaxError as e:
                raise Exception(f"Файл {filename} содержит синтаксические ошибки: {e}")
        
        print(f"  ✓ {filename}: проверка пройдена")
    
    print(f"  {Colors.GREEN}✓ Все файлы проверены{Colors.RESET}\n")

def replace_old_files(sandbox_dir, downloaded_files):
    """Заменяет старые файлы новыми из песочницы"""
    print(f"{Colors.BLUE}[5/6] Замена старых файлов...{Colors.RESET}")
    
    nexus_core_dir = Path(__file__).parent
    root_dir = nexus_core_dir.parent
    
    # Файлы которые нужно заменить в nexus_core
    core_files = ["VERSION.txt", "nexus_bot.py", "requirements.txt"]
    
    # Файлы которые нужно заменить в корне
    root_files = ["launcher.py"]
    
    backup_dir = None
    
    try:
        # Создаем резервную копию
        backup_dir = nexus_core_dir / "update_backup"
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Копируем старые файлы в резервную копию
        print("  Создание резервной копии...")
        for filename in core_files:
            old_path = nexus_core_dir / filename
            if old_path.exists():
                shutil.copy2(old_path, backup_dir / filename)
                print(f"    ✓ {filename} скопирован в резервную копию")
        
        for filename in root_files:
            old_path = root_dir / filename
            if old_path.exists():
                shutil.copy2(old_path, backup_dir / filename)
                print(f"    ✓ {filename} скопирован в резервную копию")
        
        # Заменяем файлы
        print("\n  Замена файлов...")
        for filename in core_files:
            if filename in downloaded_files:
                new_path = sandbox_dir / filename
                old_path = nexus_core_dir / filename
                shutil.copy2(new_path, old_path)
                print(f"    ✓ {filename} заменен")
        
        for filename in root_files:
            if filename in downloaded_files:
                new_path = sandbox_dir / filename
                old_path = root_dir / filename
                shutil.copy2(new_path, old_path)
                print(f"    ✓ {filename} заменен")
        
        print(f"  {Colors.GREEN}✓ Файлы успешно заменены{Colors.RESET}\n")
        return True
        
    except Exception as e:
        print(f"  {Colors.RED}✗ Ошибка замены файлов: {e}{Colors.RESET}")
        return False

def rollback(backup_dir):
    """Делает откат к старой версии при ошибке"""
    print(f"\n{Colors.RED}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.BOLD}❌ ОШИБКА ОБНОВЛЕНИЯ - ВЫПОЛНЯЮ ОТКАТ{Colors.RESET}")
    print(f"{Colors.RED}{'=' * 50}{Colors.RESET}\n")
    
    if backup_dir is None or not backup_dir.exists():
        print(f"  {Colors.RED}✗ Резервная копия не найдена! Откат невозможен!{Colors.RESET}")
        return False
    
    nexus_core_dir = Path(__file__).parent
    root_dir = nexus_core_dir.parent
    
    try:
        # Восстанавливаем файлы из резервной копии
        print("  Восстановление файлов из резервной копии...")
        
        for backup_file in backup_dir.iterdir():
            filename = backup_file.name
            
            if filename in ["VERSION.txt", "nexus_bot.py", "requirements.txt"]:
                target_path = nexus_core_dir / filename
            elif filename == "launcher.py":
                target_path = root_dir / filename
            else:
                continue
            
            shutil.copy2(backup_file, target_path)
            print(f"    ✓ {filename} восстановлен")
        
        print(f"  {Colors.GREEN}✓ Откат выполнен успешно{Colors.RESET}")
        return True
        
    except Exception as e:
        print(f"  {Colors.RED}✗ Ошибка отката: {e}{Colors.RESET}")
        return False

def cleanup(sandbox_dir, backup_dir):
    """Удаляет временные папки"""
    print(f"{Colors.BLUE}[6/6] Очистка временных файлов...{Colors.RESET}")
    
    try:
        if sandbox_dir.exists():
            shutil.rmtree(sandbox_dir)
            print(f"  ✓ Песочница удалена")
        
        if backup_dir and backup_dir.exists():
            shutil.rmtree(backup_dir)
            print(f"  ✓ Резервная копия удалена")
        
        print(f"  {Colors.GREEN}✓ Очистка завершена{Colors.RESET}\n")
        
    except Exception as e:
        print(f"  {Colors.YELLOW}~ Ошибка очистки: {e}{Colors.RESET}")

def launch_updated_launcher():
    """Запускает обновленный лаунчер"""
    print(f"{Colors.GREEN}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.BOLD}✅ ОБНОВЛЕНИЕ ЗАВЕРШЕНО УСПЕШНО!{Colors.RESET}")
    print(f"{Colors.GREEN}{'=' * 50}{Colors.RESET}\n")
    
    nexus_core_dir = Path(__file__).parent
    root_dir = nexus_core_dir.parent
    launcher_path = root_dir / "launcher.py"
    
    if not launcher_path.exists():
        print(f"{Colors.RED}✗ launcher.py не найден!{Colors.RESET}")
        return False
    
    print(f"Запуск обновленного лаунчера...\n")
    
    try:
        # Запускаем обновленный лаунчер
        subprocess.Popen([sys.executable, str(launcher_path)])
        print(f"{Colors.GREEN}✓ Лаунчер запущен{Colors.RESET}")
        return True
        
    except Exception as e:
        print(f"{Colors.RED}✗ Ошибка запуска лаунчера: {e}{Colors.RESET}")
        return False

def main():
    """Основная функция установщика"""
    import subprocess
    
    print_banner()
    
    # Проверка активных процессов
    check_running_processes()
    
    # Создание песочницы
    sandbox_dir = create_sandbox()
    backup_dir = None
    
    try:
        # Скачивание файлов
        downloaded_files = download_files_to_sandbox(sandbox_dir)
        
        # Проверка целостности
        verify_downloaded_files(sandbox_dir, downloaded_files)
        
        # Замена файлов
        if not replace_old_files(sandbox_dir, downloaded_files):
            raise Exception("Не удалось заменить файлы")
        
        # Очистка
        backup_dir = Path(__file__).parent / "update_backup"
        cleanup(sandbox_dir, backup_dir)
        
        # Запуск обновленного лаунчера
        launch_updated_launcher()
        
    except Exception as e:
        print(f"\n{Colors.RED}❌ КРИТИЧЕСКАЯ ОШИБКА: {e}{Colors.RESET}")
        
        # Делаем откат
        if backup_dir is None:
            backup_dir = Path(__file__).parent / "update_backup"
        
        rollback(backup_dir)
        
        # Очистка даже при ошибке
        cleanup(sandbox_dir, None)
        
        print(f"\n{Colors.YELLOW}Обновление прервано. Попробуйте снова позже.{Colors.RESET}")
        input("Нажмите Enter для выхода...")
        sys.exit(1)
    
    # Успешное завершение
    sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Получен сигнал остановки...{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}✗ Критическая ошибка установщика: {e}{Colors.RESET}")
        sys.exit(1)
