#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nexus Prime Bot v1.3.2
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
            description="Nexus Prime Bot v1.3.2 - Помощник сервера"
        )
        
        self.config = None
        self.start_time = None
        self.owner_id = None
    
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
            
            # Поддержка старых и новых ключей
            token = self.config.get("bot_token") or self.config.get("BOT_TOKEN")
            if not token:
                print(f"{Fore.RED}✗ BOT_TOKEN не указан в конфигурации!{Style.RESET_ALL}")
                return False
            
            # Загружаем ID владельца
            self.owner_id = self.config.get("owner_id", "")
            
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
{Back.BLUE}{Fore.WHITE}              PRIME BOT v1.3.2                                {Style.RESET_ALL}
{Back.BLUE}{Fore.WHITE}              Разработано для Вовы и Рокси                    {Style.RESET_ALL}
{Back.BLUE}{Fore.WHITE}                                                              {Style.RESET_ALL}
"""
        print(banner)
        
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓ Система инициализирована{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓ Зависимости загружены{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓ Конфигурация загружена{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    
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
        print(f"{Fore.WHITE}└─{'─'*58}┘{Style.RESET_ALL}\n")
        
        # Играющий статус
        await self.change_presence(
            activity=discord.Game(name="!help | Nexus Prime v1.3.2")
        )
        
        print(f"{Fore.GREEN}Бот готов к работе!{Style.RESET_ALL}")

        print(f"{Fore.CYAN}Префикс команд: !{Style.RESET_ALL}\n")

        # Проверка владельца
        if not self.owner_id:
            print(f"{Fore.YELLOW}⚠️ ВЛАДЕЛЕЦ НЕ УСТАНОВЛЕН{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Напишите команду !прайм для установки владельца{Style.RESET_ALL}\n")
        else:
            try:
                owner = await self.fetch_user(int(self.owner_id))
                print(f"{Fore.GREEN}✓ Владелец: @{owner.name}{Style.RESET_ALL}\n")
            except Exception:
                print(f"{Fore.GREEN}✓ Владелец установлен (ID: {self.owner_id}){Style.RESET_ALL}\n")

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
            embed.set_footer(text=f"Nexus Prime Bot v1.3 | Префикс: !")
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

        # Команды владельца
        @self.command(name="прайм", aliases=["owner", "владелец"], help="Установить владельца (только если не установлен)")
        async def owner_command(ctx):
            """Команда для установки владельца"""
            config_path = Path("nexus_config.json")
            
            # Проверяем, установлен ли уже владелец
            if self.owner_id:
                try:
                    owner = await self.fetch_user(int(self.owner_id))
                    await ctx.send(f"⛔ Владелец уже установлен: @{owner.name}")
                except Exception:
                    await ctx.send(f"⛔ Владелец уже установлен (ID: {self.owner_id})")
                return
            
            # Устанавливаем владельца
            self.owner_id = str(ctx.author.id)
            
            # Сохраняем в конфиг
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                
                config["owner_id"] = self.owner_id
                
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                await ctx.send(f"✅ {ctx.author.name} ({ctx.author.display_name}), вы назначены владельцем Нексус Прайм!\nТеперь вы можете использовать команды управления.")
            except Exception as e:
                await ctx.send(f"❌ Ошибка при сохранении: {e}")

        @self.command(name="показать_владельца", aliases=["кто_владелец"], help="Показать кто владелец")
        async def show_owner_command(ctx):
            """Показать владельца"""
            if not self.owner_id:
                await ctx.send("⚠️ Владелец ещё не установлен.\nИспользуйте команду !прайм для установки.")
                return
            
            try:
                owner = await self.fetch_user(int(self.owner_id))
                await ctx.send(f"👑 Владелец проекта: @{owner.name} (ID: {self.owner_id})")
            except Exception:
                await ctx.send(f"👑 Владелец проекта (ID: {self.owner_id})")

        @self.command(name="статус", help="Показать статус бота")
        async def status_command(ctx):
            """Показать статус бота"""
            owner_text = "Не установлен"
            if self.owner_id:
                try:
                    owner = await self.fetch_user(int(self.owner_id))
                    owner_text = f"@{owner.name}"
                except Exception:
                    owner_text = f"ID: {self.owner_id}"
            
            embed = discord.Embed(
                title="🌌 NEXUS PRIME BOT v1.3.2",
                color=discord.Color.blue()
            )
            embed.add_field(name="Владелец", value=owner_text, inline=False)
            embed.add_field(name="Серверов", value=len(self.guilds), inline=True)
            embed.add_field(name="Пользователей", value=sum(len(g.members) for g in self.guilds), inline=True)
            embed.add_field(name="Статус", value="онлайн", inline=True)
            embed.set_footer(text=f"Nexus Prime Bot v1.3.2")
            await ctx.send(embed=embed)

        # Проверка прав владельца
        def is_owner_check():
            async def predicate(ctx):
                if not self.owner_id:
                    return True  # Если владелец не установлен, разрешаем все команды
                return str(ctx.author.id) == self.owner_id
            
            if not self.owner_id:
                return True
            return commands.check(predicate)


async def main():
    """Основная функция запуска"""
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}NEXUS PRIME BOT - Инициализация{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    
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
        print(f"{Fore.RED}✗ Конфигурация не загружена{Style.RESET_ALL}")
        sys.exit(1)
    print(f"{Fore.GREEN}✓ Конфигурация загружена{Style.RESET_ALL}")
    
    # Установка команд
    await bot.setup_commands()
    print(f"{Fore.GREEN}✓ Команды загружены{Style.RESET_ALL}")
    
    # Запуск бота
    token = (bot.config.get("bot_token") or bot.config.get("BOT_TOKEN"))
    
    if not token:
        print(f"{Fore.RED}✗ Токен не указан{Style.RESET_ALL}")
        sys.exit(1)
    
    print(f"\n{Fore.CYAN}Подключение к Discord...{Style.RESET_ALL}\n")
    
    try:
        await bot.start(token)
    except discord.LoginFailure:
        print(f"{Fore.RED}✗ Неверный токен!{Style.RESET_ALL}")
        sys.exit(1)
    except discord.PrivilegedIntentsRequired:
        print(f"{Fore.RED}✗ Требуются Privileged Intents!{Style.RESET_ALL}")
        sys.exit(2)
    except Exception as e:
        if "network" in str(e).lower() or "connection" in str(e).lower():
            sys.exit(3)
        else:
            print(f"{Fore.RED}✗ Ошибка: {e}{Style.RESET_ALL}")
            sys.exit(4)


if __name__ == "__main__":
    try:
        discord.utils.setup_logging()
    except AttributeError:
        pass
    
    import asyncio
    asyncio.run(main())
