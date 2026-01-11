"""
UI - Dashboard, help screens, tutorial
"""

from rich.console import Console
from rich.theme import Theme
from rich.table import Table
from rich.prompt import Prompt

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
        self.console.print("dojo", style="header bold", end="")
        self.console.print(" 🌸", style="header")
        self.console.print(" Your dev home\n", style="dim")
    
    def show_dashboard(self):
        self.show_header()
        
        if self.ctx.is_in_dojo():
            location = str(self.ctx.cwd.relative_to(self.ctx.dojo_root))
            self.console.print(f" 📍 [path]{location}[/]")
            if self.ctx.project_type != 'folder':
                self.console.print(f" 📦 {self.ctx.project_type}\n", style="dim")
            else:
                self.console.print()
        else:
            self.console.print(f" 📍 [path]{self.ctx.cwd}[/]")
            self.console.print(" [dim](outside dojo)\n")
        
        table = Table.grid(padding=(0, 2), pad_edge=False)
        table.add_column(style="accent", justify="right", width=3)
        table.add_column(style="text")
        table.add_column(style="dim")
        
        num = 1
        
        quick_actions = self.ctx.get_quick_actions()
        if quick_actions:
            table.add_row("", "[accent]QUICK ACTIONS[/]", "")
            for cmd, desc, _ in quick_actions[:3]:
                table.add_row(f"{num}", cmd, desc)
                num += 1
            table.add_row("", "", "")
        
        table.add_row("", "[accent]NAVIGATE[/]", "")
        nav_items = [("goto", "Jump to project"), ("recent", "Recent projects"), ("ls", "List: apps, bots, tools")]
        for cmd, desc in nav_items:
            table.add_row(f"{num}", cmd, desc)
            num += 1
        table.add_row("", "", "")
        
        table.add_row("", "[accent]UTILS[/]", "")
        util_items = [("code", "Open in VS Code"), ("health", "Check git/python/node"), ("clean", "Clean build files")]
        for cmd, desc in util_items:
            table.add_row(f"{num}", cmd, desc)
            num += 1
        table.add_row("", "", "")
        
        table.add_row(f"{num}", "help", "Show all commands")
        
        self.console.print(table)
        self.console.print()
        Prompt.ask(" [accent]❯[/]", default="help")
    
    def show_help(self):
        self.show_header()
        
        if self.ctx.is_in_dojo():
            location = str(self.ctx.cwd.relative_to(self.ctx.dojo_root))
            self.console.print(f" 📍 [dim]{location}[/]\n")
        
        sections = [
            {
                "icon": "🚀",
                "title": "QUICK",
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
                    ("recent", "Show recent projects"),
                    ("ls [apps|bots|tools]", "List projects by type"),
                    ("where", "Show current location + options"),
                ]
            },
            {
                "icon": "🩺",
                "title": "HEALTH & MAINTENANCE",
                "commands": [
                    ("health", "Quick health check (git/python/node)"),
                    ("sync", "Pull all git repos"),
                    ("clean [--deep]", "Remove build artifacts"),
                ]
            },
            {
                "icon": "📚",
                "title": "LEARNING",
                "commands": [
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
    
    def show_tutorial(self):
        self.show_header()
        self.console.print(" [accent]TUTORIAL - Let's learn together![/]\n")
        
        steps = [
            {"title": "1. Finding your way around", "content": "Use 'dojo ls' to see all your projects, or 'dojo recent' to see what you worked on lately.", "try": "dojo recent"},
            {"title": "2. Jumping to projects", "content": "Use 'dojo goto <name>' with fuzzy search. Try 'dojo goto ops' to find ops-home!", "try": "dojo goto ops"},
            {"title": "3. Starting development", "content": "Once in a project folder, just type 'dojo dev' and it auto-detects the type!", "try": "cd ops-home && dojo dev"},
            {"title": "4. Health checks", "content": "Run 'dojo health' to check all repos, venvs, and node_modules at once.", "try": "dojo health"}
        ]
        
        for step in steps:
            self.console.print(f" [accent]{step['title']}[/]")
            self.console.print(f" {step['content']}\n")
            self.console.print(f" [dim]Try: {step['try']}[/]\n")
            
            if not Prompt.ask(" Continue?", choices=["y", "n"], default="y") == "y":
                break
        
        self.console.print(" [success]Tutorial complete! 🎉[/]\n")
    
    def show_examples(self):
        self.show_header()
        self.console.print(" [accent]COMMON WORKFLOWS[/]\n")
        
        examples = [
            {"task": "Start working on a project", "steps": ["dojo recent", "dojo goto ops", "dojo dev"]},
            {"task": "Check everything is healthy", "steps": ["dojo health", "# Choose 'y' to auto-fix issues"]},
            {"task": "Clean up space", "steps": ["dojo clean", "dojo clean --deep"]},
            {"task": "Update all repos", "steps": ["dojo sync"]}
        ]
        
        for ex in examples:
            self.console.print(f" [accent]→ {ex['task']}[/]")
            for step in ex['steps']:
                self.console.print(f"   [dim]{step}[/]")
            self.console.print()
