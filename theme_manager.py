import logging
from PySide6.QtWidgets import QApplication
from themes import THEMES
from PySide6.QtCore import QSettings

logger = logging.getLogger(__name__)

class ThemeManager:
    def __init__(self, app: QApplication):
        self.app = app
        self.themes = THEMES
        
        self.settings = QSettings("MyAwesomePlayer", "PySideMPV")
        saved_theme = self.settings.value("current_theme", "Nord Dark")
        
        self.current_theme = saved_theme if saved_theme in self.themes else "Nord Dark"
        self.apply_theme(self.current_theme)


    def get_theme_names(self):
        """Returns a list of available theme names."""
        return list(self.themes.keys())

    def apply_theme(self, theme_name):
        """Applies a theme by its name."""
        if theme_name not in self.themes:
            logger.warning(f"Theme '{theme_name}' not found. Using default.")
            theme_name = "Nord Dark"
            
        stylesheet = self.themes[theme_name]
        self.app.setStyleSheet(stylesheet)
        self.current_theme = theme_name        
        self.settings.setValue("current_theme", theme_name)      
        logger.info(f"Applied theme: {theme_name}")