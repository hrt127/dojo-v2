# ⛄ Dojo v2 - Your Dev Home 🌸

> Progressive, context-aware CLI that learns with you

A modern, intelligent CLI for managing your development workspace. Designed with progressive disclosure, learning mode, and fuzzy search.

## ✨ Key Features

### 🧠 Smart & Context-Aware
- **Auto-detects project type**: Next.js, Python, Streamlit, Foundry, etc.
- **Shows relevant commands**: Only see what you can do HERE
- **Git-aware**: Displays sync status, branch info
- **Learning mode**: Explains every command as you use it

### 🎯 Interactive & Simple
- **Numbered menus**: Just type a number instead of commands
- **Fuzzy search**: `dojo goto intel` finds `farcaster-intel`
- **Recent tracking**: Remembers what you work on
- **Setup wizard**: Guides new users through setup

### 🔧 Powerful Maintenance
- **Health checks**: Check git/python/node across all projects
- **Auto-fix**: Can automatically fix common issues
- **Smart sync**: Pull all repos at once
- **Clean builds**: Interactive cleanup with preview

### 🌸 Beautiful UI
- **Soft snowzies theme**: Pink/purple/mint colors
- **Progressive disclosure**: Show 5-10 commands, not 50
- **Helpful tips**: Contextual guidance

## 🚀 Quick Install

```bash
cd ~/dojo-cli

# Clone from GitHub
git clone https://github.com/hrt127/dojo-v2.git temp
mv temp/* .
rm -rf temp

# Install dependency
pip install --break-system-packages rich

# Make executable
chmod +x dojo2

# Try it!
./dojo2
```

## 🎓 First Time Setup

```bash
# Run the setup wizard
./dojo2 wizard

# Or manually enable learning mode
./dojo2 learn on

# Take the interactive tutorial
./dojo2 tutorial
```

## 📚 Commands

### Interactive Menu (Just type `dojo`)

```bash
dojo
# Shows numbered menu with:
# - Quick actions for current project
# - Navigation options
# - Utils
# - Learning resources
# Just type a number to run!
```

### Quick Actions

```bash
dojo dev [project]        # Start dev (auto-detects: npm/python/streamlit)
dojo code [project]       # Open in VS Code
dojo open [project]       # Open in file explorer
dojo quick <project>      # Smart: goto + run most common action
```

### Navigation

```bash
dojo goto <name>          # Fuzzy search jump ("ops" finds "ops-home")
dojo recent               # Recent projects with timestamps
dojo ls [category]        # List: apps, bots, tools, contracts
dojo where                # Where am I? What can I do?
```

### Health & Maintenance

```bash
dojo health               # Check git/python/node everywhere
dojo fix all              # Auto-fix issues
dojo sync                 # Pull all git repos
dojo clean [--deep]       # Remove build artifacts (interactive)
```

### Learning & Config

```bash
dojo tutorial             # Interactive walkthrough
dojo examples             # Common workflow examples  
dojo wizard               # Setup wizard for new users
dojo learn [on|off]       # Toggle learning mode
dojo config               # Show current config
dojo config set <k> <v>   # Update config
```

### Migration (Optional)

```bash
# Migrate from old structure (apps/bots) to new (work/lab/research)
dojo migrate              # Preview migration
dojo migrate --execute    # Perform migration
dojo migrate --rollback   # Undo migration
```

## 📚 Learning Mode

Enable learning mode to see explanations for every command:

```bash
dojo learn on

# Now when you run commands:
dojo dev

# You'll see:
# 💡 LEARNING MODE
# This will:
#   • Navigate to your project
#   • Check if dependencies are installed
#   • Run 'npm run dev' to start the server
#   • Open http://localhost:3000
# 
# Command: npm run dev
# Continue? [Y/n]
```

Perfect for learning the CLI or understanding what each command does!

## 📁 Folder Structure

### Current Structure (Legacy)
```
~/dojo/
├── apps/              # Applications
├── bots/              # Trading bots
├── tools/             # Utilities
├── contracts/         # Smart contracts
├── experiments/       # Learning
├── protocols/         # Research
└── archive/           # Old stuff
```

### New Structure (Optional Migration)
```
~/dojo/
├── work/              # Active development
│   ├── apps/
│   ├── bots/
│   ├── tools/
│   └── contracts/
├── lab/               # Experiments & learning
├── research/          # Knowledge & analysis
│   ├── defi/
│   └── strategies/
└── resources/         # Static assets
```

Use `dojo migrate` to upgrade (with rollback support)!

## 🎯 Examples

### Start Working on a Project
```bash
dojo recent              # See what you worked on
# Pick a number or:
dojo goto ops            # Jump to ops-home
dojo dev                 # Start dev server
```

### Health Check Everything
```bash
dojo health
# Checks:
# ✓ Git: 12/14 repos synced
# ⚠  Python: 1 venv missing
# ✓ Node: 8 projects healthy
#
# Run automated fixes? [y/N]
```

### Clean Up Space
```bash
dojo clean
# Found 15 items (2.3 GB)
#   apps/ops-home/node_modules (842 MB)
#   bots/intel/__pycache__ (12 MB)
#   ...
# Delete these files? [y/N]

dojo clean --deep       # Also removes node_modules
```

### Interactive Dashboard
```bash
dojo

# ⛄ dojo v2 🌸
# Your dev home
#
# 📍 apps/ops-home
# 📦 NEXTJS
# ✓ main (synced)
#
# QUICK ACTIONS
#  1  dev              Start dev server
#  2  build            Build for production
#  3  test             Run test suite
#
# NAVIGATE
#  4  goto             Jump to project
#  5  recent           Recent projects
#  6  ls               List all projects
# ...
#
# Type a number or command ❯
```

## 🔧 Technical Details

### Dependencies
- Python 3.8+
- `rich` - Beautiful terminal UI

### File Structure
```
dojo-v2/
├── dojo2              # Main CLI script
├── lib/
│   ├── context.py    # Project detection & config
│   ├── navigator.py  # goto, ls, recent commands
│   ├── health.py     # Health checks & fixes
│   ├── ui.py         # Dashboard & themes
│   └── migrate.py    # Folder structure migration
└── README.md

~/.config/dojo/
├── config.json        # User preferences
├── history.json       # Recent projects & commands
└── migration_backup.json  # Migration rollback data
```

### Configuration

Config stored in `~/.config/dojo/config.json`:
```json
{
  "learning_mode": false,
  "version": "v2",
  "theme": "snowzies",
  "auto_open_browser": true
}
```

### History Tracking

Automatically tracks:
- Recent projects (last 20)
- Visit counts per project
- Command history (last 100)
- Timestamps for everything

## 🔄 Migration from Old Dojo

### Side-by-Side (Recommended)
```bash
# Both work together!
mv dojo dojo-old         # Backup old bash script
# Install dojo2 (see above)
./dojo2                  # Try the new one
dojo-old map             # Old one still works
```

### Full Replacement
```bash
# After testing dojo2:
mv dojo2 dojo
# Your .bashrc stays unchanged!
```

## 🎨 Design Philosophy

1. **Progressive Disclosure**: Show 5-10 commands initially, not 50
2. **Context-Aware**: Only show relevant commands for current location
3. **Learning by Doing**: Explain as you use, not before
4. **Smart Defaults**: Commands work without arguments when possible
5. **Fuzzy Everything**: Partial names work everywhere

## 🐛 Troubleshooting

### Rich library not found
```bash
pip install --break-system-packages rich
```

### Commands not working
```bash
chmod +x dojo2           # Make sure it's executable
./dojo2 --version        # Test basic functionality
```

### Reset config
```bash
rm -rf ~/.config/dojo
./dojo2 wizard           # Re-run setup
```

## 💬 Feedback & Contributing

This is your personal CLI! Customize it:
- Fork the repo
- Modify colors in `lib/ui.py` (THEME)
- Add commands in `dojo2` main script
- Adjust folder mappings in `lib/migrate.py`

---

**Made with ⛄🌸 by [@snowziesk](https://github.com/hrt127)**

*Progressive CLI design inspired by modern UX principles*
