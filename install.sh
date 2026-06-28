#!/bin/bash
set -e

echo "[*] Initializing hacker environment..."
INSTALL_DIR="$HOME/.terminalchat"

if [ -d "$INSTALL_DIR" ]; then
    echo "[*] Updating existing installation..."
    cd "$INSTALL_DIR"
    git pull origin main
else
    echo "[*] Cloning TerminalChat repository..."
    git clone https://github.com/tahaspc82442/TerminalChat.git "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"

# Ensure Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[!] ERROR: python3 is not installed. Please install Python 3 and try again."
    exit 1
fi

echo "[*] Setting up isolated virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

echo "[*] Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
echo "[*] Installing stealth browser engine..."
playwright install chromium > /dev/null 2>&1

echo "[*] Creating global executable command..."
# Create a wrapper script in a directory that is likely in the user's PATH
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"

WRAPPER_SCRIPT="$BIN_DIR/terminalchat"
cat << EOF > "$WRAPPER_SCRIPT"
#!/bin/bash
# Wrapper to launch TerminalChat from anywhere
cd "$INSTALL_DIR"
source venv/bin/activate
exec python3 cli.py "\$@"
EOF

chmod +x "$WRAPPER_SCRIPT"

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo ""
    echo "[!] IMPORTANT: $BIN_DIR is not in your PATH."
    echo "To run 'terminalchat' from anywhere, add this line to your ~/.zshrc or ~/.bash_profile:"
    echo "export PATH=\"\$PATH:$BIN_DIR\""
    echo ""
    echo "Then run: source ~/.zshrc"
else
    echo ""
    echo "[+] SUCCESS! TerminalChat is installed globally."
    echo "[+] Type 'terminalchat' anywhere in your terminal to begin."
fi
