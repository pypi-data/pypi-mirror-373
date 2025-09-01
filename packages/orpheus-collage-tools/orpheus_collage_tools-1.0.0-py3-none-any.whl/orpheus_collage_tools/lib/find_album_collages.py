#!/usr/bin/env python3
"""
Find albums with detailed release information and optional collage membership
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
from typing import List, Dict

class OrpheusAlbumSearcher:
    def __init__(self, username: str = None, password: str = None, api_key: str = None):
        # Load credentials from ~/.orpheus-config/config.json if not provided
        if not all([username, password, api_key]):
            config_path = Path.home() / '.orpheus-config' / 'config.json'
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    username = username or config.get('username')
                    password = password or config.get('password')
                    api_key = api_key or config.get('api_key')

        self.username = username
        self.password = password
        self.api_key = api_key
        self.base_url = "https://orpheus.network"
        self.session = None

        # Release type mappings
        self.RELEASE_TYPES = {
            1: 'Album',
            3: 'Soundtrack',
            5: 'EP',
            6: 'Anthology',
            7: 'Compilation',
            8: 'Sampler',
            9: 'Single',
            10: 'Demo',
            11: 'Live album',
            12: 'Split',
            13: 'Remix',
            14: 'Bootleg',
            15: 'Interview',
            16: 'Mixtape',
            21: 'Unknown'
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
            'User-Agent': 'AlbumSearcher/1.0'
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
            print(f"   ⚠️  API error for group {group_id}: {e}")
        return None

    async def get_artist_id(self, artist_name: str) -> int:
        """Search for artist and return their ID"""
        search_url = f"{self.base_url}/artist.php"
        params = {'artistname': artist_name}

        async with self.session.get(search_url, params=params) as response:
            if response.status != 200:
                return None

            # Check if we were redirected to artist page (exact match)
            if 'artist.php?id=' in str(response.url):
                artist_id = re.search(r'id=(\d+)', str(response.url))
                if artist_id:
                    return int(artist_id.group(1))

            # Otherwise, parse the search results
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            # Find first artist link
            artist_link = soup.find('a', href=re.compile(r'artist\.php\?id=\d+'))
            if artist_link:
                artist_id = re.search(r'id=(\d+)', artist_link['href'])
                if artist_id:
                    return int(artist_id.group(1))

        return None

    async def get_artist_releases(self, artist_id: int) -> Dict:
        """Get all releases for an artist using the artist API"""
        url = f"{self.base_url}/ajax.php"
        params = {
            'action': 'artist',
            'id': artist_id
        }

        headers = {
            'Authorization': f'token {self.api_key}',
            'User-Agent': 'AlbumSearcher/1.0'
        }

        try:
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'success':
                        return data['response']
        except Exception as e:
            print(f"   ⚠️  API error for artist {artist_id}: {e}")
        return None

    async def search_albums(self, artist_name: str = None, album_name: str = None) -> List[Dict]:
        """Search for albums - uses artist API for comprehensive results"""
        albums = []

        # If we have an artist name, use the artist API to get ALL releases
        if artist_name and not album_name:
            artist_id = await self.get_artist_id(artist_name)
            if artist_id:
                artist_data = await self.get_artist_releases(artist_id)
                if artist_data:
                    artist_name_actual = artist_data.get('name', artist_name)

                    # Convert torrentgroup format to our album format
                    for group in artist_data.get('torrentgroup', []):
                        album_info = {
                            'group_id': group.get('groupId'),
                            'artist': artist_name_actual,
                            'album': group.get('groupName', 'Unknown'),
                            'year': group.get('groupYear', 0),
                            'releaseType': group.get('releaseType', 21),
                            'vanityHouse': group.get('groupVanityHouse', False),
                            'url': f"{self.base_url}/torrents.php?id={group.get('groupId')}"
                        }
                        albums.append(album_info)

                    return albums

        # Otherwise fall back to search (for album searches or if artist not found)
        search_url = f"{self.base_url}/torrents.php"
        params = {'action': 'advanced'}

        if artist_name:
            params['artistname'] = artist_name
        if album_name:
            params['groupname'] = album_name

        async with self.session.get(search_url, params=params) as response:
            if response.status != 200:
                return []

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            seen_groups = set()

            # Find all torrent group links
            for group_link in soup.find_all('a', href=re.compile(r'torrents\.php\?id=\d+')):
                # Skip if it's a torrent link (has #torrent)
                if '#torrent' in group_link.get('href', ''):
                    continue

                group_id = re.search(r'id=(\d+)', group_link['href'])
                if group_id:
                    gid = int(group_id.group(1))
                    if gid in seen_groups:
                        continue
                    seen_groups.add(gid)

                    # Get the album name (link text)
                    album_text = group_link.text.strip()

                    # Try to find artist name (usually in a nearby link)
                    artist = "Unknown"
                    parent = group_link.parent
                    if parent:
                        artist_link = parent.find('a', href=re.compile(r'artist\.php'))
                        if artist_link:
                            artist = artist_link.text.strip()

                    album_info = {
                        'group_id': gid,
                        'artist': artist,
                        'album': album_text,
                        'url': f"{self.base_url}/torrents.php?id={gid}"
                    }

                    albums.append(album_info)

        return albums

    def sort_albums_by_relevance(self, albums: List[Dict], search_artist: str = None) -> List[Dict]:
        """Sort albums: exact artist matches first, then by compilation status"""

        def get_sort_key(album):
            artist = album['artist'].lower()
            album_name = album['album'].lower()

            # Priority scoring
            priority = 0

            # Highest priority: Exact artist match
            if search_artist:
                search_lower = search_artist.lower()
                if artist == search_lower:
                    priority = 1000  # Exact match
                elif search_lower in artist:
                    priority = 900   # Partial match

            # Penalize "Unknown" artists
            if artist == "unknown":
                priority -= 500

            # Penalize obvious compilations
            compilation_words = ['various', 'compilation', 'best of', 'greatest hits', 'collection', 'anthology', 'mixed by', 'vol.', 'volume']
            if any(word in album_name for word in compilation_words):
                priority -= 300

            # Secondary sort by artist name, then album name
            return (-priority, artist, album_name)

        return sorted(albums, key=get_sort_key)

    async def get_album_collages(self, group_id: int) -> List[Dict]:
        """Get all collages containing this album"""
        album_url = f"{self.base_url}/torrents.php?id={group_id}"

        async with self.session.get(album_url) as response:
            if response.status != 200:
                return []

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            collages = []
            seen_ids = set()

            # Find all collage links on the page
            for link in soup.find_all('a', href=re.compile(r'collages\.php\?id=\d+')):
                # Skip "Add to collage" type links
                if 'add' in link.text.lower() or 'create' in link.text.lower():
                    continue

                collage_id = re.search(r'id=(\d+)', link['href'])
                if collage_id:
                    cid = int(collage_id.group(1))
                    if cid not in seen_ids:
                        seen_ids.add(cid)
                        collages.append({
                            'id': cid,
                            'name': link.text.strip()
                        })

            return collages

    def format_file_size(self, size_bytes: int) -> str:
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def extract_songs_from_filelist(self, file_list: str) -> List[str]:
        """Extract song names from the fileList string"""
        if not file_list:
            return []

        songs = []
        # Split by ||| and look for audio files
        files = file_list.split('|||')
        for file_entry in files:
            # Extract filename (before the {{{size}}})
            filename = file_entry.split('{{{')[0].strip()
            # Check if it's an audio file
            if any(filename.lower().endswith(ext) for ext in ['.mp3', '.flac', '.wav', '.m4a', '.ogg']):
                # Clean up track numbering and file extension
                song_name = re.sub(r'^\d+[\.\-\s]*', '', filename)  # Remove track numbers
                song_name = re.sub(r'\.[^.]+$', '', song_name)      # Remove file extension
                if song_name and song_name not in songs:
                    songs.append(song_name)

        return songs  # Show ALL songs, no limit

    async def display_albums(
        self,
        albums: List[Dict],
        start_idx: int = 0,
        limit: int = 1,
        show_collages: bool = False,
        show_tracks: bool = True
    ) -> int:
        """Display albums with optional interactive pagination"""

        end_idx = min(start_idx + limit, len(albums))

        for i in range(start_idx, end_idx):
            album = albums[i]
            print(f"\n{i + 1}. {album['artist']} — {album['album']}")
            print("═" * 60)

            # Get detailed torrent information (if not already loaded)
            if 'details' in album:
                details = album['details']
            else:
                details = await self.get_torrent_group_details(album['group_id'])

            # Get collages info (cache it in album dict)
            if 'collages' not in album:
                album['collages'] = await self.get_album_collages(album['group_id'])

            if details:
                # Extract basic album info
                group = details.get('group', {})
                year = group.get('year', 0)

                # Show loading line with collage indicator if needed
                collages = album.get('collages', [])
                if collages and not show_collages:
                    loading_msg = "🔄  Loading release details..."
                    collage_indicator = f"! 📚 In {len(collages)} collage(s)...press c to show"
                    # Calculate padding to align properly
                    padding = 60 - len(loading_msg) - len(collage_indicator)
                    print(f"{loading_msg}{' ' * padding}{collage_indicator}")
                else:
                    print("🔄  Loading release details...")

                if year > 0:
                    print(f"📅  Year: {year}")

                # Store release type and vanity house status for filtering
                album['releaseType'] = group.get('releaseType', 21)  # 21 = Unknown
                album['vanityHouse'] = group.get('vanityHouse', False)

                # Show available releases/torrents
                torrents = details.get('torrents', [])
                if torrents:
                    print(f"💿  Available Releases ({len(torrents)}):")
                    print()

                    # Store torrent info for potential download
                    album['torrents'] = torrents
                    album['year'] = year

                    # Group by RELEASE (not format) - each release gets different formats
                    release_groups = {}
                    for torrent in torrents:
                        # Create release key from remaster info + media
                        remaster_year = torrent.get('remasterYear', year) or year
                        remaster_title = torrent.get('remasterTitle', '') or ''
                        remaster_label = torrent.get('remasterRecordLabel', '') or ''
                        remaster_catalog = torrent.get('remasterCatalogueNumber', '') or ''
                        media = torrent.get('media', '')

                        # Create unique release identifier
                        release_key = f"{remaster_year}|{remaster_title}|{remaster_label}|{remaster_catalog}|{media}"

                        if release_key not in release_groups:
                            release_groups[release_key] = {
                                'year': remaster_year,
                                'title': remaster_title,
                                'label': remaster_label,
                                'catalog': remaster_catalog,
                                'media': media,
                                'torrents': []
                            }
                        release_groups[release_key]['torrents'].append(torrent)

                    # Display each RELEASE with its available formats
                    release_letter = 'a'
                    for release_key, release_data in release_groups.items():
                        # Build release description
                        release_parts = [str(release_data['year'])]
                        if release_data['title']:
                            release_parts.append(release_data['title'])
                        if release_data['label']:
                            release_parts.append(release_data['label'])
                        if release_data['catalog']:
                            release_parts.append(release_data['catalog'])
                        if release_data['media']:
                            release_parts.append(release_data['media'])

                        release_desc = " | ".join(release_parts)
                        print(f"   • Release {release_letter.upper()}: {release_desc}")

                        # Show formats available for this release
                        format_number = 1
                        for torrent in release_data['torrents']:
                            format_str = f"{torrent.get('format', 'Unknown')} {torrent.get('encoding', '')}".strip()
                            size = self.format_file_size(torrent.get('size', 0))
                            seeders = torrent.get('seeders', 0)

                            # Create selection index (a1, a2, b1, b2, etc.)
                            selection_id = f"{release_letter}{format_number}"
                            torrent['display_index'] = selection_id

                            # Pad format string to fixed width for alignment
                            format_str_padded = format_str.ljust(20)
                            size_str = size.rjust(10)
                            print(f"     [{selection_id}] {format_str_padded} | {size_str} | {seeders:3d} seeders")
                            format_number += 1

                        # Move to next release letter
                        release_letter = chr(ord(release_letter) + 1)

                # Show collages if requested
                if show_collages and collages:
                    print("═" * 60)
                    print(f"📚  In {len(collages)} collage(s):")
                    for collage in collages:
                        print(f"   - [{collage['id']}] {collage['name']}")

                # Show sample songs if available
                if torrents and torrents[0].get('fileList'):
                    songs = self.extract_songs_from_filelist(torrents[0]['fileList'])
                    if songs:
                        print("═" * 60)
                        print(f"🎵  TRACKLIST ({len(songs)} tracks):", end="")
                        if show_tracks:
                            print()
                            for j, song in enumerate(songs, 1):
                                print(f"   {j:2d}. {song}")
                        else:
                            print(" Press 't' to view")

        print("═" * 60)
        return end_idx

    async def interactive_search(self, albums: List[Dict], show_collages: bool = False, page_size: int = 1):
        """Interactive album browsing with pagination and download options"""
        current_idx = 0
        current_filter = None  # Track if we're filtering by specific release type
        filtered_albums = albums.copy()  # Working copy of albums
        show_tracks = False  # Track if we should show tracks for current album
        show_collages_toggle = False  # Track if we should show collages for current album

        while current_idx < len(filtered_albums):
            # Count available release types in current album set
            release_type_counts = {}
            # Use the original full album list for counts, not the filtered one
            for album in albums:
                rt = album.get('releaseType', 21)
                if rt in self.RELEASE_TYPES:
                    release_type_counts[rt] = release_type_counts.get(rt, 0) + 1

            # Clear screen effect with newline
            print("\n" + "="*60)

            # Show current filter status at the top
            if current_filter:
                print(f"🎯  Filtering: {self.RELEASE_TYPES[current_filter]}s only")
            else:
                print("🔄  Showing all release types")
            print("="*60)

            # Show available release type filters at the TOP (compact format)
            if len(release_type_counts) > 1 or current_filter:
                print("\n🎵 Filter by Release Type:")
                print("-" * 60)

                # Build filter options in a compact format
                filter_options = []
                if current_filter:
                    filter_options.append("a = Show all")

                for rt, count in sorted(release_type_counts.items()):
                    if rt != current_filter:  # Don't show current filter as option
                        filter_options.append(f"{rt} = {self.RELEASE_TYPES[rt]}s ({count})")

                # Display 3 options per line
                for i in range(0, len(filter_options), 3):
                    line_options = filter_options[i:i+3]
                    print("  " + " | ".join(line_options))

                print("=" * 60)

            # Display current page with optional track display
            next_idx = await self.display_albums(filtered_albums, current_idx, page_size, show_collages_toggle, show_tracks)

            # Show pagination info
            remaining = len(filtered_albums) - next_idx
            print(f"\n👋  Showing {next_idx} of {len(filtered_albums)} releases ({remaining} remaining)")
            print("-" * 60)

            print("\n🎯 Options:")

            # Check if current album has collages
            current_album = filtered_albums[current_idx] if current_idx < len(filtered_albums) else None
            has_collages = current_album and current_album.get('collages', [])

            # Build compact options in new format
            line1_options = []
            line2_options = []
            line3_options = []

            # Line 1: n, t, q
            if remaining > 0:
                line1_options.append("n = Next release")
            if show_tracks:
                line1_options.append("t = Hide tracks") 
            else:
                line1_options.append("t = Show tracks")
            line1_options.append("q = Quit")

            # Line 2: d, c
            line2_options.append("d <#> <fmt> = Download (e.g. 'd 1 a2')")
            if has_collages:
                if show_collages_toggle:
                    line2_options.append("c = Hide collages")
                else:
                    line2_options.append("c = Show collages")
            else:
                line2_options.append("c = Show collages")

            # Line 3: s, h
            line3_options.append(f"s <#> = Jump to page # of {len(filtered_albums)}")
            line3_options.append("h = Home (main menu)")

            # Print compact format with better spacing
            print("   " + "  |  ".join(line1_options))
            print("   " + "  |  ".join(line2_options))
            print("   " + "  |  ".join(line3_options))


            try:
                choice = input("\n> ").strip().lower()

                if choice == 'q':
                    print("👋 Goodbye!")
                    break
                elif choice == 'n' or (choice == '' and remaining > 0):
                    current_idx = next_idx
                    show_tracks = False  # Reset track display for next album
                    show_collages_toggle = False  # Reset collage display
                    continue
                elif choice == 't':
                    show_tracks = not show_tracks
                    continue  # Redisplay current album with/without tracks
                elif choice == 'c' and has_collages:
                    show_collages_toggle = not show_collages_toggle
                    continue  # Redisplay current album with/without collages
                elif choice == 'h':
                    # Return to main menu
                    print("🏠 Returning to main menu...")
                    return 'MAIN_MENU'
                elif choice == 'a' and current_filter:
                    # Reset to show all
                    filtered_albums = albums.copy()
                    current_filter = None
                    current_idx = 0
                    show_tracks = False
                    show_collages_toggle = False
                    continue
                elif choice.isdigit() and int(choice) in release_type_counts:
                    # Filter by release type
                    rt = int(choice)
                    filtered_albums = [a for a in albums if a.get('releaseType', 21) == rt]
                    current_filter = rt
                    current_idx = 0
                    show_tracks = False
                    show_collages_toggle = False
                    continue
                elif choice.startswith('s '):
                    # Skip to page command
                    parts = choice.split()
                    if len(parts) == 2:
                        try:
                            page_num = int(parts[1])
                            if 1 <= page_num <= len(filtered_albums):
                                current_idx = page_num - 1
                                show_tracks = False
                                show_collages_toggle = False
                                continue
                            else:
                                print(f"❌ Page number must be between 1 and {len(filtered_albums)}")
                        except ValueError:
                            print("❌ Invalid page number! Use: s <number>")
                    else:
                        print("❌ Invalid format! Use: s <number> (e.g., 's 150')")
                elif choice.startswith('d '):
                    # Parse download command: d [album_num] [release_format]
                    parts = choice.split()
                    if len(parts) == 3:
                        try:
                            album_num = int(parts[1]) - 1  # Convert to 0-based
                            release_format = parts[2].lower()  # e.g., "a1", "b2"

                            if 0 <= album_num < len(filtered_albums):
                                album = filtered_albums[album_num]
                                if 'torrents' in album:
                                    # Find torrent by display index (a1, b2, etc.)
                                    target_torrent = None
                                    for torrent in album['torrents']:
                                        if torrent.get('display_index') == release_format:
                                            target_torrent = torrent
                                            break
                                    if target_torrent:
                                        # Clear screen and show download progress
                                        print("\n" + "="*60)
                                        print("⬇️  DOWNLOADING TORRENT")
                                        print("="*60)
                                        
                                        await self.download_single_torrent(album, target_torrent)
                                        
                                        # Show download summary
                                        print("\n" + "="*60)
                                        print("✅ DOWNLOAD COMPLETE")
                                        print("="*60)
                                        print(f"📁 Release: {album['artist']} - {album['album']}")
                                        print(f"🎵 Format: {target_torrent.get('format', '')} {target_torrent.get('encoding', '')}")
                                        print(f"💾 Size: {self.format_file_size(target_torrent.get('size', 0))}")
                                        print(f"🌱 Seeders: {target_torrent.get('seeders', 0)}")
                                        print("\n💡 Next steps:")
                                        print("   • Load the .torrent file in your torrent client")
                                        print("   • The file is saved in your Documents/Orpheus folder")
                                        print("   • Press Enter to continue browsing...")
                                        
                                        # Wait for user to acknowledge
                                        input()
                                        
                                        # Return to album display
                                        continue
                                    else:
                                        print(f"❌ Release format '{release_format}' not found!")
                                else:
                                    print(f"❌ No torrent data available for release #{album_num + 1}")
                            else:
                                print(f"❌ Release #{album_num + 1} not found!")
                        except ValueError:
                            print("❌ Invalid format! Use: d <#> <fmt> (e.g., 'd 1 a2')")
                    else:
                        print("❌ Invalid format! Use: d <#> <fmt> (e.g., 'd 1 a2')")
                else:
                    print("❌ Invalid choice. Use 'n' for next, 't' for tracks, 'c' for collages, 'd <#> <fmt>' to download, 's <#>' to skip to page, 'h' for home, or a number to filter.")
                    continue
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break

    async def download_single_torrent(self, album: Dict, torrent: Dict):
        """Download a specific torrent file"""
        try:
            torrent_id = torrent.get('id')
            if not torrent_id:
                print("❌ No torrent ID found!")
                return
            # Build download URL
            download_url = f"{self.base_url}/torrents.php"
            params = {
                'action': 'download',
                'id': torrent_id
            }

            print(f"\n⬇️ Downloading torrent...")
            print(f"   Release: {album['artist']} - {album['album']} ({album.get('year', 'Unknown')})")
            print(f"   Format: {torrent.get('media', '')} | {torrent.get('format', '')} {torrent.get('encoding', '')}")
            print(f"   Size: {self.format_file_size(torrent.get('size', 0))}")

            async with self.session.get(download_url, params=params) as response:
                if response.status == 200:
                    # Create filename
                    safe_artist = "".join(c for c in album['artist'] if c.isalnum() or c in (' ', '-', '_')).strip()
                    safe_album = "".join(c for c in album['album'] if c.isalnum() or c in (' ', '-', '_')).strip()
                    filename = f"{safe_artist} - {safe_album} [{torrent.get('format', 'Unknown')}].torrent"

                    # Save torrent file
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
                    # If background downloading is enabled, add to torrent manager
                    # Background downloading removed
                    try:
                        import sys
                        sys.path.append(str(Path(__file__).parent))


                        album_info = {
                            'artist': album['artist'],
                            'album': album['album'],
                            'year': album.get('year')
                        }

                        print("💡 Load the torrent file in your preferred torrent client")

                    except Exception as e:
                        print(f"⚠️  Background download setup failed: {e}")
                        print("   You can manually load the torrent file in your client")

                else:
                    print(f"❌ Download failed! Status: {response.status}")

        except Exception as e:
            print(f"❌ Download error: {e}")

async def main(args_list=None):
    parser = argparse.ArgumentParser(description="Search for albums with detailed release information")
    parser.add_argument('--artist', help='Artist name to search for')
    parser.add_argument('--album', help='Album name to search for')
    parser.add_argument('--show-collages', action='store_true', help='Show collage membership (default: hidden)')
    parser.add_argument('--official-only', action='store_true', help='Show only official releases (skip compilations)')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive pagination mode')
    parser.add_argument('--limit', type=int, default=10, help='Number of results to show (default: 10)')

    parser.add_argument('--all', action='store_true', help='Show all results')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')

    if args_list is not None:
        args = parser.parse_args(args_list)
    else:
        args = parser.parse_args()

    if not args.artist and not args.album:
        parser.print_help()
        print("\nExample usage:")
        print('  ./collage_tools find-album --artist "The Prodigy"')
        print('  ./collage_tools find-album --artist "The Prodigy" --official-only')
        print('  ./collage_tools find-album --artist "The Prodigy" --interactive')
        print('  ./collage_tools find-album --artist "The Prodigy" --show-collages')
        return

    async with OrpheusAlbumSearcher() as searcher:
        # Login
        print("🔐 Logging in to Orpheus...")
        if not await searcher.login():
            print("❌ Login failed")
            return

        # Search for albums
        print(f"\n🔍 Searching for {'all releases' if not args.official_only else 'official releases'} by {args.artist}...")
        albums = await searcher.search_albums(args.artist, args.album)

        if not albums:
            print("❌ No releases found")
            return

        # Sort albums by relevance
        print(f"\n📊 Sorting {len(albums)} releases...")
        sorted_albums = searcher.sort_albums_by_relevance(albums, args.artist)

        # Fetch details for all albums to enable proper filtering
        # (Skip if we already have releaseType from artist API)
        for album in sorted_albums:
            if 'releaseType' not in album:
                details = await searcher.get_torrent_group_details(album['group_id'])
                if details:
                    group = details.get('group', {})
                    album['releaseType'] = group.get('releaseType', 21)
                    album['vanityHouse'] = group.get('vanityHouse', False)
                    album['year'] = group.get('year', 0)
                    album['details'] = details

        # Filter for official releases only if requested
        if args.official_only:
            # Define official release types: Album, Soundtrack, EP, Anthology, Single, Demo, Live album, Split
            OFFICIAL_RELEASE_TYPES = [1, 3, 5, 6, 9, 10, 11, 12]
            original_count = len(sorted_albums)

            sorted_albums = [
                album for album in sorted_albums
                if album.get('releaseType', 21) in OFFICIAL_RELEASE_TYPES
                and not album.get('vanityHouse', False)
            ]

            # Sort by priority release types, then by year (newest to oldest)
            # Priority 1: Albums, EPs, Singles, Live albums (all mixed, sorted by year)
            # Priority 2: Soundtracks, Anthologies, Demos, Splits (all mixed, sorted by year)
            PRIORITY_RELEASE_TYPES = [1, 5, 9, 11]  # Album, EP, Single, Live album
            SECONDARY_RELEASE_TYPES = [3, 6, 10, 12]  # Soundtrack, Anthology, Demo, Split

            priority_albums = []
            secondary_albums = []

            for album in sorted_albums:
                if album.get('releaseType', 21) in PRIORITY_RELEASE_TYPES:
                    priority_albums.append(album)
                else:
                    secondary_albums.append(album)

            # Sort each group by year only (newest to oldest)
            priority_albums.sort(key=lambda x: x.get('year', 0), reverse=True)
            secondary_albums.sort(key=lambda x: x.get('year', 0), reverse=True)

            # Combine: priority releases first, then secondary
            sorted_albums = priority_albums + secondary_albums

            print(f"📋 Filtered to {len(sorted_albums)} official releases (from {original_count} total)")
        else:
            # For "All albums", just sort by year (newest to oldest)
            sorted_albums.sort(key=lambda x: x.get('year', 0), reverse=True)
            print(f"📋 Found {len(sorted_albums)} total releases")

        if not sorted_albums:
            if args.json:
                return json.dumps([])
            print("❌ No releases found after filtering")
            return None

        print(f"\n✅ Found {len(sorted_albums)} release(s)")

        if args.json:
            return json.dumps(sorted_albums, indent=2, default=str)

        # Interactive mode or batch display
        if args.interactive:
            result = await searcher.interactive_search(sorted_albums, args.show_collages, page_size=1)
            if result == 'MAIN_MENU':
                return 'MAIN_MENU'
        else:
            # Non-interactive display
            if args.all:
                limit = len(sorted_albums)
            else:
                limit = min(args.limit, len(sorted_albums))

            await searcher.display_albums(sorted_albums, 0, limit, args.show_collages)

            # Show pagination options for non-interactive mode
            if len(sorted_albums) > limit:
                remaining = len(sorted_albums) - limit
                print(f"\n📄 Showing {limit} of {len(sorted_albums)} albums ({remaining} remaining)")
                print(f"   Use --all to see all results")
                print(f"   Use --interactive for page-by-page browsing")
                print(f"   Use --limit {limit + 10} to see more")
            return None

if __name__ == "__main__":
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("❌ BeautifulSoup4 is required. Install it with:")
        print("   pip3 install beautifulsoup4")
        sys.exit(1)

    result = asyncio.run(main())
    if result == 'MAIN_MENU':
        sys.exit(2)  # Special exit code for returning to main menu
    elif result:
        print(result)
