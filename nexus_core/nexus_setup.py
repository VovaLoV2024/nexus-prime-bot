"""
Nexus Setup - Утилита для первоначальной настройки бота
"""
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "nexus_config.json")
EXAMPLE_PATH = os.path.join(SCRIPT_DIR, "nexus_config.example.json")

def main():
    print("╔══════════════════════════════════════════════════════╗")
    print("║         NEXUS PRIME BOT - SETUP UTILITY             ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()
    
    # Проверяем, существует ли уже конфиг
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        if config.get("bot_token"):
            print("✓ Конфигурация уже настроена!")
            return
    
    # Копируем пример в конфиг
    if os.path.exists(EXAMPLE_PATH):
        with open(EXAMPLE_PATH, "r", encoding="utf-8") as f:
            example = json.load(f)
        
        config = {
            "bot_token": "",
            "guild_id": "",
            "owner_id": ""
        }
        
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print("✓ Создан файл конфигурации nexus_config.json")
    
    print()
    print("Для запуска бота используйте: python launcher.py")
    print("Launcher сам запросит токен при первом запуске.")

if __name__ == "__main__":
    main()
