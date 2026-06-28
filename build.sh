#!/bin/bash
set -e

echo "[*] Cleaning up old builds..."
rm -rf build dist TerminalChat.app TerminalChat.dmg TerminalChat.iconset TerminalChat.icns

echo "[*] Creating iconset..."
mkdir TerminalChat.iconset
# Place your custom logo here as logo.png
IMG="logo.png"

if [ ! -f "$IMG" ]; then
    echo "[!] ERROR: $IMG not found! Please place your logo in the mac_app folder."
    exit 1
fi

sips -s format png -s dpiWidth 72 -s dpiHeight 72 -z 16 16   $IMG --out TerminalChat.iconset/icon_16x16.png
sips -s format png -s dpiWidth 144 -s dpiHeight 144 -z 32 32   $IMG --out TerminalChat.iconset/icon_16x16@2x.png
sips -s format png -s dpiWidth 72 -s dpiHeight 72 -z 32 32   $IMG --out TerminalChat.iconset/icon_32x32.png
sips -s format png -s dpiWidth 144 -s dpiHeight 144 -z 64 64   $IMG --out TerminalChat.iconset/icon_32x32@2x.png
sips -s format png -s dpiWidth 72 -s dpiHeight 72 -z 128 128 $IMG --out TerminalChat.iconset/icon_128x128.png
sips -s format png -s dpiWidth 144 -s dpiHeight 144 -z 256 256 $IMG --out TerminalChat.iconset/icon_128x128@2x.png
sips -s format png -s dpiWidth 72 -s dpiHeight 72 -z 256 256 $IMG --out TerminalChat.iconset/icon_256x256.png
sips -s format png -s dpiWidth 144 -s dpiHeight 144 -z 512 512 $IMG --out TerminalChat.iconset/icon_256x256@2x.png
sips -s format png -s dpiWidth 72 -s dpiHeight 72 -z 512 512 $IMG --out TerminalChat.iconset/icon_512x512.png
sips -s format png -s dpiWidth 144 -s dpiHeight 144 -z 1024 1024 $IMG --out TerminalChat.iconset/icon_512x512@2x.png

iconutil -c icns TerminalChat.iconset
rm -rf TerminalChat.iconset

echo "[*] Building PyInstaller executable..."
# We use PyInstaller to package the python code so it runs without python installed on the target machine
source venv/bin/activate
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

# Apply the generated icns file
cp TerminalChat.icns TerminalChat.app/Contents/Resources/applet.icns

# Touch the app so macOS refreshes the icon cache
touch TerminalChat.app

echo "[*] Stripping Code Signature..."
# osacompile automatically ad-hoc signs the app bundle. 
# macOS Gatekeeper will flag any downloaded ad-hoc signed app as "Damaged". 
# By completely stripping the signature, we downgrade the error to "Unidentified Developer", 
# which users can easily bypass by Right-Clicking and selecting "Open".
codesign --remove-signature TerminalChat.app

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
