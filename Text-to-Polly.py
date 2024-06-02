import pygame
import boto3
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QLineEdit, QComboBox, QSlider,
                             QTextEdit, QMessageBox)
from PyQt5.QtGui import QGuiApplication
import os
import botocore.exceptions


class CredentialsDialog(QWidget):
    def __init__(self, initial_key="", initial_secret=""):
        super().__init__()
        self.setWindowTitle("AWS Credentials Input")
        self.setFixedSize(300, 150)
        self.result = False

        layout = QVBoxLayout()

        key_layout = QHBoxLayout()
        self.key_edit = QLineEdit(initial_key)
        key_layout.addWidget(QLabel("Polly AccessKey:"))
        key_layout.addWidget(self.key_edit)

        secret_layout = QHBoxLayout()
        self.secret_edit = QLineEdit(initial_secret)
        secret_layout.addWidget(QLabel("Polly SecretAccess:"))
        secret_layout.addWidget(self.secret_edit)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.submit)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)

        layout.addLayout(key_layout)
        layout.addLayout(secret_layout)
        layout.addWidget(self.ok_button)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

    def submit(self):
        if self.key_edit.text() and self.secret_edit.text():
            self.result = True
            self.close()

    def exec_(self):
        super().exec_()
        return self.result, self.key_edit.text(), self.secret_edit.text()


class TextToSpeech(QWidget):
    def __init__(self):
        super().__init__()
        pygame.mixer.init()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Text to Speech")
        self.setGeometry(100, 100, 400, 300)

        self.text_area = QTextEdit(self)
        self.voice_combobox = QComboBox(self)
        self.voice_combobox.addItems(['Daniel', 'Vicki', 'Ruth', 'Stephen'])
        self.speed_slider = QSlider(Qt.Horizontal, self)
        self.speed_slider.setMinimum(50)
        self.speed_slider.setMaximum(250)
        self.speed_slider.setValue(100)

        self.play_button = QPushButton("Play", self)
        self.update_credentials_button = QPushButton("Update AWS Credentials", self)
        self.paste_button = QPushButton("Paste", self)
        self.clear_button = QPushButton("Clear", self)

        layout = QVBoxLayout(self)
        layout.addWidget(self.text_area)
        layout.addWidget(self.voice_combobox)
        layout.addWidget(self.speed_slider)
        layout.addWidget(self.play_button)
        layout.addWidget(self.update_credentials_button)
        layout.addWidget(self.paste_button)
        layout.addWidget(self.clear_button)

        self.play_button.clicked.connect(self.play)
        self.update_credentials_button.clicked.connect(self.update_credentials)
        self.paste_button.clicked.connect(self.paste_from_clipboard)
        self.clear_button.clicked.connect(self.clear)

    def setup_polly_client(self):
        try:
            self.polly_client = boto3.Session(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name='eu-west-1'
            ).client('polly')
            # Führe einen einfachen Test aus, um die Gültigkeit zu überprüfen
            self.polly_client.describe_voices()
            return True
        except (botocore.exceptions.ClientError, botocore.exceptions.NoCredentialsError) as e:
            QMessageBox.critical(self, "AWS Client Error", f"An error occurred: {str(e)}")
            return False

    def get_voices(self):
        return ['Daniel', 'Vicki', 'Ruth', 'Stephen']

    def load_aws_credentials(self):
        filepath = 'polly_credentials.txt'
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            with open(filepath, 'r') as f:
                lines = f.read().splitlines()
                if len(lines) >= 2:
                    return lines[0].strip(), lines[1].strip()
        return None, None  # Return None if the credentials are invalid

    def update_credentials(self):
        dialog = CredentialsDialog()
        result, key, secret = dialog.exec_()
        if result:
            self.aws_access_key_id = key
            self.aws_secret_access_key = secret
            # Versuche, den Polly-Client mit den neuen Credentials zu initialisieren
            if self.setup_polly_client():
                QMessageBox.information(self, "Success", "Credentials successfully updated and verified.")
            else:
                QMessageBox.critical(self, "Error", "Credentials updated but not valid. Please try again.")
        else:
            QMessageBox.warning(self, "Cancelled", "Credential update cancelled.")

    def synthesize_speech(self, text, voice, speed):
        if self.aws_access_key_id and self.aws_secret_access_key:
            try:
                # Konvertiere Speed-Wert von Slider zu einem Prozentsatz für Polly
                speed_percentage = str(int((speed / 100.0) * 2.5 * 100)) + '%'
                # Generiere SSML Text
                ssml_text = f"<speak><prosody rate='{speed_percentage}'>{text}</prosody></speak>"
                # Führe Sprachsynthese aus
                response = self.polly_client.synthesize_speech(
                    VoiceId=voice,
                    OutputFormat='mp3',
                    Text=ssml_text,
                    TextType="ssml",
                    Engine='neural'
                )
                # Speichere die Audiodaten in einer Datei
                with open('speech.mp3', 'wb') as f:
                    f.write(response['AudioStream'].read())
                # Spiele die Audio-Datei ab
                pygame.mixer.init()
                pygame.mixer.music.load('speech.mp3')
                pygame.mixer.music.play()
                QMessageBox.information(self, "Playing", "Playing the synthesized speech.")
                return True
            except (botocore.exceptions.ClientError, ValueError) as e:
                QMessageBox.critical(self, "AWS Client Error", f"An error occurred: {str(e)}")
                self.update_credentials()  # Aufforderung zur erneuten Eingabe der Anmeldeinformationen
                return False
        else:
            QMessageBox.warning(self, "Credential Issue", "Please update your AWS credentials first.")
            self.update_credentials()
            return False

    def paste_from_clipboard(self):
        clipboard = QGuiApplication.clipboard()  # Zugriff auf das Clipboard
        text = clipboard.text()  # Holen des Textes aus dem Clipboard
        if text:
            self.text_area.insertPlainText(text)  # Fügt den Text an der aktuellen Cursorposition ein
        else:
            QMessageBox.warning(self, "Empty Clipboard", "There is no text to paste from the clipboard.")

    def play(self):
        if self.aws_access_key_id and self.aws_secret_access_key:
            try:
                text = self.text_area.toPlainText()
                voice = self.voice_combobox.currentText()
                speed = self.speed_slider.value()
                response = self.polly_client.synthesize_speech(
                    VoiceId=voice,
                    OutputFormat='mp3',
                    Text=text,
                    TextType='text',
                    Engine='neural'
                )
                # Hier könnte man die Audiodaten speichern oder direkt abspielen
                with open('speech.mp3', 'wb') as f:
                    f.write(response['AudioStream'].read())
                # Abspielen der Datei
                pygame.mixer.init()
                pygame.mixer.music.load('speech.mp3')
                pygame.mixer.music.play()
                QMessageBox.information(self, "Playing", "Playing the synthesized speech.")
            except botocore.exceptions.ClientError as e:
                QMessageBox.critical(self, "AWS Client Error", f"An error occurred: {str(e)}")
                self.update_credentials()  # Prompt to re-enter credentials if there's a client error
        else:
            QMessageBox.warning(self, "Credential Issue", "Please update your AWS credentials first.")
            self.update_credentials()

    def pause(self):
        pygame.mixer.music.pause()

    def unpause(self):
        pygame.mixer.music.unpause()

    def stop(self):
        pygame.mixer.music.stop()

    def clear(self):
        self.text_area.clear()  # Löscht den gesamten Text aus dem QTextEdit

    def clear_paste_play(self):
        self.clear()  # Klartextfeld
        self.paste_from_clipboard()  # Fügt Text aus der Zwischenablage ein
        self.play()  # Spielt den eingefügten Text ab


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TextToSpeech()
    window.show()
    sys.exit(app.exec_())
