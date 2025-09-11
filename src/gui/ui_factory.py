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
        size=32,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.RED_400
    )
    
    subtitle = ft.Text(
        "Download YouTube videos with subtitles",
        size=16,
        color=ft.Colors.GREY_600
    )
    
    return title, subtitle


def create_input_section() -> tuple:
    """Create URL input and output directory input with browse button"""
    url_input = ft.TextField(
        label="YouTube URL",
        hint_text="https://www.youtube.com/watch?v=...",
        width=600,
        border_radius=8,
        prefix_icon=ft.Icons.LINK,
        content_padding=ft.padding.all(12)
    )
    
    output_dir_input = ft.TextField(
        label="Output Directory",
        value=DEFAULT_OUTPUT_DIR,
        width=560,  # Reduced to accommodate button with spacing
        border_radius=8,
        prefix_icon=ft.Icons.FOLDER,
        hint_text="Select or enter output directory path",
        content_padding=ft.padding.all(12)
    )
    
    browse_button = ft.IconButton(
        ft.Icons.FOLDER_OPEN,
        tooltip="Browse for folder",
        icon_size=20
    )
    
    dir_row = ft.Container(
        content=ft.Row(
            [output_dir_input, browse_button],
            spacing=8,
            alignment=ft.MainAxisAlignment.START  # Align to start for consistent left edge
        ),
        width=600,  # Same width as URL input
        alignment=ft.alignment.center_left
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
        height=45,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
    )
    
    download_button = ft.ElevatedButton(
        "Download Video",
        icon=ft.Icons.DOWNLOAD,
        bgcolor=ft.Colors.RED_400,
        color=ft.Colors.WHITE,
        width=180,
        height=45,
        disabled=True,  # Initially disabled until preview
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
    )
    
    clear_button = ft.OutlinedButton(
        "Reset",
        icon=ft.Icons.REFRESH,
        width=120,
        height=45,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            side=ft.BorderSide(1, ft.Colors.GREY_400)
        )
    )
    
    button_row = ft.Row(
        [preview_button, download_button, clear_button],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=12
    )
    
    return preview_button, download_button, clear_button, button_row


def create_status_section() -> tuple:
    """Create status display and progress components"""
    status_text = ft.Text(
        "Ready to download",
        size=14,
        color=ft.Colors.GREY_600,
        text_align=ft.TextAlign.CENTER
    )
    
    progress_bar = ft.ProgressBar(
        width=580,
        visible=False,
        color=ft.Colors.RED_400,
        bgcolor=ft.Colors.GREY_200,
        border_radius=4
    )
    
    # Additional progress information
    progress_info = ft.Text(
        "",
        size=11,
        color=ft.Colors.GREY_500,
        visible=False,
        text_align=ft.TextAlign.CENTER
    )
    
    return status_text, progress_bar, progress_info


def create_video_info_card() -> ft.Card:
    """Create video information display card"""
    video_info_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("Video Information", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.GREY_700),
                ft.Text("", key="video_title", size=13),
                ft.Text("", key="video_id", size=12, color=ft.Colors.GREY_600),
                ft.Text("", key="video_folder", size=12, color=ft.Colors.GREY_600),
                ft.Text("", key="download_status", size=13),
            ], spacing=4),
            padding=12,
            border_radius=8
        ),
        visible=False,
        elevation=1
    )
    return video_info_card


def create_config_section() -> ft.Container:
    """Create download configuration display"""
    config_info = ft.Container(
        content=ft.Column([
            ft.Text("Settings", weight=ft.FontWeight.W_500, size=12, color=ft.Colors.GREY_500),
            ft.Text(f"Format: {VIDEO_FORMAT} • Subtitles: {', '.join(SUBTITLE_LANGUAGES)}", 
                   size=11, color=ft.Colors.GREY_400),
        ], spacing=1),
        padding=8,
        border_radius=4,
        bgcolor=ft.Colors.GREY_100,
        border=ft.border.all(0.5, ft.Colors.GREY_200)
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
        "Modern YouTube Downloader with Love",
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
                spacing=6
            ),
            padding=40,
            border_radius=12,
            height=650  # Make card taller
        ),
        elevation=4
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