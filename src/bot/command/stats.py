from textwrap import dedent

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown

import src.database.reviewer as Reviewer
import src.database.submitter as Submitter
from src.config import ReviewConfig


async def submitter_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    userid = update.effective_user.id
    if update.effective_chat.id == ReviewConfig.REVIEWER_GROUP:
        if not context.args:
            return await update.message.reply_text("请提供用户ID")
        userid = context.args[0]
    submitter_info = await Submitter.get_submitter(userid)
    if not submitter_info or not submitter_info.submission_count:
        return await update.message.reply_text("还没有投稿过任何内容")
    reply_string = "*\-\-基础信息\-\-*\n" + escape_markdown(
            f"投稿数量: {submitter_info.submission_count}\n"
            f"通过数量: {submitter_info.approved_count}\n"
            f"拒绝数量: {submitter_info.rejected_count}\n"
            f"投稿通过率: {submitter_info.approved_count / submitter_info.submission_count * 100:.2f}%",
            version=2,
    )
    await update.message.reply_text(reply_string, parse_mode=ParseMode.MARKDOWN_V2)


async def reviewer_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reviewer_id = context.args[0] if context.args else update.effective_user.id
    if not (reviewer_info := await Reviewer.get_reviewer(reviewer_id)):
        return await update.message.reply_text("还没有审核过任何内容")
    reply_string = "*\-\-基础信息\-\-*\n" + escape_markdown(
            dedent(
                    f"""
        审核数量: {reviewer_info.approve_count + reviewer_info.reject_count}
        通过数量: {reviewer_info.approve_count}
        拒稿数量: {reviewer_info.reject_count}
        通过但稿件被拒数量: {reviewer_info.approve_but_rejected_count}
        拒稿但稿件通过数量: {reviewer_info.reject_but_approved_count}

        通过但稿件被拒数量 / 通过数量: {reviewer_info.approve_but_rejected_count / reviewer_info.approve_count * 100 if reviewer_info.approve_count else 0.0:.2f}%
        拒稿但稿件通过数量 / 拒稿数量: {reviewer_info.reject_but_approved_count / reviewer_info.reject_count * 100 if reviewer_info.reject_count else 0.0:.2f}%

        最后一次审核时间: {reviewer_info.last_time}"""
            ),
            version=2,
    )
    await update.message.reply_text(reply_string, parse_mode=ParseMode.MARKDOWN_V2)
