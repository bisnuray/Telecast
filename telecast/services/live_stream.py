# Copyright (C) @itsSmartDev

import asyncio
import os
import re
import time
from typing import Dict, Optional

from aiohttp import web

from telecast.core.logging import logger

IDLE_TIMEOUT = 30.0
CLIENT_WAIT = 5.0
WRITE_CHUNK = 1 << 16


class _Stream:
    def __init__(self, path: str, state: Dict):
        self.path = path
        self.state = state

    @property
    def total(self) -> int:
        try:
            return int(self.state.get('total') or 0)
        except (TypeError, ValueError):
            return 0

    @property
    def finished(self) -> bool:
        return bool(self.state.get('done')) or bool(self.state.get('error'))

    def resolve(self) -> str:
        if os.path.exists(self.path):
            return self.path
        final = self.state.get('final_path')
        if final and os.path.exists(final):
            return final
        return self.path

    def available(self) -> int:
        try:
            return os.path.getsize(self.resolve())
        except OSError:
            return 0


class LiveStreamServer:
    def __init__(self):
        self._runner = None
        self._site = None
        self._base = ""
        self._streams: Dict[str, _Stream] = {}
        self._counter = 0

    @property
    def running(self) -> bool:
        return self._site is not None

    async def start(self) -> bool:
        if self.running:
            return True
        try:
            app = web.Application()
            app.router.add_get('/stream/{token}', self._handle)
            self._runner = web.AppRunner(app, access_log=None)
            await self._runner.setup()
            self._site = web.TCPSite(self._runner, '127.0.0.1', 0)
            await self._site.start()
            port = self._site._server.sockets[0].getsockname()[1]
            self._base = f'http://127.0.0.1:{port}/stream'
            logger.info(f"Live stream server listening on {self._base}")
            return True
        except Exception as e:
            logger.error(f"Failed to start live stream server: {e}")
            self._site = None
            self._runner = None
            return False

    async def stop(self):
        try:
            if self._runner:
                await self._runner.cleanup()
        except Exception as e:
            logger.error(f"Failed to stop live stream server: {e}")
        finally:
            self._runner = None
            self._site = None
            self._streams.clear()

    def register(self, path: str, state: Dict) -> str:
        self._counter += 1
        token = f"{int(time.time())}_{self._counter}"
        self._streams[token] = _Stream(path, state)
        return f"{self._base}/{token}"

    def release(self, url: Optional[str]):
        token = self._token_of(url)
        if token:
            self._streams.pop(token, None)

    def local_path(self, url: Optional[str]) -> Optional[str]:
        token = self._token_of(url)
        if not token:
            return None
        stream = self._streams.get(token)
        return stream.resolve() if stream else None

    def is_finished(self, url: Optional[str]) -> bool:
        token = self._token_of(url)
        if not token:
            return True
        stream = self._streams.get(token)
        return stream.finished if stream else True

    @staticmethod
    def is_stream_url(url) -> bool:
        return (
            isinstance(url, str)
            and url.startswith('http://127.0.0.1:')
            and '/stream/' in url
        )

    def _token_of(self, url: Optional[str]) -> Optional[str]:
        if not self.is_stream_url(url):
            return None
        return url.rsplit('/', 1)[-1]

    async def _handle(self, request: web.Request) -> web.StreamResponse:
        stream = self._streams.get(request.match_info['token'])
        if stream is None:
            raise web.HTTPNotFound(reason='unknown stream')

        deadline = time.monotonic() + CLIENT_WAIT
        while stream.total == 0 and not stream.finished and time.monotonic() < deadline:
            await asyncio.sleep(0.05)

        total = stream.total
        range_header = request.headers.get('Range')
        start = 0
        end = total - 1 if total else None

        if range_header:
            match = re.match(r'bytes=(\d+)-(\d*)', range_header)
            if match:
                start = int(match.group(1))
                if match.group(2):
                    end = int(match.group(2))
                elif total:
                    end = total - 1

        response = web.StreamResponse(status=206 if range_header else 200)
        response.headers['Accept-Ranges'] = 'bytes'
        response.headers['Content-Type'] = 'application/octet-stream'
        if total:
            response.headers['Content-Range'] = f'bytes {start}-{end}/{total}'
            if end is not None:
                response.headers['Content-Length'] = str(max(0, end - start + 1))
        await response.prepare(request)

        position = start
        last_progress = time.monotonic()
        handle = None
        try:
            while True:
                available = stream.available()
                if position < available:
                    if handle is None:
                        handle = open(stream.resolve(), 'rb')
                    handle.seek(position)
                    chunk = handle.read(min(WRITE_CHUNK, available - position))
                    if chunk:
                        await response.write(chunk)
                        position += len(chunk)
                        last_progress = time.monotonic()
                        continue
                if stream.finished:
                    break
                if time.monotonic() - last_progress > IDLE_TIMEOUT:
                    logger.warning("Live stream stalled, closing response")
                    break
                await asyncio.sleep(0.02)
        except (ConnectionResetError, asyncio.CancelledError):
            raise
        except Exception as e:
            logger.error(f"Live stream error: {e}")
        finally:
            if handle:
                handle.close()

        try:
            await response.write_eof()
        except Exception:
            pass
        return response


live_stream = LiveStreamServer()
