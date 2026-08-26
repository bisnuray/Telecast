# Copyright (C) @itsSmartDev

import os

from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.types import CallbackQuery

from telecast.db import db
from telecast.core.config import Config
from telecast.utils.permissions import permission_checker
from telecast.ui.keyboards import keyboards
from telecast.ui.messages import messages
from telecast.core.logging import logger
from telecast.handlers.commands import show_rankings
from telecast.handlers.commands.admin import read_log_tail

from . import player as player_handlers
from . import settings as settings_handlers
from . import effects as effects_handlers
from . import queue as queue_handlers


async def handle_callback(client: Client, callback_query: CallbackQuery, player, user_client: Client = None):
    data = callback_query.data
    user_id = callback_query.from_user.id
    message = callback_query.message
    chat_id = message.chat.id

    if data == "help_menu":
        await message.edit_text(
            messages.help_message(),
            reply_markup=keyboards.help_back_button()
        )
        await callback_query.answer()
        return

    if data == "back_to_start":
        me = await client.get_me()
        await message.edit_text(
            messages.start_welcome(),
            reply_markup=keyboards.start_menu(me.username)
        )
        await callback_query.answer()
        return

    if data in ("log_display", "log_clear", "log_close"):
        if user_id != Config.BOT_OWNER_ID:
            await callback_query.answer("❌ Owner only", show_alert=True)
            return

        if data == "log_close":
            await callback_query.answer()
            await message.delete()
            return

        if data == "log_display":
            await callback_query.answer()
            await message.delete()
            await client.send_message(
                chat_id,
                f"📄 Bot Logs\n\n{read_log_tail()}",
                reply_markup=keyboards.logs_close(),
                parse_mode=ParseMode.DISABLED
            )
        else:  # log_clear
            log_path = os.path.join(Config.LOGS_DIR, "bot.log")
            try:
                with open(log_path, "w"):
                    pass
                logger.info(f"Logs cleared by owner (ID: {user_id})")
            except Exception as e:
                logger.error(f"Log clear error: {e}")
                await callback_query.answer("❌ Failed to clear logs", show_alert=True)
                return
            await callback_query.answer("✅ Logs cleared", show_alert=True)
        return

    if data.startswith("rank_daily_") or data.startswith("rank_weekly_") or data.startswith("rank_global_"):
        scope = "daily" if data.startswith("rank_daily_") else "weekly" if data.startswith("rank_weekly_") else "global"
        try:
            await callback_query.answer()
        except Exception:
            pass
        try:
            await show_rankings(client, message, chat_id, scope, edit=True)
        except Exception as e:
            logger.error(f"Ranking button failed ({scope}): {e}")
        return

    is_group_admin = await permission_checker.is_admin(client, chat_id, user_id)
    is_vc_admin = await db.is_vc_admin(chat_id, user_id)

    if not (is_group_admin or is_vc_admin):
        await callback_query.answer("❌ Admin only", show_alert=True)
        return

    settings = await db.get_chat_settings(chat_id)

    try:
        if data.startswith((
            "pause_", "resume_", "skip_", "stop_", "toggle_repeat_", "loop_",
            "setloop_", "back_", "rewind_", "seek_", "replay_", "volume_",
            "mute_btn_", "unmute_btn_", "vol_", "join_", "close_",
        )) or data == "noop":
            await player_handlers.handle(client, callback_query, player, user_client, settings)
        elif data.startswith((
            "settings_", "toggle_mode_", "toggle_autoplay_", "toggle_title_",
            "toggle_admin_", "toggle_shuffle_", "toggle_mention_",
            "toggle_playlist_perm_", "toggle_autoreply_", "quality_",
            "setquality_", "audioquality_", "setaudioquality_",
        )):
            await settings_handlers.handle(client, callback_query, player, user_client, settings)
        elif data.startswith(("effects_", "seteffect_", "speedmenu_", "setspeed_")):
            await effects_handlers.handle(client, callback_query, player, user_client, settings)
        elif data.startswith(("queue_", "qpage_", "clearqueue_", "shuffle_", "loadpl_", "delpl_")):
            await queue_handlers.handle(client, callback_query, player, user_client, settings)

    except Exception as e:
        logger.error(f"Error handling callback {data}: {e}")
        try:
            await callback_query.answer("❌ Error occurred", show_alert=True)
        except Exception:
            pass


def register_callbacks(app: Client, player, user_client: Client = None):
    @app.on_callback_query()
    async def callback_handler(client: Client, callback_query: CallbackQuery):
        await handle_callback(client, callback_query, player, user_client)
