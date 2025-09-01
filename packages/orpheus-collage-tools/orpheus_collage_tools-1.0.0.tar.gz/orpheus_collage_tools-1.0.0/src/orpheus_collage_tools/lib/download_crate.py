#!/usr/bin/env python3
"""
Download music crates - collections of albums with preferences
"""

import asyncio
import json
import argparse
import sys
import os
from pathlib import Path
from typing import List, Dict

# Add current directory to path for local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from download_album_preferences import OrpheusAlbumDownloader

class MusicCrateManager:
    def __init__(self):
        # Use relative path from the script location to find resources/data/crates
        script_dir = Path(__file__).parent.parent  # Go up from lib/ to project root
        self.crates_dir = script_dir / 'resources' / 'data' / 'crates'
        # Cross-platform download directory
        import platform
        system = platform.system()
        if system == "Windows":
            self.downloads_dir = Path.home() / 'Documents' / 'Orpheus'
        elif system == "Darwin":  # macOS
            self.downloads_dir = Path.home() / 'Documents' / 'Orpheus'
        else:  # Linux and other Unix-like systems
            self.downloads_dir = Path.home() / 'Documents' / 'Orpheus'
        self.crates_dir.mkdir(exist_ok=True)
        self.downloads_dir.mkdir(parents=True, exist_ok=True)

    def create_crate_template(self, crate_name: str) -> str:
        """Create a template crate file"""
        template = {
            "name": crate_name,
            "description": f"Music collection: {crate_name}",
            "created_by": "Orpheus Crate Manager",
            "preferences": {
                "media": "vinyl",
                "encoding": "flac"
            },
            "albums": [
                {
                    "artist": "Example Artist",
                    "album": "Example Album",
                    "notes": "Optional notes about this album"
                },
                {
                    "artist": "Another Artist", 
                    "album": "Another Album",
                    "group_id": 12345,
                    "notes": "You can also specify direct group_id instead of artist/album"
                }
            ]
        }
        
        crate_file = self.crates_dir / f"{crate_name}.json"
        with open(crate_file, 'w') as f:
            json.dump(template, f, indent=2)
        
        return str(crate_file)

    def load_crate(self, crate_name: str) -> Dict:
        """Load a crate file"""
        crate_file = self.crates_dir / f"{crate_name}.json"
        if not crate_file.exists():
            raise FileNotFoundError(f"Crate '{crate_name}' not found at {crate_file}")
        
        with open(crate_file, 'r') as f:
            return json.load(f)

    def list_crates(self) -> List[str]:
        """List all available crates"""
        return [f.stem for f in self.crates_dir.glob("*.json")]

    async def download_crate(
        self, 
        crate_name: str, 
        prefer_media: str = None,
        prefer_encoding: str = None,
        dry_run: bool = False,
        skip_existing: bool = True
    ):
        """Download all albums in a crate"""
        
        # Load crate
        print(f"📦 Loading crate: {crate_name}")
        crate = self.load_crate(crate_name)
        
        # Use crate preferences if not overridden
        crate_prefs = crate.get('preferences', {})
        media_pref = prefer_media or crate_prefs.get('media')
        encoding_pref = prefer_encoding or crate_prefs.get('encoding')
        
        print(f"🎵 Crate: {crate['name']}")
        if crate.get('description'):
            print(f"📝 Description: {crate['description']}")
        print(f"💿 Albums to download: {len(crate['albums'])}")
        
        if media_pref:
            print(f"🎯 Media preference: {media_pref}")
        if encoding_pref:
            print(f"🎵 Encoding preference: {encoding_pref}")
        
        # Create crate folder
        crate_folder = self.downloads_dir / f"Crates" / crate_name
        if not dry_run:
            crate_folder.mkdir(parents=True, exist_ok=True)
            print(f"📁 Download folder: {crate_folder}")
        
        print(f"\n{'=' * 60}")
        
        successful_downloads = 0
        failed_downloads = 0
        skipped_downloads = 0
        
        async with OrpheusAlbumDownloader() as downloader:
            # Login
            print("🔐 Logging in to Orpheus...")
            if not await downloader.login():
                print("❌ Login failed")
                return
            
            # Download each album
            for i, album_info in enumerate(crate['albums'], 1):
                print(f"\n[{i}/{len(crate['albums'])}] Processing album...")
                
                # Extract album info
                artist = album_info.get('artist')
                album = album_info.get('album') 
                group_id = album_info.get('group_id')
                notes = album_info.get('notes', '')
                
                if notes:
                    print(f"📝 Notes: {notes}")
                
                # Check if already downloaded
                if skip_existing and not dry_run:
                    if artist and album:
                        safe_artist = "".join(c for c in artist if c.isalnum() or c in (' ', '-', '_')).strip()
                        safe_album = "".join(c for c in album if c.isalnum() or c in (' ', '-', '_')).strip()
                        pattern = f"{safe_artist} - {safe_album}*"
                    else:
                        pattern = f"GroupID-{group_id}*" if group_id else "*"
                    
                    existing_files = list(crate_folder.glob(f"**/{pattern}.torrent"))
                    if existing_files:
                        print(f"⏭️  Already downloaded: {existing_files[0].name}")
                        skipped_downloads += 1
                        continue
                
                if dry_run:
                    print(f"🔍 Would download: {artist} - {album}" + (f" (Group ID: {group_id})" if group_id else ""))
                    continue
                
                try:
                    # Create custom downloader for this album with crate folder
                    class CrateAlbumDownloader(OrpheusAlbumDownloader):
                        def __init__(self, crate_folder, *args, **kwargs):
                            super().__init__(*args, **kwargs)
                            self.crate_folder = crate_folder
                        
                        async def download_torrent(self, torrent_id: int, filename: str):
                            """Override to download to crate folder"""
                            download_url = f"{self.base_url}/torrents.php"
                            params = {
                                'action': 'download',
                                'id': torrent_id
                            }

                            async with self.session.get(download_url, params=params) as response:
                                if response.status == 200:
                                    content = await response.read()
                                    
                                    file_path = self.crate_folder / filename
                                    
                                    with open(file_path, 'wb') as f:
                                        f.write(content)
                                    
                                    print(f"✅ Downloaded: {filename}")
                                    print(f"   Saved to: {file_path}")
                                    return True
                                else:
                                    print(f"❌ Download failed! Status: {response.status}")
                                    return False
                    
                    # Use the existing session from the outer downloader
                    crate_downloader = CrateAlbumDownloader(crate_folder)
                    crate_downloader.session = downloader.session
                    crate_downloader.username = downloader.username
                    crate_downloader.password = downloader.password
                    crate_downloader.api_key = downloader.api_key
                    
                    # Download the album
                    success = await crate_downloader.download_album_with_preferences(
                        artist=artist,
                        album=album,
                        group_id=group_id,
                        prefer_media=media_pref,
                        prefer_encoding=encoding_pref,
                        show_all=False
                    )
                    
                    if success:
                        successful_downloads += 1
                    else:
                        failed_downloads += 1
                        
                except Exception as e:
                    print(f"❌ Error downloading album: {e}")
                    failed_downloads += 1
                
                print(f"{'─' * 60}")
        
        # Summary
        print(f"\n🎯 Crate Download Summary")
        print(f"{'=' * 30}")
        print(f"✅ Successful: {successful_downloads}")
        print(f"❌ Failed: {failed_downloads}")
        if skip_existing:
            print(f"⏭️  Skipped (already downloaded): {skipped_downloads}")
        print(f"📦 Total albums: {len(crate['albums'])}")
        
        if not dry_run and successful_downloads > 0:
            print(f"📁 All downloads saved to: {crate_folder}")

def main():
    parser = argparse.ArgumentParser(
        description="Download music crates - collections of albums",
        epilog="""Examples:
  # Create a new crate template
  python3 download_crate.py --create-crate "90s Hip Hop"
  
  # List all available crates
  python3 download_crate.py --list-crates
  
  # Download all albums in a crate
  python3 download_crate.py --download-crate "90s Hip Hop"
  
  # Download with custom preferences (overrides crate preferences)
  python3 download_crate.py --download-crate "90s Hip Hop" --prefer-media cd --prefer-encoding v0
  
  # Dry run to see what would be downloaded
  python3 download_crate.py --download-crate "90s Hip Hop" --dry-run
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Main actions
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument('--create-crate', metavar='NAME', help='Create a new crate template')
    action_group.add_argument('--download-crate', metavar='NAME', help='Download all albums in a crate')
    action_group.add_argument('--list-crates', action='store_true', help='List all available crates')
    
    # Preferences (for download)
    parser.add_argument('--prefer-media', help='Preferred media type (overrides crate preference)')
    parser.add_argument('--prefer-encoding', help='Preferred encoding (overrides crate preference)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be downloaded without downloading')
    parser.add_argument('--no-skip-existing', action='store_true', help='Re-download existing files')
    
    args = parser.parse_args()
    
    manager = MusicCrateManager()
    
    if args.create_crate:
        try:
            crate_file = manager.create_crate_template(args.create_crate)
            print(f"✅ Created crate template: {crate_file}")
            print(f"📝 Edit the file to add your albums, then use:")
            print(f"   python3 download_crate.py --download-crate \"{args.create_crate}\"")
        except Exception as e:
            print(f"❌ Error creating crate: {e}")
    
    elif args.list_crates:
        crates = manager.list_crates()
        if crates:
            print("📦 Available crates:")
            for crate in crates:
                crate_file = manager.crates_dir / f"{crate}.json"
                try:
                    with open(crate_file, 'r') as f:
                        crate_data = json.load(f)
                    album_count = len(crate_data.get('albums', []))
                    description = crate_data.get('description', 'No description')
                    print(f"   • {crate} ({album_count} albums) - {description}")
                except:
                    print(f"   • {crate} (error reading file)")
        else:
            print("📦 No crates found. Create one with --create-crate")
    
    elif args.download_crate:
        try:
            asyncio.run(manager.download_crate(
                crate_name=args.download_crate,
                prefer_media=args.prefer_media,
                prefer_encoding=args.prefer_encoding,
                dry_run=args.dry_run,
                skip_existing=not args.no_skip_existing
            ))
        except FileNotFoundError as e:
            print(f"❌ {e}")
            print(f"💡 Available crates: {', '.join(manager.list_crates())}")
        except Exception as e:
            print(f"❌ Error downloading crate: {e}")

if __name__ == "__main__":
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("❌ BeautifulSoup4 is required. Install it with:")
        print("   pip3 install beautifulsoup4")
        sys.exit(1)
    
    main()
