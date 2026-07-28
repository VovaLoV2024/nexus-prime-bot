import discord
from discord.ext import commands
import json
import sys
import os

# Получаем путь к директории скрипта
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "nexus_config.json")

def load_config():
    """Загружает конфигурацию из файла"""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Ошибка: файл конфигурации не найден!")
        sys.exit(4)
    except json.JSONDecodeError:
        print("Ошибка: неверный формат конфигурации!")
        sys.exit(4)

def save_config(config):
    """Сохраняет конфигурацию в файл"""
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

# Загружаем конфиг
config = load_config()

# Проверяем токен
bot_token = config.get("bot_token", "")
if not bot_token:
    print("Ошибка: токен бота пустой!")
    sys.exit(1)

guild_id = config.get("guild_id", "")
owner_id = config.get("owner_id", "")

# Создаем бота с необходимыми интентами
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

try:
    bot = commands.Bot(command_prefix="!", intents=intents)
except Exception as e:
    print(f"Ошибка при создании бота: {e}")
    print("Возможно, не включены Privileged Intents в настройках бота!")
    sys.exit(2)

@bot.event
async def on_ready():
    print(f"Nexus Prime Bot запущен как {bot.user}")
    print(f"ID: {bot.user.id}")
    if guild_id:
        print(f"Сервер ID: {guild_id}")
    if owner_id:
        print(f"Владелец ID: {owner_id}")

@bot.command(name="помощь")
@bot.command(name="commands")
async def help_command(ctx):
    """Показывает список команд"""
    embed = discord.Embed(
        title="📋 Nexus Prime Bot - Команды",
        color=discord.Color.blue()
    )
    embed.add_field(name="!помощь / !commands", value="Список команд", inline=False)
    embed.add_field(name="!пинг", value="Проверить пинг бота", inline=False)
    embed.add_field(name="!инфо", value="Информация о боте", inline=False)
    embed.add_field(name="!сервер", value="Информация о сервере", inline=False)
    embed.add_field(name="!прайм", value="Установить владельца", inline=False)
    embed.add_field(name="!статус", value="Показать статус бота", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="пинг")
async def ping_command(ctx):
    """Проверяет пинг бота"""
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Пинг: {latency}ms")

@bot.command(name="инфо")
async def info_command(ctx):
    """Показывает информацию о боте"""
    embed = discord.Embed(
        title="ℹ️ Информация о боте",
        description="Nexus Prime Bot v1.4.0 (Beta)",
        color=discord.Color.green()
    )
    embed.add_field(name="Разработчик", value="Qwen Coder", inline=True)
    embed.add_field(name="Создатель", value="Вова (VovaLoV)", inline=True)
    embed.add_field(name="Помощница", value="Рокси 🐺", inline=True)
    embed.add_field(name="Библиотека", value="discord.py", inline=True)
    embed.add_field(name="Серверов", value=str(len(bot.guilds)), inline=True)
    await ctx.send(embed=embed)

@bot.command(name="сервер")
async def server_command(ctx):
    """Показывает информацию о сервере"""
    if ctx.guild:
        embed = discord.Embed(
            title=f"🏰 {ctx.guild.name}",
            color=discord.Color.purple()
        )
        embed.add_field(name="ID сервера", value=str(ctx.guild.id), inline=True)
        embed.add_field(name="Участников", value=str(ctx.guild.member_count), inline=True)
        embed.add_field(name="Каналов", value=str(len(ctx.guild.channels)), inline=True)
        embed.add_field(name="Ролей", value=str(len(ctx.guild.roles)), inline=True)
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Эта команда работает только на сервере!")

@bot.command(name="прайм")
async def prime_command(ctx):
    """Устанавливает владельца бота"""
    if ctx.author.id == int(owner_id) if owner_id else True:
        config["owner_id"] = str(ctx.author.id)
        save_config(config)
        await ctx.send(f"✅ Владелец установлен: <@{ctx.author.id}>")
    else:
        await ctx.send("❌ Только текущий владелец может изменить эту настройку!")

@bot.command(name="статус")
async def status_command(ctx):
    """Показывает статус бота"""
    embed = discord.Embed(
        title="📊 Статус бота",
        color=discord.Color.gold()
    )
    embed.add_field(name="Статус", value="🟢 Онлайн", inline=True)
    embed.add_field(name="Пинг", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="Версия", value="1.4.0", inline=True)
    if owner_id:
        embed.add_field(name="Владелец", value=f"<@{owner_id}>", inline=True)
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Команда не найдена! Используйте !помощь для списка команд.")
    else:
        print(f"Ошибка команды: {error}")

# Запускаем бота
try:
    bot.run(bot_token)
except discord.errors.LoginFailure:
    print("Ошибка: недействительный токен бота!")
    sys.exit(1)
except Exception as e:
    print(f"Ошибка при запуске бота: {e}")
    sys.exit(4)
