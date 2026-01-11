# ⛄ Dojo v2 - Your Dev Home 🌸

> Simple, helpful, learns with you

A modern, interactive CLI for managing your development workspace with soft snowzies colors.

## ✨ Features

- **Context-Aware**: Auto-detects project type (Next.js, Python, Streamlit, etc.)
- **Interactive Dashboard**: Just type `dojo` for a helpful menu
- **Fuzzy Search**: `dojo goto intel` finds `farcaster-intel`
- **Recent Projects**: Tracks what you work on with timestamps
- **Health Checks**: Check git/python/node across all projects at once
- **Auto-Fix**: Can automatically fix common issues
- **Colorful**: Soft pink/purple/mint theme that's easy on the eyes

## 🚀 Quick Install

```bash
cd ~/dojo-cli
git clone https://github.com/hrt127/dojo-v2.git .
pip install rich
chmod +x dojo2
./dojo2
```

## 📚 Commands

### Quick Actions
- `dojo dev` - Start development (auto-detects: npm/python/streamlit)
- `dojo code` - Open in VS Code
- `dojo open` - Open in file explorer

### Navigation
- `dojo goto <name>` - Jump to project (fuzzy search)
- `dojo recent` - Show recent projects
- `dojo ls [apps|bots|tools]` - List projects
- `dojo where` - Where am I? What can I do?

### Health & Maintenance
- `dojo health` - Check git/python/node across all projects
- `dojo sync` - Pull all git repos
- `dojo clean` - Remove build artifacts (interactive)

### Learning
- `dojo tutorial` - Interactive walkthrough
- `dojo examples` - Common workflows
- `dojo help` - Full command list

## 🎨 Color Theme

Soft snowzies palette:
- Soft Pink (#FFB7C5) - Headers
- Light Purple (#C8A2C8) - Accents
- Mint (#A8E6CF) - Success
- Peach (#FFD3B6) - Warnings
- Snow White (#E0E6ED) - Text

## 📁 Structure

```
dojo-v2/
├── dojo2              # Main CLI script
├── lib/
│   ├── context.py    # Project detection
│   ├── navigator.py  # Navigation commands
│   ├── health.py     # Health checks
│   └── ui.py         # Dashboard & themes
└── README.md
```

## 🔧 Migration from Old Dojo

1. Backup: `mv dojo dojo-old`
2. Install dojo v2 (see above)
3. Test: `./dojo2`
4. When ready: `mv dojo2 dojo`

Both versions work side-by-side!

## 🎓 Examples

**Start working on a project:**
```bash
dojo recent              # See what you worked on
dojo goto ops            # Jump to ops-home
dojo dev                 # Start dev server
```

**Check everything is healthy:**
```bash
dojo health             # Run all checks
# Choose 'y' to auto-fix issues
```

**Clean up space:**
```bash
dojo clean              # Preview what will be deleted
dojo clean --deep       # Also remove node_modules
```

---

Made with ⛄🌸 by [@snowziesk](https://github.com/hrt127)
