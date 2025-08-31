"""
HALO Interactive CLI for Gemini batch prediction with YouTube video, chunking, and caching.
Beautiful, conversational, and cost-efficient.
"""
import asyncio
import json
import tempfile
import base64
import os
import re
import sys
import shutil
import subprocess
import platform
from typing import List, Dict, Any, Optional
import yt_dlp
import ffmpeg
import whisper
import google.generativeai as genai
from PIL import Image
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.align import Align
from rich import box
import click

from .config_manager import ConfigManager
from .gemini_batch_predictor import GeminiBatchPredictor
from .transcript_utils import chunk_transcript, find_relevant_chunk

console = Console()

# Package version
__version__ = "1.0.2"

HALO_BANNER = r'''
[bold cyan]
........................................................................
.  _   _    _    _     ___   
. | | | |  / \  | |   / _ \  
. | |_| | / _ \ | |  | | | | 
. |  _  |/ ___ \| |__| |_| | 
. |_| |_/_/   \_\____|\___/  
........................................................................
[/bold cyan]
'''

WELCOME_MESSAGE = """
[bold magenta]🎥 Welcome to HALO Video![/bold magenta]

[green]HALO combines AI-powered audio transcription with visual frame analysis 
to let you ask intelligent questions about any YouTube video.[/green]

[yellow]✨ What can HALO do?[/yellow]
• 🎵 [cyan]Audio Analysis[/cyan]: Transcribe speech and dialogue using OpenAI Whisper
• 👁️  [cyan]Visual Analysis[/cyan]: Analyze video frames using Google Gemini Vision
• 🤖 [cyan]Smart Q&A[/cyan]: Ask questions about content, visuals, or both
• 💾 [cyan]Cost Efficient[/cyan]: Smart caching minimizes API usage

[blue]📋 Prerequisites:[/blue]
• Google Gemini API key (free at https://makersuite.google.com/app/apikey)
• FFmpeg (will be auto-installed if missing)
"""

# Helper: Estimate tokens (roughly 1 token ≈ 4 chars)
def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)

# Helper: Check if FFmpeg is available
def check_ffmpeg() -> bool:
    """Check if FFmpeg is available in the system"""
    return shutil.which('ffmpeg') is not None

# Helper: Install FFmpeg using imageio-ffmpeg as fallback
def install_ffmpeg_fallback():
    """Install FFmpeg using imageio-ffmpeg as a fallback"""
    try:
        import imageio_ffmpeg as ffmpeg_download
        ffmpeg_download.get_ffmpeg_exe()
        console.print("[green]✅ FFmpeg installed successfully via imageio-ffmpeg![/green]")
        return True
    except Exception as e:
        console.print(f"[red]❌ Failed to install FFmpeg: {e}[/red]")
        return False

# Helper: Guide user to install FFmpeg manually
def guide_ffmpeg_installation():
    """Provide platform-specific FFmpeg installation instructions"""
    system = platform.system().lower()
    
    console.print(Panel(
        f"""[bold red]FFmpeg is required but not found![/bold red]

[yellow]Please install FFmpeg for your system:[/yellow]

[bold cyan]macOS (using Homebrew):[/bold cyan]
  brew install ffmpeg

[bold cyan]Ubuntu/Debian:[/bold cyan]
  sudo apt update && sudo apt install ffmpeg

[bold cyan]Windows (using Chocolatey):[/bold cyan]
  choco install ffmpeg

[bold cyan]Or download directly:[/bold cyan]
  https://ffmpeg.org/download.html

[dim]After installation, restart your terminal and run 'halo-video' again.[/dim]
""", 
        title="[red]FFmpeg Installation Required[/red]",
        box=box.DOUBLE
    ))

# Helper: Ensure FFmpeg is available
def ensure_ffmpeg() -> bool:
    """Ensure FFmpeg is available, try to install if missing"""
    if check_ffmpeg():
        return True
    
    console.print("[yellow]⚠️  FFmpeg not found. Attempting automatic installation...[/yellow]")
    
    # Try imageio-ffmpeg fallback
    if install_ffmpeg_fallback():
        return True
    
    # Show manual installation guide
    guide_ffmpeg_installation()
    return False

# Helper: Download YouTube video and extract audio
def extract_video_id(youtube_url: str) -> str:
    """Extracts the video ID from a YouTube URL."""
    match = re.search(r"(?:v=|youtu.be/)([\w-]+)", youtube_url)
    return match.group(1) if match else "unknown"

async def download_youtube_audio(youtube_url: str, output_dir: str) -> str:
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=True)
        audio_path = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.wav'
    return audio_path

# Helper: Extract frames every 15 seconds directly from stream (no video file saved)
def extract_frames_from_url(youtube_url: str, output_dir: str) -> List[str]:
    frame_pattern = os.path.join(output_dir, "frame_%04d.jpg")
    try:
        # Extract frames directly from YouTube stream without saving video
        (
            ffmpeg
            .input(youtube_url)
            .output(frame_pattern, vf='fps=1/15', format='image2', vcodec='mjpeg')
            .run(quiet=True, overwrite_output=True)
        )
        # Collect all frame file paths
        frames = sorted([
            os.path.join(output_dir, fname)
            for fname in os.listdir(output_dir)
            if fname.startswith("frame_") and fname.endswith(".jpg")
        ])
        return frames
    except Exception as e:
        console.print(f"[yellow][WARNING] Frame extraction failed: {e}[/yellow]")
        return []

# Helper: Describe an image frame using Gemini Vision API
async def describe_image(image_path: str, frame_number: int, timestamp: float, model=None) -> str:
    try:
        # Use provided model or create new one
        if model is None:
            config_manager = ConfigManager()
            api_key = config_manager.get_api_key()
            if not api_key:
                raise ValueError("No API key configured")
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Load and prepare the image
        img = Image.open(image_path)
        
        # Create a detailed prompt for image description
        minutes = int(timestamp // 60)
        seconds = int(timestamp % 60)
        
        prompt = f"""Describe this video frame in ONE concise sentence. Focus only on key visual elements:
        - What people are wearing (colors, clothing types)
        - Main objects and their colors
        - Setting/location if obvious
        - Any text visible on screen
        
        Keep it brief and factual - this supplements audio transcript for visual questions only."""
        
        # Generate description using Gemini Vision
        response = model.generate_content([prompt, img])
        
        # Check if response is valid
        if not response or not hasattr(response, 'text') or not response.text:
            raise Exception("Empty response from Gemini API")
            
        description = response.text.strip()
        
        # Ensure we got a meaningful response
        if not description or description.lower() in ['', 'none', 'n/a']:
            raise Exception("Invalid description received")
        
        return f"[Frame at {minutes:02d}:{seconds:02d}] {description}"
        
    except Exception as e:
        # Fallback description if API fails
        minutes = int(timestamp // 60)
        seconds = int(timestamp % 60)
        console.print(f"[yellow][WARNING] Image description failed for frame {frame_number}: {e}[/yellow]")
        return f"[Frame at {minutes:02d}:{seconds:02d}] Video frame captured at this timestamp (description unavailable)."

# Helper: Transcribe audio using Whisper
async def transcribe_audio(audio_path: str) -> str:
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]

# Command functions
def show_version():
    """Show version information"""
    console.print(f"[bold cyan]HALO Video v{__version__}[/bold cyan]")
    console.print("[dim]AI-powered YouTube video analysis[/dim]")

def show_help():
    """Show comprehensive help"""
    help_table = Table(title="🎯 HALO Video Commands", box=box.ROUNDED)
    help_table.add_column("Command", style="bold cyan", no_wrap=True)
    help_table.add_column("Description", style="white")
    
    help_table.add_row("analyze", "🎥 Analyze a YouTube video (main function)")
    help_table.add_row("config", "🔧 Manage API key configuration")
    help_table.add_row("reset", "🔄 Reset/re-enter API key")
    help_table.add_row("version", "📋 Show version information")
    help_table.add_row("upgrade", "⬆️  Check for package updates")
    help_table.add_row("help", "❓ Show this help message")
    help_table.add_row("exit", "👋 Exit HALO Video")
    
    console.print(help_table)
    
    console.print(Panel(
        """[yellow]💡 Quick Start:[/yellow]
1. Run [cyan]'analyze'[/cyan] to start video analysis
2. Paste any YouTube URL when prompted
3. Ask questions about the video content
4. Type [cyan]'exit'[/cyan] to quit at any time

[yellow]🔑 First time?[/yellow]
You'll be asked for your Google Gemini API key.
Get it free at: [blue]https://makersuite.google.com/app/apikey[/blue]""",
        title="[bold green]Getting Started[/bold green]",
        box=box.DOUBLE
    ))

def check_for_updates():
    """Check for package updates"""
    try:
        import subprocess
        import json
        
        console.print("[dim]Checking for updates...[/dim]")
        result = subprocess.run([
            sys.executable, "-m", "pip", "index", "versions", "halo-video"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if lines:
                latest_line = lines[-1]
                if 'Available versions:' in latest_line:
                    versions = latest_line.split('Available versions:')[1].strip().split(',')
                    latest_version = versions[0].strip() if versions else __version__
                    
                    if latest_version != __version__:
                        console.print(f"[yellow]📦 Update available: v{latest_version} (current: v{__version__})[/yellow]")
                        console.print("[cyan]Run: pip install --upgrade halo-video[/cyan]")
                    else:
                        console.print("[green]✅ You're running the latest version![/green]")
                else:
                    console.print("[green]✅ You're running the latest version![/green]")
        else:
            console.print("[yellow]⚠️  Could not check for updates[/yellow]")
            
    except Exception as e:
        console.print(f"[yellow]⚠️  Update check failed: {e}[/yellow]")

def manage_config():
    """Manage configuration"""
    config_manager = ConfigManager()
    
    if config_manager.has_api_key():
        console.print("[green]✅ API key is configured[/green]")
        if Confirm.ask("[yellow]Would you like to view/change your API key?[/yellow]"):
            current_key = config_manager.get_api_key()
            masked_key = current_key[:8] + "..." + current_key[-8:] if len(current_key) > 16 else "***"
            console.print(f"[dim]Current API key: {masked_key}[/dim]")
            
            if Confirm.ask("[yellow]Enter a new API key?[/yellow]"):
                setup_api_key(config_manager, force_reset=True)
    else:
        console.print("[red]❌ No API key configured[/red]")
        setup_api_key(config_manager)

def setup_api_key(config_manager: ConfigManager, force_reset: bool = False):
    """Setup or reset API key with comprehensive handling"""
    if force_reset or not config_manager.has_api_key():
        console.print("\n[bold red]🔑 Gemini API Key Required[/bold red]")
        console.print("[yellow]To use HALO, you need a Google Gemini API key.[/yellow]")
        console.print("[blue]Get your free API key at: https://makersuite.google.com/app/apikey[/blue]")
        console.print("[dim]Note: Your input will be hidden for security[/dim]")
        
        # Try multiple input methods for better compatibility
        api_key = None
        try:
            # First try with password=True (hidden input)
            api_key = Prompt.ask("[bold yellow]Enter your Gemini API key[/bold yellow]", password=True)
        except:
            try:
                # Fallback to regular input if password input fails
                console.print("[yellow]Note: API key input will be visible[/yellow]")
                api_key = Prompt.ask("[bold yellow]Enter your Gemini API key[/bold yellow]")
            except:
                # Final fallback to built-in input
                console.print("[yellow]Using basic input mode[/yellow]")
                api_key = input("Enter your Gemini API key: ")
        
        if not api_key or not api_key.strip():
            console.print("[bold red]❌ No API key provided.[/bold red]")
            return False
        
        api_key = api_key.strip()
        
        # Validate API key format (basic check)
        if not api_key.startswith('AI') or len(api_key) < 20:
            console.print("[bold yellow]⚠️  Warning: API key format may be invalid[/bold yellow]")
            if not Confirm.ask("[yellow]Continue anyway?[/yellow]", default=False):
                return False
        
        config_manager.save_api_key(api_key)
        console.print("[bold green]✅ API key saved successfully![/bold green]")
        
        # Test API key immediately
        console.print("[dim]Testing API key...[/dim]")
        try:
            genai.configure(api_key=api_key)
            test_model = genai.GenerativeModel('gemini-1.5-flash')
            test_response = test_model.generate_content("Hello")
            if test_response and test_response.text:
                console.print("[bold green]✅ API key is working![/bold green]")
                return True
            else:
                console.print("[bold yellow]⚠️  API key test returned empty response[/bold yellow]")
        except Exception as e:
            console.print(f"[bold red]❌ API key test failed: {str(e)}[/bold red]")
            console.print("[yellow]The API key was saved but may not be working properly.[/yellow]")
            return Confirm.ask("[yellow]Continue anyway?[/yellow]", default=False)
    
    return True

def show_main_menu():
    """Show the main interactive menu"""
    console.clear()
    console.print(HALO_BANNER)
    console.print(WELCOME_MESSAGE)
    
    menu_table = Table(title="🎯 Choose an Action", box=box.ROUNDED, show_header=False)
    menu_table.add_column("Option", style="bold cyan", no_wrap=True)
    menu_table.add_column("Description", style="white")
    
    menu_table.add_row("1", "🎥 Analyze YouTube Video")
    menu_table.add_row("2", "🔧 Manage API Key")
    menu_table.add_row("3", "📋 Show Version")
    menu_table.add_row("4", "⬆️  Check for Updates")
    menu_table.add_row("5", "❓ Show Help")
    menu_table.add_row("6", "👋 Exit")
    
    console.print(menu_table)
    
    while True:
        choice = Prompt.ask(
            "\n[bold yellow]Enter your choice (1-6) or command name[/bold yellow]",
            choices=["1", "2", "3", "4", "5", "6", "analyze", "config", "version", "upgrade", "help", "exit"],
            show_choices=False
        )
        
        if choice in ["1", "analyze"]:
            return "analyze"
        elif choice in ["2", "config"]:
            return "config"
        elif choice in ["3", "version"]:
            return "version"
        elif choice in ["4", "upgrade"]:
            return "upgrade"
        elif choice in ["5", "help"]:
            return "help"
        elif choice in ["6", "exit"]:
            return "exit"
# Interactive CLI for video analysis
async def analyze_video():
    """Main video analysis function"""
    config_manager = ConfigManager()
    
    # Ensure FFmpeg is available
    if not ensure_ffmpeg():
        console.print("[bold red]❌ Cannot proceed without FFmpeg. Please install it and try again.[/bold red]")
        return
    
    # Check for API key
    if not setup_api_key(config_manager):
        return
    
    console.print("\n[bold blue]Tip:[/bold blue] Paste a YouTube link and press Enter. Type 'exit' anytime to quit.")
    console.rule("[bold cyan]VIDEO ANALYSIS[/bold cyan]")
    
    youtube_url = Prompt.ask("[bold yellow]Enter YouTube video link[/bold yellow]").strip()
    if not youtube_url or youtube_url.lower() == 'exit':
        console.print("[bold yellow]👋 Analysis cancelled.[/bold yellow]")
        return
        
    video_id = extract_video_id(youtube_url)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
            progress.add_task(description=f"Downloading audio for video ID: {video_id}...", total=None)
            audio_path = await download_youtube_audio(youtube_url, tmpdir)
        console.print(f"[green][INFO] Audio saved to {audio_path}[/green]")
        
        # NEW: Extract frames directly from YouTube stream (no video file saved)
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
            progress.add_task(description="Extracting frames every 15 seconds...", total=None)
            frames = extract_frames_from_url(youtube_url, tmpdir)
        console.print(f"[green][INFO] Extracted {len(frames)} frames.[/green]")

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
            progress.add_task(description="Transcribing audio (this may take a while)...", total=None)
            transcript = await transcribe_audio(audio_path)
        
        # NEW: Describe each frame and append to transcript
        frame_descriptions = []
        if frames:
            # Initialize Gemini model once for all frames
            try:
                api_key = config_manager.get_api_key()
                if not api_key:
                    raise ValueError("No API key configured")
                genai.configure(api_key=api_key)
                vision_model = genai.GenerativeModel('gemini-1.5-flash')
                
                with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
                    task = progress.add_task(description="Generating detailed frame descriptions...", total=len(frames))
                    for i, frame_path in enumerate(frames):
                        timestamp = i * 15  # 15 seconds per frame
                        desc = await describe_image(frame_path, i, timestamp, vision_model)
                        frame_descriptions.append(desc)
                        progress.update(task, advance=1)
                        
            except Exception as e:
                console.print(f"[bold red]❌ Error initializing vision model: {e}[/bold red]")
                console.print("[yellow]Continuing without frame descriptions...[/yellow]")
                
            frames_text = "\n".join(frame_descriptions)
            # Append frame descriptions to transcript
            transcript_with_images = transcript + "\n\n[Visual Context - Key frames every 15 seconds]\n" + frames_text
            console.print(f"[bold green][INFO] Audio transcript ready with {len(frame_descriptions)} visual context frames. You can now ask questions![/bold green]")
        else:
            transcript_with_images = transcript
            console.print("[bold green][INFO] Transcript ready (no frames extracted). You can now ask questions![/bold green]")
        
        chunks = chunk_transcript(transcript_with_images, max_tokens=4000, overlap=500)
        total_tokens_full = estimate_tokens(transcript_with_images)
        total_tokens_sent = 0
        total_tokens_saved = 0
        cache_hits = 0
        cache_lookups = 0
        question_history = []
        console.print(Panel(f"[b]Video ID:[/b] {video_id}\n[b]Transcript length:[/b] {len(transcript_with_images)} chars, ~{total_tokens_full} tokens\n[b]Chunks created:[/b] {len(chunks)} (chunk size ~4000 tokens)", title="[bold magenta]VIDEO INFO[/bold magenta]", box=box.DOUBLE))
        console.print("[bold blue]Type your question and press Enter. Type 'exit' to quit.[/bold blue]\n")
        
        # Initialize predictor with proper API key
        try:
            api_key = config_manager.get_api_key()
            if not api_key:
                raise ValueError("No API key configured")
            predictor = GeminiBatchPredictor(api_key=api_key, use_persistent_cache=True)
        except Exception as e:
            console.print(f"[bold red]❌ Error initializing predictor: {e}[/bold red]")
            return
        try:
            while True:
                if question_history:
                    console.print(Panel("\n".join([f"[bold cyan]Q{idx+1}:[/bold cyan] {q}" for idx, q in enumerate(question_history)]), title="[bold yellow]Your Question History[/bold yellow]", style="yellow", box=box.ROUNDED))
                question = Prompt.ask("[bold yellow]\nAsk a question about the video[/bold yellow]").strip()
                if question.lower() in ("exit", "quit"): break
                question_history.append(question)
                console.rule("[bold cyan]PROCESS: Semantic Chunking & Context Selection[/bold cyan]")
                context = find_relevant_chunk(question, chunks)
                context_tokens = estimate_tokens(context)
                console.print(f"[bold]Selected chunk size:[/bold] {context_tokens} tokens (vs. {total_tokens_full} for full transcript)")
                console.print("[bold]Checking cache...[/bold]")
                cache_key = predictor._make_cache_key(video_id, question, context)
                cached = None
                if hasattr(predictor.cache, 'get'):
                    cached = predictor.cache.get(cache_key)
                    if asyncio.iscoroutine(cached):
                        cached = await cached
                cache_lookups += 1
                if cached:
                    cache_hits += 1
                    console.print(Panel(cached, title="[bold green]ANSWER (from cache)[/bold green]", style="green", box=box.ROUNDED))
                    tokens_saved = total_tokens_full - context_tokens
                    if tokens_saved > 0:
                        console.print(f"[bold green]Tokens saved this question:[/bold green] {tokens_saved}")
                    else:
                        console.print(f"[bold yellow]No tokens saved: full context was used.[/bold yellow]")
                    console.print(f"[bold green]Running total tokens saved:[/bold green] {total_tokens_saved + tokens_saved}")
                    total_tokens_saved += tokens_saved
                    continue
                with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
                    progress.add_task(description="Sending context to Gemini API...", total=None)
                    questions = [{"question": question}]
                    results = await predictor.predict_batch(context, questions, use_chunking=False, video_id=video_id, context_override=context)
                console.print(Panel(results[0]["answer"], title="[bold blue]ANSWER[/bold blue]", style="blue", box=box.ROUNDED))
                total_tokens_sent += context_tokens
                tokens_saved = total_tokens_full - context_tokens
                if tokens_saved > 0:
                    console.print(f"[bold cyan]Tokens saved this question:[/bold cyan] {tokens_saved}")
                else:
                    console.print(f"[bold yellow]No tokens saved: full context was used.[/bold yellow]")
                console.print(f"[bold cyan]Running total tokens saved:[/bold cyan] {total_tokens_saved + tokens_saved}")
                total_tokens_saved += tokens_saved
                followup = Prompt.ask("[bold yellow]Is the answer satisfactory? (y/n)[/bold yellow]").strip().lower()
                if followup == 'n':
                    console.print("[bold magenta][INFO] Expanding context to more chunks...[/bold magenta]")
                    scored_chunks = [(c, sum(c.lower().count(k) for k in question.lower().split())) for c in chunks]
                    top_chunks = sorted(scored_chunks, key=lambda x: -x[1])[:3]
                    merged_context = '\n'.join([c[0] for c in top_chunks])
                    merged_tokens = estimate_tokens(merged_context)
                    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
                        progress.add_task(description="Sending expanded context to Gemini API...", total=None)
                        results = await predictor.predict_batch(merged_context, questions, use_chunking=False, video_id=video_id, context_override=merged_context)
                    console.print(Panel(results[0]["answer"], title="[bold magenta]EXPANDED ANSWER[/bold magenta]", style="magenta", box=box.ROUNDED))
                    total_tokens_sent += merged_tokens
                    tokens_saved = total_tokens_full - merged_tokens
                    if tokens_saved > 0:
                        console.print(f"[bold magenta]Tokens saved (expanded):[/bold magenta] {tokens_saved}")
                    else:
                        console.print(f"[bold yellow]No tokens saved: full context was used.[/bold yellow]")
                    console.print(f"[bold magenta]Running total tokens saved:[/bold magenta] {total_tokens_saved + tokens_saved}")
                    total_tokens_saved += tokens_saved
        finally:
            await predictor.close()
        # Show summary dashboard
        console.rule("[bold green]SESSION SUMMARY[/bold green]")
        table = Table(title="Gemini API Usage Summary", show_lines=True, box=box.DOUBLE)
        table.add_column("Metric", style="bold")
        table.add_column("Value", style="cyan")
        table.add_row("Total tokens sent", str(total_tokens_sent))
        table.add_row("Total tokens saved", str(total_tokens_saved))
        table.add_row("Cache lookups", str(cache_lookups))
        table.add_row("Cache hits", str(cache_hits))
        hit_rate = f"{(cache_hits / cache_lookups * 100):.1f}%" if cache_lookups else "0%"
        table.add_row("Cache hit rate", hit_rate)
        console.print(table)
        console.print(Align.center("[bold cyan]Analysis complete! Thank you for using HALO![/bold cyan]", vertical="middle"))

# Main CLI application
async def run_cli():
    """Main CLI application with menu system"""
    try:
        while True:
            action = show_main_menu()
            
            if action == "analyze":
                await analyze_video()
                if not Confirm.ask("\n[yellow]Would you like to analyze another video?[/yellow]"):
                    break
            elif action == "config":
                manage_config()
                input("\nPress Enter to continue...")
            elif action == "version":
                show_version()
                input("\nPress Enter to continue...")
            elif action == "upgrade":
                check_for_updates()
                input("\nPress Enter to continue...")
            elif action == "help":
                show_help()
                input("\nPress Enter to continue...")
            elif action == "exit":
                break
                
    except KeyboardInterrupt:
        pass
    
    console.print("\n[bold cyan]👋 Thank you for using HALO Video![/bold cyan]")
    console.print("[green]Made with ❤️  for the AI community[/green]")

# Legacy function name for backward compatibility
async def interactive_cli():
    """Legacy function for backward compatibility"""
    await run_cli()

def main():
    """Main entry point for the CLI application."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="🎥 HALO Video - AI-powered YouTube video analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  halo-video              Start interactive CLI
  halo-video --version    Show version
  halo-video --help       Show this help

For more information, visit: https://github.com/jeet-dekivadia/halo-video
        """
    )
    parser.add_argument('--version', action='version', version=f'HALO Video {__version__}')
    parser.add_argument('--config', action='store_true', help='Manage API key configuration')
    parser.add_argument('--reset', action='store_true', help='Reset API key')
    parser.add_argument('--upgrade-check', action='store_true', help='Check for updates')
    
    args = parser.parse_args()
    
    try:
        if args.config:
            manage_config()
        elif args.reset:
            config_manager = ConfigManager()
            config_manager.clear_config()
            setup_api_key(config_manager, force_reset=True)
        elif args.upgrade_check:
            check_for_updates()
        else:
            # Show welcome message for first-time users
            config_manager = ConfigManager()
            if not config_manager.has_api_key():
                console.print(Panel(
                    """[bold green]🎉 Welcome to HALO Video![/bold green]
                    
[yellow]This appears to be your first time using HALO Video.[/yellow]
You'll be guided through the setup process.

[cyan]💡 Tip: Get your free Gemini API key at:[/cyan]
[blue]https://makersuite.google.com/app/apikey[/blue]""",
                    title="[bold magenta]First Time Setup[/bold magenta]",
                    box=box.DOUBLE
                ))
            
            asyncio.run(run_cli())
    except KeyboardInterrupt:
        console.print("\n[bold yellow]👋 Goodbye![/bold yellow]")
    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]")
        console.print("[dim]For help, run: halo-video --help[/dim]")

if __name__ == "__main__":
    main()
