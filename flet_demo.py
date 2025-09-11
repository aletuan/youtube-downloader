#!/usr/bin/env python3
import flet as ft

def main(page: ft.Page):
    """Main Flet application entry point"""
    
    # Configure page properties
    page.title = "Flet Demo - Hello World"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_width = 500
    page.window_height = 400
    page.window_resizable = False
    
    # Create UI components
    title = ft.Text(
        "Hello World - Flet Demo",
        size=32,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.BLUE_400
    )
    
    subtitle = ft.Text(
        "Modern Python GUI Framework",
        size=16,
        color=ft.Colors.GREY_600
    )
    
    # Input field for user interaction
    user_input = ft.TextField(
        label="Enter your name",
        width=300,
        border_radius=10
    )
    
    # Output text
    greeting_text = ft.Text(
        "",
        size=18,
        color=ft.Colors.GREEN_600
    )
    
    # Button click handler
    def on_button_click(e):
        name = user_input.value.strip()
        if name:
            greeting_text.value = f"Hello, {name}! Welcome to Flet! 🎉"
        else:
            greeting_text.value = "Please enter your name first! 😊"
        page.update()
    
    # Clear button handler
    def on_clear_click(e):
        user_input.value = ""
        greeting_text.value = ""
        page.update()
    
    # Create buttons
    hello_button = ft.ElevatedButton(
        "Say Hello",
        on_click=on_button_click,
        bgcolor=ft.Colors.BLUE_400,
        color=ft.Colors.WHITE,
        width=150
    )
    
    clear_button = ft.OutlinedButton(
        "Clear",
        on_click=on_clear_click,
        width=100
    )
    
    # Button row
    button_row = ft.Row(
        [hello_button, clear_button],
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
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    user_input,
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    button_row,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    greeting_text,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            padding=40,
            border_radius=15
        ),
        elevation=8
    )
    
    # Add components to page
    page.add(
        ft.Column(
            [
                ft.Row(
                    [theme_button],
                    alignment=ft.MainAxisAlignment.END
                ),
                main_card
            ],
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        )
    )

if __name__ == "__main__":
    # Run the Flet app
    ft.app(target=main)