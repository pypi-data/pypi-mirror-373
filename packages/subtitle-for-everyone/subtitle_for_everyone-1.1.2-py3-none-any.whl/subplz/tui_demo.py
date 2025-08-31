#!/usr/bin/env python3
"""
SubPlz Textual TUI - Simplified Working Demo
This demonstrates the core concepts of how to implement a TUI with Textual
"""

import asyncio
import os
from pathlib import Path
from typing import Optional
from datetime import datetime

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Header, Footer, Input, Button, Static, ProgressBar, 
    Log, Tabs, TabPane, DataTable, Label, Select, Switch
)
from textual.reactive import reactive
from textual.screen import Screen
from textual import on
from rich.text import Text


class JobStatus:
    """Simple job status tracking"""
    def __init__(self, source: str):
        self.source = source
        self.status = "pending"
        self.progress = 0.0
        self.start_time = datetime.now()
        self.current_step = "Starting..."


class ProcessTab(Static):
    """Main processing tab"""
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("🎬 SubPlz - Subtitle Generator", classes="title")
            yield Static("Enter a YouTube URL or local video path:", classes="subtitle")
            
            with Horizontal():
                yield Input(placeholder="https://youtube.com/watch?v=... or C:/path/to/video.mp4", id="source_input")
                yield Button("Process", id="process_btn", variant="primary")
            
            yield Static("📋 Processing Queue:", classes="section-title")
            yield DataTable(id="queue_table")
    
    def on_mount(self) -> None:
        """Initialize the queue table"""
        table = self.query_one("#queue_table", DataTable)
        table.add_columns("Source", "Status", "Progress")
        # Add sample data
        table.add_rows([
            ("example_video.mp4", "Completed", "100%"),
            ("https://youtube.com/watch?v=demo", "Processing", "45%"),
        ])
    
    @on(Button.Pressed, "#process_btn")
    def start_processing(self) -> None:
        """Start processing button handler"""
        source_input = self.query_one("#source_input", Input)
        source = source_input.value.strip()
        
        if not source:
            self.app.notify("⚠️ Please enter a video source")
            return
        
        # Validate input
        if not (source.startswith(('http://', 'https://')) or Path(source).suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv']):
            self.app.notify("⚠️ Please enter a valid YouTube URL or video file path")
            return
        
        self.app.notify(f"🚀 Starting processing: {Path(source).name if not source.startswith('http') else 'YouTube Video'}")
        self.app.start_job(source)
        source_input.value = ""  # Clear input


class ProgressTab(Static):
    """Progress monitoring tab"""
    
    current_job: reactive[Optional[JobStatus]] = reactive(None)
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("📈 Processing Progress", classes="title")
            
            with Container(id="progress_container"):
                yield Static("No active jobs", id="status_text", classes="status")
                yield ProgressBar(id="main_progress", show_percentage=True)
                yield Log(id="progress_log", auto_scroll=True)
    
    def watch_current_job(self, job: Optional[JobStatus]) -> None:
        """React to job status changes"""
        if job is None:
            self.query_one("#status_text", Static).update("No active jobs")
            self.query_one("#main_progress", ProgressBar).progress = 0
            return
        
        # Create rich status text
        status_text = Text()
        status_text.append("Processing: ", style="bold")
        source_name = Path(job.source).name if not job.source.startswith('http') else 'YouTube Video'
        status_text.append(f"{source_name}\n", style="cyan")
        status_text.append("Status: ", style="bold")
        status_text.append(f"{job.status.title()}\n", style="green" if job.status == "completed" else "yellow")
        status_text.append("Step: ", style="bold")
        status_text.append(job.current_step, style="blue")
        
        self.query_one("#status_text", Static).update(status_text)
        self.query_one("#main_progress", ProgressBar).progress = job.progress * 100
        
        # Add to log
        log = self.query_one("#progress_log", Log)
        timestamp = datetime.now().strftime("%H:%M:%S")
        log.write_line(f"[{timestamp}] {job.current_step}")


class SettingsTab(Static):
    """Settings configuration tab"""
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("⚙️ Configuration", classes="title")
            
            # Whisper Model Selection
            yield Label("Whisper AI Model:")
            yield Select([
                ("tiny", "Tiny (fastest, least accurate)"),
                ("base", "Base (good balance)"), 
                ("small", "Small (better accuracy)"),
                ("medium", "Medium (high accuracy)"),
                ("large", "Large (best accuracy, slowest)")
            ], value="base", id="whisper_model")
            
            # Output Settings
            yield Label("Output Directory:")
            yield Input(value="processed_videos", id="output_dir", placeholder="Directory for output files")
            
            # Quality Settings  
            yield Label("Video Quality:")
            yield Select([
                ("high", "High Quality (slower)"),
                ("medium", "Medium Quality (balanced)"),
                ("low", "Low Quality (faster)")
            ], value="medium", id="quality_setting")
            
            # Cleanup option
            yield Label("Cleanup temporary files:")
            yield Switch(value=True, id="cleanup_switch")
            
            # Action buttons
            with Horizontal():
                yield Button("💾 Save Settings", id="save_settings", variant="primary")
                yield Button("🔄 Reset Defaults", id="reset_settings")
    
    @on(Button.Pressed, "#save_settings")
    def save_settings(self) -> None:
        self.app.notify("✅ Settings saved successfully!")
    
    @on(Button.Pressed, "#reset_settings")  
    def reset_settings(self) -> None:
        self.query_one("#whisper_model", Select).value = "base"
        self.query_one("#output_dir", Input).value = "processed_videos"
        self.query_one("#quality_setting", Select).value = "medium"
        self.query_one("#cleanup_switch", Switch).value = True
        self.app.notify("🔄 Settings reset to defaults")


class ResultsTab(Static):
    """Results and history tab"""
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("📁 Processing Results", classes="title")
            
            yield DataTable(id="results_table")
            
            with Horizontal():
                yield Button("📂 Open Output Folder", id="open_folder")
                yield Button("🗑️ Clear History", id="clear_history")
    
    def on_mount(self) -> None:
        """Initialize results table"""
        table = self.query_one("#results_table", DataTable)
        table.add_columns("Source", "Status", "Duration", "Output File", "Size")
        
        # Sample completed jobs
        table.add_rows([
            ("my_video.mp4", "✅ Completed", "2m 34s", "my_video_with_subtitles.mp4", "156 MB"),
            ("https://youtube.com/watch?v=abc", "❌ Failed", "45s", "None", "0 MB"),
            ("lecture.avi", "✅ Completed", "5m 12s", "lecture_with_subtitles.mp4", "892 MB"),
        ])
    
    @on(Button.Pressed, "#open_folder")
    def open_output_folder(self) -> None:
        self.app.notify("📂 Opening output folder...")
        # In real implementation: os.startfile() on Windows, open on macOS, etc.
    
    @on(Button.Pressed, "#clear_history")
    def clear_history(self) -> None:
        table = self.query_one("#results_table", DataTable)
        table.clear()
        table.add_rows([])  # Empty table
        self.app.notify("🗑️ History cleared")


class SubPlzTUIDemo(App):
    """Main Textual Application"""
    
    # CSS Styling for the app
    CSS = """
    .title {
        text-align: center;
        color: $accent;
        text-style: bold;
        margin: 1;
        background: $surface;
    }
    
    .subtitle {
        text-align: center;
        margin: 1;
        color: $text-muted;
    }
    
    .section-title {
        text-style: bold;
        margin: 1 0;
        color: $warning;
    }
    
    .status {
        padding: 1;
        background: $panel;
        border: thick $primary;
        margin: 1 0;
    }
    
    #progress_container {
        border: thick $primary;
        margin: 1;
        padding: 1;
    }
    
    #source_input {
        width: 80%;
    }
    
    Button {
        margin: 0 1;
    }
    
    DataTable {
        height: 8;
        margin: 1 0;
    }
    
    Select, Input {
        margin: 0 0 1 0;
    }
    
    Label {
        margin: 1 0 0 0;
    }
    """
    
    TITLE = "SubPlz TUI Demo"
    SUB_TITLE = "Terminal User Interface for Video Subtitle Generation"
    
    def __init__(self):
        super().__init__()
        self.current_job: Optional[JobStatus] = None
        self.completed_jobs = []
    
    def compose(self) -> ComposeResult:
        """Create the app layout"""
        yield Header()
        with Container():
            with Tabs():
                with TabPane("🎬 Process", id="process"):
                    yield ProcessTab()
                with TabPane("📈 Progress", id="progress"):
                    yield ProgressTab()
                with TabPane("⚙️ Settings", id="settings"):
                    yield SettingsTab()
                with TabPane("📁 Results", id="results"):
                    yield ResultsTab()
        yield Footer()
    
    def start_job(self, source: str) -> None:
        """Start a new processing job"""
        # Switch to progress tab to show the work
        tabs = self.query_one("Tabs")
        tabs.active = "progress"
        
        # Create and start job
        job = JobStatus(source)
        self.current_job = job
        
        # Update the progress tab
        progress_tab = self.query_one("ProgressTab")
        progress_tab.current_job = job
        
        # Start async processing simulation
        asyncio.create_task(self._simulate_processing(job))
    
    async def _simulate_processing(self, job: JobStatus) -> None:
        """Simulate the processing steps with realistic timing"""
        steps = [
            ("Validating input...", 0.1, 1),
            ("Checking dependencies...", 0.2, 0.5),
            ("Downloading video...", 0.4, 3),
            ("Extracting audio...", 0.6, 2),
            ("Generating subtitles with Whisper AI...", 0.8, 4),
            ("Burning subtitles into video...", 0.95, 2),
            ("Finalizing output...", 1.0, 0.5)
        ]
        
        for step_text, progress, duration in steps:
            job.current_step = step_text
            job.progress = progress
            job.status = "processing"
            
            # Update UI
            if hasattr(self, 'query_one'):
                try:
                    progress_tab = self.query_one("ProgressTab")
                    progress_tab.current_job = job
                except:
                    pass
            
            # Simulate work time
            await asyncio.sleep(duration)
        
        # Complete the job
        job.status = "completed"
        job.current_step = "✅ Processing completed successfully!"
        self.completed_jobs.append(job)
        self.current_job = None
        
        # Final UI update
        try:
            progress_tab = self.query_one("ProgressTab")
            progress_tab.current_job = job
        except:
            pass
        
        self.notify("✅ Video processing completed! Check the Results tab.")


def run_demo():
    """Run the demo application"""
    app = SubPlzTUIDemo()
    app.run()


if __name__ == "__main__":
    print("🎬 SubPlz TUI Demo")
    print("==================")
    print("This demonstrates a modern Terminal User Interface (TUI)")
    print("for the SubPlz subtitle generation pipeline using Textual.")
    print()
    print("Features demonstrated:")
    print("• Tabbed interface with different functions")
    print("• Real-time progress monitoring") 
    print("• Interactive form controls")
    print("• Data tables for job management")
    print("• Async job processing simulation")
    print()
    print("Press Ctrl+C to exit at any time.")
    print("Use Tab/Shift+Tab to navigate between widgets.")
    print()
    
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n👋 Demo completed! Thanks for exploring SubPlz TUI!")
    except Exception as e:
        print(f"Demo error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you have the latest textual: pip install textual>=0.41.0")
        print("2. Check your terminal supports rich text (most modern terminals do)")
        print("3. Try running in a different terminal if you see display issues")
