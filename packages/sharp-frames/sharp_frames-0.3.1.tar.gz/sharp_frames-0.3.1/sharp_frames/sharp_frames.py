#!/usr/bin/env python3
import argparse
import os
import sys
from typing import List, Dict, Any, Tuple, Set
# Import the core processor class and custom exception
from .sharp_frames_processor import SharpFrames, ImageProcessingError

# Import video directory utilities
from .video_utils import get_video_files_in_directory, detect_input_type

# Helper functions for interactive mode
def get_valid_file_path(prompt: str, must_exist: bool = True) -> str:
    """Get a valid file path from user input."""
    while True:
        path = input(prompt).strip()
        
        # Handle empty input
        if not path:
            print("Please enter a valid path.")
            continue
            
        # Expand user directory if present (e.g., ~/videos)
        path = os.path.expanduser(path)
        
        # Check if file exists when required
        if must_exist and not os.path.isfile(path):
            print(f"Error: File '{path}' not found. Please enter a valid file path.")
            continue
            
        return path

def get_valid_dir_path(prompt: str, create_if_missing: bool = True, check_emptiness: bool = True) -> str:
    """Get a valid directory path from user input."""
    while True:
        path = input(prompt).strip()
        
        # Handle empty input
        if not path:
            print("Please enter a valid directory path.")
            continue
            
        # Expand user directory if present (e.g., ~/output)
        path = os.path.expanduser(path)
        
        # Check if directory exists
        if os.path.exists(path):
            if not os.path.isdir(path):
                print(f"Error: '{path}' exists but is not a directory. Please enter a directory path.")
                continue
                
            # Check if directory is empty only if requested
            if check_emptiness and os.listdir(path):
                overwrite = input(f"Directory '{path}' is not empty. Files may be overwritten. Continue? (y/n): ").strip().lower()
                if overwrite not in ['y', 'yes']:
                    continue
        elif create_if_missing:
            try:
                os.makedirs(path)
                print(f"Created directory: {path}")
            except Exception as e:
                print(f"Error creating directory '{path}': {str(e)}. Please enter a valid path.")
                continue
        else:
            print(f"Error: Directory '{path}' does not exist. Please enter a valid path.")
            continue
            
        return path

def get_valid_int(prompt: str, min_value: int = None, max_value: int = None, default: int = None) -> int:
    """Get a valid integer from user input."""
    # Add default to prompt if provided
    if default is not None:
        prompt = f"{prompt} [{default}]: "
    
    while True:
        user_input = input(prompt).strip()
        
        # Use default value if input is empty
        if user_input == "" and default is not None:
            return default
        
        # Try to convert to integer
        try:
            value = int(user_input)
        except ValueError:
            print("Please enter a valid integer.")
            continue
            
        # Validate range if specified
        if min_value is not None and value < min_value:
            print(f"Please enter a value greater than or equal to {min_value}.")
            continue
            
        if max_value is not None and value > max_value:
            print(f"Please enter a value less than or equal to {max_value}.")
            continue
            
        return value

def get_choice(prompt: str, choices: List[str], default: str = None) -> str:
    """Get a choice from a list of options."""
    # Format choices for display
    choices_display = "/".join(choices)
    
    # Add default to prompt if provided
    if default is not None and default in choices:
        prompt = f"{prompt} ({choices_display}) [{default}]: "
    else:
        prompt = f"{prompt} ({choices_display}): "
    
    while True:
        user_input = input(prompt).strip().lower()
        
        # Use default value if input is empty
        if user_input == "" and default is not None:
            return default
        
        # Check if input is a valid full choice (case-insensitive)
        for choice in choices:
            if user_input == choice.lower():
                return choice

        # Check if input is 3 letters and matches the start of a choice (case-insensitive)
        if len(user_input) == 3:
            for choice in choices:
                if choice.lower().startswith(user_input):
                    return choice # Assume first 3 letters are unique enough

        # If no match found (full or 3-letter prefix)
        print(f"Please enter one of the following (or first 3 letters): {choices_display}")

def get_yes_no(prompt: str, default: bool = None) -> bool:
    """Get a yes/no response from the user."""
    # Add default to prompt if provided
    if default is not None:
        default_str = "y" if default else "n"
        prompt = f"{prompt} (y/n) [{default_str}]: "
    else:
        prompt = f"{prompt} (y/n): "
    
    while True:
        user_input = input(prompt).strip().lower()
        
        # Use default value if input is empty
        if user_input == "" and default is not None:
            return default
        
        if user_input in ["y", "yes"]:
            return True
        elif user_input in ["n", "no"]:
            return False
        else:
            print("Please enter 'y' or 'n'.")

def main():
    parser = argparse.ArgumentParser(description="Extract, score, and select the best frames from a video, video directory, or image directory.")
    parser.add_argument("input_path", nargs="?", help="Path to the input video file, video directory, or image directory")
    parser.add_argument("output_dir", nargs="?", help="Directory to save selected frames")
    parser.add_argument("--fps", type=int, default=10, help="Frames per second to extract (video and video directory input, default: 10)")
    parser.add_argument("--num-frames", type=int, default=300, help="Number of frames to select (default: 300)")
    parser.add_argument("--min-buffer", type=int, default=3, help="Minimum buffer between selected frames (default: 3)")
    parser.add_argument("--format", choices=["jpg", "png"], default="jpg", help="Output image format (default: jpg)")
    parser.add_argument("--force-overwrite", action="store_true", help="Overwrite existing files without confirmation")
    parser.add_argument("--selection-method", choices=["best-n", "batched", "outlier-removal"],
                       default="best-n", help="Frame selection method (default: best-n)")
    parser.add_argument("--batch-size", type=int, default=5,
                       help="Number of frames in each batch for batch selection (default: 5)")
    parser.add_argument("--batch-buffer", type=int, default=2,
                       help="Number of frames to skip between batches (default: 2)")
    parser.add_argument("--outlier-window-size", type=int, default=15,
                       help="Number of neighboring frames to compare for outlier detection (default: 15)")
    parser.add_argument("--outlier-sensitivity", type=int, default=50,
                       help="Sensitivity of outlier detection, 0-100 (default: 50)")
    parser.add_argument("--width", type=int, default=0,
                       help="Width to resize output images (height will be adjusted proportionally, 0 for no resizing)")
    parser.add_argument("--interactive", action="store_true", help="Run in legacy terminal prompt mode")
    parser.add_argument("--textual", action="store_true", help="Run with TUI interface (default when no paths provided)")

    args = parser.parse_args()

    # If no paths provided, launch the TUI interface
    if args.input_path is None and args.output_dir is None:
        if args.interactive:
            # User explicitly requested legacy interactive mode
            return run_interactive_mode()
        else:
            # Default to TUI interface
            try:
                from .textual_interface import run_textual_interface
                return 0 if run_textual_interface() else 1
            except ImportError:
                print("Error: Textual package is required for the Sharp Frames interface.")
                print("Install it with: pip install textual")
                print("Or use --interactive for legacy terminal-based input.")
                return 1
    
    # Check for explicit textual interface request (even with paths provided)
    if args.textual:
        try:
            from .textual_interface import run_textual_interface
            return 0 if run_textual_interface() else 1
        except ImportError:
            print("Error: Textual package is required for --textual mode.")
            print("Install it with: pip install textual")
            return 1

    # Validate input path and determine type
    if not os.path.exists(args.input_path):
        print(f"Error: Input path not found: {args.input_path}")
        return 1

    input_type = detect_input_type(args.input_path)
    
    # Handle input type specific logic
    if input_type == "directory":
        print("Input path is a directory. Processing images.")
        # Ensure FPS is not used inappropriately
        if args.fps != 10: # Check if user explicitly set FPS for directory
             print("Warning: --fps argument is ignored for directory input.")
        args.fps = 0 # Set fps to 0 or None to signal directory input downstream
    elif input_type == "video_directory":
        video_files = get_video_files_in_directory(args.input_path)
        print(f"Input path is a directory containing {len(video_files)} video file(s). Processing videos.")
        # FPS is used for video directory processing

    # Ensure output directory is specified
    if not args.output_dir:
         print("Error: Output directory must be specified.")
         parser.print_help()
         return 1

    processor = SharpFrames(
        input_path=args.input_path,
        input_type=input_type, # Pass the detected input type
        output_dir=args.output_dir,
        fps=args.fps,
        num_frames=args.num_frames,
        min_buffer=args.min_buffer,
        output_format=args.format,
        force_overwrite=args.force_overwrite,
        selection_method=args.selection_method,
        batch_size=args.batch_size,
        batch_buffer=args.batch_buffer,
        outlier_window_size=args.outlier_window_size,
        outlier_sensitivity=args.outlier_sensitivity,
        width=args.width
    )

    success = processor.run()
    return 0 if success else 1

def run_interactive_mode():
    """Run the program in interactive mode, prompting the user for input."""
    print("\033[34m" + r"""
                                                                                                                                                                                                        
  ______ _     _ _______ ______  ______     _______ ______  _______ _______ _______  ______ 
 / _____|_)   (_|_______|_____ \(_____ \   (_______|_____ \(_______|_______|_______)/ _____)
( (____  _______ _______ _____) )_____) )   _____   _____) )_______ _  _  _ _____  ( (____  
 \____ \|  ___  |  ___  |  __  /|  ____/   |  ___) |  __  /|  ___  | ||_|| |  ___)  \____ \ 
 _____) ) |   | | |   | | |  \ \| |        | |     | |  \ \| |   | | |   | | |_____ _____) )
(______/|_|   |_|_|   |_|_|   |_|_|        |_|     |_|   |_|_|   |_|_|   |_|_______|______/                                                                                                                                                                      
""" + "\033[0m")

    print("\n=== Sharp Frames by Reflct.app - Interactive Mode ===")
    print("Please answer the following questions to configure the processing.\n")

    # Determine input type
    input_type_choice = get_choice(
        "What would you like to process? (or first 3 letters)",
        ["video", "directory", "video-directory"],
        default="video"
    )

    input_path = ""
    if input_type_choice == "video":
        input_path = get_valid_file_path("Enter the path to the input video file: ", must_exist=True)
        input_type = "video"
        # Get frames per second only for video
        fps = get_valid_int("Enter frames per second to extract", min_value=1, max_value=60, default=10)
    elif input_type_choice == "video-directory":
        # Use get_valid_dir_path but don't create or check emptiness for INPUT dir
        input_path = get_valid_dir_path(
            "Enter the path to the directory containing video files: ",
            create_if_missing=False,
            check_emptiness=False # Don't check emptiness for input
        )
        input_type = "video_directory"
        # Get frames per second for video directory processing
        fps = get_valid_int("Enter frames per second to extract from each video", min_value=1, max_value=60, default=10)
        # Show how many videos were found
        video_files = get_video_files_in_directory(input_path)
        if not video_files:
            print(f"Warning: No video files found in directory '{input_path}'")
        else:
            print(f"Found {len(video_files)} video file(s) to process.")
    else:
        # Use get_valid_dir_path but don't create or check emptiness for INPUT dir
        input_path = get_valid_dir_path(
            "Enter the path to the input image directory: ",
            create_if_missing=False,
            check_emptiness=False # Don't check emptiness for input
        )
        input_type = "directory"
        fps = 0 # Set fps to 0 for directory input

    output_dir = get_valid_dir_path(
        "Enter the output directory path (will be created if needed): ",
        create_if_missing=True,
        check_emptiness=True # Check emptiness for output
    )

    # Common options
    selection_method = get_choice(
        "Choose frame/image selection method (or first 3 letters)",
        choices=["best-n", "batched", "outlier-removal"],
        default="best-n"
    )

    # Set defaults first
    num_frames = 300
    min_buffer = 3
    batch_size = 5
    batch_buffer = 2
    outlier_window_size = 15
    outlier_sensitivity = 50

    # Get method-specific parameters
    if selection_method == "best-n":
        num_frames = get_valid_int("Enter number of frames/images to select", min_value=1, default=300)
        min_buffer = get_valid_int("Enter minimum buffer between frames/images", min_value=0, default=3)
    elif selection_method == "batched":
        batch_size = get_valid_int("Enter batch size", min_value=1, default=5)
        batch_buffer = get_valid_int("Enter batch buffer (frames/images to skip between batches)", min_value=0, default=2)
    elif selection_method == "outlier-removal":
        outlier_window_size = get_valid_int("Enter window size for comparison", min_value=3, max_value=30, default=15)
        outlier_sensitivity = get_valid_int("Enter sensitivity (0-100, higher is more aggressive)", min_value=0, max_value=100, default=50)

    output_format = get_choice(
        "Choose output format for saved images (or first 3 letters)",
        choices=["jpg", "png"],
        default="jpg"
    )
    
    # Add option for resizing
    width = get_valid_int("Enter width to resize images (0 for no resizing, height will be adjusted proportionally)", min_value=0, default=0)
    
    force_overwrite = get_yes_no("Force overwrite existing files in output directory without confirmation?", default=False)

    # Print summary
    print("\n=== Configuration Summary ===")
    print(f"Input path: {input_path} (Type: {input_type})")
    print(f"Output directory: {output_dir}")
    if input_type in ["video", "video_directory"]:
        print(f"FPS for extraction: {fps}")
    print(f"Selection method: {selection_method}")

    if selection_method == "best-n":
        print(f"Number of frames/images: {num_frames}")
        print(f"Minimum buffer: {min_buffer}")
    elif selection_method == "batched":
        print(f"Batch size: {batch_size}")
        print(f"Batch buffer: {batch_buffer}")
    elif selection_method == "outlier-removal":
        print(f"Window size: {outlier_window_size}")
        print(f"Sensitivity: {outlier_sensitivity}")

    print(f"Output format: {output_format}")
    if width > 0:
        print(f"Resize width: {width} (proportional height)")
    else:
        print("No resizing will be applied")
    print(f"Force overwrite: {'Yes' if force_overwrite else 'No'}")

    # Confirm before proceeding
    proceed = get_yes_no("\nProceed with these settings?", default=True)
    if not proceed:
        print("Operation cancelled by user.")
        return 1

    # Process the video or directory
    processor = SharpFrames(
        input_path=input_path,
        input_type=input_type,
        output_dir=output_dir,
        fps=fps,
        num_frames=num_frames,
        min_buffer=min_buffer,
        output_format=output_format,
        force_overwrite=force_overwrite,
        selection_method=selection_method,
        batch_size=batch_size,
        batch_buffer=batch_buffer,
        outlier_window_size=outlier_window_size,
        outlier_sensitivity=outlier_sensitivity,
        width=width
    )

    success = processor.run()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())