import os
import json
import yt_dlp


def get_from_configYouTubeDLP(request_data, file_path='json/configYouTubeDLP.json'):
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


download_folder_config = get_from_configYouTubeDLP('download_folder')            # Запрашиваем папку для сохранения аудиофайлов
format_cfg = get_from_configYouTubeDLP('format_YouTube_DLP')      # Запрашиваем формат из конфига
outtmpl_cfg = get_from_configYouTubeDLP('outtmpl_YouTube_DLP')
embed_thumbnail_cfg = get_from_configYouTubeDLP('embed_thumbnail_YouTube_DLP')
if not os.path.exists(download_folder_config):
    os.makedirs(download_folder_config)


# def youtube_download(url, download_folder, outtmpl_DLP='%(id)s.%(ext)s', format_DLP='bestaudio/best'):
def youtube_download(url, download_folder=download_folder_config):
    ydl_opts = {
        # 'listformats': True,
        'format': f'{format_cfg}',                      # 'bestaudio/best' автоатически выберает лучшый формат аудио
        'outtmpl': f'{download_folder}/{outtmpl_cfg}',  # Имя файла на выходе
        'postprocessors': [
            {
                'key': 'FFmpegMetadata',  # Встраивает метаданные, такие как обложка
                'add_metadata': True,
            },
            {
                'key': 'EmbedThumbnail',  # Встраивает обложку в аудиофайл
                'already_have_thumbnail': embed_thumbnail_cfg,
            },
        ],
        'writethumbnail': embed_thumbnail_cfg,  # Загрузка обложки
        'prefer_ffmpeg': embed_thumbnail_cfg,  # Использование ffmpeg для обработки
        # 'quiet': True,  # подавляет вывод информации в консоль
        # 'cookiefile': 'cookies.txt',  # Путь к файлу cookies
    }


    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)    # Extract information and download
        title = info_dict.get('title', None)                # Подготовка имени файла с использованием title
        filename = f"{title}.m4a"
        return filename
        # return ydl.prepare_filename(ydl.extract_info(url))


youtube_download('https://www.youtube.com/watch?v=WLYI5BPsZF8', 'Music')
