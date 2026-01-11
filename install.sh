#!/bin/bash
# Dojo v2 Quick Installer

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

# Install rich
echo "✓ Installing rich library..."
pip install -q rich || pip3 install -q rich

# Make dojo2 executable
if [ -f "dojo2" ]; then
    chmod +x dojo2
    echo "✓ Made dojo2 executable"
fi

# Create config directory
mkdir -p ~/.config/dojo
echo "✓ Created config directory"

echo ""
echo "🎉 Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Test it:    ./dojo2"
echo "  2. Try:        ./dojo2 recent"
echo "  3. When ready: mv dojo2 dojo"
echo ""
echo "Both 'dojo' (old) and 'dojo2' (new) work side-by-side!"
echo ""
