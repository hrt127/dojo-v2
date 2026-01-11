"""
Migration - Tool to migrate from old to new folder structure
"""

from pathlib import Path
from rich.prompt import Confirm
from rich.table import Table
import shutil
import json
from datetime import datetime

class Migration:
    def __init__(self, ctx, console):
        self.ctx = ctx
        self.console = console  # Use themed console passed from main
        self.dojo_root = ctx.dojo_root
        self.backup_file = ctx.config_dir / 'migration_backup.json'
        
        # Mapping from old to new structure
        self.structure_map = {
            'apps': 'work/apps',
            'bots': 'work/bots',
            'tools': 'work/tools',
            'contracts': 'work/contracts',
            'experiments': 'lab',
            'protocols': 'research/defi',
            'ideas': 'research/strategies',
            'archive': 'resources',
            'downloads': 'resources/downloads'
        }
    
    def preview(self):
        """Show what would be migrated"""
        self.console.print("\n [accent]MIGRATION PREVIEW[/]\n")
        self.console.print(" This will reorganize your dojo structure:\n")
        
        # Old structure
        self.console.print(" [dim]OLD STRUCTURE:[/]")
        old_folders = ['apps', 'bots', 'experiments', 'protocols', 'ideas', 'tools', 'contracts']
        for folder in old_folders:
            if (self.dojo_root / folder).exists():
                count = len(list((self.dojo_root / folder).iterdir()))
                self.console.print(f"   {folder}/ [dim]({count} items)[/]")
        
        self.console.print()
        
        # New structure
        self.console.print(" [accent]NEW STRUCTURE:[/]")
        new_structure = {
            'work': 'Active development (apps, bots, tools, contracts)',
            'lab': 'Experiments & learning',
            'research': 'Knowledge & analysis',
            'resources': 'Static assets & archives'
        }
        
        for folder, desc in new_structure.items():
            self.console.print(f"   {folder}/ [dim]{desc}[/]")
        
        self.console.print()
        
        # Show detailed mapping
        table = Table(title="Folder Mapping")
        table.add_column("Old Path", style="dim")
        table.add_column("→", justify="center")
        table.add_column("New Path", style="text")
        
        for old, new in self.structure_map.items():
            if (self.dojo_root / old).exists():
                table.add_row(old, "→", new)
        
        self.console.print(table)
        self.console.print()
        
        # Safety notes
        self.console.print(" [warning]⚠  IMPORTANT NOTES:[/]")
        self.console.print("   • This will move folders, not copy")
        self.console.print("   • A backup record will be saved")
        self.console.print("   • You can rollback if needed")
        self.console.print("   • Git repos will be preserved\n")
    
    def execute(self):
        """Execute the migration"""
        self.preview()
        
        if not Confirm.ask(" [text]Proceed with migration?[/]"):
            self.console.print(" [dim]Migration cancelled[/]\n")
            return
        
        self.console.print("\n [accent]Starting migration...[/]\n")
        
        # Create backup record
        backup = {
            'timestamp': datetime.now().isoformat(),
            'moves': []
        }
        
        # Create new top-level directories
        (self.dojo_root / 'work').mkdir(exist_ok=True)
        (self.dojo_root / 'lab').mkdir(exist_ok=True)
        (self.dojo_root / 'research').mkdir(exist_ok=True)
        (self.dojo_root / 'resources').mkdir(exist_ok=True)
        
        # Perform migrations
        for old_path, new_path in self.structure_map.items():
            old = self.dojo_root / old_path
            new = self.dojo_root / new_path
            
            if not old.exists():
                continue
            
            self.console.print(f" Moving {old_path}... ", end="")
            
            try:
                # Ensure parent exists
                new.parent.mkdir(parents=True, exist_ok=True)
                
                # Move folder
                shutil.move(str(old), str(new))
                
                backup['moves'].append({
                    'from': old_path,
                    'to': new_path
                })
                
                self.console.print("[success]✓[/]")
            except Exception as e:
                self.console.print(f"[error]✗ {e}[/]")
        
        # Save backup
        self.backup_file.write_text(json.dumps(backup, indent=2))
        
        self.console.print()
        self.console.print(" [success]Migration complete! 🎉[/]")
        self.console.print(f" [dim]Backup saved to: {self.backup_file}[/]\n")
        
        # Show new structure
        self.console.print(" [accent]Your new structure:[/]\n")
        self._show_tree()
    
    def rollback(self):
        """Rollback migration"""
        if not self.backup_file.exists():
            self.console.print(" [error]No migration backup found[/]\n")
            return
        
        self.console.print("\n [warning]ROLLBACK MIGRATION[/]\n")
        
        try:
            backup = json.loads(self.backup_file.read_text())
            timestamp = backup['timestamp']
            moves = backup['moves']
            
            self.console.print(f" Found backup from: [dim]{timestamp}[/]")
            self.console.print(f" This will reverse {len(moves)} moves\n")
            
            if not Confirm.ask(" Proceed with rollback?"):
                self.console.print(" [dim]Rollback cancelled[/]\n")
                return
            
            self.console.print()
            
            # Reverse moves
            for move in reversed(moves):
                old = self.dojo_root / move['from']
                new = self.dojo_root / move['to']
                
                self.console.print(f" Restoring {move['from']}... ", end="")
                
                try:
                    # Move back
                    shutil.move(str(new), str(old))
                    self.console.print("[success]✓[/]")
                except Exception as e:
                    self.console.print(f"[error]✗ {e}[/]")
            
            # Remove backup
            self.backup_file.unlink()
            
            self.console.print()
            self.console.print(" [success]Rollback complete![/]\n")
            
        except Exception as e:
            self.console.print(f" [error]Rollback failed: {e}[/]\n")
    
    def _show_tree(self):
        """Show new folder structure"""
        structure = {
            'work': ['apps', 'bots', 'tools', 'contracts'],
            'lab': [],
            'research': ['defi', 'strategies'],
            'resources': []
        }
        
        for parent, children in structure.items():
            parent_path = self.dojo_root / parent
            if not parent_path.exists():
                continue
            
            self.console.print(f" {parent}/")
            
            # Show known subdirs
            for child in children:
                child_path = parent_path / child
                if child_path.exists():
                    count = len(list(child_path.iterdir()))
                    self.console.print(f"   ├─ {child}/ [dim]({count} items)[/]")
            
            # Show other items
            known_children = set(children)
            for item in parent_path.iterdir():
                if item.name not in known_children:
                    if item.is_dir():
                        count = len(list(item.iterdir()))
                        self.console.print(f"   ├─ {item.name}/ [dim]({count} items)[/]")
            
            self.console.print()
