# main_window.py
# (UPDATED to set the window icon)

import logging
import os   # --- IMPORT OS ---
import sys  # --- IMPORT SYS ---
from PySide6.QtWidgets import (
    QMainWindow, QFileDialog, QMenuBar, QStyle, 
    QMessageBox, QInputDialog
)
from PySide6.QtGui import (
    QAction, QKeySequence, 
    QDesktopServices, QIcon  # --- IMPORT QIcon ---
)
from PySide6.QtCore import QSize, Slot, QUrl, Qt, QSettings
from pathlib import Path
from player_widget import PlayerWidget

logger = logging.getLogger(__name__)

# --- NEW HELPER FUNCTION ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Not running in a PyInstaller bundle
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
# ---------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 MPV Player")
        self.resize(800, 600)
        
        # --- SET THE ICON HERE ---
        icon_path = resource_path("icon.png")
        if Path(icon_path).exists():
            self.setWindowIcon(QIcon(icon_path))
        else:
            logger.warning(f"Could not find icon at: {icon_path}")
        # -------------------------
        
        self.settings = QSettings("MyAwesomePlayer", "PySideMPV")
        
        self.player_widget = PlayerWidget(self)
        self.setCentralWidget(self.player_widget)
        
        self.create_menu()
        self.player_widget.toggle_fullscreen_requested.connect(self.toggle_fullscreen)

    # ... (the rest of the file is exactly the same) ...

    def create_menu(self):
        # ... (unchanged) ...
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        open_action = QAction("&Open File...", self) 
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        open_network_action = QAction("&Open Network Stream...", self)
        open_network_action.setShortcut(QKeySequence("Ctrl+N"))
        open_network_action.triggered.connect(self.open_network_stream)
        file_menu.addAction(open_network_action)
        file_menu.addSeparator()
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        help_menu = menu_bar.addMenu("&Help")
        help_action = QAction("&Help", self)
        help_action.setShortcut(QKeySequence.StandardKey.HelpContents)
        help_action.triggered.connect(self.open_help_link)
        help_menu.addAction(help_action)
        help_menu.addSeparator()
        about_action = QAction("&About...", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
        
    @Slot()
    def open_file(self):
        # ... (unchanged) ...
        last_path = self.settings.value("last_open_path", "") 
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open Video File",
            last_path, # Use the last path here
            "Video Files (*.mp4 *.mkv *.avi *.mov);;All Files (*.*)"
        )
        if filepath:
            self.settings.setValue("last_open_path", str(Path(filepath).parent))
            self.player_widget.load_file(filepath)
            
    @Slot()
    def open_network_stream(self):
        # ... (unchanged) ...
        url, ok = QInputDialog.getText(self, "Open Network Stream", "Enter URL:")
        if ok and url:
            logger.info(f"User entered URL: {url}")
            self.player_widget.load_network_stream(url)
    
    @Slot()
    def toggle_fullscreen(self):
        # ... (unchanged) ...
        if self.isFullScreen():
            self.showNormal()
            self.player_widget.overlay.fullscreen_btn.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp)
            )
            self.menuBar().setVisible(True)
        else:
            self.showFullScreen()
            self.player_widget.overlay.fullscreen_btn.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowDown)
            )
            self.menuBar().setVisible(False)
            
    @Slot()
    def show_about_dialog(self):
        # ... (unchanged) ...
        about_text = (
            "<b>PySide6 MPV Player</b><br><br>"
            "A professional media player built with PySide6 and python-mpv.<br><br>"
            "This application is for demonstration purposes."
        )
        QMessageBox.about(self, "About Player", about_text)

    @Slot()
    def open_help_link(self):
        # ... (unchanged) ...
        url = QUrl("https://mpv.io/manual/stable/")
        if not QDesktopServices.openUrl(url):
            logger.warning(f"Could not open URL: {url.toString()}")
            
    def closeEvent(self, event):
        # ... (unchanged) ...
        logger.info("Shutting down...") 
        self.player_widget.shutdown()
        event.accept()

    def keyPressEvent(self, event):
        # ... (unchanged) ...
        if self.focusWidget() and isinstance(self.focusWidget(), (QInputDialog)):
             super().keyPressEvent(event)
             return
        if event.key() == Qt.Key.Key_Space:
            self.player_widget.toggle_pause()
            event.accept()
        elif event.key() == Qt.Key.Key_F:
            self.toggle_fullscreen()
            event.accept()
        elif event.key() == Qt.Key.Key_Escape and self.isFullScreen():
            self.toggle_fullscreen()
            event.accept()
        elif event.key() == Qt.Key.Key_Right:
            self.player_widget.seek_forward()
            event.accept()
        elif event.key() == Qt.Key.Key_Left:
            self.player_widget.seek_backward()
            event.accept()
        elif event.key() == Qt.Key.Key_Up:
            self.player_widget.add_volume(5)
            event.accept()
        elif event.key() == Qt.Key.Key_Down:
            self.player_widget.add_volume(-5)
            event.accept()
        else:
            super().keyPressEvent(event)