"""
UI - Interactive dashboard with progressive disclosure and learning mode
"""

from rich.console import Console
from rich.theme import Theme
from rich.table import Table
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.panel import Panel
from rich import box

THEME = Theme({
    "header": "bold #FFB7C5",
    "accent": "color(208)",
    "text": "#E0E6ED",
    "success": "#A8E6CF",
    "warning": "#FFD3B6",
    "error": "bold #FF8BA7",
    "dim": "#6B7280",
    "path": "cyan",
    "number": "bold #C8A2C8",
})

class UI:
    def __init__(self, ctx):
        self.ctx = ctx
        self.console = Console(theme=THEME)
    
    def show_header(self):
        """Show dojo header"""
        self.console.print()
        self.console.print(" ⛄ ", style="header", end="")
        self.console.print("dojo v2", style="header", end="")
        self.console.print(" 🌸", style="header")
        
        if self.ctx.is_learning_mode():
            self.console.print(" [dim]💡 Learning mode ON[/]")
        
        self.console.print()
    
    def show_dashboard(self):
        """Interactive numbered dashboard"""
        self.show_header()
        
        # Context header
        if self.ctx.is_in_dojo():
            location = str(self.ctx.cwd.relative_to(self.ctx.dojo_root))
            self.console.print(f" 📍 [path]{location}[/]")
            
            if self.ctx.project_type != 'folder':
                type_display = self.ctx.project_type.upper()
                self.console.print(f" 📦 {type_display}", style="dim")
            
            # Git status
            if self.ctx.git_status:
                git = self.ctx.git_status
                if git['synced'] and git['clean']:
                    self.console.print(f" ✓ [success]{git['branch']} (synced)[/]")
                elif git['behind']:
                    self.console.print(f" ⚠ [warning]{git['branch']} (behind origin)[/]")
                elif not git['clean']:
                    self.console.print(f" ⚠ [warning]{git['branch']} (uncommitted changes)[/]")
            
            self.console.print()
        else:
            self.console.print(f" 📍 [path]{self.ctx.cwd}[/]")
            self.console.print(" [dim](outside dojo)\n")
        
        # Build menu
        menu_items = []
        num = 1
        
        # Quick actions
        quick_actions = self.ctx.get_quick_actions()
        if quick_actions:
            menu_items.append(('header', 'QUICK ACTIONS'))
            for cmd, desc, _, _ in quick_actions[:3]:
                menu_items.append(('action', num, cmd, desc))
                num += 1
        
        # Navigation
        menu_items.append(('header', 'NAVIGATE'))
        nav_items = [
            ('goto', 'Jump to project'),
            ('recent', 'Recent projects'),
            ('ls', 'List all projects')
        ]
        for cmd, desc in nav_items:
            menu_items.append(('action', num, cmd, desc))
            num += 1
        
        # Utils
        menu_items.append(('header', 'UTILS'))
        util_items = [
            ('code', 'Open in VS Code'),
            ('health', 'Health check'),
            ('clean', 'Clean build files')
        ]
        for cmd, desc in util_items:
            menu_items.append(('action', num, cmd, desc))
            num += 1
        
        # Learn
        menu_items.append(('header', 'LEARN'))
        learn_items = [
            ('tutorial', 'Interactive tutorial'),
            ('examples', 'Common workflows'),
            ('help', 'Full documentation')
        ]
        for cmd, desc in learn_items:
            menu_items.append(('action', num, cmd, desc))
            num += 1
        
        # Display menu
        table = Table.grid(padding=(0, 2), pad_edge=False)
        table.add_column(style="number", justify="right", width=3)
        table.add_column(style="text")
        table.add_column(style="dim")
        
        for item in menu_items:
            if item[0] == 'header':
                table.add_row("", f"[accent]{item[1]}[/]", "")
            else:
                _, num, cmd, desc = item
                table.add_row(f"{num}", cmd, desc)
        
        self.console.print(table)
        self.console.print()
        
        # Prompt
        choice = Prompt.ask(" [accent]❯[/]", default="help")
        
        # Handle numeric choice
        if choice.isdigit():
            idx = int(choice) - 1
            action_items = [item for item in menu_items if item[0] == 'action']
            if 0 <= idx < len(action_items):
                cmd = action_items[idx][2]
                self.console.print(f"\n [dim]Running: dojo {cmd}[/]\n")
    
    def show_help(self):
        """Context-aware help system"""
        self.show_header()
        
        if self.ctx.is_in_dojo():
            location = str(self.ctx.cwd.relative_to(self.ctx.dojo_root))
            ptype = self.ctx.project_type.upper() if self.ctx.project_type != 'folder' else 'folder'
            self.console.print(f" 🧭 You're in: [path]{location}[/] [dim]({ptype})[/]\n")
        
        sections = [
            {
                "icon": "🚀",
                "title": "QUICK ACTIONS",
                "desc": "Context-aware commands that just work",
                "commands": [
                    ("dev [project]", "Start development (auto-detects type)"),
                    ("code [project]", "Open in VS Code"),
                    ("open [project]", "Open in file explorer"),
                ]
            },
            {
                "icon": "🧭",
                "title": "NAVIGATION",
                "desc": "Find your way around",
                "commands": [
                    ("goto <name>", "Jump to project (fuzzy search)"),
                    ("recent", "Show recent projects"),
                    ("ls [category]", "List projects"),
                    ("where", "Where am I? What can I do?"),
                ]
            },
            {
                "icon": "🪺",
                "title": "HEALTH & MAINTENANCE",
                "desc": "Keep everything running smoothly",
                "commands": [
                    ("health", "Quick health check"),
                    ("sync", "Pull all git repos"),
                    ("clean [--deep]", "Remove build artifacts"),
                    ("fix <issue>", "Auto-fix common problems"),
                ]
            },
            {
                "icon": "📚",
                "title": "LEARNING & CONFIG",
                "desc": "Customize and learn",
                "commands": [
                    ("tutorial", "Interactive walkthrough"),
                    ("examples", "Common workflows"),
                    ("learn [on|off]", "Toggle learning mode"),
                    ("config", "Configure dojo"),
                ]
            }
        ]
        
        # Show relevant actions first if in a project
        if self.ctx.project_type != 'folder':
            actions = self.ctx.get_quick_actions()
            if actions:
                self.console.print(" [accent]WHAT YOU CAN DO HERE:[/]")
                for cmd, desc, _, _ in actions:
                    self.console.print(f"   dojo {cmd:<15} [dim]{desc}[/]")
                self.console.print()
        
        for section in sections:
            self.console.print(f" {section['icon']} [accent]{section['title']}[/]")
            if section.get('desc'):
                self.console.print(f"    [dim]{section['desc']}[/]")
            for cmd, desc in section['commands']:
                self.console.print(f"   [text]{cmd:<25}[/] [dim]{desc}[/]")
            self.console.print()
        
        # Tips
        tips = [
            "Type 'dojo' alone for interactive menu",
            "Use 'dojo learn on' to see explanations for every command",
            "Most commands work without arguments from inside a project"
        ]
        
        self.console.print(" [accent]💡 TIPS[/]")
        for tip in tips:
            self.console.print(f"   [dim]{tip}[/]")
        self.console.print()
    
    def explain_command(self, command, action_details):
        """Show learning mode explanation"""
        if not self.ctx.is_learning_mode():
            return
        
        cmd, desc, exec_cmd, explanation = action_details
        
        panel = Panel(
            f"[accent]LEARNING MODE[/]\n\n"
            f"This will:\n"
            f"  • {explanation}\n\n"
            f"Command: [dim]{exec_cmd}[/]",
            title="💡 What's happening?",
            border_style="accent",
            box=box.ROUNDED
        )
        
        self.console.print()
        self.console.print(panel)
        self.console.print()
        
        if not Confirm.ask(" Continue?", default=True):
            self.console.print(" [dim]Cancelled[/]\n")
            return False
        
        return True
    
    def show_wizard(self):
        """Setup wizard for new users"""
        self.show_header()
        self.console.print(" [accent]WELCOME TO DOJO! 🎉[/]\n")
        self.console.print(" Let's get you set up in 3 quick steps.\n")
        
        # Step 1: Check structure
        self.console.print(" [accent]Step 1: Checking your dojo structure...[/]")
        
        if self.ctx.needs_migration():
            self.console.print(" [warning]⚠  Found old folder structure[/]")
            self.console.print(" [dim]Old: apps/bots/experiments/protocols[/]")
            self.console.print(" [dim]New: work/lab/research[/]\n")
            
            if Confirm.ask(" Would you like to migrate to the new structure?"):
                self.console.print(" [success]Great! Run 'dojo migrate' when ready[/]\n")
        else:
            self.console.print(" [success]✓ Structure looks good![/]\n")
        
        # Step 2: Learning mode
        self.console.print(" [accent]Step 2: Learning mode[/]")
        self.console.print(" This shows explanations for every command.")
        self.console.print(" Perfect for getting started!\n")
        
        if Confirm.ask(" Enable learning mode?", default=True):
            self.ctx.save_config('learning_mode', True)
            self.console.print(" [success]✓ Learning mode enabled![/]")
            self.console.print(" [dim]Toggle anytime with: dojo learn off[/]\n")
        
        # Step 3: Quick tour
        self.console.print(" [accent]Step 3: Quick tour[/]")
        self.console.print(" Let me show you the basics:\n")
        
        basics = [
            ("dojo", "Interactive menu (you can pick with numbers!)"),
            ("dojo goto <name>", "Jump to any project (fuzzy search)"),
            ("dojo recent", "See what you worked on"),
            ("dojo dev", "Start dev server (auto-detects type)"),
            ("dojo health", "Check if everything is healthy")
        ]
        
        for cmd, desc in basics:
            self.console.print(f"   [text]{cmd:<20}[/] [dim]{desc}[/]")
        
        self.console.print()
        self.console.print(" [success]You're all set! 🌸[/]")
        self.console.print(" [dim]Type 'dojo tutorial' for an interactive walkthrough[/]\n")
    
    def show_tutorial(self):
        """Interactive tutorial"""
        self.show_header()
        self.console.print(" [accent]INTERACTIVE TUTORIAL[/]\n")
        
        lessons = [
            {
                "title": "Lesson 1: Finding Projects",
                "content": [
                    "Use 'dojo ls' to see all your projects organized by type.",
                    "Use 'dojo recent' to see what you've worked on lately.",
                    "Pro tip: Type just the number in the interactive menu!"
                ],
                "try": "dojo recent"
            },
            {
                "title": "Lesson 2: Jumping Around",
                "content": [
                    "Use 'dojo goto <name>' with partial names.",
                    "Example: 'dojo goto ops' finds 'ops-home'.",
                    "If multiple matches, you can choose!"
                ],
                "try": "dojo goto <partial-name>"
            },
            {
                "title": "Lesson 3: Starting Development",
                "content": [
                    "From inside a project, just type 'dojo dev'.",
                    "It auto-detects: Next.js, Python, Streamlit, etc.",
                    "Or specify: 'dojo dev <project-name>'"
                ],
                "try": "cd <project> && dojo dev"
            },
            {
                "title": "Lesson 4: Health Checks",
                "content": [
                    "Run 'dojo health' to check all projects at once.",
                    "It checks: git sync, venvs, node_modules.",
                    "It can even auto-fix issues!"
                ],
                "try": "dojo health"
            }
        ]
        
        for i, lesson in enumerate(lessons, 1):
            self.console.print(f" [accent]{lesson['title']}[/]\n")
            for line in lesson['content']:
                self.console.print(f"   {line}")
            self.console.print()
            self.console.print(f" [dim]Try: {lesson['try']}[/]\n")
            
            if i < len(lessons):
                if not Confirm.ask(" Continue to next lesson?", default=True):
                    break
            self.console.print()
        
        self.console.print(" [success]Tutorial complete! 🎉[/]")
        self.console.print(" [dim]You're ready to use dojo![/]\n")
    
    def show_examples(self):
        """Show common workflow examples"""
        self.show_header()
        self.console.print(" [accent]COMMON WORKFLOWS[/]\n")
        
        workflows = [
            {
                "task": "Start working on a project",
                "steps": [
                    "[text]dojo recent[/]",
                    "[text]dojo goto ops[/]",
                    "[text]dojo dev[/]"
                ]
            },
            {
                "task": "Check everything is healthy",
                "steps": [
                    "[text]dojo health[/]",
                    "[dim]# Choose 'y' to auto-fix issues[/]"
                ]
            },
            {
                "task": "Clean up disk space",
                "steps": [
                    "[text]dojo clean[/]",
                    "[dim]# Review what will be deleted[/]",
                    "[text]dojo clean --deep[/]",
                    "[dim]# Also removes node_modules[/]"
                ]
            },
            {
                "task": "Update all repositories",
                "steps": [
                    "[text]dojo sync[/]",
                    "[dim]# Pulls all git repos at once[/]"
                ]
            },
            {
                "task": "Open project in VS Code",
                "steps": [
                    "[text]dojo code ops-home[/]",
                    "[dim]# Or from inside project: dojo code[/]"
                ]
            }
        ]
        
        for workflow in workflows:
            self.console.print(f" [accent]→ {workflow['task']}[/]")
            for step in workflow['steps']:
                self.console.print(f"   {step}")
            self.console.print()
    
    def show_config(self):
        """Show current configuration"""
        self.show_header()
        self.console.print(" [accent]CURRENT CONFIGURATION[/]\n")
        
        config = self.ctx.config
        
        table = Table(show_header=False, box=box.SIMPLE)
        table.add_column("Setting", style="text")
        table.add_column("Value", style="accent")
        
        table.add_row("Learning Mode", "ON" if config.get('learning_mode') else "OFF")
        table.add_row("Version", config.get('version', 'v2'))
        table.add_row("Theme", config.get('theme', 'snowzies'))
        table.add_row("Auto-open Browser", "YES" if config.get('auto_open_browser', True) else "NO")
        
        self.console.print(table)
        self.console.print()
        
        self.console.print(" [dim]Change settings:[/]")
        self.console.print("   dojo learn [on|off]")
        self.console.print("   dojo config set <key> <value>\n")
