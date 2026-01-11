"""
UI - Enhanced with interactive menus, learning mode, wizard
"""

from rich.console import Console
from rich.theme import Theme
from rich.table import Table
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text

THEME = Theme({
    "header": "bold #FFB7C5",
    "accent": "#C8A2C8",
    "text": "#E0E6ED",
    "success": "#A8E6CF",
    "warning": "#FFD3B6",
    "error": "bold #FF8BA7",
    "dim": "#6B7280",
    "path": "cyan",
})

class UI:
    def __init__(self, ctx):
        self.ctx = ctx
        self.console = Console(theme=THEME)
    
    def show_header(self):
        self.console.print()
        self.console.print(" ⛄ ", style="header", end="")
        self.console.print("dojo v2", style="header bold", end="")
        self.console.print(" 🌸", style="header")
        self.console.print(" Your dev home\n", style="dim")
    
    def show_dashboard(self):
        """Interactive numbered dashboard"""
        self.show_header()
        
        # Location info
        if self.ctx.is_in_dojo():
            location = str(self.ctx.cwd.relative_to(self.ctx.dojo_root))
            self.console.print(f" 📍 [path]{location}[/]")
            if self.ctx.project_type != 'folder':
                self.console.print(f" 📦 {self.ctx.project_type}", style="dim")
            if self.ctx.in_git_repo:
                self.console.print(" 🌿 [dim]git repo[/]")
            self.console.print()
        else:
            self.console.print(f" 📍 [path]{self.ctx.cwd}[/]")
            self.console.print(" [dim](outside dojo)\n")
        
        # Build numbered menu
        menu_items = []
        num = 1
        
        # Quick actions for current context
        quick_actions = self.ctx.get_quick_actions()
        if quick_actions:
            menu_items.append((None, "[accent]QUICK ACTIONS[/]", None))
            for cmd, desc, _ in quick_actions[:3]:
                menu_items.append((num, cmd, desc))
                num += 1
            menu_items.append((None, "", None))
        
        # Navigation
        menu_items.append((None, "[accent]NAVIGATE[/]", None))
        nav_commands = [
            ("goto", "Jump to project (fuzzy search)"),
            ("recent", "Recent projects (last 7 days)"),
            ("ls", "List: apps, bots, tools"),
            ("fav", "Favorites"),
        ]
        for cmd, desc in nav_commands:
            menu_items.append((num, cmd, desc))
            num += 1
        menu_items.append((None, "", None))
        
        # Utilities
        menu_items.append((None, "[accent]UTILS[/]", None))
        util_commands = [
            ("code", "Open in VS Code"),
            ("health", "Check git/python/node"),
            ("clean", "Clean build files"),
        ]
        for cmd, desc in util_commands:
            menu_items.append((num, cmd, desc))
            num += 1
        menu_items.append((None, "", None))
        
        # Learning
        menu_items.append((None, "[accent]LEARN[/]", None))
        learn_commands = [
            ("wizard", "Setup wizard for beginners"),
            ("tutorial", "Interactive walkthrough"),
            ("examples", "Common workflows"),
        ]
        for cmd, desc in learn_commands:
            menu_items.append((num, cmd, desc))
            num += 1
        
        # Display menu
        table = Table.grid(padding=(0, 2), pad_edge=False)
        table.add_column(style="accent", justify="right", width=3)
        table.add_column(style="text")
        table.add_column(style="dim")
        
        for number, cmd, desc in menu_items:
            if number is None:
                table.add_row("", cmd or "", desc or "")
            else:
                table.add_row(str(number), cmd, desc)
        
        self.console.print(table)
        self.console.print()
        
        # Learning mode indicator
        if self.ctx.learning_mode:
            self.console.print(" [success]💡 Learning mode: ON[/] [dim](explains as you go)[/]\n")
        
        # Interactive prompt
        choice = Prompt.ask(" [accent]❯[/]", default="help")
        
        # Handle choice
        self._handle_dashboard_choice(choice, menu_items)
    
    def _handle_dashboard_choice(self, choice, menu_items):
        """Handle user choice from dashboard"""
        # Try to parse as number
        try:
            num = int(choice)
            # Find command for this number
            for n, cmd, _ in menu_items:
                if n == num and cmd:
                    self.console.print(f"\n [dim]Running: dojo {cmd}[/]\n")
                    # Execute command (would integrate with main CLI)
                    return
        except ValueError:
            pass
        
        # Handle as command
        if choice in ['help', 'h', '?']:
            self.show_help()
        elif choice == 'wizard':
            self.show_wizard()
        else:
            self.console.print(f" [dim]Try typing the full command: dojo {choice}[/]\n")
    
    def show_help(self):
        """Context-aware help"""
        self.show_header()
        
        if self.ctx.is_in_dojo():
            location = str(self.ctx.cwd.relative_to(self.ctx.dojo_root))
            self.console.print(f" 📍 [dim]{location}[/]")
            if self.ctx.project_type != 'folder':
                self.console.print(f" 📦 [dim]{self.ctx.project_type}[/]")
            self.console.print()
        
        sections = [
            {
                "icon": "🚀",
                "title": "QUICK ACTIONS",
                "commands": [
                    ("dev [project]", "Start development (auto-detects type)"),
                    ("code [project]", "Open in VS Code"),
                    ("open [project]", "Open in file explorer"),
                ]
            },
            {
                "icon": "🧭",
                "title": "NAVIGATE",
                "commands": [
                    ("goto <name>", "Jump to project (fuzzy search)"),
                    ("recent [days]", "Show recent projects"),
                    ("ls [type]", "List projects (apps|bots|tools)"),
                    ("where", "Show current location + options"),
                    ("fav", "Toggle favorite for current project"),
                    ("favorites", "Show all favorites"),
                ]
            },
            {
                "icon": "🩺",
                "title": "HEALTH & MAINTENANCE",
                "commands": [
                    ("health", "Quick health check (git/python/node)"),
                    ("sync", "Pull all git repos"),
                    ("clean [--deep]", "Remove build artifacts"),
                    ("fix <issue>", "Auto-fix common problems"),
                ]
            },
            {
                "icon": "⚙️",
                "title": "CONFIGURATION",
                "commands": [
                    ("config", "Show current config"),
                    ("learn [on|off]", "Toggle learning mode"),
                    ("migrate", "Migrate to new folder structure"),
                ]
            },
            {
                "icon": "📚",
                "title": "LEARNING",
                "commands": [
                    ("wizard", "Setup wizard for beginners"),
                    ("tutorial", "Interactive walkthrough"),
                    ("examples", "Common workflows"),
                    ("help", "This help screen"),
                ]
            }
        ]
        
        for section in sections:
            self.console.print(f" {section['icon']} [accent]{section['title']}[/]")
            for cmd, desc in section['commands']:
                self.console.print(f"   [text]{cmd:<25}[/] [dim]{desc}[/]")
            self.console.print()
        
        self.console.print(" [dim]💡 Type 'dojo' alone for interactive menu[/]\n")
    
    def show_wizard(self):
        """Setup wizard for beginners"""
        self.show_header()
        self.console.print(" [accent]WELCOME TO DOJO![/] 🎊\n")
        
        panel = Panel(
            "This wizard will help you get started.\n"
            "We'll set up your preferences and show you around.",
            border_style="accent"
        )
        self.console.print(panel)
        self.console.print()
        
        # Step 1: Learning mode
        self.console.print(" [accent]Step 1: Learning Mode[/]\n")
        self.console.print(" Learning mode explains each command as you use it.")
        self.console.print(" Great for beginners, can be disabled later.\n")
        
        enable_learning = Confirm.ask(" Enable learning mode?", default=True)
        self.ctx.save_config({'learning_mode': enable_learning})
        self.console.print()
        
        # Step 2: Tour
        self.console.print(" [accent]Step 2: Quick Tour[/]\n")
        self.console.print(" Let's see what's in your dojo...\n")
        
        # Count projects
        from pathlib import Path
        categories = ['apps', 'bots', 'tools', 'contracts']
        counts = {}
        for cat in categories:
            cat_path = self.ctx.dojo_root / cat
            if cat_path.exists():
                counts[cat] = len([d for d in cat_path.iterdir() if d.is_dir()])
        
        self.console.print(" [success]Your workspace:[/]\n")
        for cat, count in counts.items():
            icon = {'apps': '📱', 'bots': '🤖', 'tools': '🛠️', 'contracts': '📜'}.get(cat, '')
            self.console.print(f"   {icon} {count} {cat}")
        
        self.console.print()
        
        # Step 3: First command
        self.console.print(" [accent]Step 3: Try Your First Command[/]\n")
        self.console.print(" [dim]Recommended commands to try:[/]\n")
        self.console.print("   1. dojo recent   - See what you worked on")
        self.console.print("   2. dojo ls       - List all projects")
        self.console.print("   3. dojo health   - Check everything is healthy\n")
        
        self.console.print(" [success]Setup complete! 🎉[/]")
        self.console.print(" [dim]Type 'dojo' anytime for the interactive menu.\n")
    
    def show_tutorial(self):
        """Interactive tutorial"""
        self.show_header()
        self.console.print(" [accent]INTERACTIVE TUTORIAL[/] 🎓\n")
        
        steps = [
            {
                "title": "1. Finding your way around",
                "content": "Use 'dojo ls' to see all projects, or 'dojo recent' to see what you worked on lately.",
                "try": "dojo recent",
                "explain": "This shows your most recently accessed projects with timestamps."
            },
            {
                "title": "2. Jumping to projects",
                "content": "Use 'dojo goto <name>' with fuzzy search. Type part of the name!",
                "try": "dojo goto ops",
                "explain": "Fuzzy search means you can type 'ops' to find 'ops-home' or 'intel' to find 'farcaster-intel'."
            },
            {
                "title": "3. Starting development",
                "content": "Once in a project folder, type 'dojo dev' - it auto-detects the type!",
                "try": "dojo dev",
                "explain": "This automatically runs the right command: 'npm run dev' for Next.js, 'streamlit run' for Streamlit, etc."
            },
            {
                "title": "4. Health checks",
                "content": "Run 'dojo health' to check all repos, venvs, and node_modules at once.",
                "try": "dojo health",
                "explain": "This scans all your projects and shows which ones need syncing, missing dependencies, etc."
            },
            {
                "title": "5. Favorites",
                "content": "Mark projects you use often as favorites with 'dojo fav'.",
                "try": "dojo fav",
                "explain": "Favorites show up with a ⭐ in listings and you can quickly see them with 'dojo favorites'."
            }
        ]
        
        for step in steps:
            panel = Panel(
                f"[accent]{step['title']}[/]\n\n"
                f"{step['content']}\n\n"
                f"[success]Try:[/] {step['try']}\n\n"
                f"[dim]{step['explain']}[/]",
                border_style="accent"
            )
            self.console.print(panel)
            self.console.print()
            
            if not Confirm.ask(" Continue to next step?", default=True):
                break
        
        self.console.print(" [success]Tutorial complete! 🎉[/]")
        self.console.print(" [dim]You're ready to explore. Type 'dojo' for the menu.\n")
    
    def show_examples(self):
        """Common workflow examples"""
        self.show_header()
        self.console.print(" [accent]COMMON WORKFLOWS[/] 📚\n")
        
        examples = [
            {
                "task": "Start working on a project",
                "steps": [
                    "dojo recent              # See what you worked on",
                    "dojo goto ops            # Jump to ops-home",
                    "dojo dev                 # Start dev server"
                ]
            },
            {
                "task": "Check everything is healthy",
                "steps": [
                    "dojo health             # Run all checks",
                    "# Review issues",
                    "dojo fix git             # Auto-fix git issues"
                ]
            },
            {
                "task": "Clean up disk space",
                "steps": [
                    "dojo clean              # Preview deletions",
                    "dojo clean --deep       # Include node_modules"
                ]
            },
            {
                "task": "Update all repos",
                "steps": [
                    "dojo sync               # Pull all repos"
                ]
            },
            {
                "task": "Find and open a project",
                "steps": [
                    "dojo goto intel         # Fuzzy search",
                    "dojo code               # Open in VS Code"
                ]
            }
        ]
        
        for ex in examples:
            self.console.print(f" [accent]→ {ex['task']}[/]")
            for step in ex['steps']:
                if step.startswith('#'):
                    self.console.print(f"   [dim]{step}[/]")
                else:
                    self.console.print(f"   {step}")
            self.console.print()
    
    def show_config(self):
        """Show current configuration"""
        self.show_header()
        self.console.print(" [accent]CONFIGURATION[/] ⚙️\n")
        
        config = self.ctx.config
        
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column(style="accent")
        table.add_column()
        
        table.add_row("Version", config.get('version', '2.0'))
        table.add_row("CLI Mode", config.get('cli_mode', 'v2'))
        table.add_row("Learning Mode", "ON" if config.get('learning_mode') else "OFF")
        table.add_row("Theme", config.get('theme', 'snowzies'))
        table.add_row("Auto Sync", "ON" if config.get('auto_sync') else "OFF")
        table.add_row("Fuzzy Threshold", str(config.get('fuzzy_threshold', 0.6)))
        
        self.console.print(table)
        self.console.print()
        self.console.print(" [dim]Change settings: dojo learn [on|off][/]\n")
