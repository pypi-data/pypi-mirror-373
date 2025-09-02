import argparse
import os
import tempfile
import shutil
import json
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

from titanshield_cli.reporter import generate_sarif_report 
from .decompiler import decompile_apk
from .rule_engine import load_rules_from_dir, run_rules_on_file
# from .reporter import generate_sarif

def cli():
    parser = argparse.ArgumentParser(description="Tianshield CLI - Static Analysis for Android APKs")
    parser.add_argument("apk_path", help="Path to the APK file to analyze.")
    parser.add_argument("--max-mem", default="4g", help="Maximum memory for JADX (e.g., '2g', '4096m'). Defaults to 4g.")
    parser.add_argument("--output", "-o", default="console", help="Output format (console or sarif).")
    parser.add_argument("--file", "-f", default="titanshield-results.sarif", help="Output file name for SARIF format.")
    args = parser.parse_args()

    console = Console()

    if not os.path.exists(args.apk_path):
        console.print(f"[bold red]Error:[/bold red] File not found at {args.apk_path}")
        return

    with Progress(console=console) as progress:
        task1 = progress.add_task("[green]Decompiling APK...", total=1)
        with tempfile.TemporaryDirectory() as temp_dir:
            if not decompile_apk(args.apk_path, temp_dir, args.max_mem): # <-- L'argument est ici
                progress.update(task1, completed=1, description="[red]Decompilation Failed.")
                return
            progress.update(task1, completed=1, description="[green]Decompilation Complete.")

            task2 = progress.add_task("[cyan]Analyzing files...", total=None)
            rules_path = os.path.join(os.path.dirname(__file__), 'rules', 'android')
            rules = load_rules_from_dir(rules_path)
            progress.update(task2, description=f"[cyan]Analyzing with {len(rules)} rules...")

            all_findings = []
            source_files = [os.path.join(root, file) for root, _, files in os.walk(temp_dir) for file in files if file.endswith(('.java', '.kt', '.xml'))]
            
            progress.update(task2, total=len(source_files))
            for file_path in source_files:
                relative_path = os.path.relpath(file_path, temp_dir)
                findings_in_file = run_rules_on_file(file_path, rules)
                for finding in findings_in_file:
                    finding['file_path'] = relative_path
                all_findings.extend(findings_in_file)
                progress.update(task2, advance=1)
            progress.update(task2, description="[green]Analysis Complete.")

    if args.output == 'sarif':
        sarif_report = generate_sarif_report(all_findings, rules)
        with open(args.file, 'w') as f:
            json.dump(sarif_report, f, indent=2)
        console.print(f"\n[bold green]✅ SARIF report saved to {args.file}[/bold green]")
    else: # Console
        console.print("\n[bold]--- Analysis Complete ---[/bold]")
        if not all_findings:
            console.print("[bold green]✅ No issues found based on the current rule set.[/bold green]")
        else:
            console.print(f"[bold red]🔥 Found {len(all_findings)} potential issues:[/bold red]")
            table = Table(title="Vulnerability Summary")
            table.add_column("Severity", justify="center", style="bold")
            table.add_column("Rule Name", style="cyan")
            table.add_column("File", style="magenta")

            for finding in sorted(all_findings, key=lambda x: {"CRITICAL":0, "HIGH":1, "MEDIUM":2}.get(x['severity'], 3)):
                sev_style = {"CRITICAL": "red", "HIGH": "yellow", "MEDIUM": "blue"}.get(finding['severity'], "white")
                table.add_row(f"[{sev_style}]{finding['severity']}[/{sev_style}]", finding['name'], finding['file_path'])
            
            console.print(table)
    console.print("\n[bold yellow]✨ You caught the common vulnerabilities. Time to catch the legendaries.[/bold yellow]")
    console.print("The TitanShield Cloud Platform is waiting. Join the hunt at [link=https://titanshield.tech]titanshield.tech[/link] 🏹")