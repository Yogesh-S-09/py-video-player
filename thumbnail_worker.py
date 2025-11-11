# thumbnail_worker.py
# (UPDATED to remove emojis from the log handler)

import logging
import mpv
import tempfile
import os
import urllib.request
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
    # Replace emojis to be safe
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
    # ... (rest of the file is unchanged) ...
    
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
             
        self.thumbnail_path = os.path.join(self.temp_dir, f"{safe_filename}_{row_index}.jpg")

    def run(self):
        try:
            if os.path.exists(self.thumbnail_path):
                logger.debug(f"Loading cached thumbnail for: {self.filepath}")
                metadata = self.fetch_metadata_fast()
                icon = QIcon(self.thumbnail_path)
                self.thumbnail_ready.emit(self.row_index, icon, metadata['duration'], metadata['resolution'])
                return

            logger.debug(f"Fetching metadata and thumbnail for: {self.filepath}")
            
            ydl_opts = {
                'quiet': True,
                'skip_download': True,
                'forcejson': True,
                'extract_flat': False,
            }

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.filepath, download=False)
            
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
                urllib.request.urlretrieve(thumbnail_url, self.thumbnail_path)
            
                if os.path.exists(self.thumbnail_path):
                    icon = QIcon(self.thumbnail_path)
                    self.thumbnail_ready.emit(self.row_index, icon, duration_str, resolution_str)
                else:
                    raise Exception("Thumbnail download failed.")
            else:
                logger.debug("No web thumbnail found, sending metadata only.")
                self.thumbnail_ready.emit(self.row_index, QIcon(), duration_str, resolution_str)

        except Exception as e:
            logger.error(f"Thumbnail worker failed for {self.filepath}: {e}", exc_info=True)
            self.thumbnail_failed.emit(self.row_index, str(e))

    def fetch_metadata_fast(self):
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'forcejson': True,
            'extract_flat': True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(self.filepath, download=False)
        
        duration = info.get('duration', 0)
        width = info.get('width', 0)
        height = info.get('height', 0)
        
        return {
            'duration': format_time(duration),
            'resolution': f"{width}x{height}" if width > 0 else "N/A"
        }