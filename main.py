# main.py
# (UPDATED to configure logging)

import sys
import logging # Import logging
from PySide6.QtWidgets import QApplication
from main_window import MainWindow
from stylesheet import STYLESHEET

def setup_logging():
    """Configures the global logger for the application."""
    # Configure the root logger
    logging.basicConfig(
        level=logging.DEBUG,  # Set the default level (e.g., DEBUG, INFO)
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            # logging.StreamHandler(sys.stdout) # Log to the console
            # You can also add a FileHandler here:
            logging.FileHandler("player.log", mode="w")
        ]
    )
    logging.info("Logging configured successfully.")

def main():
    # Set up logging as the very first step
    setup_logging()
    
    # Create the QApplication
    app = QApplication(sys.argv)
    
    # Apply the dark theme stylesheet
    app.setStyleSheet(STYLESHEET)
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()