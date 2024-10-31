import sys
import pandas as pd
from PyQt5.QtCore import *
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl('https://google.com'))  # Set default URL to Google
        self.browser.setZoomFactor(1.6)  # Set zoom factor to 1.6
        self.setCentralWidget(self.browser)
        self.showMaximized()

        self.history = []  # List to store browsing history

        # Load credentials from Excel file
        self.credentials = pd.read_excel('credentials.xlsx')

        # Navbar
        navbar = QToolBar()
        navbar.setIconSize(QSize(24, 24))  # Set larger icon size
        self.addToolBar(navbar)

        back_btn = QAction(QIcon('back.png'), 'Back', self)
        back_btn.triggered.connect(self.browser.back)
        navbar.addAction(back_btn)

        forward_btn = QAction(QIcon('forward.png'), 'Forward', self)
        forward_btn.triggered.connect(self.browser.forward)
        navbar.addAction(forward_btn)

        reload_btn = QAction(QIcon('reload.png'), 'Reload', self)
        reload_btn.triggered.connect(self.browser.reload)
        navbar.addAction(reload_btn)

        home_btn = QAction(QIcon('home.png'), 'Home', self)
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)

        # Add spacers and address bar
        spacer1 = QWidget()
        spacer1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        navbar.addWidget(spacer1)

        self.url_bar = QLineEdit()
        self.url_bar.setFixedWidth(900)  # Set the width of the address bar to 900
        font = self.url_bar.font()
        font.setPointSize(14)  # Set the font size
        self.url_bar.setFont(font)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)

        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(100)
        self.progress_bar.setTextVisible(False)
        navbar.addWidget(self.progress_bar)

        # Add green tick icon
        self.green_tick = QLabel()
        self.green_tick.setPixmap(QPixmap('green_tick.png').scaled(16, 16, Qt.KeepAspectRatio))
        self.green_tick.setVisible(False)
        navbar.addWidget(self.green_tick)

        spacer2 = QWidget()
        spacer2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        navbar.addWidget(spacer2)

        # Add sign-in button
        self.sign_in_btn = QAction('Sign In', self)
        self.sign_in_btn.triggered.connect(self.sign_in)
        navbar.addAction(self.sign_in_btn)

        # Add history button (initially hidden)
        self.history_btn = QAction('History', self)
        self.history_btn.triggered.connect(self.show_history)
        self.history_btn.setVisible(False)
        navbar.addAction(self.history_btn)

        # Add theme toggle button
        self.theme_btn = QAction('Dark Mode', self)
        self.theme_btn.triggered.connect(self.toggle_theme)
        navbar.addAction(self.theme_btn)

        self.browser.urlChanged.connect(self.update_url)
        self.browser.loadProgress.connect(self.update_progress)
        self.browser.loadFinished.connect(self.on_load_finished)

        # Handle location permission requests
        self.browser.page().featurePermissionRequested.connect(self.on_feature_permission_requested)

        # Set initial theme
        self.set_light_theme()

    def navigate_home(self):
        self.browser.setUrl(QUrl('https://www.google.com'))

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith(('http://', 'https://')):
            if '.' in url:
                url = 'https://' + url
            else:
                url = 'https://www.google.com/search?q=' + url
        self.browser.setUrl(QUrl(url))

    def update_url(self, q):
        url = q.toString()
        self.url_bar.setText(url)
        if 'google.com/search?q=' in url:
            search_query = url.split('q=')[1]
            self.history.append(f"Search: {search_query} - {url}")
        else:
            self.history.append(f"Website: {url}")

    def update_progress(self, progress):
        self.progress_bar.setValue(progress)
        if progress < 100:
            self.progress_bar.setVisible(True)
            self.green_tick.setVisible(False)

    def on_load_finished(self):
        self.progress_bar.setVisible(False)
        self.green_tick.setVisible(True)

    def sign_in(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Sign In')
        layout = QVBoxLayout()

        username_label = QLabel('Username:')
        layout.addWidget(username_label)
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        password_label = QLabel('Password:')
        layout.addWidget(password_label)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.error_label = QLabel('')
        self.error_label.setStyleSheet('color: red')
        layout.addWidget(self.error_label)

        sign_in_button = QPushButton('Sign In')
        sign_in_button.clicked.connect(lambda: self.authenticate(dialog))
        layout.addWidget(sign_in_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def authenticate(self, dialog):
        username = self.username_input.text()
        password = self.password_input.text()

        # Check credentials from the Excel file
        if ((self.credentials['uid'] == username) & (self.credentials['pw'] == password)).any():
            dialog.accept()
            self.history_btn.setVisible(True)  # Show history button after successful login
            self.sign_in_btn.setText('Sign Out')  # Change sign-in button to sign-out
            self.sign_in_btn.triggered.disconnect()
            self.sign_in_btn.triggered.connect(self.sign_out)
        else:
            self.error_label.setText('Invalid username or password')

    def sign_out(self):
        self.history_btn.setVisible(False)  # Hide history button
        self.sign_in_btn.setText('Sign In')  # Change sign-out button to sign-in
        self.sign_in_btn.triggered.disconnect()
        self.sign_in_btn.triggered.connect(self.sign_in)

    def show_history(self):
        history_dialog = QDialog(self)
        history_dialog.setWindowTitle('Browsing History')
        history_dialog.resize(800, 600)  # Make the window bigger
        layout = QVBoxLayout()

        history_list = QListWidget()
        history_list.addItems(self.history)
        layout.addWidget(history_list)

        close_button = QPushButton('Close')
        close_button.clicked.connect(history_dialog.accept)
        layout.addWidget(close_button)

        history_dialog.setLayout(layout)
        history_dialog.exec_()

    def toggle_theme(self):
        if self.theme_btn.text() == 'Dark Mode':
            self.set_dark_theme()
            self.theme_btn.setText('Light Mode')
        else:
            self.set_light_theme()
            self.theme_btn.setText('Dark Mode')

    def set_light_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
            }
            QToolBar {
                background-color: #f0f0f0;
            }
            QLineEdit {
                background-color: white;
                color: black;
            }
            QLabel {
                color: black;
            }
            QProgressBar {
                background-color: white;
                color: black;
            }
            QPushButton {
                background-color: #e0e0e0;
                color: black;
            }
            QListWidget {
                background-color: white;
                color: black;
            }
        """)

    def set_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2e2e2e;
            }
            QToolBar {
                background-color: #3c3c3c;
            }
            QLineEdit {
                background-color: #3c3c3c;
                color: white;
            }
            QLabel {
                color: white;
            }
            QProgressBar {
                background-color: #3c3c3c;
                color: white;
            }
            QPushButton {
                background-color: #5c5c5c;
                color: white;
            }
            QListWidget {
                background-color: #3c3c3c;
                color: white;
            }
        """)

    def on_feature_permission_requested(self, url, feature):
        if feature == QWebEnginePage.Geolocation:
            self.browser.page().setFeaturePermission(url, feature, QWebEnginePage.PermissionGrantedByUser)

app = QApplication(sys.argv)
QApplication.setApplicationName('SGWEB')  # Set application name to SGWEB
window = MainWindow()
app.exec_()
