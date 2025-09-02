#!/usr/bin/env python
import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path
from typing import List

# --- Third-party libraries ---
from dotenv import load_dotenv
from rich import print as rprint
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Confirm
from rich.console import Console

# --- AI (Gemini) Configuration ---
import google.generativeai as genai

# --- Local Imports ---
from resolver import (
    parse_first_conflict,
    replace_first_conflict_with,
    get_file_language,
    call_gemini_for_resolution,
    get_resolve_prompt,
    get_explain_prompt,
    call_gemini_for_explanation
)

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
console = Console()

def get_conflicted_files() -> List[Path]:
    try:
        result = subprocess.run(['git', 'diff', '--name-only', '--diff-filter=U'], capture_output=True, text=True, check=True)
        return [Path(line.strip()) for line in result.stdout.splitlines() if line.strip()]
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Git error: {e.stderr.strip()}")

def create_backup(src: Path, backup_dir: Path) -> Path:
    backup_dir.mkdir(parents=True, exist_ok=True)
    dest = backup_dir / (src.name + ".bak")
    shutil.copy2(src, dest)
    return dest

# ==============================================================================
# CORE COMMANDS
# ==============================================================================

def handle_resolve_command(args: argparse.Namespace):
    """Handles the 'resolve' command with confidence-based batching."""
    conflicted_files = get_conflicted_files()
    if not conflicted_files:
        rprint("[bold green]✅ No merge conflicts found. You're all clear![/]")
        return

    rprint(Panel(f"Found [bold]{len(conflicted_files)}[/] conflicted file(s). Using [bold]{args.strategy}[/] strategy.", title="Merge Mate", border_style="yellow"))

    for file_path in conflicted_files:
        console.rule(f"[bold cyan]{file_path}[/]", style="cyan")
        try:
            original_text = file_path.read_text(encoding="utf-8")
            conflict_data = parse_first_conflict(original_text)
            
            if not conflict_data:
                rprint(f"[yellow] No standard conflict markers found. Skipping.[/]")
                continue

            head, incoming, _, _ = conflict_data
            prompt = get_resolve_prompt(str(file_path), head, incoming, args.strategy)
            
            with console.status("[bold yellow]🤖 Asking AI for a resolution...", spinner="dots"):
                ai_response = call_gemini_for_resolution(prompt, args.model)
            
            merged_code = ai_response.get("resolved_code", "")
            confidence = ai_response.get("confidence_score", 0)
            
            if not merged_code:
                raise RuntimeError("AI returned empty resolved code.")

            confidence_color = "green" if confidence >= 90 else "yellow" if confidence >= 70 else "red"
            rprint(Panel(Syntax(merged_code, get_file_language(str(file_path)), theme="monokai", line_numbers=True), 
                         title=f"🤖 AI Suggested Resolution ([{confidence_color}]Confidence: {confidence}%[/])", 
                         border_style=confidence_color))

            apply_change = False
            if confidence >= args.threshold:
                rprint(f"[bold green]Confidence ({confidence}%) is above threshold ({args.threshold}%). Applying automatically.[/]")
                apply_change = True
            else:
                apply_change = Confirm.ask(f"Confidence is below threshold. Apply this suggestion to [bold]{file_path}[/]?", default=True)

            if apply_change:
                create_backup(file_path, Path(args.backup_dir))
                final_content = replace_first_conflict_with(original_text, merged_code)
                file_path.write_text(final_content, encoding="utf-8")
                rprint(f"[bold green]✅ Conflict resolved in {file_path}[/]")
            else:
                rprint(f"[yellow]Skipped applying changes to {file_path}.[/]")

        except Exception as e:
            rprint(Panel(f"[bold red]Error processing {file_path}:[/]\n{e}", border_style="red"))


def handle_explain_command(args: argparse.Namespace):
    conflicted_files = get_conflicted_files()
    if not conflicted_files:
        rprint("[bold green]✅ No merge conflicts to explain.[/]")
        return
    
    rprint(Panel(f"Found [bold]{len(conflicted_files)}[/] conflicted file(s) to explain.", title="Merge Mate", border_style="yellow"))

    for file_path in conflicted_files:
        console.rule(f"[bold cyan]{file_path}[/]", style="cyan")
        try:
            text = file_path.read_text(encoding="utf-8")
            conflict_data = parse_first_conflict(text)
            if not conflict_data:
                rprint(f"[yellow] No standard conflict markers found. Skipping.[/]")
                continue
            head, incoming, _, _ = conflict_data
            prompt = get_explain_prompt(str(file_path), head, incoming)
            
            with console.status("[bold yellow]🤖 Asking AI for an explanation...", spinner="dots"):
                explanation = call_gemini_for_explanation(prompt, args.model)
            
            rprint(Panel(explanation, title=f"🤖 AI Explanation for {file_path}", border_style="blue"))
        except Exception as e:
            rprint(Panel(f"[bold red]Error explaining {file_path}:[/]\n{e}", border_style="red"))

# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(prog="merge-mate", description="Your AI co-pilot for Git merge conflicts.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Resolve Command ---
    resolve_parser = subparsers.add_parser("resolve", help="Intelligently resolve merge conflicts.")
    resolve_parser.add_argument("--strategy", choices=["cautious", "aggressive"], default="cautious", help="The AI's resolution strategy.")
    resolve_parser.add_argument("--backup-dir", default=".ai_backups", help="Directory for file backups.")
    resolve_parser.add_argument("--threshold", type=int, default=95, help="Confidence score (0-100) above which changes are applied automatically.")
    resolve_parser.set_defaults(func=handle_resolve_command)
    
    # --- Explain Command ---
    explain_parser = subparsers.add_parser("explain", help="Explain the cause of conflicts.")
    explain_parser.set_defaults(func=handle_explain_command)

    for p in [resolve_parser, explain_parser]:
        p.add_argument("--model", default="gemini-1.5-flash", help="The Google Gemini model.")

    args = parser.parse_args()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        rprint("[bold red]❌ GEMINI_API_KEY not found.[/]")
        sys.exit(1)
    genai.configure(api_key=api_key)

    try:
        subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], capture_output=True, text=True, check=True)
        args.func(args)
    except subprocess.CalledProcessError:
        rprint("[bold red]❌ Not a Git repository.[/]")
        sys.exit(1)
    except Exception as e:
        rprint(f"[bold red]An unexpected error occurred: {e}[/]")
        sys.exit(1)

if __name__ == "__main__":
    main()