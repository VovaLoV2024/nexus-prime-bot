import discord
from discord.ext import commands
import json
import sys
import os

# Получаем путь к директории бота
BOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BOT_DIR, "nexus_config.json")

def load_config():
    """Загружает конфигурацию из nexus_config.json"""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Ошибка: nexus_config.json не найден!")
        sys.exit(1)
    except json.JSONDecodeError:
        print("❌ Ошибка: nexus_config.json содержит некорректный JSON!")
        sys.exit(1)

def save_config(config):
    """Сохраняет конфигурацию в nexus_config.json"""
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

# Загружаем конфиг
config = load_config()

# Проверяем токен
bot_token = config.get("bot_token", "").strip()
if not bot_token:
    print("❌ Ошибка: bot_token пустой! Пожалуйста, укажите токен вашего бота.")
    sys.exit(1)

guild_id = config.get("guild_id", "")
owner_id = config.get("owner_id", "")

# Создаем бота
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

try:
    bot = commands.Bot(command_prefix='!', intents=intents)
except Exception as e:
    print(f"❌ Ошибка инициализации бота: {e}")
    print("💡 Возможно, не включены Privileged Intents в настройках бота на Discord Developer Portal")
    sys.exit(2)

@bot.event
async def on_ready():
    print(f"✅ Бот запущен как {bot.user.name} (ID: {bot.user.id})")
    print(f"📊 Подключен к {len(bot.guilds)} серверам")
    print("=" * 50)

@bot.command(name="помощь", aliases=["команды"])
async def help_command(ctx):
    """Показывает список команд"""
    embed = discord.Embed(
        title="🤖 Nexus Prime Bot - Команды",
        description="Список доступных команд:",
        color=discord.Color.blue()
    )
    embed.add_field(name="!помощь", value="Показать этот список команд", inline=False)
    embed.add_field(name="!пинг", value="Проверить пинг бота", inline=False)
    embed.add_field(name="!инфо", value="Информация о боте", inline=False)
    embed.add_field(name="!сервер", value="Информация о сервере", inline=False)
    embed.add_field(name="!прайм", value="Установить владельца (только для автора сообщения)", inline=False)
    embed.add_field(name="!статус", value="Показать статус бота", inline=False)
    embed.set_footer(text=f"Nexus Prime Bot v1.4.1 | Автор: Вова (VovaLoV)")
    await ctx.send(embed=embed)

@bot.command(name="пинг", aliases=["ping"])
async def ping_command(ctx):
    """Проверяет пинг бота"""
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Пинг: **{latency}ms**")

@bot.command(name="инфо", aliases=["info", "бот"])
async def info_command(ctx):
    """Показывает информацию о боте"""
    embed = discord.Embed(
        title="ℹ️ Информация о боте",
        description="Nexus Prime Bot - бот для управления мультивселенной Нексус Прайм",
        color=discord.Color.green()
    )
    embed.add_field(name="Версия", value="1.4.1 (Beta)", inline=True)
    embed.add_field(name="Библиотека", value="discord.py", inline=True)
    embed.add_field(name="Серверов", value=str(len(bot.guilds)), inline=True)
    embed.add_field(name="Разработчик", value="Вова (VovaLoV)", inline=False)
    embed.add_field(name="Помощница", value="Рокси 🐺", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="сервер", aliases=["server", "guild"])
async def server_command(ctx):
    """Показывает информацию о сервере"""
    guild = ctx.guild
    if guild is None:
        await ctx.send("Эта команда работает только на сервере!")
        return
    
    embed = discord.Embed(
        title=f"📊 Информация о сервере: {guild.name}",
        color=discord.Color.purple()
    )
    embed.add_field(name="ID сервера", value=str(guild.id), inline=True)
    embed.add_field(name="Владелец", value=str(guild.owner), inline=True)
    embed.add_field(name="Участников", value=str(guild.member_count), inline=True)
    embed.add_field(name="Каналов", value=str(len(guild.channels)), inline=True)
    embed.add_field(name="Ролей", value=str(len(guild.roles)), inline=True)
    embed.add_field(name="Регион", value=str(guild.region), inline=True)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    await ctx.send(embed=embed)

@bot.command(name="прайм", aliases=["owner", "владелец"])
async def prime_command(ctx):
    """Устанавливает владельца бота"""
    global owner_id
    # Устанавливаем автора команды как владельца
    owner_id = str(ctx.author.id)
    config["owner_id"] = owner_id
    save_config(config)
    
    embed = discord.Embed(
        title="👑 Владелец установлен!",
        description=f"Теперь **{ctx.author.name}** является владельцем Nexus Prime Bot!",
        color=discord.Color.gold()
    )
    embed.add_field(name="ID владельца", value=owner_id, inline=False)
    embed.set_footer(text="Команда !прайм выполнена успешно")
    await ctx.send(embed=embed)
    print(f"✅ Владелец установлен: {ctx.author.name} (ID: {owner_id})")

@bot.command(name="статус", aliases=["status"])
async def status_command(ctx):
    """Показывает статус бота"""
    embed = discord.Embed(
        title="📈 Статус бота",
        color=discord.Color.blue()
    )
    embed.add_field(name="Статус", value="🟢 Онлайн", inline=True)
    embed.add_field(name="Пинг", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="Версия", value="1.4.1", inline=True)
    embed.add_field(name="Владелец", value=f"<@{owner_id}>" if owner_id else "Не установлен", inline=False)
    embed.add_field(name="Серверов", value=str(len(bot.guilds)), inline=True)
    embed.add_field(name="Пользователей", value=str(len(set(bot.get_all_members()))), inline=True)
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    """Обрабатывает ошибки команд"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Команда не найдена! Используйте `!помощь` для списка команд.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ У вас недостаточно прав для выполнения этой команды!")
    else:
        print(f"Ошибка команды: {error}")
        await ctx.send(f"❌ Произошла ошибка: {error}")

# Запускаем бота
try:
    bot.run(bot_token)
except discord.LoginFailure:
    print("❌ Ошибка: Неверный токен бота!")
    sys.exit(1)
except discord.PrivilegedIntentsRequired:
    print("❌ Ошибка: Требуется включить Privileged Intents!")
    print("💡 Перейдите на https://discord.com/developers/applications")
    print("   Выберите ваше приложение → Bot → Privileged Gateway Intents")
    print("   Включите MESSAGE CONTENT INTENT и SERVER MEMBERS INTENT")
    sys.exit(2)
except Exception as e:
    print(f"❌ Ошибка запуска бота: {e}")
    sys.exit(4)
