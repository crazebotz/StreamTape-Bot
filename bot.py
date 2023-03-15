from test import *
from screenshot import take_screen_shot


@xbot.on_message(
  filters.command(['start', 'fast']) & filters.chat(OWNER_ID) & filters.private
)
async def start(bot, update):
  await update.reply_text(
    f"I'm StreamtapeLoader\nYou can upload streamtape.com stream url to telegram using this bot",
    True,
    reply_markup=InlineKeyboardMarkup(START_BUTTONS))


@xbot.on_message(filters.text & filters.chat(OWNER_ID) & filters.private)
async def loader(bot, update):
  dirs = './downloads/'
  if not os.path.isdir(dirs):
    os.mkdir(dirs)

  if 'streamtape.com' in update.text:
    link = update.text
  elif 'strtapeadblocker.xyz' in update.text:
    link = update.text

  elif 'streamtape.to' in update.text:
    link = update.text.replace("https://streamtape.to",
                               "https://streamtape.com")

  else:
    link = update.text
  link = link
  if 'streamtape' in link:
    if '/' in link:
      links = link.split('/')
      if len(links) == 6:
        if link.endswith('mp4'):
          link = link
        else:
          link = link + 'video.mp4'
      elif len(links) == 5:
        link = link + '/video.mp4'
      else:
        return
    else:
      return

  if 'streamtape' in link:
    url = get_direct_streamtape(link)

  else:
    url = link

  pablo = await update.reply_text('Downloading...')
  dirs = f"{dirs}/Video.mp4"

  dl_path1 = await download_multithreaded1(url, 5, dirs, xbot, pablo.chat.id,
                                           pablo.id)

  if dl_path1:

    thumb = None

    width = 1240
    height = 710
    duration = 0
    metadata = extractMetadata(createParser(dl_path1))

    if metadata.has("duration"):
      duration = metadata.get('duration').seconds
    if metadata.has("width"):
      width = metadata.get("width")
    if metadata.has("height"):
      height = metadata.get("height")

    start_dl = time.time()

    await pablo.edit_text('Uploading...')
    if AS_DOC == 'True':
      await update.reply_document(document=dl_path1,
                                  quote=True,
                                  thumb=thumb,
                                  progress=progress_for_pyrogram,
                                  progress_args=('Uploading...', pablo,
                                                 start_dl))
      os.remove(dl_path1)

    elif AS_DOC == 'False':
      thumb = await take_screen_shot(dl_path1, os.path.dirname(dl_path1), random.randint(0, duration - 1))
      await update.reply_video(video=dl_path1,
                               quote=True,
                               thumb=thumb,
                               duration=duration,
                               width=width,
                               height=height,
                               progress=progress_for_pyrogram,
                               progress_args=('Uploading...', pablo, start_dl))
      os.remove(dl_path1)

  else:
    await pablo.edit_text('Downloading failed.')
  await pablo.delete()


xbot.run()
