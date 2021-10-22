# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available

• `{i}ugdrive <reply/file name>`
    Reply to file to upload on Google Drive.
    Add file name to upload on Google Drive.

• `{i}drivesearch <file name>`
    Search file name on Google Drive and get link.

• `{i}udir <directory name>`
    Upload a directory on Google Drive.

• `{i}listdrive`
    List all GDrive files.

• `{i}gfolder`
    Link to your Google Drive Folder.
    If added then all uploaded files will be placed here.
"""

import os
import time
from datetime import datetime

from pyUltroid.functions.gDrive import GDriveManager

from . import Redis, asst, downloader, eod, eor, get_string, ultroid_cmd

GDrive = GDriveManager()


@ultroid_cmd(
    pattern="listdrive$",
)
async def files(event):
    files = GDrive._list_files()
    eve = await eor(event, get_string("com_1"))
    msg = f"{len(files.keys())} files found in gdrive.\n\n"
    if files:
        for _ in files:
            msg += f"> [{files[_]}]({_})\n"
    else:
        msg += "Nothing in Gdrive"
    if len(msg) < 4096:
        await eve.edit(msg, link_preview=False)
    else:
        with open("drive-files.txt", "w") as f:
            f.write(
                msg.replace("[", "File Name: ")
                .replace("](", " Link: ")
                .replace(")", "")
            )
        try:
            await eve.delete()
        except BaseException:
            pass
        await event.client.send_file(
            event.chat_id,
            "drive-files.txt",
            thumb="resources/extras/ultroid.jpg",
            reply_to=eve,
        )
        os.remove("drive-files.txt")


@ultroid_cmd(
    pattern="ugdrive ?(.*)",
)
async def _(event):
    mone = await eor(event, get_string("com_1"))
    if not os.path.exists(GDrive.token_file):
        return await eod(mone, get_string("gdrive_6").format(asst.me.username))
    input_str = event.pattern_match.group(1)
    filename = None
    start = datetime.now()
    dddd = time.time()
    if event.reply_to_msg_id and not input_str:
        reply_message = await event.get_reply_message()
        try:
            downloaded_file_name = await downloader(
                "resources/downloads/" + reply_message.file.name,
                reply_message.media.document,
                mone,
                dddd,
                get_string("com_5"),
            )
            filename = downloaded_file_name.name
        except TypeError:
            filename = await event.client.download_media(
                "resources/downloads", reply_message.media
            )
        except Exception as e:
            return await eor(mone, str(e), time=10)
        end = datetime.now()
        ms = (end - start).seconds
        await mone.edit(
            f"Downloaded to `{filename}` in {ms} seconds.",
        )
    elif input_str:
        filename = input_str.strip()
        if os.path.exists(filename):
            await mone.edit(f"Found `{filename}`")
        else:
            return await eod(
                mone,
                "File Not found in local server. Give me a file path :((",
                time=5,
            )
    if not filename:
        return await eor(mone, "`File Not found in local server.`", time=10)

    try:
        g_drive_link = await GDrive._upload_file(
            mone,
            filename,
        )
        await mone.edit(get_string("gdrive_7").format(filename, g_drive_link))
    except Exception as e:
        await mone.edit(f"Exception occurred while uploading to gDrive {e}")


@ultroid_cmd(
    pattern="drivesearch ?(.*)",
)
async def sch(event):
    if not os.path.exists(TOKEN_FILE):
        return await eor(event, get_string("gdrive_6").format(asst.me.username), time=5)
    http = authorize(TOKEN_FILE, None)
    input_str = event.pattern_match.group(1).strip()
    a = await eor(event, f"Searching for {input_str} in G-Drive.")
    if Redis("GDRIVE_FOLDER_ID") is not None:
        query = "'{}' in parents and (title contains '{}')".format(
            Redis("GDRIVE_FOLDER_ID"),
            input_str,
        )
    else:
        query = f"title contains '{input_str}'"
    try:
        msg = await gsearch(http, query, input_str)
        return await a.edit(str(msg))
    except Exception as ex:
        return await a.edit(str(ex))


@ultroid_cmd(
    pattern="udir ?(.*)",
)
async def _(event):
    if not os.path.exists(TOKEN_FILE):
        return await eor(event, get_string("gdrive_6").format(asst.me.username), time=5)
    input_str = event.pattern_match.group(1)
    if not os.path.isdir(input_str):
        return await eor(event, f"Directory {input_str} does not seem to exist", time=5)

    http = authorize(TOKEN_FILE, None)
    a = await eor(event, f"Uploading `{input_str}` to G-Drive...")
    dir_id = await create_directory(
        http,
        os.path.basename(os.path.abspath(input_str)),
        Redis("GDRIVE_FOLDER_ID"),
    )
    await DoTeskWithDir(http, input_str, event, dir_id)
    dir_link = f"https://drive.google.com/folderview?id={dir_id}"
    await eor(a, get_string("gdrive_7").format(input_str, dir_link), time=5)


@ultroid_cmd(
    pattern="gfolder$",
)
async def _(event):
    if Redis("GDRIVE_FOLDER_ID"):
        folder_link = "https://drive.google.com/folderview?id=" + Redis(
            "GDRIVE_FOLDER_ID",
        )
        await eor(
            event, "`Here is Your G-Drive Folder link : `\n" + folder_link, time=5
        )
    else:
        await eor(event, "Set GDRIVE_FOLDER_ID with value of your folder id", time=5)
