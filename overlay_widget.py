# overlay_widget.py
# (UPDATED with new buttons and visibility logic)

import logging
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QSlider, QLabel, QToolButton, QMenu, QStyle,
    QToolTip
)
from PySide6.QtCore import Qt, Signal, QEvent, Slot
from PySide6.QtGui import QAction, QCursor
from utils import format_time
from pathlib import Path

logger = logging.getLogger(__name__)

class OverlayWidget(QWidget):
    # ... (signals unchanged) ...
    seek = Signal(int)
    fullscreen_toggled = Signal()
    back_requested = Signal()

    def __init__(self, player, parent=None):
        # ... (init unchanged) ...
        super().__init__(parent)
        self.player = player
        self.is_seeking = False
        self.video_duration = 0.0
        self.chapter_list = []
        self.setObjectName("ControlOverlay")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.audio_menu = QMenu(self)
        self.sub_menu = QMenu(self)
        self.video_menu = QMenu(self)
        self.chapter_menu = QMenu(self)
        self.create_widgets()
        self.create_layouts()
        self.create_connections()


    def create_widgets(self):
        self.back_btn = QPushButton("Library")
        self.back_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowLeft))
        
        self.time_label = QLabel("00:00 / 00:00")
        self.seek_slider = QSlider(Qt.Orientation.Horizontal)
        self.seek_slider.setTracking(True)
        self.seek_slider.setMouseTracking(True)
        
        self.play_pause_btn = QPushButton()
        self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

        # --- PLAYLIST & CHAPTER BUTTONS ---
        self.prev_file_btn = QPushButton()
        self.prev_file_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSkipBackward))
        self.prev_file_btn.setToolTip("Previous in Playlist")
        self.prev_file_btn.setVisible(False) # Hide by default
        
        self.prev_chapter_btn = QPushButton()
        self.prev_chapter_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekBackward))
        self.prev_chapter_btn.setToolTip("Previous Chapter")
        self.prev_chapter_btn.setVisible(False) # Hide by default
        
        self.seek_backward_btn = QPushButton("-10s")
        self.seek_backward_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekBackward))
        
        self.seek_forward_btn = QPushButton("+10s")
        self.seek_forward_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekForward))

        self.next_chapter_btn = QPushButton()
        self.next_chapter_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekForward))
        self.next_chapter_btn.setToolTip("Next Chapter")
        self.next_chapter_btn.setVisible(False) # Hide by default
        
        self.next_file_btn = QPushButton()
        self.next_file_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSkipForward))
        self.next_file_btn.setToolTip("Next in Playlist")
        self.next_file_btn.setVisible(False) # Hide by default
        # ----------------------------------
        
        self.stop_btn = QPushButton()
        self.stop_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        
        # --- LOOP BUTTON ---
        self.loop_btn = QPushButton("Loop: Off")
        self.loop_btn.setFixedWidth(80) # Give it space
        # -------------------
        
        self.mute_btn = QPushButton()
        self.mute_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100); self.volume_slider.setValue(100)
        self.volume_slider.setFixedWidth(100); self.volume_slider.setMouseTracking(True)
        self.volume_label = QLabel("100%"); self.volume_label.setFixedWidth(40)
        
        self.audio_btn = QToolButton(); self.audio_btn.setText("🔊")
        self.audio_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.sub_btn = QToolButton(); self.sub_btn.setText("💬")
        self.sub_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.video_btn = QToolButton(); self.video_btn.setText("🎬")
        self.video_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        
        self.chapter_btn = QToolButton(); self.chapter_btn.setText("📜")
        self.chapter_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.chapter_btn.setVisible(False) # Hide by default
        
        self.fullscreen_btn = QPushButton()
        self.fullscreen_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp))

    def create_layouts(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.time_label)
        top_layout.addWidget(self.seek_slider)
        
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.back_btn)
        bottom_layout.addWidget(self.play_pause_btn)
        bottom_layout.addWidget(self.prev_file_btn)    # New
        bottom_layout.addWidget(self.prev_chapter_btn)
        bottom_layout.addWidget(self.seek_backward_btn)
        bottom_layout.addWidget(self.seek_forward_btn)
        bottom_layout.addWidget(self.next_chapter_btn)
        bottom_layout.addWidget(self.next_file_btn)    # New
        bottom_layout.addWidget(self.stop_btn)
        bottom_layout.addWidget(self.loop_btn)         # New
        bottom_layout.addWidget(self.mute_btn)
        bottom_layout.addWidget(self.volume_slider)
        bottom_layout.addWidget(self.volume_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.audio_btn)
        bottom_layout.addWidget(self.sub_btn)
        bottom_layout.addWidget(self.video_btn)
        bottom_layout.addWidget(self.chapter_btn)
        bottom_layout.addWidget(self.fullscreen_btn)
        
        layout.addLayout(top_layout)
        layout.addLayout(bottom_layout)
        self.setLayout(layout)

    def create_connections(self):
        player_widget = self.parent()
        
        self.back_btn.clicked.connect(self.back_requested.emit)
        self.play_pause_btn.clicked.connect(self.toggle_pause)
        self.stop_btn.clicked.connect(self.stop_video)
        self.fullscreen_btn.clicked.connect(self.fullscreen_toggled.emit)
        self.mute_btn.clicked.connect(self.toggle_mute)
        
        self.seek_slider.sliderMoved.connect(self.show_seek_tooltip_at_value)
        self.seek_slider.sliderPressed.connect(self.on_seek_press)
        self.seek_slider.sliderReleased.connect(self.on_seek_release)
        self.seek_slider.installEventFilter(self)
        
        self.volume_slider.sliderMoved.connect(self.show_volume_tooltip)
        self.volume_slider.valueChanged.connect(self.on_volume_change)
        self.volume_slider.installEventFilter(self)

        self.chapter_btn.setMenu(self.chapter_menu)

        if player_widget:
            self.prev_chapter_btn.clicked.connect(player_widget.prev_chapter)
            self.next_chapter_btn.clicked.connect(player_widget.next_chapter)
            self.seek_backward_btn.clicked.connect(player_widget.seek_backward)
            self.seek_forward_btn.clicked.connect(player_widget.seek_forward)
            # --- NEW CONNECTIONS ---
            self.loop_btn.clicked.connect(player_widget.cycle_loop_state)
            # We will connect prev/next file in main_window.py
            # -----------------------

        if player_widget and hasattr(player_widget, 'hide_timer'):
            # ... (menu connections unchanged) ...
            self.audio_menu.aboutToShow.connect(player_widget.hide_timer.stop)
            self.sub_menu.aboutToShow.connect(player_widget.hide_timer.stop)
            self.video_menu.aboutToShow.connect(player_widget.hide_timer.stop)
            self.chapter_menu.aboutToShow.connect(player_widget.hide_timer.stop)
            self.audio_menu.aboutToHide.connect(player_widget.hide_timer.start)
            self.sub_menu.aboutToHide.connect(player_widget.hide_timer.start)
            self.video_menu.aboutToHide.connect(player_widget.hide_timer.start)
            self.chapter_menu.aboutToHide.connect(player_widget.hide_timer.start)

    # --- NEW SLOTS ---
    @Slot(str)
    def update_loop_button(self, state):
        if state == 'one':
            self.loop_btn.setText("Loop: One")
        elif state == 'all':
            self.loop_btn.setText("Loop: All")
        else:
            self.loop_btn.setText("Loop: Off")

    @Slot(bool)
    def set_playlist_controls_visible(self, visible):
        self.prev_file_btn.setVisible(visible)
        self.next_file_btn.setVisible(visible)
    # -----------------

    # ... (eventFilter, find_chapter_for_time, tooltips, and playback methods are unchanged) ...
    def eventFilter(self, watched, event):
        if watched == self.seek_slider:
            if event.type() == QEvent.Type.MouseMove:
                if not self.is_seeking:
                    x = event.pos().x(); width = self.seek_slider.width()
                    if width > 0:
                        value = (self.seek_slider.maximum() * x) / width
                        self.show_seek_tooltip_at_value(value)
            elif event.type() == QEvent.Type.Leave: QToolTip.hideText()
        elif watched == self.volume_slider:
            if event.type() == QEvent.Type.MouseMove:
                if not (event.buttons() & Qt.MouseButton.LeftButton):
                    x = event.pos().x(); width = self.volume_slider.width()
                    if width > 0:
                        value = (self.volume_slider.maximum() * x) / width
                        self.show_volume_tooltip(int(value))
            elif event.type() == QEvent.Type.Leave: QToolTip.hideText()
        return super().eventFilter(watched, event)
    def find_chapter_for_time(self, time_sec):
        if not self.chapter_list: return None
        for chapter in reversed(self.chapter_list):
            if time_sec >= chapter.get('time', 0):
                return chapter.get('title', 'Chapter')
        return None
    def show_seek_tooltip_at_value(self, value):
        time_str = format_time(value); chapter_title = self.find_chapter_for_time(value)
        tooltip_str = time_str
        if chapter_title: tooltip_str = f"{time_str}\n{chapter_title}"
        QToolTip.showText(QCursor.pos(), tooltip_str, self.seek_slider)
    def show_volume_tooltip(self, value):
        vol_str = f"{value}%"; QToolTip.showText(QCursor.pos(), vol_str, self.volume_slider)
    def toggle_pause(self):
        if self.player: self.player.pause = not self.player.pause
    def stop_video(self):
        if self.player: self.player.stop()
    def toggle_mute(self):
        if self.player: self.player.mute = not self.player.mute
    def on_volume_change(self, value):
        if self.player: self.player.volume = value
    def update_volume_slider(self, value):
        if value is None: value = 100
        self.volume_slider.setValue(value); self.volume_label.setText(f"{value}%")
    def update_mute_button(self, is_muted):
        if is_muted:
            self.mute_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolumeMuted))
            self.volume_label.setText("Mute")
        else:
            self.mute_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))
            if self.player: self.volume_label.setText(f"{int(self.player.volume)}%")
    def update_pause_button(self, is_paused):
        if is_paused:
            self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        else:
            self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
    def update_time(self, current_time):
        if current_time is None: current_time = 0.0
        if not self.is_seeking: self.seek_slider.setValue(int(current_time))
        self.time_label.setText(f"{format_time(current_time)} / {format_time(self.video_duration)}")
    def update_duration(self, duration):
        if duration is None: duration = 0.0
        self.video_duration = duration
        self.seek_slider.setMaximum(int(duration))
    def on_seek_press(self): self.is_seeking = True
    def on_seek_release(self,):
        self.is_seeking = False; seek_time = self.seek_slider.value()
        if self.player: self.player.time_pos = seek_time
    def set_track(self, property, value):
        if self.player: setattr(self.player, property, value)
    def set_track_and_update_menu(self, property, value, menu):
        self.set_track(property, value)
        for action in menu.actions():
            if not action.isCheckable(): continue
            action.setChecked(action.data() == value)
    def _format_bitrate(self, bitrate):
        if bitrate is None or bitrate <= 0: return None
        if bitrate > 1_000_000: return f"{bitrate / 1_000_000:.1f} Mbps"
        return f"{bitrate / 1_000:.0f} kbps"
    def update_track_menus(self, tracks, current_aid, current_sid, current_vid):
        # ... (this method is unchanged) ...
        if tracks is None: tracks = []
        self.audio_menu.clear(); self.sub_menu.clear(); self.video_menu.clear()
        audio_none = QAction("None", self); audio_none.setCheckable(True); audio_none.setData("no")
        audio_none.setChecked(current_aid == 'no'); audio_none.triggered.connect(lambda: self.set_track_and_update_menu('aid', 'no', self.audio_menu))
        self.audio_menu.addAction(audio_none); self.audio_menu.addSeparator()
        sub_none = QAction("None", self); sub_none.setCheckable(True); sub_none.setData("no")
        sub_none.setChecked(current_sid == 'no'); sub_none.triggered.connect(lambda: self.set_track_and_update_menu('sid', 'no', self.sub_menu))
        self.sub_menu.addAction(sub_none); self.sub_menu.addSeparator()
        video_none = QAction("None", self); video_none.setCheckable(True); video_none.setData("no")
        video_none.setChecked(current_vid == 'no'); video_none.triggered.connect(lambda: self.set_track_and_update_menu('vid', 'no', self.video_menu))
        self.video_menu.addAction(video_none); self.video_menu.addSeparator()
        for track in tracks:
            track_id = str(track['id']); title = track.get('title'); lang = track.get('lang'); codec = track.get('codec'); bitrate_str = self._format_bitrate(track.get('demux-bitrate'))
            label_parts = []; details = []
            if title: label_parts.append(title)
            else:
                if track['type'] == 'video': label_parts.append(f"Video #{track_id}")
                elif track['type'] == 'audio': label_parts.append(f"Audio #{track_id}")
                elif track['type'] == 'sub': label_parts.append(f"Subtitle #{track_id}")
            if lang: label_parts.append(f"[{lang.upper()}]")
            if codec: details.append(codec)
            if bitrate_str and track['type'] != 'sub': details.append(bitrate_str)
            if details: label_parts.append(f"({' / '.join(details)})")
            if track['type'] == 'video':
                res = f"[{track.get('demux-w', '?')}x{track.get('demux-h', '?')}]"
                label_parts.insert(0, res)
            label = " ".join(label_parts); action = QAction(label, self); action.setCheckable(True); action.setData(track_id)
            if track['type'] == 'audio':
                action.setChecked(track_id == current_aid); action.triggered.connect(lambda _, i=track_id: self.set_track_and_update_menu('aid', i, self.audio_menu))
                self.audio_menu.addAction(action)
            elif track['type'] == 'sub':
                action.setChecked(track_id == current_sid); action.triggered.connect(lambda _, i=track_id: self.set_track_and_update_menu('sid', i, self.sub_menu))
                self.sub_menu.addAction(action)
            elif track['type'] == 'video':
                action.setChecked(track_id == current_vid); action.triggered.connect(lambda _, i=track_id: self.set_track_and_update_menu('vid', i, self.video_menu))
                self.video_menu.addAction(action)
        self.audio_btn.setMenu(self.audio_menu); self.sub_btn.setMenu(self.sub_menu); self.video_btn.setMenu(self.video_menu)
    def update_track_selection(self, name, value):
        # ... (this method is unchanged) ...
        menu = None
        if name == 'aid': menu = self.audio_menu
        elif name == 'sid': menu = self.sub_menu
        elif name == 'vid': menu = self.video_menu
        else: return
        if not menu: return
        for action in menu.actions():
            if not action.isCheckable(): continue
            action.setChecked(action.data() == value)
    def set_chapter_and_update_menu(self, index):
        # ... (this method is unchanged) ...
        if self.player: self.player.chapter = index
        for action in self.chapter_menu.actions():
            if not action.isCheckable(): continue
            action.setChecked(action.data() == index)

    # --- UPDATED: Use setVisible instead of setEnabled ---
    def update_chapter_menu(self, chapters):
        self.chapter_list = chapters or []
        self.chapter_menu.clear()
        
        has_chapters = bool(self.chapter_list)
        
        self.chapter_btn.setVisible(has_chapters)
        self.prev_chapter_btn.setVisible(has_chapters)
        self.next_chapter_btn.setVisible(has_chapters)
        
        if not has_chapters:
            return
            
        for i, chap in enumerate(self.chapter_list):
            title = chap.get('title', f"Chapter {i+1}"); start_time = chap.get('time', 0)
            end_time = self.chapter_list[i+1].get('time') if i + 1 < len(self.chapter_list) else self.video_duration
            label = f"{title} ({format_time(start_time)} - {format_time(end_time)})"
            action = QAction(label, self); action.setData(i); action.setCheckable(True)
            action.triggered.connect(lambda _, idx=i: self.set_chapter_and_update_menu(idx))
            self.chapter_menu.addAction(action)

    def update_chapter_selection(self, chapter_index):
        # ... (this method is unchanged) ...
        for action in self.chapter_menu.actions():
            if not action.isCheckable(): continue
            action.setChecked(action.data() == chapter_index)