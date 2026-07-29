import discord
from discord.ext import commands
import json
import sys
import os
import sys
import asyncio
sys.stdout.reconfigure(encoding='utf-8')

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

@bot.command(name="помощь", aliases=["команды", "helpcmd"])
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
    embed.add_field(name="!статус", value="Показать статус бота", inline=False)
    embed.set_footer(text=f"Nexus Prime Bot v1.4.5 | Автор: Вова (VovaLoV)")
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
    embed.add_field(name="Версия", value="1.4.5 (Beta)", inline=True)
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
    """Секретная команда владельца - скрыта из помощи"""
    global owner_id
    config_path = CONFIG_PATH
    
    # Читаем актуальный конфиг
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            current_config = json.load(f)
        existing_owner_id = current_config.get("owner_id", "")
    except FileNotFoundError:
        current_config = {"bot_token": "", "guild_id": "", "owner_id": ""}
        existing_owner_id = ""
    except json.JSONDecodeError:
        return
    
    # ПЕРВЫЙ ЗАПУСК - владелец ещё не назначен
    if not existing_owner_id:
        # Запрос подтверждения (можно добавить реакцию или таймаут)
        confirm_msg = await ctx.send(f"🔐 {ctx.author.mention}, вы хотите стать владельцем Nexus Prime Bot?\nНажмите ✅ для подтверждения.")
        await confirm_msg.add_reaction("✅")
        
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == "✅" and reaction.message.id == confirm_msg.id
        
        try:
            await bot.wait_for("reaction_add", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("⏱ Время вышло. Команда отменена.")
            return
        
        # Сохраняем владельца
        new_owner_id = str(ctx.author.id)
        current_config["owner_id"] = new_owner_id
        owner_id = new_owner_id
        
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(current_config, f, indent=2, ensure_ascii=False)
            
            # Публичный эмбед только для первой привязки
            embed = discord.Embed(
                title="👑 Владелец установлен!",
                description=f"Теперь **{ctx.author.name}** является владельцем Nexus Prime Bot!",
                color=discord.Color.gold()
            )
            embed.add_field(name="ID владельца", value=new_owner_id, inline=False)
            embed.set_footer(text="Команда !прайм выполнена успешно")
            await ctx.send(embed=embed)
            print(f"✅ Владелец установлен: {ctx.author.name} (ID: {new_owner_id})")
        except Exception as e:
            await ctx.send(f"❌ Ошибка при сохранении: {e}")
        return
    
    # ВЛАДЕЛЕЦ уже назначен - проверяем, тот ли это пользователь
    if str(ctx.author.id) == existing_owner_id:
        # Это владелец - удаляем сообщение и отправляем ЛС со списком команд
        try:
            await ctx.message.delete()
        except discord.errors.Forbidden:
            pass  # Нет прав на удаление
        
        # Формируем список всех команд (включая секретные)
        embed = discord.Embed(
            title="🔐 Nexus Prime Bot - Панель Владельца",
            description="Полный список доступных команд:",
            color=discord.Color.gold()
        )
        embed.add_field(name="!помощь", value="Показать публичный список команд", inline=False)
        embed.add_field(name="!пинг", value="Проверить пинг бота", inline=False)
        embed.add_field(name="!инфо", value="Информация о боте", inline=False)
        embed.add_field(name="!сервер", value="Информация о сервере", inline=False)
        embed.add_field(name="!статус", value="Показать статус бота", inline=False)
        embed.add_field(name="!прайм", value="🔥 СЕКРЕТНАЯ: Открыть панель владельца (эта команда)", inline=False)
        embed.add_field(name="!загрузить", value="🔥 СЕКРЕТНАЯ: Перезагрузить конфигурацию", inline=False)
        embed.add_field(name="!перезапуск", value="🔥 СЕКРЕТНАЯ: Перезапустить бота", inline=False)
        embed.add_field(name="!остановить", value="🔥 СЕКРЕТНАЯ: Остановить бота", inline=False)
        embed.set_footer(text=f"Nexus Prime Bot v1.4.5 | Автор: Вова (VovaLoV)")
        
        try:
            await ctx.author.send(embed=embed)
        except discord.errors.Forbidden:
            await ctx.send("⚠ Не удалось отправить ЛС. Проверьте настройки приватности.", delete_after=5)
    else:
        # НЕ ВЛАДЕЛЕЦ пишет команду - удаляем и молчим (или временное сообщение)
        try:
            await ctx.message.delete()
        except discord.errors.Forbidden:
            pass
        
        # Временное сообщение которое удалится через 3 секунды
        temp_msg = await ctx.send("⛔ Неверная команда", delete_after=3)

@bot.command(name="статус", aliases=["status"])
async def status_command(ctx):
    """Показывает статус бота"""
    embed = discord.Embed(
        title="📈 Статус бота",
        color=discord.Color.blue()
    )
    embed.add_field(name="Статус", value="🟢 Онлайн", inline=True)
    embed.add_field(name="Пинг", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="Версия", value="1.4.5", inline=True)
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
