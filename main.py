# main.py
# (UPDATED to create the log file next to the .exe)

import sys
import logging
from pathlib import Path # --- IMPORT Pathlib ---
from PySide6.QtWidgets import QApplication
from main_window import MainWindow
from stylesheet import STYLESHEET

def setup_logging():
    """Configures the global logger for the application."""
    
    # --- THIS IS THE FIX ---
    # Get the directory where the script/exe is located
    # sys.argv[0] is the path to our script or .exe
    base_path = Path(sys.argv[0]).parent.resolve()
    log_file_path = base_path / "player.log"
    # -----------------------
    
    logging.basicConfig(
        level=logging.DEBUG, 
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            # Use the new, absolute path
            logging.FileHandler(log_file_path, mode="w") 
        ]
    )
    logging.info(f"Logging configured. Log file at: {log_file_path}")

def main():
    setup_logging()
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    
    file_to_open = None
    if len(sys.argv) > 1:
        file_to_open = sys.argv[1]
        logging.info(f"Attempting to open file from argument: {file_to_open}")

    window = MainWindow()
    window.show()
    
    if file_to_open:
        # --- FIX: Need to import Path in this file to use it here ---
        # We check if the file exists before trying to load it
        if Path(file_to_open).exists():
            window.player_widget.load_file(file_to_open)
        else:
            logging.warning(f"File not found: {file_to_open}")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()