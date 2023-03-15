import os
import time,math
import requests
import asyncio
from concurrent.futures import ThreadPoolExecutor
import requests, math, bs4, json
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image
import re
# from test import *


OWNER_ID = 5294965763
API_HASH = "ca5085c3f41b16df46dbeebed6e56081"
APP_ID = 28160559
BOT_TOKEN = "5696074673:AAFSjLPwlYT6usWNs4e5XGFqe94PSq9PK98"
AS_DOC = "False"
DEFAULT_THUMBNAIL = "https://telegra.ph/file/7adee9735e65353398942.jpg"
# Buttons
START_BUTTONS=[
    [
        InlineKeyboardButton("Source", url="https://github.com/X-Gorn/StreamtapeLoader"),
        InlineKeyboardButton("Project Channel", url="https://t.me/xTeamBots"),
    ],
    [InlineKeyboardButton("Author", url="https://t.me/xgorn")],
]


# Running bot
xbot = Client(
    'StreamtapeLoader',
    api_id=APP_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers = 3
)


# Helpers

# Get Login Key and Key from streamtape.com/api
# Credit: https://github.com/DebXD/streamtape-scraper

login_key = "092bad969dc91a35b649"   #   os.environ['LOGIN_KEY'] # api login
key = "kqq3bYPdkvS6x9" # os.environ['KEY'] # api password

def get_ticket(file_id):
    headers = {'file':file_id,'login':login_key,'key':key}
    response = requests.get("https://api.strtape.tech/file/dlticket?",headers)
    data = json.loads(response.text)
    # print(data)
    result = data.get('result')
    return result

async def get_details(url):
    response = requests.head(url)
    if "Content-Disposition" in response.headers:
        try:
            filename = re.findall("filename=(.+)", response.headers["Content-Disposition"])[0]
        except:
            filename = "Untitled"
    else:
        filename = url.split("/")[-1]
        
    return filename

def dl_url(ticket,file_id):
    headers = {'file':file_id,'ticket':ticket,'login':login_key,'key':key}
    response = requests.get("https://api.strtape.tech/file/dl?",headers)
    data = json.loads(response.text)
    # print(data)
    result = data.get('result')
    if result is not None:
        link = result.get('url')
        return link
    else:
        return "Not Found"

def get_file_id(link):
    lst = []
    for i in link:
        lst.append(i)

    lst2 = lst[25:]

    file_id = ""
    for i in lst2:
        if i == "/":
            break;
        else:
            file_id += i
    # print(file_id)
    return file_id  

def get_direct_streamtape(url):
    file_id = get_file_id(url)
    result = get_ticket(file_id)
    # print(result)
    ticket = result.get('ticket')
    # print(ticket)
    time.sleep(result.get('wait_time'))
    link = dl_url(ticket,file_id)
    return link


# later
def streamtape_scrape(url):
    text = requests.get(url).text
    soup = bs4.BeautifulSoup(text, 'html.parser')
    norobotlink = soup.find(id='norobotlink')
    return norobotlink.text


def scrape_poster(url):
    s = requests.Session()
    text = s.get(url).text
    soup = bs4.BeautifulSoup(text, 'html.parser')
    try:
        mainvideo = soup.find('video', id='mainvideo')
        return True, mainvideo['poster']
    except:
        return False, 'error'



# https://github.com/SpEcHiDe/AnyDLBot
async def progress_for_pyrogram(
    current,
    total,
    ud_type,
    message,
    start
):
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        # if round(current / total * 100, 0) % 5 == 0:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

        progress = "[{0}{1}] \nP: {2}%\n".format(
            ''.join(["█" for i in range(math.floor(percentage / 5))]),
            ''.join(["░" for i in range(20 - math.floor(percentage / 5))]),
            round(percentage, 2))

        tmp = progress + "{0} of {1}\nSpeed: {2}/s\nETA: {3}\n".format(
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            # elapsed_time if elapsed_time != '' else "0 s",
            estimated_total_time if estimated_total_time != '' else "0 s"
        )
        try:
            await message.edit(
                text="{}\n{}".format(
                    ud_type,
                    tmp
                )
            )
        except:
            pass


def humanbytes(size):
    # https://stackoverflow.com/a/49361727/4723940
    # 2**10 = 1024
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "") + \
        ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2]
# 

async def download_multithreaded1(url, num_threads, output_file, bot, chat_id, message_id):
    def download_chunk(start_byte, end_byte):
        headers = {'Range': f'bytes={start_byte}-{end_byte}'}
        response = requests.get(url, headers=headers, stream=True)
        content_range = response.headers.get('Content-Range')
        chunk_size = end_byte - start_byte
        return response.content

    response = requests.head(url)
    content_length = int(response.headers['Content-Length'])
    chunk_size = content_length // num_threads

    downloaded = 0
    start = time.time()
    display_message = ""

    with ThreadPoolExecutor() as executor:
        futures = []
        for i in range(num_threads):
            start_byte = i * chunk_size
            end_byte = (i + 1) * chunk_size - 1 if i < num_threads - 1 else content_length - 1
            future = executor.submit(download_chunk, start_byte, end_byte)
            futures.append(future)
        contents = []
        for future in futures:
            chunk = future.result()
            contents.append(chunk)
            downloaded += len(chunk)

            # Update progress display
            if downloaded > 0:
                percentage = downloaded / content_length * 100
                speed = downloaded / (time.time() - start)
                eta = human_readable_time((content_length - downloaded) / speed) if speed > 0 else "00:00:00"
                downloaded_size = human_readable_size(downloaded)
                total_size = human_readable_size(content_length)
                progress_display = f"{downloaded_size} of {total_size} ({percentage:.2f}%) @ {human_readable_size(speed)}/s - ETA: {eta}"
                progress_display2 = "[{0}{1}]\n**Progress :** {2}%\n".format(
                    ''.join(["◾️" for i in range(math.floor(percentage / 10))]),
                    ''.join(["◽️" for i in range(10 - math.floor(percentage / 10))]),
                    round(percentage, 2))
                if progress_display != display_message:
                    await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=progress_display2)
                    display_message = progress_display

    # Save downloaded content to file
    with open(output_file, 'wb') as f:
        f.write(b''.join(contents))

    return output_file


def human_readable_time(seconds):
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:.0f}m, {seconds:.0f}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:.0f}h, {minutes:.0f}m, {seconds:.0f}s"



def human_readable_size(size):
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    index = 0
    while size > 1024 and index < len(units) - 1:
        size /= 1024
        index += 1
    return f"{size:.2f}{units[index]}"
