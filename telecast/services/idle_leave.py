import asyncio
import time
from typing import Optional

from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait

from telecast.core.config import Config
from telecast.core.logging import logger
from telecast.db import db
from telecast.services.queue import queue_manager


class IdleLeaveManager:
    def __init__(self):
        self._task: Optional[asyncio.Task] = None
        self.tgcalls = None

    @property
    def enabled(self) -> bool:
        return Config.ASSISTANT_IDLE_LEAVE_SECONDS > 0

    async def touch(self, chat_id: int):
        if not self.enabled:
            return
        try:
            await db.touch_assistant_active(chat_id, time.time())
        except Exception as e:
            logger.warning(f"Could not record assistant activity for {chat_id}: {e}")

    def start(self, tgcalls_manager):
        if not self.enabled:
            logger.info("Assistant idle-leave is disabled (ASSISTANT_IDLE_LEAVE_SECONDS=0)")
            return
        self.tgcalls = tgcalls_manager
        self._task = asyncio.create_task(self._loop())
        logger.info(
            f"Assistant idle-leave enabled: leaves after {Config.ASSISTANT_IDLE_LEAVE_SECONDS}s "
            f"without playback (checked every {Config.ASSISTANT_IDLE_CHECK_INTERVAL}s)"
        )

    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except (asyncio.CancelledError, Exception):
                pass
            self._task = None

    async def _loop(self):
        while True:
            try:
                await asyncio.sleep(Config.ASSISTANT_IDLE_CHECK_INTERVAL)
                await self._sweep()
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.error(f"Idle-leave sweep failed: {e}")

    async def _sweep(self):
        cutoff = time.time() - Config.ASSISTANT_IDLE_LEAVE_SECONDS
        for chat_id in await db.get_idle_assistant_chats(cutoff):
            try:
                if not await self._leave_if_idle(chat_id):
                    continue
                await asyncio.sleep(2)
            except FloodWait as e:
                logger.warning(f"FloodWait {e.value}s while leaving chats — ending this sweep")
                return
            except Exception as e:
                logger.warning(f"Idle-leave failed for {chat_id}: {e}")

    async def _leave_if_idle(self, chat_id: int) -> bool:
        if chat_id in self.tgcalls.streams or await queue_manager.get_queue(chat_id):
            await db.touch_assistant_active(chat_id, time.time())
            return False

        user_client = self.tgcalls.client
        try:
            member = await user_client.get_chat_member(chat_id, "me")
        except Exception as e:
            logger.info(f"Assistant is no longer in {chat_id} ({type(e).__name__}); dropping idle tracking")
            await db.clear_assistant_active(chat_id)
            return False

        if member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            logger.info(f"Assistant is {member.status.name.lower()} in {chat_id}; not leaving")
            await db.clear_assistant_active(chat_id)
            return False

        await user_client.leave_chat(chat_id)
        await db.clear_assistant_active(chat_id)
        logger.info(
            f"Assistant left {chat_id} after {Config.ASSISTANT_IDLE_LEAVE_SECONDS}s idle; "
            f"it will rejoin on the next play request"
        )
        return True


idle_leave_manager = IdleLeaveManager()
