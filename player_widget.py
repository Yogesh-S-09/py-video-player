# player_widget.py
# (UPDATED with seek and volume-add methods)

import logging 
import mpv
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, 
    QApplication
)
from PySide6.QtCore import Qt, QTimer, Signal
from overlay_widget import OverlayWidget

logger = logging.getLogger(__name__)

def mpv_log_handler(level, prefix, text):
    # ... (this function is unchanged) ...
    text = text.strip();
    if level == 'error': logger.error(f"[MPV:{prefix}] {text}")
    elif level == 'warn': logger.warning(f"[MPV:{prefix}] {text}")
    elif level == 'info': logger.info(f"[MPV:{prefix}] {text}")
    elif level == 'debug': logger.debug(f"[MPV:{prefix}] {text}")
    else: logger.debug(f"[MPV:{prefix} ({level})] {text}")


class PlayerWidget(QWidget):
    # ... (signals are unchanged) ...
    pause_changed = Signal(bool); time_pos_changed = Signal(float)
    duration_changed = Signal(float); track_list_changed = Signal(list, str, str, str)
    aid_changed = Signal(str); sid_changed = Signal(str); vid_changed = Signal(str)
    toggle_fullscreen_requested = Signal(); volume_changed = Signal(int)
    mute_changed = Signal(bool); chapter_list_changed = Signal(list)
    chapter_changed = Signal(int)
    
    def __init__(self, parent=None):
        # ... (init is unchanged) ...
        super().__init__(parent)
        self.player = None; self.overlay = None; self.current_aid = 'no'
        self.current_sid = 'no'; self.current_vid = 'no'
        self.chapter_list = []; self.current_chapter = 0
        self.video_widget = QWidget(self)
        self.video_widget.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
        self.video_widget.setStyleSheet("background-color: black;")
        layout = QVBoxLayout(); layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.video_widget); self.setLayout(layout)
        self.setMouseTracking(True); self.video_widget.setMouseTracking(True)
        self.video_widget.setFocus() 
        self.hide_timer = QTimer(self); self.hide_timer.setInterval(3000)
        self.hide_timer.setSingleShot(True); self.hide_timer.timeout.connect(self.hide_controls)
        self.initialize_player()
        if self.player:
            self.overlay = OverlayWidget(self.player, self)
            self.overlay.hide()
            self.setup_observers()
            self.setup_connections()

    def initialize_player(self):
        # ... (this method is unchanged) ...
        try:
            self.player = mpv.MPV(
                wid=str(int(self.video_widget.winId())), vo='gpu',
                log_handler=mpv_log_handler, input_default_bindings=True,
                input_vo_keyboard=True
            )
            self.player.volume = 100 
            logger.info("MPV Player initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing MPV: {e}", exc_info=True)
            error_label = QLabel(f"Error: {e}\nIs mpv installed?", self.video_widget)
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("color: red; background-color: black;")

    def setup_observers(self):
        # ... (this method is unchanged) ...
        if not self.player: return
        self.player.observe_property('pause', lambda n, v: self.pause_changed.emit(v if v is not None else False))
        self.player.observe_property('time-pos', lambda n, v: self.time_pos_changed.emit(v if v is not None else 0.0))
        self.player.observe_property('duration', lambda n, v: self.duration_changed.emit(v if v is not None else 0.0))
        self.player.observe_property('volume', lambda n, v: self.volume_changed.emit(int(v) if v is not None else 100))
        self.player.observe_property('mute', lambda n, v: self.mute_changed.emit(v if v is not None else False))
        self.player.observe_property('track-list', 
            lambda n, v: self.track_list_changed.emit(
                v if v is not None else [], self.current_aid,
                self.current_sid, self.current_vid
            ))
        self.player.observe_property('aid', self.on_aid_change)
        self.player.observe_property('sid', self.on_sid_change)
        self.player.observe_property('vid', self.on_vid_change)
        self.player.observe_property('chapter-list', self.on_chapter_list_change)
        self.player.observe_property('chapter', self.on_chapter_change)

    def on_aid_change(self, name, value):
        # ... (this method is unchanged) ...
        self.current_aid = str(value) if value is not None else 'no'
        self.aid_changed.emit(self.current_aid)
        
    def on_sid_change(self, name, value):
        # ... (this method is unchanged) ...
        self.current_sid = str(value) if value is not None else 'no'
        self.sid_changed.emit(self.current_sid)
        
    def on_vid_change(self, name, value):
        # ... (this method is unchanged) ...
        self.current_vid = str(value) if value is not None else 'no'
        self.vid_changed.emit(self.current_vid)

    def on_chapter_list_change(self, name, value):
        # ... (this method is unchanged) ...
        self.chapter_list = value or []
        self.chapter_list_changed.emit(self.chapter_list)
        
    def on_chapter_change(self, name, value):
        # ... (this method is unchanged) ...
        self.current_chapter = value or 0
        self.chapter_changed.emit(self.current_chapter)

    def setup_connections(self):
        if not self.overlay: return
        # ... (other connections unchanged) ...
        self.pause_changed.connect(self.overlay.update_pause_button)
        self.time_pos_changed.connect(self.overlay.update_time)
        self.duration_changed.connect(self.overlay.update_duration)
        self.track_list_changed.connect(self.overlay.update_track_menus)
        self.aid_changed.connect(lambda v: self.overlay.update_track_selection('aid', v))
        self.sid_changed.connect(lambda v: self.overlay.update_track_selection('sid', v))
        self.vid_changed.connect(lambda v: self.overlay.update_track_selection('vid', v))
        self.overlay.fullscreen_toggled.connect(self.toggle_fullscreen_requested.emit)
        self.volume_changed.connect(self.overlay.update_volume_slider)
        self.mute_changed.connect(self.overlay.update_mute_button)
        self.chapter_list_changed.connect(self.overlay.update_chapter_menu)
        self.chapter_changed.connect(self.overlay.update_chapter_selection)

    def toggle_pause(self):
        # ... (this method is unchanged) ...
        if self.player: self.player.pause = not self.player.pause

    def next_chapter(self):
        # ... (this method is unchanged) ...
        if self.player: self.player.command('add', 'chapter', 1)
            
    def prev_chapter(self):
        # ... (this method is unchanged) ...
        if self.player: self.player.command('add', 'chapter', -1)
    
    # --- NEW METHODS ---
    def seek_forward(self):
        """Seeks forward 10 seconds."""
        if self.player:
            self.player.command('seek', 10, 'relative')
            
    def seek_backward(self):
        """Seeks backward 10 seconds."""
        if self.player:
            self.player.command('seek', -10, 'relative')
            
    def add_volume(self, amount):
        """Adds a value (e.g., +/- 5) to the current volume."""
        if self.player:
            self.player.command('add', 'volume', amount)
    # -------------------

    def load_file(self, filepath):
        # ... (this method is unchanged) ...
        if self.player:
            logger.info(f"Loading file: {filepath}")
            self.player.play(filepath); self.player.pause = False
            self.show_controls()
            
    def load_network_stream(self, url):
        # ... (this method is unchanged) ...
        if self.player:
            logger.info(f"Loading network stream with yt-dlp: {url}")
            prefixed_url = f"ytdl://{url}"
            self.player.play(prefixed_url); self.player.pause = False
            self.show_controls()
            
    def shutdown(self):
        # ... (this method is unchanged) ...
        if self.player:
            logger.info("Shutting down MPV player.")
            self.player.stop(); self.player.command('quit'); self.player.terminate()
        else:
            logger.info("Shutdown called, but no player instance found.")

    def resizeEvent(self, event):
        # ... (this method is unchanged) ...
        if self.overlay:
            overlay_height = self.overlay.sizeHint().height()
            x = 0; y = self.height() - overlay_height
            w = self.width(); h = overlay_height
            self.overlay.setGeometry(x, y, w, h)
        super().resizeEvent(event)

    def mouseMoveEvent(self, event):
        # ... (this method is unchanged) ...
        self.show_controls(); super().mouseMoveEvent(event)
        
    def mousePressEvent(self, event):
        # ... (this method is unchanged) ...
        if not self.player or not self.overlay:
            super().mousePressEvent(event); return
        self.video_widget.setFocus()
        if not self.overlay.isVisible():
            self.show_controls()
        elif not self.overlay.geometry().contains(event.pos()):
            self.hide_controls()
        widget = QApplication.widgetAt(event.globalPos())
        if widget and self.overlay.isAncestorOf(widget): pass
        else: super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        # ... (this method is unchanged) ...
        self.toggle_fullscreen_requested.emit(); super().mouseDoubleClickEvent(event)

    def show_controls(self):
        # ... (this method is unchanged) ...
        if self.overlay:
            self.overlay.show()
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.hide_timer.start()
            focused_widget = QApplication.instance().focusWidget()
            if not (focused_widget and self.overlay.isAncestorOf(focused_widget)):
                 self.video_widget.setFocus()

    def hide_controls(self):
        # ... (this method is unchanged) ...
        if self.overlay:
            focused_widget = QApplication.instance().focusWidget()
            is_overlay_focused = False
            if focused_widget:
                widget = focused_widget
                while widget: 
                    if widget == self.overlay:
                        is_overlay_focused = True; break
                    widget = widget.parent()
            if is_overlay_focused:
                self.hide_timer.start(); return
            self.overlay.hide()
            self.setCursor(Qt.CursorShape.BlankCursor)