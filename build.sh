#!/bin/bash
set -e

echo "[*] Cleaning up old builds..."
rm -rf build dist TerminalChat.app TerminalChat.dmg TerminalChat.iconset TerminalChat.icns

echo "[*] Downloading icon injector..."
curl -sL https://raw.githubusercontent.com/mklement0/fileicon/master/bin/fileicon > fileicon
chmod +x fileicon

# Place your custom logo here as logo.png
IMG="logo.png"

if [ ! -f "$IMG" ]; then
    echo "[!] ERROR: $IMG not found! Please place your logo in the mac_app folder."
    exit 1
fi

echo "[*] Building PyInstaller executable..."
# Ensure Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[!] ERROR: python3 is not installed."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "[*] Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "[*] Installing dependencies..."
    pip install -r requirements.txt
    playwright install chromium
else
    source venv/bin/activate
fi
pip install pyinstaller
pyinstaller --onefile --name cli_engine --collect-all playwright_stealth cli.py

echo "[*] Creating AppleScript App Bundle..."
# We create an AppleScript that opens Terminal and runs our bundled executable
cat << 'EOF' > launcher.applescript
set bundlePath to POSIX path of (path to me)
set exePath to bundlePath & "Contents/Resources/cli_engine"
tell application "Terminal"
    activate
    do script ("'" & exePath & "'")
end tell
EOF

osacompile -o TerminalChat.app launcher.applescript
rm launcher.applescript

echo "[*] Injecting payload into App Bundle..."
# Move the compiled python binary into the App's Resources folder so the AppleScript can find it
mv dist/cli_engine TerminalChat.app/Contents/Resources/

# Use the downloaded swift-based utility to forcefully set the native macOS app icon
echo "[*] Applying custom icon to app bundle..."
./fileicon set TerminalChat.app "$IMG"

# Touch the app so macOS refreshes the icon cache
touch TerminalChat.app

echo "[*] Code signing App Bundle..."
# We must re-sign the app bundle because adding the custom executable and icon broke the original signature!
# Without this, macOS Gatekeeper will say the app is "damaged and should be moved to trash"
codesign --force --deep --sign - TerminalChat.app

echo "[*] Creating DMG..."
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Create a folder for the DMG contents
mkdir dmg_folder
mv TerminalChat.app dmg_folder/
# Create a symlink to /Applications so users can drag-and-drop
ln -s /Applications dmg_folder/Applications

# Force macOS to bust the icon cache by giving the volume a unique name
hdiutil create -volname "TerminalChat_${TIMESTAMP}" -srcfolder dmg_folder -ov -format UDZO TerminalChat.dmg
rm -rf dmg_folder

echo "[*] Moving DMG to Releases Folder..."
mkdir -p ~/Desktop/TerminalChat_Releases
cp TerminalChat.dmg ~/Desktop/TerminalChat_Releases/TerminalChat_v1.0_${TIMESTAMP}.dmg

echo "[+] SUCCESS! TerminalChat_v1.0_${TIMESTAMP}.dmg is in ~/Desktop/TerminalChat_Releases/"
