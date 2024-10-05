from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown

import src.database.ban as Banned_user
from src.database import BannedUserModel
from src.utils import get_banned_user_info, get_name_from_uid


async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("请提供用户ID和原因")
    user, result = context.args[0], context.args[1:]
    if not user.isdigit():
        return await update.message.reply_text(f"ID *{escape_markdown(user, version=2, )}* 无效", parse_mode=ParseMode.MARKDOWN_V2)
    if Banned_user.is_banned(user):
        return await update.message.reply_text(f"{user} 已被屏蔽\n" +
                                               await get_banned_user_info(context, (await Banned_user.get_banned_user(user))),
                                               parse_mode=ParseMode.MARKDOWN_V2)
    
    username, fullname = await get_name_from_uid(context, user)
    user_data = BannedUserModel(
            user_id=user,
            user_name=username,
            user_fullname=fullname,
            banned_reason=" ".join(result),
            banned_by=update.effective_user.id,
    )
    await Banned_user.ban_user(user_data)
    if user_data.banned_date:
        await update.message.reply_text(await get_banned_user_info(context, await Banned_user.get_banned_user(user)) +
                                        escape_markdown(f"\n\n#BAN_{user} #OPERATOR_{update.effective_user.id}", version=2, ),
                                        parse_mode=ParseMode.MARKDOWN_V2)
    else:
        await update.message.reply_text(f"*{user}* 屏蔽失败", parse_mode=ParseMode.MARKDOWN_V2)


async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text(
                "请提供用户ID",
        )
    user = context.args[0]
    if await Banned_user.unban_user(user):
        await update.message.reply_text(
                f"*{user}* " + escape_markdown(f"已解除屏蔽\n\n#UNBAN_{user} #OPERATOR_{update.effective_user.id}", version=2, ),
                parse_mode=ParseMode.MARKDOWN_V2)
    else:
        await update.message.reply_text(f"*{user}* 解除屏蔽失败", parse_mode=ParseMode.MARKDOWN_V2)


async def list_banned_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = await Banned_user.get_all_banned_users()
    users_string = "屏蔽用户列表:\n" if users else "无屏蔽用户\n"
    for user in users:
        users_string += f"\- {await get_banned_user_info(context, user)}\n"
    await update.message.reply_text(users_string, parse_mode=ParseMode.MARKDOWN_V2)
