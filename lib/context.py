"""
Context detection - knows where you are and what you can do
Enhanced with learning mode, smart history, and config
"""

from pathlib import Path
import json
from datetime import datetime, timedelta
import yaml

class DojoContext:
    def __init__(self):
        self.cwd = Path.cwd()
        self.dojo_root = Path.home() / 'dojo'
        self.config_dir = Path.home() / '.dojo'
        self.config_file = self.config_dir / 'config.yml'
        self.history_file = self.config_dir / 'history.json'
        
        # Ensure config exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._init_config()
        self._init_history()
        
        # Load config
        self.config = self._load_config()
        self.learning_mode = self.config.get('learning_mode', False)
        
        self.project_type = self.detect_type()
        self.project_name = self.get_project_name()
        self.in_git_repo = self._is_git_repo()
        
        # Log this visit
        self.log_visit()
    
    def _init_config(self):
        """Initialize config file with defaults"""
        if not self.config_file.exists():
            default_config = {
                'version': '2.0',
                'learning_mode': False,
                'cli_mode': 'v2',
                'theme': 'snowzies',
                'auto_sync': False,
                'fuzzy_threshold': 0.6,
            }
            self.config_file.write_text(yaml.dump(default_config))
    
    def _init_history(self):
        """Initialize history file"""
        if not self.history_file.exists():
            self.history_file.write_text(json.dumps({
                'recent': [],
                'visits': {},
                'commands': [],
                'favorites': []
            }, indent=2))
    
    def _load_config(self):
        """Load config from YAML"""
        try:
            return yaml.safe_load(self.config_file.read_text())
        except:
            return {'learning_mode': False, 'cli_mode': 'v2'}
    
    def save_config(self, updates):
        """Save config updates"""
        self.config.update(updates)
        self.config_file.write_text(yaml.dump(self.config))
    
    def is_in_dojo(self):
        """Check if current dir is inside dojo"""
        try:
            return self.dojo_root in self.cwd.parents or self.cwd == self.dojo_root
        except:
            return False
    
    def get_project_name(self):
        """Get current project name"""
        if not self.is_in_dojo():
            return None
        
        try:
            # Get name relative to dojo root
            rel_path = self.cwd.relative_to(self.dojo_root)
            parts = rel_path.parts
            
            # If in a category folder, return category/name
            if len(parts) >= 2 and parts[0] in ['apps', 'bots', 'tools', 'contracts', 'work', 'lab', 'research']:
                return f"{parts[0]}/{parts[1]}"
            return str(rel_path)
        except:
            return None
    
    def _is_git_repo(self):
        """Check if current directory is in a git repo"""
        current = self.cwd
        while current != current.parent:
            if (current / '.git').exists():
                return True
            current = current.parent
        return False
    
    def detect_type(self):
        """Auto-detect project type with enhanced detection"""
        checks = [
            ('package.json', self._check_node),
            ('app.py', lambda: 'streamlit'),
            ('requirements.txt', lambda: 'python'),
            ('foundry.toml', lambda: 'foundry'),
            ('hardhat.config.js', lambda: 'hardhat'),
            ('Cargo.toml', lambda: 'rust'),
            ('go.mod', lambda: 'golang'),
        ]
        
        for file, checker in checks:
            if (self.cwd / file).exists():
                return checker() if callable(checker) else checker
        
        return 'folder'
    
    def _check_node(self):
        """Detailed Node.js project detection"""
        if (self.cwd / 'next.config.ts').exists() or (self.cwd / 'next.config.js').exists():
            return 'nextjs'
        if (self.cwd / 'next.config.mjs').exists():
            return 'nextjs'
        
        try:
            pkg = json.loads((self.cwd / 'package.json').read_text())
            deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
            
            if 'next' in deps:
                return 'nextjs'
            elif 'react' in deps:
                return 'react'
            elif 'express' in deps:
                return 'express'
            elif 'vite' in deps:
                return 'vite'
        except:
            pass
        
        return 'node'
    
    def get_quick_actions(self):
        """Return available quick actions for current project"""
        actions = {
            'nextjs': [
                ('dev', 'Start dev server', 'npm run dev'),
                ('build', 'Build for production', 'npm run build'),
                ('test', 'Run tests', 'npm test'),
            ],
            'react': [
                ('dev', 'Start dev server', 'npm start'),
                ('build', 'Build', 'npm run build'),
                ('test', 'Test', 'npm test'),
            ],
            'vite': [
                ('dev', 'Start dev server', 'npm run dev'),
                ('build', 'Build', 'npm run build'),
                ('preview', 'Preview build', 'npm run preview'),
            ],
            'node': [
                ('dev', 'Start dev', 'npm run dev'),
                ('start', 'Start', 'npm start'),
                ('install', 'Install deps', 'npm install'),
            ],
            'streamlit': [
                ('dev', 'Run streamlit', 'streamlit run app.py'),
                ('install', 'Install deps', 'pip install -r requirements.txt'),
            ],
            'python': [
                ('dev', 'Run main.py', 'python main.py'),
                ('install', 'Install deps', 'pip install -r requirements.txt'),
                ('venv', 'Create venv', 'python -m venv venv'),
            ],
            'foundry': [
                ('build', 'Build contracts', 'forge build'),
                ('test', 'Run tests', 'forge test'),
                ('deploy', 'Deploy', 'forge script'),
            ],
            'hardhat': [
                ('compile', 'Compile contracts', 'npx hardhat compile'),
                ('test', 'Run tests', 'npx hardhat test'),
                ('deploy', 'Deploy', 'npx hardhat run scripts/deploy.js'),
            ],
        }
        
        return actions.get(self.project_type, [])
    
    def log_visit(self):
        """Log current project visit for recent tracking"""
        if not self.project_name:
            return
        
        try:
            data = json.loads(self.history_file.read_text())
            
            # Update visits count
            visits = data.get('visits', {})
            visits[self.project_name] = visits.get(self.project_name, 0) + 1
            
            # Update recent list
            recent = data.get('recent', [])
            entry = {
                'name': self.project_name,
                'type': self.project_type,
                'timestamp': datetime.now().isoformat(),
                'path': str(self.cwd)
            }
            
            # Remove if already in recent
            recent = [r for r in recent if r['name'] != self.project_name]
            # Add to front
            recent.insert(0, entry)
            # Keep only last 20
            recent = recent[:20]
            
            data['recent'] = recent
            data['visits'] = visits
            
            self.history_file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            # Silent fail - history is not critical
            pass
    
    def log_command(self, command):
        """Log command for history"""
        try:
            data = json.loads(self.history_file.read_text())
            commands = data.get('commands', [])
            
            entry = {
                'command': command,
                'timestamp': datetime.now().isoformat(),
                'project': self.project_name,
                'path': str(self.cwd)
            }
            
            commands.insert(0, entry)
            commands = commands[:100]  # Keep last 100 commands
            
            data['commands'] = commands
            self.history_file.write_text(json.dumps(data, indent=2))
        except:
            pass
    
    def get_recent_projects(self, limit=10, days=7):
        """Get recent projects with filtering"""
        try:
            data = json.loads(self.history_file.read_text())
            recent = data.get('recent', [])
            
            # Filter by date if specified
            if days:
                cutoff = datetime.now() - timedelta(days=days)
                recent = [
                    r for r in recent 
                    if datetime.fromisoformat(r['timestamp']) > cutoff
                ]
            
            return recent[:limit]
        except:
            return []
    
    def add_favorite(self, project_name):
        """Add project to favorites"""
        try:
            data = json.loads(self.history_file.read_text())
            favorites = data.get('favorites', [])
            
            if project_name not in favorites:
                favorites.append(project_name)
                data['favorites'] = favorites
                self.history_file.write_text(json.dumps(data, indent=2))
                return True
            return False
        except:
            return False
    
    def get_favorites(self):
        """Get favorite projects"""
        try:
            data = json.loads(self.history_file.read_text())
            return data.get('favorites', [])
        except:
            return []
