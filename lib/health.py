"""
Health - Enhanced with auto-fix capabilities
"""

from pathlib import Path
from rich.console import Console
from rich.prompt import Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
import subprocess
import shutil

console = Console()

class Health:
    def __init__(self, ctx):
        self.ctx = ctx
        self.dojo_root = ctx.dojo_root
    
    def run_check(self):
        """Run all health checks with actionable fixes"""
        console.print("\n ⛄ [accent]HEALTH CHECK[/]\n")
        
        git_issues = []
        python_issues = []
        node_issues = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            task1 = progress.add_task(" Checking git repos...", total=None)
            git_results = self._check_git()
            progress.remove_task(task1)
            
            task2 = progress.add_task(" Checking python environments...", total=None)
            python_results = self._check_python()
            progress.remove_task(task2)
            
            task3 = progress.add_task(" Checking node projects...", total=None)
            node_results = self._check_node()
            progress.remove_task(task3)
        
        # Git results
        total_repos = len(git_results)
        synced = sum(1 for r in git_results if r['synced'])
        
        if synced == total_repos:
            console.print(f" [success]✓[/] Git: All {total_repos} repos synced")
        else:
            console.print(f" [warning]⚠[/]  Git: {synced}/{total_repos} repos synced")
            for r in git_results:
                if not r['synced']:
                    console.print(f"   [dim]{r['name']}: {r['issue']}[/]")
                    git_issues.append(r)
        console.print()
        
        # Python results
        total_py = len(python_results)
        healthy_py = sum(1 for r in python_results if r['healthy'])
        
        if healthy_py == total_py and total_py > 0:
            console.print(f" [success]✓[/] Python: All {total_py} venvs healthy")
        elif total_py > 0:
            console.print(f" [warning]⚠[/]  Python: {healthy_py}/{total_py} venvs healthy")
            for r in python_results:
                if not r['healthy']:
                    console.print(f"   [dim]{r['name']}: {r['issue']}[/]")
                    python_issues.append(r)
        else:
            console.print(" [dim]No Python projects found[/]")
        console.print()
        
        # Node results
        total_node = len(node_results)
        if total_node > 0:
            missing_nm = sum(1 for r in node_results if r.get('missing', False))
            if missing_nm == 0:
                console.print(f" [success]✓[/] Node: All {total_node} projects have dependencies")
            else:
                console.print(f" [warning]⚠[/]  Node: {missing_nm}/{total_node} projects missing node_modules")
                for r in node_results:
                    if r.get('missing'):
                        console.print(f"   [dim]{r['name']}: missing node_modules[/]")
                        node_issues.append(r)
        else:
            console.print(" [dim]No Node projects found[/]")
        console.print()
        
        # Offer quick fixes
        has_issues = git_issues or python_issues or node_issues
        
        if has_issues:
            console.print(" [accent]⚡ QUICK FIXES AVAILABLE:[/]\n")
            if git_issues:
                console.print("   dojo fix git        # Sync all repos")
            if python_issues:
                console.print("   dojo fix python     # Fix venv issues")
            if node_issues:
                console.print("   dojo fix node       # Install missing deps")
            console.print("   dojo fix all        # Fix everything\n")
            
            if Confirm.ask(" [text]Run automated fixes now?[/]"):
                console.print()
                self._auto_fix(git_results, python_results, node_results)
        else:
            console.print(" [success]Everything looks healthy! ✨[/]\n")
    
    def auto_fix(self, target):
        """Run specific auto-fix"""
        console.print(f"\n [accent]FIXING: {target.upper()}[/]\n")
        
        if target == 'git':
            git_results = self._check_git()
            self._fix_git(git_results)
        elif target == 'python':
            python_results = self._check_python()
            self._fix_python(python_results)
        elif target == 'node':
            node_results = self._check_node()
            self._fix_node(node_results)
        elif target == 'all':
            git_results = self._check_git()
            python_results = self._check_python()
            node_results = self._check_node()
            self._auto_fix(git_results, python_results, node_results)
        else:
            console.print(f" [error]Unknown target: {target}[/]")
            console.print(" [dim]Try: git, python, node, or all[/]\n")
    
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
                    results.append({'name': str(name), 'synced': False, 'issue': 'unpushed commits', 'path': path})
                elif 'behind' in status:
                    results.append({'name': str(name), 'synced': False, 'issue': 'behind origin', 'path': path})
                elif 'Your branch is up to date' in status or 'branch.head' in status:
                    results.append({'name': str(name), 'synced': True, 'issue': None, 'path': path})
                else:
                    has_changes = bool([l for l in status.split('\n') if l.strip() and not l.startswith('#')])
                    if has_changes:
                        results.append({'name': str(name), 'synced': False, 'issue': 'uncommitted changes', 'path': path})
                    else:
                        results.append({'name': str(name), 'synced': True, 'issue': None, 'path': path})
            except:
                results.append({'name': str(path.relative_to(self.dojo_root)), 'synced': False, 'issue': 'error', 'path': path})
        
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
                results.append({'name': str(name), 'healthy': False, 'issue': 'no venv', 'path': path})
                continue
            
            req_file = path / 'requirements.txt'
            if req_file.exists():
                site_packages = venv_path / 'lib'
                has_packages = any(site_packages.rglob('site-packages'))
                
                if has_packages:
                    results.append({'name': str(name), 'healthy': True, 'issue': None, 'path': path})
                else:
                    results.append({'name': str(name), 'healthy': False, 'issue': 'missing deps', 'path': path})
            else:
                results.append({'name': str(name), 'healthy': True, 'issue': None, 'path': path})
        
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
                results.append({'name': str(name), 'outdated': 0, 'missing': True, 'path': path})
            else:
                results.append({'name': str(name), 'outdated': 0, 'missing': False, 'path': path})
        
        return results
    
    def _find_node_projects(self):
        """Find Node projects"""
        projects = []
        for pkg in self.dojo_root.rglob('package.json'):
            if 'node_modules' not in pkg.parts:
                projects.append(pkg.parent)
        return projects
    
    def _auto_fix(self, git_results, python_results, node_results):
        """Run all automated fixes"""
        self._fix_git(git_results)
        self._fix_python(python_results)
        self._fix_node(node_results)
        
        console.print("\n [success]All fixes complete! ✨[/]\n")
    
    def _fix_git(self, git_results):
        """Fix git issues"""
        behind = [r for r in git_results if r.get('issue') == 'behind origin']
        if behind:
            console.print(" [accent]Pulling repos...[/]")
            for r in behind:
                console.print(f"   {r['name']}...", end="")
                try:
                    subprocess.run(['git', 'pull'], cwd=r['path'], capture_output=True, timeout=30)
                    console.print(" [success]✓[/]")
                except:
                    console.print(" [error]✗[/]")
            console.print()
    
    def _fix_python(self, python_results):
        """Fix Python issues"""
        missing_venv = [r for r in python_results if r.get('issue') == 'no venv']
        if missing_venv:
            console.print(" [accent]Creating venvs...[/]")
            for r in missing_venv:
                console.print(f"   {r['name']}...", end="")
                try:
                    subprocess.run(['python3', '-m', 'venv', 'venv'], cwd=r['path'], capture_output=True, timeout=60)
                    console.print(" [success]✓[/]")
                except:
                    console.print(" [error]✗[/]")
            console.print()
        
        missing_deps = [r for r in python_results if r.get('issue') == 'missing deps']
        if missing_deps:
            console.print(" [accent]Installing dependencies...[/]")
            for r in missing_deps:
                console.print(f"   {r['name']}...", end="")
                try:
                    venv_pip = r['path'] / 'venv' / 'bin' / 'pip'
                    subprocess.run(
                        [str(venv_pip), 'install', '-r', 'requirements.txt'],
                        cwd=r['path'],
                        capture_output=True,
                        timeout=300
                    )
                    console.print(" [success]✓[/]")
                except:
                    console.print(" [error]✗[/]")
            console.print()
    
    def _fix_node(self, node_results):
        """Fix Node issues"""
        missing = [r for r in node_results if r.get('missing')]
        if missing:
            console.print(" [accent]Installing node_modules...[/]")
            for r in missing:
                console.print(f"   {r['name']}...", end="")
                try:
                    subprocess.run(['npm', 'install'], cwd=r['path'], capture_output=True, timeout=300)
                    console.print(" [success]✓[/]")
                except:
                    console.print(" [error]✗[/]")
            console.print()
    
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
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(" Scanning...", total=None)
            
            for pattern in patterns:
                for path in self.dojo_root.rglob(pattern):
                    if path.is_dir():
                        try:
                            size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
                            to_delete.append((path, size))
                            total_size += size
                        except:
                            pass
            
            progress.remove_task(task)
        
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
