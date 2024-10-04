from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.utils import MEDIA_GROUPS


async def reply_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if message.media_group_id:
        if message.media_group_id in MEDIA_GROUPS:
            submission = MEDIA_GROUPS[message.media_group_id]
        else:
            submission = {
                "media_id_list": [],
                "media_type_list": [],
                "document_id_list": [],
                "document_type_list": [],
            }
        if message.photo:
            submission["media_id_list"].append(message.photo[-1].file_id)
            submission["media_type_list"].append("photo")
        if message.video:
            submission["media_id_list"].append(message.video.file_id)
            submission["media_type_list"].append("video")
        if message.animation:  # GIF
            submission["media_id_list"].append(message.animation.file_id)
            submission["media_type_list"].append("animation")
        # elif because gif is also a document but can not be sent as a group
        elif message.document:
            submission["document_id_list"].append(message.document.file_id)
            submission["document_type_list"].append("document")

        if message.media_group_id in MEDIA_GROUPS:
            return
        MEDIA_GROUPS[message.media_group_id] = submission

    # show options as an inline keyboard
    keyboard = [
        [
            InlineKeyboardButton("署名投稿", callback_data=f"realname"),
            InlineKeyboardButton("匿名投稿", callback_data=f"anonymous"),
        ],
        [InlineKeyboardButton("取消投稿", callback_data="cancel")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        """❔确认投稿？（确认后无法编辑内容）

请确认稿件不包含以下内容，否则可能不会被通过：
- 过于哗众取宠、摆拍卖蠢（傻逼不算沙雕）
- 火星救援
- 纯链接（请投稿链接里的内容，如图片、视频等）
- 恶俗性挂人

稿件将由多位管理投票审核，每位管理的审核标准可能不一，投票制可以改善这类问题，但仍可能对部分圈内的梗不太熟悉，请您理解""",
        quote=True,
        reply_markup=reply_markup,
    )
