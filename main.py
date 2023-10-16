import os, shutil
from pyrogram import Client

OWNER_ID = 5294965763
API_HASH = "ca5085c3f41b16df46dbeebed6e56081"
APP_ID = 28160559
BOT_TOKEN = os.environ.get("BOT_TOKEN",
                           "6308227197:AAH3bgbZxmu8gxwe6bgCJZSCVcIPTL1MDks")


DOWNLOAD_LOCATION = "./DOWNLOADS/"

if not os.path.isdir(DOWNLOAD_LOCATION):
        os.makedirs(DOWNLOAD_LOCATION)

else:
        try:
            shutil.rmtree(DOWNLOAD_LOCATION)
            os.makedirs(DOWNLOAD_LOCATION)
        except:
            pass


plugins = dict(root="plugins")

# Running bot
xbot = Client(
    'StreamtapeLoader',
    api_id=APP_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=3,
    plugins=plugins
)

print("Started :)")

xbot.run()
