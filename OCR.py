import sys
from PyQt5.QtWidgets import QApplication, QRubberBand, QWidget, QPushButton, QVBoxLayout, QLabel, QMainWindow, QFrame, QHBoxLayout, QTextEdit, QScrollArea
from PyQt5.QtCore import Qt, QRect, QPoint, QSize, pyqtSignal, QMimeDatabase
from PyQt5.QtGui import QPixmap, QFont, QGuiApplication, QImage, QPainter
import pytesseract
from PIL import ImageGrab, Image
import spacy

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'D:\New folder (3)\tesseract.exe'

# NLP Model for Named Entity Recognition
nlp_ner = spacy.load("en_core_web_sm")  # Named Entity Recognition


class ScreenCapture(QWidget):
    textCaptured = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        screen = QGuiApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setWindowOpacity(0.2)
        self.setCursor(Qt.CrossCursor)
        self.start_point = QPoint()
        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        self.showFullScreen()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = event.pos()
            self.rubber_band.setGeometry(QRect(self.start_point, QSize()))
            self.rubber_band.show()

    def mouseMoveEvent(self, event):
        self.rubber_band.setGeometry(QRect(self.start_point, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            end_point = event.pos()
            self.rubber_band.hide()
            left, top = min(self.start_point.x(), end_point.x()), min(self.start_point.y(), end_point.y())
            right, bottom = max(self.start_point.x(), end_point.x()), max(self.start_point.y(), end_point.y())
            region = (left, top, right, bottom)
            screenshot = ImageGrab.grab(bbox=region)
            screenshot.save("selected_screenshot.png")
            text = pytesseract.image_to_string(screenshot)
            with open("captured_text_drag_global.txt", "w") as f:
                f.write(text)
            self.textCaptured.emit(text, "selected_screenshot.png")
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart OCR Tool")
        self.setGeometry(200, 200, 1000, 800)
        self.setStyleSheet("background-color: #f4f7f6; font-family: 'Arial', sans-serif;")
        self.initUI()

    def initUI(self):
        # Main layout
        main_layout = QVBoxLayout()

        # Title
        title_label = QLabel("📄 Text Extraction and Screen Capture Tool")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #333; padding: 20px; background-color: #00bcd4; border-radius: 10px;")
        main_layout.addWidget(title_label)

        # Button Layout
        button_layout = QHBoxLayout()
        
        # Capture Button
        self.capture_button = QPushButton("Capture Screen Region")
        self.capture_button.setFont(QFont("Arial", 12))
        self.capture_button.setStyleSheet(
            "QPushButton {background-color: #4CAF50; color: white; border-radius: 10px; padding: 12px; border: none;}"
            "QPushButton:hover {background-color: #45a049;}")
        self.capture_button.clicked.connect(self.launch_capture)
        button_layout.addWidget(self.capture_button)

        # Reset Button
        self.reset_button = QPushButton("Reset")
        self.reset_button.setFont(QFont("Arial", 12))
        self.reset_button.setStyleSheet(
            "QPushButton {background-color: #f44336; color: white; border-radius: 10px; padding: 12px; border: none;}"
            "QPushButton:hover {background-color: #e53935;}")
        self.reset_button.clicked.connect(self.reset_fields)
        button_layout.addWidget(self.reset_button)

        main_layout.addLayout(button_layout)

        # Instructions
        self.instruction_label = QLabel("Click the button above to select a region of the screen for text extraction.")
        self.instruction_label.setFont(QFont("Arial", 12))
        self.instruction_label.setAlignment(Qt.AlignCenter)
        self.instruction_label.setStyleSheet("color: #555; padding: 10px;")
        main_layout.addWidget(self.instruction_label)

        # Create scroll area for feedback and content display
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background-color: #ffffff; border-radius: 10px;")

        # Feedback area (Image + Text Display)
        self.feedback_area = QWidget()
        feedback_layout = QVBoxLayout()

        # Title for Screenshot area
        screenshot_title = QLabel("🖼 Screenshot")
        screenshot_title.setFont(QFont("Arial", 14, QFont.Bold))
        screenshot_title.setAlignment(Qt.AlignCenter)
        screenshot_title.setStyleSheet("color: #00bcd4; padding: 10px;")
        feedback_layout.addWidget(screenshot_title)

        # Image display (for screenshot)
        self.image_frame = QLabel()
        self.image_frame.setFrameShape(QFrame.Box)
        self.image_frame.setFixedSize(500, 300)
        self.image_frame.setAlignment(Qt.AlignCenter)
        self.image_frame.setStyleSheet("background-color: #f1f1f1; border-radius: 10px;")
        feedback_layout.addWidget(self.image_frame)

        # Title for Extracted Text area
        extracted_text_title = QLabel("📝Extracted Text")
        extracted_text_title.setFont(QFont("Arial", 14, QFont.Bold))
        extracted_text_title.setAlignment(Qt.AlignCenter)
        extracted_text_title.setStyleSheet("color: #00bcd4; padding: 10px;")
        feedback_layout.addWidget(extracted_text_title)

        # Extracted text display (for OCR output)
        self.text_output = QTextEdit()
        self.text_output.setFont(QFont("Arial", 10))
        self.text_output.setReadOnly(True)
        self.text_output.setStyleSheet("background-color: #f9f9f9; border-radius: 10px; padding: 10px;")
        feedback_layout.addWidget(self.text_output)

        # Add feedback area to scroll area
        self.feedback_area.setLayout(feedback_layout)
        self.scroll_area.setWidget(self.feedback_area)

        main_layout.addWidget(self.scroll_area)

        # Container for layout
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def launch_capture(self):
        self.capture_window = ScreenCapture()
        self.capture_window.textCaptured.connect(self.update_feedback)
        self.capture_window.show()

    def update_feedback(self, text, image_path):
        if text.strip():
            self.image_frame.setPixmap(QPixmap(image_path).scaled(500, 300, Qt.KeepAspectRatio))
            self.text_output.setText(text)
        else:
            self.text_output.setText("❌ No text found in the screenshot.")

    def reset_fields(self):
        self.image_frame.clear()
        self.text_output.clear()

    def analyze_text(self, text):
        doc = nlp_ner(text)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        ner_result = "\n".join([f"{entity[0]} ({entity[1]})" for entity in entities]) if entities else "No named entities found."
        return ner_result


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
