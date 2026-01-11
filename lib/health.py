"""
Health - git/python/node checks and fixes
"""

from pathlib import Path
from rich.console import Console
from rich.prompt import Confirm
import subprocess
import shutil

console = Console()

class Health:
    def __init__(self, ctx):
        self.ctx = ctx
        self.dojo_root = ctx.dojo_root
    
    def run_check(self):
        """Run all health checks"""
        console.print("\n ⛄ [accent]HEALTH CHECK[/]\n")
        
        with console.status(" Checking git repos...", spinner="dots"):
            git_results = self._check_git()
        
        total_repos = len(git_results)
        synced = sum(1 for r in git_results if r['synced'])
        
        if synced == total_repos:
            console.print(f" [success]✓[/] Git: All {total_repos} repos synced")
        else:
            console.print(f" [warning]⚠[/]  Git: {synced}/{total_repos} repos synced")
            for r in git_results:
                if not r['synced']:
                    console.print(f"   [dim]{r['name']}: {r['issue']}[/]")
        console.print()
        
        with console.status(" Checking python environments...", spinner="dots"):
            python_results = self._check_python()
        
        total_py = len(python_results)
        healthy_py = sum(1 for r in python_results if r['healthy'])
        
        if healthy_py == total_py and total_py > 0:
            console.print(f" [success]✓[/] Python: All {total_py} venvs healthy")
        elif total_py > 0:
            console.print(f" [warning]⚠[/]  Python: {healthy_py}/{total_py} venvs healthy")
            for r in python_results:
                if not r['healthy']:
                    console.print(f"   [dim]{r['name']}: {r['issue']}[/]")
        else:
            console.print(" [dim]No Python projects found[/]")
        console.print()
        
        with console.status(" Checking node projects...", spinner="dots"):
            node_results = self._check_node()
        
        total_node = len(node_results)
        if total_node > 0:
            console.print(f" [success]✓[/] Node: {total_node} projects found")
            outdated = [r for r in node_results if r.get('outdated', 0) > 0]
            if outdated:
                for r in outdated:
                    console.print(f"   [warning]{r['name']}: {r['outdated']} packages outdated[/]")
        else:
            console.print(" [dim]No Node projects found[/]")
        console.print()
        
        issues = (not all(r['synced'] for r in git_results) or 
                 not all(r['healthy'] for r in python_results))
        
        if issues and Confirm.ask(" [text]Run automated fixes?[/]"):
            console.print()
            self._auto_fix(git_results, python_results)
    
    def _check_git(self):
        """Check all git repos"""
        results = []
        
        for path in self._find_git_repos():
            try:
                result = subprocess.run(
                    ['git', 'status', '-sb'],
                    cwd=path,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                status = result.stdout
                name = path.relative_to(self.dojo_root)
                
                if 'ahead' in status:
                    results.append({'name': str(name), 'synced': False, 'issue': 'unpushed commits'})
                elif 'behind' in status:
                    results.append({'name': str(name), 'synced': False, 'issue': 'behind origin'})
                elif 'Your branch is up to date' in status or 'branch.head' in status:
                    results.append({'name': str(name), 'synced': True, 'issue': None})
                else:
                    has_changes = bool([l for l in status.split('\n') if l.strip() and not l.startswith('#')])
                    if has_changes:
                        results.append({'name': str(name), 'synced': False, 'issue': 'uncommitted changes'})
                    else:
                        results.append({'name': str(name), 'synced': True, 'issue': None})
            except:
                results.append({'name': str(path.relative_to(self.dojo_root)), 'synced': False, 'issue': 'error'})
        
        return results
    
    def _find_git_repos(self):
        """Find all .git folders"""
        repos = []
        for path in self.dojo_root.rglob('.git'):
            if path.is_dir():
                repos.append(path.parent)
        return repos
    
    def _check_python(self):
        """Check Python projects"""
        results = []
        
        for path in self._find_python_projects():
            name = path.relative_to(self.dojo_root)
            venv_path = path / 'venv'
            
            if not venv_path.exists():
                results.append({'name': str(name), 'healthy': False, 'issue': 'no venv'})
                continue
            
            req_file = path / 'requirements.txt'
            if req_file.exists():
                site_packages = venv_path / 'lib'
                has_packages = any(site_packages.rglob('site-packages'))
                
                if has_packages:
                    results.append({'name': str(name), 'healthy': True, 'issue': None})
                else:
                    results.append({'name': str(name), 'healthy': False, 'issue': 'missing deps'})
            else:
                results.append({'name': str(name), 'healthy': True, 'issue': None})
        
        return results
    
    def _find_python_projects(self):
        """Find Python projects"""
        projects = []
        for req in self.dojo_root.rglob('requirements.txt'):
            projects.append(req.parent)
        return projects
    
    def _check_node(self):
        """Check Node projects"""
        results = []
        
        for path in self._find_node_projects():
            name = path.relative_to(self.dojo_root)
            
            if not (path / 'node_modules').exists():
                results.append({'name': str(name), 'outdated': 0, 'missing': True})
            else:
                results.append({'name': str(name), 'outdated': 0, 'missing': False})
        
        return results
    
    def _find_node_projects(self):
        """Find Node projects"""
        projects = []
        for pkg in self.dojo_root.rglob('package.json'):
            if 'node_modules' not in pkg.parts:
                projects.append(pkg.parent)
        return projects
    
    def _auto_fix(self, git_results, python_results):
        """Run automated fixes"""
        behind = [r for r in git_results if r.get('issue') == 'behind origin']
        if behind:
            console.print(" [accent]Pulling repos...[/]")
            for r in behind:
                path = self.dojo_root / r['name']
                console.print(f"   {r['name']}...", end="")
                try:
                    subprocess.run(['git', 'pull'], cwd=path, capture_output=True, timeout=30)
                    console.print(" [success]✓[/]")
                except:
                    console.print(" [error]✗[/]")
        
        missing_venv = [r for r in python_results if r.get('issue') == 'no venv']
        if missing_venv:
            console.print("\n [accent]Creating venvs...[/]")
            for r in missing_venv:
                path = self.dojo_root / r['name']
                console.print(f"   {r['name']}...", end="")
                try:
                    subprocess.run(['python', '-m', 'venv', 'venv'], cwd=path, timeout=60)
                    console.print(" [success]✓[/]")
                except:
                    console.print(" [error]✗[/]")
        
        console.print("\n [success]Done![/]\n")
    
    def sync_repos(self):
        """Pull all git repos"""
        console.print("\n [accent]SYNCING ALL REPOS[/]\n")
        
        repos = self._find_git_repos()
        
        for repo in repos:
            name = repo.relative_to(self.dojo_root)
            console.print(f" {name}...", end="")
            
            try:
                result = subprocess.run(
                    ['git', 'pull'],
                    cwd=repo,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if 'Already up to date' in result.stdout:
                    console.print(" [dim]✓[/]")
                else:
                    console.print(" [success]✓ updated[/]")
            except:
                console.print(" [error]✗[/]")
        
        console.print()
    
    def clean(self, deep=False):
        """Clean build artifacts"""
        console.print("\n [accent]CLEANING BUILD ARTIFACTS[/]\n")
        
        patterns = ['__pycache__', '*.pyc', '.pytest_cache']
        if deep:
            patterns.extend(['node_modules', '.next', 'dist', 'build', 'out'])
        
        console.print(f" Searching for: {', '.join(patterns)}\n")
        
        to_delete = []
        total_size = 0
        
        with console.status(" Scanning...", spinner="dots"):
            for pattern in patterns:
                for path in self.dojo_root.rglob(pattern):
                    if path.is_dir():
                        size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
                        to_delete.append((path, size))
                        total_size += size
        
        if not to_delete:
            console.print(" [dim]Nothing to clean[/]\n")
            return
        
        console.print(f" Found {len(to_delete)} items ({total_size / 1024 / 1024:.1f} MB)\n")
        
        for path, size in sorted(to_delete, key=lambda x: x[1], reverse=True)[:10]:
            rel_path = path.relative_to(self.dojo_root)
            console.print(f"   {rel_path} [dim]({size / 1024 / 1024:.1f} MB)[/]")
        
        if len(to_delete) > 10:
            console.print(f"   [dim]... and {len(to_delete) - 10} more[/]")
        
        console.print()
        
        if Confirm.ask(" [text]Delete these files?[/]"):
            console.print()
            for path, _ in to_delete:
                try:
                    shutil.rmtree(path)
                except:
                    pass
            console.print(" [success]Cleaned![/]\n")
