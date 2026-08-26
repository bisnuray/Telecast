# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

**Telecast** — a Telegram voice-chat music/video bot. Users request YouTube tracks (or send Telegram audio/video files) in a group; the bot downloads/streams them into the group's live voice chat with inline player controls, playlists, audio effects, and rankings.

It is a single-process async Python application (no web framework, no Dockerfile, no test suite). There is no README and no lint/format config.

## Running

```bash
pip install -r requirements.txt   # kurigram (a Pyrogram fork), py-tgcalls, ntgcalls, motor, yt-dlp, Pillow, numpy, ...
python bot.py                     # start the bot
```

Runtime prerequisites (not installable via pip):
- **ffmpeg** on `PATH` — used for audio effects (in-process via `py-tgcalls`) and re-encoding in `media/processor.py`.
- **`yt-dlp` CLI** on `PATH` — `media/processor.get_stream_url` shells out to it for live-stream URL extraction (the Python `yt_dlp` lib handles the rest).
- **MongoDB** running (default `mongodb://localhost:27017/vcbot`) — all persistence goes through it.

There is **no build step, linter, or test runner configured**. Verification is done by running the bot and observing logs (`logs/bot.log` plus stdout).

## Configuration

Secrets and tunables come from `.env` (see `.env.example`): `API_ID`, `API_HASH`, `BOT_TOKEN`, `SESSION_STRING`, `MONGODB_URI`, `LOG_LEVEL`, `LOG_CHAT_ID`, plus limits (`MAX_QUEUE_SIZE`, `MAX_CONCURRENT_CHATS`, `MAX_PLAYLIST_TRACKS`, `MAX_TRACK_DURATION`). `Config.validate()` (`config.py`) hard-fails on startup if required values are missing. `Config.BOT_OWNER_ID` is hardcoded, not env-driven.

Runtime dirs `downloads/`, `cache/`, `logs/` are wiped and recreated on every startup (`VCMusicBot._cleanup_files`). `cookies/yt.txt` is a Netscape-format cookie file that `yt-dlp` reads for YouTube.

## Architecture

The entrypoint `bot.py` (`VCMusicBot`) wires everything together. The single most important structural fact: **there are two Pyrogram clients**.

- `vc_music_bot` — the bot (BOT_TOKEN). Handles all commands, callbacks, and messages.
- `user_client` — a user account (SESSION_STRING). `py-tgcalls` requires a *user* account to stream into voice chats, so this account actually joins the call and streams. `utils/auto_join.py` adds this account to a chat (via invite link / public join / join-request approval) before playback.

The `tgcalls` package name is misleadingly similar to the bot concept: it is the **`py-tgcalls` wrapper** (`tgcalls/manager.py`), not the app's own code.

Data flow for a play request:

```
handlers/commands.py (play_command)
  -> media/downloader.py  (yt-dlp metadata, run in a threadpool)
  -> music_queue/manager.py  (in-memory list + MongoDB persistence)
  -> player/controller.py  (play / play_next / pause / seek / loop / effects / volume)
  -> tgcalls/manager.py  (py-tgcalls stream + VC join/leave/empty-leave)
```

Key modules:

- **`player/controller.py`** — `PlayerController`, the heart of playback. All per-chat state is held in dicts keyed by `chat_id` (`current_playing`, `loop_modes`, `now_playing_messages`, pause bookkeeping). `play_next` implements loop modes, queue advance, playlist lazy-fetch, and autoplay stub. Playback errors are caught and translated into user-facing messages here.
- **`tgcalls/manager.py`** — `TGCallsManager`, wraps `PyTgCalls`. Owns stream state, join/leave/control timeouts (`_await_op` + `asyncio.wait_for` to prevent silent event-loop stalls), join retries with FLOOD_WAIT backoff, a VC-member cache, and empty-VC auto-leave. Custom exceptions (`FloodWaitError`, `TelegramServerError`, `StreamOperationTimeout`) are defined here.
- **`music_queue/manager.py`** — `QueueManager`. Queue is an in-memory `dict[chat_id, list[track]]` lazily loaded from MongoDB and re-saved on every mutation. Also tracks `playlist_states` for lazy playlist fetching (a playlist URL is ingested 10 tracks at a time, not all at once).
- **`database/mongodb.py`** — the only DB access layer, via async `motor`. Collections: `chat_settings`, `queues`, `playlists`, `vc_admins`, `broadcast_users`, `broadcast_groups`, `play_history`, `stats`. Per-chat settings are fetched with `get_chat_settings` (inserts defaults on first access).
- **`media/`** — `downloader.py` (yt-dlp in a `ThreadPoolExecutor`, with a 300s in-memory metadata cache and file-existence cache), `processor.py` (ffmpeg subprocess + Telegram file download + `yt-dlp -g` for streams), `effects.py` (FFmpeg filter preset strings — see gotchas).
- **`handlers/`** — `commands.py` (text commands), `callbacks.py` (one big `callback_data`-prefix router for all inline buttons), `broadcast.py` (owner `/broadcast`), `events.py` (group add/remove tracking), `inline.py` (YouTube inline search).
- **`ui/`** — `keyboards.py` + `messages.py` (all button/markup and message text), `title_updater.py` (edits the live group-call title via `user_client` raw `EditGroupCallTitle`), `progress_updater.py` (20s background loop editing the now-playing message), `banner_renderer.py` + `rankings_banner.py` (Pillow/numpy image rendering for `/rank`).
- **`utils/`** — `permissions.py` (admin/VC-admin checks), `auto_join.py` (adds user client to chats, handles ban/unban/join-request), `validators.py` (source detection: youtube/url/search), `watchdog.py` (event-loop stall detector), `monitor_logger.py` (Telegram log-channel notifications).

## Patterns and gotchas

- **Module-level singletons + post-init wiring.** Most modules expose an instance at import time (`queue_manager`, `db`, `downloader`, `processor`, `playlist_manager`, `monitor_logger`). But `player_controller`, `title_updater`, `progress_updater`, and `live_stream_handler` are `None` at import and are **assigned onto the module objects** by `bot.py` after construction (e.g. `import player.controller as pc_mod; pc_mod.player_controller = self.player_controller`). Code that needs them imports the *module* (`import ui.title_updater`) and dereferences the attribute, not `from ... import title_updater`, which would capture the stale `None`.
- **Blocking work must stay off the event loop.** The whole bot runs on one loop; a single blocking call freezes every command silently (the reason `utils/watchdog.py` exists). yt-dlp runs via `loop.run_in_executor`, Pillow rendering via `asyncio.to_thread`, ffmpeg via `asyncio.create_subprocess_exec`. Follow this pattern for anything CPU/IO-heavy.
- **`track` dict shape.** Tracks are plain dicts with `type` (`youtube` | `telegram` | `url` | `live`), `url`, `title`, `duration`, `uploader`, `is_live`, `requested_by`/`requested_by_id`, and `_raw_info` (the full yt-dlp info dict, carried through to avoid re-extracting metadata on download). The player mutates `track['seek_position']` and `track['file_path']`.
- **FFmpeg audio filters** (`media/effects.py`) must be placed in the audio stream's **`mid` (post-input) section** using the `--audio -x:mid -af <filter>` structural markers; `-ss` seek stays pre-input. Placing `-af` before `-i` makes FFmpeg abort ("Option af cannot be applied to input").
- **Callback `answer()` ordering.** Buttons that re-stream (seek/rewind/effect/speed) must `callback_query.answer(...)` *before* awaiting the operation — rejoining the stream can exceed Telegram's ~15s callback window and otherwise throws `QUERY_ID_INVALID`.
- **Callbacks are admin/VC-admin gated** except ranking buttons, help, and back-to-start (see the top of `handle_callback`). `/play` respects the `admin_only` chat setting; control commands always require admin/VC-admin.
- **State is chat-scoped, in-memory, and mirrored to MongoDB.** On a VC close (`_on_vc_closed`) the queue is cleared and all per-chat state is dropped; the queue is the source of truth for what plays next.
