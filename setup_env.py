"""Setup environment and launch Roleplay Abyss"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

# Required Python packages
REQUIRED_PIP = [
    'PyQt5',
    'requests',
    'wikipedia',
    'duckduckgo_search',
    'markdown'
]

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / 'models'
MODEL_DIR.mkdir(exist_ok=True)
LLM_DIR = BASE_DIR / 'llm'
LLM_DIR.mkdir(exist_ok=True)
KOBOLD_DIR = LLM_DIR / 'koboldcpp'
MODEL_PATH = MODEL_DIR / 'MythoMax-L2.Q4_K_M.gguf'

KOBOLD_PORT = '5001'

KOBOLD_REPO = 'https://github.com/LostRuins/koboldcpp.git'
MODEL_URL = 'https://huggingface.co/Gryphe/MythoMax-L2-GGUF/resolve/main/MythoMax-L2-Q4_K_M.gguf'


def check_cmd(cmd: str):
    """Ensure a system command exists"""
    if shutil.which(cmd) is None:
        print(f"Error: {cmd} is required but not found in PATH.")
        sys.exit(1)


def install_packages():
    for pkg in REQUIRED_PIP:
        subprocess.call([sys.executable, '-m', 'pip', 'install', pkg])


def clone_koboldcpp():
    if not KOBOLD_DIR.exists():
        subprocess.check_call(['git', 'clone', KOBOLD_REPO, str(KOBOLD_DIR)])


def download_model():
    if not MODEL_PATH.exists():
        subprocess.check_call(['wget', MODEL_URL, '-O', str(MODEL_PATH)])


def start_koboldcpp() -> subprocess.Popen:
    exe = './koboldcpp'
    if sys.platform.startswith('win'):
        exe = 'koboldcpp.exe'
    cmd = [exe, '--model', str(MODEL_PATH), '--port', KOBOLD_PORT]
    return subprocess.Popen(cmd, cwd=str(KOBOLD_DIR))


def launch_gui():
    """Launch the PyQt5 GUI as a module."""
    subprocess.check_call([sys.executable, '-m', 'gui.app_gui'])


def main():
    for cmd in ['pip', 'git', 'wget']:
        check_cmd(cmd)
    install_packages()
    clone_koboldcpp()
    download_model()

    kobold = start_koboldcpp()
    try:
        launch_gui()
    finally:
        kobold.terminate()
        kobold.wait()


if __name__ == '__main__':
    main()
