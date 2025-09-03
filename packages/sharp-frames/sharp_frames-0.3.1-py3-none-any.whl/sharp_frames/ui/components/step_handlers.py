"""
Step handlers for TwoPhaseConfigurationForm.
These handlers follow the interface expected by the v2 configuration form.
"""

import os
from typing import Dict, Any, Optional
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Label, Input, Select, RadioSet, RadioButton, Checkbox, Static

from ..constants import UIElementIds, InputTypes
from .validators import (
    IntRangeValidator, 
    VideoFileValidator, 
    VideoDirectoryValidator, 
    ImageDirectoryValidator,
    OutputDirectoryValidator
)


class StepHandler:
    """Base class for two-phase configuration step handlers."""
    
    def __init__(self):
        pass
    
    def get_title(self) -> str:
        """Get the step title."""
        raise NotImplementedError
    
    def get_description(self) -> str:
        """Get the step description."""
        raise NotImplementedError
    
    def render(self, screen, container: Container) -> None:
        """Render the step content into the container."""
        raise NotImplementedError
    
    def validate(self, screen) -> bool:
        """Validate the current step."""
        return True
    
    def get_data(self, screen) -> Dict[str, Any]:
        """Get data from the step."""
        return {}
    
    def set_data(self, screen, data: Any) -> None:
        """Set data for the step."""
        pass
    
    def get_help_text(self) -> str:
        """Get help text for this step."""
        return ""


class InputTypeStepHandler(StepHandler):
    """Handler for input type selection step."""
    
    def get_title(self) -> str:
        return "Input Type Selection"
    
    def get_description(self) -> str:
        return "Choose what type of input you want to process"
    
    def render(self, screen, container: Container) -> None:
        """Render the input type selection step."""
        container.mount(Label("What type of input do you want to process?", classes="question"))
        
        # Create radio buttons for input types
        container.mount(
            RadioSet(
                RadioButton("Single video file", id="video", value=True),
                RadioButton("Directory of video files", id="video_directory"),
                RadioButton("Directory of images", id="image_directory"),
                id="input-type-selection"
            )
        )
    
    def validate(self, screen) -> bool:
        """Validate input type selection."""
        try:
            radio_set = screen.query_one("#input-type-selection", RadioSet)
            return radio_set.pressed_index is not None
        except:
            return False
    
    def get_data(self, screen) -> Dict[str, Any]:
        """Get selected input type."""
        try:
            radio_set = screen.query_one("#input-type-selection", RadioSet)
            if radio_set.pressed_index is not None:
                # Map the pressed index to the input type
                # Use "directory" for image directories to match SharpFrames expectations
                input_types = ["video", "video_directory", "directory"]
                return {"input_type": input_types[radio_set.pressed_index]}
        except Exception as e:
            screen.app.log.error(f"Error getting input type data: {e}")
        return {}
    
    def set_data(self, screen, data: Any) -> None:
        """Set input type selection."""
        if not data:
            return
        try:
            input_type = data.get("input_type", "video")
            radio_set = screen.query_one("#input-type-selection", RadioSet)
            # Map the input type to the index
            # Handle both "image_directory" and "directory" for compatibility
            if input_type == "directory":
                input_type = "image_directory"  # Convert for display
            input_types = ["video", "video_directory", "image_directory"]
            if input_type in input_types:
                radio_set.pressed_index = input_types.index(input_type)
        except Exception as e:
            screen.app.log.error(f"Error setting input type data: {e}")


class InputPathStepHandler(StepHandler):
    """Handler for input path selection step."""
    
    def get_title(self) -> str:
        return "Input Path"
    
    def get_description(self) -> str:
        return "Enter the path to your input file or directory"
    
    def render(self, screen, container: Container) -> None:
        """Render the input path step."""
        input_type = screen.config_data.get("input_type", "video")
        
        if input_type == "video":
            container.mount(Label("Enter the path to your video file:", classes="question"))
            container.mount(Static("Tip: You can drag and drop a video file here", classes="hint"))
        elif input_type == "video_directory":
            container.mount(Label("Enter the path to your video directory:", classes="question"))
            container.mount(Static("Tip: You can drag and drop a directory here", classes="hint"))
        else:  # directory (image directory)
            container.mount(Label("Enter the path to your image directory:", classes="question"))
            container.mount(Static("Tip: You can drag and drop a directory here", classes="hint"))
        
        container.mount(Input(placeholder="Path to input...", id="input-path"))
    
    def validate(self, screen) -> bool:
        """Validate input path."""
        try:
            input_widget = screen.query_one("#input-path", Input)
            path = input_widget.value.strip()
            
            if not path:
                screen.query_one("#step-description").update("Please enter an input path")
                return False
            
            # Expand user path
            expanded_path = os.path.expanduser(path)
            
            if not os.path.exists(expanded_path):
                screen.query_one("#step-description").update("Path does not exist")
                return False
            
            input_type = screen.config_data.get("input_type", "video")
            
            if input_type == "video":
                if not os.path.isfile(expanded_path):
                    screen.query_one("#step-description").update("Path must be a video file")
                    return False
                # Could add video format validation here
            else:  # directory types
                if not os.path.isdir(expanded_path):
                    screen.query_one("#step-description").update("Path must be a directory")
                    return False
            
            return True
        except Exception as e:
            screen.query_one("#step-description").update(f"Validation error: {str(e)}")
            return False
    
    def get_data(self, screen) -> Dict[str, Any]:
        """Get input path data."""
        try:
            input_widget = screen.query_one("#input-path", Input)
            path = input_widget.value.strip()
            return {"input_path": os.path.expanduser(path)}
        except:
            return {}
    
    def set_data(self, screen, data: Any) -> None:
        """Set input path."""
        if not data:
            return
        try:
            input_path = data.get("input_path", "")
            input_widget = screen.query_one("#input-path", Input)
            input_widget.value = input_path
        except:
            pass


class OutputDirStepHandler(StepHandler):
    """Handler for output directory selection step."""
    
    def get_title(self) -> str:
        return "Output Directory"
    
    def get_description(self) -> str:
        return "Choose where to save the selected frames"
    
    def render(self, screen, container: Container) -> None:
        """Render the output directory step."""
        container.mount(Label("Enter the output directory for selected frames:", classes="question"))
        container.mount(Static("Tip: Directory will be created if it doesn't exist", classes="hint"))
        container.mount(Input(placeholder="Path to output directory...", id="output-dir-input"))
    
    def validate(self, screen) -> bool:
        """Validate output directory."""
        try:
            input_widget = screen.query_one("#output-dir-input", Input)
            path = input_widget.value.strip()
            
            if not path:
                screen.query_one("#step-description").update("Please enter an output directory")
                return False
            
            # Expand user path
            expanded_path = os.path.expanduser(path)
            
            # Check if parent directory exists and is writable
            parent_dir = os.path.dirname(expanded_path)
            if parent_dir and not os.path.exists(parent_dir):
                screen.query_one("#step-description").update("Parent directory does not exist")
                return False
            
            if parent_dir and not os.access(parent_dir, os.W_OK):
                screen.query_one("#step-description").update("Cannot write to parent directory")
                return False
            
            return True
        except Exception as e:
            screen.query_one("#step-description").update(f"Validation error: {str(e)}")
            return False
    
    def get_data(self, screen) -> Dict[str, Any]:
        """Get output directory data."""
        try:
            input_widget = screen.query_one("#output-dir-input", Input)
            path = input_widget.value.strip()
            return {"output_dir": os.path.expanduser(path)}
        except:
            return {}
    
    def set_data(self, screen, data: Any) -> None:
        """Set output directory."""
        if not data:
            return
        try:
            output_dir = data.get("output_dir", "")
            input_widget = screen.query_one("#output-dir", Input)
            input_widget.value = output_dir
        except:
            pass


class FpsStepHandler(StepHandler):
    """Handler for FPS selection step."""
    
    def get_title(self) -> str:
        return "Frame Extraction Rate"
    
    def get_description(self) -> str:
        return "Set the frame extraction rate (frames per second)"
    
    def render(self, screen, container: Container) -> None:
        """Render the FPS step."""
        container.mount(Label("At what rate should frames be extracted?", classes="question"))
        container.mount(Static("Higher values extract more frames but take longer to process", classes="hint"))
        
        # Add line break and better layout
        container.mount(Static(""))  # Line break
        container.mount(Label("FPS (frames per second):", classes="field-label"))
        container.mount(Input(value="10", placeholder="10", id="fps-input", classes="field-input"))
    
    def validate(self, screen) -> bool:
        """Validate FPS value."""
        try:
            input_widget = screen.query_one("#fps-input", Input)
            fps_str = input_widget.value.strip()
            
            if not fps_str:
                screen.query_one("#step-description").update("Please enter an FPS value")
                return False
            
            fps = float(fps_str)
            if fps <= 0:
                screen.query_one("#step-description").update("FPS must be greater than 0")
                return False
            
            if fps > 60:
                screen.query_one("#step-description").update("FPS should not exceed 60")
                return False
            
            return True
        except ValueError:
            screen.query_one("#step-description").update("FPS must be a valid number")
            return False
        except Exception as e:
            screen.query_one("#step-description").update(f"Validation error: {str(e)}")
            return False
    
    def get_data(self, screen) -> Dict[str, Any]:
        """Get FPS data."""
        try:
            input_widget = screen.query_one("#fps-input", Input)
            fps = float(input_widget.value.strip())
            return {"fps": fps}
        except:
            return {"fps": 10}  # Default value
    
    def set_data(self, screen, data: Any) -> None:
        """Set FPS value."""
        if not data:
            return
        try:
            fps = data.get("fps", 10)
            input_widget = screen.query_one("#fps-input", Input)
            input_widget.value = str(fps)
        except:
            pass


class OutputFormatStepHandler(StepHandler):
    """Handler for output format selection step."""
    
    def get_title(self) -> str:
        return "Output Format"
    
    def get_description(self) -> str:
        return "Choose the image format for saved frames"
    
    def render(self, screen, container: Container) -> None:
        """Render the output format step."""
        container.mount(Label("What image format should be used for saved frames?", classes="question"))
        container.mount(Static("Choose the best format for your needs", classes="hint"))
        
        # Add line break and better layout
        container.mount(Static(""))  # Line break
        container.mount(Label("Image format:", classes="field-label"))
        
        formats = [
            ("jpg", "JPEG (smaller file size, good quality)"),
            ("png", "PNG (larger file size, lossless quality)")
        ]
        
        options = [(desc, fmt) for fmt, desc in formats]
        container.mount(Select(options, value="jpg", id="format-select", classes="field-select"))
    
    def validate(self, screen) -> bool:
        """Validate output format."""
        return True  # Select widget always has a valid value
    
    def get_data(self, screen) -> Dict[str, Any]:
        """Get output format data."""
        try:
            select_widget = screen.query_one("#format-select", Select)
            return {"output_format": select_widget.value}
        except:
            return {"output_format": "jpg"}  # Default value
    
    def set_data(self, screen, data: Any) -> None:
        """Set output format."""
        if not data:
            return
        try:
            format_value = data.get("output_format", "jpg")
            select_widget = screen.query_one("#format-select", Select)
            select_widget.value = format_value
        except:
            pass


class WidthStepHandler(StepHandler):
    """Handler for width/resize selection step."""
    
    def get_title(self) -> str:
        return "Image Width"
    
    def get_description(self) -> str:
        return "Set output image width (0 for original size)"
    
    def render(self, screen, container: Container) -> None:
        """Render the width step."""
        container.mount(Label("What should be the width of output images?", classes="question"))
        container.mount(Static("Enter 0 to keep original size, or specify width in pixels", classes="hint"))
        
        # Add line break and better layout
        container.mount(Static(""))  # Line break
        container.mount(Label("Width (in pixels):", classes="field-label"))
        container.mount(Input(value="0", placeholder="0", id="width-input", classes="field-input"))
    
    def validate(self, screen) -> bool:
        """Validate width value."""
        try:
            input_widget = screen.query_one("#width-input", Input)
            width_str = input_widget.value.strip()
            
            if not width_str:
                screen.query_one("#step-description").update("Please enter a width value")
                return False
            
            width = int(width_str)
            if width < 0:
                screen.query_one("#step-description").update("Width cannot be negative")
                return False
            
            if width > 0 and width < 100:
                screen.query_one("#step-description").update("Width should be at least 100 pixels if not 0")
                return False
            
            return True
        except ValueError:
            screen.query_one("#step-description").update("Width must be a valid integer")
            return False
        except Exception as e:
            screen.query_one("#step-description").update(f"Validation error: {str(e)}")
            return False
    
    def get_data(self, screen) -> Dict[str, Any]:
        """Get width data."""
        try:
            input_widget = screen.query_one("#width-input", Input)
            width = int(input_widget.value.strip())
            return {"width": width}
        except:
            return {"width": 0}  # Default value
    
    def set_data(self, screen, data: Any) -> None:
        """Set width value."""
        if not data:
            return
        try:
            width = data.get("width", 0)
            input_widget = screen.query_one("#width-input", Input)
            input_widget.value = str(width)
        except:
            pass


class ForceOverwriteStepHandler(StepHandler):
    """Handler for force overwrite option step."""
    
    def get_title(self) -> str:
        return "Overwrite Settings"
    
    def get_description(self) -> str:
        return "Choose whether to overwrite existing files"
    
    def render(self, screen, container: Container) -> None:
        """Render the force overwrite step."""
        container.mount(Label("How should existing files be handled?", classes="question"))
        container.mount(Static("Choose whether to skip confirmation prompts", classes="hint"))
        
        # Add line break and better layout
        container.mount(Static(""))  # Line break
        container.mount(Label("File handling:", classes="field-label"))
        container.mount(Checkbox("Force overwrite existing files without asking", id="force-overwrite", classes="field-checkbox"))
        container.mount(Static(""))  # Line break
        container.mount(Static("If unchecked, you'll be prompted before overwriting files", classes="hint"))
    
    def validate(self, screen) -> bool:
        """Validate force overwrite setting."""
        return True  # Checkbox always has a valid value
    
    def get_data(self, screen) -> Dict[str, Any]:
        """Get force overwrite data."""
        try:
            checkbox = screen.query_one("#force-overwrite", Checkbox)
            return {"force_overwrite": checkbox.value}
        except:
            return {"force_overwrite": False}  # Default value
    
    def set_data(self, screen, data: Any) -> None:
        """Set force overwrite setting."""
        if not data:
            return
        try:
            force_overwrite = data.get("force_overwrite", False)
            checkbox = screen.query_one("#force-overwrite", Checkbox)
            checkbox.value = force_overwrite
        except:
            pass


class ConfirmStepHandler(StepHandler):
    """Handler for configuration confirmation step."""
    
    def get_title(self) -> str:
        return "Configuration Summary"
    
    def get_description(self) -> str:
        return "Review your configuration before starting processing"
    
    def render(self, screen, container: Container) -> None:
        """Render the confirmation step."""
        container.mount(Label("Please review your configuration:", classes="question"))
        container.mount(Static(""))  # Line break
        
        # Show configuration summary
        config = screen.config_data
        
        # Build summary items with better formatting
        summary_items = []
        
        # Input configuration
        summary_items.append(Label("Input Configuration", classes="summary-section-title"))
        summary_items.append(Static(f"  Type: {config.get('input_type', 'Unknown')}"))
        summary_items.append(Static(f"  Path: {config.get('input_path', 'Not set')}"))
        summary_items.append(Static(""))  # Section break
        
        # Output configuration
        summary_items.append(Label("Output Configuration", classes="summary-section-title"))
        summary_items.append(Static(f"  Directory: {config.get('output_dir', 'Not set')}"))
        summary_items.append(Static(f"  Format: {config.get('output_format', 'jpg').upper()}"))
        
        width = config.get('width', 0)
        if width == 0:
            summary_items.append(Static("  Width: Original size"))
        else:
            summary_items.append(Static(f"  Width: {width} pixels"))
        summary_items.append(Static(""))  # Section break
        
        # Processing configuration
        summary_items.append(Label("Processing Configuration", classes="summary-section-title"))
        
        # Show FPS only for video inputs
        input_type = config.get('input_type', '')
        if input_type in ['video', 'video_directory']:
            summary_items.append(Static(f"  Frame Rate: {config.get('fps', 10)} FPS"))
        
        overwrite = config.get('force_overwrite', False)
        summary_items.append(Static(f"  Overwrite Files: {'Yes' if overwrite else 'No'}"))
        
        container.mount(Vertical(*summary_items, classes="summary"))
        container.mount(Static(""))  # Line break
        container.mount(Static("Click 'Start Processing' to begin frame extraction and analysis.", classes="hint"))
    
    def validate(self, screen) -> bool:
        """Validate complete configuration."""
        return True  # Final validation happens in the form itself
    
    def get_data(self, screen) -> Dict[str, Any]:
        """Get confirmation data."""
        return {}  # No additional data from confirmation step
    
    def set_data(self, screen, data: Any) -> None:
        """Set confirmation data."""
        pass  # Nothing to set for confirmation step


class ValidationHelpers:
    """Helper class for validation functions."""
    
    @staticmethod
    def validate_path(path: str, must_exist: bool = True) -> bool:
        """Validate a file path."""
        if not path:
            return False
        
        expanded_path = os.path.expanduser(path)
        
        if must_exist and not os.path.exists(expanded_path):
            return False
        
        return True
    
    @staticmethod
    def validate_fps(fps_str: str) -> tuple[bool, Optional[float]]:
        """Validate FPS value."""
        try:
            fps = float(fps_str)
            if fps <= 0 or fps > 60:
                return False, None
            return True, fps
        except ValueError:
            return False, None
    
    @staticmethod
    def validate_width(width_str: str) -> tuple[bool, Optional[int]]:
        """Validate width value."""
        try:
            width = int(width_str)
            if width < 0:
                return False, None
            if width > 0 and width < 100:
                return False, None
            return True, width
        except ValueError:
            return False, None