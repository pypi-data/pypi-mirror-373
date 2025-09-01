#!/usr/bin/env python3
"""
Search for collages that contain albums by a specific artist
Enhanced implementation based on Gazelle source code analysis
"""

import asyncio
import json
import re
import argparse
import sys
import subprocess
from pathlib import Path
import aiohttp
import ssl
from bs4 import BeautifulSoup
from typing import List, Dict, Set, Optional
from collections import defaultdict
import time

class CollageArtistSearcher:
    def __init__(self, username: str = None, password: str = None, api_key: str = None):
        # Load credentials from ~/.orpheus/config.json if not provided
        if not all([username, password, api_key]):
            config_path = Path.home() / '.orpheus' / 'config.json'
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
        self.request_delay = 1.0  # Delay between requests to avoid rate limiting
        self.max_concurrent_requests = 5  # Limit concurrent requests

    async def __aenter__(self):
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        connector = aiohttp.TCPConnector(ssl=ssl_context, limit=self.max_concurrent_requests)
        self.session = aiohttp.ClientSession(connector=connector)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def login(self) -> bool:
        """Login to Orpheus website using session-based authentication"""
        login_url = f"{self.base_url}/login.php"

        login_data = {
            'username': self.username,
            'password': self.password,
            'keeplogged': '1',
            'login': 'Log in'
        }

        try:
            async with self.session.post(login_url, data=login_data, allow_redirects=False) as response:
                if 'session' in response.cookies or response.status in [302, 303]:
                    print("✅ Web login successful")
                    return True
        except Exception as e:
            print(f"❌ Login error: {e}")
        return False

    async def get_artist_id(self, artist_name: str) -> Optional[int]:
        """Search for artist and return their ID using web scraping"""
        search_url = f"{self.base_url}/artist.php"
        params = {'artistname': artist_name}

        try:
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

        except Exception as e:
            print(f"   ⚠️  Artist search error: {e}")
        return None

    async def get_artist_releases(self, artist_id: int) -> Optional[Dict]:
        """Get all releases for an artist using the API (preferred method)"""
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
                        artist_data = data['response']
                        
                        # Filter out compilations (releaseType 7) to reduce search scope
                        original_count = len(artist_data.get('torrentgroup', []))
                        filtered_groups = [
                            group for group in artist_data.get('torrentgroup', [])
                            if group.get('releaseType') != 7  # 7 = Compilation
                        ]
                        artist_data['torrentgroup'] = filtered_groups
                        
                        if original_count != len(filtered_groups):
                            print(f"   📊 Filtered out {original_count - len(filtered_groups)} compilations")
                        
                        return artist_data
        except Exception as e:
            print(f"   ⚠️  API error for artist {artist_id}: {e}")

        # Fallback to web scraping if API fails
        print("   🔄 API failed, falling back to web scraping...")
        return await self._get_artist_releases_web(artist_id)

    async def _get_artist_releases_web(self, artist_id: int) -> Optional[Dict]:
        """Fallback method to get artist releases via web scraping"""
        artist_url = f"{self.base_url}/artist.php?id={artist_id}"

        try:
            async with self.session.get(artist_url) as response:
                if response.status != 200:
                    return None

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                # Parse torrent groups from the page
                torrent_groups = []
                group_rows = soup.find_all('tr', class_=re.compile(r'group'))

                for row in group_rows:
                    # Extract group information
                    group_link = row.find('a', href=re.compile(r'torrents\.php\?id=\d+'))
                    if group_link:
                        group_id_match = re.search(r'id=(\d+)', group_link['href'])
                        if group_id_match:
                            group_id = int(group_id_match.group(1))
                            group_name = group_link.text.strip()

                            # Extract year
                            year_elem = row.find('td', class_='year')
                            year = 0
                            if year_elem:
                                year_text = year_elem.text.strip()
                                year_match = re.search(r'\b(19|20)\d{2}\b', year_text)
                                if year_match:
                                    year = int(year_match.group(0))

                            # Extract release type from the row
                            release_type = 1  # Default to Album
                            type_elem = row.find('td', class_='type')
                            if type_elem:
                                type_text = type_elem.text.strip().lower()
                                # Map common types to release type numbers
                                if 'compilation' in type_text:
                                    release_type = 7
                                elif 'album' in type_text:
                                    release_type = 1
                                elif 'ep' in type_text:
                                    release_type = 5
                                elif 'single' in type_text:
                                    release_type = 9
                                elif 'soundtrack' in type_text:
                                    release_type = 3

                            # Skip compilations
                            if release_type == 7:
                                continue

                            torrent_groups.append({
                                'groupId': group_id,
                                'groupName': group_name,
                                'groupYear': year,
                                'groupRecordLabel': '',
                                'groupCatalogueNumber': '',
                                'tags': [],
                                'releaseType': release_type,
                                'groupVanityHouse': False,
                                'hasBookmarked': False,
                                'torrent': []  # Will be populated if needed
                            })

                return {
                    'id': artist_id,
                    'name': '',  # Would need to extract from page title
                    'torrentgroup': torrent_groups
                }

        except Exception as e:
            print(f"   ⚠️  Web scraping error for artist {artist_id}: {e}")
        return None

    async def get_album_collages(self, group_id: int) -> List[Dict]:
        """Get all collages containing this album using web scraping"""
        album_url = f"{self.base_url}/torrents.php?id={group_id}"

        try:
            async with self.session.get(album_url) as response:
                if response.status != 200:
                    return []

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                collages = []
                seen_ids = set()

                # Find all collage links on the page
                # Look for links containing "collages.php?id="
                for link in soup.find_all('a', href=re.compile(r'collages\.php\?id=\d+')):
                    # Skip "Add to collage" type links
                    link_text = link.text.strip().lower()
                    if any(skip_word in link_text for skip_word in ['add', 'create', 'new', 'manage']):
                        continue

                    collage_id_match = re.search(r'id=(\d+)', link['href'])
                    if collage_id_match:
                        cid = int(collage_id_match.group(1))
                        if cid not in seen_ids:
                            seen_ids.add(cid)

                            # Get collage name from link text or title attribute
                            collage_name = link.text.strip()
                            if not collage_name:
                                collage_name = link.get('title', f'Collage {cid}')

                            collages.append({
                                'id': cid,
                                'name': collage_name
                            })

                # Rate limiting delay
                await asyncio.sleep(self.request_delay)

                return collages

        except Exception as e:
            print(f"   ⚠️  Error getting collages for album {group_id}: {e}")
            return []

    async def get_collage_details(self, collage_id: int) -> Optional[Dict]:
        """Get detailed information about a collage using the API"""
        url = f"{self.base_url}/ajax.php"
        params = {
            'action': 'collage',
            'id': collage_id
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
            print(f"   ⚠️  Error getting collage {collage_id} details: {e}")
        return None

    async def search_collages_by_artist(self, artist_name: str) -> Dict:
        """Search for all collages that contain albums by the specified artist"""
        print(f"🔍 Finding artist ID for '{artist_name}'...")
        artist_id = await self.get_artist_id(artist_name)

        if not artist_id:
            return {'error': f"Could not find artist '{artist_name}'"}

        print(f"✅ Found artist ID: {artist_id}")
        print(f"📀 Getting all releases by {artist_name}...")

        artist_data = await self.get_artist_releases(artist_id)
        if not artist_data:
            return {'error': f"Could not get releases for artist '{artist_name}'"}

        albums = artist_data.get('torrentgroup', [])
        print(f"🎵 Found {len(albums)} releases by {artist_name}")

        if not albums:
            return {'error': f"No releases found for artist '{artist_name}'"}

        # Collect all collages
        all_collages = {}
        album_collage_count = defaultdict(int)

        print(f"🔍 Searching for collages containing {artist_name}'s albums...")
        print("   This may take a moment...")

        # Process albums in batches to avoid overwhelming the server
        batch_size = 10
        bar_length = 30
        total_albums = len(albums)
        
        for i in range(0, len(albums), batch_size):
            batch = albums[i:i + batch_size]
            progress = min(i + batch_size, len(albums))
            percentage = int((progress / total_albums) * 100)
            
            # Create visual progress bar
            filled_length = int((progress / total_albums) * bar_length)
            filled = "█" * filled_length
            empty = "░" * (bar_length - filled_length)
            
            # Print progress bar (overwrite previous line)
            print(f"\r\033[1;32m[{filled}{empty}]\033[0m {percentage:3d}% ({progress}/{total_albums} albums checked)", end="", flush=True)

            # Process batch concurrently
            tasks = []
            for album in batch:
                group_id = album.get('groupId')
                if group_id:
                    tasks.append(self.get_album_collages(group_id))

            # Wait for all tasks in this batch to complete
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    print(f"   ⚠️  Error processing album {batch[j].get('groupId')}: {result}")
                    continue

                album = batch[j]
                collages = result

                for collage in collages:
                    collage_id = collage['id']
                    if collage_id not in all_collages:
                        all_collages[collage_id] = {
                            'id': collage_id,
                            'name': collage['name'],
                            'albums': [],
                            'details': None  # Will be populated later if needed
                        }

                    all_collages[collage_id]['albums'].append({
                        'name': album.get('groupName', 'Unknown'),
                        'year': album.get('groupYear', 0),
                        'id': album.get('groupId')
                    })
                    album_collage_count[collage_id] += 1

        # Print newline after progress bar completes
        print()

        print(f"\n📊 Sorting {len(albums)} releases...")
        sorted_collages = sorted(
            all_collages.values(),
            key=lambda x: len(x['albums']),
            reverse=True
        )

        result = {
            'artist': artist_name,
            'artist_id': artist_id,
            'total_albums': len(albums),
            'total_collages': len(sorted_collages),
            'collages': sorted_collages
        }

        print(f"\n✅ Found {len(sorted_collages)} collage(s)")

        return result

    async def display_collages(
        self,
        collages: List[Dict],
        start_idx: int = 0,
        limit: int = 1,
        show_details: bool = False,
        searched_artist: str = ""
    ) -> int:
        """Display collages with optional interactive pagination"""

        end_idx = min(start_idx + limit, len(collages))

        for i in range(start_idx, end_idx):
            collage = collages[i]
            print(f"\n{i + 1}. 📚 {collage['name']}")
            print("═" * 60)

            # Get detailed collage information (if not already loaded)
            if 'details' in collage:
                details = collage['details']
            else:
                details = await self.get_collage_details(collage['id'])

            if details:
                # Extract basic collage info
                collage_info = details.get('collage', {})
                description = collage_info.get('description', '')
                creator = collage_info.get('username', 'Unknown')
                subscribers = collage_info.get('subscribers', 0)
                torrents = details.get('torrents', [])

                print("🔄  Loading collage details...")

                if description:
                    # Truncate long descriptions
                    desc = description[:100] + "..." if len(description) > 100 else description
                    print(f"📝  {desc}")

                print(f"👤  Created by: {creator}")
                print(f"👥  Subscribers: {subscribers}")

                # Show albums by searched artist vs total in collage
                albums_by_artist = len(collage.get('albums', []))
                total_albums = len(torrents)
                print(f"💿  {albums_by_artist} {searched_artist} albums (of {total_albums} total in collage)")

                # Store torrent info for potential download
                collage['torrents'] = torrents
                collage['creator'] = creator
                collage['subscribers'] = subscribers
                collage['description'] = description

            # Show albums in this collage
            albums = collage.get('albums', [])
            if albums:
                print(f"🎵  {searched_artist} albums in this collage:")
                print()

                if show_details:
                    # Show all albums with artist name
                    for j, album in enumerate(albums, 1):
                        year = album.get('year', 0)
                        year_str = f" ({year})" if year > 0 else ""
                        print(f"   {j:2d}. {searched_artist} — {album.get('name', 'Unknown')}{year_str}")
                else:
                    # Show first few albums with artist name
                    max_show = min(5, len(albums))
                    for j, album in enumerate(albums[:max_show], 1):
                        year = album.get('year', 0)
                        year_str = f" ({year})" if year > 0 else ""
                        print(f"   {j:2d}. {searched_artist} — {album.get('name', 'Unknown')}{year_str}")

                    if len(albums) > max_show:
                        remaining = len(albums) - max_show
                        print(f"   ... and {remaining} more {searched_artist} album(s)")

            print(f"🔗  https://orpheus.network/collages.php?id={collage['id']}")

        print("═" * 60)
        return end_idx

    async def interactive_search(self, collages: List[Dict], page_size: int = 1, searched_artist: str = ""):
        """Interactive collage browsing with pagination and download options"""
        current_idx = 0
        show_details = False  # Track if we should show all albums

        while current_idx < len(collages):
            # Clear screen effect with newline
            print("\n" + "="*60)

            # Display current page
            next_idx = await self.display_collages(collages, current_idx, page_size, show_details, searched_artist)

            # Show pagination info
            remaining = len(collages) - next_idx
            print(f"\n👋  Showing {next_idx} of {len(collages)} collages ({remaining} remaining)")
            print("-" * 60)

            print("\n🎯 Options:")

            # Build compact options
            line1_options = []
            line2_options = []

            # Line 1: n, d, q
            if remaining > 0:
                line1_options.append("n = Next collage")
            line1_options.append("d = Download this collage")
            line1_options.append("q = Quit")

            # Line 2: c, s
            if show_details:
                line2_options.append("c = Hide album details")
            else:
                line2_options.append("c = Show all albums")
            line2_options.append(f"s <#> = Jump to page # of {len(collages)}")

            # Print compact format
            print("   " + "  |  ".join(line1_options))
            print("   " + "  |  ".join(line2_options))

            try:
                choice = input("\n> ").strip().lower()

                if choice == 'q':
                    print("👋 Goodbye!")
                    break
                elif choice == 'n' or (choice == '' and remaining > 0):
                    current_idx = next_idx
                    show_details = False  # Reset details view for next collage
                    continue
                elif choice == 'c':
                    show_details = not show_details
                    continue  # Redisplay current collage with/without details
                elif choice == 's':
                    # Skip to page command
                    parts = choice.split()
                    if len(parts) == 2:
                        try:
                            page_num = int(parts[1])
                            if 1 <= page_num <= len(collages):
                                current_idx = page_num - 1
                                show_details = False
                                continue
                            else:
                                print(f"❌ Page number must be between 1 and {len(collages)}")
                        except ValueError:
                            print("❌ Invalid page number! Use: s <number>")
                    else:
                        print("❌ Invalid format! Use: s <number> (e.g., 's 5')")
                elif choice == 'd':
                    # Download this collage
                    collage = collages[current_idx]
                    await self.download_collage_torrents(collage, searched_artist)
                    continue  # Return to collage display
                else:
                    print("❌ Invalid choice. Use 'n' for next, 'c' for details, 'd' to download, 's <#>' to skip to page, 'q' to quit.")
                    continue
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break

    async def download_collage_torrents(self, collage: Dict, searched_artist: str = ""):
        """Download all torrents from a collage"""
        try:
            collage_id = collage['id']
            collage_name = collage['name']

            # Clear screen and show download progress
            print("\n" + "="*60)
            print("⬇️  DOWNLOADING COLLAGE TORRENTS")
            print("="*60)

            print(f"📚 Collage: {collage_name}")
            print(f"🆔 ID: {collage_id}")
            albums_by_artist = len(collage.get('albums', []))
            print(f"💿 Contains {albums_by_artist} {searched_artist} albums")

            # Ask for download preferences
            print("\n🎵 Choose download format:")
            print("1. MP3 320 CBR     (High quality, universal compatibility)")
            print("2. MP3 V0 VBR      (Excellent quality, smaller files)")
            print("3. FLAC Lossless   (Perfect quality, largest files)")
            print("")

            while True:
                try:
                    format_choice = input("Choose option (1-3): ").strip()
                    if format_choice == '1':
                        prefer = "--prefer-320"
                        format_name = "MP3 320 CBR"
                        break
                    elif format_choice == '2':
                        prefer = "--prefer-v0"
                        format_name = "MP3 V0 VBR"
                        break
                    elif format_choice == '3':
                        prefer = "--prefer-flac"
                        format_name = "FLAC Lossless"
                        break
                    else:
                        print("❌ Invalid choice! Please choose 1, 2, or 3.")
                except KeyboardInterrupt:
                    print("\n👋 Download cancelled")
                    return

            print(f"\n⬇️ Starting download of collage ID: {collage_id}")
            print(f"🎵 Preferred format: {format_name}")
            print("")

            # Import and run the download script
            try:
                import subprocess
                import sys
                result = subprocess.run([
                    sys.executable,
                    "/Users/cameronbrooks/.orpheus/lib/download_collage_torrents.py",
                    str(collage_id),
                    prefer
                ], cwd="/Users/cameronbrooks/.orpheus/lib")

                if result.returncode == 0:
                    print("\n✅ Download completed successfully!")
                else:
                    print(f"\n❌ Download failed with exit code: {result.returncode}")

            except Exception as e:
                print(f"\n❌ Download error: {e}")

            print("\n💡 Press Enter to continue browsing collages...")
            input()

        except Exception as e:
            print(f"❌ Download error: {e}")

    async def display_results(self, results: Dict):
        """Display the search results in an interactive format"""
        if 'error' in results:
            print(f"❌ Error: {results['error']}")
            return

        artist = results['artist']
        total_collages = results['total_collages']
        total_albums = results['total_albums']
        collages = results['collages']

        print(f"\n🎵 COLLAGES FEATURING '{artist.upper()}'")
        print("=" * 60)
        print(f"📊 Found {total_collages} collage(s) containing {total_albums} of {artist}'s albums")
        print("=" * 60)

        if not collages:
            print(f"❌ No collages found containing {artist}'s albums")
            return

        # Use the new interactive search method
        await self.interactive_search(collages, page_size=1, searched_artist=artist)

        print(f"\n" + "=" * 60)
        print("💡 Use './collage_tools download {collages[0]['id']} --prefer-320' to download the first collage")
        print("💡 Use './collage_tools 3b' to search collages by name instead")


async def main():
    parser = argparse.ArgumentParser(description="Search for collages containing albums by a specific artist")
    parser.add_argument('artist', help='Artist name to search for')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')

    args = parser.parse_args()

    async with CollageArtistSearcher() as searcher:
        print("🔐 Logging in to Orpheus...")
        if not await searcher.login():
            print("❌ Login failed")
            return

        results = await searcher.search_collages_by_artist(args.artist)

        if args.json:
            print(json.dumps(results, indent=2, default=str))
        else:
            await searcher.display_results(results)


if __name__ == "__main__":
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("❌ BeautifulSoup4 is required. Install it with:")
        print("   pip3 install beautifulsoup4")
        sys.exit(1)

    asyncio.run(main())