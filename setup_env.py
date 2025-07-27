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
    """Install required Python packages in a single pip call."""
    subprocess.check_call([
        sys.executable, '-m', 'pip', 'install', '--upgrade', *REQUIRED_PIP
    ])


def clone_koboldcpp():
    if not KOBOLD_DIR.exists():
        subprocess.check_call(['git', 'clone', KOBOLD_REPO, str(KOBOLD_DIR)])


def build_koboldcpp():
    """Compile KoboldCpp if the executable does not exist."""
    exe = KOBOLD_DIR / ('koboldcpp.exe' if sys.platform.startswith('win') else 'koboldcpp')
    if not exe.exists():
        subprocess.check_call(['make', '-j'], cwd=str(KOBOLD_DIR))


def download_model():
    if not MODEL_PATH.exists():
        subprocess.check_call(['wget', MODEL_URL, '-O', str(MODEL_PATH)])


def start_koboldcpp() -> subprocess.Popen:
    exe = './koboldcpp'
    if sys.platform.startswith('win'):
        exe = 'koboldcpp.exe'
    cmd = [exe, '--model', str(MODEL_PATH), '--port', KOBOLD_PORT]
    return subprocess.Popen(cmd, cwd=str(KOBOLD_DIR))


def create_shortcut():
    """Create a desktop shortcut on Windows"""
    if not sys.platform.startswith('win'):
        return
    desktop = Path(os.path.join(os.environ['USERPROFILE'], 'Desktop'))
    shortcut = desktop / 'Roleplay Abyss.lnk'
    target = Path(sys.executable)
    script = BASE_DIR / 'setup_env.py'
    cmd = [
        'powershell', '-NoProfile', '-Command',
        (
            f"$s=(New-Object -COM WScript.Shell).CreateShortcut('{shortcut}');"
            f"$s.TargetPath='{target}';"
            f"$s.Arguments='\"{script}\"';"
            f"$s.WorkingDirectory='{BASE_DIR}';"
            "$s.Save()"
        )
    ]
    subprocess.call(cmd)


def launch_gui():
    """Launch the PyQt5 GUI as a module."""
    subprocess.check_call([sys.executable, '-m', 'gui.app_gui'])


def main():
    for cmd in ['pip', 'git', 'wget']:
        check_cmd(cmd)
    install_packages()
    clone_koboldcpp()
    build_koboldcpp()
    download_model()
    create_shortcut()

    kobold = start_koboldcpp()
    try:
        launch_gui()
    finally:
        kobold.terminate()
        kobold.wait()


if __name__ == '__main__':
    main()
