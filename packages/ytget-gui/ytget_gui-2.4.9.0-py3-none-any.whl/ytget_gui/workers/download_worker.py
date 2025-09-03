# File: ytget_gui/workers/download_worker.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from PySide6.QtCore import QObject, Signal, QProcess, QTimer
import os
import re
from pathlib import Path

from ytget_gui.styles import AppStyles
from ytget_gui.settings import AppSettings


@dataclass
class QueueItem:
    url: str
    title: str
    format_code: str


class DownloadWorker(QObject):
    log = Signal(str, str)
    finished = Signal(int)
    error = Signal(str)

    def __init__(self, item: Dict[str, Any], settings: AppSettings, log_flush_ms: int = 1000):
        super().__init__()
        self.item = item
        self.settings = settings
        self.process: Optional[QProcess] = None
        self._cancel_requested = False

        # --- Optimisation: log batching ---
        self._log_buffer: list[tuple[str, str]] = []
        self._log_timer = QTimer(self)
        self._log_timer.setInterval(log_flush_ms)
        self._log_timer.timeout.connect(self._flush_logs)
        self._log_timer.start()

        # --- Precompile error detection regex ---
        self._error_regex = re.compile(r"error", re.IGNORECASE)

    def run(self):
        try:
            cmd = self._build_command()
            self._add_log(
                f"🚀 Starting Download for: {self._short(self.item['title'])}\n",
                AppStyles.INFO_COLOR,
            )
            self.process = QProcess()
            self.process.setProcessChannelMode(QProcess.MergedChannels)
            self.process.readyReadStandardOutput.connect(self._on_read)
            self.process.errorOccurred.connect(self._on_error)
            self.process.finished.connect(self._on_finished)
            self.process.start(cmd[0], cmd[1:])
            if not self.process.waitForStarted(5000):
                self.error.emit("Failed to start yt-dlp process.")
                self.finished.emit(-1)
        except Exception as e:
            self.error.emit(f"Error preparing download: {e}")
            self.finished.emit(-1)

    def cancel(self):
        self._cancel_requested = True
        if self.process and self.process.state() == QProcess.Running:
            self._add_log("⏹️ Cancelling Download...\n", AppStyles.WARNING_COLOR)
            self.process.terminate()
            if not self.process.waitForFinished(3000):
                self.process.kill()

    def _on_read(self):
        if not self.process:
            return
        text = self.process.readAllStandardOutput().data().decode(errors="ignore")
        color = AppStyles.ERROR_COLOR if self._error_regex.search(text) else AppStyles.TEXT_COLOR
        self._add_log(text, color)

    def _on_error(self, _code):
        self._add_log("❌ yt-dlp encountered an error.\n", AppStyles.ERROR_COLOR)

    def _on_finished(self, exit_code: int, _status):
        if self._cancel_requested:
            self._add_log("⏹️ Download cancelled by user.\n", AppStyles.WARNING_COLOR)
            self.finished.emit(-1)
        elif exit_code == 0:
            self._add_log("✅ Download Finished Successfully.\n", AppStyles.SUCCESS_COLOR)
            QTimer.singleShot(0, self._post_finish_cleanup)
            self.finished.emit(0)
        else:
            self._add_log(f"❌ yt-dlp exited with code {exit_code}.\n", AppStyles.ERROR_COLOR)
            self.finished.emit(exit_code)

    def _post_finish_cleanup(self):
        try:
            if self._is_audio_download():
                cleaned = self._clean_music_video_tags()
                if cleaned > 0:
                    self._add_log(f"✨ Cleaned {cleaned} filename(s).\n", AppStyles.SUCCESS_COLOR)
        except Exception as e:
            self._add_log(f"⚠️ Filename cleanup failed: {e}\n", AppStyles.WARNING_COLOR)

    def _short(self, title: str) -> str:
        return title[:50] + "..." if len(title) > 50 else title

    @staticmethod
    def is_short_video(url: str) -> bool:
        return "youtube.com/shorts/" in url

    def _is_audio_download(self) -> bool:
        code = self.item["format_code"]
        return code in ("bestaudio", "playlist_mp3", "youtube_music", "audio_flac")

    def _should_force_title(self, is_playlist: bool) -> bool:
        s = self.settings
        no_cookie = not (s.COOKIES_PATH.exists() and s.COOKIES_PATH.stat().st_size > 0)
        no_browser = not bool(s.COOKIES_FROM_BROWSER)
        return (not is_playlist) and no_cookie and no_browser

    def _safe_filename(self, name: str) -> str:
        if not name:
            return "Unknown"
        name = "".join(ch for ch in name if ord(ch) >= 32)
        name = re.sub(r'[\\/:*?"<>|]', " ", name)
        name = re.sub(r"\s+", " ", name).strip().rstrip(" .")
        reserved = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}
        if name.upper() in reserved:
            name += "_"
        if len(name) > 180:
            name = name[:180].rstrip(" .")
        return name or "Unknown"

    def _build_command(self) -> List[str]:
        s = self.settings
        it = self.item

        cmd: List[str] = [
            str(s.YT_DLP_PATH),
            "--no-warnings",
            "--progress",
            "--output-na-placeholder", "Unknown",
            "--ffmpeg-location", str(s.FFMPEG_PATH.parent),
        ]

        format_code = it["format_code"]
        is_playlist = "list=" in it["url"] or format_code in ("playlist_mp3", "youtube_music")
        is_audio = self._is_audio_download()
        is_flac = (format_code == "audio_flac")

        # Auth/network
        if s.COOKIES_PATH.exists() and s.COOKIES_PATH.stat().st_size > 0:
            cmd.extend(["--cookies", str(s.COOKIES_PATH)])
        if s.COOKIES_FROM_BROWSER:
            cmd.extend(["--cookies-from-browser", s.COOKIES_FROM_BROWSER])
        if s.PROXY_URL:
            cmd.extend(["--proxy", s.PROXY_URL])
        if s.LIMIT_RATE:
            cmd.extend(["--limit-rate", s.LIMIT_RATE])
        cmd.extend(["--retries", str(s.RETRIES)])

        # Filters and playlist behavior
        if s.DATEAFTER:
            cmd.extend(["--dateafter", s.DATEAFTER])
        if s.LIVE_FROM_START:
            cmd.append("--live-from-start")
        if is_playlist:
            cmd.append("--ignore-errors")
        if s.ENABLE_ARCHIVE:
            cmd.extend(["--download-archive", str(s.ARCHIVE_PATH)])
        if s.PLAYLIST_REVERSE:
            cmd.append("--playlist-reverse")
        if s.PLAYLIST_ITEMS:
            cmd.extend(["--playlist-items", s.PLAYLIST_ITEMS])
        if s.CLIP_START and s.CLIP_END:
            cmd.extend(["--download-sections", f"*{s.CLIP_START}-{s.CLIP_END}"])

        # Decide output base directory
        if is_playlist:
            base = Path(s.DOWNLOADS_DIR) / "%(playlist_title)s"
            if s.ORGANIZE_BY_UPLOADER:
                base /= "%(uploader)s"
        else:
            base = Path(s.DOWNLOADS_DIR)
            if s.ORGANIZE_BY_UPLOADER:
                base /= "%(uploader)s"

        # Filename template
        if s.YT_MUSIC_METADATA and (is_audio or is_playlist):
            fallback = "%(artist)s - %(title)s.%(ext)s"
        else:
            fallback = "%(title)s.%(ext)s"

        if self._should_force_title(is_playlist):
            safe = self._safe_filename(it.get("title") or "Unknown")
            filename = f"{safe}.%(ext)s"
        else:
            filename = fallback

        out_tmpl = str(Path(base) / filename)
        if is_playlist:
            cmd.extend(["--yes-playlist", "-o", out_tmpl])
        else:
            cmd.extend(["-o", out_tmpl])

        # Audio-only path
        if is_audio:
            cmd.extend([
                "-f", "bestaudio",
                "--extract-audio",
                "--audio-format", "flac" if is_flac else "mp3",
                "--embed-thumbnail",        
            ])
            if s.ADD_METADATA:
                cmd.append("--add-metadata")
            if not is_flac:
                cmd.extend(["--audio-quality", "0"])
            if is_flac:
                cmd.extend(["--postprocessor-args", "ffmpeg:-compression_level 12 -sample_fmt s16"])
            if format_code == "youtube_music" and s.YT_MUSIC_METADATA:
                cmd.extend([
                    "--parse-metadata", "description:(?s)(?P<meta_comment>.+)",
                    "--parse-metadata", "%(meta_comment)s:(?P<artist>[^\n]+)",
                    "--parse-metadata", "%(meta_comment)s:.+ - (?P<title>[^\n]+)",
                ])
        else:
            # Video path
            preferred = (s.VIDEO_FORMAT.lstrip(".")) or "mkv"
            if preferred not in {"mkv", "mp4", "webm"}:
                preferred = "mkv"
            cmd.extend(["-f", format_code, "--merge-output-format", preferred])
            if s.ADD_METADATA:
                cmd.append("--add-metadata")

        # SponsorBlock
        if s.SPONSORBLOCK_CATEGORIES and not self.is_short_video(it["url"]):
            cmd.extend(["--sponsorblock-remove", ",".join(s.SPONSORBLOCK_CATEGORIES)])
            cmd.extend(["--sleep-requests", "1", "--sleep-subtitles", "1"])

        # Chapters
        if s.CHAPTERS_MODE == "split":
            cmd.append("--split-chapters")
        elif s.CHAPTERS_MODE == "embed":
            cmd.append("--embed-chapters")

        # Subtitles
        if s.WRITE_SUBS:
            cmd.append("--write-subs")
            if s.SUB_LANGS:
                cmd.extend(["--sub-langs", s.SUB_LANGS])
            if s.WRITE_AUTO_SUBS:
                cmd.append("--write-auto-subs")
            if s.CONVERT_SUBS_TO_SRT:
                cmd.extend(["--convert-subs", "srt"])

        # Write thumbnail
        if s.WRITE_THUMBNAIL:
            cmd.append("--write-thumbnail")

        # Convert thumbnail
        if s.CONVERT_THUMBNAILS:
            fmt = s.THUMBNAIL_FORMAT or "png"
            cmd.extend(["--convert-thumbnails", fmt])

        # Embed thumbnail in video container
        if s.EMBED_THUMBNAIL and not is_audio:
            # Log the cover-embed event
            self._add_log(
                f"🖼️ Embedding thumbnail as cover for: {self._short(it['title'])}\n",
                AppStyles.INFO_COLOR
            )
            cmd.append("--embed-thumbnail")
            fmt = s.THUMBNAIL_FORMAT or "png"
            meta = f"ffmpeg:-metadata:s:t mimetype=image/{fmt} -metadata:s:t filename=cover.{fmt}"
            cmd.extend(["--postprocessor-args", meta])

        # Custom FFmpeg args
        if s.CUSTOM_FFMPEG_ARGS:
            cmd.extend(["--postprocessor-args", f"ffmpeg:{s.CUSTOM_FFMPEG_ARGS}"])

        # Finally the URL
        cmd.append(it["url"])
        return cmd

    def _clean_music_video_tags(self) -> int:
        downloads_root: Path = Path(self.settings.DOWNLOADS_DIR)
        if not downloads_root.exists():
            return 0
        audio_exts = {".mp3", ".flac"}
        tag_texts = [
            "(music video)", "(official video)", "(official visualizer)", "(video oficial)",
            "[official video]", "(drone)", "(video)", "(visualiser)", "(lyric video)", "(lyrics)",
            "(audio)", "(official track)", "(original mix)", "(hq)", "(hd)", "(high quality)",
            "(full song)", "(snippet)", "(reaction)", "(review)", "(trailer)", "(teaser)",
            "(fan edit)", "(studio version)", "(youtube)", "(vevo)", "(tiktok)",
            "(drone shot)", "(pov video)", "(official music video)",
        ]
        escaped = "|".join(re.escape(t) for t in tag_texts)
        combined = re.compile(r"\s*(?:" + escaped + r")", re.IGNORECASE)
        renamed = 0

        for root, _dirs, files in os.walk(downloads_root):
            for fname in files:
                p = Path(root) / fname
                if p.suffix.lower() not in audio_exts:
                    continue
                if not combined.search(fname):
                    continue
                new_stem = combined.sub("", p.stem)
                new_stem = re.sub(r"\s{2,}", " ", new_stem).strip(" -_.,")
                if not new_stem:
                    new_stem = p.stem
                new_name = f"{new_stem}{p.suffix}"
                new_path = p.with_name(new_name)
                if new_path == p:
                    continue
                if new_path.exists():
                    i = 1
                    while True:
                        candidate = p.with_name(f"{new_stem} ({i}){p.suffix}")
                        if not candidate.exists():
                            new_path = candidate
                            break
                        i += 1
                try:
                    p.rename(new_path)
                    renamed += 1
                    self._add_log(f"🧹 Renamed: {p.name} → {new_path.name}\n", AppStyles.INFO_COLOR)
                except Exception as e:
                    self._add_log(f"⚠️ Could not rename {p.name}: {e}\n", AppStyles.WARNING_COLOR)
        return renamed

    # --- Optimisation helpers ---
    def _add_log(self, text: str, color: str):
        """
        Buffer a log entry instead of emitting immediately.
        """
        self._log_buffer.append((text, color))

    def _flush_logs(self):
        """
        Emit any buffered log entries to connected slots, then clear the buffer.
        """
        if not self._log_buffer:
            return
        for text, color in self._log_buffer:
            self.log.emit(text, color)
        self._log_buffer.clear()
