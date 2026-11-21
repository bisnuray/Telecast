# Copyright (C) @itsSmartDev

class ChatSettingsMixin:
    async def get_chat_settings(self, chat_id):
        settings = await self.db.chat_settings.find_one({"chat_id": chat_id})
        if not settings:
            settings = {
                "chat_id": chat_id,
                "mode": "audio",
                "quality": "720p",
                "audio_quality": "high",
                "audio_effect": "none",
                "playback_speed": 1.0,
                "autoplay": False,
                "autoplay_permission": "everyone",
                "title_update": False,
                "preferred_source": "youtube",
                "loop_mode": "off",
                "mention_requester": True,
                "vc_welcome": True
            }
            await self.db.chat_settings.insert_one(settings)
        return settings

    async def update_chat_settings(self, chat_id, updates):
        await self.db.chat_settings.update_one(
            {"chat_id": chat_id},
            {"$set": updates},
            upsert=True
        )

    async def touch_assistant_active(self, chat_id, when):
        await self.db.chat_settings.update_one(
            {"chat_id": chat_id},
            {"$set": {"assistant_last_active": when}},
            upsert=True
        )

    async def clear_assistant_active(self, chat_id):
        await self.db.chat_settings.update_one(
            {"chat_id": chat_id},
            {"$unset": {"assistant_last_active": ""}}
        )

    async def get_idle_assistant_chats(self, cutoff, limit=20):
        cursor = self.db.chat_settings.find(
            {"assistant_last_active": {"$lte": cutoff}},
            {"chat_id": 1, "_id": 0},
        ).limit(limit)
        return [doc["chat_id"] async for doc in cursor]
