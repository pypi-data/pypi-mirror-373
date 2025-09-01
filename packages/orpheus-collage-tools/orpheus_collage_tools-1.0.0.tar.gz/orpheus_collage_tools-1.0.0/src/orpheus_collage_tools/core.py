#!/usr/bin/env python3
"""
Orpheus Collage Tools - Cross-Platform Core
Core functionality for Windows/Linux implementations
"""

import os
import sys
import json
import platform
import subprocess
from pathlib import Path
import getpass
import urllib.request
import urllib.parse
import http.cookiejar
from typing import Optional, Dict, Any

class OrpheusTools:
    def __init__(self):
        self.system = platform.system().lower()
        self.script_dir = Path(__file__).parent.parent
        self.lib_dir = self.script_dir / "lib"

        # Cross-platform config directory
        if self.system == "windows":
            self.config_dir = Path(os.environ.get("APPDATA", "")) / "orpheus"
        else:
            self.config_dir = Path.home() / ".orpheus"

        self.config_file = self.config_dir / "config.json"

        # Add lib directory to Python path
        sys.path.insert(0, str(self.lib_dir))

    def clear_screen(self):
        """Cross-platform screen clearing"""
        if self.system == "windows":
            os.system("cls")
        else:
            os.system("clear")

    def setup_config(self) -> bool:
        """Setup configuration file with user credentials"""
        print("🔧 Setting up Orpheus configuration...")

        # Create config directory
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created config directory: {self.config_dir}")
        except Exception as e:
            print(f"❌ Failed to create config directory: {e}")
            return False

        if self.config_file.exists():
            print("✅ Configuration file already exists")
            return True

        print("\n🔑 Orpheus Configuration Setup")
        print("==============================")
        print("Configuration file not found. Please provide your Orpheus credentials.")
        print()

        # Get credentials
        username = self._get_input("Enter your Orpheus username: ")
        if not username:
            print("❌ Username is required!")
            return False

        password = getpass.getpass("Enter your Orpheus password: ")
        if not password:
            print("❌ Password is required!")
            return False

        # Validate credentials
        print("🔍 Validating credentials...")
        if not self._validate_credentials(username, password):
            print("❌ Credential validation failed!")
            return False

        # Get API key
        api_key = self._get_input("Enter your Orpheus API key: ")
        if not api_key:
            print("❌ API key is required!")
            return False

        # Validate API key
        print("🔍 Validating API key...")
        if not self._validate_api_key(api_key):
            print("❌ API key validation failed!")
            return False

        # Save configuration
        config = {
            "username": username,
            "password": password,
            "api_key": api_key
        }

        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)

            # Set appropriate permissions (readable only by owner)
            if self.system != "windows":
                self.config_file.chmod(0o600)

            print(f"✅ Configuration saved to: {self.config_file}")
            print("🔒 File permissions set to owner-only access")
            return True

        except Exception as e:
            print(f"❌ Failed to save configuration: {e}")
            return False

    def _get_input(self, prompt: str) -> str:
        """Cross-platform input handling"""
        try:
            return input(prompt).strip()
        except KeyboardInterrupt:
            print("\n❌ Setup cancelled by user")
            sys.exit(1)

    def _validate_credentials(self, username: str, password: str) -> bool:
        """Validate login credentials using HTTP request"""
        try:
            # Create cookie jar
            cookie_jar = http.cookiejar.CookieJar()

            # Prepare login data
            login_data = {
                'username': username,
                'password': password,
                'keeplogged': '1',
                'login': 'Log in'
            }

            # Create opener with cookie support
            opener = urllib.request.build_opener(
                urllib.request.HTTPCookieProcessor(cookie_jar)
            )

            # Encode data
            data = urllib.parse.urlencode(login_data).encode('utf-8')

            # Create request
            req = urllib.request.Request(
                'https://orpheus.network/login.php',
                data=data,
                headers={
                    'User-Agent': 'Orpheus-CLI/1.0',
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            )

            # Make request
            with opener.open(req) as response:
                return response.getcode() in [200, 302, 303]

        except Exception as e:
            print(f"❌ Credential validation error: {e}")
            return False

    def _validate_api_key(self, api_key: str) -> bool:
        """Validate API key with a test request"""
        try:
            # Create request
            req = urllib.request.Request(
                'https://orpheus.network/ajax.php?action=collage&id=1',
                headers={
                    'Authorization': f'token {api_key}',
                    'User-Agent': 'Orpheus-CLI/1.0'
                }
            )

            # Make request
            with urllib.request.urlopen(req) as response:
                if response.getcode() == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    return data.get('status') == 'success'
                return False

        except Exception as e:
            print(f"❌ API key validation error: {e}")
            return False

    def load_config(self) -> Optional[Dict[str, Any]]:
        """Load configuration from file"""
        if not self.config_file.exists():
            return None

        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return None

    def run_interactive_menu(self):
        """Run the interactive menu system"""
        self.clear_screen()

        # ASCII Art header
        print("\033[1;34m")
        print("  ######    ######    ######  ##    ##  #######  ##    ##  ######  ")
        print(" ##    ##  ##   ##   ##   ##  ##    ##  ##       ##    ## ##    ## ")
        print(" ##    ##  ##   ##   ##   ##  ##    ##  ##       ##    ## ##       ")
        print(" ##    ##  ######    ######   ########  ######   ##    ##  ######  ")
        print(" ##    ##  ##  ##    ##       ##    ##  ##       ##    ##       ## ")
        print(" ##    ##  ##   ##   ##       ##    ##  ##       ##    ## ##    ## ")
        print("  ######   ##    ##  ##       ##    ##  #######   ######   ######  ")
        print("\033[1;36m")
        print(" Orpheus Collage Tools - Interactive Mode")
        print("\033[1;32m")
        print()
        print("===========================================")
        print()
        print("What would you like to do?")
        print("\033[1;31m")
        print("1. 🎤 Find artist albums & releases (with crates)")
        print("\033[1;32m")
        print("2. 🔍 Find collages")
        print("\033[1;35m")
        print("3. ⬇️  Download torrents from a collage")
        print("\033[1;37m")
        print("4. 📦 Manage crates")
        print("\033[1;38m")
        print("5. 🎯 Load crate and browse")
        print("\033[1;39m")
        print("6. ❌ Exit")
        print()
        print("💡 Quick tips:")
        print("   • Use option 1 for browsing artist discographies")
        print("   • Use option 2 for all collage search and discovery")
        print("   • Use option 3 to download by collage ID")
        print("   • All downloads save to ~/Documents/Orpheus/")
        print()
        print()

        try:
            choice = self._get_input("Choose option (1-6): ").strip()

            if choice == "1":
                self._handle_artist_search()
            elif choice == "2":
                self._handle_collage_menu()
            elif choice == "3":
                self._handle_download()
            elif choice == "4":
                self._handle_crate_management()
            elif choice == "5":
                self._handle_crate_browse()
            elif choice == "6":
                print("👋 Goodbye!")
                return
            else:
                print("❌ Invalid choice!")
                self._get_input("Press Enter to continue...")
                self.run_interactive_menu()

        except KeyboardInterrupt:
            print("\n❌ Cancelled by user")
            return
        except Exception as e:
            print(f"❌ Error: {e}")
            self._get_input("Press Enter to continue...")
            self.run_interactive_menu()

    def _handle_artist_search(self):
        """Handle artist search option"""
        print("\n🎤 Find Artist Albums & Releases (Enhanced with Crates)")
        print("======================================================")

        artist = self._get_input("Enter artist name: ")
        if not artist:
            print("❌ Artist name is required!")
            self._get_input("Press Enter to continue...")
            self.run_interactive_menu()
            return

        print("\n🎵 Release search options:")
        print("1. All releases (including compilations)")
        print("2. Official releases only")
        print("3. Search specific release")
        print()

        search_option = self._get_input("Choose option (1-3): ").strip()

        if search_option == "1":
            print(f"\n🔍 Searching for all releases by {artist}...")
            self.run_command("find_album_collages", "--artist", artist, "--interactive")
        elif search_option == "2":
            print(f"\n🔍 Searching for official releases by {artist}...")
            self.run_command("find_album_collages", "--artist", artist, "--official-only", "--interactive")
        elif search_option == "3":
            album = self._get_input("Enter album/release name: ")
            if not album:
                print("❌ Album name is required!")
                self._get_input("Press Enter to continue...")
                self.run_interactive_menu()
                return
            print(f"\n🔍 Searching for '{album}' by {artist}...")
            self.run_command("find_album_collages", "--artist", artist, "--album", album, "--interactive")
        else:
            print("❌ Invalid choice!")
            self._get_input("Press Enter to continue...")
            self.run_interactive_menu()
            return

        self._get_input("Press Enter to return to main menu...")
        self.run_interactive_menu()

    def _handle_collage_menu(self):
        """Handle collage search submenu"""
        print("\n🔍 COLLAGE SEARCH OPTIONS")
        print("=========================")
        print()
        print("1. 🎵 Find collages featuring an artist")
        print("2. 🔍 Find which collages contain a specific album")
        print("3. 📝 Search & download collages by name")
        print("4. 🔙 Back to main menu")
        print()

        choice = self._get_input("Choose option (1-4): ").strip()

        if choice == "1":
            artist = self._get_input("Enter artist name: ")
            if not artist:
                print("❌ Artist name is required!")
                self._get_input("Press Enter to continue...")
                self._handle_collage_menu()
                return
            print(f"\n🔍 Searching for collages that contain albums by {artist}...")
            print("💡 This will find all collages featuring the artist's music")
            self.run_command("search_artist_collages", artist)

        elif choice == "2":
            artist = self._get_input("Enter artist name: ")
            album = self._get_input("Enter album name: ")
            if not artist or not album:
                print("❌ Both artist and album names are required!")
                self._get_input("Press Enter to continue...")
                self._handle_collage_menu()
                return
            print(f"\n🔍 Searching for '{album}' by {artist} in collages...")
            self.run_command("find_album_collages", "--artist", artist, "--album", album, "--show-collages")

        elif choice == "3":
            search_term = self._get_input("Enter collage name or keywords: ")
            if not search_term:
                print("❌ Search term is required!")
                self._get_input("Press Enter to continue...")
                self._handle_collage_menu()
                return
            print(f"\n🔍 Searching for collages containing: '{search_term}'")
            print("💡 This will show matching collages with their IDs")
            print("   You can then use option 3 to download them")
            # Note: This would need a search_collages.py script
            print("❌ Collage search by name not yet implemented")

        elif choice == "4":
            self.run_interactive_menu()
            return
        else:
            print("❌ Invalid choice! Please choose 1, 2, 3, or 4.")
            self._get_input("Press Enter to continue...")
            self._handle_collage_menu()
            return

        self._get_input("Press Enter to return to collage menu...")
        self._handle_collage_menu()

    def _handle_download(self):
        """Handle torrent download option"""
        print("\n⬇️  Download Torrents from a Collage")
        print("====================================")

        collage_id = self._get_input("Enter collage ID: ")
        if not collage_id:
            print("❌ Collage ID is required!")
            self._get_input("Press Enter to continue...")
            self.run_interactive_menu()
            return

        print("\n📀 Choose preferred encoding:")
        print("1. MP3 320 CBR     (High quality, universal compatibility)")
        print("2. MP3 V0 VBR      (Excellent quality, smaller files)")
        print("3. FLAC Lossless   (Perfect quality, largest files)")
        print()
        print("💡 Tips:")
        print("   • 320 CBR: Best for most users, works everywhere")
        print("   • V0 VBR: Great quality with smaller file sizes")
        print("   • FLAC: Perfect quality for audiophiles")
        print()

        encoding_choice = self._get_input("Choose option (1-3): ").strip()

        if encoding_choice == "1":
            prefer = "--prefer-320"
            format_name = "MP3 320 CBR"
        elif encoding_choice == "2":
            prefer = "--prefer-v0"
            format_name = "MP3 V0 VBR"
        elif encoding_choice == "3":
            prefer = "--prefer-flac"
            format_name = "FLAC Lossless"
        else:
            print("❌ Invalid choice!")
            self._get_input("Press Enter to continue...")
            self.run_interactive_menu()
            return

        print(f"\n⬇️ Starting download from collage ID: {collage_id}")
        print(f"🎵 Preferred format: {format_name}")
        print()
        self.run_command("download_collage_torrents", collage_id, prefer)
        self._get_input("Press Enter to return to main menu...")
        self.run_interactive_menu()

    def _handle_crate_management(self):
        """Handle crate management option"""
        print("\n📦 Crate Management")
        print("==================")
        print("1. 📋 List existing crates")
        print("2. 📝 Create new crate")
        print("3. ⬇️  Download a crate")
        print("4. 🔙 Back to main menu")
        print()

        choice = self._get_input("Choose option (1-4): ").strip()

        if choice == "1":
            self.run_command("download_crate", "--list-crates")
        elif choice == "2":
            crate_name = self._get_input("Enter crate name: ")
            if crate_name:
                self.run_command("download_crate", "--create-crate", crate_name)
            else:
                print("❌ Please provide a crate name")
        elif choice == "3":
            print()
            self.run_command("download_crate", "--list-crates")
            print()
            crate_name = self._get_input("Enter crate name to download: ")
            if crate_name:
                self.run_command("download_crate", "--download-crate", crate_name)
            else:
                print("❌ Please provide a crate name")
        elif choice == "4":
            self.run_interactive_menu()
            return
        else:
            print("❌ Invalid choice!")

        self._get_input("Press Enter to continue...")
        self.run_interactive_menu()

    def _handle_crate_browse(self):
        """Handle crate browsing option"""
        print("\n🎯 Load Crate and Browse")
        print("=======================")

        self.run_command("download_crate", "--list-crates")
        print()

        crate_name = self._get_input("Enter crate name to load: ")
        if not crate_name:
            print("❌ Please provide a crate name")
            self._get_input("Press Enter to continue...")
            self.run_interactive_menu()
            return

        artist = self._get_input("Enter artist to search: ")
        if not artist:
            print("❌ Artist name is required for browsing")
            self._get_input("Press Enter to continue...")
            self.run_interactive_menu()
            return

        print("🔍 Searching with crate functionality...")
        self.run_command("find_album_collages", "--artist", artist, "--interactive")
        self._get_input("Press Enter to return to main menu...")
        self.run_interactive_menu()

    def run_command(self, command: str, *args):
        """Run a Python script from the lib directory"""
        script_path = self.lib_dir / f"{command}.py"
        if not script_path.exists():
            print(f"❌ Script not found: {script_path}")
            return

        # Build command arguments
        cmd_args = [sys.executable, str(script_path)] + list(args)

        try:
            subprocess.run(cmd_args)
        except KeyboardInterrupt:
            print("\n❌ Command cancelled by user")
        except Exception as e:
            print(f"❌ Error running command: {e}")

    def show_help(self):
        """Show help information"""
        print("🎵 Orpheus Collage Tools - Cross-Platform")
        print("==========================================")
        print()
        print("Usage:")
        print("  orpheus                    # Interactive mode")
        print("  orpheus find-album --artist 'Name'")
        print("  orpheus find-artist-collages 'Artist'")
        print("  orpheus download <id> --prefer-320")
        print("  orpheus crate list")
        print()
        print("For more help, run without arguments for interactive mode")
