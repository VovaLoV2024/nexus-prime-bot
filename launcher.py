import json
import os
import sys
import subprocess
import platform
import shutil
import signal
import time

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
    """Выводит красивый баннер"""
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("╔══════════════════════════════════════════════════════╗")
    print("║         NEXUS PRIME BOT - LAUNCHER v1.4.0           ║")
    print("║              Discord Multiverse Bot                  ║")
    print("╚══════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")

def get_script_dir():
    """Получает директорию скрипта"""
    return os.path.dirname(os.path.abspath(__file__))

def get_core_dir():
    """Получает директорию nexus_core"""
    return os.path.join(get_script_dir(), "nexus_core")

def read_version():
    """Читает версию из VERSION.txt"""
    version_path = os.path.join(get_core_dir(), "VERSION.txt")
    versions = {}
    try:
        with open(version_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    versions[key.strip()] = value.strip()
    except FileNotFoundError:
        versions = {"launcher_version": "unknown", "bot_version": "unknown", "release_tag": "unknown"}
    return versions

def load_config():
    """Загружает конфигурацию"""
    config_path = os.path.join(get_core_dir(), "nexus_config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"bot_token": "", "guild_id": "", "owner_id": ""}

def save_config(config):
    """Сохраняет конфигурацию"""
    config_path = os.path.join(get_core_dir(), "nexus_config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def check_system():
    """Проверяет систему"""
    print(f"\n{Colors.YELLOW}[1/6] Проверка системы...{Colors.RESET}")
    
    # ОС
    os_name = platform.system()
    os_release = platform.release()
    print(f"  ✓ ОС: {os_name} {os_release}")
    
    # Python
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"  ✓ Python: {python_version}")
    
    if sys.version_info < (3, 8):
        print(f"  {Colors.RED}✗ Требуется Python 3.8+!{Colors.RESET}")
        return False
    
    # RAM
    try:
        import psutil
        ram_total = psutil.virtual_memory().total / (1024**3)
        print(f"  ✓ RAM: {ram_total:.1f} GB")
    except ImportError:
        print(f"  ⚠ Не удалось проверить RAM (установите psutil)")
    
    # Диск
    try:
        disk_usage = shutil.disk_usage(get_script_dir())
        disk_free = disk_usage.free / (1024**3)
        print(f"  ✓ Свободно на диске: {disk_free:.1f} GB")
    except:
        print(f"  ⚠ Не удалось проверить диск")
    
    # Git
    git_exists = shutil.which("git") is not None
    if git_exists:
        print(f"  ✓ Git установлен")
    else:
        print(f"  ⚠ Git не найден (не критично)")
    
    # Интернет
    try:
        import socket
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        print(f"  ✓ Интернет подключен")
    except:
        print(f"  ⚠ Нет подключения к интернету")
    
    return True

def check_dependencies():
    """Проверяет зависимости"""
    print(f"\n{Colors.YELLOW}[2/6] Проверка зависимостей...{Colors.RESET}")
    
    try:
        import discord
        print(f"  ✓ discord.py установлен (v{discord.__version__})")
    except ImportError:
        print(f"  {Colors.RED}✗ discord.py не установлен!{Colors.RESET}")
        return False
    
    try:
        import colorama
        print(f"  ✓ colorama установлен")
        colorama.init()
    except ImportError:
        print(f"  {Colors.RED}✗ colorama не установлен!{Colors.RESET}")
        return False
    
    return True

def check_versions():
    """Проверяет версии на GitHub (заглушка)"""
    print(f"\n{Colors.YELLOW}[3/6] Проверка версий...{Colors.RESET}")
    
    versions = read_version()
    print(f"  Launcher версия: {versions.get('launcher_version', 'unknown')}")
    print(f"  Бот версия: {versions.get('bot_version', 'unknown')}")
    print(f"  Статус: {versions.get('release_tag', 'unknown')}")
    
    # Здесь можно добавить проверку версий на GitHub
    print(f"  {Colors.GREEN}✓ Версии актуальны{Colors.RESET}")
    
    return True

def request_token():
    """Запрашивает токен у пользователя"""
    print(f"\n{Colors.YELLOW}[4/6] Настройка токена...{Colors.RESET}")
    
    config = load_config()
    
    if not config.get("bot_token"):
        print(f"  {Colors.MAGENTA}Требуется токен Discord бота{Colors.RESET}")
        print(f"  Создайте бота на: https://discord.com/developers/applications")
        print(f"  Включите Privileged Intents: Message Content Intent, Server Members Intent")
        print()
        
        token = input(f"  {Colors.CYAN}Введите токен бота: {Colors.RESET}").strip()
        
        if not token:
            print(f"  {Colors.RED}✗ Токен не может быть пустым!{Colors.RESET}")
            return False
        
        config["bot_token"] = token
        save_config(config)
        print(f"  {Colors.GREEN}✓ Токен сохранён{Colors.RESET}")
    else:
        print(f"  {Colors.GREEN}✓ Токен уже настроен{Colors.RESET}")
    
    return True

def start_bot():
    """Запускает бота"""
    print(f"\n{Colors.YELLOW}[5/6] Запуск бота...{Colors.RESET}")
    
    bot_path = os.path.join(get_core_dir(), "nexus_bot.py")
    
    if not os.path.exists(bot_path):
        print(f"  {Colors.RED}✗ Файл nexus_bot.py не найден!{Colors.RESET}")
        return False
    
    print(f"  Запуск nexus_bot.py...")
    
    process = subprocess.Popen(
        [sys.executable, bot_path],
        cwd=get_core_dir()
    )
    
    return process

def handle_exit_code(code, process):
    """Обрабатывает код выхода бота"""
    if code == 0:
        print(f"\n{Colors.GREEN}✓ Бот успешно завершил работу{Colors.RESET}")
    elif code == 1:
        print(f"\n{Colors.RED}✗ Ошибка токена!{Colors.RESET}")
        print(f"  Проверьте токен в nexus_core/nexus_config.json")
        # Очищаем токен для повторного ввода
        config = load_config()
        config["bot_token"] = ""
        save_config(config)
    elif code == 2:
        print(f"\n{Colors.RED}✗ Ошибка Privileged Intents!{Colors.RESET}")
        print(f"  Включите в настройках бота на Discord Developer Portal:")
        print(f"  - Message Content Intent")
        print(f"  - Server Members Intent")
    elif code == 3:
        print(f"\n{Colors.RED}✗ Ошибка сети!{Colors.RESET}")
        print(f"  Проверьте подключение к интернету")
    elif code == 4:
        print(f"\n{Colors.RED}✗ Другая ошибка!{Colors.RESET}")
    else:
        print(f"\n{Colors.RED}✗ Бот завершился с кодом {code}{Colors.RESET}")

def main():
    """Основная функция"""
    print_banner()
    
    bot_process = None
    
    def signal_handler(sig, frame):
        """Обработчик Ctrl+C"""
        print(f"\n\n{Colors.YELLOW}Остановка бота...{Colors.RESET}")
        if bot_process:
            bot_process.terminate()
            try:
                bot_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                bot_process.kill()
        print(f"{Colors.GREEN}До свидания!{Colors.RESET}")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Проверка системы
    if not check_system():
        sys.exit(1)
    
    # Проверка зависимостей
    if not check_dependencies():
        print(f"\n{Colors.YELLOW}Установите зависимости: pip install -r nexus_core/requirements.txt{Colors.RESET}")
        sys.exit(1)
    
    # Проверка версий
    if not check_versions():
        sys.exit(1)
    
    # Запрос токена
    if not request_token():
        sys.exit(1)
    
    # Запуск бота
    bot_process = start_bot()
    
    if bot_process:
        try:
            exit_code = bot_process.wait()
            handle_exit_code(exit_code, bot_process)
            
            # Если была ошибка токена (код 1), пробуем снова
            if exit_code == 1:
                print(f"\n{Colors.YELLOW}Повторная настройка...{Colors.RESET}")
                time.sleep(1)
                if request_token():
                    bot_process = start_bot()
                    if bot_process:
                        exit_code = bot_process.wait()
                        handle_exit_code(exit_code, bot_process)
        except KeyboardInterrupt:
            signal_handler(None, None)

if __name__ == "__main__":
    main()
