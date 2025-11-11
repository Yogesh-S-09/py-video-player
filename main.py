# main.py
# (UPDATED to fix logging and 'Open With' TypeError)

import sys
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
from main_window import MainWindow
from stylesheet import STYLESHEET

def setup_logging():
    """Configures the global logger for the application."""
    try:
        base_path = Path(sys.argv[0]).parent.resolve()
        log_file_path = base_path / "player.log"
        
        logging.basicConfig(
            level=logging.INFO,  
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(log_file_path, mode="w", encoding='utf-8')
            ]
        )
        logging.info("Logging configured successfully.")
    except Exception as e:
        print(f"Failed to configure logging: {e}", file=sys.stderr)

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
        file_path = Path(file_to_open)
        if file_path.exists():
            if file_path.is_file():
                try:
                    # This is for a local file, so audio/video tracks are empty
                    window.library_widget.add_file(file_to_open)
                    window.play_file_and_switch(file_to_open, [], [])
                    logging.info(f"Successfully opened file: {file_to_open}")
                except Exception as e:
                    logging.error(f"Failed to open file {file_to_open}: {e}", exc_info=True)
            else:
                logging.error(f"Path is not a file: {file_to_open}")
        else:
            logging.warning(f"File not found: {file_to_open}")
            QMessageBox.warning(window, "File Not Found", 
                              f"The file could not be found:\n{file_to_open}")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()