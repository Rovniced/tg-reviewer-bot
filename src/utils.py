from telegram import (
    Bot,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
    LinkPreviewOptions,
    ReplyParameters,
)
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from telegram.ext.filters import MessageFilter
from telegram.helpers import escape_markdown

from src.config import Config
from src.database import BannedUserModel

MEDIA_GROUPS = {}


class PrefixFilter(MessageFilter):
    prefix = "/append"
    
    def __init__(self, prefix):
        super().__init__()
        self.prefix = prefix
    
    def filter(self, message):
        return message.text.startswith(self.prefix)


async def send_group(
        context: ContextTypes.DEFAULT_TYPE,
        chat_id,
        item_list,
        type_list,
        text="",
        has_spoiler=False,
):
    sent_messages = []
    
    # use item_list and type_list to build a list of telegram.InputMediaDocument, telegram.InputMediaPhoto, telegram.InputMediaVideo
    media = []
    stickers = []
    gifs = []
    for i in range(len(item_list)):
        match type_list[i]:
            case "photo":
                media.append(InputMediaPhoto(item_list[i], has_spoiler=has_spoiler))
            case "video":
                media.append(InputMediaVideo(item_list[i], has_spoiler=has_spoiler))
            case "document":
                media.append(InputMediaDocument(item_list[i]))
            case "sticker":
                stickers.append(item_list[i])
                text = text.strip()
            case "animation":
                gifs.append(item_list[i])
    
    # gifs can not be sent as a group
    for gif in gifs:
        sent_messages.append(
                await context.bot.send_animation(
                        chat_id=chat_id,
                        animation=gif,
                        caption=text,
                        parse_mode=ParseMode.MARKDOWN_V2,
                )
        )
    
    for i in range(0, len(media), 10):
        portion = media[i: i + 10]
        if len(portion) > 1:
            sent_messages.extend(
                    await context.bot.send_media_group(
                            chat_id=chat_id,
                            media=portion,
                            caption=text,
                            parse_mode=ParseMode.MARKDOWN_V2,
                    )
            )
            continue
        match portion[0]:
            case InputMediaPhoto():
                sent_messages.append(
                        await context.bot.send_photo(
                                chat_id=chat_id,
                                photo=portion[0].media,
                                caption=text,
                                has_spoiler=has_spoiler,
                                parse_mode=ParseMode.MARKDOWN_V2,
                        )
                )
            case InputMediaVideo():
                sent_messages.append(
                        await context.bot.send_video(
                                chat_id=chat_id,
                                video=portion[0].media,
                                caption=text,
                                has_spoiler=has_spoiler,
                                parse_mode=ParseMode.MARKDOWN_V2,
                        )
                )
            case InputMediaDocument():
                sent_messages.append(
                        await context.bot.send_document(
                                chat_id=chat_id,
                                document=portion[0].media,
                                caption=text,
                                parse_mode=ParseMode.MARKDOWN_V2,
                        )
                )
    
    for sticker in stickers:
        sent_messages.append(
                await context.bot.send_sticker(
                        chat_id=chat_id,
                        sticker=sticker,
                )
        )
    
    # if there are only stickers and text message, send text message additionally
    if not media and not gifs and text:
        sent_messages.append(
                await context.bot.send_message(
                        chat_id=chat_id,
                        text=text,
                        parse_mode=ParseMode.MARKDOWN_V2,
                )
        )
    
    return sent_messages


async def send_submission(
        context: ContextTypes.DEFAULT_TYPE,
        chat_id,
        media_id_list,
        media_type_list,
        documents_id_list,
        document_type_list,
        text="",
        has_spoiler=False,
):
    sent_messages = []
    
    # no media or documents, just send text
    if not media_id_list and not documents_id_list:
        sent_messages.append(
                await context.bot.send_message(
                        chat_id=chat_id,
                        text=text,
                        parse_mode=ParseMode.MARKDOWN_V2,
                        link_preview_options=LinkPreviewOptions(is_disabled=True),
                )
        )
        return sent_messages
    
    # send media and documents
    if media_id_list:
        sent_messages.extend(
                await send_group(
                        context=context,
                        chat_id=chat_id,
                        item_list=media_id_list,
                        type_list=media_type_list,
                        text=text,
                        has_spoiler=has_spoiler,
                )
        )
    if documents_id_list:
        sent_messages.extend(
                await send_group(
                        context=context,
                        chat_id=chat_id,
                        item_list=documents_id_list,
                        type_list=document_type_list,
                        text=text,
                )
        )
    
    return sent_messages


async def send_result_to_submitter(
        context,
        submitter_id,
        submit_message_id,
        message,
        inline_keyboard_markup=None,
):
    try:
        await context.bot.send_message(
                chat_id=submitter_id,
                text=message,
                reply_parameters=ReplyParameters(
                        submit_message_id, allow_sending_without_reply=True
                ),
                reply_markup=inline_keyboard_markup,
                parse_mode=ParseMode.MARKDOWN_V2,
        )
    except "send_result_to_submitter 失败":
        pass


async def get_name_from_uid(context, user_id):
    try:
        user = await context.bot.get_chat(user_id)
        return user.username, user.full_name
    except Exception as e:
        print(e)
        return "", ""


async def get_username() -> str:
    tg_bot = Bot(token=Config.BOT_TOKEN)
    await tg_bot.initialize()
    BOT_USERNAME = tg_bot.username
    return BOT_USERNAME


async def get_banned_user_info(context: ContextTypes.DEFAULT_TYPE, user: BannedUserModel):
    banned_userinfo = escape_markdown(
            f"{user.user_fullname} ({f'@{user.user_name}, ' if user.user_name else ''}{user.user_id})",
            version=2,
    )
    banned_by_username, banned_by_fullname = await get_name_from_uid(
            context, user.banned_by
    )
    banned_by_userinfo = escape_markdown(
            f"{banned_by_fullname} ({banned_by_username}, {user.banned_by})",
            version=2,
    )
    users_string = (
        f"*{banned_userinfo}* 在 *{escape_markdown(str(user.banned_date), version=2)}* 由 *{banned_by_userinfo}* 因 *"
        f"{escape_markdown(user.banned_reason, version=2)}* 屏蔽"
    )
    return users_string
