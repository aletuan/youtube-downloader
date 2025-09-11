#!/usr/bin/env python3
"""
Simple test script to verify Flet installation and basic functionality
"""

def test_flet_import():
    """Test that Flet can be imported successfully"""
    try:
        import flet as ft
        print("PASS: Flet imported successfully")
        print(f"INFO: Flet module available: {ft.__name__}")
        # Get version from package metadata
        try:
            import importlib.metadata
            version = importlib.metadata.version('flet')
            print(f"INFO: Flet version: {version}")
        except:
            print("INFO: Flet version: Available (version detection not supported)")
        return True
    except ImportError as e:
        print(f"FAIL: Failed to import Flet: {e}")
        return False

def test_flet_components():
    """Test that basic Flet components can be created"""
    try:
        import flet as ft
        
        # Test basic components
        text = ft.Text("Hello Flet", color=ft.Colors.BLUE)
        button = ft.ElevatedButton("Test Button")
        textfield = ft.TextField(label="Test Input")
        
        print("PASS: Basic Flet components created successfully")
        print(f"   - Text component: {type(text).__name__}")
        print(f"   - Button component: {type(button).__name__}")
        print(f"   - TextField component: {type(textfield).__name__}")
        print("PASS: Flet API (Colors) working correctly")
        return True
    except Exception as e:
        print(f"FAIL: Failed to create Flet components: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Flet Framework Setup...")
    print("=" * 40)
    
    # Run tests
    import_ok = test_flet_import()
    components_ok = test_flet_components()
    
    print("=" * 40)
    if import_ok and components_ok:
        print("SUCCESS: All tests passed! Flet is ready to use.")
        print("INFO: You can now run: python flet_demo.py")
        return True
    else:
        print("ERROR: Some tests failed. Please check the installation.")
        return False

if __name__ == "__main__":
    main()