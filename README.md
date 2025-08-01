# Roleplay Abyss

Roleplay Abyss is an offline desktop chatbot built with PyQt5 that connects to a locally running KoboldCpp server. It allows you to create and manage characters, toggle NSFW mode, and log conversations. All models and data stay on your machine.

## Features
- PyQt5 GUI chat interface
- Local KoboldCpp integration on `localhost:5001`
- Character creation with optional info from Wikipedia or DuckDuckGo
- Per-character NSFW/Safe Mode
- Markdown formatting in replies
- Chat logs stored in `/logs`

## Setup

Run the setup script to install dependencies, download KoboldCpp and a GGUF model, then launch the GUI. The script also starts KoboldCpp in the background and shuts it down once you close the window:

Run the setup script to install dependencies, download KoboldCpp and a GGUF model, then launch the GUI:


```bash
python setup_env.py
```


After the initial run, simply execute the same command again to launch the app.

The first launch may take a while while the model downloads.
