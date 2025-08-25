# Telegram Messenger Bot - README

## 📋 Overview

A feature-rich Telegram bot with a console interface that allows you to manage chats, send messages with timers, and track message views. This bot provides a terminal-based interface for interacting with Telegram messages.

## ✨ Features

- **Console-based Interface**: Navigate chats and messages through a terminal interface
- **Message Timers**: Set timers for automatic message deletion
- **Image Support**: Send and receive images with preview notifications
- **View Tracking**: See when your messages have been viewed (✓ for sent, ✓✓ for seen)
- **Chat Management**: Delete chats or individual messages from your local history
- **Auto-replies**: Automatic responses to common messages like "hi", "hello", etc.
- **Multi-threaded**: Handles incoming messages while you interact with the console

## 🛠️ Installation

### Prerequisites

- Python 3.7+
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)

### Setup

1. **Clone or create the project structure:**
   ```
   telegram_messenger/
   ├── main.py
   ├── config.py
   ├── downloaded_images/
   ├── __init__.py
   └── README.md
   ```

2. **Install required packages:**
   ```bash
   pip install python-telegram-bot requests
   ```

3. **Configure your bot token:**
   - Create a `config.py` file with your bot token:
   ```python
   BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
   ```
   - Get your token from [@BotFather](https://t.me/BotFather) on Telegram

4. **Run the bot:**
   ```bash
   python main.py
   ```

## 🎮 Usage

### Main Commands

| Command | Description |
|---------|-------------|
| `/exit` | Quit the application |
| `/refresh` | Refresh the current view |
| `/clear` | Clear the console screen |
| `/ids` | Show only chat IDs |
| `/delete` | Delete a chat |
| `/settings` | Change message settings |
| `/dmsg` | Delete messages in current chat |
| `/image` | Send a photo |
| `/timer` | Set timer for messages |

### Navigation

1. **Main Screen**: Shows all active chats
2. **Chat View**: Enter a chat by typing its ID
3. **Message Deletion**: Use `/dmsg` while in a chat to delete messages

### Sending Messages with Timers

1. Type your message normally or use `/image` to send a photo
2. The bot will ask if you want to set a timer
3. Enter the number of seconds for auto-deletion (0 for no timer)

## ⚙️ Settings

Access settings with `/settings`:

1. **Set default timer for images** - Automatic deletion timer for images
2. **Set default timer for messages** - Automatic deletion timer for text messages  
3. **Enable/disable auto-delete** - Toggle automatic deletion after sending

## 🔧 Technical Details

### File Structure

```
telegram_messenger/
├── main.py              # Main application code
├── config.py            # Bot token configuration
├── downloaded_images/   # Directory for received images
├── __init__.py          # Python package file
└── README.md           # This file
```

### Key Components

- **Console Interface**: Handles user input and display
- **Message Queue**: Processes incoming messages asynchronously
- **View Tracking**: Monitors message view status in background threads
- **Timer System**: Manages scheduled message deletions

## ⚠️ Limitations

- Message deletion (`/dmsg`) only affects local history, not Telegram servers
- View tracking uses a simulated approach due to Telegram API limitations
- Image display depends on system capabilities (may not work on all terminals)

## 🐛 Troubleshooting

### Common Issues

1. **`/dmsg` not working**: 
   - Make sure you're in a chat conversation first
   - The chat must have messages to delete

2. **Images not displaying**:
   - The bot tries various image viewers based on your OS
   - Images are always saved to `downloaded_images/` directory

3. **Bot not receiving messages**:
   - Verify your bot token in `config.py`
   - Ensure the bot has been started with `/start` in Telegram

### Getting Help

If you encounter issues:
1. Check that all dependencies are installed
2. Verify your bot token is correct
3. Ensure you've started the bot in Telegram first

## 📝 License

This project is for educational and personal use. Please respect Telegram's Terms of Service when using this bot.

## 🔄 Updates

For updates and improvements, check the original source or repository where you obtained this code.

---

**Note**: This bot is designed for personal use and demonstration purposes. Always respect privacy and comply with Telegram's terms of service.

--Completed By Soumya Das
