import sys
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QMovie, QIcon

class AnimatedIcon(QLabel):
    def __init__(self, gif_path, offset_x=0, offset_y=0, scale_factor=1.0):
        super().__init__()

        # Set up the window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Initialize offsets
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.scale_factor = scale_factor
        
        # Load the GIF
        self.movie = QMovie(gif_path)
        
        # Connect to the frameChanged signal to adjust the window size when the GIF is loaded
        self.movie.frameChanged.connect(self.adjustSizeToGIF)
        self.setMovie(self.movie)
        self.movie.start()
        
        # Calculate the initial position to place the window in the center-right-bottom of the screen
        screen_geometry = QApplication.desktop().availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        
        # Set initial position
        self.move_to_position(screen_width, screen_height)

        # Make the window draggable
        self.dragging = False

    def adjustSizeToGIF(self):
        if self.movie.frameCount() > 0:
            size = self.movie.currentImage().size()
            scaled_width = int(size.width() * self.scale_factor)
            scaled_height = int(size.height() * self.scale_factor)
            scaled_size = QSize(scaled_width, scaled_height)
            self.movie.setScaledSize(scaled_size)
            self.setFixedSize(scaled_size)
            self.movie.frameChanged.disconnect(self.adjustSizeToGIF)  # Disconnect after the first call

            # Recalculate and update the position after adjusting size
            screen_geometry = QApplication.desktop().availableGeometry()
            screen_width = screen_geometry.width()
            screen_height = screen_geometry.height()
            self.move_to_position(screen_width, screen_height)

    def move_to_position(self, screen_width, screen_height):
        # Calculate the position to place the window in the center-bottom of the screen
        new_x = (screen_width - self.width()) // 2 + self.offset_x
        new_y = screen_height - self.height() + self.offset_y
        self.move(new_x, new_y)

    def mousePressEvent(self, event):
        self.dragging = True
        self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
        event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPos() - self.drag_start_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.dragging = False
        event.accept()

    def raise_window(self):
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.show()

def main():
    # Ensure the application supports transparency
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    QApplication.setAttribute(Qt.AA_UseDesktopOpenGL)

    app = QApplication(sys.argv)
    
    # Set the application name and display name
    app.setApplicationName("ChatMate")
    app.setApplicationDisplayName("ChatMate")

    # Set the application icon
    app_icon = QIcon('static/SynopAI-Logo-rb.png')  # Replace with the path to your icon file
    app.setWindowIcon(app_icon)

    # Adjust the scale_factor as needed
    icon = AnimatedIcon('static/helper_rb_crop.gif', 0, 0, scale_factor=0.5)  # Adjust the scale_factor as needed
    icon.show()

    # Ensure the icon window stays on top
    icon.raise_window()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()