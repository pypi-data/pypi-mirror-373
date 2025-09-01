#!/usr/bin/env python3
"""
Orpheus Collage Tools - Cross-Platform CLI
Main entry point for the Orpheus Collage Tools package
"""

import sys
import platform
from pathlib import Path

def main():
    """Main entry point that delegates to platform-specific implementations"""
    system = platform.system().lower()

    if system == "darwin":  # macOS
        # Use the existing bash script for macOS
        script_dir = Path(__file__).parent
        bash_script = script_dir / "scripts" / "macos" / "collage_tools.sh"

        if not bash_script.exists():
            print("❌ macOS script not found!")
            sys.exit(1)

        # Execute the bash script
        import subprocess
        result = subprocess.run([str(bash_script)] + sys.argv[1:])
        sys.exit(result.returncode)

    elif system in ["windows", "linux"]:
        # Use Python implementation for Windows/Linux
        from orpheus_collage_tools.core import OrpheusTools

        tools = OrpheusTools()

        # Setup configuration if needed
        if not tools.config_file.exists():
            if not tools.setup_config():
                print("❌ Configuration setup failed!")
                sys.exit(1)

        # Check command line arguments
        if len(sys.argv) == 1:
            # No arguments - run interactive mode
            tools.run_interactive_menu()
            return

        # Parse command line arguments
        command = sys.argv[1]
        args = sys.argv[2:]

        if command == "find-album":
            tools.run_command("find_album_collages", *args)
        elif command == "find-artist-collages":
            tools.run_command("search_artist_collages", *args)
        elif command == "download":
            tools.run_command("download_collage_torrents", *args)
        elif command == "crate":
            tools.run_command("download_crate", *args)
        else:
            tools.show_help()

    else:
        print(f"❌ Unsupported platform: {system}")
        print("Supported platforms: macOS, Windows, Linux")
        sys.exit(1)

if __name__ == "__main__":
    main()
