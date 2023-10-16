import os
from pyrogram import filters, Client
from pyrogram.types import Message
from plugins.stream import *
from plugins.helpers import *
DOWNLOAD_LOCATION = "./DOWNLOADS/"


@Client.on_message(filters.private & filters.command("start"))
async def start(_, update):
    await update.reply_text("I'm StreamtapeLoader\nYou can upload streamtape.com stream url to telegram using this bot")


def get_streamtape_video_link(update_text):
    if 'streamtape.com' in update_text or 'strtapeadblocker.xyz' in update_text:
        link = update_text
    elif 'streamtape.to' in update_text:
        link = update_text.replace(
            "https://streamtape.to", "https://streamtape.com")
    else:
        link = update_text

    if 'streamtape' in link:
        links = link.split('/')
        if len(links) in {5, 6} and not link.endswith('mp4'):
            link = link + '/video.mp4'

    return link


SUDO_USERS = [5144980226, 874964742, 839221827, 5294965763, 5317652430]


@Client.on_message(filters.text & filters.private & filters.user(SUDO_USERS))
async def loader(app: Client, update: Message):
    try:
        msg = await update.reply_text('Downloading...')
        link = get_streamtape_video_link(update.text)

        if 'streamtape' in link:
            url = get_direct_streamtape(link)
        else:
            url = link

        video_path, filename = await download_multithreaded(url, DOWNLOAD_LOCATION, app, msg.chat.id,
                                                            msg.id)

        if video_path:
            width, height, duration = await Video_info(video_path)
            thumb = await Take_screen_shot(video_path)

            start_dl = time.time()

            await msg.edit_text('Uploading...')

            await update.reply_video(video=video_path,
                                     caption=filename,
                                     quote=True,
                                     width=width,
                                     thumb=thumb,
                                     height=height,
                                     duration=duration,
                                     progress=progress_for_pyrogram,
                                     progress_args=('Uploading...', msg, start_dl))
            os.remove(video_path)
            os.remove(f"{video_path}.jpg")

        else:
            await msg.edit_text('Downloading failed.')
        await msg.delete()
    except:
        pass
