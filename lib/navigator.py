"""
Navigator - Enhanced with fuzzy search, favorites, and migration
"""

from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
import subprocess
import json
import shutil
from datetime import datetime
from difflib import SequenceMatcher

console = Console()

class Navigator:
    def __init__(self, ctx):
        self.ctx = ctx
        self.dojo_root = ctx.dojo_root
    
    def goto(self, search_term):
        """Fuzzy search and jump to project"""
        matches = self._fuzzy_search(search_term)
        
        if not matches:
            console.print(f" [error]No projects found matching '{search_term}'[/]\n")
            console.print(" [dim]💡 Tip: Try 'dojo ls' to see all projects[/]\n")
            return
        
        if len(matches) == 1:
            target = matches[0]
            full_path = self.dojo_root / target
            console.print(f" [success]→[/] {target}\n")
            console.print(f" [dim]cd {full_path}[/]\n")
            
            # Show what you can do here
            self._show_quick_preview(full_path)
            return
        
        # Multiple matches - interactive selection
        console.print(f"\n [accent]Found {len(matches)} matches:[/]\n")
        
        table = Table.grid(padding=(0, 2))
        table.add_column(style="accent", justify="right")
        table.add_column()
        table.add_column(style="dim")
        
        for i, match in enumerate(matches[:10], 1):
            ptype = self._detect_project_type(self.dojo_root / match)
            table.add_row(str(i), match, ptype)
        
        console.print(table)
        console.print()
        
        choice = Prompt.ask(" [accent]Choose[/]", default="1")
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(matches):
                target = matches[idx]
                full_path = self.dojo_root / target
                console.print(f"\n [success]→[/] {target}\n")
                console.print(f" [dim]cd {full_path}[/]\n")
                self._show_quick_preview(full_path)
        except:
            console.print(" [error]Invalid choice[/]\n")
    
    def _fuzzy_search(self, term):
        """Enhanced fuzzy search with scoring"""
        term = term.lower()
        matches = []
        threshold = self.ctx.config.get('fuzzy_threshold', 0.6)
        
        categories = ['apps', 'bots', 'tools', 'contracts', 'work', 'lab', 'research']
        
        for cat in categories:
            cat_path = self.dojo_root / cat
            if not cat_path.exists():
                continue
            
            for item in cat_path.iterdir():
                if not item.is_dir():
                    continue
                
                # Calculate fuzzy match score
                score = SequenceMatcher(None, term, item.name.lower()).ratio()
                
                # Also check if term is substring
                if term in item.name.lower():
                    score = max(score, 0.8)
                
                if score >= threshold:
                    matches.append((f"{cat}/{item.name}", score))
        
        # Sort by score (highest first)
        matches.sort(key=lambda x: x[1], reverse=True)
        return [m[0] for m in matches]
    
    def _show_quick_preview(self, path):
        """Show quick preview of what you can do at this location"""
        # Change to that directory for context detection
        import os
        original_cwd = os.getcwd()
        os.chdir(path)
        
        # Re-detect context
        temp_ctx = type('obj', (object,), {
            'cwd': path,
            'dojo_root': self.dojo_root,
            'project_type': self.ctx.detect_type.__func__(type('obj', (object,), {'cwd': path})())
        })()
        
        from context import DojoContext
        temp_full_ctx = DojoContext()
        actions = temp_full_ctx.get_quick_actions()
        
        if actions:
            console.print(" [accent]Quick actions:[/]")
            for cmd, desc, _ in actions[:3]:
                console.print(f"   dojo {cmd:<10} {desc}")
            console.print()
        
        os.chdir(original_cwd)
    
    def list_projects(self, category=None):
        """Enhanced list with counts and status"""
        console.print()
        
        categories = {
            'apps': '📱 Apps',
            'bots': '🤖 Bots', 
            'tools': '🛠️  Tools',
            'contracts': '📜 Contracts',
            'work': '💼 Work',
            'lab': '🧪 Lab',
            'research': '📚 Research'
        }
        
        if category and category not in categories:
            console.print(f" [error]Unknown category. Try: {', '.join(categories.keys())}[/]\n")
            return
        
        targets = [category] if category else categories.keys()
        
        total_projects = 0
        
        for cat in targets:
            cat_path = self.dojo_root / cat
            if not cat_path.exists():
                continue
            
            items = sorted([d for d in cat_path.iterdir() if d.is_dir()])
            
            if not items:
                continue
            
            console.print(f" [accent]{categories[cat]}[/] [dim]({len(items)})[/]")
            total_projects += len(items)
            
            for item in items:
                ptype = self._detect_project_type(item)
                # Check if it's a favorite
                is_fav = f"{cat}/{item.name}" in self.ctx.get_favorites()
                star = "⭐" if is_fav else "  "
                
                console.print(f"   {star} {item.name:<30} [dim]{ptype}[/]")
            
            console.print()
        
        console.print(f" [dim]Total: {total_projects} projects[/]\n")
    
    def _detect_project_type(self, path):
        """Quick type detection for listing"""
        if (path / 'package.json').exists():
            if (path / 'next.config.js').exists() or (path / 'next.config.ts').exists():
                return 'nextjs'
            return 'node'
        elif (path / 'app.py').exists():
            return 'streamlit'
        elif (path / 'requirements.txt').exists():
            return 'python'
        elif (path / 'foundry.toml').exists():
            return 'foundry'
        elif (path / 'hardhat.config.js').exists():
            return 'hardhat'
        return ''
    
    def show_recent(self, days=7):
        """Enhanced recent with more details"""
        console.print("\n [accent]RECENT PROJECTS[/]")
        console.print(f" [dim]Last {days} days[/]\n")
        
        recent = self.ctx.get_recent_projects(limit=15, days=days)
        
        if not recent:
            console.print(" [dim]No recent projects[/]")
            console.print(" [dim]💡 Start working on something to track it here![/]\n")
            return
        
        table = Table.grid(padding=(0, 2))
        table.add_column(style="accent", justify="right")
        table.add_column()
        table.add_column(style="dim", justify="right")
        table.add_column(style="dim")
        
        for i, entry in enumerate(recent, 1):
            name = entry['name']
            ptype = entry['type']
            timestamp = datetime.fromisoformat(entry['timestamp'])
            
            # Calculate time ago
            now = datetime.now()
            delta = now - timestamp
            
            if delta.seconds < 3600:
                time_str = f"{delta.seconds // 60}m ago"
            elif delta.days == 0:
                time_str = f"{delta.seconds // 3600}h ago"
            elif delta.days == 1:
                time_str = "yesterday"
            else:
                time_str = f"{delta.days}d ago"
            
            # Check if favorite
            is_fav = "⭐" if name in self.ctx.get_favorites() else ""
            
            table.add_row(str(i), f"{is_fav} {name}", time_str, ptype)
        
        console.print(table)
        console.print()
        console.print(" [dim]💡 Type 'dojo goto <number>' to jump to a project[/]\n")
    
    def show_where(self):
        """Enhanced location awareness"""
        console.print()
        console.print(" ⛄ [accent]WHERE AM I?[/]\n")
        
        if self.ctx.is_in_dojo():
            rel_path = self.ctx.cwd.relative_to(self.dojo_root)
            console.print(f" 📍 [path]{rel_path}[/]")
            console.print(f" 📦 {self.ctx.project_type}")
            
            if self.ctx.in_git_repo:
                console.print(" 🌿 [dim]git repo[/]")
            
            console.print()
            
            actions = self.ctx.get_quick_actions()
            if actions:
                console.print(" [accent]WHAT YOU CAN DO:[/]")
                for i, (cmd, desc, _) in enumerate(actions, 1):
                    console.print(f"   {i}. dojo {cmd:<12} {desc}")
                console.print()
        else:
            console.print(f" 📍 [path]{self.ctx.cwd}[/]")
            console.print(" [dim](outside dojo)[/]")
            console.print(f"\n [dim]💡 Navigate to dojo: cd {self.dojo_root}[/]\n")
    
    def toggle_favorite(self, project_name=None):
        """Add/remove favorite"""
        if not project_name:
            project_name = self.ctx.project_name
        
        if not project_name:
            console.print(" [error]Not in a project[/]\n")
            return
        
        favorites = self.ctx.get_favorites()
        
        if project_name in favorites:
            # Remove
            data = json.loads(self.ctx.history_file.read_text())
            data['favorites'] = [f for f in data['favorites'] if f != project_name]
            self.ctx.history_file.write_text(json.dumps(data, indent=2))
            console.print(f" [dim]Removed {project_name} from favorites[/]\n")
        else:
            # Add
            if self.ctx.add_favorite(project_name):
                console.print(f" [success]⭐ Added {project_name} to favorites![/]\n")
    
    def show_favorites(self):
        """Show favorite projects"""
        console.print("\n [accent]⭐ FAVORITE PROJECTS[/]\n")
        
        favorites = self.ctx.get_favorites()
        
        if not favorites:
            console.print(" [dim]No favorites yet[/]")
            console.print(" [dim]💡 Use 'dojo fav' to add current project[/]\n")
            return
        
        for i, fav in enumerate(favorites, 1):
            path = self.dojo_root / fav
            ptype = self._detect_project_type(path) if path.exists() else "missing"
            console.print(f" [accent]{i}[/] {fav:<30} [dim]{ptype}[/]")
        
        console.print()
    
    def run_dev(self, target=None):
        """Run development command with learning mode support"""
        if target:
            matches = self._fuzzy_search(target)
            if not matches:
                console.print(f" [error]Project not found: {target}[/]\n")
                return
            
            project_path = self.dojo_root / matches[0]
            console.print(f" [success]Running dev in {matches[0]}...[/]\n")
            import os
            os.chdir(project_path)
            self.ctx.cwd = project_path
            self.ctx.project_type = self.ctx.detect_type()
        
        actions = self.ctx.get_quick_actions()
        dev_action = next((a for a in actions if a[0] == 'dev'), None)
        
        if not dev_action:
            console.print(" [error]No dev command available for this project type[/]\n")
            return
        
        cmd = dev_action[2]
        
        # Learning mode explanation
        if self.ctx.learning_mode:
            panel = Panel(
                f"This will run: [accent]{cmd}[/]\n\n"
                f"Project type: {self.ctx.project_type}\n"
                f"Location: {self.ctx.cwd}\n\n"
                "This starts your development server.",
                title="💡 Learning Mode",
                border_style="dim"
            )
            console.print(panel)
            
            if not Confirm.ask(" Continue?", default=True):
                return
            console.print()
        
        console.print(f" [dim]$ {cmd}[/]\n")
        
        try:
            subprocess.run(cmd, shell=True, cwd=self.ctx.cwd)
        except KeyboardInterrupt:
            console.print("\n [dim]Stopped[/]\n")
    
    def open_vscode(self, target=None):
        """Open project in VS Code"""
        if target:
            matches = self._fuzzy_search(target)
            if not matches:
                console.print(f" [error]Project not found: {target}[/]\n")
                return
            path = self.dojo_root / matches[0]
        else:
            path = self.ctx.cwd
        
        console.print(f" [success]Opening in VS Code...[/] [dim]{path}[/]\n")
        subprocess.run(['code', str(path)])
    
    def open_explorer(self, target=None):
        """Open in file explorer"""
        if target:
            matches = self._fuzzy_search(target)
            if not matches:
                console.print(f" [error]Project not found: {target}[/]\n")
                return
            path = self.dojo_root / matches[0]
        else:
            path = self.ctx.cwd
        
        console.print(f" [success]Opening explorer...[/] [dim]{path}[/]\n")
        subprocess.run(['explorer.exe', str(path)])
