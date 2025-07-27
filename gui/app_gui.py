"""PyQt5 GUI for Roleplay Abyss"""
import sys
import requests
from datetime import datetime
from pathlib import Path
from PyQt5 import QtWidgets, QtGui
from markdown import markdown
from .character_manager import Character, autofill_character

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

KOBOLD_ENDPOINT = 'http://localhost:5001/api/v1/generate'

class ChatWindow(QtWidgets.QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Roleplay Abyss')
        self.resize(800, 600)
        self.character = None
        self.history = []  # store conversation history
        self.init_ui()

    def init_ui(self):
        widget = QtWidgets.QWidget(self)
        self.setCentralWidget(widget)
        layout = QtWidgets.QVBoxLayout(widget)

        # Character selection and management
        char_layout = QtWidgets.QHBoxLayout()
        self.char_combo = QtWidgets.QComboBox()
        self.refresh_characters()
        self.char_combo.currentTextChanged.connect(self.load_character)
        char_layout.addWidget(self.char_combo)
        self.new_btn = QtWidgets.QPushButton('New')
        self.new_btn.clicked.connect(self.new_character)
        char_layout.addWidget(self.new_btn)
        self.edit_btn = QtWidgets.QPushButton('Edit')
        self.edit_btn.clicked.connect(self.edit_character)
        char_layout.addWidget(self.edit_btn)
        layout.addLayout(char_layout)

        # Avatar
        self.avatar_label = QtWidgets.QLabel()
        self.avatar_label.setFixedHeight(150)
        layout.addWidget(self.avatar_label)

        # Chat display
        self.chat_view = QtWidgets.QTextBrowser()
        layout.addWidget(self.chat_view)

        # Input area
        input_layout = QtWidgets.QHBoxLayout()
        self.input_edit = QtWidgets.QLineEdit()
        self.input_edit.returnPressed.connect(self.send_message)
        self.send_btn = QtWidgets.QPushButton('Send')
        self.send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(self.send_btn)
        layout.addLayout(input_layout)

    def new_character(self):
        name, ok = QtWidgets.QInputDialog.getText(self, 'Character Name', 'Enter character name:')
        if not ok or not name:
            return
        char = autofill_character(name)
        if char.description:
            QtWidgets.QMessageBox.information(self, 'Info Found', char.description)
        char.save()
        self.refresh_characters()
        index = self.char_combo.findText(name)
        if index >= 0:
            self.char_combo.setCurrentIndex(index)

    def edit_character(self):
        if not self.character:
            QtWidgets.QMessageBox.warning(self, 'No Character', 'Select a character to edit.')
            return
        text, ok = QtWidgets.QInputDialog.getMultiLineText(self, 'Edit Memory/Personality',
                                                          'Enter memory/personality:', self.character.memory)
        if ok:
            self.character.memory = text
            nsfw = QtWidgets.QMessageBox.question(self, 'NSFW Mode', 'Enable NSFW for this character?',
                                                 QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            self.character.nsfw = nsfw == QtWidgets.QMessageBox.Yes
            path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Select Avatar', '', 'Images (*.png *.jpg *.jpeg)')
            if path:
                self.character.avatar = path
            self.character.save()
            self.load_character(self.character.name)

    def refresh_characters(self):
        self.char_combo.clear()
        for name in Character.list_characters():
            self.char_combo.addItem(name)

    def load_character(self, name):
        if not name:
            return
        try:
            self.character = Character.load(name)
            if self.character.avatar and Path(self.character.avatar).exists():
                pix = QtGui.QPixmap(self.character.avatar)
                self.avatar_label.setPixmap(pix.scaledToHeight(150))
            else:
                self.avatar_label.clear()
            self.append_chat(f"Loaded character: {name}")
        except Exception as exc:
            QtWidgets.QMessageBox.warning(self, 'Error', str(exc))

    def append_chat(self, text, sender='System'):
        """Append text to chat display"""
        html = markdown(f"**{sender}:** {text}")
        self.chat_view.append(html)

    def send_message(self):
        if not self.character:
            QtWidgets.QMessageBox.warning(self, 'No Character', 'Please select a character first.')
            return
        user_text = self.input_edit.text().strip()
        if not user_text:
            return
        self.append_chat(user_text, 'You')
        self.history.append({'role': 'user', 'content': user_text})
        self.input_edit.clear()
        prompt = self.build_prompt(user_text)
        reply = self.query_kobold(prompt)
        self.append_chat(reply, self.character.name)
        self.history.append({'role': 'assistant', 'content': reply})
        self.log_message('You', user_text)
        self.log_message(self.character.name, reply)

    def build_prompt(self, user_text: str) -> str:
        """Construct a prompt including memory and chat history."""
        memory = f"{self.character.memory}\n" if self.character.memory else ""
        history_lines = [f"You: {msg['content']}" if msg['role'] == 'user' else f"{self.character.name}: {msg['content']}" for msg in self.history]
        history = "\n".join(history_lines)
        nsfw_tag = "" if self.character.nsfw else " [safe]"
        return f"{memory}{history}\nYou: {user_text}\n{self.character.name}{nsfw_tag}:"

    def log_message(self, speaker, text):
        ts = datetime.now().strftime('%Y%m%d')
        path = LOG_DIR / f"{self.character.name}_{ts}.log"
        with open(path, 'a', encoding='utf-8') as f:
            f.write(f"{speaker}: {text}\n")

    def query_kobold(self, prompt: str) -> str:
        """Send prompt string to KoboldCpp server"""
        payload = {
            'prompt': prompt,
            'max_new_tokens': 200,
            'stop_sequence': ['You:']
        }
        try:
            r = requests.post(KOBOLD_ENDPOINT, json=payload, timeout=60)
            r.raise_for_status()
            data = r.json()
            return data.get('results', [{}])[0].get('text', '').strip()
        except Exception as exc:
            return f"[Error contacting KoboldCpp: {exc}]"


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = ChatWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
