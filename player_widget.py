# player_widget.py
# (UPDATED to remove emojis from the log handler)

import logging 
import mpv
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, 
    QApplication, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot
from overlay_widget import OverlayWidget
from persistence_manager import PersistenceManager
from utils import format_time

logger = logging.getLogger(__name__)

# --- UPDATED LOG HANDLER (Emojis removed) ---
def mpv_log_handler(level, prefix, text):
    """
    A simple wrapper function to catch MPV's log messages and
    pass them to our main logger.
    """
    text = text.strip()
    text = text.replace("📺", "[Video]").replace("🔊", "[Audio]")
    
    if level == 'error':
        logger.error(f"[MPV:{prefix}] {text}")
    elif level == 'warn':
        logger.warning(f"[MPV:{prefix}] {text}")
    elif level == 'info':
        logger.info(f"[MPV:{prefix}] {text}")
    elif level == 'debug':
        logger.debug(f"[MPV:{prefix}] {text}")
    else:
        logger.debug(f"[MPV:{prefix} ({level})] {text}")
# ------------------------------------------

class PlayerWidget(QWidget):
    # ... (rest of the file is unchanged) ...
    
    pause_changed = Signal(bool); time_pos_changed = Signal(float)
    duration_changed = Signal(float); track_list_changed = Signal(list, str, str, str)
    aid_changed = Signal(str); sid_changed = Signal(str); vid_changed = Signal(str)
    toggle_fullscreen_requested = Signal(); volume_changed = Signal(int)
    mute_changed = Signal(bool); chapter_list_changed = Signal(list)
    chapter_changed = Signal(int); playback_finished = Signal(bool)
    show_library_requested = Signal()
    loop_state_changed = Signal(str)
    end_file_signal = Signal()
    
    def __init__(self, parent=None, persistence_manager: PersistenceManager = None):
        super().__init__(parent)
        self.persistence_manager = persistence_manager
        self.player = None
        self.overlay = None 
        self.current_aid = 'no'
        self.current_sid = 'no'
        self.current_vid = 'no'
        self.chapter_list = [] 
        self.current_chapter = 0
        self.current_filepath = None
        self.loop_state = 0
        self.pending_resume_time = 0.0
        self.is_initialized = False
       
        self.video_widget = QWidget(self)
        self.video_widget.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
        self.video_widget.setStyleSheet("background-color: black;")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.video_widget)
        self.setLayout(layout)

        self.setMouseTracking(True)
        self.video_widget.setMouseTracking(True)
        self.video_widget.setFocus() 

        self.hide_timer = QTimer(self)
        self.hide_timer.setInterval(3000)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide_controls)

        self.overlay = OverlayWidget(None, self)  # Create overlay without player
        self.create_basic_connections()

    def ensure_initialized(self):
        """Initialize MPV player on first use."""
        if not self.is_initialized:
            self.initialize_player()
            if self.player:
                self.player.event_callback('playback-restart')(self.on_playback_restart_event)
                self.player.event_callback('end-file')(self.on_end_file_event)
                self.overlay.player = self.player  # Update overlay reference
                self.setup_observers()
                self.setup_full_connections()
            self.is_initialized = True

    def create_basic_connections(self):
        """Setup connections that don't require MPV player."""
        if self.overlay:
            self.overlay.fullscreen_toggled.connect(self.toggle_fullscreen_requested.emit)
            self.overlay.back_requested.connect(self.show_library_requested.emit)

    def setup_full_connections(self):
        """Setup all MPV-dependent connections."""
        if not self.overlay:
            return
            
        self.pause_changed.connect(self.overlay.update_pause_button)
        self.time_pos_changed.connect(self.overlay.update_time)
        self.duration_changed.connect(self.overlay.update_duration)
        self.track_list_changed.connect(self.overlay.update_track_menus)
        self.aid_changed.connect(lambda v: self.overlay.update_track_selection('aid', v))
        self.sid_changed.connect(lambda v: self.overlay.update_track_selection('sid', v))
        self.vid_changed.connect(lambda v: self.overlay.update_track_selection('vid', v))
        self.volume_changed.connect(self.overlay.update_volume_slider)
        self.mute_changed.connect(self.overlay.update_mute_button)
        self.chapter_list_changed.connect(self.overlay.update_chapter_menu)
        self.chapter_changed.connect(self.overlay.update_chapter_selection)
        self.loop_state_changed.connect(self.overlay.update_loop_button)
        self.end_file_signal.connect(self.handle_end_file)
        
        # Connect overlay buttons to player methods
        if self.player:
            self.overlay.prev_chapter_btn.clicked.connect(self.prev_chapter)
            self.overlay.next_chapter_btn.clicked.connect(self.next_chapter)
            self.overlay.seek_backward_btn.clicked.connect(self.seek_backward)
            self.overlay.seek_forward_btn.clicked.connect(self.seek_forward)
            self.overlay.loop_btn.clicked.connect(self.cycle_loop_state)

    def initialize_player(self):
        try:
            self.player = mpv.MPV(
                wid=str(int(self.video_widget.winId())), vo='gpu',
                log_handler=mpv_log_handler, # Use the safe handler
                input_default_bindings=True,
                input_vo_keyboard=True,
                ytdl=True
            )
            self.player.volume = 100 
            logger.info("MPV Player initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing MPV: {e}", exc_info=True)
            error_label = QLabel(f"Error: {e}\nIs mpv installed?", self.video_widget)
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("color: red; background-color: black;")

    def setup_observers(self):
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
        self.current_aid = str(value) if value is not None else 'no'
        self.aid_changed.emit(self.current_aid)
    def on_sid_change(self, name, value):
        self.current_sid = str(value) if value is not None else 'no'
        self.sid_changed.emit(self.current_sid)
    def on_vid_change(self, name, value):
        self.current_vid = str(value) if value is not None else 'no'
        self.vid_changed.emit(self.current_vid)
    def on_chapter_list_change(self, name, value):
        self.chapter_list = value or []
        self.chapter_list_changed.emit(self.chapter_list)
    def on_chapter_change(self, name, value):
        self.current_chapter = value or 0
        self.chapter_changed.emit(self.current_chapter)

    def on_end_file_event(self, event):
        try:
            event_id = event.event_id
            reason = getattr(event.data, 'reason', None)
            
            # Check if this is an END_FILE event with EOF reason (normal playback end)
            # Multiple comparison methods for robustness across different mpv versions
            is_end_file = (event_id == mpv.MpvEventID.END_FILE or 
                          str(event_id) == 'end-file' or 
                          'end-file' in str(event_id).lower() or
                          (hasattr(event_id, 'value') and event_id.value == 7))
            
            if is_end_file:
                # In python-mpv, reason values:
                # 0 = EOF (End of File - normal end)
                # 2 = STOP (User stopped)
                # 3 = QUIT (Player quit)
                # 4 = ERROR (Playback error)
                
                if reason == 0:
                    logger.info("Video playback finished (EOF). Emitting end_file_signal.")
                    self.end_file_signal.emit()
                else:
                    logger.debug(f"End-file event with reason={reason} (not EOF, ignoring)")
        except Exception as e:
            logger.error(f"Error in on_end_file_event: {e}", exc_info=True)

    def on_playback_restart_event(self, event):
        try:
            logger.debug("Playback-restart event triggered.")
            if self.pending_resume_time > 0:
                self.player.time_pos = self.pending_resume_time
                self.pending_resume_time = 0.0
            self.player.pause = False
        except Exception as e:
            logger.error(f"Error in on_playback_restart_event: {e}", exc_info=True)
            self.player.pause = False

    @Slot()
    def handle_end_file(self):
        """Handle end-file signal and emit playback_finished if not in Loop One mode."""
        if self.loop_state == 1:
            logger.debug("Loop One active, video will repeat automatically.")
            return
        
        loop_all_active = self.loop_state == 2
        logger.info(f"Playback finished. Loop All: {loop_all_active}")
        self.playback_finished.emit(loop_all_active)

    def toggle_pause(self):
        if self.player:
            try:
                self.player.pause = not self.player.pause
            except Exception as e:
                logger.error(f"Failed to toggle pause: {e}")

    def next_chapter(self):
        if self.player and self.chapter_list:
            try:
                total_chapters = len(self.chapter_list)
                current_index = self.current_chapter # This is the 0-based index

                # Only advance if we are NOT on the last chapter
                if current_index < (total_chapters - 1):
                    new_index = current_index + 1
                    logger.debug(f"Setting chapter from {current_index} to {new_index}")
                    # Explicitly SET the chapter property to the new index
                    self.player.chapter = new_index
                else:
                    logger.debug("Already on last chapter, not advancing.")
                    
            except Exception as e:
                logger.error(f"Failed to set next chapter: {e}")

    def prev_chapter(self):
        if self.player and self.chapter_list:
            try:
                current_index = self.current_chapter # This is the 0-based index

                # Only go back if we are NOT on the first chapter
                if current_index > 0:
                    new_index = current_index - 1
                    logger.debug(f"Setting chapter from {current_index} to {new_index}")
                    # Explicitly SET the chapter property to the new index
                    self.player.chapter = new_index
                else:
                    logger.debug("Already on first chapter, not going back.")
                    
            except Exception as e:
                logger.error(f"Failed to set previous chapter: {e}")
                
    def seek_forward(self):
        if self.player:
            try:
                self.player.command('seek', 10, 'relative')
            except Exception as e:
                logger.error(f"Failed to seek forward: {e}")

    def seek_backward(self):
        if self.player:
            try:
                self.player.command('seek', -10, 'relative')
            except Exception as e:
                logger.error(f"Failed to seek backward: {e}")

    def add_volume(self, amount):
        if self.player:
            try:
                self.player.command('add', 'volume', amount)
            except Exception as e:
                logger.error(f"Failed to adjust volume: {e}")

    def toggle_mute(self):
        """Toggles the player's mute status."""
        if self.player:
            try:
                self.player.mute = not self.player.mute
            except Exception as e:
                logger.error(f"Failed to toggle mute: {e}")

    def cycle_subtitles(self):
        """Cycles to the next subtitle track."""
        if self.player:
            try:
                self.player.command('cycle', 'sub')
                logger.debug("Cycled subtitle track.")
            except Exception as e:
                logger.error(f"Failed to cycle subtitles: {e}")

    def cycle_audio_track(self):
        """Cycles to the next audio track."""
        if self.player:
            try:
                self.player.command('cycle', 'audio')
                logger.debug("Cycled audio track.")
            except Exception as e:
                logger.error(f"Failed to cycle audio: {e}")

    def cycle_video_track(self):
        """Cycles to the next video track."""
        if self.player:
            try:
                self.player.command('cycle', 'video')
                logger.debug("Cycled video track.")
            except Exception as e:
                logger.error(f"Failed to cycle video: {e}")

    @Slot()
    def cycle_loop_state(self):
        if not self.player:
            return
        try:
            if self.loop_state == 0:
                self.loop_state = 1
                self.player.loop_file = 'inf'
                self.loop_state_changed.emit('one')
                logger.info("Loop state set to ONE.")
            elif self.loop_state == 1:
                self.loop_state = 2
                self.player.loop_file = 'no'
                self.loop_state_changed.emit('all')
                logger.info("Loop state set to ALL.")
            else:
                self.loop_state = 0
                self.player.loop_file = 'no'
                self.loop_state_changed.emit('none')
                logger.info("Loop state set to NONE.")
        except Exception as e:
            logger.error(f"Failed to cycle loop state: {e}")

    @Slot(str, list, list)
    def load_file(self, filepath, audio_tracks=None, video_tracks=None, show_controls=True):
        if self.player:
            self.save_current_position()
            self.player.stop() 
            logger.info(f"Loading file: {filepath}")
            self.current_filepath = filepath
            
            self.check_for_resume() 
            
            self.player.play(filepath)

            if video_tracks:
                for track in video_tracks:
                    try:
                        logger.debug(f"Adding video track: {track['name']}")
                        self.player.command('video-add', track['url'], 'auto', track['name'])
                    except Exception as e:
                        logger.warning(f"Failed to add video track {track.get('name')}: {e}")

            if audio_tracks:
                for track in audio_tracks:
                    try:
                        logger.debug(f"Adding audio track: {track['name']}")
                        self.player.command('audio-add', track['url'], 'auto', track['name'])
                    except Exception as e:
                        logger.warning(f"Failed to add audio track {track.get('name')}: {e}")
            
            if show_controls:
                self.show_controls()
            
    def check_for_resume(self):
        self.pending_resume_time = 0.0
        
        if self.loop_state == 2:
            logger.debug("Loop All active, skipping resume dialog.")
            return

        if not self.persistence_manager or not self.current_filepath:
            return
            
        last_time = self.persistence_manager.load_playback_position(self.current_filepath)
        
        if last_time > 10:
            logger.info(f"Found saved position: {last_time}s")
            
            reply = QMessageBox.question(
                self, "Resume Playback?",
                f"You last stopped watching at {format_time(last_time)}.\n\nDo you want to resume from this position?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.pending_resume_time = last_time

    def save_current_position(self):
        if (self.persistence_manager and 
            self.player and 
            self.current_filepath and 
            self.player.time_pos is not None):
            current_time = self.player.time_pos
            duration = self.player.duration
            if duration and (duration - current_time) < 5:
                logger.debug("Near end, clearing saved position.")
                self.persistence_manager.save_playback_position(self.current_filepath, 0.0)
            elif current_time > 10:
                self.persistence_manager.save_playback_position(self.current_filepath, current_time)
                
    def shutdown(self):
        if self.player:
            logger.info("Shutting down MPV player.")
            try:
                self.player.stop()
                self.player.command('quit')
            except Exception as e:
                logger.warning(f"Error during MPV shutdown: {e}")
            finally:
                try:
                    self.player.terminate()
                except Exception as e:
                    logger.warning(f"Error terminating MPV: {e}")
        else:
            logger.info("Shutdown called, but no player instance found.")
            
    def resizeEvent(self, event):
        if self.overlay:
            overlay_height = self.overlay.sizeHint().height()
            x = 0; y = self.height() - overlay_height
            w = self.width(); h = overlay_height
            self.overlay.setGeometry(x, y, w, h)
        super().resizeEvent(event)
        
    def mouseMoveEvent(self, event):
        self.show_controls(); super().mouseMoveEvent(event)
        
    def mousePressEvent(self, event):
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
        self.toggle_fullscreen_requested.emit(); super().mouseDoubleClickEvent(event)
        
    def show_controls(self):
        if self.overlay and self.isVisible():
            self.overlay.show()
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.hide_timer.start()
            focused_widget = QApplication.instance().focusWidget()
            if not (focused_widget and self.overlay.isAncestorOf(focused_widget)):
                 self.video_widget.setFocus()
            logger.debug("Controls shown.")
                 
    def hide_controls(self, force=False):
        if self.overlay:
            if not force:
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
            
            # Stop the hide timer when forcing hide
            if force:
                self.hide_timer.stop()
            
            self.overlay.hide()
            self.setCursor(Qt.CursorShape.BlankCursor)
            logger.debug("Controls hidden.")