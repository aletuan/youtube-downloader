#!/usr/bin/env python3
"""
YouTube Downloader GUI - Modern Flet Interface

A Material Design GUI for downloading YouTube videos with subtitles.
"""

import flet as ft
import sys
import os
import threading
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import core functionality
from core.downloader import download_youtube_video
from config.settings import DEFAULT_OUTPUT_DIR

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
        width=500,
        border_radius=10,
        prefix_icon=ft.Icons.FOLDER
    )
    
    # Browse button for output directory
    def browse_folder(e):
        def get_directory_result(e: ft.FilePickerResultEvent):
            if e.path:
                output_dir_input.value = e.path
                page.update()
        
        get_directory_dialog = ft.FilePicker(on_result=get_directory_result)
        page.overlay.append(get_directory_dialog)
        page.update()
        get_directory_dialog.get_directory_path()
    
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
    
    # Progress bar
    progress_bar = ft.ProgressBar(
        width=600,
        visible=False,
        color=ft.Colors.RED_400
    )
    
    # Download button click handler
    def on_download_click(e):
        url = url_input.value.strip()
        output_dir = output_dir_input.value.strip()
        
        # Validate inputs
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
        
        # Disable download button and show progress
        download_button.disabled = True
        progress_bar.visible = True
        status_text.value = "🔄 Starting download..."
        status_text.color = ft.Colors.BLUE_600
        page.update()
        
        # Run download in separate thread to avoid blocking UI
        def download_thread():
            try:
                # Update status
                status_text.value = "🔄 Downloading video..."
                page.update()
                
                # Perform download
                download_youtube_video(url, output_dir)
                
                # Success
                status_text.value = f"✅ Download completed! Saved to: {output_dir}"
                status_text.color = ft.Colors.GREEN_600
                
            except Exception as error:
                # Error handling
                status_text.value = f"❌ Error: {str(error)}"
                status_text.color = ft.Colors.RED_600
            
            finally:
                # Re-enable button and hide progress
                download_button.disabled = False
                progress_bar.visible = False
                page.update()
        
        # Start download thread
        threading.Thread(target=download_thread, daemon=True).start()
    
    # Clear button handler
    def on_clear_click(e):
        url_input.value = ""
        output_dir_input.value = DEFAULT_OUTPUT_DIR
        status_text.value = "Ready to download"
        status_text.color = ft.Colors.GREY_700
        progress_bar.visible = False
        page.update()
    
    # Create buttons
    download_button = ft.ElevatedButton(
        "Download Video",
        icon=ft.Icons.DOWNLOAD,
        on_click=on_download_click,
        bgcolor=ft.Colors.RED_400,
        color=ft.Colors.WHITE,
        width=200,
        height=50
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
        [download_button, clear_button],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )
    
    # Theme toggle button
    def toggle_theme(e):
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
                    ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
                    url_input,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    dir_row,
                    ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
                    button_row,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    progress_bar,
                    status_text,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            padding=40,
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