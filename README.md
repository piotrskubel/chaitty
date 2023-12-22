# ChAItty

## Charming AI talks to you!

![enter image description here](https://i.ibb.co/dQn5zHn/conversation.jpg)

Learn foreign languages the natural way, by having engaging conversations with AI. Just launch the app, choose your settings and enjoy talking. This **Python** app is designed for non-native English speakers who want to improve their skills.

## Installation

1. Clone the repository.

2. Having the **Python** installed create a **virtual environment**. Enter the cloned project directory and type (Windows):

```bash
python -m venv venv-name
cd venv-name
cd Scripts
activate
cd..
cd..
```

3. Install required frameworks:

```bash
pip install -r requirements.txt
```

4. Create the free accounts on the following websites:

- https://www.cloudflare.com/
- https://elevenlabs.io/

5.  Create .env file and enter required information:

```txt
CLOUDFLARE_API={your cloudflare.com API key}
CLOUDFLARE_ID={your cloudflare.com free account ID number}
ELEVENLABS_API={your elevenlabs.io API key, which allows you to produce voice of 10 000 characters each month for free}
```

6. Include **ffmpeg** in system Path variable. In case to do so follow the steps:

- Download **ffmpeg** from https://ffmpeg.org/

- Go to: System -> Advanced system settings -> Advanced tab -> Environment Variables -> System variables section -> Edit button -> New:

```
your path\ffmpeg\bin
```

## Usage

Start the app with

```bash
python main.py
```

Wait for the simple GUI to load. There are 3 options in the menu:

- Start chat
- Settings
- Exit

While the chat is active the **GUI** will be hidden and you should follow the messages printed in the terminal. Wait for the **Recording...** and start speaking. If the app detects a longer silent moment you will see the **Silence detected** and **Recording finished** statements. After processing you will hear a response.

## Settings and context

In the **Settings** menu you can change 4 options:

- the **LLM** responsible for generating the answers
- the **voice** used for playing the answers
- the **duration of silence** in seconds, after which current recording will stop
- ability to enable or disable chat **auto-continue**

If **auto-continue** is disabled you will see the GUI after each response and you can **Continue chat**, adjust the **Settings** or **Exit**.
If **auto-continue** is enabled you will see a short countdown for the next **Recording...** after each response.
To end the chat just say goodbye.

A conversation history is in default stored in the _context.txt_ file in the main directory. Context for the language model is created from the affirmative lines of the whole conversation. The algorithm calculates a similarity score for each line and selects the ones, which best apply to the current user input.
