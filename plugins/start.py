import os, asyncio, humanize
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait,ChatAdminRequired, UserIsBlocked, InputUserDeactivated
from bot import Bot
from config import *
from helper_func import subscribed, encode, decode, get_messages
from database.database import add_user, del_user, full_userbase, present_user
logger = logging.getLogger(__name__)
from utils import check_verification, get_token, verify_user, check_token
from pyrogram import enums

neha_delete_time = FILE_AUTO_DELETE
neha = neha_delete_time
file_auto_delete = humanize.naturaldelta(neha)

@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    await message.reply_chat_action(enums.ChatAction.TYPING)
    if not await present_user(id):
        try:
            await add_user(id)
        except Exception as e:
            print(f"Error adding user: {e}")
            pass

    text = message.text
    if len(message.command) != 2 :
        await message.reply_chat_action(enums.ChatAction.TYPING)
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('⚡️ • ᴍᴀɪɴ ᴄʜᴀɴɴᴇʟ • ⚡️', url='https://t.me/movi_video7'),
                ],
                [
                    InlineKeyboardButton('🍁 ᴄᴏɴᴛᴀᴄᴛ ᴍᴇ •', url='https://telegram.me/shk112244'),
                    InlineKeyboardButton('🔒 ᴄʟᴏꜱᴇ •', callback_data="close")
                ]
            ]
        )

        await message.reply_text(
            text=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            quote=True
        )
        return
    try:
        data = message.command[1]
        if data.split("-", 1)[0] == "verify":
            await message.reply_chat_action(enums.ChatAction.TYPING)
            userid = data.split("-", 2)[1]
            token = data.split("-", 3)[2]
            if str(message.from_user.id) != str(userid):
                return await message.reply_text(
                    text="<b>💔 Invalid link or Expired link !</b>",
                    protect_content=True
                )
            is_valid = await check_token(client, userid, token)
            if is_valid == True:
                await message.reply_text(
                    text=f"<b>🎉 Congratulations! {message.from_user.mention}, Ads token refreshed successfully 🍿! \n\nIt will expire after midnight ✅</b>",
                    protect_content=True
                )
                await verify_user(client, userid, token)
            else:
                return await message.reply_text(
                    text="<b>💔 Invalid link or Expired link !</b>",
                    protect_content=True
                )
    except Exception as e:
        print("Not virification link")
        return

    if len(text) > 7:
        # check verfication start
        try:
            # print('A user hit this case....')
            zab_user_id = message.from_user.id
            if not await check_verification(client, zab_user_id) and TOKEN_VERIFICATION == True:
                await message.reply_chat_action(enums.ChatAction.TYPING)
                lazy_url = await get_token(client, zab_user_id, f"https://telegram.me/{client.username}?start=")
                lazy_verify_btn = [
                    [
                    InlineKeyboardButton("Click Here To Refresh Token", url=lazy_url)
                    ],[
                    InlineKeyboardButton("Need Help? Watch Video Tutorial", url=lazy_url)
                    ]
                ]
                await message.reply_text(
                    text=f"👋 Hey Buddy {message.from_user.mention}, \n\nYour Ads token is expired, refresh your token and try again.\n\n<b>Token Timeout:</b> 24 hours[midnight]\n\n<b>What is token?</b>\nThis is an ads token. If you pass 1 ad, you can use the bot for 24 hours after passing the ad.",
                    reply_markup=InlineKeyboardMarkup(lazy_verify_btn)
                )
                return
        except Exception as e:
            print(f"Exception occured : {str(e)}")
        # ./check verfication end
        try:
            base64_string = text.split(" ", 1)[1]
        except IndexError:
            return

        string = await decode(base64_string)
        argument = string.split("-")
        
        ids = []
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
                ids = range(start, end + 1) if start <= end else list(range(start, end - 1, -1))
            except Exception as e:
                print(f"Error decoding IDs: {e}")
                return

        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except Exception as e:
                print(f"Error decoding ID: {e}")
                return

        temp_msg = await message.reply("Wait A Sec..")
        try:
            messages = await get_messages(client, ids)
        except Exception as e:
            await message.reply_text("Something Went Wrong..!")
            print(f"Error getting messages: {e}")
            return
        finally:
            await temp_msg.delete()

        lazy_msgs = []  # List to keep track of sent messages

        await message.reply_chat_action(enums.ChatAction.TYPING)
        for msg in messages:
            caption = (CUSTOM_CAPTION.format(previouscaption="" if not msg.caption else msg.caption.html, 
                                             filename=msg.document.file_name) if bool(CUSTOM_CAPTION) and bool(msg.document)
                       else ("" if not msg.caption else msg.caption.html))

            reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None

            try:
                await message.reply_chat_action(enums.ChatAction.UPLOAD_DOCUMENT)
                copied_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, 
                                            reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                lazy_msgs.append(copied_msg)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await message.reply_chat_action(enums.ChatAction.UPLOAD_DOCUMENT)
                copied_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, 
                                            reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                lazy_msgs.append(copied_msg)
            except Exception as e:
                print(f"Failed to send message: {e}")
                pass
        await message.reply_chat_action(enums.ChatAction.TYPING)
        k = await client.send_message(chat_id=message.from_user.id, 
                                      text=f"<b><i>This File is deleting automatically in {file_auto_delete}. Forward in your Saved Messages..!</i></b>")

        # Schedule the file deletion
        asyncio.create_task(delete_files(lazy_msgs, client, k))

        return


@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    try:
        invite_link = await client.create_chat_invite_link(int(FORCE_SUB_CHANNEL), creates_join_request=True)
        invite_link2 = await client.create_chat_invite_link(int(FORCE_SUB_CHANNEL2), creates_join_request=True)
    except ChatAdminRequired:
        logger.error("Hey Sona, Ek dfa check kr lo ki auth Channel mei Add hu ya nhi...!")
        return
    buttons = [
        [
            InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 1", url=invite_link.invite_link),
            InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 2", url=invite_link2.invite_link),
        ]
    ]
    try:
        buttons.append(
            [
                InlineKeyboardButton(
                    text='↻ʀᴇʟᴏᴀᴅ',
                    url=f"https://t.me/{client.username}?start={message.command[1]}"
                )
            ]
        )
    except IndexError:
        pass
    await message.reply_chat_action(enums.ChatAction.TYPING)
    await message.reply(
        text=FORCE_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=None if not message.from_user.username else '@' + message.from_user.username,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True,
        disable_web_page_preview=True
    )

@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    await message.reply_chat_action(enums.ChatAction.TYPING)
    msg = await client.send_message(chat_id=message.chat.id, text=f"Processing...")
    users = await full_userbase()
    await msg.edit(f"{len(users)} Users Are Using This Bot")

@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        await message.reply_chat_action(enums.ChatAction.TYPING)
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0
        
        pls_wait = await message.reply("<i>Broadcasting Message.. This will Take Some Time</i>")
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except Exception as e:
                print(f"Failed to send message to {chat_id}: {e}")
                unsuccessful += 1
                pass
            total += 1
        
        status = f"""<b><u>Broadcast Completed</u></b>

<b>Total Users :</b> <code>{total}</code>
<b>Successful :</b> <code>{successful}</code>
<b>Blocked Users :</b> <code>{blocked}</code>
<b>Deleted Accounts :</b> <code>{deleted}</code>
<b>Unsuccessful :</b> <code>{unsuccessful}</code>"""
        
        return await pls_wait.edit(status)

    else:
        await message.reply_chat_action(enums.ChatAction.TYPING)
        msg = await message.reply(f"Use This Command As A Reply To Any Telegram Message Without Any Spaces.")
        await asyncio.sleep(8)
        await msg.delete()

# Function to handle file deletion
async def delete_files(messages, client, k):
    await asyncio.sleep(FILE_AUTO_DELETE)  # Wait for the duration specified in config.py
    
    for msg in messages:
        try:
            await client.delete_messages(chat_id=msg.chat.id, message_ids=[msg.id])
        except Exception as e:
            print(f"The attempt to delete the media {msg.id} was unsuccessful: {e}")

    # Safeguard against k.command being None or having insufficient parts
    command_part = k.command[1] if k.command and len(k.command) > 1 else None
    if command_part:
        button_url = f"https://t.me/{client.username}?start={command_part}"
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("ɢᴇᴛ ғɪʟᴇ ᴀɢᴀɪɴ!", url=button_url)]
            ]
        )
    else:
        keyboard = None

    # Edit message with the button
    await k.reply_chat_action(enums.ChatAction.TYPING)
    await k.edit_text("<b><i>Your Video / File Is Successfully Deleted ✅</i></b>", reply_markup=keyboard)

@Bot.on_message(filters.command('about') & filters.private)
async def aboutbot(client, message):
    try:
        text = f"<b>○ OWNER : <a href='https://t.me/admiinn101'>❤ Zynk Admin 🤞</a>\n○ Developer : <a href='https://t.me/LazyDeveloperr'>❤LazyDeveloperr❤</a></b>",
        
        reply_markup = InlineKeyboardMarkup(
                    [
                        [
                        InlineKeyboardButton("🔐 ᴄʟᴏsᴇ", callback_data = "close")
                        ]
                    ]
                )
        
        await message.reply(text=text, reply_markup=reply_markup, disable_web_page_preview = True,)
    except Exception as lazy:
        print(lazy)
        pass