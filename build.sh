#!/bin/bash
set -e

echo "[*] Cleaning up old builds..."
rm -rf build dist TerminalChat.app TerminalChat.dmg TerminalChat.iconset TerminalChat.icns

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
    pip install -r requirements.txt pillow
    playwright install chromium
else
    source venv/bin/activate
    pip install pillow
fi

# Place your custom logo here as logo.png
IMG="logo.png"
if [ ! -f "$IMG" ]; then
    echo "[!] ERROR: $IMG not found! Please place your logo in the mac_app folder."
    exit 1
fi

echo "[*] Sanitizing logo with Pillow..."
cat << 'EOF' > fix_icon.py
import sys
from PIL import Image
try:
    img = Image.open(sys.argv[1]).convert('RGBA')
    img = img.resize((1024, 1024), Image.Resampling.LANCZOS)
    img.save('clean_logo.png', format='PNG', dpi=(72, 72))
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
EOF
python3 fix_icon.py "$IMG"
rm fix_icon.py

echo "[*] Creating iconset..."
mkdir TerminalChat.iconset
sips -s format png -z 16 16   clean_logo.png --out TerminalChat.iconset/icon_16x16.png
sips -s format png -z 32 32   clean_logo.png --out TerminalChat.iconset/icon_16x16@2x.png
sips -s format png -z 32 32   clean_logo.png --out TerminalChat.iconset/icon_32x32.png
sips -s format png -z 64 64   clean_logo.png --out TerminalChat.iconset/icon_32x32@2x.png
sips -s format png -z 128 128 clean_logo.png --out TerminalChat.iconset/icon_128x128.png
sips -s format png -z 256 256 clean_logo.png --out TerminalChat.iconset/icon_128x128@2x.png
sips -s format png -z 256 256 clean_logo.png --out TerminalChat.iconset/icon_256x256.png
sips -s format png -z 512 512 clean_logo.png --out TerminalChat.iconset/icon_256x256@2x.png
sips -s format png -z 512 512 clean_logo.png --out TerminalChat.iconset/icon_512x512.png
sips -s format png -z 1024 1024 clean_logo.png --out TerminalChat.iconset/icon_512x512@2x.png
iconutil -c icns TerminalChat.iconset
rm -rf TerminalChat.iconset clean_logo.png

echo "[*] Building PyInstaller executable..."
pip install pyinstaller
pyinstaller --onefile --name cli_engine --collect-all playwright_stealth cli.py

echo "[*] Creating AppleScript App Bundle..."
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
mv dist/cli_engine TerminalChat.app/Contents/Resources/
cp TerminalChat.icns TerminalChat.app/Contents/Resources/applet.icns

# Touch the app so macOS refreshes the icon cache
touch TerminalChat.app

echo "[*] Code signing App Bundle..."
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
