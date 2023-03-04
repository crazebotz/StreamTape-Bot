from test import *

dirs = './DOWNLOADS/'
if not os.path.isdir(dirs):
   os.mkdir(dirs)


# Start message
@xbot.on_message(filters.command(['start','fast']) & filters.chat(OWNER_ID) & filters.private)
async def start(bot, update):
    await update.reply_text(f"I'm StreamtapeLoader\nYou can upload streamtape.com stream url to telegram using this bot", True, reply_markup=InlineKeyboardMarkup(START_BUTTONS))


@xbot.on_message(filters.text & filters.chat(OWNER_ID) & filters.private)
async def loader(bot, update):
    
     
    if 'streamtape.com' in update.text:
        link = update.text
    elif 'strtapeadblocker.xyz' in update.text:
        link = update.text

    elif 'streamtape.to' in update.text:
        link = update.text.replace("https://streamtape.to","https://streamtape.com")
      
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
    file_name = await get_details(url)
    file_path = f"{dirs}/{file_name}"
    
    
    dl_path1 = await download_multithreaded1(url, 4, file_path,xbot,pablo.chat.id,pablo.id)
    
    
    result = True #, dl_path = download_file(url, dirs)
    print(result, dl_path1)
    if result == True:
        
        
        thumb_url = DEFAULT_THUMBNAIL
        thumb = f'./downloads/thumb_{update.id}.jpg'
        r = requests.get(thumb_url, allow_redirects=True)
        open(thumb, 'wb').write(r.content)
        if os.path.exists(thumb):
            width = 0
            height = 0
            metadata = extractMetadata(createParser(thumb))
            if metadata.has('width'):
                width = metadata.get('width')
            if metadata.has('height'):
                height = metadata.get('height')
            Image.open(thumb).convert('RGB').save(thumb)
            img = Image.open(thumb)
            # https://stackoverflow.com/a/37631799/4723940
            # img.thumbnail((90, 90))
            if AS_DOC == 'True':
                img.resize((320, height))
            elif AS_DOC == 'False':
                img.resize((90, height))
            img.save(thumb, "JPEG")
        metadata = extractMetadata(createParser(dl_path1))
        if metadata is not None:
            if metadata.has("duration"):
                duration = metadata.get('duration').seconds
            else:
                duration = 0
        start_dl = time.time()
        await pablo.edit_text('Uploading...')
        if AS_DOC == 'True':
            await update.reply_document(
                document=dl_path1, 
                quote=True, 
                thumb=thumb, 
                progress=progress_for_pyrogram, 
                progress_args=(
                    'Uploading...', 
                    pablo, 
                    start_dl
                )
            )
            os.remove(dl_path1)
            os.remove(thumb)
        elif AS_DOC == 'False':
            await update.reply_video(
                video=dl_path1,
                quote=True,
                thumb=thumb,
                duration=duration,
                progress=progress_for_pyrogram,
                progress_args=(
                    'Uploading...',
                    pablo,
                    start_dl
                )
            )
            os.remove(dl_path1)
            os.remove(thumb)
    else:
        await pablo.edit_text('Downloading failed.')
    await pablo.delete()


xbot.run()
