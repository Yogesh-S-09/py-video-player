# themes.py
# (UPDATED with QToolTip and :focus styles)

# A modern, Nlight-inspired dark theme QSS
NORD_DARK = """
QWidget {
    background-color: #2e3440;
    color: #eceff4;
    font-size: 10pt;
    font-family: "Segoe UI", "Arial", "sans-serif";
    border: none;
}
QMainWindow {
    background-color: #2e3440;
}
QMenu {
    background-color: #3b4252;
    color: #eceff4;
    border: 1px solid #4c566a;
}
QMenu::item:selected {
    background-color: #4c566a;
}
QMenuBar {
    background-color: #3b4252;
    color: #eceff4;
}
QMenuBar::item:selected {
    background-color: #4c566a;
}
QPushButton, QToolButton {
    background-color: #434c5e;
    color: #eceff4;
    border: 1px solid #4c566a;
    padding: 5px;
    border-radius: 4px;
    min-height: 20px;
    min-width: 20px;
}
QPushButton:hover, QToolButton:hover {
    background-color: #4c566a;
}
QPushButton:pressed {
    background-color: #5e81ac;
}
QPushButton:focus, QToolButton:focus {
    border: 1px solid #88c0d0;
}
QSlider::groove:horizontal {
    background: #3b4252;
    height: 4px;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #88c0d0;
    border: 1px solid #88c0d0;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::sub-page:horizontal {
    background: #88c0d0;
    height: 4px;
    border-radius: 2px;
}
QSlider::add-page:horizontal {
    background: #3b4252;
    height: 4px;
    border-radius: 2px;
}
QLabel {
    color: #d8dee9;
    background-color: transparent;
}
#ControlOverlay {
    background-color: rgba(46, 52, 64, 0.85);
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}
#ControlOverlay QLabel {
    background-color: transparent;
    color: #d8dee9;
    font-size: 9pt;
}
QToolButton {
    min-width: 30px;
    font-size: 11pt;
}
QToolButton::menu-indicator {
    image: none;
}
QTableWidget {
    border: 1px solid #3b4252;
    gridline-color: #3b4252;
    background-color: #2e3440;
    color: #eceff4;
}
QTableWidget::item {
    padding: 5px;
    border-color: #3b4252;
}
QTableWidget::item:selected {
    background-color: #4c566a;
    color: #eceff4;
}
QHeaderView::section {
    background-color: #3b4252;
    color: #eceff4;
    padding: 4px;
    border: 1px solid #434c5e;
}
QScrollBar:vertical {
    background: #2e3440;
    width: 12px;
}
QScrollBar::handle:vertical {
    background: #434c5e;
    min-height: 20px;
    border-radius: 6px;
}
QScrollBar:horizontal {
    background: #2e3440;
    height: 12px;
}
QScrollBar::handle:horizontal {
    background: #434c5e;
    min-width: 20px;
    border-radius: 6px;
}
QToolTip {
    background-color: #3b4252;
    color: #eceff4;
    border: 1px solid #4c566a;
    padding: 4px;
    border-radius: 3px;
}
"""

# A clean, Material-inspired dark theme
MATERIAL_DARK = """
QWidget {
    background-color: #212121;
    color: #ffffff;
    font-size: 10pt;
    font-family: "Segoe UI", "Arial", "sans-serif";
    border: none;
}
QMainWindow {
    background-color: #212121;
}
QMenu {
    background-color: #424242;
    color: #ffffff;
    border: 1px solid #424242;
}
QMenu::item:selected {
    background-color: #515151;
}
QMenuBar {
    background-color: #313131;
    color: #ffffff;
}
QMenuBar::item:selected {
    background-color: #515151;
}
QPushButton, QToolButton {
    background-color: #424242;
    color: #ffffff;
    border: 1px solid #515151;
    padding: 5px;
    border-radius: 4px;
    min-height: 20px;
    min-width: 20px;
}
QPushButton:hover, QToolButton:hover {
    background-color: #515151;
}
QPushButton:pressed {
    background-color: #00b0ff;
}
QPushButton:focus, QToolButton:focus {
    border: 1px solid #40c4ff;
}
QSlider::groove:horizontal {
    background: #424242;
    height: 4px;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #40c4ff;
    border: 1px solid #40c4ff;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::sub-page:horizontal {
    background: #40c4ff;
    height: 4px;
    border-radius: 2px;
}
QSlider::add-page:horizontal {
    background: #424242;
    height: 4px;
    border-radius: 2px;
}
QLabel {
    color: #ffffff;
    background-color: transparent;
}
#ControlOverlay {
    background-color: rgba(33, 33, 33, 0.85);
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}
#ControlOverlay QLabel {
    background-color: transparent;
    color: #ffffff;
    font-size: 9pt;
}
QToolButton {
    min-width: 30px;
    font-size: 11pt;
}
QToolButton::menu-indicator {
    image: none;
}
QTableWidget {
    border: 1px solid #424242;
    gridline-color: #424242;
    background-color: #212121;
    color: #ffffff;
}
QTableWidget::item {
    padding: 5px;
    border-color: #424242;
}
QTableWidget::item:selected {
    background-color: #515151;
    color: #ffffff;
}
QHeaderView::section {
    background-color: #313131;
    color: #ffffff;
    padding: 4px;
    border: 1px solid #424242;
}
QScrollBar:vertical {
    background: #212121;
    width: 12px;
}
QScrollBar::handle:vertical {
    background: #424242;
    min-height: 20px;
    border-radius: 6px;
}
QScrollBar:horizontal {
    background: #212121;
    height: 12px;
}
QScrollBar::handle:horizontal {
    background: #424242;
    min-width: 20px;
    border-radius: 6px;
}
QToolTip {
    background-color: #424242;
    color: #ffffff;
    border: 1px solid #515151;
    padding: 4px;
    border-radius: 3px;
}
"""

# A clean, professional light theme
WINDOWS_LIGHT = """
QWidget {
    background-color: #f3f3f3;
    color: #000000;
    font-size: 10pt;
    font-family: "Segoe UI", "Arial", "sans-serif";
    border: none;
}
QMainWindow {
    background-color: #f3f3f3;
}
QMenu {
    background-color: #ffffff;
    color: #000000;
    border: 1px solid #cccccc;
}
QMenu::item:selected {
    background-color: #0078d7;
    color: #ffffff;
}
QMenuBar {
    background-color: #f3f3f3;
    color: #000000;
}
QMenuBar::item:selected {
    background-color: #e0e0e0;
}
QPushButton, QToolButton {
    background-color: #ffffff;
    color: #000000;
    border: 1px solid #cccccc;
    padding: 5px;
    border-radius: 4px;
    min-height: 20px;
    min-width: 20px;
}
QPushButton:hover, QToolButton:hover {
    background-color: #e5f1fb;
    border: 1px solid #0078d7;
}
QPushButton:pressed {
    background-color: #cce4f7;
}
QPushButton:focus, QToolButton:focus {
    border: 1px solid #0078d7;
    outline: none;
}
QSlider::groove:horizontal {
    background: #cccccc;
    height: 4px;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #0078d7;
    border: 1px solid #0078d7;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::sub-page:horizontal {
    background: #0078d7;
    height: 4px;
    border-radius: 2px;
}
QSlider::add-page:horizontal {
    background: #cccccc;
    height: 4px;
    border-radius: 2px;
}
QLabel {
    color: #000000;
    background-color: transparent;
}
#ControlOverlay {
    background-color: rgba(243, 243, 243, 0.85);
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}
#ControlOverlay QLabel {
    background-color: transparent;
    color: #000000;
    font-size: 9pt;
}
QToolButton {
    min-width: 30px;
    font-size: 11pt;
}
QToolButton::menu-indicator {
    image: none;
}
QTableWidget {
    border: 1px solid #e0e0e0;
    gridline-color: #e0e0e0;
    background-color: #ffffff;
    color: #000000;
}
QTableWidget::item {
    padding: 5px;
    border-color: #e0e0e0;
}
QTableWidget::item:selected {
    background-color: #0078d7;
    color: #ffffff;
}
QHeaderView::section {
    background-color: #f3f3f3;
    color: #000000;
    padding: 4px;
    border: 1px solid #e0e0e0;
}
QScrollBar:vertical {
    background: #f3f3f3;
    width: 12px;
}
QScrollBar::handle:vertical {
    background: #c0c0c0;
    min-height: 20px;
    border-radius: 6px;
}
QScrollBar:horizontal {
    background: #f3f3f3;
    height: 12px;
}
QScrollBar::handle:horizontal {
    background: #c0c0c0;
    min-width: 20px;
    border-radius: 6px;
}
QToolTip {
    background-color: #ffffff;
    color: #000000;
    border: 1px solid #cccccc;
    padding: 4px;
    border-radius: 3px;
}
"""


# Dictionary to hold all themes
THEMES = {
    "Nord Dark": NORD_DARK,
    "Material Dark": MATERIAL_DARK,
    "Windows Light": WINDOWS_LIGHT
}