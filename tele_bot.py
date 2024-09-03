from telegram import Update, InputMediaPhoto, InputMediaVideo
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler, MessageHandler, filters

from reddit import RatsRetriever
from utils import get_submission_data

import os
from time import sleep
import logging
from json import load, dump

ratsretriever = RatsRetriever()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)


async def main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    while True:
        sleep(5)
        if not os.listdir("cache"):
            new_posts = ratsretriever.get_hots()
            for post in new_posts:
                ratsretriever.download_submissions(new_posts)
        else:
            with open(f"cache/{os.listdir('cache')[0]}", "rb") as submission:
                caption = ""
                url = ""
                if "_" in submission.name:
                    gallery_id = submission.name[:submission.name.rfind("_")]
                    gallery_files = []

                    for file_name in os.listdir("cache"):
                        if gallery_id in file_name:
                            caption, url = get_submission_data(file_name)

                            with open(f"cache/{file_name}", "rb") as f1:
                                if ".mp4" in f1.name:
                                    gallery_files.append(InputMediaVideo(f1))
                                else:
                                    gallery_files.append(InputMediaPhoto(f1))

                    await update.effective_chat.send_media_group(media=gallery_files,
                            caption=f"<a href={url}>{caption}</a>", parse_mode=ParseMode.HTML)

                else:
                    caption, url = get_submission_data(submission)
                    if "jpeg" or "png" in submission.name:
                        await update.effective_chat.send_photo(photo=submission,
                                caption=f"<a href={url}>{caption}</a>", parse_mode=ParseMode.HTML)
                    else:
                        await update.effective_chat.send_video(video=submission,
                                caption=f"<a href={url}>{caption}</a>", parse_mode=ParseMode.HTML)


if __name__ == "__main__":
    token = "insert telegram bot token here"
    app = ApplicationBuilder().token(token).build()
    app.add_handler(MessageHandler(filters.Text(["start"]), main))
    app.run_polling()
