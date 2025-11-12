# key_manager.py
# (UPDATED to be fully dynamic)

import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, 
    QSizePolicy
)
from PySide6.QtCore import Qt
from key_config import SHORTCUT_GROUPS  # <--- Import the config

logger = logging.getLogger(__name__)

class ShortcutsDialog(QDialog):
    """
    A simple dialog to display a list of keyboard shortcuts
    dynamically built from the key_config.py file.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Keyboard Shortcuts")
        self.setMinimumWidth(350)

        # Build the text dynamically
        shortcut_text = self.build_shortcut_text()

        layout = QVBoxLayout()
        label = QLabel(shortcut_text)
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setWordWrap(True)
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        layout.addWidget(label)
        self.setLayout(layout)

    def build_shortcut_text(self):
        """
        Dynamically builds the HTML for the shortcuts dialog
        by reading from the imported SHORTCUT_GROUPS.
        """
        html = []
        for category, shortcuts in SHORTCUT_GROUPS.items():
            html.append(f"<h2>{category}</h2><p>")
            for shortcut in shortcuts:
                # Use 'display' text for the key
                key_display = shortcut.get("display", "N/A")
                desc = shortcut.get("desc", "No description")
                html.append(f"<b>{key_display}</b> &nbsp;&nbsp;&nbsp; {desc}<br>")
            html.append("</p>")
        
        return "".join(html)