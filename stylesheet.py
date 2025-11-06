# stylesheet.py
# (UPDATED to fix button sizes)

# A modern, Nlight-inspired dark theme QSS
STYLESHEET = """
QWidget {
    background-color: #2e3440;
    color: #eceff4;
    font-size: 10pt;
    font-family: "Segoe UI", "Arial", "sans-serif";
}

QMainWindow {
    background-color: #2e3440;
}

/* --- Menu Bar --- */
QMenuBar {
    background-color: #3b4252;
    color: #eceff4;
}
QMenuBar::item:selected {
    background-color: #4c566a;
}
QMenu {
    background-color: #3b4252;
    color: #eceff4;
    border: 1px solid #4c566a;
}
QMenu::item:selected {
    background-color: #4c566a;
}

/* --- Buttons (UPDATED) --- */
QPushButton, QToolButton {
    background-color: #434c5e;
    color: #eceff4;
    border: 1px solid #4c566a;
    padding: 5px;
    border-radius: 4px;
    min-height: 20px; /* Set a minimum height */
    min-width: 20px; /* Set a minimum width */
}
QPushButton:hover, QToolButton:hover {
    background-color: #4c566a;
}
QPushButton:pressed {
    background-color: #5e81ac;
}

/* --- Slider (Seek Bar) --- */
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

/* --- Labels --- */
QLabel {
    color: #d8dee9;
    background-color: transparent;
}

/* --- Overlay Special --- */
#ControlOverlay {
    /* Semi-transparent background for the overlay */
    background-color: rgba(46, 52, 64, 0.85);
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}
#ControlOverlay QLabel {
    background-color: transparent;
    font-size: 9pt;
}

/* --- Menu Buttons (UPDATED) --- */
QToolButton {
    min-width: 30px; /* Specific min-width for the tool buttons */
    font-size: 11pt; /* Make the emoji text a bit bigger */
}
QToolButton::menu-indicator {
    image: none; /* Hide default dropdown arrow */
}
"""