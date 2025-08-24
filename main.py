import threading
import time
import os
import requests
from io import BytesIO
from datetime import datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN
import mimetypes
import shutil
import random

# Store chat data
active_chats = {}
message_queue = []
console_lock = threading.Lock()
current_display = "main"  # Track what's currently displayed
refresh_needed = False  # Flag to indicate if display needs refresh
pending_deletions = []  # Track messages scheduled for deletion

def clear_console():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_image_notification(image_path, chat_name):
    """Display image notification in console"""
    try:
        # Try to display image using various methods
        if os.name == 'nt':  # Windows
            os.system(f'start {image_path}')
        elif os.name == 'posix':  # Linux/Mac
            if os.system('which feh > /dev/null 2>&1') == 0:
                os.system(f'feh {image_path} &')
            elif os.system('which eog > /dev/null 2>&1') == 0:
                os.system(f'eog {image_path} &')
            else:
                print(f"📸 Image received from {chat_name}")
                print(f"📁 Image saved at: {image_path}")
        else:
            print(f"📸 Image received from {chat_name}")
            print(f"📁 Image saved at: {image_path}")
            
    except Exception as e:
        print(f"📸 Image received from {chat_name}")
        print(f"📁 Image saved at: {image_path}")

def display_main_interface():
    """Display the main interface with active chats"""
    global refresh_needed
    with console_lock:
        clear_console()
        print("╔════════════════════ TELEGRAM MESSENGER ═══════════════════════╗")
        print("║ Type /exit to quit, /refresh to refresh, /clear to clear      ║")
        print("║ Type /ids to show only chat IDs                               ║")
        print("║ Type /delete to delete a chat                                 ║")
        print("║ Type /settings to change message settings                     ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()
        
        if not active_chats:
            print("No active chats yet. Waiting for messages...")
        else:
            print("Your active chats:")
            print("─" * 60)
            print("ID        Name")
            print("─" * 60)
            for chat_id, chat in active_chats.items():
                unread = sum(1 for msg in chat['messages'] if msg['direction'] == 'incoming' and not msg.get('read', False))
                unread_indicator = f" ({unread} new)" if unread > 0 else ""
                print(f"{chat_id:<9} {chat['name']}{unread_indicator}")
            
            print("─" * 60)
        
        print("\nEnter chat ID to reply or command:")
        refresh_needed = False

def display_ids_only():
    """Display only chat IDs"""
    global refresh_needed
    with console_lock:
        clear_console()
        print("╔════════════════════ CHAT IDs ════════════════════╗")
        print("║ Type /back to return to main screen              ║")
        print("║ Type /delete to delete a chat                    ║")
        print("╚══════════════════════════════════════════════════╝")
        print()
        
        if not active_chats:
            print("No active chats yet. Waiting for messages...")
        else:
            print("Chat IDs:")
            print("─" * 30)
            for chat_id, chat in active_chats.items():
                unread = sum(1 for msg in chat['messages'] if msg['direction'] == 'incoming' and not msg.get('read', False))
                unread_indicator = f" ({unread} new)" if unread > 0 else ""
                print(f"{chat_id}{unread_indicator}")
            
            print("─" * 30)
        
        print("\nType /back to return or /delete to delete:")
        refresh_needed = False

def display_chat_interface(chat_id):
    """Display the chat interface for a specific chat"""
    global refresh_needed
    with console_lock:
        clear_console()
        chat = active_chats[chat_id]
        print(f"╔════════════════ CHAT WITH {chat['name'].upper()} ═════════════════╗")
        print(f"║ ID: {chat_id}                                                  ║")
        if chat.get('username'):
            print(f"║ Username: @{chat['username']}                                      ║")
        print("║ Type /back to return, /refresh to refresh, /clear to clear  ║")
        print("║ Type /delete to delete this chat, /dmsg to delete messages  ║")
        print("║ Type /image to send photo, /timer to set timer for messages ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()
        
        # Mark messages as read when viewing chat
        for msg in chat['messages']:
            if msg['direction'] == 'incoming':
                msg['read'] = True
        
        # Display messages
        for msg in chat['messages']:
            timestamp = msg['time'].strftime("%H:%M")
            seen_indicator = " ✓✓" if msg.get('seen') else " ✓" if msg['direction'] == 'outgoing' else ""
            
            if msg['direction'] == 'incoming':
                if msg['type'] == 'text':
                    print(f"{timestamp} {chat['name']}: {msg['text']}{seen_indicator}")
                elif msg['type'] == 'image':
                    print(f"{timestamp} {chat['name']}: [Image: {msg.get('filename', 'photo')}] 📸{seen_indicator}")
                    if msg.get('local_path'):
                        print(f"         📁 Saved at: {msg['local_path']}")
            else:
                if msg['type'] == 'text':
                    print(f"{timestamp} You: {msg['text']}{seen_indicator}")
                elif msg['type'] == 'image':
                    print(f"{timestamp} You: [Image: {msg.get('filename', 'photo')}] 📸{seen_indicator}")
        
        print("─" * 60)
        print("Type your message or command:")
        refresh_needed = False

def delete_chat_interface():
    """Display interface for deleting a chat"""
    global refresh_needed
    with console_lock:
        clear_console()
        print("╔════════════════════ DELETE CHAT ════════════════════╗")
        print("║ Type /back to return to main screen                 ║")
        print("╚═════════════════════════════════════════════════════╝")
        print()
        
        if not active_chats:
            print("No active chats to delete.")
            print("\nType /back to return:")
            return
        
        print("Select chat to delete:")
        print("─" * 60)
        print("ID        Name")
        print("─" * 60)
        for i, (chat_id, chat) in enumerate(active_chats.items(), 1):
            print(f"{i}. {chat_id:<9} {chat['name']}")
        
        print("─" * 60)
        print("\nEnter the number of chat to delete or /back to return:")
        refresh_needed = False

def delete_message_interface(chat_id):
    """Display interface for deleting messages in a chat"""
    global refresh_needed
    with console_lock:
        clear_console()
        chat = active_chats[chat_id]
        print(f"╔════════════ DELETE MESSAGES - {chat['name'].upper()} ════════════╗")
        print(f"║ ID: {chat_id}                                                  ║")
        print("║ Type /back to return to chat                                  ║")
        print("║ Type /all to delete all messages                              ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()
        
        if not chat['messages']:
            print("No messages to delete.")
            print("\nType /back to return:")
            return
        
        print("Select message to delete:")
        print("─" * 80)
        print("No.  Time     Direction  Message")
        print("─" * 80)
        for i, msg in enumerate(chat['messages'], 1):
            timestamp = msg['time'].strftime("%H:%M")
            direction = "Incoming" if msg['direction'] == 'incoming' else "Outgoing"
            preview = msg['text'][:40] + "..." if msg['type'] == 'text' and len(msg['text']) > 40 else msg['text'] if msg['type'] == 'text' else ""
            if msg['type'] == 'image':
                preview = f"[Image: {msg.get('filename', 'photo')}]"
            print(f"{i:<4} {timestamp} {direction:<10} {preview}")
        
        print("─" * 80)
        print("\nEnter message number to delete, /all to delete all, or /back to return:")
        refresh_needed = False

def settings_interface():
    """Display settings interface"""
    global refresh_needed
    with console_lock:
        clear_console()
        print("╔════════════════════ SETTINGS ═════════════════════╗")
        print("║ Type /back to return to main screen               ║")
        print("║                                                   ║")
        print("║ Message Timer Settings:                           ║")
        print("║ 1. Set default timer for images (seconds)         ║")
        print("║ 2. Set default timer for messages (seconds)       ║")
        print("║ 3. Enable/disable auto-delete after sending       ║")
        print("╚═══════════════════════════════════════════════════╝")
        print()
        
        print("Current Settings:")
        print("─" * 40)
        print(f"Image Timer: {message_timer.get('image', 0)} seconds")
        print(f"Message Timer: {message_timer.get('text', 0)} seconds")
        print(f"Auto Delete: {'Enabled' if auto_delete else 'Disabled'}")
        print("─" * 40)
        
        print("\nEnter option number to change or /back to return:")
        refresh_needed = False

# Global settings
message_timer = {'image': 0, 'text': 0}  # Default no timer
auto_delete = False

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages"""
    user = update.message.from_user
    chat_id = update.message.chat.id
    text = update.message.text.strip().lower() if update.message.text else ""
    timestamp = datetime.now()
    
    # Initialize chat if not exists
    if chat_id not in active_chats:
        active_chats[chat_id] = {
            'name': user.first_name + (f" {user.last_name}" if user.last_name else ""),
            'username': user.username,
            'messages': []
        }
    
    # Check if message contains photo
    if update.message.photo:
        # Get the highest resolution photo
        photo = update.message.photo[-1]
        file_id = photo.file_id
        
        # Download the photo
        file = await context.bot.get_file(file_id)
        file_path = file.file_path
        
        # Create images directory if it doesn't exist
        os.makedirs("downloaded_images", exist_ok=True)
        
        # Generate filename
        filename = f"image_{chat_id}_{int(time.time())}.jpg"
        local_path = os.path.join("downloaded_images", filename)
        
        # Download the file
        await file.download_to_drive(local_path)
        
        # Add image message to chat history
        active_chats[chat_id]['messages'].append({
            'type': 'image',
            'filename': filename,
            'local_path': local_path,
            'time': timestamp,
            'direction': 'incoming',
            'read': False
        })
        
        # Add to message queue for display
        message_queue.append({
            'type': 'image',
            'chat_id': chat_id,
            'filename': filename,
            'local_path': local_path,
            'name': active_chats[chat_id]['name'],
            'time': timestamp
        })
        
    else:
        # Add text message to chat history
        active_chats[chat_id]['messages'].append({
            'type': 'text',
            'text': update.message.text,
            'time': timestamp,
            'direction': 'incoming',
            'read': False
        })
        
        # Add to message queue for display
        message_queue.append({
            'type': 'message',
            'chat_id': chat_id,
            'text': update.message.text,
            'name': active_chats[chat_id]['name'],
            'time': timestamp
        })

    # --- Auto-reply section ---
    auto_replies = {
        "hi": "Hello! 👋",
        "hello": "Hi there!",
        "how are you": "I'm doing great, thanks for asking! How about you?",
        "bye": "Goodbye! 👋",
        "thanks": "You're welcome! 😊"
    }

    for trigger, reply in auto_replies.items():
        if trigger in text:
            # Send reply using bot API
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {'chat_id': chat_id, 'text': reply}
            response = requests.post(url, data=data)

            if response.status_code == 200:
                # Add auto-reply to chat history
                active_chats[chat_id]['messages'].append({
                    'type': 'text',
                    'text': reply,
                    'time': datetime.now(),
                    'direction': 'outgoing'
                })
                
                # Add to message queue for display
                message_queue.append({
                    'type': 'message',
                    'chat_id': chat_id,
                    'text': reply,
                    'name': "You",
                    'time': datetime.now()
                })
            break  # stop after first match

def send_message_with_timer(chat_id, text, is_image=False):
    """Send message with timer option and return message info"""
    try:
        if is_image:
            # Send image
            with open(text, 'rb') as f:
                photo_data = f.read()
            
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
            files = {'photo': (os.path.basename(text), BytesIO(photo_data))}
            data = {'chat_id': chat_id, 'caption': '📸 Photo'}
            
            response = requests.post(url, files=files, data=data)
            response_data = response.json()
            
            if response.status_code == 200:
                message_id = response_data['result']['message_id']
                # Add to chat history
                active_chats[chat_id]['messages'].append({
                    'type': 'image',
                    'filename': os.path.basename(text),
                    'time': datetime.now(),
                    'direction': 'outgoing',
                    'message_id': message_id,
                    'seen': False  # Track if message has been seen
                })
                return True, message_id
        else:
            # Send text message
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {'chat_id': chat_id, 'text': text}
            
            response = requests.post(url, data=data)
            response_data = response.json()
            
            if response.status_code == 200:
                message_id = response_data['result']['message_id']
                # Add to chat history
                active_chats[chat_id]['messages'].append({
                    'type': 'text',
                    'text': text,
                    'time': datetime.now(),
                    'direction': 'outgoing',
                    'message_id': message_id,
                    'seen': False  # Track if message has been seen
                })
                return True, message_id
        
        return False, None
        
    except Exception as e:
        print(f"Error sending message: {e}")
        return False, None

def delete_message_from_server(message_id, chat_id):
    """Delete message from Telegram server"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage"
        data = {'chat_id': chat_id, 'message_id': message_id}
        response = requests.post(url, data=data)
        return response.status_code == 200
    except:
        return False

def check_message_views(chat_id, message_id):
    """Check if a message has been viewed"""
    try:
        # This is a simplified approach - actual implementation may vary
        # based on Telegram API limitations for checking message views
        
        # For now, we'll use a placeholder that randomly returns True/False
        # In a real implementation, you might need to use message updates
        # or other Telegram API methods
        return random.choice([True, False])  # Placeholder
        
    except Exception as e:
        print(f"Error checking message views: {e}")
        return False

def check_seen_status():
    """Background thread to check if messages have been seen"""
    while True:
        for chat_id, chat in active_chats.items():
            for msg in chat['messages']:
                if msg['direction'] == 'outgoing' and not msg.get('seen', False) and msg.get('message_id'):
                    # Check if this message has been seen
                    if check_message_views(chat_id, msg.get('message_id')):
                        msg['seen'] = True
                        global refresh_needed
                        refresh_needed = True
        
        time.sleep(10)  # Check every 10 seconds

def process_deletions():
    """Process scheduled message deletions"""
    while True:
        current_time = time.time()
        to_remove = []
        
        for i, deletion in enumerate(pending_deletions):
            if current_time >= deletion['delete_time']:
                # Try to delete from server
                if deletion.get('message_id'):
                    delete_message_from_server(deletion['message_id'], deletion['chat_id'])
                
                # Delete from local history
                chat_id = deletion['chat_id']
                if chat_id in active_chats:
                    for msg in active_chats[chat_id]['messages']:
                        if (msg['direction'] == 'outgoing' and 
                            msg['type'] == deletion['message_type'] and
                            msg.get('filename') == deletion.get('filename')):
                            active_chats[chat_id]['messages'].remove(msg)
                            break
                
                to_remove.append(i)
                global refresh_needed
                refresh_needed = True
                print(f"Message deleted from chat {chat_id}")
        
        # Remove processed deletions
        for i in sorted(to_remove, reverse=True):
            if i < len(pending_deletions):
                pending_deletions.pop(i)
        
        time.sleep(1)  # Check every second

def process_message_queue():
    """Process and display incoming messages"""
    global refresh_needed, current_display
    
    while True:
        if message_queue:
            with console_lock:
                msg = message_queue.pop(0)
                timestamp = msg['time'].strftime("%H:%M:%S")
                
                if msg['type'] == 'message':
                    if current_display == "main":
                        # Show notification on main screen
                        print(f"\n[{timestamp}] New message from {msg['name']} (ID: {msg['chat_id']}):")
                        print(f"→ {msg['text']}")
                        print("\nEnter chat ID to reply or command:")
                    elif current_display == "ids":
                        # Show notification on IDs screen
                        print(f"\n[{timestamp}] New message from ID: {msg['chat_id']}:")
                        print(f"→ {msg['text']}")
                        print("\nType /back to return:")
                    elif current_display == "delete":
                        # Show notification on delete screen
                        print(f"\n[{timestamp}] New message from ID: {msg['chat_id']}:")
                        print(f"→ {msg['text']}")
                        print("\nEnter the number of chat to delete or /back to return:")
                    elif current_display == "settings":
                        # Show notification on settings screen
                        print(f"\n[{timestamp}] New message from ID: {msg['chat_id']}:")
                        print(f"→ {msg['text']}")
                        print("\nEnter option number to change or /back to return:")
                    elif isinstance(current_display, tuple) and current_display[0] == "dmsg":
                        # Show notification on delete message screen
                        print(f"\n[{timestamp}] New message from ID: {msg['chat_id']}:")
                        print(f"→ {msg['text']}")
                        print("\nEnter message number to delete, /all to delete all, or /back to return:")
                    else:
                        # If we're in a chat, show notification even if it's from another user
                        if current_display == msg['chat_id']:
                            # Message is from current chat
                            refresh_needed = True
                            print(f"\n[{timestamp}] New message from {msg['name']}:")
                            print(f"→ {msg['text']}")
                            print("\nType your message or command:")
                        else:
                            # Message is from another user
                            print(f"\n[{timestamp}] New message from {msg['name']} (ID: {msg['chat_id']}):")
                            print(f"→ {msg['text']}")
                            print("\nType your message or command:")
                
                elif msg['type'] == 'image':
                    if current_display == "main":
                        # Show image notification on main screen
                        print(f"\n[{timestamp}] 📸 New image from {msg['name']} (ID: {msg['chat_id']})")
                        print(f"→ Image saved as: {msg['filename']}")
                        display_image_notification(msg['local_path'], msg['name'])
                        print("\nEnter chat ID to reply or command:")
                    elif current_display == "ids":
                        # Show image notification on IDs screen
                        print(f"\n[{timestamp}] 📸 New image from ID: {msg['chat_id']}")
                        print(f"→ Image saved as: {msg['filename']}")
                        display_image_notification(msg['local_path'], f"ID: {msg['chat_id']}")
                        print("\nType /back to return:")
                    elif current_display == "delete":
                        # Show image notification on delete screen
                        print(f"\n[{timestamp}] 📸 New image from ID: {msg['chat_id']}")
                        print(f"→ Image saved as: {msg['filename']}")
                        display_image_notification(msg['local_path'], f"ID: {msg['chat_id']}")
                        print("\nEnter the number of chat to delete or /back to return:")
                    elif current_display == "settings":
                        # Show image notification on settings screen
                        print(f"\n[{timestamp}] 📸 New image from ID: {msg['chat_id']}")
                        print(f"→ Image saved as: {msg['filename']}")
                        display_image_notification(msg['local_path'], f"ID: {msg['chat_id']}")
                        print("\nEnter option number to change or /back to return:")
                    elif isinstance(current_display, tuple) and current_display[0] == "dmsg":
                        # Show image notification on delete message screen
                        print(f"\n[{timestamp}] 📸 New image from ID: {msg['chat_id']}")
                        print(f"→ Image saved as: {msg['filename']}")
                        display_image_notification(msg['local_path'], f"ID: {msg['chat_id']}")
                        print("\nEnter message number to delete, /all to delete all, or /back to return:")
                    else:
                        # If we're in a chat, show image notification
                        if current_display == msg['chat_id']:
                            # Image is from current chat
                            refresh_needed = True
                            print(f"\n[{timestamp}] 📸 New image from {msg['name']}:")
                            print(f"→ Image saved as: {msg['filename']}")
                            display_image_notification(msg['local_path'], msg['name'])
                            print("\nType your message or command:")
                        else:
                            # Image is from another user
                            print(f"\n[{timestamp}] 📸 New image from {msg['name']} (ID: {msg['chat_id']}):")
                            print(f"→ Image saved as: {msg['filename']}")
                            display_image_notification(msg['local_path'], msg['name'])
                            print("\nType your message or command:")
        
        # Check if we need to refresh the display
        if refresh_needed:
            if current_display == "main":
                display_main_interface()
            elif current_display == "ids":
                display_ids_only()
            elif current_display == "delete":
                delete_chat_interface()
            elif current_display == "settings":
                settings_interface()
            elif isinstance(current_display, tuple) and current_display[0] == "dmsg":
                delete_message_interface(current_display[1])
            else:
                display_chat_interface(current_display)
        
        time.sleep(0.5)  # Check for new messages every 0.5 seconds

def console_interface(app: Application):
    """Handle console input for replying to messages"""
    global current_display, refresh_needed, message_timer, auto_delete
    
    time.sleep(1)  # Wait for bot to initialize
    
    display_main_interface()
    current_display = "main"
    
    while True:
        try:
            # Check if we need to refresh due to new messages
            if refresh_needed:
                if current_display == "main":
                    display_main_interface()
                elif current_display == "ids":
                    display_ids_only()
                elif current_display == "delete":
                    delete_chat_interface()
                elif current_display == "settings":
                    settings_interface()
                elif isinstance(current_display, tuple) and current_display[0] == "dmsg":
                    delete_message_interface(current_display[1])
                else:
                    display_chat_interface(current_display)
            
            user_input = input().strip()
            
            if user_input.lower() == '/exit':
                print("Goodbye!")
                os._exit(0)
                
            elif user_input.lower() == '/refresh':
                if current_display == "main":
                    display_main_interface()
                elif current_display == "ids":
                    display_ids_only()
                elif current_display == "delete":
                    delete_chat_interface()
                elif current_display == "settings":
                    settings_interface()
                elif isinstance(current_display, tuple) and current_display[0] == "dmsg":
                    delete_message_interface(current_display[1])
                else:
                    display_chat_interface(current_display)
                continue
                
            elif user_input.lower() == '/clear':
                clear_console()
                if current_display == "main":
                    display_main_interface()
                elif current_display == "ids":
                    display_ids_only()
                elif current_display == "delete":
                    delete_chat_interface()
                elif current_display == "settings":
                    settings_interface()
                elif isinstance(current_display, tuple) and current_display[0] == "dmsg":
                    delete_message_interface(current_display[1])
                else:
                    display_chat_interface(current_display)
                continue
                
            elif user_input.lower() == '/back':
                if current_display != "main":
                    display_main_interface()
                    current_display = "main"
                continue
                
            elif user_input.lower() == '/ids':
                display_ids_only()
                current_display = "ids"
                continue
                
            elif user_input.lower() == '/delete':
                delete_chat_interface()
                current_display = "delete"
                continue
                
            elif user_input.lower() == '/settings':
                settings_interface()
                current_display = "settings"
                continue
                
            elif user_input.lower() == '/dmsg':
                if isinstance(current_display, int) and current_display in active_chats:
                    delete_message_interface(current_display)
                    current_display = ("dmsg", current_display)
                else:
                    print("You need to be in a chat to delete messages.")
                    time.sleep(1)
                    if current_display == "main":
                        display_main_interface()
                continue
                
            # Handle settings changes
            elif current_display == "settings" and user_input.isdigit():
                option = int(user_input)
                if option == 1:
                    try:
                        timer = int(input("Enter timer for images (seconds, 0 for no timer): "))
                        message_timer['image'] = max(0, timer)
                        print(f"Image timer set to {message_timer['image']} seconds")
                        time.sleep(1)
                    except:
                        print("Invalid input")
                        time.sleep(1)
                    settings_interface()
                elif option == 2:
                    try:
                        timer = int(input("Enter timer for messages (seconds, 0 for no timer): "))
                        message_timer['text'] = max(0, timer)
                        print(f"Message timer set to {message_timer['text']} seconds")
                        time.sleep(1)
                    except:
                        print("Invalid input")
                        time.sleep(1)
                    settings_interface()
                elif option == 3:
                    auto_delete = not auto_delete
                    print(f"Auto-delete {'enabled' if auto_delete else 'disabled'}")
                    time.sleep(1)
                    settings_interface()
                else:
                    print("Invalid option")
                    time.sleep(1)
                    settings_interface()
                continue
                    
            # Handle chat deletion
            elif current_display == "delete" and user_input.isdigit():
                chat_index = int(user_input)
                chat_ids = list(active_chats.keys())
                
                if 1 <= chat_index <= len(chat_ids):
                    chat_id_to_delete = chat_ids[chat_index - 1]
                    chat_name = active_chats[chat_id_to_delete]['name']
                    
                    # Confirmation
                    confirm = input(f"Are you sure you want to delete chat with {chat_name}? (y/N): ").strip().lower()
                    if confirm == 'y':
                        del active_chats[chat_id_to_delete]
                        print(f"Chat with {chat_name} (ID: {chat_id_to_delete}) has been deleted.")
                        time.sleep(2)
                        
                        display_main_interface()
                        current_display = "main"
                    else:
                        print("Deletion cancelled.")
                        time.sleep(1)
                        delete_chat_interface()
                else:
                    print("Invalid selection. Please try again.")
                    time.sleep(1)
                    delete_chat_interface()
                continue
                
            # Handle message deletion - FIXED SECTION
            elif isinstance(current_display, tuple) and current_display[0] == "dmsg":
                chat_id = current_display[1]
                
                if user_input.lower() == '/all':
                    # Delete all messages confirmation
                    confirm = input("Are you sure you want to delete ALL messages? (y/N): ").strip().lower()
                    if confirm == 'y':
                        active_chats[chat_id]['messages'] = []
                        print("All messages deleted.")
                        time.sleep(1)
                        display_chat_interface(chat_id)
                        current_display = chat_id
                    else:
                        print("Deletion cancelled.")
                        time.sleep(1)
                        delete_message_interface(chat_id)
                elif user_input.isdigit():
                    msg_index = int(user_input)
                    messages = active_chats[chat_id]['messages']
                    
                    if 1 <= msg_index <= len(messages):
                        # Delete single message
                        del messages[msg_index - 1]
                        print(f"Message {msg_index} deleted.")
                        time.sleep(1)
                        
                        if not messages:
                            display_chat_interface(chat_id)
                            current_display = chat_id
                        else:
                            delete_message_interface(chat_id)
                    else:
                        print("Invalid message number.")
                        time.sleep(1)
                        delete_message_interface(chat_id)
                elif user_input.lower() == '/back':
                    display_chat_interface(chat_id)
                    current_display = chat_id
                else:
                    print("Invalid command. Please enter a message number, /all, or /back")
                    time.sleep(1)
                    delete_message_interface(chat_id)
                continue
                    
            # Check if we're in the main screen and input is a chat ID
            elif current_display == "main" and user_input.isdigit():
                chat_id = int(user_input)
                if chat_id in active_chats:
                    display_chat_interface(chat_id)
                    current_display = chat_id
                else:
                    print("Chat ID not found. Use /refresh to see active chats.")
                    time.sleep(1)
                    display_main_interface()
                    
            # If we're in a chat conversation, handle message input
            elif isinstance(current_display, int) and current_display in active_chats:
                chat_id = current_display
                
                if user_input.lower() == '/delete':
                    # Delete current chat with confirmation
                    chat_name = active_chats[chat_id]['name']
                    confirm = input(f"Are you sure you want to delete chat with {chat_name}? (y/N): ").strip().lower()
                    if confirm == 'y':
                        del active_chats[chat_id]
                        print(f"Chat with {chat_name} has been deleted.")
                        time.sleep(2)
                        
                        display_main_interface()
                        current_display = "main"
                    else:
                        print("Deletion cancelled.")
                        time.sleep(1)
                        display_chat_interface(chat_id)
                    
                elif user_input.lower() == '/dmsg':
                    # Delete messages in current chat
                    delete_message_interface(chat_id)
                    current_display = ("dmsg", chat_id)
                    
                elif user_input.lower() == '/image':
                    image_path = input("Enter the path to the image: ").strip()
                    
                    if not os.path.exists(image_path):
                        print("File not found. Please check the path.")
                        time.sleep(1)
                        display_chat_interface(chat_id)
                        continue
                        
                    # Ask if user wants to set a timer
                    timer_choice = input("Set timer for this image? (y/N): ").strip().lower()
                    timer_seconds = 0
                    
                    if timer_choice == 'y':
                        try:
                            timer_seconds = int(input("Enter timer in seconds: "))
                            timer_seconds = max(0, timer_seconds)
                        except:
                            print("Invalid input, sending without timer")
                            timer_seconds = 0
                            time.sleep(1)
                    
                    # Send image with timer
                    success, message_id = send_message_with_timer(chat_id, image_path, is_image=True)
                    
                    if success:
                        print("Photo sent!")
                        
                        # Set timer for auto-delete if enabled
                        if timer_seconds > 0:
                            print(f"Photo will be deleted in {timer_seconds} seconds...")
                            
                            # Store message info for later deletion
                            message_info = {
                                'chat_id': chat_id,
                                'message_id': message_id,
                                'message_type': 'image',
                                'delete_time': time.time() + timer_seconds,
                                'filename': os.path.basename(image_path)
                            }
                            pending_deletions.append(message_info)
                        
                        time.sleep(1)
                        display_chat_interface(chat_id)
                    else:
                        print("Error sending photo.")
                        time.sleep(2)
                        display_chat_interface(chat_id)
                        
                elif user_input.lower() == '/timer':
                    try:
                        timer_type = input("Set timer for (1) images or (2) messages: ").strip()
                        timer_seconds = int(input("Enter timer in seconds (0 to disable): "))
                        
                        if timer_type == '1':
                            message_timer['image'] = max(0, timer_seconds)
                            print(f"Image timer set to {message_timer['image']} seconds")
                        else:
                            message_timer['text'] = max(0, timer_seconds)
                            print(f"Message timer set to {message_timer['text']} seconds")
                            
                        time.sleep(1)
                        display_chat_interface(chat_id)
                    except:
                        print("Invalid input")
                        time.sleep(1)
                        display_chat_interface(chat_id)
                        
                else:
                    # Ask if user wants to set a timer
                    timer_choice = input("Set timer for this message? (y/N): ").strip().lower()
                    timer_seconds = 0
                    
                    if timer_choice == 'y':
                        try:
                            timer_seconds = int(input("Enter timer in seconds: "))
                            timer_seconds = max(0, timer_seconds)
                        except:
                            print("Invalid input, sending without timer")
                            timer_seconds = 0
                            time.sleep(1)
                    
                    # Send text message with timer
                    success, message_id = send_message_with_timer(chat_id, user_input)
                    
                    if success:
                        print("Message sent!")
                        
                        # Set timer for auto-delete if enabled
                        if timer_seconds > 0:
                            print(f"Message will be deleted in {timer_seconds} seconds...")
                            
                            # Store message info for later deletion
                            message_info = {
                                'chat_id': chat_id,
                                'message_id': message_id,
                                'message_type': 'text',
                                'delete_time': time.time() + timer_seconds,
                                'text': user_input
                            }
                            pending_deletions.append(message_info)
                        
                        time.sleep(0.5)
                        display_chat_interface(chat_id)
                    else:
                        error_msg = "Error sending message"
                        print(error_msg)
                        time.sleep(2)
                        display_chat_interface(chat_id)
                
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2)
            if current_display == "main":
                display_main_interface()
            elif current_display == "ids":
                display_ids_only()
            elif current_display == "delete":
                delete_chat_interface()
            elif current_display == "settings":
                settings_interface()
            elif isinstance(current_display, tuple) and current_display[0] == "dmsg":
                delete_message_interface(current_display[1])
            else:
                display_chat_interface(current_display)

def main():
    # Initialize bot
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_message))
    
    print("Starting Telegram Messenger with advanced features...")
    
    # Create directory for downloaded images
    os.makedirs("downloaded_images", exist_ok=True)
    
    # Start message processing thread
    threading.Thread(target=process_message_queue, daemon=True).start()
    
    # Start seen status checking thread
    threading.Thread(target=check_seen_status, daemon=True).start()
    
    # Start deletion processing thread
    threading.Thread(target=process_deletions, daemon=True).start()
    
    # Start console interface in a separate thread
    threading.Thread(target=console_interface, args=(app,), daemon=True).start()
    
    # Start the bot
    app.run_polling()

if __name__ == "__main__":
    main()