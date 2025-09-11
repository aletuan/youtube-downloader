#!/usr/bin/env python3
"""Event handler functions for YouTube Downloader GUI"""

import flet as ft
import threading
import platform
import subprocess
from pathlib import Path

from core.downloader import download_youtube_video, _get_video_info, _check_video_exists
from core.validation import validate_youtube_url, validate_output_directory, classify_error_type
from core.progress import DownloadProgress
from config.settings import DEFAULT_OUTPUT_DIR
from gui.ui_factory import get_common_folders

# Global variable to track active download thread
_active_download_thread = None
_download_cancelled = False

# Global variable to track downloaded video path for playback
_last_downloaded_video_path = None


def handle_folder_browse(page: ft.Page, output_dir_input: ft.TextField, status_text: ft.Text):
    """Handle folder browse button click"""
    def folder_thread():
        # Try native dialog with very short timeout
        selected_path = None
        if platform.system() == "Darwin":  # macOS
            try:
                result = subprocess.run([
                    "osascript", "-e", 
                    'tell application "Finder" to return POSIX path of (choose folder with prompt "Select Output Directory")'
                ], capture_output=True, text=True, timeout=5)  # Very short timeout
                if result.returncode == 0:
                    selected_path = result.stdout.strip()
            except (subprocess.TimeoutExpired, Exception):
                selected_path = None
        
        if selected_path:
            # Success - update UI
            path_obj = Path(selected_path)
            if path_obj.exists() and path_obj.is_dir():
                output_dir_input.value = selected_path
                status_text.value = f"✅ Output directory set: {path_obj.name}/"
                status_text.color = ft.Colors.GREEN_600
        else:
            # Failed - show helpful shortcuts
            shortcuts = get_common_folders()
            
            # Set to Downloads as a good default
            downloads_path = shortcuts["Downloads"]
            if Path(downloads_path).exists():
                output_dir_input.value = downloads_path
                status_text.value = f"📥 Set to Downloads folder. You can edit the path above or drag & drop a folder."
                status_text.color = ft.Colors.BLUE_600
            else:
                status_text.value = "📝 Please type or paste your desired folder path above"
                status_text.color = ft.Colors.ORANGE_600
        
        page.update()
    
    # Run in thread
    threading.Thread(target=folder_thread, daemon=True).start()


def handle_preview_click(
    page: ft.Page,
    url_input: ft.TextField, 
    output_dir_input: ft.TextField,
    status_text: ft.Text,
    video_info_card: ft.Card,
    download_button: ft.ElevatedButton,
    preview_button: ft.ElevatedButton
):
    """Handle preview button click"""
    url = url_input.value.strip() if url_input.value else ""
    
    # Validate URL
    is_valid, error_msg = validate_youtube_url(url)
    if not is_valid:
        status_text.value = error_msg
        status_text.color = ft.Colors.RED_600
        page.update()
        return
    
    # Disable preview button and show loading
    preview_button.disabled = True
    status_text.value = "🔄 Getting video information..."
    status_text.color = ft.Colors.BLUE_600
    page.update()
    
    # Run preview in separate thread
    def preview_thread():
        try:
            # Get video information
            video_title, video_id = _get_video_info(url)
            output_dir = output_dir_input.value.strip() or DEFAULT_OUTPUT_DIR
            
            # Check if video already exists
            exists, video_folder, existing_files = _check_video_exists(output_dir, video_title, video_id)
            
            # Update video info display
            info_column = video_info_card.content.content
            info_column.controls[1].value = f"Title: {video_title}"
            info_column.controls[2].value = f"ID: {video_id}"
            info_column.controls[3].value = f"Output folder: {video_folder.name}/"
            
            # Update download status based on existence
            if exists:
                info_column.controls[4].value = f"⚠️ Already downloaded! Files: {', '.join(existing_files)}"
                info_column.controls[4].color = ft.Colors.ORANGE_600
                download_button.text = "Re-download"
                download_button.bgcolor = ft.Colors.ORANGE_400
                download_button.icon = ft.Icons.REFRESH
                status_text.value = "⚠️ Video already exists. Click Re-download to download again."
                status_text.color = ft.Colors.ORANGE_600
            else:
                info_column.controls[4].value = "✅ Ready to download"
                info_column.controls[4].color = ft.Colors.GREEN_600
                download_button.text = "Download"
                download_button.bgcolor = ft.Colors.RED_400
                download_button.icon = ft.Icons.DOWNLOAD
                status_text.value = "✅ Video information loaded. Ready to download!"
                status_text.color = ft.Colors.GREEN_600
            
            # Show video info card and enable download
            video_info_card.visible = True
            download_button.disabled = False
            
        except Exception as error:
            # Error handling
            status_text.value = f"❌ Error getting video info: {str(error)}"
            status_text.color = ft.Colors.RED_600
            video_info_card.visible = False
            download_button.disabled = True
        
        finally:
            # Re-enable preview button
            preview_button.disabled = False
            page.update()
    
    # Start preview thread
    threading.Thread(target=preview_thread, daemon=True).start()


def handle_download_click(
    page: ft.Page,
    url_input: ft.TextField,
    output_dir_input: ft.TextField,
    status_text: ft.Text,
    progress_bar: ft.ProgressBar,
    progress_info: ft.Text,
    download_button: ft.ElevatedButton,
    preview_button: ft.ElevatedButton,
    play_button: ft.ElevatedButton = None
):
    """Handle download button click"""
    url = url_input.value.strip() if url_input.value else ""
    output_dir = output_dir_input.value.strip()
    
    # Validate inputs
    is_valid_url, url_error = validate_youtube_url(url)
    if not is_valid_url:
        status_text.value = url_error
        status_text.color = ft.Colors.RED_600
        page.update()
        return
    
    if not output_dir:
        output_dir = DEFAULT_OUTPUT_DIR
        output_dir_input.value = DEFAULT_OUTPUT_DIR
    
    is_valid_dir, dir_error = validate_output_directory(output_dir)
    if not is_valid_dir:
        status_text.value = dir_error
        status_text.color = ft.Colors.RED_600
        page.update()
        return
    
    # Disable buttons and show progress
    download_button.disabled = True
    preview_button.disabled = True
    progress_bar.visible = True
    progress_info.visible = True
    status_text.value = "🔄 Starting download..."
    status_text.color = ft.Colors.BLUE_600
    page.update()
    
    # Run download in separate thread to avoid blocking UI
    def download_thread():
        global _download_cancelled
        _download_cancelled = False
        
        try:
            # Check if download was cancelled before starting
            if _download_cancelled:
                return
                
            # Check if this is a re-download
            is_redownload = download_button.text == "Re-download"
            action_text = "Re-downloading" if is_redownload else "Downloading"
            
            # Create progress callback for GUI updates
            def progress_callback(progress: DownloadProgress):
                """Update GUI with download progress"""
                try:
                    # Check if download was cancelled
                    if _download_cancelled:
                        return
                        
                    if progress.status == "downloading":
                        # Update progress bar
                        progress_bar.value = progress.percent / 100.0 if progress.percent else None
                        
                        # Update status text
                        status_text.value = f"🔄 {action_text} - {progress.percent_str}"
                        
                        # Update progress info with detailed information
                        progress_info.value = f"{progress.size_str} | {progress.speed_str} | ETA: {progress.eta_str}"
                        
                    elif progress.status == "finished":
                        # Download completed
                        progress_bar.value = 1.0
                        status_text.value = f"✅ {action_text} completed!"
                        progress_info.value = f"Completed in {progress.elapsed:.1f}s"
                        
                    elif progress.status == "error":
                        # Download error
                        status_text.value = f"❌ {action_text} failed"
                        progress_info.value = f"Failed after {progress.elapsed:.1f}s"
                    
                    # Update the UI
                    page.update()
                except Exception:
                    # Don't let UI update errors break the download
                    pass
            
            # Update status with more details
            status_text.value = f"🔄 {action_text} video to {output_dir}..."
            page.update()
            
            # Perform download with enhanced error handling and progress tracking
            download_youtube_video(url, output_dir, progress_callback=progress_callback)
            
            # Get final video info for success message and video path tracking
            try:
                video_title, video_id = _get_video_info(url)
                final_folder = Path(output_dir) / f"{video_title}_{video_id}"
                
                # Find the downloaded video file
                global _last_downloaded_video_path
                _last_downloaded_video_path = None
                if final_folder.exists():
                    # Look for common video file extensions
                    video_extensions = ['.mp4', '.mkv', '.webm', '.avi', '.mov', '.m4v', '.flv']
                    found_files = []
                    
                    for file_path in final_folder.iterdir():
                        if file_path.is_file():
                            found_files.append(str(file_path))
                            if file_path.suffix.lower() in video_extensions:
                                _last_downloaded_video_path = str(file_path)
                                print(f"[DEBUG] Video file found: {_last_downloaded_video_path}")
                                break
                    
                    if not _last_downloaded_video_path and found_files:
                        print(f"[DEBUG] No video file found. Files in folder: {found_files}")
                    elif not found_files:
                        print(f"[DEBUG] No files found in folder: {final_folder}")
                
                if is_redownload:
                    status_text.value = f"✅ Re-download completed!\nSaved to: {final_folder}"
                else:
                    status_text.value = f"✅ Download completed!\nSaved to: {final_folder}"
            except:
                action_text = "Re-download" if is_redownload else "Download"
                status_text.value = f"✅ {action_text} completed! Saved to: {output_dir}"
            
            status_text.color = ft.Colors.GREEN_600
            
            # Show play button if video was successfully downloaded
            if play_button and _last_downloaded_video_path:
                play_button.visible = True
                
        except Exception as error:
            # Enhanced error handling with more specific messages
            status_text.value = classify_error_type(str(error))
            status_text.color = ft.Colors.RED_600
        
        finally:
            # Re-enable buttons and hide progress
            download_button.disabled = False
            preview_button.disabled = False
            # Keep progress bar visible for a moment to show completion
            # progress_bar.visible = False  # Let user see the completed progress
            progress_info.visible = False
            
            # Check if cancelled and update status accordingly
            if _download_cancelled:
                status_text.value = "⏹️ Download cancelled"
                status_text.color = ft.Colors.ORANGE_600
                progress_bar.visible = False
                progress_bar.value = None
                progress_info.visible = False
                progress_info.value = ""
            
            # Clear the active download thread reference
            global _active_download_thread
            _active_download_thread = None
            page.update()
    
    # Start download thread and store reference
    _active_download_thread = threading.Thread(target=download_thread, daemon=True)
    _active_download_thread.start()


# Reset/Clear functionality removed - simplified UI without reset button


def handle_play_click(page: ft.Page, video_title: str = "Video"):
    """Handle play button click - navigate to video player screen"""
    global _last_downloaded_video_path
    
    print(f"[DEBUG] Play button clicked. Video path: {_last_downloaded_video_path}")
    print(f"[DEBUG] Video title: {video_title}")
    
    if not _last_downloaded_video_path:
        print("[DEBUG] No video path available")
        return
        
    if not Path(_last_downloaded_video_path).exists():
        print(f"[DEBUG] Video file does not exist at path: {_last_downloaded_video_path}")
        return
    
    print(f"[DEBUG] Loading video player for file: {_last_downloaded_video_path}")
    
    # Import here to avoid circular imports
    from gui.video_player import VideoPlayerScreen
    
    # Create video player screen
    player_screen = VideoPlayerScreen(page)
    player_view = player_screen.create_player_view(_last_downloaded_video_path, video_title)
    
    # Navigate to video player
    print(f"[DEBUG] Current views before adding player: {len(page.views)}")
    page.views.append(player_view)
    print(f"[DEBUG] Views after adding player: {len(page.views)}")
    page.update()
    
    print("[DEBUG] Video player screen should now be displayed")


def handle_theme_toggle(page: ft.Page):
    """Handle theme toggle button click"""
    page.theme_mode = (
        ft.ThemeMode.DARK 
        if page.theme_mode == ft.ThemeMode.LIGHT 
        else ft.ThemeMode.LIGHT
    )
    page.update()


def handle_file_picker_result(
    e: ft.FilePickerResultEvent,
    output_dir_input: ft.TextField,
    status_text: ft.Text,
    page: ft.Page
):
    """Handle file picker result (fallback for other platforms)"""
    if e.path:
        selected_path = Path(e.path)
        if selected_path.exists() and selected_path.is_dir():
            output_dir_input.value = e.path
            status_text.value = f"✅ Output directory set: {selected_path.name}/"
            status_text.color = ft.Colors.GREEN_600
        else:
            status_text.value = f"❌ Invalid directory selected: {e.path}"
            status_text.color = ft.Colors.RED_600
    else:
        status_text.value = "Ready to download"
        status_text.color = ft.Colors.GREY_700
    page.update()