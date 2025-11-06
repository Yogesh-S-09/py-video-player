# PySide MPV Player

A feature-rich, modern media player built with Python, PySide6, and the powerful `mpv` playback engine.

This project is a high-performance video player that combines the speed and compatibility of `mpv` with a sleek, responsive, and dark-themed graphical interface built in PySide6 (Qt). It integrates `yt-dlp` for seamless network streaming and provides a full suite of professional features, including chapter support, advanced track selection, and keyboard shortcuts.

![Main Player Screenshot](https://i.imgur.com/YOUR_SCREENSHOT_URL.png)

---

## ✨ Features

* **Modern Qt Interface**: A professional, Nlight-inspired dark theme built with PySide6.
* **Auto-Hiding Overlay**: All controls are on a semi-transparent overlay that disappears after 3 seconds of inactivity and reappears instantly on mouse movement, click, or focus.
* **Powerful MPV Backend**: Uses `python-mpv` to leverage the `mpv` player for high-performance playback of virtually any media codec.
* **Network Streaming**: "Open Network Stream" (Ctrl+N) uses `yt-dlp` to play from any supported URL, including YouTube, Vimeo, etc.
* **Comprehensive Playback Controls**:
    * Play / Pause (with icon toggle)
    * Stop
    * Volume Slider (0-100%)
    * Mute Button (with icon toggle)
    * Live Volume Percentage Display
* **Advanced Seeking**:
    * Seek Bar with hover-to-preview
    * Seek Forward (+10s) button
    * Seek Backward (-10s) button
    * Previous/Next Chapter buttons
* **Full Chapter Support**:
    * A dedicated "Chapter List" (📜) menu.
    * Menu displays all chapters with their **Start - End** timestamps.
    * Click any chapter in the menu to seek directly to it.
* **Intelligent Seek Tooltip**: Hovering over the seek bar shows a live tooltip with the exact time and the **title of the chapter** at that position.
* **Advanced Track Selection**:
    * Dedicated menus for Video (🎬), Audio (🔊), and Subtitles (💬).
    * Displays all available tracks with rich metadata:
        * **Video**: Resolution, Title, Language, Codec, Bitrate
        * **Audio**: Title, Language, Codec, Bitrate
        * **Subtitle**: Title, Language, Codec
    * Includes a "None" option for all track types.
* **Fullscreen Mode**:
    * Toggle with a dedicated button.
    * Toggle by **double-clicking** the video.
    * Toggle with the **'F' key**.
    * Menu bar is automatically hidden in fullscreen.
* **Full Keyboard Shortcuts**:
    * **Space**: Play/Pause
    * **F**: Toggle Fullscreen
    * **Esc**: Exit Fullscreen
    * **Right Arrow**: Seek +10s
    * **Left Arrow**: Seek -10s
    * **Up Arrow**: Volume +5%
    * **Down Arrow**: Volume -5%
* **Application Polish**:
    * **"Open With..." Support**: Can be set as the default player in Windows.
    * **Persistent Settings**: Remembers the last folder you used to open a file.
    * **Custom Icon**: Features a custom application icon for the `.exe`, window, and taskbar.
    * **Robust Logging**: All `mpv` and application events are logged to a `player.log` file in the application directory for easy debugging.

---

## 📸 Screenshots

| Player with Overlay | Track Selection Menus |
| :---: | :---: |
| ![Overlay Screenshot](https://i.imgur.com/YOUR_OVERLAY_SCREENSHOT.png) | ![Track Menu Screenshot](https://i.imgur.com/YOUR_TRACK_MENU_SCREENSHOT.png) |
| **Chapter List Menu** | **Seek Bar Tooltip** |
| ![Chapter Menu Screenshot](https://i.imgur.com/YOUR_CHAPTER_MENU_SCREENSHOT.png) | ![Seek Tooltip Screenshot](https://i.imgur.com/YOUR_SEEK_TOOLTIP_SCREENSHOT.png) |

---

## 🚀 Getting Started

You can either run the player from the Python source or build the standalone executable.

### Prerequisites

You must have the following dependencies available.

1.  **Python 3.8+**
2.  **MPV Binary**: The core `libmpv-2.dll` (or `mpv-1.dll`) library.
    * **Windows**: Download the `dev` package from [mpv.io/installation/](https://mpv.io/installation/). Find the `.dll` file and place it in the `Assets/` folder.
    * **macOS**: `brew install mpv`
    * **Linux**: `sudo apt-get install libmpv-dev`
3.  **yt-dlp Binary**: Required for the "Open Network Stream" feature.
    * Download `yt-dlp.exe` (Windows) or `yt-dlp` (macOS/Linux) from [their GitHub releases page](https://github.com/yt-dlp/yt-dlp/releases/latest).
    * Place the executable in the `Assets/` folder.

### Running from Source

1.  Clone this repository:
    ```bash
    git clone [https://github.com/YOUR-USERNAME/YOUR-PROJECT-NAME.git](https://github.com/YOUR-USERNAME/YOUR-PROJECT-NAME.git)
    cd YOUR-PROJECT-NAME
    ```

2.  Create a `requirements.txt` file in the root of the project:
    ```
    PySide6
    python-mpv
    ```

3.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

4.  Ensure your `Assets` folder contains `libmpv-2.dll` and `yt-dlp.exe`.

5.  Run the application:
    ```bash
    python main.py
    ```

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
| :--- | :--- |
| **Spacebar** | Play / Pause |
| **F** | Toggle Fullscreen |
| **Esc** | Exit Fullscreen |
| **Right Arrow** | Seek Forward +10s |
| **Left Arrow** | Seek Backward -10s |
| **Up Arrow** | Volume +5 |
| **Down Arrow** | Volume -5 |
| **Ctrl + O** | Open File |
| **Ctrl + N** | Open Network Stream |
| **F1** | Open Help (mpv manual) |

---

## 📦 Building a Single `.exe` File

This project is configured to be built into a single, standalone executable using `PyInstaller`.

1.  Install PyInstaller:
    ```bash
    pip install pyinstaller
    ```

2.  Organize your project folder as follows:
    ```
    YOUR-PROJECT-FOLDER/
    ├── Assets/
    │   ├── icon.ico         (For the .exe file)
    │   ├── icon.png         (For the window title bar)
    │   ├── libmpv-2.dll     (The mpv binary)
    │   └── yt-dlp.exe       (The yt-dlp binary)
    ├── main.py
    ├── main_window.py
    ├── player_widget.py
    ├── overlay_widget.py
    ├── stylesheet.py
    └── utils.py
    ```

3.  Run the following `PyInstaller` command from your project's root folder:

    ```bash
    pyinstaller --onefile --windowed --name="MyMediaPlayer" --icon="Assets/icon.ico" --add-data="Assets/icon.png;." --add-data="Assets/libmpv-2.dll;." --add-data="Assets/yt-dlp.exe;." main.py
    ```

    * `--onefile`: Bundles everything into a single `.exe`.
    * `--windowed`: Hides the black console window on launch.
    * `--name="MyMediaPlayer"`: Sets the name of your final executable.
    * `--icon="Assets/icon.ico"`: Sets the file icon for the `.exe`.
    * `--add-data="...;."`: Bundles the required non-Python files (`.png`, `.dll`, `.exe`) into your application.

4.  Your standalone `MyMediaPlayer.exe` will be in the `dist/` folder.

---

## 🙏 Acknowledgements

This player stands on the shoulders of giants. A huge thank you to the teams behind:
* [mpv](https://mpv.io/)
* [python-mpv](https://github.com/jaseg/python-mpv)
* [yt-dlp](https://github.com/yt-dlp/yt-dlp)
* [PySide6 (Qt for Python)](https://www.qt.io/qt-for-python)

---

## 📄 License

This project is licensed under the MIT License - see the `LICENSE.md` file for details.