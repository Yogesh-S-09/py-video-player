# thumbnail_worker.py
# (UPDATED with hybrid logic for local vs network files)

import logging
import mpv
import tempfile
import os
import urllib.request
import urllib.error
import socket
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QIcon
from utils import format_time
from pathlib import Path
from yt_dlp import YoutubeDL

logger = logging.getLogger(__name__)

# --- UPDATED LOG HANDLER (Emojis removed) ---
def worker_log_handler(level, prefix, text):
    """
    A simple wrapper function to catch MPV's log messages from
    this worker thread and pass them to our main logger.
    """
    text = text.strip()
    text = text.replace("📺", "[Video]").replace("🔊", "[Audio]")
    
    if level == 'error':
        logger.error(f"[Worker-MPV:{prefix}] {text}")
    elif level == 'warn':
        logger.warning(f"[Worker-MPV:{prefix}] {text}")
    elif level == 'info':
        logger.info(f"[Worker-MPV:{prefix}] {text}")
    elif level == 'debug':
        logger.debug(f"[Worker-MPV:{prefix}] {text}")
    else:
        logger.debug(f"[Worker-MPV:{prefix} ({level})] {text}")
# ------------------------------------------

class ThumbnailWorker(QThread):
    
    thumbnail_ready = Signal(int, QIcon, str, str)
    thumbnail_failed = Signal(int, str)

    def __init__(self, filepath, row_index, parent=None):
        super().__init__(parent)
        self.filepath = filepath
        self.row_index = row_index
        
        self.temp_dir = os.path.join(tempfile.gettempdir(), "py-mpv-player-cache")
        os.makedirs(self.temp_dir, exist_ok=True)
        
        safe_filename = "".join(c for c in Path(filepath).name if c.isalnum())
        if not safe_filename:
             safe_filename = str(hash(filepath))
             
        # Use .jpg for consistency
        self.thumbnail_path = os.path.join(self.temp_dir, f"{safe_filename}_{row_index}.jpg")

    def run(self):
        """Runs the background task."""
        try:
            # --- 1. Check for cached thumbnail ---
            if os.path.exists(self.thumbnail_path):
                logger.debug(f"Loading cached thumbnail for: {self.filepath}")
                metadata = self.fetch_metadata_fast()
                icon = QIcon(self.thumbnail_path)
                self.thumbnail_ready.emit(self.row_index, icon, metadata['duration'], metadata['resolution'])
                return

            # --- 2. Run correct task based on file type ---
            if self.filepath.startswith('http'):
                self.run_network_task()
            else:
                self.run_local_task()

        except Exception as e:
            logger.error(f"Thumbnail worker failed for {self.filepath}: {e}", exc_info=True)
            self.thumbnail_failed.emit(self.row_index, str(e))

    def run_network_task(self):
        """Uses yt-dlp to fetch metadata and thumbnail for a URL."""
        logger.debug(f"Fetching network metadata and thumbnail for: {self.filepath}")
        
        ydl_opts = {
            'quiet': True, 'skip_download': True,
            'forcejson': True, 'extract_flat': False,
            'socket_timeout': 10,  # Add timeout
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.filepath, download=False)
        except Exception as e:
            logger.error(f"Failed to extract info for {self.filepath}: {e}")
            raise
        
        duration = info.get('duration', 0)
        width = info.get('width', 0)
        height = info.get('height', 0)
        duration_str = format_time(duration)
        resolution_str = f"{width}x{height}" if width > 0 else "N/A"
        
        thumbnail_url = None
        if info.get('thumbnails'):
            thumbnail_url = info['thumbnails'][-1].get('url')
        
        if thumbnail_url:
            logger.debug(f"Downloading thumbnail from: {thumbnail_url}")
            try:
                # Set timeout for network request
                old_timeout = socket.getdefaulttimeout()
                socket.setdefaulttimeout(10)
                try:
                    urllib.request.urlretrieve(thumbnail_url, self.thumbnail_path)
                finally:
                    socket.setdefaulttimeout(old_timeout)
                    
                if os.path.exists(self.thumbnail_path):
                    icon = QIcon(self.thumbnail_path)
                    self.thumbnail_ready.emit(self.row_index, icon, duration_str, resolution_str)
                else:
                    raise Exception("Thumbnail download failed.")
            except (urllib.error.URLError, socket.timeout, OSError) as e:
                logger.warning(f"Failed to download thumbnail: {e}. Using metadata only.")
                self.thumbnail_ready.emit(self.row_index, QIcon(), duration_str, resolution_str)
        else:
            logger.debug("No web thumbnail found, sending metadata only.")
            self.thumbnail_ready.emit(self.row_index, QIcon(), duration_str, resolution_str)

    def run_local_task(self):
        """Uses mpv (headless) to fetch metadata and thumbnail for a local file."""
        logger.debug(f"Generating local thumbnail for: {self.filepath}")
        
        player = None
        try:
            player = mpv.MPV(
                vo='null',  # No video output window
                log_handler=worker_log_handler,
                ytdl=False  # Not needed for local files
            )

            player.play(self.filepath)
            player.wait_for_property('duration')
            
            duration = player.duration or 0
            width = player.width or 0
            height = player.height or 0
            
            duration_str = format_time(duration)
            resolution_str = f"{width}x{height}" if width > 0 else "N/A"
            
            seek_time = min(duration * 0.1, 5.0)
            
            player.time_pos = seek_time
            player.wait_for_property('playback-time')
            
            player.command('screenshot-to-file', self.thumbnail_path, 'video')

            if os.path.exists(self.thumbnail_path):
                icon = QIcon(self.thumbnail_path)
                self.thumbnail_ready.emit(self.row_index, icon, duration_str, resolution_str)
            else:
                raise Exception("Screenshot file was not created.")
        finally:
            if player:
                try:
                    player.terminate()
                except Exception as e:
                    logger.warning(f"Failed to terminate player: {e}")

    def fetch_metadata_fast(self):
        """
        Lightweight metadata fetch for cached files.
        This must also be hybrid.
        """
        player = None
        try:
            if self.filepath.startswith('http'):
                ydl_opts = {
                    'quiet': True, 'skip_download': True,
                    'forcejson': True, 'extract_flat': True,
                    'socket_timeout': 10
                }
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(self.filepath, download=False)
                duration = info.get('duration', 0)
                width = info.get('width', 0)
                height = info.get('height', 0)
            else:
                player = mpv.MPV(vo='null', log_handler=worker_log_handler, ytdl=False)
                player.play(self.filepath)
                player.wait_for_property('duration')
                duration = player.duration or 0
                width = player.width or 0
                height = player.height or 0
            
            return {
                'duration': format_time(duration),
                'resolution': f"{width}x{height}" if width > 0 else "N/A"
            }
        finally:
            if player:
                try:
                    player.terminate()
                except Exception as e:
                    logger.warning(f"Failed to terminate player in metadata fetch: {e}")