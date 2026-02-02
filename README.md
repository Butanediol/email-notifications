# Multi-method email notifications

Sometimes mail client notifications don't work very well. There is a script that checks the mailbox and sends notifications of new email messages via other services.

## Supported Senders

- Telegram
- Bark for iOS

Senders are implemented as plugins and are automatically discovered and enabled based on your configuration.

## Configuration

This bot reads config from environment variables.

See `.env.example` for an example.

Senders are **automatically enabled** when their required environment variables are set. You only need to configure the senders you want to use.

### General Settings

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `INTERVAL` | No | `30` | Check interval in seconds |
| `LOG_LEVEL` | No | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

### IMAP Settings (required)

| Variable | Required | Description |
|----------|----------|-------------|
| `IMAP_MAIL_SERVER` | Yes | IMAP server address (e.g., `imap.gmail.com`, `imap.mail.me.com`) |
| `IMAP_MAIL_USERNAME` | Yes | IMAP username (typically `user@example.com`, sometimes just `user`) |
| `IMAP_MAIL_PASSWORD` | Yes | Account password (some services require an app-specific password) |
| `IMAP_MAIL_FOLDER` | No | Folder to check (default: `INBOX`) |

> Note: IMAP username may differ from the address others see when you send emails. For example, iCloud custom domain email users should use their original iCloud email address.

To list available folders:
```bash
python tools/list_folders.py
```

### Telegram Settings

**Required variables:** `TELEGRAM_CHAT_ID`, `TELEGRAM_BOT_TOKEN`

When both are set, the Telegram sender is automatically enabled.

<details>
<summary>Setup instructions</summary>

1. Find [@BotFather](https://t.me/botfather) in Telegram
2. Create a bot and copy the API token → set as `TELEGRAM_BOT_TOKEN`
3. Get your chat ID:
   - For personal notifications: send a message to your bot
   - For group notifications: add the bot to a group and send a message
4. Visit `https://api.telegram.org/bot<token>/getUpdates` to find the chat ID
5. Set `TELEGRAM_CHAT_ID` (group IDs are negative numbers)

> Tip: When creating a group, add a second administrator immediately to prevent the group ID from changing when it becomes a supergroup.

</details>

### Bark Settings (iOS)

**Required variables:** `BARK_TOKEN`

When set, the Bark sender is automatically enabled.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BARK_TOKEN` | Yes | - | Your Bark device key |
| `BARK_SERVER` | No | `https://api.day.app` | Bark server URL |
| `BARK_GROUP` | No | `Email` | Notification group name |
| `BARK_ICON` | No | (default icon) | Custom notification icon URL |

<details>
<summary>Setup instructions</summary>

1. Install [Bark](https://apps.apple.com/us/app/bark-customed-notifications/id1403753865) on your iPhone/iPad
2. Open the app and register the device
3. Tap the cloud icon → select a server → copy the key
4. Set `BARK_TOKEN` to the key

</details>

## Usage

### Running directly

```bash
# Install dependencies
pip install -r requirements.txt

# Run the script
python main.py
```

### Running with Docker

```bash
docker run -d \
  -e IMAP_MAIL_SERVER=imap.gmail.com \
  -e IMAP_MAIL_USERNAME=you@gmail.com \
  -e IMAP_MAIL_PASSWORD=your-app-password \
  -e TELEGRAM_BOT_TOKEN=your-token \
  -e TELEGRAM_CHAT_ID=your-chat-id \
  ghcr.io/butanediol/email-notifications
```

### Testing your configuration

Test that your senders are working without needing real emails:

```bash
python tools/test_sender.py

# With custom message
python tools/test_sender.py --from "alice@example.com" --to "bob@example.com" --subject "Hello" --body "Test body"
```

## Creating Custom Senders

Senders are plugins that are automatically discovered. To create a new sender:

1. Create a new file in the `Senders/` directory (e.g., `Senders/my_sender.py`)
2. Implement a class that extends `BaseSender`:

```python
from Senders.base import BaseSender
from email.message import Message
from os import environ

class MySender(BaseSender):

    @classmethod
    def enabled(cls) -> bool:
        # Return True when required env vars are set
        return 'MY_SENDER_TOKEN' in environ

    def send(self, message: Message):
        # Send the notification
        pass
```

The sender will be automatically discovered and enabled when `enabled()` returns `True`.

---

## Troubleshooting

1. **Authentication issues**: Some providers (like Gmail) require app-specific passwords
2. **Telegram blocked**: If Telegram is blocked in your region, the script may fail to send notifications
3. **No senders enabled**: Check that required environment variables are set. Run `python tools/test_sender.py` to verify
