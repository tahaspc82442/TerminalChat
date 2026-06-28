<div align="center">
  <img src="logo.png" alt="TerminalChat Logo" width="128" />
  <h1>TerminalChat</h1>
  <p><strong>The Hacker Terminal for Instagram DMs. Combat Brainrot. Escape the Reels.</strong></p>

  <p>
    <a href="#features">Features</a> •
    <a href="#why-terminalchat">Why?</a> •
    <a href="#installation">Installation</a> •
    <a href="#usage">Usage</a>
  </p>
</div>

<br/>

<div align="center">
  <img src="images/demo.gif" alt="TerminalChat Screenshot" width="800" />
</div>

## 🧠 Why TerminalChat?

Instagram is designed to hijack your attention. You log in to reply to a single DM from a friend, and suddenly you're scrolling through 45 minutes of mindless Reels, brainrot, and algorithms designed to keep you trapped.

**TerminalChat** is the antidote. It strips away the UI, the addictive feeds, the explore page, and the infinite scrolling. It transforms your Instagram DMs into a pure, distraction-free, 1990s-style hacker terminal CLI. 

Read your messages. Reply to your friends. Get out. Stay focused.

## 🚀 Features

- **Matrix Aesthetics**: Immerse yourself in a beautifully styled, green-on-black terminal environment complete with blinking block cursors and typewriter text effects.
- **Zero Distractions**: No reels. No stories. No explore page. Just you and your chats.
- **Live Sync**: Uses an invisible headless browser (Playwright) to instantly route your messages in real-time.
- **Privacy First**: Everything runs entirely on your local machine. No middleman servers, no data scraping.
- **Mac Native**: Packaged as a lightweight, plug-and-play `.dmg` macOS application.

## 🛠 Installation

Because this is a pure hacker tool, you can install it instantly via the command line (just like `npm` or `brew`) without dealing with macOS DMG warnings or Gatekeeper!

Open your Terminal and run:

```bash
curl -sL https://raw.githubusercontent.com/tahaspc82442/TerminalChat/main/install.sh | bash
```

The script will automatically:
1. Clone the repository into a hidden folder (`~/.terminalchat`)
2. Create an isolated environment
3. Install the stealth browser engine
4. Create a global `terminalchat` command on your Mac

Once finished, simply type:
```bash
terminalchat
```
...and you're in. 

*(If you get a "command not found" error, the installer will print a single `export PATH` line for you to copy into your `~/.zshrc`).*

## 💻 Usage

Once booted, the terminal is entirely command-driven. 

- View your inbox and active chats
- Select a target to initiate a secure message stream
- Type `/inbox` at any time to return to the main menu
- Press `Ctrl+C` to terminate the connection

---

<div align="center">
  <i>"Disconnect from the feed. Reconnect with reality."</i>
</div>
