#!/usr/bin/env python3
"""
YouTube Downloader GUI - Modern Flet Interface

A Material Design GUI for downloading YouTube videos with subtitles.
"""

import flet as ft
import sys
import os
import threading
import platform
import subprocess
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import core functionality
from core.downloader import download_youtube_video, _get_video_info, _check_video_exists
from config.settings import (
    DEFAULT_OUTPUT_DIR,
    SUBTITLE_LANGUAGES,
    SUBTITLE_FORMAT,
    VIDEO_FORMAT
)

def main(page: ft.Page):
    """Main YouTube Downloader GUI entry point"""
    
    # Configure page properties
    page.title = "YouTube Downloader"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.window_width = 800
    page.window_height = 600
    page.window_resizable = True
    page.padding = 20
    
    
    # Create UI components
    title = ft.Text(
        "YouTube Downloader",
        size=36,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.RED_400
    )
    
    subtitle = ft.Text(
        "Download YouTube videos with subtitles",
        size=18,
        color=ft.Colors.GREY_600
    )
    
    # URL input field
    url_input = ft.TextField(
        label="YouTube URL",
        hint_text="https://www.youtube.com/watch?v=...",
        width=600,
        border_radius=10,
        prefix_icon=ft.Icons.LINK
    )
    
    # Output directory input
    output_dir_input = ft.TextField(
        label="Output Directory",
        value=DEFAULT_OUTPUT_DIR,
        width=520,
        border_radius=10,
        prefix_icon=ft.Icons.FOLDER,
        hint_text="Select or enter output directory path"
    )
    
    # Simple helper to get user home shortcuts
    def get_common_folders():
        """Get common user folders"""
        import os
        return {
            "Desktop": os.path.expanduser("~/Desktop"),
            "Documents": os.path.expanduser("~/Documents"), 
            "Downloads": os.path.expanduser("~/Downloads"),
            "Movies": os.path.expanduser("~/Movies"),
            "Home": os.path.expanduser("~")
        }

    # Flet FilePicker callback (fallback for other platforms)  
    def get_directory_result(e: ft.FilePickerResultEvent):
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
    
    # Create the FilePicker as fallback
    file_picker = ft.FilePicker(on_result=get_directory_result)
    
    # Browse button for output directory  
    def browse_folder(_):
        # Simple fallback approach for macOS
        def show_folder_help():
            status_text.value = "💡 Click here to set common folders: Desktop, Documents, Downloads"
            status_text.color = ft.Colors.BLUE_600
            page.update()
            
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
    
    browse_button = ft.IconButton(
        ft.Icons.FOLDER_OPEN,
        on_click=browse_folder,
        tooltip="Browse for folder"
    )
    
    # Directory row
    dir_row = ft.Row(
        [output_dir_input, browse_button],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10
    )
    
    # Status display
    status_text = ft.Text(
        "Ready to download",
        size=16,
        color=ft.Colors.GREY_700
    )
    
    # Video info display (initially hidden)
    video_info_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("Video Information", weight=ft.FontWeight.BOLD, size=16),
                ft.Text("", key="video_title"),
                ft.Text("", key="video_id"),
                ft.Text("", key="video_folder"),
                ft.Text("", key="download_status"),
            ], spacing=5),
            padding=15,
            border_radius=10
        ),
        visible=False,
        elevation=2
    )
    
    # Configuration display
    config_info = ft.Container(
        content=ft.Column([
            ft.Text("Download Settings", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.GREY_600),
            ft.Text(f"Format: {VIDEO_FORMAT}", size=12, color=ft.Colors.GREY_500),
            ft.Text(f"Subtitles: {', '.join(SUBTITLE_LANGUAGES)} ({SUBTITLE_FORMAT})", size=12, color=ft.Colors.GREY_500),
        ], spacing=2),
        padding=10,
        border_radius=5,
        bgcolor=ft.Colors.GREY_50,
        border=ft.border.all(1, ft.Colors.GREY_300)
    )
    
    # Progress bar
    progress_bar = ft.ProgressBar(
        width=600,
        visible=False,
        color=ft.Colors.RED_400
    )
    
    # Preview button click handler
    def on_preview_click(_):
        url = url_input.value.strip()
        
        # Validate URL
        if not url:
            status_text.value = "❌ Please enter a YouTube URL"
            status_text.color = ft.Colors.RED_600
            page.update()
            return
        
        if not url.startswith(('https://www.youtube.com/', 'https://youtube.com/', 'https://youtu.be/')):
            status_text.value = "❌ Please enter a valid YouTube URL"
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
                    download_button.text = "Re-download Video"
                    download_button.bgcolor = ft.Colors.ORANGE_400
                    download_button.icon = ft.Icons.REFRESH
                    status_text.value = "⚠️ Video already exists. Click Re-download to download again."
                    status_text.color = ft.Colors.ORANGE_600
                else:
                    info_column.controls[4].value = "✅ Ready to download"
                    info_column.controls[4].color = ft.Colors.GREEN_600
                    download_button.text = "Download Video"
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
    
    # Download button click handler
    def on_download_click(_):
        url = url_input.value.strip()
        output_dir = output_dir_input.value.strip()
        
        # Validate inputs (enhanced validation)
        if not url:
            status_text.value = "❌ Please enter a YouTube URL"
            status_text.color = ft.Colors.RED_600
            page.update()
            return
        
        if not url.startswith(('https://www.youtube.com/', 'https://youtube.com/', 'https://youtu.be/')):
            status_text.value = "❌ Please enter a valid YouTube URL"
            status_text.color = ft.Colors.RED_600
            page.update()
            return
        
        if not output_dir:
            output_dir = DEFAULT_OUTPUT_DIR
            output_dir_input.value = DEFAULT_OUTPUT_DIR
        
        # Check if output directory exists
        output_path = Path(output_dir)
        if not output_path.exists():
            try:
                output_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                status_text.value = f"❌ Cannot create output directory: {str(e)}"
                status_text.color = ft.Colors.RED_600
                page.update()
                return
        
        # Disable buttons and show progress
        download_button.disabled = True
        preview_button.disabled = True
        progress_bar.visible = True
        status_text.value = "🔄 Starting download..."
        status_text.color = ft.Colors.BLUE_600
        page.update()
        
        # Run download in separate thread to avoid blocking UI
        def download_thread():
            try:
                # Check if this is a re-download
                is_redownload = download_button.text == "Re-download Video"
                action_text = "Re-downloading" if is_redownload else "Downloading"
                
                # Update status with more details
                status_text.value = f"🔄 {action_text} video to {output_dir}..."
                page.update()
                
                # Perform download with enhanced error handling
                download_youtube_video(url, output_dir)
                
                # Get final video info for success message
                try:
                    video_title, video_id = _get_video_info(url)
                    final_folder = Path(output_dir) / f"{video_title}_{video_id}"
                    if is_redownload:
                        status_text.value = f"✅ Re-download completed!\nSaved to: {final_folder}"
                    else:
                        status_text.value = f"✅ Download completed!\nSaved to: {final_folder}"
                except:
                    action_text = "Re-download" if is_redownload else "Download"
                    status_text.value = f"✅ {action_text} completed! Saved to: {output_dir}"
                
                status_text.color = ft.Colors.GREEN_600
                
            except Exception as error:
                # Enhanced error handling with more specific messages
                error_msg = str(error)
                if "Network" in error_msg or "connection" in error_msg.lower():
                    status_text.value = f"❌ Network error: Check your internet connection"
                elif "permission" in error_msg.lower():
                    status_text.value = f"❌ Permission error: Check folder write permissions"
                elif "not found" in error_msg.lower():
                    status_text.value = f"❌ Video not found: Invalid URL or private video"
                else:
                    status_text.value = f"❌ Error: {error_msg}"
                
                status_text.color = ft.Colors.RED_600
            
            finally:
                # Re-enable buttons and hide progress
                download_button.disabled = False
                preview_button.disabled = False
                progress_bar.visible = False
                page.update()
        
        # Start download thread
        threading.Thread(target=download_thread, daemon=True).start()
    
    # Clear button handler
    def on_clear_click(_):
        url_input.value = ""
        output_dir_input.value = DEFAULT_OUTPUT_DIR
        status_text.value = "Ready to download"
        status_text.color = ft.Colors.GREY_700
        progress_bar.visible = False
        video_info_card.visible = False
        
        # Reset download button to original state
        download_button.disabled = True
        download_button.text = "Download Video"
        download_button.bgcolor = ft.Colors.RED_400
        download_button.icon = ft.Icons.DOWNLOAD
        
        page.update()
    
    # Create buttons
    preview_button = ft.ElevatedButton(
        "Preview Video",
        icon=ft.Icons.PREVIEW,
        on_click=on_preview_click,
        bgcolor=ft.Colors.BLUE_400,
        color=ft.Colors.WHITE,
        width=160,
        height=50
    )
    
    download_button = ft.ElevatedButton(
        "Download Video",
        icon=ft.Icons.DOWNLOAD,
        on_click=on_download_click,
        bgcolor=ft.Colors.RED_400,
        color=ft.Colors.WHITE,
        width=180,
        height=50,
        disabled=True  # Initially disabled until preview
    )
    
    clear_button = ft.OutlinedButton(
        "Clear",
        icon=ft.Icons.CLEAR,
        on_click=on_clear_click,
        width=120,
        height=50
    )
    
    # Button row
    button_row = ft.Row(
        [preview_button, download_button, clear_button],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=15
    )
    
    # Theme toggle button
    def toggle_theme(_):
        page.theme_mode = (
            ft.ThemeMode.DARK 
            if page.theme_mode == ft.ThemeMode.LIGHT 
            else ft.ThemeMode.LIGHT
        )
        page.update()
    
    theme_button = ft.IconButton(
        ft.Icons.DARK_MODE,
        on_click=toggle_theme,
        tooltip="Toggle Dark/Light Mode"
    )
    
    # Create main container with Material Design card
    main_card = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    title,
                    subtitle,
                    ft.Divider(height=25, color=ft.Colors.TRANSPARENT),
                    url_input,
                    ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                    dir_row,
                    ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                    config_info,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    button_row,
                    ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                    video_info_card,
                    progress_bar,
                    status_text,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8
            ),
            padding=35,
            border_radius=15
        ),
        elevation=8
    )
    
    # Footer with info
    footer = ft.Text(
        "Modern YouTube Downloader with Subtitles • Built with Flet",
        size=12,
        color=ft.Colors.GREY_500,
        text_align=ft.TextAlign.CENTER
    )
    
    # Add FilePicker to page overlay
    page.overlay.append(file_picker)
    
    # Add components to page
    page.add(
        ft.Column(
            [
                ft.Row(
                    [theme_button],
                    alignment=ft.MainAxisAlignment.END
                ),
                main_card,
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                footer
            ],
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )
    )

if __name__ == "__main__":
    # Run the YouTube Downloader GUI
    ft.app(target=main)