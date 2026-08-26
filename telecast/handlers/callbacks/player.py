# Copyright (C) @itsSmartDev

from telecast.db import db
from telecast.services.queue import queue_manager
from telecast.ui.keyboards import keyboards
from telecast.ui.messages import messages
from telecast.core.logging import logger


async def handle(client, callback_query, player, user_client, settings):
    data = callback_query.data
    message = callback_query.message
    chat_id = message.chat.id

    if data.startswith("pause_"):
        await player.pause(chat_id)
        await callback_query.answer("⏸️ Paused")

        current = await player.get_current_track(chat_id)
        if current:
            loop_mode = settings.get('loop_mode', 'off')
            await message.edit_reply_markup(keyboards.player_controls(chat_id, is_paused=True, loop_mode=loop_mode))

    elif data.startswith("resume_"):
        await player.resume(chat_id)
        await callback_query.answer("▶️ Resumed")

        current = await player.get_current_track(chat_id)
        if current:
            loop_mode = settings.get('loop_mode', 'off')
            await message.edit_reply_markup(keyboards.player_controls(chat_id, is_paused=False, loop_mode=loop_mode))

    elif data.startswith("skip_"):
        try:
            await callback_query.answer("⏭️ Skipping...")
        except:
            pass

        user_name = callback_query.from_user.first_name if callback_query.from_user else "Unknown"
        user_id = callback_query.from_user.id if callback_query.from_user else "Unknown"
        logger.info(f"SKIP BUTTON - User: {user_name} (ID: {user_id}) pressed skip in chat {chat_id}")
        await player.skip(chat_id)

    elif data.startswith("stop_"):
        await player.stop(chat_id)
        await queue_manager.clear_queue(chat_id)
        await callback_query.answer("⏹️ Stopped")
        try:
            await message.delete()
        except Exception:
            pass
        await client.send_message(chat_id, "⏹️ Stopped and left voice chat.")

    elif data.startswith("toggle_repeat_"):
        settings = await db.get_chat_settings(chat_id)
        current_mode = settings.get('loop_mode', 'off')

        new_mode = 'track' if current_mode == 'off' else 'off'

        await player.set_loop_mode(chat_id, new_mode)
        await db.update_chat_settings(chat_id, {'loop_mode': new_mode})

        if new_mode == 'track':
            await callback_query.answer("🔁 Repeat On")
        else:
            await callback_query.answer("🔁 Repeat Off")

    elif data.startswith("loop_"):
        settings = await db.get_chat_settings(chat_id)
        loop_mode = settings.get('loop_mode', 'off')

        await message.edit_text(
            "🔁 **Loop Mode**",
            reply_markup=keyboards.loop_menu(chat_id, loop_mode)
        )

    elif data.startswith("setloop_"):
        mode = data.split("_")[1]
        await player.set_loop_mode(chat_id, mode)
        await db.update_chat_settings(chat_id, {'loop_mode': mode})
        await callback_query.answer(f"Loop: {mode}")

        settings = await db.get_chat_settings(chat_id)
        await message.edit_text(
            messages.settings_info(settings),
            reply_markup=keyboards.settings_menu(chat_id, settings)
        )

    elif data.startswith("back_"):
        current = await player.get_current_track(chat_id)
        if current:
            queue = await queue_manager.get_queue(chat_id)
            playlist_state = queue_manager.get_playlist_state(chat_id)
            playlist_unfetched = (playlist_state['total'] - playlist_state['fetched']) if playlist_state else 0
            settings = await db.get_chat_settings(chat_id)
            loop_mode = settings.get('loop_mode', 'off')
            await message.edit_text(
                messages.now_playing(current, current.get('requested_by', 'Unknown'), 0, queue, playlist_unfetched),
                reply_markup=keyboards.player_controls(chat_id, loop_mode=loop_mode)
            )
        else:
            await message.edit_text("No track playing")
        try:
            await callback_query.answer()
        except Exception:
            pass

    elif data.startswith("rewind_"):
        try:
            await callback_query.answer("⏪ Rewinded 10s")
        except Exception:
            pass
        await player.seek(chat_id, -10)

    elif data.startswith("seek_"):
        try:
            await callback_query.answer("⏩ Seeked 10s")
        except Exception:
            pass
        await player.seek(chat_id, 10)

    elif data.startswith("replay_"):
        try:
            await callback_query.answer("🔁 Replaying from start")
        except Exception:
            pass
        await player.seek(chat_id, 0)

    elif data.startswith("volume_"):
        is_muted = player.tgcalls.is_muted(chat_id)
        await message.edit_text(
            "🔊 **Volume Control**\n\nSelect volume level:",
            reply_markup=keyboards.volume_menu(chat_id, is_muted=is_muted)
        )

    elif data.startswith("mute_btn_"):
        try:
            await player.mute(chat_id)
            await callback_query.answer("🔇 Muted")

            is_muted = player.tgcalls.is_muted(chat_id)
            await message.edit_text(
                "🔊 **Volume Control**\n\nSelect volume level:",
                reply_markup=keyboards.volume_menu(chat_id, is_muted=is_muted)
            )
        except Exception as e:
            await callback_query.answer(f"❌ Failed to mute: {str(e)}", show_alert=True)

    elif data.startswith("unmute_btn_"):
        try:
            await player.unmute(chat_id)
            await callback_query.answer("🔊 Unmuted")

            is_muted = player.tgcalls.is_muted(chat_id)
            await message.edit_text(
                "🔊 **Volume Control**\n\nSelect volume level:",
                reply_markup=keyboards.volume_menu(chat_id, is_muted=is_muted)
            )
        except Exception as e:
            await callback_query.answer(f"❌ Failed to unmute: {str(e)}", show_alert=True)

    elif data.startswith("vol_"):
        volume = int(data.split("_")[1])
        try:
            if player.tgcalls.is_muted(chat_id):
                await player.unmute(chat_id)

            await player.set_volume(chat_id, volume)
            await callback_query.answer(f"🔊 Volume: {volume}%")

            current = await player.get_current_track(chat_id)
            if current:
                queue = await queue_manager.get_queue(chat_id)
                playlist_state = queue_manager.get_playlist_state(chat_id)
                playlist_unfetched = (playlist_state['total'] - playlist_state['fetched']) if playlist_state else 0
                settings = await db.get_chat_settings(chat_id)
                loop_mode = settings.get('loop_mode', 'off')
                await message.edit_text(
                    messages.now_playing(current, current.get('requested_by', 'Unknown'), 0, queue, playlist_unfetched),
                    reply_markup=keyboards.player_controls(chat_id, loop_mode=loop_mode)
                )
        except NotImplementedError as e:
            await callback_query.answer(f"⚠️ {str(e)}", show_alert=True)
        except Exception as e:
            await callback_query.answer(f"❌ Failed to set volume: {str(e)}", show_alert=True)

    elif data.startswith("join_"):
        await callback_query.answer("✅ Already in voice chat")

    elif data.startswith("close_"):
        await callback_query.answer()
        await message.delete()

    elif data == "noop":
        await callback_query.answer()
