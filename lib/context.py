"""
Context - Smart project detection with learning mode and history
"""

from pathlib import Path
import json
from datetime import datetime
import subprocess

class DojoContext:
    def __init__(self):
        self.cwd = Path.cwd()
        self.dojo_root = Path.home() / 'dojo'
        self.config_dir = Path.home() / '.config' / 'dojo'
        self.history_file = self.config_dir / 'history.json'
        self.config_file = self.config_dir / 'config.json'
        
        # Ensure config exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        if not self.history_file.exists():
            self.history_file.write_text(json.dumps({
                'recent': [], 
                'visits': {},
                'command_history': []
            }, indent=2))
        
        if not self.config_file.exists():
            self.config_file.write_text(json.dumps({
                'learning_mode': False,
                'version': 'v2',
                'theme': 'snowzies',
                'auto_open_browser': True
            }, indent=2))
        
        self.config = self._load_config()
        self.project_type = self.detect_type()
        self.project_name = self.get_project_name()
        self.git_status = self.get_git_status()
        
        # Log this visit
        self.log_visit()
    
    def _load_config(self):
        """Load user config"""
        try:
            return json.loads(self.config_file.read_text())
        except:
            return {'learning_mode': False, 'version': 'v2'}
    
    def save_config(self, key, value):
        """Update config value"""
        self.config[key] = value
        self.config_file.write_text(json.dumps(self.config, indent=2))
    
    def is_learning_mode(self):
        """Check if learning mode is enabled"""
        return self.config.get('learning_mode', False)
    
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
            rel_path = self.cwd.relative_to(self.dojo_root)
            parts = rel_path.parts
            
            # Check new structure (work/lab/research)
            if len(parts) >= 2 and parts[0] in ['work', 'lab', 'research']:
                if len(parts) >= 3:
                    return f"{parts[0]}/{parts[1]}/{parts[2]}"
                return f"{parts[0]}/{parts[1]}"
            
            # Legacy structure (apps/bots/tools)
            if len(parts) >= 2 and parts[0] in ['apps', 'bots', 'tools', 'contracts', 'protocols', 'experiments']:
                return f"{parts[0]}/{parts[1]}"
            
            return str(rel_path)
        except:
            return None
    
    def detect_type(self):
        """Auto-detect project type with detailed classification"""
        checks = [
            ('package.json', self._check_node),
            ('app.py', lambda: 'streamlit'),
            ('requirements.txt', lambda: 'python'),
            ('foundry.toml', lambda: 'foundry'),
            ('Cargo.toml', lambda: 'rust'),
            ('go.mod', lambda: 'go'),
        ]
        
        for file, checker in checks:
            if (self.cwd / file).exists():
                return checker() if callable(checker) else checker
        
        return 'folder'
    
    def _check_node(self):
        """Detailed Node.js project detection"""
        # Check for Next.js
        if (self.cwd / 'next.config.ts').exists() or (self.cwd / 'next.config.js').exists():
            return 'nextjs'
        
        # Check for Next.js app directory
        if (self.cwd / 'app').is_dir() and (self.cwd / 'package.json').exists():
            try:
                pkg = json.loads((self.cwd / 'package.json').read_text())
                if 'next' in pkg.get('dependencies', {}):
                    return 'nextjs'
            except:
                pass
        
        try:
            pkg = json.loads((self.cwd / 'package.json').read_text())
            deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
            
            if 'react' in deps:
                return 'react'
            elif 'express' in deps:
                return 'express'
            elif 'vite' in deps:
                return 'vite'
        except:
            pass
        
        return 'node'
    
    def get_git_status(self):
        """Get git status for current directory"""
        try:
            result = subprocess.run(
                ['git', 'status', '-sb'],
                cwd=self.cwd,
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode != 0:
                return None
            
            status = result.stdout
            return {
                'branch': self._extract_branch(status),
                'ahead': 'ahead' in status,
                'behind': 'behind' in status,
                'synced': 'up to date' in status.lower() or 'up-to-date' in status.lower(),
                'clean': not bool([l for l in status.split('\n')[1:] if l.strip()])
            }
        except:
            return None
    
    def _extract_branch(self, status):
        """Extract branch name from git status"""
        try:
            first_line = status.split('\n')[0]
            if '...' in first_line:
                return first_line.split('...')[0].replace('##', '').strip()
            return first_line.replace('##', '').strip()
        except:
            return 'unknown'
    
    def get_quick_actions(self):
        """Return available quick actions for current project"""
        actions = {
            'nextjs': [
                ('dev', 'Start dev server', 'npm run dev', 'Runs Next.js development server on http://localhost:3000'),
                ('build', 'Build for production', 'npm run build', 'Creates optimized production build in .next/'),
                ('test', 'Run tests', 'npm test', 'Executes Jest test suite'),
            ],
            'react': [
                ('dev', 'Start dev server', 'npm start', 'Launches React dev server with hot reload'),
                ('build', 'Build', 'npm run build', 'Creates production build in build/ directory'),
                ('test', 'Test', 'npm test', 'Runs test suite in watch mode'),
            ],
            'node': [
                ('dev', 'Start dev', 'npm run dev', 'Starts development server (usually with nodemon)'),
                ('start', 'Start', 'npm start', 'Runs the production server'),
                ('install', 'Install deps', 'npm install', 'Installs all dependencies from package.json'),
            ],
            'streamlit': [
                ('dev', 'Run streamlit', f'streamlit run app.py', 'Launches Streamlit app in browser'),
                ('install', 'Install deps', 'pip install -r requirements.txt', 'Installs Python dependencies'),
            ],
            'python': [
                ('dev', 'Run main.py', 'python main.py', 'Executes main Python script'),
                ('install', 'Install deps', 'pip install -r requirements.txt', 'Installs required packages'),
                ('venv', 'Create venv', 'python -m venv venv', 'Creates virtual environment'),
            ],
            'foundry': [
                ('build', 'Build contracts', 'forge build', 'Compiles Solidity contracts'),
                ('test', 'Run tests', 'forge test', 'Runs Foundry test suite'),
                ('deploy', 'Deploy', 'forge script', 'Deploys contracts using scripts'),
            ],
        }
        
        return actions.get(self.project_type, [])
    
    def get_context_help(self):
        """Get contextual help based on current location"""
        if not self.is_in_dojo():
            return {
                'location': 'Outside Dojo',
                'suggestions': ['cd ~/dojo', 'dojo goto <project>']
            }
        
        actions = self.get_quick_actions()
        
        return {
            'location': self.project_name or 'Dojo root',
            'type': self.project_type,
            'actions': [a[0] for a in actions],
            'git': self.git_status
        }
    
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
        except Exception:
            pass
    
    def log_command(self, command, args):
        """Log command execution"""
        try:
            data = json.loads(self.history_file.read_text())
            cmd_history = data.get('command_history', [])
            
            cmd_history.append({
                'command': command,
                'args': args,
                'timestamp': datetime.now().isoformat(),
                'project': self.project_name
            })
            
            # Keep last 100 commands
            data['command_history'] = cmd_history[-100:]
            self.history_file.write_text(json.dumps(data, indent=2))
        except Exception:
            pass
    
    def needs_migration(self):
        """Check if old folder structure exists"""
        old_folders = ['apps', 'bots', 'experiments', 'protocols']
        return any((self.dojo_root / folder).exists() for folder in old_folders)
