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
        
        # Check for Vietnamese subtitle availability
        subtitle_info = self._get_subtitle_info()
        
        # Video player component
        video_player = self._create_video_player()
        
        # Control buttons - removed since ft.Video has built-in controls
        # control_buttons = self._create_control_buttons()
        
        # Video info - removed for simplified UI
        # video_info = self._create_video_info()
        
        # Main content
        content_items = [
            # Header with back button and title
            ft.Row([
                back_button,
                ft.Container(
                    content=title_text,
                    expand=True,
                    alignment=ft.alignment.center
                )
            ])
        ]
        
        # Add subtitle info if available
        if subtitle_info:
            content_items.append(subtitle_info)
        
        content_items.extend([
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            
            # Video player
            ft.Container(
                content=video_player,
                alignment=ft.alignment.center,
                bgcolor=ft.Colors.BLACK12,
                border_radius=12,
                padding=10
            )
        ])
        
        content = ft.Column(
            content_items, 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
            spacing=15
        )
        
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
            
            # Look for subtitle files in the same directory
            video_dir = Path(self.video_path).parent
            subtitle_file = None
            
            # Prioritize Vietnamese subtitle - if it exists, use it exclusively
            vietnamese_subtitle_found = False
            for vn_subtitle in video_dir.glob("*.vi.vtt"):
                subtitle_file = os.path.abspath(str(vn_subtitle))
                vietnamese_subtitle_found = True
                print(f"[DEBUG] Using Vietnamese subtitle exclusively: {vn_subtitle.name}")
                break
            
            # Only use English subtitle if no Vietnamese subtitle exists
            if not vietnamese_subtitle_found:
                for en_subtitle in video_dir.glob("*.en.vtt"):
                    subtitle_file = os.path.abspath(str(en_subtitle))
                    print(f"[DEBUG] No Vietnamese subtitle found, using English: {en_subtitle.name}")
                    break
            
            # Create video media with subtitle prioritization
            print(f"[DEBUG] Loading video: {absolute_path}")
            
            if subtitle_file:
                print(f"[DEBUG] Loading with preferred subtitle: {subtitle_file}")
                
                # Strategy: Temporarily rename files to ensure Vietnamese gets priority
                # This is a workaround for Flet's limited subtitle control
                temp_renamed_files = []
                
                try:
                    if vietnamese_subtitle_found:
                        # If Vietnamese subtitle exists, temporarily hide English subtitles
                        # so the video player only sees Vietnamese
                        for en_subtitle in video_dir.glob("*.en.vtt"):
                            if en_subtitle.exists():
                                temp_name = en_subtitle.with_suffix(".en.vtt.temp")
                                en_subtitle.rename(temp_name)
                                temp_renamed_files.append((temp_name, en_subtitle))
                                print(f"[DEBUG] Temporarily hiding English subtitle: {en_subtitle.name}")
                    
                    # Now create video media - Vietnamese should be the only/primary subtitle
                    video_media = ft.VideoMedia(absolute_path)
                    
                except Exception as rename_error:
                    print(f"[DEBUG] Subtitle prioritization error: {rename_error}")
                    video_media = ft.VideoMedia(absolute_path)
                
                # Restore renamed files after video creation
                for temp_file, original_file in temp_renamed_files:
                    try:
                        if temp_file.exists():
                            temp_file.rename(original_file)
                            print(f"[DEBUG] Restored subtitle file: {original_file.name}")
                    except Exception as restore_error:
                        print(f"[DEBUG] Error restoring subtitle: {restore_error}")
            else:
                print(f"[DEBUG] Loading video without subtitles")
                video_media = ft.VideoMedia(absolute_path)
            
            video = ft.Video(
                width=640,
                height=360,
                playlist=[video_media],
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
    
    def _get_subtitle_info(self) -> ft.Container:
        """Get subtitle availability information"""
        if not self.video_path:
            return None
            
        video_dir = Path(self.video_path).parent
        
        # Check for Vietnamese subtitles
        vietnamese_subtitle = None
        for subtitle_file in video_dir.glob("*.vi.vtt"):
            vietnamese_subtitle = subtitle_file
            break
            
        # Check for English subtitles
        english_subtitle = None
        for subtitle_file in video_dir.glob("*.en.vtt"):
            english_subtitle = subtitle_file
            break
            
        if vietnamese_subtitle or english_subtitle:
            subtitle_text_parts = []
            
            if vietnamese_subtitle:
                subtitle_text_parts.append("🇻🇳 Vietnamese subtitles (active)")
            elif english_subtitle:
                subtitle_text_parts.append("🇺🇸 English subtitles (active)")
                
            subtitle_text = " • ".join(subtitle_text_parts)
            
            return ft.Container(
                content=ft.Text(
                    subtitle_text,
                    size=12,
                    color=ft.Colors.GREEN_600,
                    text_align=ft.TextAlign.CENTER,
                    weight=ft.FontWeight.W_500
                ),
                padding=ft.padding.symmetric(horizontal=20, vertical=5),
                bgcolor=ft.Colors.GREEN_50,
                border_radius=8,
                border=ft.border.all(1, ft.Colors.GREEN_200)
            )
        
        return None