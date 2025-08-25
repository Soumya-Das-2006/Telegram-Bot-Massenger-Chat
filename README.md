# Telegram Messenger Bot - API

<div align="center">

![Telegram Messenger Bot](https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram) ![Python](https://img.shields.io/badge/Python-3.7%2B-green?logo=python) ![License](https://img.shields.io/badge/License-MIT-yellow) ![Status](https://img.shields.io/badge/Status-Active-brightgreen)

**A Terminal-Based Telegram Experience with Advanced Messaging Features**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Contributing](#-contributing)

</div>

## 🌟 Overview

Experience Telegram in a whole new way with this console-based messenger bot! Transform your terminal into a powerful messaging hub with advanced features like timed messages, view tracking, and intelligent auto-replies. Perfect for developers, power users, and anyone who loves command-line efficiency.

## ✨ Features

### 🎯 Core Functionality
- **Terminal-First Interface**: Navigate chats with keyboard-friendly commands
- **Real-time Message Sync**: Instant message sending and receiving
- **Multi-Chat Management**: Handle multiple conversations seamlessly

### ⏰ Smart Messaging
- **Scheduled Deletion**: Set timers for messages to auto-delete after specified intervals
- **Message Status Tracking**: See when messages are delivered (✓) and viewed (✓✓)
- **Media Support**: Send and receive images with terminal previews

### 🔧 Advanced Tools
- **Chat Organization**: Delete chats or messages from local history
- **Auto-Response System**: Smart replies to common greetings
- **Background Processing**: Multi-threaded architecture for smooth operation
- **Customizable Settings**: Configure default behaviors for your workflow

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- Terminal with Unicode support (for optimal display)

### Quick Setup

1. **Get Your Bot Token**:
   ```bash
   # Message @BotFather on Telegram and follow the prompts to create a new bot
   # Save the token provided - you'll need it next
   ```

2. **Install the Messenger Bot**:
   ```bash
   # Clone or download the project files
   mkdir telegram_messenger && cd telegram_messenger
   
   # Create your configuration
   echo "BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'" > config.py
   
   # Install dependencies
   pip install python-telegram-bot requests pillow
   ```

3. **First Run**:
   ```bash
   python main.py
   # The bot will initialize and prompt you to start a chat in Telegram
   ```

### File Structure
```
telegram_messenger/
├── main.py                 # Primary application logic
├── config.py              # Bot token configuration (create this)
├── downloaded_images/     # Automatically created for media storage
│   └── .gitkeep          # Keeps folder in version control
├── requirements.txt       # Python dependencies
└── README.md             # This documentation
```

## 🎮 Usage Guide

### Getting Started

1. **Start the bot** with `python main.py`
2. **In Telegram**, find your bot and send `/start` to initiate conversation
3. **In the terminal**, you'll see your chat list appear
4. **Type a chat number** to enter that conversation

### Command Reference

#### Global Commands (work anywhere)
| Command | Description | Example |
|---------|-------------|---------|
| `/exit` or `/quit` | Exit the application | `/exit` |
| `/refresh` or `/r` | Refresh current view | `/r` |
| `/clear` or `/cls` | Clear terminal screen | `/clear` |
| `/ids` | Show chat IDs only | `/ids` |
| `/help` | Show command help | `/help` |

#### Chat List Commands
| Command | Description | Example |
|---------|-------------|---------|
| `number` | Enter specified chat | `3` |
| `/delete [id]` | Delete a chat | `/delete 2` |
| `/settings` | Configure bot settings | `/settings` |

#### Conversation Commands
| Command | Description | Example |
|---------|-------------|---------|
| `message` | Send text message | `Hello there!` |
| `/image [path]` | Send image | `/image photo.jpg` |
| `/timer [secs]` | Set timer for next message | `/timer 60` |
| `/dmsg [start-end]` | Delete message range | `/dmsg 5-10` |
| `..` or `/back` | Return to chat list | `..` |

### Message Timer System

Set self-destruct timers for your messages:

1. **Per-message timer**: Use `/timer` before sending a message
   ```bash
   /timer 30  # Next message will delete after 30 seconds
   Hello, this will disappear in half a minute!
   ```

2. **Default timers**: Set in settings for automatic behavior
   ```bash
   /settings
   # Choose option 2 or 3 to set default timers
   ```

3. **Image-specific timer**: Different default for media messages

### View Tracking System

The bot simulates message status tracking:
- **Single checkmark (✓)**: Message sent successfully
- **Double checkmark (✓✓)**: Message viewed by recipient
- Status updates automatically in the background

## ⚙️ Configuration

### Customizing Settings

Access the settings menu with `/settings`:

1. **Image Timer Default**: Set automatic deletion time for images
2. **Message Timer Default**: Set automatic deletion time for text
3. **Auto-Delete Toggle**: Enable/disable automatic deletion after sending
4. **Auto-Reply Settings**: Configure automatic response behavior

### Environment Variables

For advanced deployment, you can use environment variables:

```bash
export BOT_TOKEN="your_token_here"
python main.py
```

## 🎨 Interface Overview

### Chat List View
```
==================================================
📱 TELEGRAM MESSENGER BOT - CHAT LIST
==================================================
ID  Chat                Last Message           Unread
1   John Doe           Hello there!            1
2   Tech Group         [Photo]                 3
3   Alice Smith        How are you?            0
--------------------------------------------------
Enter chat ID or command (/help for options):
```

### Conversation View
```
==================================================
💬 Conversation with John Doe (ID: 12345)
==================================================
[12:30] John Doe: Hey, how's the project going?
[12:31] You: It's going well! ✓✓
[12:32] John Doe: Send me those files when you can

Type your message or command:
```

## 🔧 Technical Details

### Architecture
- **Dual-thread Design**: Separate threads for UI and message processing
- **Event-driven Updates**: Real-time refresh when new messages arrive
- **Modular Components**: Separated concerns for maintainability

### Supported Platforms
- **Windows**: Command Prompt, PowerShell, Windows Terminal
- **macOS**: Terminal, iTerm2
- **Linux**: GNOME Terminal, Konsole, Terminator

### Image Handling
- Downloads images to `downloaded_images/` directory
- Attempts to display images using system viewers
- Supports common formats: JPG, PNG, GIF

## 🤝 Contributing

We welcome contributions! Here's how to help:

1. **Report Bugs**: Open an issue with detailed description
2. **Suggest Features**: Share your ideas for improvement
3. **Submit Code**: Fork the repository and create a pull request

### Development Setup
```bash
git clone https://github.com/yourusername/telegram_messenger.git
cd telegram_messenger
pip install -r requirements.txt
# Create config.py with your BOT_TOKEN
python main.py
```

## ❓ Frequently Asked Questions

**Q: Can the bot delete messages from Telegram servers?**
A: No, message deletion only affects your local history due to Telegram API limitations.

**Q: Why don't images display in my terminal?**
A: Image preview relies on system capabilities. Images are always saved to the downloaded_images folder.

**Q: How do I reset the bot?**
A: Delete the downloaded_images folder and restart the application.

**Q: Can I use this with multiple bot tokens?**
A: Currently, the bot supports one token per instance, but you can run multiple instances.

## 📝 Release Notes

### Version 1.0
- Initial release with core messaging functionality
- Timer system for automated message deletion
- Image support with terminal preview
- View tracking simulation

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

> **Important**: This bot is designed for personal use and educational purposes. Please respect Telegram's Terms of Service and privacy of others when using this software.

## 🙏 Acknowledgments

- Thanks to the Python-Telegram-Bot library team
- Telegram API for providing the messaging platform
- Contributors and testers who helped refine the experience

---

<div align="center">

**Crafted with ❤️ by Soumya Das**

*Transform your terminal into a messaging powerhouse!*

![Terminal Demo](https://media.giphy.com/media/LmNwrBhejkK9EFP504/giphy.gif)

</div>
