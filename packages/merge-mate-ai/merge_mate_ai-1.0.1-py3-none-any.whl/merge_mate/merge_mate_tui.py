import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict

# --- Third-party libraries ---
from dotenv import load_dotenv
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

# --- Textual TUI Framework ---
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, ListView, ListItem, Label, Static, Button
from textual.worker import Worker, WorkerState

# --- AI (Gemini) Configuration ---
import google.generativeai as genai

# --- Local Imports from your resolver logic ---
from .resolver import (
    parse_first_conflict,
    replace_first_conflict_with,
    get_file_language,
    async_call_gemini_for_resolution,
    get_resolve_prompt,
    async_call_gemini_for_explanation,
    get_explain_prompt
)

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def get_conflicted_files() -> List[Path]:
    """Get list of files with unresolved merge conflicts."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=U"],
            capture_output=True,
            text=True,
            check=True,
        )
        return [Path(line.strip()) for line in result.stdout.splitlines() if line.strip()]
    except subprocess.CalledProcessError:
        return []

# ==============================================================================
# THE MAIN TUI APPLICATION
# ==============================================================================
class MergeMateTUI(App):
    """An interactive TUI for resolving Git merge conflicts with AI."""

    CSS_PATH = "merge_mate.css"
    BINDINGS = [("q", "quit", "Quit"), ("ctrl+c", "quit", "Quit")]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conflicted_files: List[Path] = []
        self.selected_file: Path | None = None
        self.current_conflict: Tuple[str, str] | None = None

    def compose(self) -> ComposeResult:
        """Create the layout of the app."""
        yield Header(name="MergeMate TUI - AI Git Co-Pilot")
        with Horizontal():
            with Vertical(id="file-list-container"):
                yield Label("Conflicted Files")
                yield ListView(id="file-list")
            with Vertical(id="content-container"):
                yield Label("File Content / Diff View", id="content-title")
                yield Static(id="file-content", expand=True)
                with Horizontal(id="button-container"):
                    yield Button("Explain Conflict", id="btn-explain", variant="primary")
                    yield Button("Resolve with AI (auto-apply)", id="btn-resolve", variant="success")
            with Vertical(id="log-container"):
                yield Label("AI Explanation / Log")
                yield Static(id="log-view", expand=True)
        yield Footer()

    def on_mount(self) -> None:
        """Populate file list on startup."""
        try:
            self.conflicted_files = get_conflicted_files()
            file_list = self.query_one("#file-list", ListView)
            file_list.clear()
            if not self.conflicted_files:
                file_list.append(ListItem(Label("✅ No conflicts found!")))
                self.query_one("#btn-explain").disabled = True
                self.query_one("#btn-resolve").disabled = True
            else:
                for file_path in self.conflicted_files:
                    item = ListItem(Label(str(file_path)))
                    item.data = file_path
                    file_list.append(item)
        except Exception as e:
            self.query_one("#log-view", Static).update(Text(f"Error on startup:\n{e}", style="bold red"))

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle file selection from the list."""
        file_path = getattr(event.item, "data", None)
        if not isinstance(file_path, Path):
            return

        self.selected_file = file_path
        self.query_one("#content-title").update(f"Diff View: {self.selected_file.name}")
        self.query_one("#log-view").update("Select an action...")
        self.current_conflict = None

        try:
            content = self.selected_file.read_text(encoding="utf-8")
            conflict = parse_first_conflict(content)
            if conflict:
                self.current_conflict = (conflict[0], conflict[1])

                head_syntax = Syntax(conflict[0], get_file_language(str(self.selected_file)), theme="monokai")
                incoming_syntax = Syntax(conflict[1], get_file_language(str(self.selected_file)), theme="monokai")

                diff_table = Table.grid(expand=True)
                diff_table.add_column("head", style="red")
                diff_table.add_column("incoming", style="green")
                diff_table.add_row(
                    Panel(head_syntax, title="Current (HEAD)", border_style="red"),
                    Panel(incoming_syntax, title="Incoming", border_style="green"),
                )
                self.query_one("#file-content").update(diff_table)
            else:
                self.query_one("#file-content").update("[i]No conflict markers found.[/i]")
        except Exception as e:
            self.query_one("#file-content").update(Text(f"Error reading file:\n{e}", style="bold red"))

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if not self.selected_file or not self.current_conflict:
            self.query_one("#log-view").update("[bold red]Please select a conflicted file first.[/]")
            return

        if event.button.id == "btn-explain":
            self.spawn_ai_explanation()
        elif event.button.id == "btn-resolve":
            self.spawn_ai_resolution()

    # ========================
    # AI methods with Worker
    # ========================
    def spawn_ai_explanation(self) -> None:
        log_view = self.query_one("#log-view", Static)
        log_view.update("[yellow]🤖 Asking AI for an explanation...[/]")
        self.run_worker(self.get_ai_explanation, exclusive=True)

    def spawn_ai_resolution(self) -> None:
        log_view = self.query_one("#log-view", Static)
        log_view.update("[yellow]🤖 Asking AI for a resolution...[/]")
        self.run_worker(self.get_ai_resolution, exclusive=True)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker state changes."""
        log_view = self.query_one("#log-view")

        if event.state == WorkerState.SUCCESS:
            if isinstance(event.worker.result, str):  # AI explanation
                log_view.update(Text(event.worker.result))

            elif isinstance(event.worker.result, dict):  # AI resolution
                resolved_code = event.worker.result.get("resolved_code", "")
                confidence = event.worker.result.get("confidence_score", 0)

                # Show resolution preview
                resolution_syntax = Syntax(
                    resolved_code,
                    get_file_language(str(self.selected_file)),
                    theme="monokai",
                    line_numbers=True,
                )
                self.query_one("#file-content").update(
                    Panel(resolution_syntax, title="AI Applied Resolution", border_style="green")
                )

                # Auto-apply resolution
                try:
                    backup_dir = Path(".ai_backups")
                    backup_dir.mkdir(exist_ok=True)
                    shutil.copy2(self.selected_file, backup_dir / (self.selected_file.name + ".bak"))

                    original_text = self.selected_file.read_text(encoding="utf-8")
                    final_content = replace_first_conflict_with(original_text, resolved_code)
                    self.selected_file.write_text(final_content, encoding="utf-8")

                    log_view.update(
                        f"[bold green]✅ Resolution auto-applied to {self.selected_file.name}![/]\n"
                        f"Confidence: {confidence}% | Backup saved in .ai_backups/"
                    )
                    self.on_mount()
                except Exception as e:
                    log_view.update(Text(f"Error applying resolution:\n{e}", style="bold red"))

        elif event.state == WorkerState.ERROR:
            log_view.update(Text(f"AI Worker Error:\n{event.worker.error}", style="bold red"))

    # --- Worker Tasks ---
    async def get_ai_explanation(self) -> str:
        head, incoming = self.current_conflict
        prompt = get_explain_prompt(str(self.selected_file), head, incoming)
        return await async_call_gemini_for_explanation(prompt, "gemini-1.5-flash")

    async def get_ai_resolution(self) -> Dict:
        head, incoming = self.current_conflict
        prompt = get_resolve_prompt(str(self.selected_file), head, incoming, strategy="cautious")
        return await async_call_gemini_for_resolution(prompt, "gemini-1.5-flash")


def main():
    load_dotenv()
    if not os.getenv("GEMINI_API_KEY"):
        print("🔴 GEMINI_API_KEY not found in .env file. Please add it.")
        sys.exit(1)
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    app = MergeMateTUI()
    app.run()


if __name__ == "__main__":
    main()
