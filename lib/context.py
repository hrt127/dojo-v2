"""
Context detection - knows where you are and what you can do
"""

from pathlib import Path
import json
from datetime import datetime

class DojoContext:
    def __init__(self):
        self.cwd = Path.cwd()
        self.dojo_root = Path.home() / 'dojo'
        self.config_dir = Path.home() / '.config' / 'dojo'
        self.history_file = self.config_dir / 'history.json'
        
        # Ensure config exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        if not self.history_file.exists():
            self.history_file.write_text('{"recent": [], "visits": {}}')
        
        self.project_type = self.detect_type()
        self.project_name = self.get_project_name()
        
        # Log this visit
        self.log_visit()
    
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
            if len(parts) >= 2 and parts[0] in ['apps', 'bots', 'tools', 'contracts']:
                return f"{parts[0]}/{parts[1]}"
            return str(rel_path)
        except:
            return None
    
    def detect_type(self):
        """Auto-detect project type"""
        checks = [
            ('package.json', self._check_node),
            ('app.py', lambda: 'streamlit'),
            ('requirements.txt', lambda: 'python'),
            ('foundry.toml', lambda: 'foundry'),
            ('Cargo.toml', lambda: 'rust'),
        ]
        
        for file, checker in checks:
            if (self.cwd / file).exists():
                return checker() if callable(checker) else checker
        
        return 'folder'
    
    def _check_node(self):
        """Detailed Node.js project detection"""
        if (self.cwd / 'next.config.ts').exists() or (self.cwd / 'next.config.js').exists():
            return 'nextjs'
        
        try:
            import json
            pkg = json.loads((self.cwd / 'package.json').read_text())
            deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
            
            if 'react' in deps:
                return 'react'
            elif 'express' in deps:
                return 'express'
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
            'node': [
                ('dev', 'Start dev', 'npm run dev'),
                ('start', 'Start', 'npm start'),
                ('install', 'Install deps', 'npm install'),
            ],
            'streamlit': [
                ('dev', 'Run streamlit', f'streamlit run app.py'),
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
