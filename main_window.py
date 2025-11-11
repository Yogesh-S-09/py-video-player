# main_window.py
# (UPDATED to fix icon path and 'Open With' logic)

import logging
import os
import sys
from PySide6.QtWidgets import (
    QMainWindow, QFileDialog, QMenuBar, QStyle, 
    QMessageBox, QInputDialog, QListWidget,
    QStackedWidget
)
from PySide6.QtGui import (
    QAction, QKeySequence, 
    QDesktopServices, QIcon
)
from PySide6.QtCore import QSize, Slot, QUrl, Qt
from pathlib import Path

from persistence_manager import PersistenceManager
from player_widget import PlayerWidget
from library_widget import LibraryWidget
from stream_extractor import get_all_streams

logger = logging.getLogger(__name__)

def resource_path(relative_path):
    # ... (this function is unchanged) ...
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 MPV Player")
        self.resize(1000, 600)
        
        # --- FIX: Use correct icon path ---
        icon_path = resource_path("Assets/icon.png")
        if Path(icon_path).exists():
            self.setWindowIcon(QIcon(icon_path))
        else:
            logger.warning(f"Could not find icon at: {icon_path}")
        # ----------------------------------
        
        self.persistence_manager = PersistenceManager()
        self.stack = QStackedWidget()
        self.player_widget = PlayerWidget(self, self.persistence_manager)
        self.library_widget = LibraryWidget(self.persistence_manager, self)
        self.stack.addWidget(self.library_widget)
        self.stack.addWidget(self.player_widget)
        self.setCentralWidget(self.stack)
        self.create_menu()
        self.player_widget.toggle_fullscreen_requested.connect(self.toggle_fullscreen)
        self.library_widget.play_file_requested.connect(self.play_file_and_switch)
        self.player_widget.playback_finished.connect(self.on_playback_finished)
        self.player_widget.show_library_requested.connect(self.switch_to_library)
        self.player_widget.overlay.prev_file_btn.clicked.connect(self.library_widget.play_previous)
        self.player_widget.overlay.next_file_btn.clicked.connect(
            lambda: self.library_widget.play_next(loop_all=False)
        )
        self.library_widget.count_changed.connect(self.on_playlist_count_changed)

    def create_menu(self):
        # ... (this method is unchanged) ...
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        add_files_action = QAction("&Add File(s) to Library...", self) 
        add_files_action.setShortcut(QKeySequence.StandardKey.Open)
        add_files_action.triggered.connect(self.library_widget.open_add_files_dialog)
        file_menu.addAction(add_files_action)
        open_network_action = QAction("&Open Network Stream...", self)
        open_network_action.setShortcut(QKeySequence("Ctrl+N"))
        open_network_action.triggered.connect(self.open_network_stream)
        file_menu.addAction(open_network_action)
        file_menu.addSeparator()
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        view_menu = menu_bar.addMenu("&View")
        go_to_library_action = QAction("Show Library", self)
        go_to_library_action.setShortcut("Ctrl+P")
        go_to_library_action.triggered.connect(self.switch_to_library) 
        view_menu.addAction(go_to_library_action)
        help_menu = menu_bar.addMenu("&Help")
        help_action = QAction("&Help", self)
        help_action.setShortcut(QKeySequence.StandardKey.HelpContents)
        help_action.triggered.connect(self.open_help_link)
        help_menu.addAction(help_action)
        help_menu.addSeparator()
        about_action = QAction("&About...", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    @Slot(int)
    def on_playlist_count_changed(self, count):
        # ... (this method is unchanged) ...
        self.player_widget.overlay.set_playlist_controls_visible(count > 1)

    @Slot(bool)
    def on_playback_finished(self, loop_all_is_active):
        # ... (this method is unchanged) ...
        if loop_all_is_active:
            logger.info("File ended, Loop All active: calling play_next(True).")
            self.library_widget.play_next(loop_all=True)
        else:
            logger.info("File ended, Loop Off: switching to library.")
            self.switch_to_library()
            
    # --- THIS IS THE UPDATED METHOD ---
    @Slot(str, list, list)
    def play_file_and_switch(self, filepath, audio_tracks, video_tracks):
        """Loads a file in the player and switches to the player view."""
        if filepath is None:
            self.switch_to_library()
            return
            
        # --- This call is now correct ---
        self.player_widget.load_file(filepath, audio_tracks, video_tracks)
        self.stack.setCurrentWidget(self.player_widget)
    # ------------------------------------

    @Slot()
    def switch_to_library(self):
        # ... (this method is unchanged) ...
        logger.debug("Switching to library view.")
        self.player_widget.hide_controls(force=True)
        self.player_widget.save_current_position()
        self.player_widget.player.stop()
        self.stack.setCurrentWidget(self.library_widget)
        if self.isFullScreen():
            self.toggle_fullscreen()
            
    @Slot()
    def open_network_stream(self):
        # ... (this method is unchanged) ...
        url, ok = QInputDialog.getText(self, "Open Network Stream", "Enter URL:")
        if not (ok and url):
            return
        logger.info(f"User entered URL: {url}. Fetching streams...")
        stream_data = get_all_streams(url)
        if not stream_data or not stream_data.get('video_streams'):
            QMessageBox.warning(self, "No Streams Found", "Could not find any playable video streams at that URL.")
            return
        self.library_widget.add_file(
            filepath=url, 
            display_name=stream_data.get('title', url),
            stream_data=stream_data
        )
        main_video_url = stream_data['video_streams'][0]['url']
        other_video_tracks = stream_data['video_streams'][1:]
        audio_tracks = stream_data.get('audio_streams', [])
        self.play_file_and_switch(main_video_url, audio_tracks, other_video_tracks)
    
    @Slot()
    def toggle_fullscreen(self):
        # ... (this method is unchanged) ...
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
        # ... (this method is unchanged) ...
        about_text = (
            "<b>PySide6 MPV Player</b><br><br>"
            "A professional media player built with PySide6 and python-mpv.<br><br>"
            "This application is for demonstration purposes."
        )
        QMessageBox.about(self, "About Player", about_text)

    @Slot()
    def open_help_link(self):
        # ... (this method is unchanged) ...
        url = QUrl("https://mpv.io/manual/stable/")
        if not QDesktopServices.openUrl(url):
            logger.warning(f"Could not open URL: {url.toString()}")
            
    def closeEvent(self, event):
        # ... (this method is unchanged) ...
        logger.info("Shutting down...") 
        self.player_widget.save_current_position()
        self.player_widget.shutdown()
        event.accept()

    def keyPressEvent(self, event):
        # ... (this method is unchanged) ...
        focused = self.focusWidget()
        if focused and isinstance(focused, (QInputDialog, QListWidget)):
             super().keyPressEvent(event)
             return
        if event.key() == Qt.Key.Key_Space:
            self.player_widget.toggle_pause()
            event.accept()
        elif event.key() == Qt.Key.Key_F:
            self.toggle_fullscreen()
            event.accept()
        elif event.key() == Qt.Key.Key_Escape and self.isFullScreen():
            if self.stack.currentWidget() == self.player_widget:
                self.toggle_fullscreen()
            event.accept()
        elif event.key() == Qt.Key.Key_Right:
            self.player_widget.seek_forward()
            event.accept()
        elif event.key() == QtKey.Key_Left:
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