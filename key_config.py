# key_config.py
# (UPDATED to be modifier-aware)

from PySide6.QtCore import Qt

"""
This is the single source of truth for all keyboard shortcuts.
- 'key' is the Qt.Key enum used by the keyPressEvent.
- 'mod' is the Qt.KeyboardModifier enum (e.g., ControlModifier, AltModifier, NoModifier).
- 'display' is the text shown in the shortcuts dialog.
- 'desc' is the description of the action.
"""

# Define keys by their function
class K:
    # --- Playback ---
    PLAY_PAUSE = {
        "key": Qt.Key.Key_Space, "mod": Qt.KeyboardModifier.NoModifier, 
        "display": "Space", "desc": "Play / Pause"
    }
    MUTE = {
        "key": Qt.Key.Key_M, "mod": Qt.KeyboardModifier.NoModifier, 
        "display": "M", "desc": "Mute / Unmute"
    }
    SEEK_FWD = {
        "key": Qt.Key.Key_Right, "mod": Qt.KeyboardModifier.NoModifier, 
        "display": "→", "desc": "Seek Forward 10s"
    }
    SEEK_BACK = {
        "key": Qt.Key.Key_Left, "mod": Qt.KeyboardModifier.NoModifier, 
        "display": "←", "desc": "Seek Backward 10s"
    }
    VOL_UP = {
        "key": Qt.Key.Key_Up, "mod": Qt.KeyboardModifier.NoModifier, 
        "display": "↑", "desc": "Volume Up (+5)"
    }
    VOL_DOWN = {
        "key": Qt.Key.Key_Down, "mod": Qt.KeyboardModifier.NoModifier, 
        "display": "↓", "desc": "Volume Down (-5)"
    }

    # --- Tracks & Chapters ---
    NEXT_CHAPTER = {
        "key": Qt.Key.Key_Right, "mod": Qt.KeyboardModifier.AltModifier,
        "display": "Alt + →", "desc": "Next Chapter"
    }
    PREV_CHAPTER = {
        "key": Qt.Key.Key_Left, "mod": Qt.KeyboardModifier.AltModifier,
        "display": "Alt + ←", "desc": "Previous Chapter"
    }
    CYCLE_SUB = {
        "key": Qt.Key.Key_C, "mod": Qt.KeyboardModifier.NoModifier,
        "display": "C", "desc": "Cycle Subtitle Tracks"
    }
    CYCLE_AUDIO = {
        "key": Qt.Key.Key_B, "mod": Qt.KeyboardModifier.NoModifier,
        "display": "B", "desc": "Cycle Audio Tracks"
    }
    CYCLE_VIDEO = {
        "key": Qt.Key.Key_V, "mod": Qt.KeyboardModifier.NoModifier,
        "display": "V", "desc": "Cycle Video Tracks"
    }

    # --- Playlist ---
    NEXT_PLAYLIST = {
        "key": Qt.Key.Key_Right, "mod": Qt.KeyboardModifier.ControlModifier,
        "display": "Ctrl + →", "desc": "Next in Playlist"
    }
    PREV_PLAYLIST = {
        "key": Qt.Key.Key_Left, "mod": Qt.KeyboardModifier.ControlModifier,
        "display": "Ctrl + ←", "desc": "Previous in Playlist"
    }
    
    # --- Window ---
    FULLSCREEN = {
        "key": Qt.Key.Key_F, "mod": Qt.KeyboardModifier.NoModifier, 
        "display": "F", "desc": "Toggle Fullscreen"
    }
    ESC_FULLSCREEN = {
        "key": Qt.Key.Key_Escape, "mod": Qt.KeyboardModifier.NoModifier, 
        "display": "Esc", "desc": "Exit Fullscreen (from player)"
    }

    # --- Menu Items (No direct key event) ---
    ADD_FILES = {
        "key": None, "mod": None, 
        "display": "Ctrl+O", "desc": "Add File(s) to Library"
    }
    NET_STREAM = {
        "key": None, "mod": None, 
        "display": "Ctrl+N", "desc": "Open Network Stream"
    }
    SHOW_LIBRARY = {
        "key": None, "mod": None, 
        "display": "Ctrl+P", "desc": "Show Library View"
    }


# --- Group the keys for the Shortcuts Dialog ---
SHORTCUT_GROUPS = {
    "Playback Controls": [
        K.PLAY_PAUSE, 
        K.MUTE,
        K.SEEK_FWD, 
        K.SEEK_BACK, 
        K.VOL_UP, 
        K.VOL_DOWN
    ],
    "Tracks & Chapters": [
        K.NEXT_CHAPTER,
        K.PREV_CHAPTER,
        K.CYCLE_SUB,
        K.CYCLE_AUDIO,
        K.CYCLE_VIDEO
    ],
    "Playlist Controls": [
        K.NEXT_PLAYLIST,
        K.PREV_PLAYLIST
    ],
    "Window Controls": [
        K.FULLSCREEN, 
        K.ESC_FULLSCREEN, 
        K.SHOW_LIBRARY
    ],
    "File Menu": [
        K.ADD_FILES, 
        K.NET_STREAM
    ]
}