# main.py
# (UPDATED to fix logging)

import sys
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication
from main_window import MainWindow
from stylesheet import STYLESHEET

def setup_logging():
    """Configures the global logger for the application."""
    try:
        base_path = Path(sys.argv[0]).parent.resolve()
        log_file_path = base_path / "player.log"
        
        logging.basicConfig(
            level=logging.DEBUG, 
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                # --- FIX: Removed 'encoding' from StreamHandler ---
                logging.StreamHandler(sys.stdout),
                # --- FileHandler is correct ---
                logging.FileHandler(log_file_path, mode="w", encoding='utf-8')
            ]
        )
        logging.info("Logging configured successfully.")
    except Exception as e:
        print(f"Failed to configure logging: {e}")

def main():
    # ... (rest of file is unchanged) ...
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
        if Path(file_to_open).exists():
            # This call is now correct
            window.play_file_and_switch(file_to_open, [], [])
        else:
            logging.warning(f"File not found: {file_to_open}")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()