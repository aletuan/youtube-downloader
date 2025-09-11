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
        
        # Control buttons - removed since ft.Video has built-in controls
        # control_buttons = self._create_control_buttons()
        
        # Video info - removed for simplified UI
        # video_info = self._create_video_info()
        
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
            )
            
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
        
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
        """Create the video player component that loads local downloaded video files"""
        if not self.video_path or not os.path.exists(self.video_path):
            # Show placeholder if video not found
            error_message = "Video file not found" if self.video_path else "No video selected"
            if self.video_path:
                error_message += f"\nPath: {self.video_path}"
            
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=64, color=ft.Colors.RED_400),
                    ft.Text(error_message, color=ft.Colors.RED_600, text_align=ft.TextAlign.CENTER),
                    ft.Text("Please ensure the video was downloaded successfully", 
                           size=12, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                width=640,
                height=360,
                bgcolor=ft.Colors.GREY_100,
                border_radius=8,
                alignment=ft.alignment.center,
                padding=20
            )
        
        # Verify file is a video file
        video_extensions = ['.mp4', '.mkv', '.webm', '.avi', '.mov', '.m4v', '.flv']
        file_extension = Path(self.video_path).suffix.lower()
        
        if file_extension not in video_extensions:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.WARNING, size=64, color=ft.Colors.ORANGE_400),
                    ft.Text(f"Unsupported video format: {file_extension}", 
                           color=ft.Colors.ORANGE_600, text_align=ft.TextAlign.CENTER),
                    ft.Text(f"Supported formats: {', '.join(video_extensions)}", 
                           size=12, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                width=640,
                height=360,
                bgcolor=ft.Colors.GREY_100,
                border_radius=8,
                alignment=ft.alignment.center,
                padding=20
            )
        
        # Create video player with local file
        try:
            # Convert to absolute path for better compatibility
            absolute_path = os.path.abspath(self.video_path)
            
            video = ft.Video(
                width=640,
                height=360,
                playlist=[ft.VideoMedia(absolute_path)],
                playlist_mode=ft.PlaylistMode.NONE,
                fill_color=ft.Colors.BLACK,
                aspect_ratio=16/9,
                autoplay=True,  # Auto-play the downloaded video
                show_controls=True,
                playback_rate=1.0,
            )
            
            return video
            
        except Exception as e:
            # Handle any video player creation errors
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ERROR, size=64, color=ft.Colors.RED_400),
                    ft.Text(f"Error loading video: {str(e)}", 
                           color=ft.Colors.RED_600, text_align=ft.TextAlign.CENTER),
                    ft.Text(f"File: {self.video_path}", 
                           size=11, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                width=640,
                height=360,
                bgcolor=ft.Colors.GREY_100,
                border_radius=8,
                alignment=ft.alignment.center,
                padding=20
            )
    
    # Control buttons and video info removed for simplified UI
    # Video player now shows only: Header + Video Player
    
    def _on_back_click(self, e):
        """Handle back button click - navigate back to main downloader screen"""
        try:
            print(f"[DEBUG] Back button clicked. Current views: {len(self.page.views)}")
            
            # Remove current video player view from stack
            if len(self.page.views) > 1:
                print("[DEBUG] Popping video player view from stack")
                self.page.views.pop()
                print(f"[DEBUG] Views after pop: {len(self.page.views)}")
                self.page.update()
                print("[DEBUG] Page updated after view pop")
            else:
                print("[DEBUG] Only one view in stack, using page.go fallback")
                # Fallback: navigate to main route
                self.page.go("/")
        except Exception as e:
            print(f"[DEBUG] Error in back navigation: {e}")
            print("[DEBUG] Using fallback navigation")
            # Fallback navigation
            self.page.go("/")
    
    # Video control event handlers removed - ft.Video handles controls internally