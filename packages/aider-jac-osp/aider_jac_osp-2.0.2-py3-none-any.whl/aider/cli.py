#!/usr/bin/env python3
"""
Aider-Genius Command Line Interface
Professional autonomous coding assistant with Jac-OSP integration
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add aider to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aider.integration.jac_bridge import JacBridge
from aider.integration.file_editor import AutoEditor
from aider.integration.llm_client import LLMClient

console = Console()

class AiderGeniusCLI:
    def __init__(self):
        self.project_root = os.getcwd()
        self.jac_bridge = None
        self.auto_editor = None
        self.llm_client = None
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all system components"""
        try:
            # Initialize Jac Bridge
            bridge_root = os.path.dirname(os.path.abspath(__file__))
            self.jac_bridge = JacBridge(bridge_root)
            
            # Initialize Auto Editor
            self.auto_editor = AutoEditor(self.jac_bridge)
            
            # Initialize LLM Client (will handle API key loading)
            self.llm_client = LLMClient()
            
            console.print("✨ [green]All components initialized successfully[/green]")
        except Exception as e:
            console.print(f"Warning: Component initialization issue - {e}")
    
    def analyze_project(self, target_dir: str = None) -> Dict[str, Any]:
        """Analyze project using OSP ranking algorithms"""
        if not target_dir:
            target_dir = self.project_root
            
        console.print(f"Analyzing project: {target_dir}")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Executing OSP analysis...", total=None)
            
            # Execute Jac OSP ranking
            try:
                osp_result = self.jac_bridge.call_walker(
                    "file_analysis", "get_osp_ranking", 
                    {"target_dir": target_dir}
                )
                progress.update(task, description="✓ OSP analysis complete")
                return osp_result
            except Exception as e:
                progress.update(task, description=f"✗ OSP analysis failed: {e}")
                return {"error": str(e)}
    
    def optimize_tokens(self, file_path: str = None) -> Dict[str, Any]:
        """Execute token usage optimization"""
        console.print("Executing token optimization...")
        
        try:
            if file_path and os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    code = f.read()
            else:
                # Project-wide optimization
                code = "# Project-wide optimization"
            
            result = self.jac_bridge.call_walker(
                "token_optimizer", "optimize_prompt",
                {"code": code}
            )
            
            console.print("✓ Token optimization complete")
            return result
            
        except Exception as e:
            console.print(f"✗ Token optimization failed: {e}")
            return {"error": str(e)}
    
    def auto_edit(self, task: str, files: List[str] = None) -> Dict[str, Any]:
        """Execute autonomous code editing using OSP guidance"""
        console.print(f"Executing autonomous edit: {task}")
        
        if not files:
            # Use OSP to identify relevant files
            console.print("Using OSP to find relevant files...")
            osp_result = self.analyze_project()
            if "ranked_files" in osp_result:
                files = [f["path"] for f in osp_result["ranked_files"][:3]]
            else:
                files = []
        
        if not files:
            return {"error": "No relevant files identified"}
        
        console.print(f"🔧 Targeting files: {files}")
        
        # Execute autonomous editing
        try:
            result = self.auto_editor.autonomous_edit(task, files)
            console.print(f"🔍 Autonomous edit result: {result}")
            return result
        except Exception as e:
            console.print(f"✗ Autonomous editing failed: {e}")
            return {"error": str(e)}
    
    def setup_config(self) -> bool:
        """Initialize system configuration"""
        console.print("Setting up Aider-Genius configuration...")
        
        config_dir = Path.home() / ".aider-genius"
        config_dir.mkdir(exist_ok=True)
        
        config_file = config_dir / "config.json"
        
        if not config_file.exists():
            default_config = {
                "llm_provider": "openai",
                "model": "gpt-4",
                "max_tokens": 4000,
                "temperature": 0.2,
                "osp_enabled": True,
                "token_optimization": True,
                "git_safety": True,
                "backup_enabled": True
            }
            
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            console.print("Configuration setup complete.")
            console.print("Add your API key to complete setup:")
            console.print(f"   Edit: {config_file}")
            console.print("   Add: 'api_key': 'your-api-key-here'")
            
        else:
            console.print("Configuration already exists")
            
        return True

def create_parser():
    """Create command line argument parser with enhanced formatting"""
    parser = argparse.ArgumentParser(
        description="🧠 Aider-Genius: Professional AI Coding Assistant with Jac-OSP",
        epilog="""
╭─ EXAMPLES ─────────────────────────────────────────╮
│                                                    │
│  📊 aider-genius analyze                           │
│      → Analyze project with OSP spatial ranking   │
│                                                    │
│  💰 aider-genius optimize main.py                  │
│      → Optimize token usage for cost efficiency   │
│                                                    │
│  🤖 aider-genius edit 'add error handling'        │
│      → Autonomous code editing with AI            │
│                                                    │
│  ⚙️  aider-genius setup                            │
│      → Configure API keys and system settings     │
│                                                    │
╰────────────────────────────────────────────────────╯
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('command', 
                       choices=['analyze', 'optimize', 'edit', 'setup'],
                       help='🎯 Command to execute')
    
    parser.add_argument('target', nargs='?',
                       help='📁 Target file or task description')
    
    parser.add_argument('--files', nargs='+',
                       help='📄 Specific files to target')
    
    parser.add_argument('--dir', 
                       help='📂 Target directory (default: current)')
    
    parser.add_argument('--dry-run', action='store_true',
                       help='🔍 Show what would be done without making changes')
    
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='📝 Verbose output')
    
    return parser

def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Initialize CLI
    cli = AiderGeniusCLI()
    
    console.print(Panel.fit(
        "[bold cyan]🧠 AIDER-GENIUS[/bold cyan]\n"
        "[green]Autonomous AI Coding Assistant[/green]\n"
        "[dim]Powered by Jac Object-Spatial Programming[/dim]",
        style="bold blue",
        border_style="cyan"
    ))
    
    # Execute commands
    if args.command == 'setup':
        cli.setup_config()
        
    elif args.command == 'analyze':
        target_dir = args.dir or args.target or os.getcwd()
        result = cli.analyze_project(target_dir)
        
        if "error" not in result:
            console.print("\n📊 [bold green]OSP SPATIAL ANALYSIS RESULTS[/bold green]")
            console.print("─" * 60)
            if "ranked_files" in result:
                for i, file_info in enumerate(result["ranked_files"][:5], 1):
                    relevance = file_info['relevance']
                    file_path = file_info['path']
                    
                    # Color-code relevance scores
                    if relevance >= 0.7:
                        color = "bright_green"
                        icon = "🟢"
                    elif relevance >= 0.4:
                        color = "yellow"
                        icon = "🟡"
                    else:
                        color = "bright_black"
                        icon = "⚪"
                    
                    console.print(f"  {icon} [{color}]{i:2d}. {file_path}[/{color}]")
                    console.print(f"     └─ Relevance: [{color}]{relevance:.2f}[/{color}] | Lines: {file_info.get('lines', 'N/A')}")
            
            console.print(f"\n💡 [dim]Analyzed {result.get('total_files_analyzed', 'N/A')} files total[/dim]")
        else:
            console.print(f"❌ [red]Analysis failed: {result['error']}[/red]")
    
    elif args.command == 'optimize':
        target_file = args.target
        result = cli.optimize_tokens(target_file)
        
        if "error" not in result:
            console.print("\n💰 [bold cyan]TOKEN OPTIMIZATION RESULTS[/bold cyan]")
            console.print("─" * 50)
            
            original = result.get('original_tokens', 'N/A')
            optimized = result.get('optimized_tokens', 'N/A')
            savings = result.get('savings_percent', 0)
            
            console.print(f"  📈 Original:   [red]{original:>6}[/red] tokens")
            console.print(f"  📉 Optimized:  [green]{optimized:>6}[/green] tokens")
            
            if savings > 0:
                console.print(f"  💸 Savings:    [bold green]{savings:>6.1f}%[/bold green] reduction")
            else:
                console.print(f"  ℹ️  Savings:    [yellow]  0.0%[/yellow] (already optimized)")
            
            if savings >= 30:
                console.print("  🎉 [green]Excellent optimization![/green]")
            elif savings >= 15:
                console.print("  👍 [yellow]Good optimization[/yellow]")
        else:
            console.print(f"❌ [red]Optimization failed: {result['error']}[/red]")
    
    elif args.command == 'edit':
        if not args.target:
            console.print("✗ Please provide a task description for editing")
            return
            
        task = args.target
        files = args.files
        
        if args.dry_run:
            console.print("\n🔍 [bold yellow]DRY RUN PREVIEW[/bold yellow]")
            console.print("─" * 40)
            console.print(f"  📋 Would Execute: [cyan]{task}[/cyan]")
            if files:
                console.print(f"  📁 Target Files:")
                for file in files:
                    console.print(f"     └─ [blue]{file}[/blue]")
            else:
                console.print(f"  🎯 Files: [yellow]Auto-selected using OSP ranking[/yellow]")
            console.print("\n💡 [dim]Use without --dry-run to execute[/dim]")
            return
        
        result = cli.auto_edit(task, files)
        
        if "error" not in result:
            console.print("\n🤖 [bold magenta]AUTONOMOUS EDITING RESULTS[/bold magenta]")
            console.print("─" * 55)
            
            task_desc = result.get('task', task)
            files_modified = result.get('files_modified', len(result.get('changes', [])))
            success_status = result.get('success', False)
            
            console.print(f"  📋 Task: [cyan]{task_desc}[/cyan]")
            console.print(f"  📁 Files Modified: [green]{files_modified}[/green]")
            console.print(f"  ✅ Status: [{'green' if success_status else 'red'}]{'Success' if success_status else 'Failed'}[/{'green' if success_status else 'red'}]")
            
            if result.get('changes'):
                console.print("\n  📝 [bold]Changes Applied:[/bold]")
                for change in result['changes']:
                    file_name = Path(change['file']).name
                    console.print(f"     └─ [blue]{file_name}[/blue]: {change.get('reasoning', 'Modified')}")
        else:
            console.print(f"❌ [red]Edit failed: {result['error']}[/red]")
    
    console.print("\n" + "─" * 60)
    console.print("💡 [bold cyan]Use --help for more options[/bold cyan] | 🚀 [dim]Powered by OSP Intelligence[/dim]")

if __name__ == "__main__":
    main()
