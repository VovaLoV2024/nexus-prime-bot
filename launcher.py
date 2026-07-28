#!/usr/bin/env python3
"""
Nexus Prime Bot Launcher v1.4.0
Главный файл запуска для бота Nexus Prime
Автор: Вова (VovaLoV)
Помощница: Рокси 🐺
"""

import os
import sys
import json
import subprocess
import signal
import platform
import shutil
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
    """Выводит приветственный баннер"""
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("╔══════════════════════════════════════════════════════╗")
    print("║         NEXUS PRIME BOT LAUNCHER v1.4.0              ║")
    print("║              Discord Multiverse Bot                  ║")
    print("║                                                      ║")
    print("║  🤖 Создатель: Вова (VovaLoV)                        ║")
    print("║  🐺 Помощница: Рокси                                 ║")
    print("╚══════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")

def check_system():
    """Проверяет систему на соответствие требованиям"""
    print(f"{Colors.BLUE}[1/6] Проверка системы...{Colors.RESET}")
    
    # Проверка ОС
    os_name = platform.system()
    os_version = platform.version()
    print(f"  ✓ ОС: {os_name} {os_version}")
    
    # Проверка Python
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info < (3, 8):
        print(f"  {Colors.RED}✗ Python версия {python_version} не поддерживается! Требуется 3.8+{Colors.RESET}")
        return False
    print(f"  ✓ Python: {python_version}")
    
    # Проверка RAM
    try:
        import psutil
        ram_gb = psutil.virtual_memory().total / (1024 ** 3)
        print(f"  ✓ RAM: {ram_gb:.1f} GB")
    except ImportError:
        print(f"  ~ RAM: не удалось проверить (установите psutil)")
    
    # Проверка диска
    try:
        disk_usage = shutil.disk_usage(".")
        disk_gb = disk_usage.free / (1024 ** 3)
        print(f"  ✓ Свободно на диске: {disk_gb:.1f} GB")
    except:
        print(f"  ~ Диск: не удалось проверить")
    
    # Проверка Git
    git_exists = shutil.which("git") is not None
    if git_exists:
        print(f"  ✓ Git установлен")
    else:
        print(f"  ~ Git: не найден (не критично)")
    
    # Проверка интернета
    import socket
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        print(f"  ✓ Интернет подключен")
    except:
        print(f"  {Colors.YELLOW}~ Интернет: не удалось проверить соединение{Colors.RESET}")
    
    print(f"  {Colors.GREEN}✓ Система проверена{Colors.RESET}\n")
    return True

def read_version():
    """Читает версию из VERSION.txt"""
    print(f"{Colors.BLUE}[2/6] Чтение версий...{Colors.RESET}")
    
    version_path = Path(__file__).parent / "nexus_core" / "VERSION.txt"
    if not version_path.exists():
        print(f"  {Colors.RED}✗ VERSION.txt не найден!{Colors.RESET}")
        return None
    
    versions = {}
    with open(version_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                versions[key.strip()] = value.strip()
    
    launcher_ver = versions.get('launcher_version', 'unknown')
    bot_ver = versions.get('bot_version', 'unknown')
    release_tag = versions.get('release_tag', 'unknown')
    
    print(f"  ✓ Лаунчер: v{launcher_ver}")
    print(f"  ✓ Бот: v{bot_ver}")
    print(f"  ✓ Статус: {release_tag}")
    print(f"  {Colors.GREEN}✓ Версии прочитаны{Colors.RESET}\n")
    
    return versions

def check_github_versions(local_versions):
    """Проверяет версии на GitHub и автоматически обновляется при необходимости"""
    print(f"{Colors.BLUE}[3/6] Проверка обновлений...{Colors.RESET}")
    
    github_url = "https://raw.githubusercontent.com/VovaLoV2024/nexus-prime-bot/main/nexus_core/VERSION.txt"
    
    try:
        import urllib.request
        
        # Скачиваем VERSION.txt с GitHub
        with urllib.request.urlopen(github_url, timeout=5) as response:
            github_content = response.read().decode('utf-8')
        
        # Парсим версии из GitHub
        github_versions = {}
        for line in github_content.splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                github_versions[key.strip()] = value.strip()
        
        github_launcher = github_versions.get('launcher_version', 'unknown')
        github_bot = github_versions.get('bot_version', 'unknown')
        
        local_launcher = local_versions.get('launcher_version', 'unknown')
        local_bot = local_versions.get('bot_version', 'unknown')
        
        print(f"  Локальная версия лаунчера: v{local_launcher}")
        print(f"  Версия на GitHub: v{github_launcher}")
        print(f"  Локальная версия бота: v{local_bot}")
        print(f"  Версия бота на GitHub: v{github_bot}")
        
        # Сравниваем версии
        needs_update = False
        if github_launcher != local_launcher:
            print(f"  {Colors.YELLOW}⚠️  Доступна новая версия лаунчера: v{github_launcher}{Colors.RESET}")
            needs_update = True
        
        if github_bot != local_bot:
            print(f"  {Colors.YELLOW}⚠️  Доступна новая версия бота: v{github_bot}{Colors.RESET}")
            needs_update = True
        
        if needs_update:
            print(f"\n  {Colors.CYAN}🔄 Начинаю автоматическое обновление...{Colors.RESET}")
            
            # Проверяем, есть ли git репозиторий
            git_dir = Path(__file__).parent / ".git"
            if not git_dir.exists():
                print(f"  {Colors.RED}✗ Не удалось обновить: это не Git-репозиторий{Colors.RESET}")
                print(f"  {Colors.CYAN}Чтобы обновиться вручную:{Colors.RESET}")
                print(f"  cd /workspace && git init && git remote add origin https://github.com/VovaLoV2024/nexus-prime-bot.git")
                print(f"  git pull origin main --force")
                return
            
            # Пытаемся сделать git pull
            import subprocess
            result = subprocess.run(
                ["git", "pull", "origin", "main", "--force"],
                cwd=str(Path(__file__).parent),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"  {Colors.GREEN}✓ Обновление успешно загружено!{Colors.RESET}")
                print(f"  {Colors.CYAN}Перезапускаю лаунчер для применения обновлений...{Colors.RESET}")
                
                # Перезапускаем лаунчер с новыми файлами
                os.execv(sys.executable, [sys.executable] + sys.argv)
            else:
                print(f"  {Colors.RED}✗ Ошибка при обновлении: {result.stderr}{Colors.RESET}")
                print(f"  {Colors.CYAN}Попробуйте обновиться вручную:{Colors.RESET}")
                print(f"  git pull origin main --force")
        else:
            print(f"  {Colors.GREEN}✓ Установлена последняя версия{Colors.RESET}")
            
    except Exception as e:
        print(f"  {Colors.YELLOW}~ Не удалось проверить обновления: {e}{Colors.RESET}")
        print(f"  ~ Продолжаем работу с локальными версиями...")
    
    print(f"  {Colors.GREEN}✓ Проверка обновлений завершена{Colors.RESET}\n")

def get_config_path():
    """Возвращает путь к конфигу"""
    return Path(__file__).parent / "nexus_core" / "nexus_config.json"

def load_config():
    """Загружает конфигурацию"""
    config_path = get_config_path()
    if not config_path.exists():
        return None
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    """Сохраняет конфигурацию"""
    config_path = get_config_path()
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def prompt_for_token():
    """Запрашивает токен у пользователя"""
    print(f"{Colors.YELLOW}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.BOLD}⚠️  ТРЕБУЕТСЯ НАСТРОЙКА БОТА{Colors.RESET}")
    print(f"{Colors.YELLOW}{'=' * 50}{Colors.RESET}\n")
    
    print("Для работы бота необходим токен Discord.")
    print("Получить токен можно здесь:")
    print(f"{Colors.CYAN}https://discord.com/developers/applications{Colors.RESET}\n")
    
    print("Инструкция:")
    print("1. Создайте новое приложение")
    print("2. Перейдите в раздел 'Bot'")
    print("3. Нажмите 'Reset Token' и скопируйте токен")
    print("4. Вставьте токен ниже\n")
    
    while True:
        token = input(f"{Colors.MAGENTA}Введите токен вашего бота: {Colors.RESET}").strip()
        if token:
            confirm = input(f"Подтвердить токен? (y/n): ").strip().lower()
            if confirm == 'y':
                return token
            print(f"{Colors.YELLOW}Токен не подтвержден. Попробуйте снова.{Colors.RESET}\n")
        else:
            print(f"{Colors.RED}Токен не может быть пустым!{Colors.RESET}\n")

def prompt_for_guild_id():
    """Запрашивает ID сервера у пользователя"""
    print(f"\n{Colors.YELLOW}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.BOLD}📊 НАСТРОЙКА СЕРВЕРА{Colors.RESET}")
    print(f"{Colors.YELLOW}{'=' * 50}{Colors.RESET}\n")
    
    print("Укажите ID вашего Discord сервера (опционально).")
    print("Чтобы получить ID сервера:")
    print("1. В Discord включите режим разработчика")
    print("   (Настройки → Дополнительно → Режим разработчика)")
    print("2. Кликните ПКМ по серверу и выберите 'Копировать ID'\n")
    
    guild_id = input(f"{Colors.MAGENTA}Введите ID сервера (или нажмите Enter для пропуска): {Colors.RESET}").strip()
    return guild_id

def install_dependencies():
    """Устанавливает зависимости"""
    print(f"{Colors.BLUE}[4/6] Установка зависимостей...{Colors.RESET}")
    
    requirements_path = Path(__file__).parent / "nexus_core" / "requirements.txt"
    if not requirements_path.exists():
        print(f"  {Colors.YELLOW}~ requirements.txt не найден{Colors.RESET}")
        return True
    
    print(f"  Установка пакетов из requirements.txt...")
    
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(requirements_path), "-q"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"  {Colors.GREEN}✓ Зависимости установлены{Colors.RESET}\n")
        return True
    else:
        print(f"  {Colors.RED}✗ Ошибка установки зависимостей{Colors.RESET}")
        print(f"  {result.stderr}")
        return False

def run_bot():
    """Запускает бота и обрабатывает коды возврата"""
    print(f"{Colors.BLUE}[6/6] Запуск бота...{Colors.RESET}")
    print(f"{Colors.YELLOW}{'=' * 50}{Colors.RESET}\n")
    
    bot_path = Path(__file__).parent / "nexus_core" / "nexus_bot.py"
    
    if not bot_path.exists():
        print(f"{Colors.RED}✗ nexus_bot.py не найден!{Colors.RESET}")
        return False
    
    process = None
    try:
        process = subprocess.Popen(
            [sys.executable, str(bot_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Читаем вывод бота
        for line in process.stdout:
            print(line, end='')
        
        process.wait()
        return_code = process.returncode
        
        print(f"\n{Colors.YELLOW}{'=' * 50}{Colors.RESET}")
        print(f"Бот завершился с кодом: {return_code}\n")
        
        if return_code == 1:
            print(f"{Colors.RED}❌ ОШИБКА ТОКЕНА{Colors.RESET}")
            print("Токен неверный или истек срок действия.")
            print("Пожалуйста, получите новый токен на Discord Developer Portal.\n")
            return "token_error"
        
        elif return_code == 2:
            print(f"{Colors.RED}❌ ОШИБКА PRIVILEGED INTENTS{Colors.RESET}")
            print("Необходимо включить Privileged Gateway Intents!")
            print("\nИнструкция:")
            print("1. Перейдите на https://discord.com/developers/applications")
            print("2. Выберите ваше приложение")
            print("3. Перейдите в раздел 'Bot'")
            print("4. Включите следующие опции:")
            print("   - SERVER MEMBERS INTENT")
            print("   - MESSAGE CONTENT INTENT")
            print("5. Сохраните изменения и перезапустите бота\n")
            return "intents_error"
        
        elif return_code == 3:
            print(f"{Colors.RED}❌ ОШИБКА СЕТИ{Colors.RESET}")
            print("Проверьте подключение к интернету.\n")
            return "network_error"
        
        elif return_code == 4:
            print(f"{Colors.RED}❌ ДРУГАЯ ОШИБКА{Colors.RESET}")
            print("Произошла непредвиденная ошибка.\n")
            return "other_error"
        
        elif return_code == 0:
            print(f"{Colors.GREEN}✓ Бот корректно остановлен{Colors.RESET}\n")
            return "stopped"
        
        else:
            print(f"{Colors.YELLOW}~ Неизвестный код возврата: {return_code}{Colors.RESET}\n")
            return "unknown"
    
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Получен сигнал остановки...{Colors.RESET}")
        if process:
            process.terminate()
            process.wait()
        print(f"{Colors.GREEN}✓ Все процессы остановлены{Colors.RESET}\n")
        return "interrupted"
    
    except Exception as e:
        print(f"{Colors.RED}✗ Ошибка запуска бота: {e}{Colors.RESET}")
        return "launch_error"

def main():
    """Основная функция лаунчера"""
    print_banner()
    
    # Проверка системы
    if not check_system():
        print(f"{Colors.RED}✗ Проверка системы не пройдена!{Colors.RESET}")
        sys.exit(1)
    
    # Чтение версий
    versions = read_version()
    if not versions:
        sys.exit(1)
    
    # Проверка обновлений на GitHub
    check_github_versions(versions)
    
    # Установка зависимостей
    if not install_dependencies():
        print(f"{Colors.YELLOW}~ Продолжаем без установки зависимостей...{Colors.RESET}\n")
    
    # Загрузка конфига
    print(f"{Colors.BLUE}[5/6] Проверка конфигурации...{Colors.RESET}")
    config = load_config()
    
    if config is None:
        print(f"  {Colors.YELLOW}~ Конфиг не найден, будет создан{Colors.RESET}")
        config = {"bot_token": "", "guild_id": "", "owner_id": ""}
    
    # Проверка токена
    bot_token = config.get("bot_token", "").strip()
    
    if not bot_token:
        print(f"  {Colors.YELLOW}⚠️  Токен не настроен{Colors.RESET}")
        
        # Запрос токена
        bot_token = prompt_for_token()
        config["bot_token"] = bot_token
        
        # Запрос ID сервера (опционально)
        guild_id = prompt_for_guild_id()
        if guild_id:
            config["guild_id"] = guild_id
        
        # Сохранение конфига
        save_config(config)
        print(f"  {Colors.GREEN}✓ Конфигурация сохранена{Colors.RESET}\n")
    else:
        print(f"  {Colors.GREEN}✓ Токен настроен{Colors.RESET}\n")
    
    print(f"{Colors.GREEN}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.BOLD}✅ ГОТОВО К ЗАПУСКУ{Colors.RESET}")
    print(f"{Colors.GREEN}{'=' * 50}{Colors.RESET}\n")
    
    # Запуск бота
    while True:
        result = run_bot()
        
        if result == "token_error":
            # Запрос нового токена
            print(f"{Colors.YELLOW}Требуется новый токен!{Colors.RESET}\n")
            new_token = prompt_for_token()
            config["bot_token"] = new_token
            save_config(config)
            print(f"{Colors.GREEN}✓ Токен обновлен{Colors.RESET}\n")
            continue
        
        elif result == "intents_error":
            print(f"{Colors.YELLOW}После включения Intents перезапустите лаунчер.{Colors.RESET}")
            input("Нажмите Enter для выхода...")
            break
        
        elif result in ["network_error", "other_error", "unknown", "launch_error"]:
            retry = input("Попробовать снова? (y/n): ").strip().lower()
            if retry != 'y':
                break
            continue
        
        else:
            # Нормальная остановка или прерывание
            break
    
    print(f"{Colors.CYAN}Спасибо за использование Nexus Prime Bot!{Colors.RESET}")
    print(f"{Colors.MAGENTA}🐺 Рокси желает вам удачного дня!{Colors.RESET}\n")

if __name__ == "__main__":
    # Обработка Ctrl+C
    def signal_handler(sig, frame):
        print(f"\n{Colors.YELLOW}Получен сигнал остановки...{Colors.RESET}")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        main()
    except Exception as e:
        print(f"{Colors.RED}✗ Критическая ошибка лаунчера: {e}{Colors.RESET}")
        sys.exit(1)
