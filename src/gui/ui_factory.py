#!/usr/bin/env python3
"""UI component factory functions for YouTube Downloader GUI"""

import flet as ft
import os
from pathlib import Path
from config.settings import DEFAULT_OUTPUT_DIR, VIDEO_FORMAT, SUBTITLE_LANGUAGES, SUBTITLE_FORMAT


def create_header_section() -> tuple:
    """Create header title and subtitle components"""
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
    
    return title, subtitle


def create_input_section() -> tuple:
    """Create URL input and output directory input with browse button"""
    url_input = ft.TextField(
        label="YouTube URL",
        hint_text="https://www.youtube.com/watch?v=...",
        width=600,
        border_radius=10,
        prefix_icon=ft.Icons.LINK
    )
    
    output_dir_input = ft.TextField(
        label="Output Directory",
        value=DEFAULT_OUTPUT_DIR,
        width=520,
        border_radius=10,
        prefix_icon=ft.Icons.FOLDER,
        hint_text="Select or enter output directory path"
    )
    
    browse_button = ft.IconButton(
        ft.Icons.FOLDER_OPEN,
        tooltip="Browse for folder"
    )
    
    dir_row = ft.Row(
        [output_dir_input, browse_button],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10
    )
    
    return url_input, output_dir_input, browse_button, dir_row


def create_button_section() -> tuple:
    """Create action buttons (preview, download, clear)"""
    preview_button = ft.ElevatedButton(
        "Preview Video",
        icon=ft.Icons.PREVIEW,
        bgcolor=ft.Colors.BLUE_400,
        color=ft.Colors.WHITE,
        width=160,
        height=50
    )
    
    download_button = ft.ElevatedButton(
        "Download Video",
        icon=ft.Icons.DOWNLOAD,
        bgcolor=ft.Colors.RED_400,
        color=ft.Colors.WHITE,
        width=180,
        height=50,
        disabled=True  # Initially disabled until preview
    )
    
    clear_button = ft.OutlinedButton(
        "Clear",
        icon=ft.Icons.CLEAR,
        width=120,
        height=50
    )
    
    button_row = ft.Row(
        [preview_button, download_button, clear_button],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=15
    )
    
    return preview_button, download_button, clear_button, button_row


def create_status_section() -> tuple:
    """Create status display and progress components"""
    status_text = ft.Text(
        "Ready to download",
        size=16,
        color=ft.Colors.GREY_700
    )
    
    progress_bar = ft.ProgressBar(
        width=600,
        visible=False,
        color=ft.Colors.RED_400
    )
    
    # Additional progress information
    progress_info = ft.Text(
        "",
        size=12,
        color=ft.Colors.GREY_600,
        visible=False
    )
    
    return status_text, progress_bar, progress_info


def create_video_info_card() -> ft.Card:
    """Create video information display card"""
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
    return video_info_card


def create_config_section() -> ft.Container:
    """Create download configuration display"""
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
    return config_info


def create_theme_button() -> ft.IconButton:
    """Create theme toggle button"""
    theme_button = ft.IconButton(
        ft.Icons.DARK_MODE,
        tooltip="Toggle Dark/Light Mode"
    )
    return theme_button


def create_footer() -> ft.Text:
    """Create footer text"""
    footer = ft.Text(
        "Modern YouTube Downloader with Subtitles • Built with Flet",
        size=12,
        color=ft.Colors.GREY_500,
        text_align=ft.TextAlign.CENTER
    )
    return footer


def create_main_card(components: list) -> ft.Card:
    """Create main application card containing all components"""
    main_card = ft.Card(
        content=ft.Container(
            content=ft.Column(
                components,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8
            ),
            padding=35,
            border_radius=15
        ),
        elevation=8
    )
    return main_card


def get_common_folders() -> dict:
    """Get common user folders for folder shortcuts"""
    return {
        "Desktop": os.path.expanduser("~/Desktop"),
        "Documents": os.path.expanduser("~/Documents"), 
        "Downloads": os.path.expanduser("~/Downloads"),
        "Movies": os.path.expanduser("~/Movies"),
        "Home": os.path.expanduser("~")
    }