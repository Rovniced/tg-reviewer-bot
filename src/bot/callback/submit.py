from telegram import Update
from telegram.constants import MessageOriginType
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown

from src.config import ReviewConfig
from src.review_utils import reply_review_message
from src.utils import MEDIA_GROUPS, send_submission
import src.database.submitter as Submitter


async def cancel_submission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.edit_message_text(text="投稿已取消")
    await query.answer()


async def confirm_submission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    user = update.effective_user

    confirm_message = update.effective_message
    origin_message = confirm_message.reply_to_message

    if query.data.startswith(("anonymous", "realname")):
        text = (
            origin_message.text_markdown_v2_urled
            or origin_message.caption_markdown_v2_urled
            or ""
        )
        # add forward origin
        if origin_message.forward_origin is not None:
            forward_string = "\n\n_from_ "
            match origin_message.forward_origin.type:
                case MessageOriginType.USER:
                    forward_string += f"[{escape_markdown(origin_message.forward_origin.sender_user.full_name,version=2,)}](tg://user?id={origin_message.forward_origin.sender_user.id})"
                case MessageOriginType.CHAT:
                    forward_string += f"[{escape_markdown(origin_message.forward_origin.sender_chat.title,version=2,)}]({origin_message.forward_origin.sender_chat.link})"
                case MessageOriginType.CHANNEL:
                    forward_string += f"[{escape_markdown(origin_message.forward_origin.chat.title,version=2,)}]({origin_message.forward_origin.chat.link}/{origin_message.forward_origin.message_id})"
                case MessageOriginType.HIDDEN_USER:

                    forward_string += escape_markdown(
                        origin_message.forward_origin.sender_user_name,
                        version=2,
                    )
            text += f"{forward_string}"

        # add submitter sign string
        if query.data.startswith("realname"):
            sign_string = f"_via_ [{escape_markdown(user.full_name,version=2,)}](tg://user?id={user.id})"
            # if the last line is a forward message, put in the same line
            if text.split("\n")[-1].startswith("_from_"):
                text += " " + sign_string
            else:
                text += "\n\n" + sign_string

        if origin_message.media_group_id:
            # is a group of media
            submission = MEDIA_GROUPS[origin_message.media_group_id]
            pass
        else:
            # single media or pure text
            submission = {
                "media_id_list": [],
                "media_type_list": [],
                "document_id_list": [],
                "document_type_list": [],
            }
            if origin_message.photo:
                submission["media_id_list"].append(origin_message.photo[-1].file_id)
                submission["media_type_list"].append("photo")
            if origin_message.video:
                submission["media_id_list"].append(origin_message.video.file_id)
                submission["media_type_list"].append("video")
            if origin_message.sticker:
                submission["media_id_list"].append(origin_message.sticker.file_id)
                submission["media_type_list"].append("sticker")
                # just ignore any forward or realname information for sticker
                # in single submit mode because it is not allowed to have
                # text with sticker
                text = ""
            if origin_message.animation:  # GIF
                submission["media_id_list"].append(origin_message.animation.file_id)
                submission["media_type_list"].append("animation")
            # elif because gif is also a document but can not be sent as a group
            elif origin_message.document:
                submission["document_id_list"].append(origin_message.document.file_id)
                submission["document_type_list"].append("document")

        submission_messages = await send_submission(
            context=context,
            chat_id=ReviewConfig.REVIEWER_GROUP,
            media_id_list=submission["media_id_list"],
            media_type_list=submission["media_type_list"],
            documents_id_list=submission["document_id_list"],
            document_type_list=submission["document_type_list"],
            text=text.strip(),
        )

        submission_meta = {
            "submitter": [
                user.id,
                user.username,
                user.full_name,
                origin_message.message_id,
            ],
            "reviewer": {},
            "text": text,
            "media_id_list": submission["media_id_list"],
            "media_type_list": submission["media_type_list"],
            "documents_id_list": submission["document_id_list"],
            "document_type_list": submission["document_type_list"],
            "append": {},
        }

        await reply_review_message(submission_messages[0], submission_meta)
        await query.edit_message_text(text="投稿成功")

        await Submitter.count_modify(user.id, "submission_count")
