from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from chat import initiate_chat
from settings import SettingsMenu

class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.title = 'ChAItty'
        self.version = '0.1'
        self.settings_menu = SettingsMenu(self)
        self.settings = self.settings_menu.load_settings()
        self.settings_menu.settings_changed.connect(self.update_settings)

        self.initUI()

    def update_settings(self, settings):
        """Update the settings."""
        self.settings = settings

    def initUI(self):
        """Initialize the user interface."""
        vbox = QVBoxLayout()
        self.setLayout(vbox)

        self.chat_button = QPushButton('Start chat')
        settings_button = QPushButton('Settings')
        exit_button = QPushButton('Exit')

        self.chat_button.clicked.connect(self.chat_function)
        settings_button.clicked.connect(self.show_settings_menu)
        exit_button.clicked.connect(QApplication.instance().quit)

        vbox.addWidget(self.chat_button)
        vbox.addWidget(settings_button)
        vbox.addWidget(exit_button)
        
        self.setWindowTitle(f'{self.title} v{self.version}')
        self.setGeometry(300, 300, 320, 480)
        self.show()

    def chat_function(self):
        """Start or continue the chat."""
        self.hide()
        self.chat_button.setText('Continue chat')
        QApplication.processEvents()
        try:
            initiate_chat(self.settings)
        except Exception as e:
            print(e)
            print(f"An error occurred, but you can continue chat")
        finally:
            self.show()

    def show_settings_menu(self):
        """Show the settings menu."""
        pos = self.pos()
        self.hide()
        self.settings_menu = SettingsMenu(self)  # Create a new instance of SettingsMenu
        self.settings_menu.move(pos)
        self.settings_menu.settings_changed.connect(self.update_settings)  # Connect the signal of the new instance
        self.settings_menu.show()

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())




