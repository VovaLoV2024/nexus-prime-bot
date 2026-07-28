#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nexus Prime Bot - Launcher v1.3.1
Главный файл запуска бота
Автор: Вова и Рокси
"""

import os
import sys
import json
import subprocess
import urllib.request
import shutil
import platform
import socket
import signal
import time
from pathlib import Path

# Версия лаунчера
LAUNCHER_VERSION = "1.3.1"
RELEASE_TAG = "beta"

# Хранилище запущенных процессов
running_processes = {}
shutdown_requested = False

# Цвета для красивого вывода
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_banner():
    """Выводит красивый баннер"""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}╔═══════════════════════════════════════════════╗
║     NEXUS PRIME BOT - LAUNCHER v{LAUNCHER_VERSION}       ║
║     Разработано для Вовы и Рокси            ║
╚═══════════════════════════════════════════════╝{Colors.RESET}
"""
    print(banner)

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.RESET}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")


def signal_handler(signum, frame):
    """Обработчик сигналов для корректной остановки"""
    global shutdown_requested
    shutdown_requested = True
    print(f"\n\n{Colors.YELLOW}Получен сигнал остановки...{Colors.RESET}")
    stop_all_processes()
    sys.exit(0)


def stop_all_processes():
    """Останавливает все запущенные процессы"""
    global running_processes
    
    if not running_processes:
        return
    
    print(f"\n{Colors.CYAN}🛑 Остановка процессов...{Colors.RESET}")
    
    for name, proc_info in list(running_processes.items()):
        proc = proc_info.get('process')
        pid = proc_info.get('pid')
        
        if proc and proc.poll() is None:
            try:
                # Пытаемся корректно завершить процесс
                proc.terminate()
                print(f"   ✓ Процесс {name} (PID: {pid}) - завершается...")
                
                # Ждём немного для graceful shutdown
                try:
                    proc.wait(timeout=5)
                    print(f"   ✓ Процесс {name} (PID: {pid}) - остановлен")
                except subprocess.TimeoutExpired:
                    # Если не завершился - убиваем
                    proc.kill()
                    print(f"   ⚠ Процесс {name} (PID: {pid}) - принудительно остановлен")
                    
            except Exception as e:
                print(f"   ✗ Ошибка остановки {name}: {e}")
        else:
            print(f"   ℹ Процесс {name} (PID: {pid}) - уже остановлен")
    
    running_processes.clear()
    
    # Удаляем файл с PID
    pid_file = Path("nexus_prime_bot/launcher.pid")
    if pid_file.exists():
        pid_file.unlink()
    
    print(f"\n{Colors.GREEN}✨ Бот остановлен пользователем{Colors.RESET}")


def save_pid_file(pid, script_name):
    """Сохраняет PID запущенного процесса в файл"""
    pid_file = Path("nexus_prime_bot/launcher.pid")
    try:
        pid_file.write_text(f"{pid}:{script_name}:{time.time()}")
    except Exception:
        pass


def check_internet_connection(host="github.com", port=443, timeout=5):
    """Проверяет наличие интернет-соединения"""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False

def check_github_api():
    """Проверяет доступность GitHub API"""
    try:
        url = "https://api.github.com"
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.status == 200
    except Exception:
        return False

def get_git_version():
    """Получает версию Git если установлен"""
    try:
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip().split()[-1]
        return None
    except Exception:
        return None

def get_system_info():
    """Собирает информацию о системе"""
    info = {}
    
    # ОС
    system = platform.system()
    release = platform.release()
    version = platform.version()
    arch = platform.machine()
    
    if system == "Windows":
        win_ver = platform.win32_ver()[0]
        info['os'] = f"{system} {win_ver} ({arch})"
    elif system == "Darwin":
        info['os'] = f"macOS {release} ({arch})"
    else:
        info['os'] = f"{system} {release} ({arch})"
    
    # Python
    py_version = f"{platform.python_version()} ({'64-bit' if platform.architecture()[0] == '64bit' else '32-bit'})"
    info['python'] = py_version
    
    # Процессор
    try:
        cpu_count = os.cpu_count() or 1
        info['cpu'] = f"{cpu_count} ядер"
    except Exception:
        info['cpu'] = "Неизвестно"
    
    # RAM
    try:
        import psutil
        total_ram = psutil.virtual_memory().total / (1024 ** 3)
        free_ram = psutil.virtual_memory().available / (1024 ** 3)
        info['ram'] = f"{total_ram:.1f} GB ({free_ram:.1f} GB свободно)"
    except ImportError:
        # Если psutil не установлен, пробуем альтернативные методы
        try:
            if system == "Linux":
                with open('/proc/meminfo', 'r') as f:
                    meminfo = {}
                    for line in f:
                        parts = line.split(':')
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip().split()[0]
                            meminfo[key] = int(value)
                total_kb = meminfo.get('MemTotal', 0)
                free_kb = meminfo.get('MemAvailable', meminfo.get('MemFree', 0))
                info['ram'] = f"{total_kb/1024/1024:.1f} GB ({free_kb/1024/1024:.1f} GB свободно)"
            else:
                info['ram'] = "Неизвестно (установите psutil)"
        except Exception:
            info['ram'] = "Неизвестно"
    
    # Диск
    try:
        import psutil
        disk = psutil.disk_usage('/')
        free_disk = disk.free / (1024 ** 3)
        info['disk'] = f"{free_disk:.1f} GB свободно"
    except ImportError:
        try:
            if system == "Windows":
                import ctypes
                free_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p("C:\\"),
                    None, None, ctypes.byref(free_bytes)
                )
                info['disk'] = f"{free_bytes.value / (1024**3):.1f} GB свободно"
            else:
                stat = os.statvfs('/')
                free_disk = (stat.f_bavail * stat.f_frsize) / (1024 ** 3)
                info['disk'] = f"{free_disk:.1f} GB свободно"
        except Exception:
            info['disk'] = "Неизвестно"
    
    # Git
    git_version = get_git_version()
    info['git'] = git_version if git_version else "Не установлен"
    
    # Интернет
    has_internet = check_internet_connection()
    info['internet'] = "подключён" if has_internet else "нет соединения"
    
    # GitHub API
    if has_internet:
        github_available = check_github_api()
        info['github'] = "доступен" if github_available else "не доступен"
    else:
        info['github'] = "нет соединения"
    
    return info

def print_system_diagnostics():
    """Выводит диагностику системы"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}🔍 ДИАГНОСТИКА СИСТЕМЫ:{Colors.RESET}")
    
    info = get_system_info()
    
    # ОС
    print(f"   ✓ ОС: {info['os']}")
    
    # Python
    print(f"   ✓ Python: {info['python']}")
    
    # Процессор
    print(f"   ✓ Процессор: {info['cpu']}")
    
    # RAM
    print(f"   ✓ RAM: {info['ram']}")
    
    # Диск
    print(f"   ✓ Диск: {info['disk']}")
    
    # Git
    if info['git'] != "Не установлен":
        print(f"   ✓ Git: {info['git']}")
    else:
        print(f"   ⚠ Git: {info['git']}")
    
    # Интернет
    if info['internet'] == "подключён":
        print(f"   ✓ Интернет: {info['internet']}")
    else:
        print(f"   ⚠ Интернет: {info['internet']}")
    
    # GitHub
    if info['github'] == "доступен":
        print(f"   ✓ GitHub: {info['github']}")
    elif info['github'] == "нет соединения":
        print(f"   ⚠ GitHub: {info['github']}")
    else:
        print(f"   ✗ GitHub: {info['github']}")
    
    print()

def get_local_versions():
    """Получает локальные версии из VERSION.txt"""
    version_file = Path("nexus_prime_bot/VERSION.txt")
    if not version_file.exists():
        return {
            'launcher_version': LAUNCHER_VERSION,
            'bot_version': '0.0.0',
            'release_tag': RELEASE_TAG
        }
    
    try:
        content = version_file.read_text(encoding='utf-8').strip()
        versions = {}
        for line in content.split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                versions[key.strip()] = value.strip()
        
        return {
            'launcher_version': versions.get('launcher_version', LAUNCHER_VERSION),
            'bot_version': versions.get('bot_version', '0.0.0'),
            'release_tag': versions.get('release_tag', RELEASE_TAG)
        }
    except Exception:
        return {
            'launcher_version': LAUNCHER_VERSION,
            'bot_version': '0.0.0',
            'release_tag': RELEASE_TAG
        }


def get_remote_version():
    """Получает версии с GitHub"""
    try:
        # Правильный путь к VERSION.txt в репозитории
        url = "https://raw.githubusercontent.com/VovaLoV2024/nexus-prime-bot/main/nexus_prime_bot/VERSION.txt"
        with urllib.request.urlopen(url, timeout=5) as response:
            content = response.read().decode('utf-8').strip()
            
            # Парсим файл
            versions = {}
            for line in content.split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    versions[key.strip()] = value.strip()
            
            return {
                'launcher_version': versions.get('launcher_version', '0.0.0'),
                'bot_version': versions.get('bot_version', '0.0.0'),
                'release_tag': versions.get('release_tag', 'beta')
            }
    except Exception:
        return None


def get_bot_version():
    """Получает версию бота из nexus_bot.py"""
    bot_file = Path("nexus_prime_bot/nexus_bot.py")
    if not bot_file.exists():
        return None
    
    try:
        content = bot_file.read_text(encoding='utf-8')
        # Ищем строку вида "Nexus Prime Bot v1.3.2" или "v1.3.2"
        import re
        match = re.search(r'v(\d+\.\d+\.\d+)', content)
        if match:
            return match.group(1)
        # Или ищем просто версию
        match = re.search(r'Version:\s*(\d+\.\d+\.\d+)', content)
        if match:
            return match.group(1)
    except Exception:
        pass
    
    return None


def version_compare(v1, v2):
    """Сравнивает две версии. Возвращает -1, 0, или 1"""
    try:
        v1_parts = [int(x) for x in v1.split('.')]
        v2_parts = [int(x) for x in v2.split('.')]
        
        if v1_parts < v2_parts:
            return -1
        elif v1_parts > v2_parts:
            return 1
        else:
            return 0
    except ValueError:
        # Если не удалось распарсить, сравниваем как строки
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
        else:
            return 0


def check_for_updates(has_internet):
    """Проверяет обновления И лаунчера, И бота"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}📦 ПРОВЕРКА ПРОЕКТА:{Colors.RESET}")
    
    # Проверяем наличие проекта
    base_dir = Path("nexus_prime_bot")
    if base_dir.exists():
        print_success("Проект найден")
    else:
        print_error("Проект не найден")
        return False
    
    # Получаем локальные версии
    local_versions = get_local_versions()
    local_launcher = local_versions['launcher_version']
    local_bot = local_versions['bot_version']
    release_tag = local_versions['release_tag']
    
    # Показываем локальные версии
    print_info(f"Версия лаунчера: {local_launcher} ({release_tag})")
    print_info(f"Версия бота: {local_bot} ({release_tag})")
    
    # Если нет интернета, не проверяем GitHub
    if not has_internet:
        print_warning("Нет интернета — проверка GitHub пропущена")
        return True
    
    # Получаем удалённые версии
    remote = get_remote_version()
    if not remote:
        print_warning("Не удалось проверить версию на GitHub")
        return True
    
    print_info(f"GitHub лаунчер: {remote['launcher_version']}")
    print_info(f"GitHub бот: {remote['bot_version']}")
    
    # Сравниваем версии
    launcher_update = version_compare(local_launcher, remote['launcher_version']) < 0
    bot_update = version_compare(local_bot, remote['bot_version']) < 0
    
    if launcher_update or bot_update:
        print_warning("Доступно обновление!")
        
        if launcher_update:
            print(f"   ⚠ Лаунчер: {local_launcher} → {remote['launcher_version']}")
        if bot_update:
            print(f"   ⚠ Бот: {local_bot} → {remote['bot_version']}")
        
        response = input("\n🤔 Обновить? (y/n): ")
        if response.lower() == 'y':
            if launcher_update:
                update_launcher(remote['launcher_version'])
            if bot_update:
                update_bot(remote['bot_version'])
            return 'updated'
        else:
            return 'skipped'
    else:
        print_success("Всё актуально!")
        return True

def update_launcher(version):
    """Скачивает новую версию лаунчера с GitHub"""
    print(f"\n{Colors.CYAN}⏳ Обновление лаунчера...{Colors.RESET}")
    try:
        url = "https://raw.githubusercontent.com/VovaLoV2024/nexus-prime-bot/main/launcher.py"
        with urllib.request.urlopen(url, timeout=10) as response:
            content = response.read().decode('utf-8')
        
        # Сохраняем новый launcher.py
        with open("launcher.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print_success(f"Лаунчер обновлён до v{version}")
        return True
    except Exception as e:
        print_error(f"Ошибка обновления лаунчера: {e}")
        return False


def update_bot(version):
    """Скачивает новую версию бота с GitHub"""
    print(f"\n{Colors.CYAN}⏳ Обновление бота...{Colors.RESET}")
    try:
        url = "https://raw.githubusercontent.com/VovaLoV2024/nexus-prime-bot/main/nexus_prime_bot/nexus_bot.py"
        with urllib.request.urlopen(url, timeout=10) as response:
            content = response.read().decode('utf-8')
        
        # Сохраняем новый nexus_bot.py
        bot_path = Path("nexus_prime_bot/nexus_bot.py")
        with open(bot_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print_success(f"Бот обновлён до v{version}")
        return True
    except Exception as e:
        print_error(f"Ошибка обновления бота: {e}")
        return False


def save_token_to_config(token):
    """Сохраняет токен в nexus_config.json"""
    import json
    config_path = Path("nexus_prime_bot/nexus_config.json")
    
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    else:
        config = {}
    
    config["bot_token"] = token
    
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def run_git_pull():
    """Выполняет git pull для обновления"""
    try:
        print_info("Загрузка обновлений...")
        result = subprocess.run(
            ["git", "pull"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print_success("Обновление успешно загружено")
            return True
        else:
            print_error(f"Ошибка при обновлении: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print_error("Тайм-аут при обновлении")
        return False
    except FileNotFoundError:
        print_error("Git не найден. Установите Git для получения обновлений")
        return False

def create_project_structure():
    """Создаёт структуру проекта при первом запуске"""
    base_dir = Path("nexus_prime_bot")
    
    if base_dir.exists():
        print_info(f"Папка {Colors.CYAN}{base_dir}{Colors.RESET} уже существует")
        return True
    
    print_info("Создание структуры проекта...")
    
    try:
        # Создаём основную папку
        base_dir.mkdir(parents=True, exist_ok=True)
        print_success(f"Создана папка: {base_dir}/")
        
        # Создаём папку конфигурации сервера
        config_dir = base_dir / "nexus_server_config"
        config_dir.mkdir(exist_ok=True)
        print_success(f"Создана папка: {config_dir}/")
        
        # Создаём все файлы
        files_created = create_all_files(base_dir, config_dir)
        
        if files_created:
            print_success("Все файлы проекта созданы успешно!")
            return True
        else:
            return False
            
    except Exception as e:
        print_error(f"Ошибка при создании структуры: {e}")
        return False

def create_all_files(base_dir, config_dir):
    """Создаёт все необходимые файлы проекта"""
    try:
        # VERSION.txt
        version_content = "1.3"
        (base_dir / "VERSION.txt").write_text(version_content)
        print_success("Создан: VERSION.txt")
        
        # nexus_config.json
        config_content = '''{
    "BOT_TOKEN": "YOUR_BOT_TOKEN_HERE",
    "GUILD_ID": "YOUR_SERVER_ID_HERE"
}
'''
        (base_dir / "nexus_config.json").write_text(config_content)
        print_success("Создан: nexus_config.json")
        
        # nexus_config.example.json
        example_content = '''{
    "BOT_TOKEN": "вставьте_ваш_токен_бота_discord",
    "GUILD_ID": "вставьте_ID_вашего_сервера"
}

# Пример токена: MTIzNDU2Nzg5MDEyMzQ1Njc4OQ.GaBcDe.FgHiJkLmNoPqRsTuVwXyZ123456789
# Пример ID сервера: 123456789012345678
'''
        (base_dir / "nexus_config.example.json").write_text(example_content)
        print_success("Создан: nexus_config.example.json")
        
        # requirements.txt
        requirements_content = """discord.py>=2.3.0
colorama>=0.4.6
"""
        (base_dir / "requirements.txt").write_text(requirements_content)
        print_success("Создан: requirements.txt")
        
        # .gitignore
        gitignore_content = """# Конфигурация с токеном
nexus_config.json

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
        (base_dir / ".gitignore").write_text(gitignore_content)
        print_success("Создан: .gitignore")
        
        # nexus_roles.json
        roles_content = """{
    "roles": [
        {
            "name": "👑 Администратор",
            "color": "#FF0000",
            "permissions": ["administrator"],
            "hoist": true,
            "mentionable": true,
            "position": 10
        },
        {
            "name": "🛡️ Модератор",
            "color": "#00FF00",
            "permissions": ["manage_messages", "kick_members"],
            "hoist": true,
            "mentionable": true,
            "position": 8
        },
        {
            "name": "✅ Проверенный",
            "color": "#0000FF",
            "permissions": [],
            "hoist": false,
            "mentionable": false,
            "position": 5,
            "auto_assign": false
        },
        {
            "name": "🤖 Бот",
            "color": "#808080",
            "permissions": [],
            "hoist": true,
            "mentionable": false,
            "position": 1
        }
    ]
}
"""
        (config_dir / "nexus_roles.json").write_text(roles_content)
        print_success("Создан: nexus_server_config/nexus_roles.json")
        
        # nexus_channels.json
        channels_content = """{
    "categories": [
        {
            "name": "📋 ИНФОРМАЦИЯ",
            "position": 0,
            "channels": [
                {
                    "name": "правила",
                    "type": "text",
                    "topic": "Правила сервера Nexus Prime"
                },
                {
                    "name": "новости",
                    "type": "text",
                    "topic": "Новости проекта"
                },
                {
                    "name": "приветствия",
                    "type": "text",
                    "topic": "Приветствия новых участников"
                }
            ]
        },
        {
            "name": "💬 ОБЩЕНИЕ",
            "position": 1,
            "channels": [
                {
                    "name": "общий-чат",
                    "type": "text",
                    "topic": "Основной чат для общения"
                },
                {
                    "name": "флудилка",
                    "type": "text",
                    "topic": "Место для свободного общения"
                },
                {
                    "name": "голосовой чат",
                    "type": "voice"
                }
            ]
        },
        {
            "name": "🔧 ТЕХНИЧЕСКИЙ",
            "position": 2,
            "channels": [
                {
                    "name": "команды-бота",
                    "type": "text",
                    "topic": "Использование команд бота"
                },
                {
                    "name": "логи",
                    "type": "text",
                    "topic": "Логирование действий"
                }
            ]
        }
    ]
}
"""
        (config_dir / "nexus_channels.json").write_text(channels_content)
        print_success("Создан: nexus_server_config/nexus_channels.json")
        
        # nexus_setup.py
        setup_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nexus Prime Bot - Setup Script
Скрипт настройки сервера
"""

import json
import sys
from pathlib import Path

try:
    import discord
    from discord.ext import commands
    from colorama import init, Fore, Style
    init()
except ImportError:
    print(f"{Fore.RED}Требуется установить зависимости: pip install -r requirements.txt{Style.RESET_ALL}")
    sys.exit(1)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def load_config():
    """Загружает конфигурацию"""
    config_path = Path("nexus_config.json")
    if not config_path.exists():
        print(f"{Fore.RED}Файл nexus_config.json не найден!{Style.RESET_ALL}")
        return None
    
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_roles_config():
    """Загружает конфигурацию ролей"""
    roles_path = Path("nexus_server_config/nexus_roles.json")
    if not roles_path.exists():
        print(f"{Fore.RED}Файл nexus_roles.json не найден!{Style.RESET_ALL}")
        return None
    
    with open(roles_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_channels_config():
    """Загружает конфигурацию каналов"""
    channels_path = Path("nexus_server_config/nexus_channels.json")
    if not channels_path.exists():
        print(f"{Fore.RED}Файл nexus_channels.json не найден!{Style.RESET_ALL}")
        return None
    
    with open(channels_path, "r", encoding="utf-8") as f:
        return json.load(f)

def hex_to_color(hex_color):
    """Конвертирует HEX цвет в discord.Color"""
    hex_color = hex_color.lstrip("#")
    return discord.Color(int(hex_color, 16))

async def setup_roles(guild, roles_config):
    """Создаёт роли на сервере"""
    print(f"{Fore.CYAN}Настройка ролей...{Style.RESET_ALL}")
    
    roles_data = roles_config.get("roles", [])
    
    for role_info in sorted(roles_data, key=lambda x: x.get("position", 0), reverse=True):
        role_name = role_info.get("name")
        
        # Проверяем, существует ли уже роль
        existing_role = discord.utils.get(guild.roles, name=role_name)
        
        if existing_role:
            print(f"{Fore.YELLOW}Роль '{role_name}' уже существует{Style.RESET_ALL}")
            continue
        
        # Создаём роль
        try:
            color = hex_to_color(role_info.get("color", "#808080"))
            permissions = discord.Permissions()
            
            for perm in role_info.get("permissions", []):
                setattr(permissions, perm, True)
            
            role = await guild.create_role(
                name=role_name,
                color=color,
                permissions=permissions,
                hoist=role_info.get("hoist", False),
                mentionable=role_info.get("mentionable", False),
                reason="Настройка Nexus Prime Bot"
            )
            print(f"{Fore.GREEN}✓ Создана роль: {role_name}{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}✗ Ошибка создания роли '{role_name}': {e}{Style.RESET_ALL}")

async def setup_channels(guild, channels_config):
    """Создаёт каналы на сервере"""
    print(f"{Fore.CYAN}Настройка каналов...{Style.RESET_ALL}")
    
    categories_data = channels_config.get("categories", [])
    
    for category_info in categories_data:
        category_name = category_info.get("name")
        
        # Проверяем, существует ли категория
        existing_category = discord.utils.get(guild.categories, name=category_name)
        
        if not existing_category:
            try:
                category = await guild.create_category_channel(
                    name=category_name,
                    position=category_info.get("position", 0),
                    reason="Настройка Nexus Prime Bot"
                )
                print(f"{Fore.GREEN}✓ Создана категория: {category_name}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}✗ Ошибка создания категории '{category_name}': {e}{Style.RESET_ALL}")
                continue
        else:
            category = existing_category
            print(f"{Fore.YELLOW}Категория '{category_name}' уже существует{Style.RESET_ALL}")
        
        # Создаём каналы в категории
        for channel_info in category_info.get("channels", []):
            channel_name = channel_info.get("name")
            channel_type = channel_info.get("type", "text")
            
            # Проверяем, существует ли канал
            existing_channel = discord.utils.get(category.text_channels, name=channel_name)
            if not existing_channel and channel_type == "text":
                existing_channel = discord.utils.get(category.voice_channels, name=channel_name)
            
            if existing_channel:
                print(f"{Fore.YELLOW}Канал '{channel_name}' уже существует{Style.RESET_ALL}")
                continue
            
            try:
                if channel_type == "text":
                    await category.create_text_channel(
                        name=channel_name,
                        topic=channel_info.get("topic", ""),
                        reason="Настройка Nexus Prime Bot"
                    )
                elif channel_type == "voice":
                    await category.create_voice_channel(
                        name=channel_name,
                        reason="Настройка Nexus Prime Bot"
                    )
                
                print(f"{Fore.GREEN}✓ Создан канал: {channel_name}{Style.RESET_ALL}")
                
            except Exception as e:
                print(f"{Fore.RED}✗ Ошибка создания канала '{channel_name}': {e}{Style.RESET_ALL}")

@bot.event
async def on_ready():
    """Запускается при подключении бота"""
    print(f"\\n{Fore.GREEN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}NEXUS PRIME BOT - SETUP{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*50}{Style.RESET_ALL}\\n")
    
    config = load_config()
    if not config:
        print(f"{Fore.RED}Ошибка загрузки конфигурации!{Style.RESET_ALL}")
        await bot.close()
        return
    
    guild_id = config.get("GUILD_ID")
    if not guild_id:
        print(f"{Fore.RED}GUILD_ID не указан в конфигурации!{Style.RESET_ALL}")
        await bot.close()
        return
    
    try:
        guild = bot.get_guild(int(guild_id))
        
        if not guild:
            print(f"{Fore.RED}Сервер с ID {guild_id} не найден!{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Проверьте, что бот добавлен на сервер{Style.RESET_ALL}")
            await bot.close()
            return
        
        print(f"{Fore.CYAN}Подключено к серверу: {guild.name}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}ID сервера: {guild.id}{Style.RESET_ALL}\\n")
        
        # Загружаем конфиги
        roles_config = load_roles_config()
        channels_config = load_channels_config()
        
        if roles_config:
            await setup_roles(guild, roles_config)
        
        if channels_config:
            await setup_channels(guild, channels_config)
        
        print(f"\\n{Fore.GREEN}{'='*50}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}НАСТРОЙКА ЗАВЕРШЕНА!{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*50}{Style.RESET_ALL}\\n")
        
        await bot.close()
        
    except Exception as e:
        print(f"{Fore.RED}Ошибка: {e}{Style.RESET_ALL}")
        await bot.close()

if __name__ == "__main__":
    config = load_config()
    if config:
        token = config.get("BOT_TOKEN")
        if token and token != "YOUR_BOT_TOKEN_HERE":
            bot.run(token)
        else:
            print(f"{Fore.RED}Укажите токен бота в nexus_config.json!{Style.RESET_ALL}")
            sys.exit(1)
'''
        (base_dir / "nexus_setup.py").write_text(setup_content)
        print_success("Создан: nexus_setup.py")
        
        # nexus_bot.py
        bot_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nexus Prime Bot v1.3.1
Основной файл Discord-бота
Разработано для Вовы и Рокси
"""

import json
import sys
from pathlib import Path
from datetime import datetime

try:
    import discord
    from discord.ext import commands
    from colorama import init, Fore, Style, Back
    
    init()
except ImportError:
    print(f"{Fore.RED}Ошибка: Требуется установить зависимости!{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Выполните команду: pip install -r requirements.txt{Style.RESET_ALL}")
    sys.exit(1)


class NexusBot(commands.Bot):
    """Основной класс бота Nexus Prime"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix="!",
            intents=intents,
            description="Nexus Prime Bot v1.3.1 - Помощник сервера"
        )
        
        self.config = None
        self.start_time = None
    
    def load_config(self):
        """Загружает конфигурацию бота"""
        config_path = Path("nexus_config.json")
        
        if not config_path.exists():
            print(f"{Fore.RED}✗ Файл конфигурации не найден!{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Создайте nexus_config.json по примеру nexus_config.example.json{Style.RESET_ALL}")
            return False
        
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
            
            if not self.config.get("BOT_TOKEN"):
                print(f"{Fore.RED}✗ BOT_TOKEN не указан в конфигурации!{Style.RESET_ALL}")
                return False
            
            return True
            
        except json.JSONDecodeError:
            print(f"{Fore.RED}✗ Ошибка чтения файла конфигурации!{Style.RESET_ALL}")
            return False
    
    def print_startup_screen(self):
        """Выводит красивый стартовый экран"""
        banner = f"""
{Back.BLUE}{Fore.WHITE}                                                              {Style.RESET_ALL}
{Back.BLUE}{Fore.WHITE}                                                              {Style.RESET_ALL}
{Back.BLUE}{Fore.WHITE}   ██████╗ ██╗   ██╗██████╗ ███████╗██████╗ ███╗   ██╗        {Style.RESET_ALL}
{Back.BLUE}{Fore.WHITE}   ██╔══██╗╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗████╗  ██║        {Style.RESET_ALL}
{Back.BLUE}{Fore.WHITE}   ██████╔╝ ╚████╔╝ ██████╔╝█████╗  ██████╔╝██╔██╗ ██║        {Style.RESET_ALL}
{Back.BLUE}{Fore.WHITE}   ██╔══██╗  ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗██║╚██╗██║        {Style.RESET_ALL}
{Back.BLUE}{Fore.WHITE}   ██████╔╝   ██║   ██████╔╝███████╗██║  ██║██║ ╚████║        {Style.RESET_ALL}
{Back.BLUE}{Fore.WHITE}   ╚═════╝    ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝        {Style.RESET_ALL}
{Back.BLUE}{Fore.WHITE}                                                              {Style.RESET_ALL}
{Back.BLUE}{Fore.WHITE}              PRIME BOT v1.3.1                                {Style.RESET_ALL}
{Back.BLUE}{Fore.WHITE}              Разработано для Вовы и Рокси                    {Style.RESET_ALL}
{Back.BLUE}{Fore.WHITE}                                                              {Style.RESET_ALL}
"""
        print(banner)
        
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓ Система инициализирована{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓ Зависимости загружены{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓ Конфигурация загружена{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\\n")
    
    async def on_ready(self):
        """Событие при подключении к Discord"""
        self.start_time = datetime.now()
        
        self.print_startup_screen()
        
        print(f"{Fore.WHITE}┌─{'─'*58}┐{Style.RESET_ALL}")
        print(f"{Fore.WHITE}│{Style.RESET_ALL}  {Fore.CYAN}Информация о боте:{Style.RESET_ALL}{Fore.WHITE}{' '*40}│{Style.RESET_ALL}")
        print(f"{Fore.WHITE}├─{'─'*58}┤{Style.RESET_ALL}")
        print(f"{Fore.WHITE}│{Style.RESET_ALL}  {Fore.GREEN}✓{Style.RESET_ALL} Бот: {Fore.YELLOW}{self.user.name}#{self.user.discriminator}{Style.RESET_ALL}{Fore.WHITE}{' '*32}│{Style.RESET_ALL}")
        print(f"{Fore.WHITE}│{Style.RESET_ALL}  {Fore.GREEN}✓{Style.RESET_ALL} ID: {Fore.YELLOW}{self.user.id}{Style.RESET_ALL}{Fore.WHITE}{' '*42}│{Style.RESET_ALL}")
        print(f"{Fore.WHITE}│{Style.RESET_ALL}  {Fore.GREEN}✓{Style.RESET_ALL} Серверов: {Fore.YELLOW}{len(self.guilds)}{Style.RESET_ALL}{Fore.WHITE}{' '*38}│{Style.RESET_ALL}")
        print(f"{Fore.WHITE}│{Style.RESET_ALL}  {Fore.GREEN}✓{Style.RESET_ALL} Пользователей: {Fore.YELLOW}{sum(len(g.members) for g in self.guilds)}{Style.RESET_ALL}{Fore.WHITE}{' '*32}│{Style.RESET_ALL}")
        print(f"{Fore.WHITE}│{Style.RESET_ALL}  {Fore.GREEN}✓{Style.RESET_ALL} Время запуска: {Fore.YELLOW}{self.start_time.strftime('%H:%M:%S')}{Style.RESET_ALL}{Fore.WHITE}{' '*33}│{Style.RESET_ALL}")
        print(f"{Fore.WHITE}└─{'─'*58}┘{Style.RESET_ALL}\\n")
        
        # Играющий статус
        await self.change_presence(
            activity=discord.Game(name="!help | Nexus Prime v1.3.1")
        )
        
        print(f"{Fore.GREEN}Бот готов к работе!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Префикс команд: !{Style.RESET_ALL}\\n")
    
    async def on_command_error(self, ctx, error):
        """Обработка ошибок команд"""
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"{Fore.RED}Команда не найдена! Используйте `!help` для списка команд.{Style.RESET_ALL}")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(f"{Fore.RED}У вас недостаточно прав для этой команды!{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Ошибка команды: {error}{Style.RESET_ALL}")
    
    async def setup_commands(self):
        """Регистрирует команды бота"""
        
        @self.command(name="commands", aliases=["помощь"], help="Показать список команд")
        async def commands_help(ctx):
            embed = discord.Embed(
                title="📋 Список команд Nexus Prime",
                description="Доступные команды бота:",
                color=discord.Color.blue()
            )
            embed.add_field(name="!commands / !помощь", value="Показать этот список", inline=False)
            embed.add_field(name="!ping", value="Проверить пинг бота", inline=False)
            embed.add_field(name="!info", value="Информация о боте", inline=False)
            embed.add_field(name="!server", value="Информация о сервере", inline=False)
            embed.set_footer(text=f"Nexus Prime Bot v1.3.1 | Префикс: !")
            await ctx.send(embed=embed)
        
        @self.command(name="ping", help="Проверить пинг")
        async def ping_command(ctx):
            latency = round(self.latency * 1000)
            embed = discord.Embed(
                title="🏓 Пинг",
                description=f"`{latency} ms`",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        
        @self.command(name="info", help="Информация о боте")
        async def info_command(ctx):
            embed = discord.Embed(
                title="ℹ️ Информация о боте",
                color=discord.Color.blue()
            )
            embed.add_field(name="Название", value=self.user.name, inline=True)
            embed.add_field(name="Версия", value="1.3", inline=True)
            embed.add_field(name="Разработчик", value="Вова и Рокси", inline=True)
            embed.add_field(name="Серверов", value=len(self.guilds), inline=True)
            embed.add_field(name="Пользователей", value=sum(len(g.members) for g in self.guilds), inline=True)
            embed.set_thumbnail(url=self.user.display_avatar.url)
            await ctx.send(embed=embed)
        
        @self.command(name="server", help="Информация о сервере")
        async def server_command(ctx):
            guild = ctx.guild
            embed = discord.Embed(
                title=f"📊 Информация о сервере",
                description=guild.name,
                color=discord.Color.gold()
            )
            embed.add_field(name="Владелец", value=guild.owner.mention if guild.owner else "Неизвестно", inline=True)
            embed.add_field(name="Участников", value=guild.member_count, inline=True)
            embed.add_field(name="Ролей", value=len(guild.roles), inline=True)
            embed.add_field(name="Каналов", value=len(guild.channels), inline=True)
            embed.add_field(name="Категорий", value=len(guild.categories), inline=True)
            embed.add_field(name="Создан", value=guild.created_at.strftime("%d.%m.%Y"), inline=True)
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)
            await ctx.send(embed=embed)


async def main():
    """Основная функция запуска"""
    print(f"\\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}NEXUS PRIME BOT - Инициализация{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\\n")
    
    # Проверки при запуске
    print(f"{Fore.YELLOW}Проверка системы...{Style.RESET_ALL}")
    
    # Проверка Python версии
    if sys.version_info < (3, 8):
        print(f"{Fore.RED}✗ Требуется Python 3.8 или выше!{Style.RESET_ALL}")
        sys.exit(1)
    print(f"{Fore.GREEN}✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}{Style.RESET_ALL}")
    
    bot = NexusBot()
    
    # Загрузка конфигурации
    if not bot.load_config():
        sys.exit(1)
    print(f"{Fore.GREEN}✓ Конфигурация загружена{Style.RESET_ALL}")
    
    # Установка команд
    await bot.setup_commands()
    print(f"{Fore.GREEN}✓ Команды загружены{Style.RESET_ALL}")
    
    # Запуск бота
    token = bot.config.get("BOT_TOKEN")
    
    print(f"\\n{Fore.CYAN}Подключение к Discord...{Style.RESET_ALL}\\n")
    
    try:
        await bot.start(token)
    except discord.LoginFailure:
        print(f"{Fore.RED}✗ Ошибка авторизации! Проверьте токен в nexus_config.json{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}✗ Ошибка запуска: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        discord.utils.setup_logging()
    except AttributeError:
        pass
    
    import asyncio
    asyncio.run(main())
'''
        (base_dir / "nexus_bot.py").write_text(bot_content)
        print_success("Создан: nexus_bot.py")
        
        return True
        
    except Exception as e:
        print_error(f"Ошибка при создании файлов: {e}")
        return False


def install_requirements():
    """Устанавливает зависимости из requirements.txt"""
    print_info("Проверка зависимостей...")
    
    req_file = Path("nexus_prime_bot/requirements.txt")
    if not req_file.exists():
        print_warning("Файл requirements.txt не найден")
        return
    
    try:
        # Проверяем, установлены ли пакеты
        import discord
        import colorama
        print_success("Все зависимости установлены")
    except ImportError:
        print_warning("Установка зависимостей...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(req_file)])
            print_success("Зависимости установлены успешно")
        except subprocess.CalledProcessError:
            print_error("Не удалось установить зависимости")
            print_info("Установите вручную: pip install -r nexus_prime_bot/requirements.txt")


def start_process(script_name, display_name=None):
    """Запускает процесс и добавляет его в список запущенных"""
    if display_name is None:
        display_name = script_name
    
    script_path = Path("nexus_prime_bot") / script_name
    
    if not script_path.exists():
        print_error(f"Файл {script_name} не найден!")
        return False
    
    try:
        # Запускаем процесс с помощью Popen для управления
        proc = subprocess.Popen(
            [sys.executable, str(script_path)],
            cwd="nexus_prime_bot",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Сохраняем информацию о процессе
        running_processes[display_name] = {
            'process': proc,
            'pid': proc.pid,
            'script': script_name,
            'start_time': time.time()
        }
        
        # Сохраняем PID в файл
        save_pid_file(proc.pid, script_name)
        
        print_success(f"Запущен: {script_name} (PID: {proc.pid})")
        return True
        
    except Exception as e:
        print_error(f"Ошибка запуска {script_name}: {e}")
        return False


def run_bot_with_retry():
    """Запускает бота с обработкой ошибок"""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        # Запускаем бота
        proc = subprocess.Popen(
            [sys.executable, "nexus_prime_bot/nexus_bot.py"],
            cwd="nexus_prime_bot",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Ждём завершения
        stdout, stderr = proc.communicate()
        return_code = proc.returncode
        
        # Выводим лог бота
        if stdout:
            print(stdout)
        if stderr:
            print(stderr, file=sys.stderr)
        
        # Анализируем код возврата
        if return_code == 0:
            # Бот работает нормально
            return True
            
        elif return_code == 1:
            # Ошибка токена
            retry_count += 1
            print(f"\n{Colors.RED}{'='*60}{Colors.RESET}")
            print(f"{Colors.RED}❌ ОШИБКА ТОКЕНА!{Colors.RESET}")
            print(f"{Colors.RED}{'='*60}{Colors.RESET}\n")
            
            print("Для работы бота нужен токен Discord.")
            print("Как получить:")
            print("1. https://discord.com/developers/applications")
            print("2. Выберите ваше приложение")
            print("3. Раздел 'Bot'")
            print("4. Нажмите 'Reset Token' и скопируйте\n")
            
            token = input(f"{Colors.BLUE}Введите токен: {Colors.RESET}").strip()
            
            if token and len(token) > 20:
                # Сохраняем токен
                save_token_to_config(token)
                print(f"\n{Colors.GREEN}✓ Токен сохранён!{Colors.RESET}")
                print(f"{Colors.CYAN}Перезапуск бота...{Colors.RESET}\n")
                continue  # Пробуем снова
            else:
                print(f"{Colors.RED}✗ Неверный токен!{Colors.RESET}")
                continue
                
        elif return_code == 2:
            # Ошибка прав
            print(f"\n{Colors.YELLOW}⚠️  Требуются Privileged Intents!{Colors.RESET}")
            print("Откройте https://discord.com/developers/applications")
            print("→ Ваше приложение → Bot")
            print("→ Включите:")
            print("  - SERVER MEMBERS INTENT")
            print("  - MESSAGE CONTENT INTENT")
            print("  - PRESENCE INTENT\n")
            return False
            
        elif return_code == 3:
            # Ошибка сети
            print(f"{Colors.RED}✗ Ошибка сети! Проверьте интернет.{Colors.RESET}")
            return False
            
        else:
            # Другая ошибка
            print(f"{Colors.RED}✗ Неизвестная ошибка (код {return_code}){Colors.RESET}")
            if stderr:
                print(f"{Colors.RED}{stderr}{Colors.RESET}")
            return False
    
    print(f"{Colors.RED}✗ Превышено количество попыток{Colors.RESET}")
    return False


def run_bot():
    """Запускает основного бота с возможностью управления процессом"""
    print_info("Запуск Nexus Prime Bot...")
    print()
    
    bot_file = Path("nexus_prime_bot/nexus_bot.py")
    
    if not bot_file.exists():
        print_error("Файл nexus_bot.py не найден!")
        return False
    
    # Устанавливаем signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Запускаем бота через Popen
    if not start_process("nexus_bot.py", "nexus_bot"):
        return False
    
    # Показываем статус
    print(f"\n{Colors.CYAN}{Colors.BOLD}📊 СТАТУС ПРОЦЕССОВ:{Colors.RESET}")
    for name, proc_info in running_processes.items():
        pid = proc_info['pid']
        status = "работает" if proc_info['process'].poll() is None else "остановлен"
        print(f"   ✓ {name} (PID: {pid}) - {status}")
    
    print(f"\n{Colors.YELLOW}Нажмите Ctrl+C для остановки всех процессов{Colors.RESET}\n")
    
    # Ждём завершения процесса бота
    proc_info = running_processes.get('nexus_bot')
    if proc_info:
        proc = proc_info['process']
        try:
            # Выводим stdout бота в реальном времени
            while proc.poll() is None:
                line = proc.stdout.readline()
                if line:
                    print(line, end='')
                time.sleep(0.1)
            
            # Процесс завершился
            return_code = proc.returncode
            if return_code == 0:
                print(f"\n{Colors.GREEN}Бот завершил работу корректно{Colors.RESET}")
            else:
                print(f"\n{Colors.RED}Бот завершил работу с кодом {return_code}{Colors.RESET}")
            
            return return_code == 0
            
        except KeyboardInterrupt:
            # Пользователь нажал Ctrl+C
            stop_all_processes()
            return True
        except Exception as e:
            print_error(f"Ошибка при выполнении бота: {e}")
            return False
    
    return True


def main():
    """Главная функция лаунчера"""
    print_banner()
    
    # Сначала - диагностика системы
    print_system_diagnostics()
    
    # Проверяем наличие интернета
    has_internet = check_internet_connection()
    
    # Проверяем, существует ли папка проекта
    base_dir = Path("nexus_prime_bot")
    
    if not base_dir.exists():
        print_info("Первый запуск! Создание проекта...")
        print()
        
        if not create_project_structure():
            print_error("Не удалось создать структуру проекта")
            sys.exit(1)
        
        print()
        print_success("Проект создан успешно!")
        print()
        print_info("Следующие шаги:")
        print(f"  1. Откройте {Colors.CYAN}nexus_prime_bot/nexus_config.json{Colors.RESET}")
        print("  2. Вставьте токен вашего бота Discord")
        print("  3. Вставьте ID вашего сервера")
        print(f"  4. Установите зависимости: {Colors.YELLOW}pip install -r nexus_prime_bot/requirements.txt{Colors.RESET}")
        print(f"  5. Запустите бота повторно: {Colors.GREEN}python launcher.py{Colors.RESET}")
        print()
        
        # Предлагаем установить зависимости сразу
        response = input(f"{Colors.BLUE}Установить зависимости сейчас? (y/n): {Colors.RESET}")
        if response.lower() == 'y':
            install_requirements()
        
        return
    
    # Проект уже существует
    print_success("Проект обнаружен")
    
    # Проверяем обновления
    update_status = check_for_updates(has_internet)
    
    # Если доступно обновление и есть git
    if update_status == 'update_available' and Path(".git").exists():
        response = input(f"\n{Colors.YELLOW}Обновить бота? (y/n): {Colors.RESET}")
        if response.lower() == 'y':
            if run_git_pull():
                print_success("Обновление завершено!")
            else:
                print_warning("Обновление не выполнено")
    elif not Path(".git").exists():
        print_info("Git репозиторий не обнаружен, проверка обновлений пропущена")
    
    print()
    
    # Устанавливаем зависимости
    install_requirements()
    
    print()
    
    # Запускаем бота
    print(f"\n{Colors.CYAN}{Colors.BOLD}🚀 Запуск Nexus Prime Bot...{Colors.RESET}\n")
    if run_bot_with_retry():
        print_success("Бот запущен!")
    else:
        print_error("Не удалось запустить бота")
        sys.exit(1)


if __name__ == "__main__":
    # Устанавливаем глобальные signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}✨ Бот остановлен пользователем{Colors.RESET}")
        stop_all_processes()
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Критическая ошибка: {e}{Colors.RESET}")
        stop_all_processes()
        sys.exit(1)
