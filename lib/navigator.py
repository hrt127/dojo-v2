"""
Navigator - goto, ls, recent, run commands
"""

from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
import subprocess
import json
from datetime import datetime

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
            return
        
        if len(matches) == 1:
            target = matches[0]
            console.print(f" [success]→[/] {target}\n")
            console.print(f" [dim]cd {self.dojo_root / target}[/]\n")
            return
        
        # Multiple matches - let user choose
        console.print(f"\n [accent]Found {len(matches)} matches:[/]\n")
        for i, match in enumerate(matches, 1):
            console.print(f" [accent]{i}[/] {match}")
        
        console.print()
        choice = Prompt.ask(" [accent]Choose[/]", default="1")
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(matches):
                target = matches[idx]
                console.print(f"\n [success]→[/] {target}\n")
                console.print(f" [dim]cd {self.dojo_root / target}[/]\n")
        except:
            console.print(" [error]Invalid choice[/]\n")
    
    def _fuzzy_search(self, term):
        """Find projects matching search term"""
        term = term.lower()
        matches = []
        
        categories = ['apps', 'bots', 'tools', 'contracts']
        
        for cat in categories:
            cat_path = self.dojo_root / cat
            if not cat_path.exists():
                continue
            
            for item in cat_path.iterdir():
                if item.is_dir() and term in item.name.lower():
                    matches.append(f"{cat}/{item.name}")
        
        return sorted(matches)
    
    def list_projects(self, category=None):
        """List projects by category"""
        console.print()
        
        categories = {
            'apps': '📱 Apps',
            'bots': '🤖 Bots', 
            'tools': '🛠️  Tools',
            'contracts': '📜 Contracts'
        }
        
        if category and category not in categories:
            console.print(f" [error]Unknown category. Try: {', '.join(categories.keys())}[/]\n")
            return
        
        targets = [category] if category else categories.keys()
        
        for cat in targets:
            cat_path = self.dojo_root / cat
            if not cat_path.exists():
                continue
            
            console.print(f" [accent]{categories[cat]}[/]")
            
            items = sorted([d for d in cat_path.iterdir() if d.is_dir()])
            
            if not items:
                console.print("   [dim](empty)[/]")
            else:
                for item in items:
                    ptype = self._detect_project_type(item)
                    console.print(f"   {item.name:<30} [dim]{ptype}[/]")
            
            console.print()
    
    def _detect_project_type(self, path):
        """Quick type detection for listing"""
        if (path / 'package.json').exists():
            return 'node'
        elif (path / 'app.py').exists():
            return 'streamlit'
        elif (path / 'requirements.txt').exists():
            return 'python'
        elif (path / 'foundry.toml').exists():
            return 'foundry'
        return ''
    
    def show_recent(self):
        """Show recent projects"""
        console.print("\n [accent]RECENT PROJECTS[/]\n")
        
        try:
            data = json.loads(self.ctx.history_file.read_text())
            recent = data.get('recent', [])[:10]
            
            if not recent:
                console.print(" [dim]No recent projects[/]\n")
                return
            
            for i, entry in enumerate(recent, 1):
                name = entry['name']
                ptype = entry['type']
                timestamp = datetime.fromisoformat(entry['timestamp'])
                
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
                
                console.print(f" [accent]{i:2}[/] {name:<30} [dim]{time_str:<12} {ptype}[/]")
            
            console.print()
            
        except Exception as e:
            console.print(f" [error]Error reading history: {e}[/]\n")
    
    def show_where(self):
        """Show current location and options"""
        console.print()
        console.print(" ⛄ [accent]WHERE AM I?[/]\n")
        
        if self.ctx.is_in_dojo():
            rel_path = self.ctx.cwd.relative_to(self.dojo_root)
            console.print(f" 📍 [path]{rel_path}[/]")
            console.print(f" 📦 {self.ctx.project_type}\n")
            
            actions = self.ctx.get_quick_actions()
            if actions:
                console.print(" [accent]WHAT YOU CAN DO:[/]")
                for cmd, desc, _ in actions:
                    console.print(f"   dojo {cmd:<15} {desc}")
                console.print()
        else:
            console.print(f" 📍 [path]{self.ctx.cwd}[/]")
            console.print(" [dim](outside dojo)\n")
    
    def run_dev(self, target=None):
        """Run development command"""
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
