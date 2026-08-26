# Copyright (C) @itsSmartDev

from typing import Dict, List

class Messages:
    @staticmethod
    def now_playing(track: Dict, requested_by: str = "Unknown", current_time: int = 0, queue: List[Dict] = None, playlist_unfetched: int = 0) -> str:
        title = track.get('title', 'Unknown')

        message = f"![🎵](tg://emoji?id=5334665104677941170) **Music Playlist:**\n\n"

        req_id = track.get('requested_by_id')
        if req_id:
            req_mention = f"[{requested_by}](tg://user?id={req_id})"
        else:
            req_mention = requested_by

        message += f"**1. ![🎸](tg://emoji?id=5465665777619204788) {title}**\n"
        message += f"![🏆](tg://emoji?id=5409008750893734809) **Requested by:** {req_mention}\n\n"

        if queue and len(queue) > 1:
            for i, next_track in enumerate(queue[1:4], start=2):
                next_title = next_track.get('title', 'Unknown')
                if len(next_title) > 50:
                    next_title = next_title[:47] + "..."
                next_name = next_track.get('requested_by', 'Unknown')
                next_id = next_track.get('requested_by_id')
                if next_id:
                    next_mention = f"[{next_name}](tg://user?id={next_id})"
                else:
                    next_mention = next_name
                message += f"**{i}. ![🎸](tg://emoji?id=5465665777619204788) {next_title}**\n"
                message += f"![🏆](tg://emoji?id=5409008750893734809) **Requested by:** {next_mention}\n\n"

            shown = min(len(queue), 4)
            remaining_in_queue = len(queue) - shown
            total_remaining = remaining_in_queue + playlist_unfetched
            if total_remaining > 0:
                message += f"**✨ {total_remaining} tracks still in the playlist.....**"

        return message

    @staticmethod
    def _create_progress_bar(current: int, total: int, length: int = 20) -> str:
        if total == 0:
            return "━" * length

        filled = int((current / total) * length)
        bar = "━" * filled + "🔘" + "━" * (length - filled - 1)
        return bar

    @staticmethod
    def queue_list(queue: List[Dict], page: int = 0, page_size: int = 10) -> str:
        if not queue:
            return "📄 **Queue is empty**"

        start = page * page_size
        end = start + page_size
        page_queue = queue[start:end]

        message = f"📄 **Queue** ({len(queue)} tracks)\n\n"

        for i, track in enumerate(page_queue, start=start+1):
            title = track.get('title', 'Unknown')
            duration = Messages._format_duration(track.get('duration', 0))
            message += f"{i}. **{title}** `[{duration}]`\n"

        total_pages = (len(queue) + page_size - 1) // page_size
        message += f"\nPage {page+1}/{total_pages}"

        return message

    @staticmethod
    def settings_info(settings: Dict) -> str:
        message = "⚙️ **Configure Your VCPlayer Settings Here.**\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━━"

        return message

    @staticmethod
    def track_added(track: Dict, position: int) -> str:
        title = track.get('title', 'Unknown')
        return f"✅ Added to queue at position {position}\n**{title}**"

    @staticmethod
    def queue_updated(queue: List[Dict]) -> str:
        if not queue:
            return "📄 **Queue is empty**"

        message = f"![🎵](tg://emoji?id=5334665104677941170) **Music Playlist:**\n\n"

        for i, track in enumerate(queue[:5], start=1):
            track_title = track.get('title', 'Unknown')
            if len(track_title) > 60:
                track_title = track_title[:57] + "..."
            req_name = track.get('requested_by', 'Unknown')
            req_id = track.get('requested_by_id')
            if req_id:
                req_mention = f"[{req_name}](tg://user?id={req_id})"
            else:
                req_mention = req_name
            message += f"**{i}. ![🎸](tg://emoji?id=5465665777619204788) {track_title}**\n"
            message += f"![🏆](tg://emoji?id=5409008750893734809) **Requested by:** {req_mention}\n\n"

        if len(queue) > 5:
            remaining = len(queue) - 5
            message += f"**✨ {remaining} tracks still in the playlist.....**"

        return message

    @staticmethod
    def playlist_saved(name: str, count: int) -> str:
        return f"💾 Playlist **{name}** saved with {count} tracks"

    @staticmethod
    def playlist_loaded(name: str, count: int) -> str:
        return f"📀 Loaded playlist **{name}** with {count} tracks"

    @staticmethod
    def error(message: str) -> str:
        return f"❌ **Error:** {message}"

    @staticmethod
    def success(message: str) -> str:
        return f"✅ {message}"

    @staticmethod
    def _format_duration(seconds: int) -> str:
        if seconds == 0:
            return "Live"

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"

    @staticmethod
    def start_welcome() -> str:
        return (
            "![🎧](tg://emoji?id=5334665104677941170) **Welcome to Telecast!**\n"
            "Your all-in-one voice chat player for music and video\n\n"
            "![🎵](tg://emoji?id=5334665104677941170) Play music & videos\n"
            "⚡️ Smooth streaming\n"
            "📌 Multi-chat support\n"
            "🏚 Full controls (pause, skip, seek, shuffle, replay)\n"
            "💿 Audio & video modes\n\n"
            "![🚀](tg://emoji?id=5429440296867886716) Choose an option below to get started!"
        )

    @staticmethod
    def help_message() -> str:
        return (
            "![🎵](tg://emoji?id=5334665104677941170) **Telecast Bot Commands**\n\n"
            "**Basic Commands:**\n"
            "`/start` - Show welcome message\n"
            "`/help` - Show this help message\n"
            "`/status` - Show bot statistics\n"
            "`/rank` or `/ranking` - View group rankings\n\n"
            "**Music Commands:** (Use in groups)\n"
            "`/play <query>` - Play a song from YouTube\n"
            "`/pause` - Pause current playback\n"
            "`/resume` - Resume playback\n"
            "`/skip` - Skip to next track\n"
            "`/stop` - Stop and leave voice chat\n"
            "`/playlist` - View current queue\n"
            "`/clearplaylist` - Clear upcoming tracks\n"
            "`/seek <seconds>` - Seek forward/backward\n"
            "`/rewind` - Rewind 10 seconds\n"
            "🎚 **Effects** - Tap the Effects button on the player for bassboost/nightcore/slowed/lofi/8d + speed control\n\n"
            "**Settings:** (Admin only)\n"
            "`/settings` - Configure bot settings\n"
            "`/vcadmin` - Add voice chat admin\n"
            "`/vcunadmin` - Remove voice chat admin\n\n"
            "**Owner Commands:**\n"
            "`/restart` - Restart the bot\n\n"
            "📌 **Note:** Most commands work only in groups where the bot is admin."
        )

    @staticmethod
    def dm_not_allowed() -> str:
        return "Add me to a group to play music!"

    @staticmethod
    def status_message(total_users: int, total_groups: int, total_songs: int, active_vcs: int,
                       ping: float = None, cpu_usage: float = None) -> str:
        text = (
            f"📊 **Bot Usage Report**\n"
            f"━━━━━━━━━━━\n"
            f"**Total Users:** {total_users}\n"
            f"**Total Groups:** {total_groups}\n"
            f"**Total Songs Played:** {total_songs}\n"
            f"**Active Voice Chats:** {active_vcs}"
        )
        if ping is not None or cpu_usage is not None:
            text += "\n\n🛰 **Voice Engine**\n"
            if ping is not None:
                text += f"**Ping:** {ping:.1f} ms\n"
            if cpu_usage is not None:
                text += f"**CPU Usage:** {cpu_usage:.1f}%"
        return text

    @staticmethod
    def ranking_message(stats: Dict, period: str = "Daily") -> str:
        message = f"![🏆](tg://emoji?id=5409008750893734809) **Group Rankings - {period}**\n"
        message += "━━━━━━━━━━━━━━━━\n\n"

        if not stats or not stats.get('total_stats'):
            return message + "❌ No data available for this period."

        top_users = stats.get('top_users', [])
        top_songs = stats.get('top_songs', [])
        total_stats = stats.get('total_stats', {})

        if top_users:
            message += "👥 **Top 5 Users:**\n"
            for i, user in enumerate(top_users, 1):
                user_name = user['_id']['user_name']
                count = user['count']
                message += f"{i}. {user_name} - {count} songs\n"
            message += "\n"
        else:
            message += "👥 **Top 5 Users:**\nNo data available\n\n"

        if top_songs:
            message += "![🎵](tg://emoji?id=5334665104677941170) **Top 5 Songs:**\n"
            for i, song in enumerate(top_songs, 1):
                song_title = song['_id']
                if len(song_title) > 40:
                    song_title = song_title[:37] + "..."
                count = song['count']
                message += f"{i}. {song_title} - {count} plays\n"
            message += "\n"
        else:
            message += "![🎵](tg://emoji?id=5334665104677941170) **Top 5 Songs:**\nNo data available\n\n"

        message += "📊 **Stats:**\n"
        total_songs = total_stats.get('total_songs', 0)
        unique_users = len(total_stats.get('unique_users', []))
        total_duration = total_stats.get('total_duration', 0)

        hours = total_duration // 3600
        minutes = (total_duration % 3600) // 60

        message += f"Total Songs: {total_songs}\n"
        message += f"Active Users: {unique_users}\n"
        message += f"Listening Time: {hours}h {minutes}m\n"

        return message

    @staticmethod
    def global_ranking_message(stats: Dict) -> str:
        message = "🌍 **Global Rankings**\n"
        message += "━━━━━━━━━━━━━━━━\n\n"

        if not stats or not stats.get('total_stats'):
            return message + "❌ No data available."

        top_groups = stats.get('top_groups', [])
        top_users = stats.get('top_users', [])
        top_songs = stats.get('top_songs', [])
        total_stats = stats.get('total_stats', {})

        if top_groups:
            message += "![🏆](tg://emoji?id=5409008750893734809) **Top 5 Groups:**\n"
            for i, group in enumerate(top_groups, 1):
                chat_title = group.get('chat_title', 'Unknown Group')
                if len(chat_title) > 30:
                    chat_title = chat_title[:27] + "..."
                count = group['count']
                message += f"{i}. {chat_title} - {count} songs\n"
            message += "\n"
        else:
            message += "![🏆](tg://emoji?id=5409008750893734809) **Top 5 Groups:**\nNo data available\n\n"

        if top_users:
            message += "👥 **Top 5 Users:**\n"
            for i, user in enumerate(top_users, 1):
                user_name = user['_id']['user_name']
                count = user['count']
                message += f"{i}. {user_name} - {count} songs\n"
            message += "\n"
        else:
            message += "👥 **Top 5 Users:**\nNo data available\n\n"

        if top_songs:
            message += "![🎵](tg://emoji?id=5334665104677941170) **Top 5 Songs:**\n"
            for i, song in enumerate(top_songs, 1):
                song_title = song['_id']
                if len(song_title) > 40:
                    song_title = song_title[:37] + "..."
                count = song['count']
                message += f"{i}. {song_title} - {count} plays\n"
            message += "\n"
        else:
            message += "![🎵](tg://emoji?id=5334665104677941170) **Top 5 Songs:**\nNo data available\n\n"

        message += "📊 **Global Stats:**\n"
        total_songs = total_stats.get('total_songs', 0)
        unique_groups = len(total_stats.get('unique_groups', []))
        total_duration = total_stats.get('total_duration', 0)

        hours = total_duration // 3600
        minutes = (total_duration % 3600) // 60

        message += f"Total Songs: {total_songs}\n"
        message += f"Total Groups: {unique_groups}\n"
        message += f"Total Time: {hours}h {minutes}m\n"

        return message

messages = Messages()
