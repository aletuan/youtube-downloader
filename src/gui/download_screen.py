#!/usr/bin/env python3
"""
YouTube Downloader - Download Screen

The main download interface where users can enter URLs, configure download settings,
and manage video downloads. Built with Flet Material Design components.
"""

import flet as ft
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import UI factory functions
from gui.ui_factory import (
    create_header_section,
    create_input_section,
    create_button_section,
    create_status_section,
    create_video_info_card,
    create_config_section,
    create_theme_button,
    create_footer,
    create_main_card
)

# Import event handlers
from gui.event_handlers import (
    handle_preview_click,
    handle_download_click,
    handle_play_click,
    handle_theme_toggle,
    handle_file_picker_result
)


def main(page: ft.Page):
    """Main download screen entry point"""
    
    # Configure page properties
    page.title = "YouTube Downloader"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.padding = 10
    
    # Configure window properties using window object
    page.window.width = 1000
    page.window.height = 800
    page.window.min_width = 1000
    page.window.min_height = 800
    page.window.resizable = True
    
    # Force update to ensure window size is applied
    page.update()
    
    # Create UI components using factory functions
    title, subtitle = create_header_section()
    url_input, output_dir_input = create_input_section()
    preview_button, download_button, play_button, button_row = create_button_section()
    status_text, progress_bar, progress_info = create_status_section()
    video_info_card = create_video_info_card()
    config_info = create_config_section()
    theme_button = create_theme_button()
    footer = create_footer()
    
    # Create FilePicker for fallback directory selection
    def get_directory_result(e: ft.FilePickerResultEvent):
        handle_file_picker_result(e, output_dir_input, status_text, page)
    
    file_picker = ft.FilePicker(on_result=get_directory_result)
    
    # Set up event handlers
    def on_preview_click(_):
        handle_preview_click(
            page, url_input, output_dir_input, status_text, 
            video_info_card, download_button, preview_button, play_button
        )
    
    def on_download_click(_):
        handle_download_click(
            page, url_input, output_dir_input, status_text, 
            progress_bar, progress_info, download_button, preview_button, play_button
        )
    
    def on_play_click(_):
        # Get video title from last download for better UX
        video_title = "Downloaded Video"  # Default title
        try:
            if url_input.value:
                from core.downloader import _get_video_info
                video_title, _ = _get_video_info(url_input.value.strip())
        except:
            pass
        handle_play_click(page, video_title)
    
    def on_theme_toggle(_):
        handle_theme_toggle(page)
    
    # Assign event handlers to buttons
    preview_button.on_click = on_preview_click
    download_button.on_click = on_download_click
    play_button.on_click = on_play_click
    theme_button.on_click = on_theme_toggle
    
    # Create main card with all components
    main_card_components = [
        title,
        subtitle,
        ft.Divider(height=12, color=ft.Colors.TRANSPARENT),
        url_input,
        ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
        output_dir_input,
        ft.Divider(height=12, color=ft.Colors.TRANSPARENT),
        button_row,
        ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
        video_info_card,
        ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
        progress_bar,
        progress_info,
        status_text,
        ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
        config_info,
    ]
    
    main_card = create_main_card(main_card_components)
    
    # Add view routing handler for navigation
    def on_route_change(route):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                    ft.Column(
                        [
                            ft.Row(
                                [theme_button],
                                alignment=ft.MainAxisAlignment.END
                            ),
                            main_card,
                            ft.Container(expand=True),  # Spacer to push footer to bottom
                            ft.Container(
                                content=footer,
                                margin=ft.margin.only(bottom=100)  # Move footer up by 100 pixels 
                            )
                        ],
                        expand=True,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10
                    )
                ]
            )
        )
        page.update()
    
    def on_view_pop(view):
        print(f"[DEBUG] View pop event triggered. Current views: {len(page.views)}")
        if len(page.views) > 1:
            page.views.pop()
            if page.views:
                top_view = page.views[-1]
                print(f"[DEBUG] Navigating to route: {top_view.route}")
                page.go(top_view.route)
            else:
                print("[DEBUG] No views remaining, going to root")
                page.go("/")
        else:
            print("[DEBUG] Only one view, staying on current route")
    
    page.on_route_change = on_route_change
    page.on_view_pop = on_view_pop
    
    # Add FilePicker to page overlay
    page.overlay.append(file_picker)
    
    # Initialize main view
    page.go("/")
    
    # Legacy approach removed in favor of view-based routing
    # This enables proper screen navigation for video player functionality


if __name__ == "__main__":
    # Run the YouTube Downloader Download Screen
    ft.app(target=main)