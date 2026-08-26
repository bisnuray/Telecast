# Copyright (C) @itsSmartDev

import asyncio
from typing import Optional, Tuple
from pyrogram import Client
from pyrogram.errors import (
    UserAlreadyParticipant, InviteHashExpired, UsersTooMuch,
    FloodWait, ChatAdminRequired, ChannelPrivate, UserBannedInChannel
)
from telecast.core.logging import logger

class AutoJoinHandler:

    @staticmethod
    async def ensure_user_in_chat(bot_client: Client, user_client: Client, chat_id: int) -> Tuple[bool, Optional[str]]:
        try:
            try:
                member = await user_client.get_chat_member(chat_id, "me")
                logger.info(f"User client is already in chat {chat_id}")
                return True, None
            except UserBannedInChannel:
                logger.warning(f"User client is banned in {chat_id}, attempting to unban...")
                success, msg = await AutoJoinHandler._handle_banned_user(bot_client, user_client, chat_id)
                if not success:
                    return False, msg
                logger.info(f"User client not in chat {chat_id}, starting auto-join process")
            except Exception as e:
                error_msg = str(e).lower()

                ban_keywords = ['banned', 'ban', 'user_banned', 'kicked', 'channel_private']
                if any(keyword in error_msg for keyword in ban_keywords):
                    logger.warning(f"User client appears to be banned in {chat_id} (error: {e}), attempting to unban...")
                    success, msg = await AutoJoinHandler._handle_banned_user(bot_client, user_client, chat_id)
                    if not success:
                        return False, msg

                logger.info(f"User client not in chat {chat_id}, starting auto-join process")

            chat = await bot_client.get_chat(chat_id)

            if chat.username:
                return await AutoJoinHandler._join_public_group(bot_client, user_client, chat.username, chat_id)
            else:
                return await AutoJoinHandler._join_private_group(bot_client, user_client, chat_id)

        except ChatAdminRequired:
            error_msg = "❌ **Bot needs admin permission**\n\nThe bot must be an admin with the following permissions:\n• Invite users\n• Export invite links\n• Manage voice chats"
            logger.error(f"Bot lacks admin permissions in {chat_id}")
            return False, error_msg

        except Exception as e:
            error_msg = f"❌ **Failed to add user client to group**\n\nError: {str(e)}"
            logger.error(f"Unexpected error in auto-join for {chat_id}: {e}")
            return False, error_msg

    @staticmethod
    async def _join_public_group(bot_client: Client, user_client: Client, username: str, chat_id: int) -> Tuple[bool, Optional[str]]:
        try:
            logger.info(f"Attempting to join public group @{username}")
            await user_client.join_chat(username)
            logger.info(f"Successfully joined public group @{username}")

            await asyncio.sleep(1)
            await user_client.get_chat_member(chat_id, "me")
            return True, None

        except UserAlreadyParticipant:
            logger.info(f"User client already in public group @{username}")
            return True, None

        except Exception as e:
            error_str = str(e)
            error_str_lower = error_str.lower()

            if 'INVITE_REQUEST_SENT' in error_str or 'invite_request_sent' in error_str_lower:
                logger.info(f"Join request sent for @{username}, attempting to approve...")

                try:
                    user_id = user_client.me.id if hasattr(user_client, 'me') else None
                    if not user_id:
                        user_info = await user_client.get_me()
                        user_id = user_info.id

                    await bot_client.approve_chat_join_request(chat_id, user_id)
                    logger.info(f"Approved join request for user {user_id} in @{username}")

                    await asyncio.sleep(2)

                    await user_client.get_chat_member(chat_id, "me")
                    logger.info(f"User client confirmed as member after approval in @{username}")
                    return True, None

                except Exception as approve_error:
                    error_msg = f"❌ **Join request sent but approval failed**\n\nPlease manually approve the join request in chat settings.\n\nError: {str(approve_error)}"
                    logger.error(f"Failed to approve join request for @{username}: {approve_error}")
                    return False, error_msg

            if any(keyword in error_str_lower for keyword in ['banned', 'ban', 'username not found', 'user_banned', 'kicked', 'channel_private']):
                logger.warning(f"User client appears to be banned in public group @{username} (error: {e}), attempting to unban...")
                success, msg = await AutoJoinHandler._handle_banned_user(bot_client, user_client, chat_id)
                if not success:
                    return False, msg

                try:
                    await user_client.join_chat(username)
                    logger.info(f"Successfully joined public group @{username} after unban")
                    await asyncio.sleep(1)
                    await user_client.get_chat_member(chat_id, "me")
                    return True, None
                except Exception as retry_error:
                    retry_str = str(retry_error)

                    if 'INVITE_REQUEST_SENT' in retry_str or 'invite_request_sent' in retry_str.lower():
                        logger.info(f"Join request sent for @{username}, attempting to approve...")

                        try:
                            user_id = user_client.me.id if hasattr(user_client, 'me') else None
                            if not user_id:
                                user_info = await user_client.get_me()
                                user_id = user_info.id

                            await bot_client.approve_chat_join_request(chat_id, user_id)
                            logger.info(f"Approved join request for user {user_id} in @{username}")

                            await asyncio.sleep(2)

                            await user_client.get_chat_member(chat_id, "me")
                            logger.info(f"User client confirmed as member after approval in @{username}")
                            return True, None

                        except Exception as approve_error:
                            error_msg = f"❌ **Join request sent but approval failed**\n\nPlease manually approve the join request in chat settings.\n\nError: {str(approve_error)}"
                            logger.error(f"Failed to approve join request for @{username}: {approve_error}")
                            return False, error_msg

                    user_info = await user_client.get_me()
                    uname = f"@{user_info.username}" if user_info.username else str(user_info.id)
                    error_msg = (
                        f"❌ **Assistant Account Banned**\n\n"
                        f"Assistant account ({uname}) is currently banned in this group.\n\n"
                        f"Please unban {uname} manually and then try again."
                    )
                    logger.error(f"Failed to join @{username} after unban: {retry_error}")
                    return False, error_msg

            raise

        except UserBannedInChannel:
            logger.warning(f"User client is banned in public group @{username}, attempting to unban...")
            success, msg = await AutoJoinHandler._handle_banned_user(bot_client, user_client, chat_id)
            if not success:
                return False, msg

            try:
                await user_client.join_chat(username)
                logger.info(f"Successfully joined public group @{username} after unban")
                await asyncio.sleep(1)
                await user_client.get_chat_member(chat_id, "me")
                return True, None
            except Exception as retry_error:
                retry_str = str(retry_error)

                if 'INVITE_REQUEST_SENT' in retry_str or 'invite_request_sent' in retry_str.lower():
                    logger.info(f"Join request sent for @{username}, attempting to approve...")

                    try:
                        user_id = user_client.me.id if hasattr(user_client, 'me') else None
                        if not user_id:
                            user_info = await user_client.get_me()
                            user_id = user_info.id

                        await bot_client.approve_chat_join_request(chat_id, user_id)
                        logger.info(f"Approved join request for user {user_id} in @{username}")

                        await asyncio.sleep(2)

                        await user_client.get_chat_member(chat_id, "me")
                        logger.info(f"User client confirmed as member after approval in @{username}")
                        return True, None

                    except Exception as approve_error:
                        error_msg = f"❌ **Join request sent but approval failed**\n\nPlease manually approve the join request in chat settings.\n\nError: {str(approve_error)}"
                        logger.error(f"Failed to approve join request for @{username}: {approve_error}")
                        return False, error_msg

                error_msg = f"❌ **Failed to join after unban**\n\nError: {str(retry_error)}"
                logger.error(f"Failed to join @{username} after unban: {retry_error}")
                return False, error_msg

        except FloodWait as e:
            error_msg = f"❌ **Rate limited**\n\nPlease wait {e.value} seconds and try again."
            logger.warning(f"FloodWait {e.value}s when joining @{username}")
            return False, error_msg

        except UsersTooMuch:
            error_msg = "❌ **Group is full**\n\nThe group has reached its member limit."
            logger.error(f"Group @{username} is full")
            return False, error_msg

        except Exception as e:
            error_msg = f"❌ **Failed to join public group**\n\nError: {str(e)}"
            logger.error(f"Failed to join public group @{username}: {e}")
            return False, error_msg

    @staticmethod
    async def _join_private_group(bot_client: Client, user_client: Client, chat_id: int) -> Tuple[bool, Optional[str]]:
        temp_message = None
        try:
            temp_message = await bot_client.send_message(
                chat_id,
                "🔄 **Adding assistant to group...**\n\nPlease wait a moment."
            )

            invite_link = None
            try:
                chat = await bot_client.get_chat(chat_id)
                if hasattr(chat, 'invite_link') and chat.invite_link:
                    invite_link = chat.invite_link
                    logger.info(f"Using existing invite link for {chat_id}")
            except:
                pass

            if not invite_link:
                try:
                    logger.info(f"Exporting new invite link for {chat_id}")
                    exported_link = await bot_client.export_chat_invite_link(chat_id)
                    invite_link = exported_link
                    logger.info(f"Exported new invite link for {chat_id}")
                except ChatAdminRequired:
                    if temp_message:
                        await temp_message.delete()
                    error_msg = "❌ **Bot needs admin permission**\n\nThe bot must be an admin to invite the assistant account."
                    logger.error(f"Bot lacks permission to export invite link in {chat_id}")
                    return False, error_msg
                except Exception as e:
                    if temp_message:
                        await temp_message.delete()
                    error_msg = f"❌ **Failed to create invite link**\n\nError: {str(e)}"
                    logger.error(f"Failed to export invite link for {chat_id}: {e}")
                    return False, error_msg

            try:
                logger.info(f"User client joining private group {chat_id} via invite link")
                await user_client.join_chat(invite_link)
                logger.info(f"Successfully joined private group {chat_id}")

                await asyncio.sleep(2)

                try:
                    member = await user_client.get_chat_member(chat_id, "me")

                    logger.info(f"User client confirmed as member of {chat_id}")

                except Exception as check_error:
                    logger.warning(f"Could not confirm membership, checking for pending join request: {check_error}")

                    try:
                        user_id = user_client.me.id if hasattr(user_client, 'me') else None
                        if not user_id:
                            user_info = await user_client.get_me()
                            user_id = user_info.id

                        logger.info(f"Attempting to approve join request for user {user_id} in {chat_id}")
                        await bot_client.approve_chat_join_request(chat_id, user_id)
                        logger.info(f"Approved join request for user {user_id} in {chat_id}")

                        await asyncio.sleep(2)

                        await user_client.get_chat_member(chat_id, "me")
                        logger.info(f"User client confirmed as member after approval in {chat_id}")

                    except Exception as approve_error:
                        logger.error(f"Failed to approve join request: {approve_error}")
                        if temp_message:
                            await temp_message.delete()
                        error_msg = "❌ **Could not join group**\n\nThe assistant account needs to be approved to join this group. Please manually approve the join request or make the bot an admin."
                        return False, error_msg

                if temp_message:
                    try:
                        await temp_message.delete()
                    except:
                        pass

                try:
                    await user_client.resolve_peer(chat_id)
                    logger.info(f"Resolved peer for {chat_id} to refresh session")
                except:
                    pass

                return True, None

            except UserAlreadyParticipant:
                logger.info(f"User client already in private group {chat_id}")
                if temp_message:
                    await temp_message.delete()
                return True, None

            except InviteHashExpired:
                if temp_message:
                    await temp_message.delete()
                logger.warning(f"Invite link expired for {chat_id}, user client may be banned — attempting unban")
                success, msg = await AutoJoinHandler._handle_banned_user(bot_client, user_client, chat_id)
                if not success:
                    return False, msg
                try:
                    new_link = await bot_client.export_chat_invite_link(chat_id)
                    await user_client.join_chat(new_link)
                    await asyncio.sleep(1)
                    await user_client.get_chat_member(chat_id, "me")
                    logger.info(f"Successfully joined {chat_id} after unban + new invite link")
                    return True, None
                except Exception as retry_err:
                    user_info = await user_client.get_me()
                    username = f"@{user_info.username}" if user_info.username else str(user_info.id)
                    error_msg = (
                        f"❌ **Assistant Account Banned**\n\n"
                        f"Assistant account ({username}) is currently banned in this group.\n\n"
                        f"Please unban {username} manually and then try again."
                    )
                    logger.error(f"Still failed to join {chat_id} after unban: {retry_err}")
                    return False, error_msg

            except FloodWait as e:
                if temp_message:
                    await temp_message.delete()
                error_msg = f"❌ **Rate limited**\n\nPlease wait {e.value} seconds and try again."
                logger.warning(f"FloodWait {e.value}s when joining {chat_id}")
                return False, error_msg

            except UserBannedInChannel:
                if temp_message:
                    await temp_message.delete()
                logger.warning(f"User client is banned in private group {chat_id}, attempting unban...")
                success, msg = await AutoJoinHandler._handle_banned_user(bot_client, user_client, chat_id)
                if not success:
                    return False, msg
                try:
                    new_link = await bot_client.export_chat_invite_link(chat_id)
                    await user_client.join_chat(new_link)
                    await asyncio.sleep(1)
                    await user_client.get_chat_member(chat_id, "me")
                    logger.info(f"Successfully joined private group {chat_id} after unban")
                    return True, None
                except Exception as retry_err:
                    user_info = await user_client.get_me()
                    username = f"@{user_info.username}" if user_info.username else str(user_info.id)
                    error_msg = (
                        f"❌ **Assistant Account Banned**\n\n"
                        f"Assistant account ({username}) is currently banned in this group.\n\n"
                        f"Please unban {username} manually and then try again."
                    )
                    logger.error(f"Still failed to join private group {chat_id} after unban: {retry_err}")
                    return False, error_msg

            except UsersTooMuch:
                if temp_message:
                    await temp_message.delete()
                error_msg = "❌ **Group is full**\n\nThe group has reached its member limit."
                logger.error(f"Group {chat_id} is full")
                return False, error_msg

        except Exception as e:
            if temp_message:
                try:
                    await temp_message.delete()
                except:
                    pass
            error_msg = f"❌ **Failed to join private group**\n\nError: {str(e)}"
            logger.error(f"Failed to join private group {chat_id}: {e}")
            return False, error_msg

    @staticmethod
    async def _handle_banned_user(bot_client: Client, user_client: Client, chat_id: int) -> Tuple[bool, Optional[str]]:
        try:
            user_id = user_client.me.id if hasattr(user_client, 'me') else None
            if not user_id:
                user_info = await user_client.get_me()
                user_id = user_info.id

            logger.info(f"Attempting to unban user {user_id} in {chat_id}")

            await bot_client.unban_chat_member(chat_id, user_id)
            logger.info(f"Successfully unbanned user {user_id} in {chat_id}")

            await asyncio.sleep(2)

            return True, None

        except ChatAdminRequired:
            try:
                user_info = await user_client.get_me()
                username = f"@{user_info.username}" if user_info.username else str(user_id)
            except Exception:
                username = str(user_id)
            error_msg = (
                f"❌ **Assistant Account Banned**\n\n"
                f"Assistant account ({username}) is currently banned in this group.\n\n"
                f"Please unban {username} manually and then try again."
            )
            logger.error(f"Bot lacks permission to unban user in {chat_id}")
            return False, error_msg

        except Exception as e:
            error_str = str(e).lower()

            if 'not found' in error_str or 'not a member' in error_str:
                logger.info(f"User {user_id} is not banned in {chat_id}, just not a member")
                return True, None

            try:
                user_info = await user_client.get_me()
                username = f"@{user_info.username}" if user_info.username else str(user_id)
            except Exception:
                username = str(user_id)
            error_msg = (
                f"❌ **Assistant Account Banned**\n\n"
                f"Assistant account ({username}) is currently banned in this group.\n\n"
                f"Please unban {username} manually and then try again."
            )
            logger.error(f"Failed to unban user in {chat_id}: {e}")
            return False, error_msg

auto_join_handler = AutoJoinHandler()
