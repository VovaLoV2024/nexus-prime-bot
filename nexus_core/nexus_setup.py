#!/usr/bin/env python3
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
    print(f"\n{Fore.GREEN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}NEXUS PRIME BOT - SETUP{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*50}{Style.RESET_ALL}\n")
    
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
        print(f"{Fore.CYAN}ID сервера: {guild.id}{Style.RESET_ALL}\n")
        
        # Загружаем конфиги
        roles_config = load_roles_config()
        channels_config = load_channels_config()
        
        if roles_config:
            await setup_roles(guild, roles_config)
        
        if channels_config:
            await setup_channels(guild, channels_config)
        
        print(f"\n{Fore.GREEN}{'='*50}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}НАСТРОЙКА ЗАВЕРШЕНА!{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*50}{Style.RESET_ALL}\n")
        
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
