# Multi-method email notifications

Sometimes mail client notifications don't work very well. There is a script that checks the mailbox and sends notifications of new email messages via other services.

- Telegram
- Bark for iOS

## Configuration

This bot reads config from environment variables.

See `.env.example` for an example.

> By 'optional', I mean you still have to fill in the variable, just use some fake data.

### IMAP Settings (required)
- `IMAP_MAIL_SERVER`

	IMAP server address, typically looks like `imap.gmail.com` or `imap.mail.me.com`.

- `IMAP_MAIL_USERNAME`

	IMAP username, typically it looks like `user@example.com`, but sometimes it can be without @ (at) and domain like just `user`.

	Also note that, this user name may differ from the address that others can see when you send emails. For example, if you use iCloud custom domain email, your IMAP username is your original iCloud email address, not the custom domain email address.

- `IMAP_MAIL_PASSWORD`

	Password of the account. Some services require you to create an app specific password.

- `IMAP_MAIL_FOLDER`

	IMAP folder to check for new emails. Defaults to `INBOX`.

	You can list all folders with `python3 tools/list_folders.py`. The output will looks like this:
	```
	(\HasNoChildren) "/" "INBOX"
	(\HasChildren \Noselect) "/" "[Gmail]"
	(\HasNoChildren) "/" "&i6KWBQ-/AppTracker"
	...
	```
	You only need the last part of the folder name.
	In this case you set `IMAP_MAIL_FOLDER` to one of the following:
	```
	"INBOX"
	"[Gmail]"
	"&i6KWBQ-/AppTracker"
	```

### Telegram Settings (optional)
- `TELEGRAM_CHAT_ID`
- `TELEGRAM_BOT_TOKEN`

1. Find https://t.me/botfather bot in Telegram
2. Get API Token of the bot and set an environment variable `TELEGRAM_BOT_TOKEN`.
3. Get updates of the bot via the next link `https://api.telegram.org/bot<token>/getUpdates`. It will be empty, but `{ ok: true }`

4. You need to get chatId of the chat which the bot will send notifications. If you have a team I recommend using a group because it's easy to manage notification recipients simply by managing group members

>  - If you want to use bot with a group you should create a group with the bot. I noticed that when you add a second administrator to the group, *your group becomes a supergroup and changes Id*. I recommend adding a second administrator at once (this may be the bot itself). When the group is created, the bot is added and you have two or more administrators, for the next step you should write something to the group
>  - If you want to get notifications in personal chat with the bot you should write to bot directly

5. Get updates of the bot via the link `https://api.telegram.org/bot<token>/getUpdates` again. You can see your message with chat Id in the response. The group chat Id must be a negative number. If there is empty, you can write something to the group or remove the bot from the group and add it, then check the link again

6. Set the environment variable `TELEGRAM_CHAT_ID` with chat Id you get from the previous step

### Bark Settings (optional)
- `BARK_TOKEN`
- `BARK_SERVER` (optional)
- `BARK_ICON` (optional)
- `BARK_GROUP` (optional)

1. Install [Bark](https://apps.apple.com/us/app/bark-customed-notifications/id1403753865) on your iPhone/iPad.
2. Open the app and click the "Register" button.
3. Tap the cloud icon on the top right corner. Tap the server you want to use. Copy address and key.
4. Set variable `BARK_TOKEN` to key, and optionally `BARK_SERVER` to server.

## Run

- Run script for testing `python3 main.py`. Send some mails to your mailbox.

- Run script in background `python3 main.py &`.

- You can also use Docker to run the script. It's dead simple. Just pass all the environment variables to the container.
	
---

Typical problems
1. Users in a mail server can be without @ (at) and domain name
2. If Telegram is blocked in your country and you try to open getUpdates link or run the script on your computer it may not be work
3. Some services like Gmail block untrusted connections. You should check permissions if the script fails

