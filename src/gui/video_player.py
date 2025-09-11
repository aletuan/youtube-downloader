#!/usr/bin/env python3
"""Video Player Screen for YouTube Downloader GUI"""

import flet as ft
import os
from pathlib import Path
from typing import Optional


class VideoPlayerScreen:
    """Video player screen with navigation and playback controls"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.video_path: Optional[str] = None
        self.video_title: Optional[str] = None
        
    def create_player_view(self, video_path: str, video_title: str = "Video") -> ft.View:
        """Create the video player view"""
        self.video_path = video_path
        self.video_title = video_title
        
        # Back button
        back_button = ft.IconButton(
            ft.Icons.ARROW_BACK,
            tooltip="Back to Downloader",
            on_click=self._on_back_click,
            icon_size=24
        )
        
        # Video title
        title_text = ft.Text(
            video_title,
            size=20,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.GREY_800,
            text_align=ft.TextAlign.CENTER
        )
        
        # Video player component
        video_player = self._create_video_player()
        
        # Control buttons
        control_buttons = self._create_control_buttons()
        
        # Video info
        video_info = self._create_video_info()
        
        # Main content
        content = ft.Column([
            # Header with back button and title
            ft.Row([
                back_button,
                ft.Container(
                    content=title_text,
                    expand=True,
                    alignment=ft.alignment.center
                )
            ]),
            
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            
            # Video player
            ft.Container(
                content=video_player,
                alignment=ft.alignment.center,
                bgcolor=ft.Colors.BLACK12,
                border_radius=12,
                padding=10
            ),
            
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            
            # Controls
            control_buttons,
            
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            
            # Video info
            video_info
            
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
        
        return ft.View(
            route="/player",
            controls=[
                ft.Container(
                    content=content,
                    padding=20,
                    expand=True
                )
            ],
            bgcolor=ft.Colors.WHITE
        )
    
    def _create_video_player(self) -> ft.Video:
        """Create the video player component"""
        if not self.video_path or not os.path.exists(self.video_path):
            # Show placeholder if video not found
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.VIDEO_FILE, size=64, color=ft.Colors.GREY_400),
                    ft.Text("Video not found", color=ft.Colors.GREY_600)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=640,
                height=360,
                bgcolor=ft.Colors.GREY_100,
                border_radius=8,
                alignment=ft.alignment.center
            )
        
        # Create video player
        video = ft.Video(
            width=640,
            height=360,
            playlist=[ft.VideoMedia(self.video_path)],
            playlist_mode=ft.PlaylistMode.NONE,
            fill_color=ft.Colors.BLACK,
            aspect_ratio=16/9,
            autoplay=False,
            show_controls=True,
            playback_rate=1.0,
        )
        
        return video
    
    def _create_control_buttons(self) -> ft.Row:
        """Create video control buttons"""
        play_button = ft.ElevatedButton(
            "Play",
            icon=ft.Icons.PLAY_ARROW,
            bgcolor=ft.Colors.GREEN_400,
            color=ft.Colors.WHITE,
            on_click=self._on_play_click
        )
        
        pause_button = ft.ElevatedButton(
            "Pause", 
            icon=ft.Icons.PAUSE,
            bgcolor=ft.Colors.ORANGE_400,
            color=ft.Colors.WHITE,
            on_click=self._on_pause_click
        )
        
        stop_button = ft.ElevatedButton(
            "Stop",
            icon=ft.Icons.STOP,
            bgcolor=ft.Colors.RED_400,
            color=ft.Colors.WHITE,
            on_click=self._on_stop_click
        )
        
        return ft.Row([
            play_button,
            pause_button, 
            stop_button
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=15)
    
    def _create_video_info(self) -> ft.Container:
        """Create video information display"""
        file_size = "Unknown"
        if self.video_path and os.path.exists(self.video_path):
            try:
                size_bytes = os.path.getsize(self.video_path)
                if size_bytes < 1024*1024:
                    file_size = f"{size_bytes/1024:.1f} KB"
                elif size_bytes < 1024*1024*1024:
                    file_size = f"{size_bytes/(1024*1024):.1f} MB"
                else:
                    file_size = f"{size_bytes/(1024*1024*1024):.1f} GB"
            except:
                file_size = "Unknown"
        
        info_content = ft.Column([
            ft.Text("Video Information", weight=ft.FontWeight.BOLD, size=14),
            ft.Text(f"File: {Path(self.video_path).name if self.video_path else 'Unknown'}", size=12),
            ft.Text(f"Size: {file_size}", size=12),
            ft.Text(f"Path: {self.video_path or 'Unknown'}", size=11, color=ft.Colors.GREY_600),
        ], spacing=5)
        
        return ft.Container(
            content=info_content,
            padding=15,
            bgcolor=ft.Colors.GREY_50,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.GREY_300)
        )
    
    def _on_back_click(self, e):
        """Handle back button click"""
        self.page.go("/")
    
    def _on_play_click(self, e):
        """Handle play button click"""
        # Video player controls are handled by the ft.Video component itself
        pass
    
    def _on_pause_click(self, e):
        """Handle pause button click"""
        # Video player controls are handled by the ft.Video component itself
        pass
    
    def _on_stop_click(self, e):
        """Handle stop button click"""
        # Video player controls are handled by the ft.Video component itself
        pass