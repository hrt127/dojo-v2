#!/bin/bash
# Dojo v2 Complete Installer

set -e

echo ""
echo "⛄ Installing Dojo v2... 🌸"
echo ""

# Check if we're in dojo-cli directory
if [[ ! "$(basename "$PWD")" == "dojo-cli" ]]; then
    echo "Error: Please run this from ~/dojo-cli directory"
    echo "  cd ~/dojo-cli"
    echo "  ./install.sh"
    exit 1
fi

# Backup existing dojo if it exists and is not already backed up
if [ -f "dojo" ] && [ ! -f "dojo-old" ]; then
    echo "✓ Backing up existing dojo to dojo-old"
    mv dojo dojo-old
fi

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found. Please install Python 3."
    exit 1
fi

echo "✓ Python 3 found"

# Check if lib directory exists
if [ ! -d "lib" ]; then
    echo "Error: lib/ directory not found. Make sure all files were downloaded."
    exit 1
fi

echo "✓ Found lib/ directory with modules"

# Install rich
echo "✓ Installing rich library..."
if pip install --break-system-packages rich 2>/dev/null || pip3 install --break-system-packages rich 2>/dev/null; then
    echo "✓ Rich installed successfully"
else
    echo "⚠  Could not install rich. You may need to run:"
    echo "   pip install --break-system-packages rich"
fi

# Make dojo2 executable
if [ -f "dojo2" ]; then
    chmod +x dojo2
    echo "✓ Made dojo2 executable"
else
    echo "Error: dojo2 script not found"
    exit 1
fi

# Create config directory
mkdir -p ~/.config/dojo
echo "✓ Created config directory"

echo ""
echo "🎉 Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Run setup:  ./dojo2 wizard"
echo "  2. Or start:   ./dojo2"
echo "  3. Learn:      ./dojo2 tutorial"
echo ""
echo "Features:"
echo "  • Interactive numbered menus"
echo "  • Learning mode (explains commands)"
echo "  • Fuzzy search (goto)"
echo "  • Health checks & auto-fixes"
echo "  • Migration tool (optional)"
echo ""
echo "Both 'dojo' (old) and 'dojo2' (new) work side-by-side!"
echo "When ready: mv dojo2 dojo"
echo ""
