from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox
import os
import json
import requests
import pygame

models = [
    ("Llama 2 7B Chat (fp16)", "@cf/meta/llama-2-7b-chat-fp16"), 
    ("Llama 2 7B Chat (int8)", "@cf/meta/llama-2-7b-chat-int8"), 
    ("Mistral 7B Instruct", "@cf/mistral/mistral-7b-instruct-v0.1"),
    ]

def get_voices():

    response = requests.get("https://api.elevenlabs.io/v1/voices")
    data = response.json()
    voices = [(voice["name"], voice["voice_id"], voice["preview_url"]) for voice in data["voices"]]

    return voices

def play_voice_preview(voice):
    # Check if the samples directory exists, if not, create it
    if not os.path.exists("samples"):
        os.makedirs("samples")

    # Check if the voice preview has already been downloaded
    if not os.path.exists(f"samples/{voice[1]}.mp3"):
        # Download the voice preview
        response = requests.get(voice[2])
        with open(f"samples/{voice[1]}.mp3", 'wb') as f:
            f.write(response.content)

    # Play the voice preview
    pygame.mixer.init()
    pygame.mixer.music.load(f"samples/{voice[1]}.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.quit()

class SettingsMenu(QWidget):

    settings_changed = pyqtSignal(dict)

    def __init__(self, main_app):
        super(SettingsMenu, self).__init__()
        self.main_app = main_app  # Save the reference to MyApp instance
        self.settings = self.load_settings()  # Save the reference to settings
        self.models = models
        self.voices = get_voices()
        self.initUI()

    def load_settings(self):

        default_settings = {
        "model": ("Llama 2 7B Chat (fp16)", "@cf/meta/llama-2-7b-chat-fp16"),
        "voice": ("Rachel", "21m00Tcm4TlvDq8ikWAM", ""),
        "silence" : 2
        }

        if os.path.exists('settings.json'):
            with open('settings.json', 'r') as f:
                settings = json.load(f)
        else:
            settings = default_settings

        return settings

    def initUI(self):
        vbox = QVBoxLayout()
        vbox.setSpacing(10)
        self.setLayout(vbox)

        self.model_label = QLabel(f'Model: {self.settings["model"][0]}')
        self.voice_label = QLabel(f'Voice: {self.settings["voice"][0]}')
        self.silence_label = QLabel(f'Silence detection: {self.settings["silence"]} s')

        self.model_combo = QComboBox()
        self.model_combo.addItems([model[0] for model in self.models])
        self.model_combo.setCurrentIndex(next(
            i for i, model in enumerate(self.models) if model[0] == self.settings["model"][0]))
        self.model_combo.currentIndexChanged.connect(self.change_model)

        self.voice_combo = QComboBox()
        self.voice_combo.addItems([voice[0] for voice in self.voices])
        self.voice_combo.setCurrentIndex(next(
            i for i, voice in enumerate(self.voices) if voice[0] == self.settings["voice"][0]))
        self.voice_combo.currentIndexChanged.connect(self.change_voice)

        self.silence_combo = QComboBox()
        silence_lowest_value = 2
        self.silence_combo.addItems([str(i) for i in range(silence_lowest_value, 11)])
        self.silence_combo.setCurrentIndex(int(self.settings["silence"]) - silence_lowest_value)
        self.silence_combo.currentIndexChanged.connect(self.change_silence_value)

        save_button = QPushButton('Save Settings')
        back_button = QPushButton('Back to Main Menu')

        save_button.clicked.connect(self.save_settings)
        back_button.clicked.connect(self.back_to_main)

        vbox.addWidget(self.model_label)
        vbox.addWidget(self.model_combo)
        vbox.addWidget(self.voice_label)
        vbox.addWidget(self.voice_combo)
        vbox.addWidget(self.silence_label)
        vbox.addWidget(self.silence_combo)
        vbox.addWidget(save_button)
        vbox.addWidget(back_button)

        self.setWindowTitle('Settings')
        self.setGeometry(300, 300, 320, 480)



    def change_model(self, index):
        self.model_label.setText(f'Model: {self.models[index][0]}')

    def change_voice(self, index):
        self.voice_label.setText(f'Voice: {self.voices[index][0]}')
        play_voice_preview(self.voices[index])  # Play the selected voice

    def change_silence_value(self):
        self.silence_label.setText(
            f'Silence detection: {self.silence_combo.currentText()} s'
        )

    def save_settings(self):
        settings = {'model': self.models[self.model_combo.currentIndex()],
                    'voice': self.voices[self.voice_combo.currentIndex()],
                    'silence': int(self.silence_combo.currentText()),}
        with open('settings.json', 'w') as f:
            json.dump(settings, f)  # Save the settings
        
        self.settings_changed.emit(settings)

    def back_to_main(self):
        """Hide the current window and show the main menu."""
        try:
            pos = self.pos()
            self.hide()
            self.main_app.move(pos)
            self.main_app.show()  # Show the main menu
        except RuntimeError as e:
            print(f"Failed to show main menu: {e}")
