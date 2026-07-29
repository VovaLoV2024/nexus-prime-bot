#!/usr/bin/env python3
"""
Nexus Prime Bot Setup Script
Скрипт для первоначальной настройки бота
"""

import os
import json
import sys
from pathlib import Path

def main():
    """Основная функция настройки"""
    print("=" * 50)
    print("NEXUS PRIME BOT - SETUP SCRIPT")
    print("=" * 50)
    print()
    
    # Путь к конфигу
    bot_dir = Path(__file__).parent
    config_path = bot_dir / "nexus_config.json"
    
    # Создаем конфиг если не существует
    if not config_path.exists():
        print("Создание конфигурации...")
        config = {
            "bot_token": "",
            "guild_id": "",
            "owner_id": ""
        }
        
        print("\nДля работы бота необходим токен Discord.")
        print("Получить токен: https://discord.com/developers/applications")
        print()
        
        token = input("Введите токен вашего бота: ").strip()
        if token:
            config["bot_token"] = token
        
        guild_id = input("Введите ID сервера (необязательно): ").strip()
        if guild_id:
            config["guild_id"] = guild_id
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Конфигурация сохранена в {config_path}")
    else:
        print(f"Конфигурация уже существует: {config_path}")
        print("Удалите файл для повторной настройки.")
    
    print("\nТеперь запустите launcher.py для запуска бота!")
    print("=" * 50)

if __name__ == "__main__":
    main()
