import os
import json
import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
from urllib.parse import urlparse


import YouTubeDLP


def get_from_config(request_data, file_path='json/config.json'):
    try:
        with open(file_path, 'r') as file:
            config = json.load(file)
            data_config = config.get(request_data)
            if data_config:
                return data_config
            else:
                raise ValueError(f"({request_data}) NOT found in the config file.")
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    except json.JSONDecodeError:
        raise ValueError(f"Error decoding JSON from the file {file_path}.")


discord_token = get_from_config('discord_token')                 # Запрашиваем Discord токен из файла конфига
download_folder = get_from_config('download_folder')            # Запрашиваем папку для сохранения аудиофайлов
# format_YouTube_DLP = get_from_config('format_YouTube_DLP')      # Запрашиваем формат из конфига
# outtmpl_YouTube_DLP = get_from_config('outtmpl_YouTube_DLP')
if not os.path.exists(download_folder):
    os.makedirs(download_folder)

FFMPEG_EXE = r'C:/Program Files/ffmpeg/bin/ffmpeg.exe'  # Указываем путь к исполняемому файлу ffmpeg на вашей системе

intents = discord.Intents.default()     # Создаем объект Intents для управления доступом к событиям
intents.message_content = True          # Включаем доступ к содержимому сообщений (если нужно)
intents.presences = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)     # Создаем экземпляр бота с префиксом команд '!'.


def get_netloc(url):
    return urlparse(url).netloc


@bot.event
# Этот метод вызывается, когда бот успешно подключился к Discord.
async def on_ready():
    print(f'Logged in as {bot.user}')


@bot.command()
# Команда '!join' подключает бота к голосовому каналу пользователя.
async def join(ctx):
    if ctx.author.voice:
        # Проверяем, подключен ли пользователь к голосовому каналу.
        channel = ctx.author.voice.channel
        # Подключаемся к голосовому каналу.
        await channel.connect()
        # Отправляем сообщение в текстовый канал, чтобы подтвердить подключение.
        await ctx.send(f'Подключился к каналу {channel.name}')
    else:
        # Если пользователь не в голосовом канале, отправляем сообщение об ошибке.
        await ctx.send('Вы не подключены к голосовому каналу')


@bot.command()
async def leave(ctx):   # Команда '!leave' отключает бота от голосового канала.
    if ctx.voice_client:
        # Проверяем, подключен ли бот к голосовому каналу.
        await ctx.voice_client.disconnect()
        # Отправляем сообщение в текстовый канал, чтобы подтвердить отключение.
        await ctx.send('Отключился от канала')
    else:
        # Если бот не подключен к голосовому каналу, отправляем сообщение об ошибке.
        await ctx.send('Я не в голосовом канале')


@bot.command()
# Команда '!stop' останавливает воспроизведение аудиофайл в голосовом канале.
async def stop(ctx):
    ctx.voice_client.stop()  # Останавливаем текущее воспроизведение, если оно есть.


@bot.command()
# Команда '!play' воспроизводит аудиофайл в голосовом канале.
async def play(ctx, *, file: str):
    if ctx.voice_client:
        if get_netloc(file) == get_netloc('https://www.youtube.com')    \
                or get_netloc(file) == get_netloc(f'https://music.youtube.com'):
            file = YouTubeDLP.youtube_download(file, download_folder)
        # Проверяем, подключен ли бот к голосовому каналу.
        ctx.voice_client.stop()  # Останавливаем текущее воспроизведение, если оно есть.
        # Создаем объект FFmpegPCMAudio для воспроизведения аудиофайла.
        source = FFmpegPCMAudio(f'{download_folder}/{file}', executable=FFMPEG_EXE)
        # source = FFmpegPCMAudio(file)
        # Воспроизводим аудио в голосовом канале.
        ctx.voice_client.play(source)
        # Отправляем сообщение в текстовый канал, чтобы подтвердить воспроизведение файла.
        await ctx.send(f'Воспроизведён файл {file}')
    else:
        # Если бот не подключен к голосовому каналу, отправляем сообщение об ошибке.
        await ctx.send('Я не подключен к голосовому каналу')


bot.run(discord_token)  # Запускаем бота с использованием токена.
