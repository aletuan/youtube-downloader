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
        """Create video information display for local downloaded video"""
        file_size = "Unknown"
        file_format = "Unknown"
        file_status = "❌ File not found"
        
        if self.video_path and os.path.exists(self.video_path):
            try:
                # Get file size
                size_bytes = os.path.getsize(self.video_path)
                if size_bytes < 1024*1024:
                    file_size = f"{size_bytes/1024:.1f} KB"
                elif size_bytes < 1024*1024*1024:
                    file_size = f"{size_bytes/(1024*1024):.1f} MB"
                else:
                    file_size = f"{size_bytes/(1024*1024*1024):.2f} GB"
                
                # Get file format
                file_format = Path(self.video_path).suffix.upper().replace('.', '') or "Unknown"
                file_status = "✅ Ready to play"
                
            except Exception as e:
                file_size = f"Error: {str(e)}"
                file_status = "❌ File access error"
        
        # Get folder name (video folder)
        folder_name = "Unknown"
        if self.video_path:
            folder_name = Path(self.video_path).parent.name
        
        info_content = ft.Column([
            ft.Text("Downloaded Video Information", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.BLUE_700),
            ft.Divider(height=1, color=ft.Colors.GREY_300),
            ft.Text(f"📁 Folder: {folder_name}", size=12),
            ft.Text(f"📄 File: {Path(self.video_path).name if self.video_path else 'Unknown'}", size=12),
            ft.Text(f"📊 Size: {file_size}", size=12),
            ft.Text(f"🎬 Format: {file_format}", size=12),
            ft.Text(f"Status: {file_status}", size=12, 
                   color=ft.Colors.GREEN_600 if "✅" in file_status else ft.Colors.RED_600),
            ft.Text(f"Local Path: {self.video_path or 'Unknown'}", 
                   size=10, color=ft.Colors.GREY_500, italic=True),
        ], spacing=6)
        
        return ft.Container(
            content=info_content,
            padding=15,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.BLUE_200)
        )
    
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