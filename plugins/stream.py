import re
import os
import bs4
import math
import time
import requests
import json
from concurrent.futures import ThreadPoolExecutor

thread_number = int(os.environ.get("NUMBER", 5))

# Get Login Key and Key from streamtape.com/api
# Credit: https://github.com/DebXD/streamtape-scraper

login_key = "092bad969dc91a35b649"  # os.environ['LOGIN_KEY'] # api login
key = "kqq3bYPdkvS6x9"  # os.environ['KEY'] # api password


def get_ticket(file_id):
    headers = {'file': file_id, 'login': login_key, 'key': key}
    response = requests.get("https://api.strtape.tech/file/dlticket?", headers)
    data = json.loads(response.text)
    # print(data)
    result = data.get('result')
    return result


async def get_details(url):
    response = requests.head(url)
    if "Content-Disposition" in response.headers:
        try:
            filename = re.findall(
                "filename=(.+)", response.headers["Content-Disposition"])[0]
        except:
            filename = "Untitled"
    else:
        filename = url.split("/")[-1]

    return filename


def dl_url(ticket, file_id):
    headers = {'file': file_id, 'ticket': ticket,
               'login': login_key, 'key': key}
    response = requests.get("https://api.strtape.tech/file/dl?", headers)
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
            break
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
    link = dl_url(ticket, file_id)
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


async def download_multithreaded(url, DOWNLOAD_LOCATION, bot, chat_id, message_id):
    def download_chunk(start_byte, end_byte):
        headers = {'Range': f'bytes={start_byte}-{end_byte}'}
        response = requests.get(url, headers=headers, stream=True)
        return response.content

    response = requests.head(url)
    # print(response.headers)
    content_length = int(response.headers['Content-Length'])
    chunk_size = content_length // thread_number

    downloaded = 0
    start = time.time()
    display_message = ""

    with ThreadPoolExecutor() as executor:
        futures = []
        for i in range(thread_number):
            start_byte = i * chunk_size
            end_byte = (i + 1) * chunk_size - \
                1 if i < thread_number - 1 else content_length - 1
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
                eta = human_readable_time(
                    (content_length - downloaded) / speed) if speed > 0 else "00:00:00"
                downloaded_size = human_readable_size(downloaded)
                total_size = human_readable_size(content_length)
                progress_display = f"{downloaded_size} of {total_size} ({percentage:.2f}%) @ {human_readable_size(speed)}/s - ETA: {eta}"
                progress_display2 = "[{0}{1}]\n**Progress :** {2}%\n".format(
                    ''.join(["◾️" for i in range(math.floor(percentage / 10))]),
                    ''.join(["◽️" for i in range(
                        10 - math.floor(percentage / 10))]),
                    round(percentage, 2))
                if progress_display != display_message:
                    await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=progress_display2)
                    display_message = progress_display

    # Save downloaded content to file
    filename = url.split("/")[-1].replace("+", "-").replace("--", "-")
    output_file = f"{DOWNLOAD_LOCATION}{filename}"
    with open(output_file, 'wb') as f:
        f.write(b''.join(contents))

    return output_file, filename


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
