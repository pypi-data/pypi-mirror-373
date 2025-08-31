#!/usr/bin/env python3
"""
SubPlz Textual TUI Application
Modern terminal user interface for the SubPlz subtitle pipeline
"""

import asyncio
import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Header, Footer, Input, Button, Static, ProgressBar, 
    Log, Tabs, TabPane, DataTable, Label, Switch, Select, TextArea
)
from textual.reactive import reactive
from textual.screen import Screen
from textual import on
from textual.message import Message
from rich.text import Text
from rich.table import Table
from rich.console import Console

from .pipeline import SubtitlePipeline
from .config import (
    WHISPER_MODEL, OUTPUT_DIR, TEMP_DIR, 
    NETFLIX_SUBTITLE_STYLE, VIDEO_FORMAT, AUDIO_FORMAT
)


class JobStatus:
    """Represents the status of a subtitle generation job"""
    def __init__(self, source: str, job_id: str):
        self.source = source
        self.job_id = job_id
        self.status = "pending"  # pending, downloading, transcribing, burning, completed, failed
        self.progress = 0.0
        self.start_time = datetime.now()
        self.end_time = None
        self.output_file = None
        self.error_message = None
        self.current_step = ""


class JobRunner:
    """Handles running subtitle generation jobs"""
    def __init__(self, app: 'SubPlzApp'):
        self.app = app
        self.pipeline = SubtitlePipeline()
        self.current_job: Optional[JobStatus] = None
    
    async def run_job(self, source: str, job_id: str) -> JobStatus:
        """Run a subtitle generation job"""
        job = JobStatus(source, job_id)
        self.current_job = job
        
        try:
            # Check dependencies
            job.current_step = "Checking dependencies..."
            self.app.update_job_status(job)
            
            if not self.pipeline.check_dependencies():
                job.status = "failed"
                job.error_message = "Missing dependencies"
                return job
            
            # Process video
            job.status = "downloading"
            job.current_step = "Processing video..."
            job.progress = 0.1
            self.app.update_job_status(job)
            
            # Simulate progress updates during processing
            success = await self._process_with_progress(source, job)
            
            if success:
                job.status = "completed"
                job.progress = 1.0
                job.current_step = "Completed successfully!"
                job.end_time = datetime.now()
                # Find the output file
                video_id = self.pipeline.get_video_title(source) if source.startswith('http') else Path(source).stem
                job.output_file = str(self.pipeline.output_dir / f"{video_id}_with_subtitles.mp4")
            else:
                job.status = "failed"
                job.error_message = "Processing failed"
                
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
        
        job.end_time = datetime.now()
        self.app.update_job_status(job)
        return job
    
    async def _process_with_progress(self, source: str, job: JobStatus) -> bool:
        """Process video with progress updates"""
        try:
            if source.startswith(('http://', 'https://')):
                # Download phase
                job.current_step = "Downloading video..."
                job.progress = 0.2
                self.app.update_job_status(job)
                await asyncio.sleep(0.1)  # Allow UI update
                
                video_id = self.pipeline.get_video_title(source)
                video_path, audio_path = self.pipeline.download_video(source, video_id)
                
                if not video_path or not audio_path:
                    return False
            else:
                video_path = source
                video_id = Path(source).stem
                
                # Extract audio
                job.current_step = "Extracting audio..."
                job.progress = 0.3
                self.app.update_job_status(job)
                await asyncio.sleep(0.1)
                
                audio_path = str(self.pipeline.temp_dir / f"{video_id}.wav")
                # Audio extraction logic would go here
            
            # Transcription phase
            job.current_step = "Generating subtitles with Whisper..."
            job.progress = 0.5
            self.app.update_job_status(job)
            await asyncio.sleep(0.1)
            
            srt_path = self.pipeline.generate_subtitles(audio_path, video_id)
            
            # Burning phase
            job.current_step = "Burning subtitles into video..."
            job.progress = 0.8
            self.app.update_job_status(job)
            await asyncio.sleep(0.1)
            
            final_path = self.pipeline.burn_subtitles(video_path, srt_path, video_id)
            
            return final_path is not None
            
        except Exception:
            return False


class MainScreen(Screen):
    """Main screen with tabs for different functionality"""
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            with Tabs():
                with TabPane("Process", id="process"):
                    yield ProcessTab()
                with TabPane("Progress", id="progress"):
                    yield ProgressTab()
                with TabPane("Settings", id="settings"):
                    yield SettingsTab()
                with TabPane("Results", id="results"):
                    yield ResultsTab()
        yield Footer()


class ProcessTab(Static):
    """Tab for processing videos"""
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("SubPlz - Subtitle Generator", classes="title")
            yield Static("Enter a YouTube URL or select a local video file:", classes="subtitle")
            
            with Horizontal():
                yield Input(placeholder="https://youtube.com/watch?v=... or file path", id="source_input")
                yield Button("Browse", id="browse_btn")
                yield Button("Process", id="process_btn", variant="primary")
            
            yield Static("Recent Sources:", classes="section-title")
            yield DataTable(id="recent_table")
    
    def on_mount(self) -> None:
        """Set up the recent files table"""
        table = self.query_one("#recent_table", DataTable)
        table.add_columns("Source", "Type", "Status")
        # Add some sample data
        table.add_rows([
            ("https://youtube.com/watch?v=example", "YouTube", "Completed"),
            ("C:/Videos/myvideo.mp4", "Local File", "Failed"),
        ])
    
    @on(Button.Pressed, "#browse_btn")
    def browse_files(self) -> None:
        """Open file browser"""
        self.app.push_screen("file_browser")
    
    @on(Button.Pressed, "#process_btn")
    def start_processing(self) -> None:
        """Start processing the video"""
        source_input = self.query_one("#source_input", Input)
        source = source_input.value.strip()
        
        if not source:
            self.app.notify("Please enter a YouTube URL or select a file")
            return
        
        # Switch to progress tab and start job
        self.app.start_job(source)


class ProgressTab(Static):
    """Tab showing current processing progress"""
    
    current_job: reactive[Optional[JobStatus]] = reactive(None)
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Processing Progress", classes="title")
            
            with Container(id="progress_container"):
                yield Static("No active jobs", id="status_text")
                yield ProgressBar(id="main_progress")
                yield Log(id="progress_log")
    
    def watch_current_job(self, job: Optional[JobStatus]) -> None:
        """Update UI when job status changes"""
        if job is None:
            self.query_one("#status_text", Static).update("No active jobs")
            self.query_one("#main_progress", ProgressBar).progress = 0
            return
        
        # Update status text
        status_text = f"Processing: {Path(job.source).name if not job.source.startswith('http') else 'YouTube Video'}"
        status_text += f"\nStatus: {job.status.title()}"
        status_text += f"\nStep: {job.current_step}"
        
        if job.end_time:
            duration = job.end_time - job.start_time
            status_text += f"\nDuration: {duration.total_seconds():.1f}s"
        
        self.query_one("#status_text", Static).update(status_text)
        self.query_one("#main_progress", ProgressBar).progress = job.progress * 100
        
        # Add log entry
        log = self.query_one("#progress_log", Log)
        timestamp = datetime.now().strftime("%H:%M:%S")
        log.write_line(f"[{timestamp}] {job.current_step}")


class SettingsTab(Static):
    """Tab for configuring settings"""
    
    def compose(self) -> ComposeResult:
        with Container():
            yield Static("Settings", classes="title")
            
            # Whisper Model Selection
            yield Label("Whisper Model:")
            yield Select([
                ("tiny", "tiny"),
                ("base", "base"), 
                ("small", "small"),
                ("medium", "medium"),
                ("large", "large")
            ], value=WHISPER_MODEL, id="whisper_model")
            
            # Output Directory
            yield Label("Output Directory:")
            yield Input(value=OUTPUT_DIR, id="output_dir")
            
            # Subtitle Style Settings
            yield Static("Subtitle Style:", classes="section-title")
            yield Label("Font Size:")
            yield Input(value=str(NETFLIX_SUBTITLE_STYLE["fontsize"]), id="font_size")
            
            # Cleanup Settings
            yield Label("Cleanup temporary files:")
            yield Switch(value=True, id="cleanup_switch")
            
            # Action Buttons
            with Horizontal():
                yield Button("Save Settings", id="save_settings", variant="primary")
                yield Button("Reset to Defaults", id="reset_settings")


class ResultsTab(Static):
    """Tab showing completed jobs and results"""
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Results", classes="title")
            yield DataTable(id="results_table")
            
            with Horizontal():
                yield Button("Open Output Folder", id="open_folder")
                yield Button("Clear History", id="clear_history")
    
    def on_mount(self) -> None:
        """Set up the results table"""
        table = self.query_one("#results_table", DataTable)
        table.add_columns("Source", "Status", "Duration", "Output File", "Actions")


class FileBrowserScreen(Screen):
    """Screen for browsing and selecting files"""
    
    def compose(self) -> ComposeResult:
        with Container():
            yield Static("Select Video File", classes="title")
            yield Static("Use the file input in the main interface or enter path directly:", classes="subtitle")
            yield Input(placeholder="Enter full path to video file", id="file_path_input")
            
            with Horizontal():
                yield Button("Cancel", id="cancel_browse")
                yield Button("Select", id="select_file", variant="primary")
    
    @on(Button.Pressed, "#cancel_browse")
    def cancel_browse(self) -> None:
        self.app.pop_screen()
    
    @on(Button.Pressed, "#select_file")
    def select_file(self) -> None:
        path_input = self.query_one("#file_path_input", Input)
        selected_path = path_input.value.strip()
        if selected_path:
            # Pass selected file back to main screen
            self.app.set_source_input(selected_path)
        self.app.pop_screen()


class SubPlzApp(App):
    """Main Textual application"""
    
    CSS = """
    .title {
        text-align: center;
        color: $accent;
        text-style: bold;
        margin: 1;
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
        height: 10;
    }
    """
    
    TITLE = "SubPlz - Subtitle Pipeline TUI"
    SUB_TITLE = "Terminal User Interface for Video Subtitle Generation"
    
    SCREENS = {
        "file_browser": FileBrowserScreen(),
    }
    
    def __init__(self):
        super().__init__()
        self.job_runner = JobRunner(self)
        self.completed_jobs: List[JobStatus] = []
        self.current_job: Optional[JobStatus] = None
    
    def compose(self) -> ComposeResult:
        yield MainScreen()
    
    def set_source_input(self, path: str) -> None:
        """Set the source input field value"""
        try:
            input_field = self.query_one("#source_input", Input)
            input_field.value = path
        except:
            pass
    
    def start_job(self, source: str) -> None:
        """Start a new subtitle generation job"""
        job_id = f"job_{len(self.completed_jobs) + 1}"
        
        # Switch to progress tab
        tabs = self.query_one("Tabs")
        tabs.active = "progress"
        
        # Start the job asynchronously
        asyncio.create_task(self._run_job_async(source, job_id))
    
    async def _run_job_async(self, source: str, job_id: str) -> None:
        """Run job asynchronously"""
        job = await self.job_runner.run_job(source, job_id)
        self.completed_jobs.append(job)
        self.current_job = None
        
        # Update results table
        self._update_results_table()
        
        # Show notification
        if job.status == "completed":
            self.notify(f"✅ Completed: {Path(job.source).name}")
        else:
            self.notify(f"❌ Failed: {job.error_message}")
    
    def update_job_status(self, job: JobStatus) -> None:
        """Update job status in the UI"""
        self.current_job = job
        try:
            progress_tab = self.query_one("ProgressTab")
            progress_tab.current_job = job
        except:
            pass
    
    def _update_results_table(self) -> None:
        """Update the results table with completed jobs"""
        try:
            table = self.query_one("#results_table", DataTable)
            table.clear()
            
            for job in self.completed_jobs:
                duration = ""
                if job.end_time:
                    duration = f"{(job.end_time - job.start_time).total_seconds():.1f}s"
                
                source_display = Path(job.source).name if not job.source.startswith('http') else "YouTube Video"
                output_file = Path(job.output_file).name if job.output_file else "None"
                
                table.add_row(
                    source_display,
                    job.status.title(),
                    duration,
                    output_file,
                    "View"
                )
        except:
            pass


def run_tui():
    """Entry point for the TUI application"""
    app = SubPlzApp()
    app.run()


if __name__ == "__main__":
    run_tui()
