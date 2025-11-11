# library_widget.py
# (UPDATED to store and pass stream_data)

import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QFileDialog,    
    QAbstractItemView, QSizePolicy, QMessageBox, QLabel,
    QHeaderView, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal, Slot, QSize, QTimer
from PySide6.QtGui import QFont, QIcon
from persistence_manager import PersistenceManager
from pathlib import Path
from thumbnail_worker import ThumbnailWorker

logger = logging.getLogger(__name__)

class LibraryWidget(QWidget):
    
    # --- UPDATED SIGNAL ---
    play_file_requested = Signal(str, list, list) # path, audio_tracks, video_tracks
    count_changed = Signal(int)
    
    def __init__(self, persistence_manager: PersistenceManager, parent=None):
        super().__init__(parent)
        self.persistence_manager = persistence_manager
        self.file_dialog = QFileDialog(self)
        self.file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        self.file_dialog.setNameFilter("Video Files (*.mp4 *.mkv *.avi *.mov);;All Files (*.*)")
        self.worker_threads = []
        self.stream_data_cache = {}
        self.thumbnail_delay_timer = QTimer(self)  # Delay timer
        self.thumbnail_delay_timer.setSingleShot(True)
        self.thumbnail_delay_timer.timeout.connect(self.process_pending_thumbnails)
        self.pending_thumbnail_requests = []  # Queue for thumbnail requests
        
        self.init_ui()
        self.create_connections()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        title = QLabel("Media Library")
        title_font = QFont()
        title_font.setPointSize(18); title_font.setBold(True)
        title.setFont(title_font); title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_layout = QHBoxLayout()
        self.add_files_btn = QPushButton("Add Files")
        self.remove_btn = QPushButton("Remove Selected")
        self.clear_btn = QPushButton("Clear All")
        button_layout.addWidget(self.add_files_btn); button_layout.addWidget(self.remove_btn)
        button_layout.addWidget(self.clear_btn); button_layout.addStretch()
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["", "Title", "Duration", "Resolution"])
        self.table_widget.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.table_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_widget.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.table_widget.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table_widget.setColumnWidth(0, 160)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.verticalHeader().setDefaultSectionSize(90)
        self.table_widget.setIconSize(QSize(160, 90))
        layout.addWidget(title)
        layout.addLayout(button_layout)
        layout.addWidget(self.table_widget)
        self.setLayout(layout)

    def create_connections(self):
        # ... (this method is unchanged) ...
        self.add_files_btn.clicked.connect(self.open_add_files_dialog)
        self.remove_btn.clicked.connect(self.remove_selected_items)
        self.clear_btn.clicked.connect(self.clear_all_items)
        self.table_widget.itemDoubleClicked.connect(self.play_item)

    @Slot()
    def open_add_files_dialog(self):
        # ... (this method is unchanged) ...
        last_path = self.persistence_manager.load_last_open_path()
        self.file_dialog.setDirectory(last_path)
        if self.file_dialog.exec():
            filepaths = self.file_dialog.selectedFiles()
            if filepaths:
                self.persistence_manager.save_last_open_path(filepaths[0])
                for filepath in filepaths:
                    self.add_file(filepath)

    def add_file(self, filepath, display_name=None, stream_data=None):
        """
        Adds a file or stream to the list.
        'filepath' is the unique ID (local path or original URL).
        'display_name' is what the user sees.
        'stream_data' is the dict from stream_extractor.
        """
        path = Path(filepath)
        
        if display_name is None:
            display_name = path.name if path.exists() else filepath
        
        if stream_data:
            self.stream_data_cache[filepath] = stream_data
        
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)
        
        thumb_item = QTableWidgetItem()
        thumb_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        thumb_item.setFlags(thumb_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        
        title_item = QTableWidgetItem(display_name)
        title_item.setData(Qt.ItemDataRole.UserRole, filepath) # Store the *original* path/URL
        title_item.setToolTip(filepath)
        
        duration_item = QTableWidgetItem("...")
        duration_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        resolution_item = QTableWidgetItem("...")
        resolution_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        self.table_widget.setItem(row_position, 0, thumb_item)
        self.table_widget.setItem(row_position, 1, title_item)
        self.table_widget.setItem(row_position, 2, duration_item)
        self.table_widget.setItem(row_position, 3, resolution_item)
        
        self.pending_thumbnail_requests.append((filepath, row_position))
        
        logger.info(f"Added to playlist: {filepath}")
        self.count_changed.emit(self.table_widget.rowCount())

        self.thumbnail_delay_timer.start(100)  # .1 second delay

    def process_pending_thumbnails(self):
        """Process queued thumbnail requests after startup delay."""
        for filepath, row in self.pending_thumbnail_requests:
            self.start_thumbnail_worker(filepath, row)
        self.pending_thumbnail_requests.clear()
    
    
    def start_thumbnail_worker(self, filepath, row):
        worker = ThumbnailWorker(filepath, row)
        worker.thumbnail_ready.connect(self.on_thumbnail_ready)
        worker.thumbnail_failed.connect(self.on_thumbnail_failed)
        worker.finished.connect(lambda: self.cleanup_worker(worker))
        worker.start()
        self.worker_threads.append(worker)

    @Slot(int, QIcon, str, str)
    def on_thumbnail_ready(self, row, icon, duration_str, resolution_str):
        try:
            self.table_widget.item(row, 0).setIcon(icon)
            self.table_widget.item(row, 2).setText(duration_str)
            self.table_widget.item(row, 3).setText(resolution_str)
        except Exception as e:
            logger.warning(f"Failed to set table data for row {row}: {e}")
    @Slot(int, str)
    def on_thumbnail_failed(self, row, error_message):
        try:
            self.table_widget.item(row, 2).setText("Error")
            self.table_widget.item(row, 3).setText("Error")
            logger.error(f"Worker for row {row} failed: {error_message}")
        except Exception as e:
            logger.warning(f"Failed to set table error data for row {row}: {e}")

    def cleanup_worker(self, worker):
        """Remove finished worker from list to prevent memory leak."""
        try:
            if worker in self.worker_threads:
                self.worker_threads.remove(worker)
                worker.deleteLater()
        except Exception as e:
            logger.warning(f"Failed to cleanup worker: {e}")
    
    def cleanup_all_workers(self):
        """Stop and cleanup all worker threads."""
        for worker in self.worker_threads:
            try:
                if worker.isRunning():
                    worker.terminate()
                    worker.wait(1000)  # Wait up to 1 second
                worker.deleteLater()
            except Exception as e:
                logger.warning(f"Failed to cleanup worker: {e}")
        self.worker_threads.clear()

    @Slot()
    def remove_selected_items(self):
        selected_rows = sorted(
            list(set(index.row() for index in self.table_widget.selectedIndexes())),
            reverse=True
        )
        if not selected_rows: return
        
        for row in selected_rows:
            try:
                item = self.table_widget.item(row, 1)
                filepath = item.data(Qt.ItemDataRole.UserRole)
                if filepath in self.stream_data_cache:
                    del self.stream_data_cache[filepath]
            except Exception as e:
                logger.warning(f"Could not remove from cache: {e}")
            self.table_widget.removeRow(row)
            
        self.count_changed.emit(self.table_widget.rowCount())

    @Slot()
    def clear_all_items(self):
        self.table_widget.setRowCount(0)
        self.stream_data_cache.clear()
        self.count_changed.emit(0)
        self.cleanup_all_workers()

    # --- UPDATED play_item ---
    @Slot(QTableWidgetItem)
    def play_item(self, item):
        """Emits the signal to play the selected item's row."""
        row = item.row()
        title_item = self.table_widget.item(row, 1)
        filepath = title_item.data(Qt.ItemDataRole.UserRole) # This is the original URL/path
        
        if not filepath:
            return

        logger.info(f"Requesting playback for: {filepath}")
        self.table_widget.setCurrentItem(title_item)
        
        if filepath in self.stream_data_cache:
            stream_data = self.stream_data_cache[filepath]
            video_streams = stream_data.get('video_streams', [])
            audio_streams = stream_data.get('audio_streams', [])
            
            if not video_streams:
                logger.error("No video streams found for this item.")
                return
                
            main_video_url = video_streams[0]['url']
            other_video_tracks = video_streams[1:]
            
            self.play_file_requested.emit(main_video_url, audio_streams, other_video_tracks)
        else:
            self.play_file_requested.emit(filepath, [], []) # Local file
    # -----------------------------------------------

    def has_next_video(self, loop_all=False):
        """Check if there's a next video to play."""
        current_row = self.table_widget.currentRow()
        next_row = current_row + 1
        row_count = self.table_widget.rowCount()
        
        if next_row >= row_count:
            # At end of playlist
            return loop_all and row_count > 0
        return True
    
    @Slot(bool)
    def play_next(self, loop_all=False):
        """Play the next video in the playlist."""
        current_row = self.table_widget.currentRow()
        next_row = current_row + 1
        row_count = self.table_widget.rowCount()
        
        # Calculate next row (with looping if needed)
        if next_row >= row_count:
            if loop_all and row_count > 0:
                logger.info("Looping playlist back to first video.")
                next_row = 0
            else:
                logger.warning("play_next called but no next video available.")
                return
        
        # Play the next item
        next_item = self.table_widget.item(next_row, 1)
        if next_item:
            self.table_widget.setCurrentItem(next_item)
            self.play_item(next_item)
        else:
            logger.error(f"No item found at row {next_row}")
            
    @Slot()
    def play_previous(self):
        # ... (this method is unchanged) ...
        current_row = self.table_widget.currentRow()
        prev_row = current_row - 1
        if prev_row < 0:
            prev_row = self.table_widget.rowCount() - 1
            if prev_row < 0:
                return
        prev_item = self.table_widget.item(prev_row, 1)
        if prev_item:
            self.table_widget.setCurrentItem(prev_item)
            self.play_item(prev_item)