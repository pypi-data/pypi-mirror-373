#!/usr/bin/env python3
"""
Find and download albums with media and encoding preferences
"""

import asyncio
import json
import re
import argparse
import sys
from pathlib import Path
import aiohttp
import ssl
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Tuple

class OrpheusAlbumDownloader:
    def __init__(self, username: str = None, password: str = None, api_key: str = None):
        # Load credentials from config if not provided
        if not all([username, password, api_key]):
            config_path = Path.home() / '.orpheus' / 'config.json'
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    username = username or config.get('username')
                    password = password or config.get('password')
                    api_key = api_key or config.get('api_key')
            else:
                raise ValueError("No credentials provided and config file not found. Please provide username, password, and api_key, or create ~/.orpheus/config.json")

        if not all([username, password, api_key]):
            raise ValueError("Missing required credentials. Please provide username, password, and api_key")

        self.username = username
        self.password = password
        self.api_key = api_key
        self.base_url = "https://orpheus.network"
        self.session = None

        # Media type preferences (order matters)
        self.MEDIA_HIERARCHY = {
            'Vinyl': 1,
            'SACD': 2,
            'Blu-Ray': 3,
            'DVD': 4,
            'CD': 5,
            'Cassette': 6,
            'WEB': 7,
            'Soundboard': 8,
            'DAT': 9,
            'HDAD': 10
        }

        # Encoding preferences
        self.ENCODING_HIERARCHY = {
            'FLAC': {
                '24bit Lossless': 1,
                'Lossless': 2
            },
            'MP3': {
                '320': 3,
                'V0 (VBR)': 4,
                'V1 (VBR)': 5,
                'V2 (VBR)': 6,
                '256': 7,
                '192': 8,
                '128': 9
            },
            'AAC': {
                '320': 10,
                '256': 11,
                '192': 12
            },
            'AC3': {
                '640': 13,
                '448': 14
            },
            'DTS': {
                'DTS': 15
            }
        }

    async def __aenter__(self):
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        connector = aiohttp.TCPConnector(ssl=ssl_context)
        self.session = aiohttp.ClientSession(connector=connector)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def login(self) -> bool:
        """Login to Orpheus website"""
        login_url = f"{self.base_url}/login.php"

        login_data = {
            'username': self.username,
            'password': self.password,
            'keeplogged': '1',
            'login': 'Log in'
        }

        async with self.session.post(login_url, data=login_data, allow_redirects=False) as response:
            if 'session' in response.cookies or response.status in [302, 303]:
                return True
        return False

    async def get_torrent_group_details(self, group_id: int) -> Dict:
        """Get detailed torrent group information via API"""
        url = f"{self.base_url}/ajax.php"
        headers = {
            'Authorization': f'token {self.api_key}',
            'User-Agent': 'AlbumDownloader/1.0'
        }

        params = {
            'action': 'torrentgroup',
            'id': group_id
        }

        try:
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'success':
                        return data['response']
        except Exception as e:
            print(f"⚠️  API error for group {group_id}: {e}")
        return None

    async def search_album(self, artist_name: str, album_name: str) -> Optional[int]:
        """Search for a specific album and return its group ID"""
        search_url = f"{self.base_url}/torrents.php"
        params = {
            'action': 'advanced',
            'artistname': artist_name,
            'groupname': album_name
        }

        async with self.session.get(search_url, params=params) as response:
            if response.status != 200:
                return None

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            # Find the first matching torrent group
            for group_link in soup.find_all('a', href=re.compile(r'torrents\.php\?id=\d+')):
                if '#torrent' in group_link.get('href', ''):
                    continue

                group_id = re.search(r'id=(\d+)', group_link['href'])
                if group_id:
                    # Verify it's the right album
                    album_text = group_link.text.strip().lower()
                    if album_name.lower() in album_text:
                        return int(group_id.group(1))

        return None

    def get_encoding_priority(self, format: str, encoding: str) -> int:
        """Get priority score for encoding (lower is better)"""
        if format in self.ENCODING_HIERARCHY:
            return self.ENCODING_HIERARCHY[format].get(encoding, 999)
        return 999

    def get_media_priority(self, media: str) -> int:
        """Get priority score for media type (lower is better)"""
        return self.MEDIA_HIERARCHY.get(media, 999)

    def score_torrent(self, torrent: Dict, prefer_media: str = None, prefer_encoding: str = None) -> Tuple[int, int, int]:
        """
        Score a torrent based on preferences
        Returns (media_score, encoding_score, seeders) for sorting
        """
        media = torrent.get('media', '')
        format = torrent.get('format', '')
        encoding = torrent.get('encoding', '')
        seeders = torrent.get('seeders', 0)

        # Media scoring
        if prefer_media and media.lower() == prefer_media.lower():
            media_score = 0  # Perfect match
        else:
            media_score = self.get_media_priority(media)

        # Encoding scoring
        if prefer_encoding:
            # Try to match the preferred encoding
            if encoding.lower() == prefer_encoding.lower():
                encoding_score = 0  # Perfect match
            elif prefer_encoding.lower() in ['v0', 'vbr'] and 'V0' in encoding:
                encoding_score = 0  # V0 match
            elif prefer_encoding.lower() == '320' and '320' in encoding:
                encoding_score = 0  # 320 match
            elif prefer_encoding.lower() == 'flac' and format == 'FLAC':
                encoding_score = 1  # Any FLAC
            else:
                encoding_score = self.get_encoding_priority(format, encoding)
        else:
            encoding_score = self.get_encoding_priority(format, encoding)

        return (media_score, encoding_score, -seeders)  # Negative seeders for reverse sort

    def find_best_torrent(self, torrents: List[Dict], prefer_media: str = None, prefer_encoding: str = None) -> Optional[Dict]:
        """Find the best torrent based on preferences"""
        if not torrents:
            return None

        # Score and sort all torrents
        scored_torrents = []
        for torrent in torrents:
            score = self.score_torrent(torrent, prefer_media, prefer_encoding)
            scored_torrents.append((score, torrent))

        # Sort by score (lower is better for media and encoding, higher is better for seeders)
        scored_torrents.sort(key=lambda x: x[0])

        # Return the best match
        return scored_torrents[0][1]
    
    def find_best_torrent_with_fallback(self, torrents: List[Dict], prefer_media: str = None, prefer_encoding: str = None) -> Tuple[Optional[Dict], str]:
        """Find the best torrent with smart fallback logic and explanation"""
        if not torrents:
            return None, ""

        # Strategy 1: Try exact media + encoding match
        if prefer_media and prefer_encoding:
            exact_matches = [
                t for t in torrents 
                if (t.get('media', '').lower() == prefer_media.lower() and 
                    (t.get('encoding', '').lower() == prefer_encoding.lower() or
                     (prefer_encoding.lower() in ['v0', 'vbr'] and 'V0' in t.get('encoding', '')) or
                     (prefer_encoding.lower() == '320' and '320' in t.get('encoding', '')) or
                     (prefer_encoding.lower() == 'flac' and t.get('format', '') == 'FLAC')))
            ]
            if exact_matches:
                best = max(exact_matches, key=lambda t: t.get('seeders', 0))
                return best, f"Perfect match: {prefer_media} + {prefer_encoding}"

        # Strategy 2: Try preferred media with best available encoding
        if prefer_media:
            media_matches = [t for t in torrents if t.get('media', '').lower() == prefer_media.lower()]
            if media_matches:
                best = self.find_best_torrent(media_matches, prefer_media, prefer_encoding)
                if best:
                    return best, f"Media match: {prefer_media} (encoding: {best.get('format', '')} {best.get('encoding', '')})"

        # Strategy 3: Try preferred encoding with best available media
        if prefer_encoding:
            encoding_matches = [
                t for t in torrents 
                if (t.get('encoding', '').lower() == prefer_encoding.lower() or
                    (prefer_encoding.lower() in ['v0', 'vbr'] and 'V0' in t.get('encoding', '')) or
                    (prefer_encoding.lower() == '320' and '320' in t.get('encoding', '')) or
                    (prefer_encoding.lower() == 'flac' and t.get('format', '') == 'FLAC'))
            ]
            if encoding_matches:
                best = max(encoding_matches, key=lambda t: t.get('seeders', 0))
                return best, f"Encoding match: {prefer_encoding} (media: {best.get('media', '')})"

        # Strategy 4: Fall back to highest seeder count overall
        best = max(torrents, key=lambda t: t.get('seeders', 0))
        reason = "Most seeders"
        if prefer_media or prefer_encoding:
            reason += f" (preferences {prefer_media or ''} {prefer_encoding or ''} not available)"
        
        return best, reason

    def format_file_size(self, size_bytes: int) -> str:
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    async def download_torrent(self, torrent_id: int, filename: str):
        """Download a specific torrent file"""
        download_url = f"{self.base_url}/torrents.php"
        params = {
            'action': 'download',
            'id': torrent_id
        }

        async with self.session.get(download_url, params=params) as response:
            if response.status == 200:
                content = await response.read()
                
                # Cross-platform download directory
                import platform
                system = platform.system()
                if system == "Windows":
                    downloads_dir = Path.home() / 'Documents' / 'Orpheus'
                elif system == "Darwin":  # macOS
                    downloads_dir = Path.home() / 'Documents' / 'Orpheus'
                else:  # Linux and other Unix-like systems
                    downloads_dir = Path.home() / 'Documents' / 'Orpheus'
                downloads_dir.mkdir(parents=True, exist_ok=True)
                file_path = downloads_dir / filename
                
                with open(file_path, 'wb') as f:
                    f.write(content)
                
                print(f"✅ Downloaded: {filename}")
                print(f"   Saved to: {file_path}")
                return True
            else:
                print(f"❌ Download failed! Status: {response.status}")
                return False

    async def download_album_with_preferences(
        self, 
        artist: str = None, 
        album: str = None, 
        group_id: int = None,
        prefer_media: str = None,
        prefer_encoding: str = None,
        show_all: bool = False
    ):
        """Main function to search and download album with preferences"""
        
        # Handle direct group ID or search
        if group_id:
            print(f"🔍 Using direct Group ID: {group_id}")
        else:
            if not artist or not album:
                print("❌ Either provide --group-id OR both --artist and --album")
                return False
            print(f"🔍 Searching for '{album}' by {artist}...")
            group_id = await self.search_album(artist, album)
            
            if not group_id:
                print("❌ Album not found!")
                return False

        # Get torrent details
        print(f"📊 Found album (Group ID: {group_id})")
        details = await self.get_torrent_group_details(group_id)
        
        if not details:
            print("❌ Could not fetch album details!")
            return False

        group = details.get('group', {})
        torrents = details.get('torrents', [])
        
        if not torrents:
            print("❌ No torrents available for this album!")
            return False

        print(f"📀 Album: {group.get('name', 'Unknown')} ({group.get('year', 'Unknown')})")
        print(f"💿 Found {len(torrents)} torrent(s)")
        
        if prefer_media:
            print(f"🎯 Media preference: {prefer_media}")
        if prefer_encoding:
            print(f"🎵 Encoding preference: {prefer_encoding}")
        
        # Find best match with improved fallback logic
        best_torrent, fallback_reason = self.find_best_torrent_with_fallback(torrents, prefer_media, prefer_encoding)
        
        if not best_torrent:
            print("❌ No suitable torrent found!")
            return False

        # Display best match and reasoning
        print("\n✨ Best match:")
        if fallback_reason:
            print(f"   {fallback_reason}")
        print(f"   Media: {best_torrent['media']}")
        print(f"   Format: {best_torrent['format']} {best_torrent['encoding']}")
        print(f"   Size: {self.format_file_size(best_torrent['size'])}")
        print(f"   Seeders: {best_torrent['seeders']}")
        
        # Show remaster info if available
        if best_torrent.get('remasterTitle'):
            print(f"   Remaster: {best_torrent['remasterTitle']}")
        if best_torrent.get('remasterRecordLabel'):
            print(f"   Label: {best_torrent['remasterRecordLabel']}")

        # Show all options if requested
        if show_all:
            print("\n📋 All available torrents (sorted by preference):")
            scored_torrents = []
            for torrent in torrents:
                score = self.score_torrent(torrent, prefer_media, prefer_encoding)
                scored_torrents.append((score, torrent))
            
            scored_torrents.sort(key=lambda x: x[0])
            
            for i, (score, torrent) in enumerate(scored_torrents, 1):
                print(f"\n   {i}. {torrent['media']} | {torrent['format']} {torrent['encoding']}")
                print(f"      Size: {self.format_file_size(torrent['size'])} | Seeders: {torrent['seeders']}")
                if torrent == best_torrent:
                    print("      ⭐ BEST MATCH")

        # Auto-download unless showing all releases
        if not show_all:
            print("\n⬇️  Downloading best match...")
            # Create safe filename
            if artist and album:
                safe_artist = "".join(c for c in artist if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_album = "".join(c for c in album if c.isalnum() or c in (' ', '-', '_')).strip()
                filename = f"{safe_artist} - {safe_album} [{best_torrent['media']} {best_torrent['format']}].torrent"
            else:
                # Fallback for group ID only searches
                album_name = group.get('name', f'GroupID-{group_id}')
                safe_album = "".join(c for c in album_name if c.isalnum() or c in (' ', '-', '_')).strip()
                filename = f"{safe_album} [{best_torrent['media']} {best_torrent['format']}].torrent"
            
            await self.download_torrent(best_torrent['id'], filename)
        else:
            print("\n💡 Showing all releases only. Remove --show-all to download best match.")
            print(f"   Best match Torrent ID: {best_torrent['id']}")

        return True

async def main():
    parser = argparse.ArgumentParser(
        description="Download albums with media and encoding preferences",
        epilog="""Examples:
  # Show all releases for Radiohead's OK Computer
  python3 download_album_preferences.py --artist "Radiohead" --album "OK Computer" --show-all
  
  # Download best vinyl V0 version (auto-downloads if found)
  python3 download_album_preferences.py --artist "Radiohead" --album "OK Computer" --prefer-media vinyl --prefer-encoding v0
  
  # Download from specific group ID
  python3 download_album_preferences.py --group-id 12345 --prefer-media cd --prefer-encoding flac
  
  # Just get the most seeded version
  python3 download_album_preferences.py --artist "Radiohead" --album "OK Computer"
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--artist', help='Artist name (use with --album)')
    parser.add_argument('--album', help='Album name (use with --artist)')
    parser.add_argument('--group-id', type=int, help='Direct Orpheus group ID (alternative to artist/album)')
    parser.add_argument('--prefer-media', help='Preferred media type (vinyl, cd, web, etc.)')
    parser.add_argument('--prefer-encoding', help='Preferred encoding (320, v0, flac, etc.)')
    parser.add_argument('--show-all', action='store_true', help='Show all available torrents (no download)')

    # Add helpful aliases for common preferences
    if len(sys.argv) > 1:
        # Convert common aliases
        for i, arg in enumerate(sys.argv):
            if arg == '--prefer-media':
                if i + 1 < len(sys.argv):
                    sys.argv[i + 1] = sys.argv[i + 1].title()  # Convert to title case
            elif arg == '--prefer-encoding':
                if i + 1 < len(sys.argv):
                    # Handle common encoding aliases
                    encoding = sys.argv[i + 1].lower()
                    if encoding in ['vbr', 'v0']:
                        sys.argv[i + 1] = 'v0'
                    elif encoding in ['320', 'mp3']:
                        sys.argv[i + 1] = '320'
                    elif encoding in ['flac', 'lossless']:
                        sys.argv[i + 1] = 'flac'

    args = parser.parse_args()

    async with OrpheusAlbumDownloader() as downloader:
        # Login
        print("🔐 Logging in to Orpheus...")
        if not await downloader.login():
            print("❌ Login failed")
            return

        # Validate arguments
        if not args.group_id and (not args.artist or not args.album):
            print("❌ Either provide --group-id OR both --artist and --album")
            return
        
        if args.group_id and (args.artist or args.album):
            print("❌ Use either --group-id OR --artist/--album, not both")
            return
        
        # Search and download
        await downloader.download_album_with_preferences(
            artist=args.artist,
            album=args.album,
            group_id=args.group_id,
            prefer_media=args.prefer_media,
            prefer_encoding=args.prefer_encoding,
            show_all=args.show_all
        )

if __name__ == "__main__":
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("❌ BeautifulSoup4 is required. Install it with:")
        print("   pip3 install beautifulsoup4")
        sys.exit(1)

    asyncio.run(main())
