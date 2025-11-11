# persistence_manager.py

import logging
from PySide6.QtCore import QSettings
from pathlib import Path

logger = logging.getLogger(__name__)

class PersistenceManager:
    """
    Manages all application settings and persistent data,
    such as playback positions and last-used paths.
    """
    def __init__(self):
        # We define a company and app name for QSettings
        self.settings = QSettings("MyAwesomePlayer", "PySideMPV")
        logger.info("Persistence Manager initialized.")

    def save_last_open_path(self, filepath):
        """Saves the parent directory of the last file opened."""
        try:
            path = Path(filepath)
            self.settings.setValue("last_open_path", str(path.parent))
        except Exception as e:
            logger.error(f"Failed to save last open path: {e}")

    def load_last_open_path(self):
        """Loads the last-used directory path."""
        return self.settings.value("last_open_path", "")

    def save_playback_position(self, filepath, time_pos):
        """Saves the playback time (in seconds) for a specific file."""
        if not filepath or time_pos is None:
            return
        
        # We store playback positions in a 'group'
        self.settings.beginGroup("playback_positions")
        # Use the filepath as the key
        self.settings.setValue(filepath, time_pos)
        self.settings.endGroup()
        logger.debug(f"Saved position for {filepath}: {time_pos}")

    def load_playback_position(self, filepath):
        """
        Loads the last-saved playback time for a specific file.
        Returns the time in seconds (float) or 0.0 if not found.
        """
        if not filepath:
            return 0.0
            
        self.settings.beginGroup("playback_positions")
        time_pos = self.settings.value(filepath, 0.0)
        self.settings.endGroup()
        
        try:
            return float(time_pos)
        except ValueError:
            return 0.0