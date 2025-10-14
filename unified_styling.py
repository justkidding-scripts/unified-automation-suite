#!/usr/bin/env python3
"""
Unified Styling System
======================
Consistent professional styling across all integrated tools.
Provides themes, color schemes, and UI configurations.

Author: Enhanced by AI Assistant
Version: 3.0.0
"""

from tkinter import ttk
import json
import os
from pathlib import Path
from typing import Dict, Any

class UnifiedThemeManager:
    """Manages unified themes across all tools"""
    
    def __init__(self):
        self.current_theme = "dark_professional"
        self.themes = self._define_themes()
        self.fonts = self._define_fonts()
        
    def _define_themes(self) -> Dict[str, Dict[str, Any]]:
        """Define all available themes"""
        return {
            "dark_professional": {
                "name": "Dark Professional",
                "colors": {
                    # Primary backgrounds
                    "bg_primary": "#1e1e1e",
                    "bg_secondary": "#2b2b2b", 
                    "bg_tertiary": "#404040",
                    "bg_input": "#404040",
                    "bg_hover": "#505050",
                    "bg_pressed": "#606060",
                    "bg_selected": "#505050",
                    
                    # Foreground colors
                    "fg_primary": "#ffffff",
                    "fg_secondary": "#cccccc",
                    "fg_muted": "#999999",
                    
                    # Accent colors
                    "accent_primary": "#00ff88",
                    "accent_secondary": "#0078d7",
                    "accent_tertiary": "#ff6b6b",
                    
                    # Status colors
                    "success": "#00ff88",
                    "warning": "#ffaa00", 
                    "error": "#ff4444",
                    "info": "#0078d7",
                    
                    # Borders and separators
                    "border": "#555555",
                    "separator": "#333333",
                    
                    # Special elements
                    "highlight": "#0078d7",
                    "selection": "#0078d7",
                    "cursor": "#ffffff"
                },
                "metrics": {
                    "border_width": 1,
                    "padding_small": 5,
                    "padding_medium": 10,
                    "padding_large": 20,
                    "corner_radius": 4
                }
            },
            
            "light_professional": {
                "name": "Light Professional",
                "colors": {
                    "bg_primary": "#f8f9fa",
                    "bg_secondary": "#ffffff",
                    "bg_tertiary": "#e9ecef",
                    "bg_input": "#ffffff",
                    "bg_hover": "#f8f9fa",
                    "bg_pressed": "#dee2e6",
                    "bg_selected": "#e3f2fd",
                    
                    "fg_primary": "#212529",
                    "fg_secondary": "#495057",
                    "fg_muted": "#6c757d",
                    
                    "accent_primary": "#007bff",
                    "accent_secondary": "#28a745",
                    "accent_tertiary": "#dc3545",
                    
                    "success": "#28a745",
                    "warning": "#ffc107",
                    "error": "#dc3545",
                    "info": "#007bff",
                    
                    "border": "#dee2e6",
                    "separator": "#e9ecef",
                    
                    "highlight": "#007bff",
                    "selection": "#cce5ff",
                    "cursor": "#000000"
                },
                "metrics": {
                    "border_width": 1,
                    "padding_small": 5,
                    "padding_medium": 10,
                    "padding_large": 20,
                    "corner_radius": 4
                }
            },
            
            "terminal_green": {
                "name": "Terminal Green",
                "colors": {
                    "bg_primary": "#0c0c0c",
                    "bg_secondary": "#1a1a1a",
                    "bg_tertiary": "#2d2d2d",
                    "bg_input": "#1a1a1a",
                    "bg_hover": "#2d2d2d",
                    "bg_pressed": "#404040",
                    "bg_selected": "#2d4a2d",
                    
                    "fg_primary": "#00ff00",
                    "fg_secondary": "#90ee90",
                    "fg_muted": "#669966",
                    
                    "accent_primary": "#00ff00",
                    "accent_secondary": "#ffff00",
                    "accent_tertiary": "#ff6600",
                    
                    "success": "#00ff00",
                    "warning": "#ffff00",
                    "error": "#ff0000",
                    "info": "#00ffff",
                    
                    "border": "#333333",
                    "separator": "#1a1a1a",
                    
                    "highlight": "#00ff00",
                    "selection": "#004400",
                    "cursor": "#00ff00"
                },
                "metrics": {
                    "border_width": 1,
                    "padding_small": 5,
                    "padding_medium": 10,
                    "padding_large": 15,
                    "corner_radius": 2
                }
            }
        }
    
    def _define_fonts(self) -> Dict[str, Dict[str, Any]]:
        """Define font configurations"""
        return {
            "default": {
                "family": "Consolas",
                "size": 10,
                "weight": "normal"
            },
            "title": {
                "family": "Consolas",
                "size": 20,
                "weight": "bold"
            },
            "subtitle": {
                "family": "Consolas", 
                "size": 12,
                "weight": "normal"
            },
            "heading": {
                "family": "Consolas",
                "size": 14,
                "weight": "bold"
            },
            "button": {
                "family": "Consolas",
                "size": 10,
                "weight": "normal"
            },
            "button_large": {
                "family": "Consolas",
                "size": 12,
                "weight": "bold"
            },
            "code": {
                "family": "Consolas",
                "size": 9,
                "weight": "normal"
            },
            "small": {
                "family": "Consolas",
                "size": 8,
                "weight": "normal"
            }
        }
    
    def get_theme(self, theme_name: str = None) -> Dict[str, Any]:
        """Get theme configuration"""
        if theme_name is None:
            theme_name = self.current_theme
        
        return self.themes.get(theme_name, self.themes["dark_professional"])
    
    def get_font(self, font_name: str) -> tuple:
        """Get font tuple for Tkinter"""
        font_config = self.fonts.get(font_name, self.fonts["default"])
        return (font_config["family"], font_config["size"], font_config["weight"])
    
    def set_theme(self, theme_name: str):
        """Set the current theme"""
        if theme_name in self.themes:
            self.current_theme = theme_name
    
    def get_available_themes(self) -> List[str]:
        """Get list of available theme names"""
        return list(self.themes.keys())

class UnifiedStyleConfigurator:
    """Configures TTK styles with unified themes"""
    
    def __init__(self, theme_manager: UnifiedThemeManager):
        self.theme_manager = theme_manager
        self.style = None
    
    def configure_style(self, root, theme_name: str = None):
        """Configure TTK styles with specified theme"""
        self.style = ttk.Style(root)
        self.style.theme_use('clam')
        
        theme = self.theme_manager.get_theme(theme_name)
        colors = theme["colors"]
        metrics = theme["metrics"]
        
        # Configure basic widget styles
        self._configure_labels(colors)
        self._configure_frames(colors)
        self._configure_buttons(colors, metrics)
        self._configure_entries(colors)
        self._configure_notebooks(colors, metrics)
        self._configure_treeviews(colors)
        self._configure_progressbars(colors)
        self._configure_checkbuttons(colors)
        self._configure_scales(colors)
        self._configure_spinboxes(colors)
        
        # Configure custom styles
        self._configure_custom_styles(colors, metrics)
        
        # Set root window options for text selection
        root.option_add('*Text.selectBackground', colors["selection"])
        root.option_add('*Text.selectForeground', colors["fg_primary"])
        root.option_add('*Entry.selectBackground', colors["selection"])
        root.option_add('*Entry.selectForeground', colors["fg_primary"])
    
    def _configure_labels(self, colors):
        """Configure label styles"""
        self.style.configure('TLabel', 
                           background=colors["bg_primary"], 
                           foreground=colors["fg_primary"])
    
    def _configure_frames(self, colors):
        """Configure frame styles"""
        self.style.configure('TFrame', background=colors["bg_primary"])
        self.style.configure('TLabelFrame', 
                           background=colors["bg_primary"], 
                           foreground=colors["fg_primary"])
        self.style.configure('TLabelFrame.Label', 
                           background=colors["bg_primary"], 
                           foreground=colors["fg_primary"])
    
    def _configure_buttons(self, colors, metrics):
        """Configure button styles"""
        self.style.configure('TButton',
                           background=colors["bg_tertiary"],
                           foreground=colors["fg_primary"],
                           borderwidth=metrics["border_width"],
                           padding=metrics["padding_small"])
        
        self.style.map('TButton',
                      background=[('active', colors["bg_hover"]), 
                                ('pressed', colors["bg_pressed"])])
    
    def _configure_entries(self, colors):
        """Configure entry styles"""
        self.style.configure('TEntry',
                           fieldbackground=colors["bg_input"],
                           foreground=colors["fg_primary"],
                           insertcolor=colors["cursor"],
                           bordercolor=colors["border"])
    
    def _configure_notebooks(self, colors, metrics):
        """Configure notebook styles"""
        self.style.configure('TNotebook',
                           background=colors["bg_primary"],
                           tabposition='n')
        
        self.style.configure('TNotebook.Tab',
                           background=colors["bg_tertiary"],
                           foreground=colors["fg_primary"],
                           padding=[metrics["padding_medium"], metrics["padding_small"]])
        
        self.style.map('TNotebook.Tab',
                      background=[('selected', colors["bg_selected"]), 
                                ('active', colors["bg_hover"])])
    
    def _configure_treeviews(self, colors):
        """Configure treeview styles"""
        self.style.configure('Treeview',
                           background=colors["bg_input"],
                           foreground=colors["fg_primary"],
                           fieldbackground=colors["bg_input"])
        
        self.style.configure('Treeview.Heading',
                           background=colors["bg_selected"],
                           foreground=colors["fg_primary"])
    
    def _configure_progressbars(self, colors):
        """Configure progressbar styles"""
        self.style.configure('TProgressbar',
                           background=colors["accent_primary"],
                           troughcolor=colors["bg_tertiary"])
    
    def _configure_checkbuttons(self, colors):
        """Configure checkbutton styles"""
        self.style.configure('TCheckbutton',
                           background=colors["bg_primary"],
                           foreground=colors["fg_primary"])
    
    def _configure_scales(self, colors):
        """Configure scale styles"""
        self.style.configure('TScale',
                           background=colors["bg_primary"],
                           troughcolor=colors["bg_tertiary"])
    
    def _configure_spinboxes(self, colors):
        """Configure spinbox styles"""
        self.style.configure('TSpinbox',
                           fieldbackground=colors["bg_input"],
                           foreground=colors["fg_primary"])
    
    def _configure_custom_styles(self, colors, metrics):
        """Configure custom widget styles"""
        
        # Title styles
        self.style.configure('Title.TLabel',
                           font=self.theme_manager.get_font("title"),
                           background=colors["bg_primary"],
                           foreground=colors["accent_primary"])
        
        # Subtitle styles
        self.style.configure('Subtitle.TLabel',
                           font=self.theme_manager.get_font("subtitle"),
                           background=colors["bg_primary"],
                           foreground=colors["fg_secondary"])
        
        # Heading styles
        self.style.configure('Heading.TLabel',
                           font=self.theme_manager.get_font("heading"),
                           background=colors["bg_primary"],
                           foreground=colors["fg_primary"])
        
        # Status styles
        self.style.configure('Status.TLabel',
                           font=self.theme_manager.get_font("default"),
                           background=colors["bg_primary"])
        
        self.style.configure('Success.TLabel',
                           foreground=colors["success"])
        
        self.style.configure('Warning.TLabel',
                           foreground=colors["warning"])
        
        self.style.configure('Error.TLabel',
                           foreground=colors["error"])
        
        self.style.configure('Info.TLabel',
                           foreground=colors["info"])
        
        # Button variations
        self.style.configure('Launch.TButton',
                           font=self.theme_manager.get_font("button_large"),
                           background=colors["success"],
                           foreground=colors["bg_primary"])
        
        self.style.configure('Stop.TButton',
                           font=self.theme_manager.get_font("button_large"),
                           background=colors["error"],
                           foreground=colors["fg_primary"])
        
        self.style.configure('Premium.TButton',
                           font=self.theme_manager.get_font("button"),
                           background=colors["accent_primary"],
                           foreground=colors["bg_primary"])
        
        # Code/terminal styles
        self.style.configure('Code.TLabel',
                           font=self.theme_manager.get_font("code"),
                           background=colors["bg_secondary"],
                           foreground=colors["fg_primary"])

class UnifiedColorScheme:
    """Provides color scheme utilities"""
    
    @staticmethod
    def get_status_color(status: str, theme_name: str = "dark_professional") -> str:
        """Get color for status indicators"""
        theme_manager = UnifiedThemeManager()
        colors = theme_manager.get_theme(theme_name)["colors"]
        
        status_map = {
            "success": colors["success"],
            "warning": colors["warning"], 
            "error": colors["error"],
            "info": colors["info"],
            "active": colors["accent_primary"],
            "inactive": colors["fg_muted"],
            "running": colors["success"],
            "stopped": colors["error"],
            "pending": colors["warning"]
        }
        
        return status_map.get(status.lower(), colors["fg_primary"])
    
    @staticmethod
    def get_gradient_colors(start_color: str, end_color: str, steps: int) -> List[str]:
        """Generate gradient color steps"""
        # Simple gradient generation - could be enhanced
        return [start_color] * steps  # Placeholder implementation

def setup_unified_styling(root, theme_name: str = "dark_professional"):
    """Convenience function to set up unified styling"""
    theme_manager = UnifiedThemeManager()
    configurator = UnifiedStyleConfigurator(theme_manager)
    configurator.configure_style(root, theme_name)
    
    return theme_manager, configurator

def apply_widget_styling(widget, style_name: str, theme_manager: UnifiedThemeManager):
    """Apply styling to individual widgets"""
    theme = theme_manager.get_theme()
    colors = theme["colors"]
    
    if hasattr(widget, 'configure'):
        if style_name == "code_text":
            widget.configure(
                bg=colors["bg_secondary"],
                fg=colors["fg_primary"],
                font=theme_manager.get_font("code"),
                insertbackground=colors["cursor"],
                selectbackground=colors["selection"],
                selectforeground=colors["fg_primary"]
            )
        
        elif style_name == "log_text":
            widget.configure(
                bg=colors["bg_secondary"],
                fg=colors["fg_primary"],
                font=theme_manager.get_font("code"),
                insertbackground=colors["cursor"],
                selectbackground=colors["selection"],
                selectforeground=colors["fg_primary"],
                wrap="word"
            )
        
        elif style_name == "status_text":
            widget.configure(
                bg=colors["bg_input"],
                fg=colors["fg_secondary"],
                font=theme_manager.get_font("default"),
                state="readonly"
            )

# Configuration management
class StylePreferences:
    """Manages style preferences and persistence"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path.home() / '.config' / 'unified_automation' / 'styles.json'
        
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.preferences = self.load_preferences()
    
    def load_preferences(self) -> Dict[str, Any]:
        """Load style preferences from file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return self.get_default_preferences()
        except Exception:
            return self.get_default_preferences()
    
    def save_preferences(self):
        """Save style preferences to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.preferences, f, indent=2)
        except Exception as e:
            print(f"Failed to save style preferences: {e}")
    
    def get_default_preferences(self) -> Dict[str, Any]:
        """Get default style preferences"""
        return {
            "theme": "dark_professional",
            "font_scale": 1.0,
            "high_contrast": False,
            "custom_colors": {},
            "per_tool_themes": {
                "telegram": "dark_professional",
                "sms_marketplace": "dark_professional", 
                "launcher": "dark_professional"
            }
        }
    
    def get_theme_for_tool(self, tool_name: str) -> str:
        """Get theme preference for specific tool"""
        return self.preferences.get("per_tool_themes", {}).get(
            tool_name, self.preferences.get("theme", "dark_professional")
        )
    
    def set_theme_for_tool(self, tool_name: str, theme_name: str):
        """Set theme preference for specific tool"""
        if "per_tool_themes" not in self.preferences:
            self.preferences["per_tool_themes"] = {}
        
        self.preferences["per_tool_themes"][tool_name] = theme_name
        self.save_preferences()

# Global instances
theme_manager = UnifiedThemeManager()
style_preferences = StylePreferences()