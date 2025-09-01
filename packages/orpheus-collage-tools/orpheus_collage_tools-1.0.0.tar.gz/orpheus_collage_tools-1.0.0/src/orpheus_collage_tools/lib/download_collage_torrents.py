#!/usr/bin/env python3
"""
Download all torrent files from an Orpheus collage
"""

import asyncio
import json
import argparse
import os
import sys
from pathlib import Path
import aiohttp
import ssl
from typing import List, Dict

class OrpheusCollageDownloader:
    def __init__(self, api_key: str = None):
        # Load API key from config if not provided
        if not api_key:
            config_path = Path.home() / '.orpheus' / 'config.json'
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    api_key = config.get('api_key')
            else:
                raise ValueError("No API key provided and config file not found. Please provide an API key or create ~/.orpheus/config.json")

        if not api_key:
            raise ValueError("API key is required. Please provide an API key or ensure it's in the config file")
        
        self.api_key = api_key
        self.base_url = "https://orpheus.network"
        self.session = None
        
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
    
    async def get_collage_info(self, collage_id: int) -> Dict:
        """Get basic collage information"""
        url = f"{self.base_url}/ajax.php"
        headers = {
            'Authorization': f'token {self.api_key}',
            'User-Agent': 'CollageDownloader/1.0'
        }
        
        params = {
            'action': 'collage',
            'id': collage_id,
            'page': 1
        }
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('status') == 'success':
                    return data['response']
        
        return None
    
    async def get_all_collage_torrents(self, collage_id: int) -> List[Dict]:
        """Get all torrent IDs from all pages of a collage"""
        url = f"{self.base_url}/ajax.php"
        headers = {
            'Authorization': f'token {self.api_key}',
            'User-Agent': 'CollageDownloader/1.0'
        }
        
        all_torrents = []
        page = 1
        
        print(f"📥 Fetching collage #{collage_id} torrents...")
        
        while True:
            params = {
                'action': 'collage',
                'id': collage_id,
                'page': page
            }
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status != 200:
                    break
                
                data = await response.json()
                if data.get('status') != 'success':
                    break
                
                resp = data['response']
                
                # Get torrents from this page
                page_torrents = []
                for item in resp.get('torrentgroups', []):
                    # The actual group info is nested inside 'group'
                    group = item.get('group', {})
                    torrents = item.get('torrents', [])
                    
                    # Extract artist names from musicInfo
                    artists = []
                    music_info = group.get('musicInfo', {})
                    if music_info:
                        # Get main artists
                        for artist in music_info.get('artists', []):
                            artists.append(artist.get('name', ''))
                        # Also get 'with' artists if any
                        for artist in music_info.get('with', []):
                            artists.append(artist.get('name', ''))
                    
                    artist_str = ', '.join(artists) if artists else 'Various Artists'
                    
                    # Add each torrent with album info
                    for torrent in torrents:
                        torrent_info = {
                            'torrent_id': torrent.get('id'),
                            'group_id': group.get('id'),
                            'artist': artist_str,
                            'album': group.get('name', ''),
                            'year': group.get('year', ''),
                            'format': torrent.get('format', ''),
                            'encoding': torrent.get('encoding', ''),
                            'media': torrent.get('media', ''),
                            'size': torrent.get('size', 0),
                            'seeders': torrent.get('seeders', 0),
                            'leechers': torrent.get('leechers', 0),
                            'snatched': torrent.get('snatched', 0)
                        }
                        page_torrents.append(torrent_info)
                
                all_torrents.extend(page_torrents)
                print(f"   Page {page}: Found {len(page_torrents)} torrents")
                
                # Check if more pages
                if page >= resp.get('pages', 1):
                    break
                page += 1
        
        print(f"✅ Total torrents found: {len(all_torrents)}")
        return all_torrents
    
    async def download_torrent_file(self, torrent_id: int, output_path: Path, filename: str = None, use_token: bool = False) -> bool:
        """Download a single torrent file"""
        url = f"{self.base_url}/ajax.php"
        headers = {
            'Authorization': f'token {self.api_key}',
            'User-Agent': 'CollageDownloader/1.0'
        }
        
        params = {
            'action': 'download',
            'id': torrent_id
        }
        
        if use_token:
            params['usetoken'] = 'true'
        
        try:
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    # Check if it's a torrent file
                    content_type = response.headers.get('content-type', '')
                    if 'application/x-bittorrent' in content_type:
                        # It's a torrent file
                        content = await response.read()
                        
                        # Generate filename if not provided
                        if not filename:
                            filename = f"torrent_{torrent_id}.torrent"
                        
                        output_file = output_path / filename
                        with open(output_file, 'wb') as f:
                            f.write(content)
                        
                        return True
                    else:
                        # It's probably a JSON error
                        data = await response.json()
                        print(f"   ❌ Error downloading torrent {torrent_id}: {data}")
                        return False
                else:
                    print(f"   ❌ HTTP error {response.status} downloading torrent {torrent_id}")
                    return False
        except Exception as e:
            print(f"   ❌ Exception downloading torrent {torrent_id}: {e}")
            return False
    
    def sanitize_filename(self, filename: str) -> str:
        """Remove invalid characters from filename"""
        # Replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        if len(filename) > 200:
            filename = filename[:200]
        
        return filename.strip()
    
    def select_best_torrent(self, torrents: List[Dict], encoding_prefs: List[str]) -> Dict:
        """Select the best torrent from a group based on encoding preferences"""
        if not torrents:
            return None
        
        # Quality scoring based on Gazelle's ZIP_OPTION hierarchy
        quality_scores = {
            # FLAC variants (highest quality)
            ('FLAC', '24bit Lossless', 'Vinyl'): 10,
            ('FLAC', '24bit Lossless', 'DVD'): 9,
            ('FLAC', '24bit Lossless', 'SACD'): 9,
            ('FLAC', '24bit Lossless', 'WEB'): 8,
            ('FLAC', '24bit Lossless'): 8,
            ('FLAC', 'Lossless', 'log_100_cue'): 7,  # Has log score 100 + cue
            ('FLAC', 'Lossless', 'log_100'): 6,      # Has log score 100
            ('FLAC', 'Lossless', 'log'): 5,          # Has log
            ('FLAC', 'Lossless', 'WEB'): 4,
            ('FLAC', 'Lossless'): 4,
            
            # MP3 CBR (preferred over VBR for consistency)
            ('MP3', '320'): 15,
            ('MP3', '256'): 12,
            ('MP3', '224'): 11,
            ('MP3', '192'): 10,
            
            # MP3 VBR High Quality
            ('MP3', 'V0 (VBR)'): 14,
            ('MP3', 'APX (VBR)'): 13,
            ('MP3', 'V1 (VBR)'): 12,
            
            # MP3 VBR Lower Quality
            ('MP3', 'V2 (VBR)'): 9,
            ('MP3', 'APS (VBR)'): 8,
            
            # Others
            ('AAC', '320'): 6,
            ('AAC', '256'): 5,
            ('DTS', ''): 3,
        }
        
        def get_torrent_score(torrent):
            format_str = torrent.get('format', '')
            encoding_str = torrent.get('encoding', '')
            media_str = torrent.get('media', '')
            has_log = torrent.get('hasLog', False)
            log_score = torrent.get('logScore', 0)
            has_cue = torrent.get('hasCue', False)
            
            # Special handling for FLAC with logs
            if format_str == 'FLAC' and encoding_str == 'Lossless':
                if has_log and log_score == 100 and has_cue:
                    key = ('FLAC', 'Lossless', 'log_100_cue')
                elif has_log and log_score == 100:
                    key = ('FLAC', 'Lossless', 'log_100')
                elif has_log:
                    key = ('FLAC', 'Lossless', 'log')
                elif media_str == 'WEB':
                    key = ('FLAC', 'Lossless', 'WEB')
                else:
                    key = ('FLAC', 'Lossless')
            elif format_str == 'FLAC' and encoding_str == '24bit Lossless':
                key = ('FLAC', '24bit Lossless', media_str)
                if key not in quality_scores:
                    key = ('FLAC', '24bit Lossless')
            else:
                key = (format_str, encoding_str)
            
            # Get base quality score
            base_score = quality_scores.get(key, 0)
            
            # Apply preference matching
            pref_bonus = 0
            for i, pref in enumerate(encoding_prefs):
                if self.matches_preference(pref, format_str, encoding_str, media_str, has_log, log_score, has_cue):
                    pref_bonus = 100 - i  # Higher preference = higher bonus
                    break
            
            # Quality bonuses
            quality_bonus = 0
            if has_log and log_score == 100:
                quality_bonus += 2
            elif has_log:
                quality_bonus += 1
            if has_cue:
                quality_bonus += 1
            
            # Seeder bonus (more seeders = slightly better)
            seeder_bonus = min(torrent.get('seeders', 0) / 10, 5)
            
            return base_score + pref_bonus + quality_bonus + seeder_bonus
        
        # Find the best torrent
        best_torrent = max(torrents, key=get_torrent_score)
        return best_torrent
    
    def matches_preference(self, pref: str, format_str: str, encoding_str: str, 
                          media_str: str, has_log: bool, log_score: int, has_cue: bool) -> bool:
        """Check if a torrent matches a preference string"""
        pref = pref.lower().strip()
        format_lower = format_str.lower()
        encoding_lower = encoding_str.lower()
        media_lower = media_str.lower()
        
        # Exact matches
        if pref == f"{format_lower} {encoding_lower}":
            return True
        
        # Common preference patterns
        patterns = {
            '320': format_lower == 'mp3' and '320' in encoding_lower,
            '320 cbr': format_lower == 'mp3' and encoding_lower == '320',
            'v0': format_lower == 'mp3' and 'v0' in encoding_lower,
            'v0 vbr': format_lower == 'mp3' and encoding_lower == 'v0 (vbr)',
            'v1': format_lower == 'mp3' and 'v1' in encoding_lower,
            'v2': format_lower == 'mp3' and 'v2' in encoding_lower,
            'flac': format_lower == 'flac',
            'flac lossless': format_lower == 'flac' and 'lossless' in encoding_lower,
            'flac 24bit': format_lower == 'flac' and '24bit' in encoding_lower,
            'flac log': format_lower == 'flac' and has_log,
            'flac log 100': format_lower == 'flac' and has_log and log_score == 100,
            'flac log cue': format_lower == 'flac' and has_log and has_cue,
            'flac vinyl': format_lower == 'flac' and media_lower == 'vinyl',
            'flac cd': format_lower == 'flac' and media_lower == 'cd',
            'flac web': format_lower == 'flac' and media_lower == 'web',
        }
        
        return patterns.get(pref, False)
    
    async def download_collage_torrents(self, collage_id: int, output_dir: str = None, 
                                      use_tokens: bool = False, format_filter: str = None,
                                      max_downloads: int = None, encoding_prefs: List[str] = None,
                                      one_per_album: bool = True, delay: float = 2.0) -> Dict:
        """Download all torrents from a collage"""
        
        # Default encoding preferences (320 CBR preferred, FLAC as fallback)
        if encoding_prefs is None:
            encoding_prefs = ['320', 'FLAC Lossless', 'FLAC Log 100', 'FLAC Log', 'FLAC', 'V0']
        
        # Get collage info
        collage_info = await self.get_collage_info(collage_id)
        if not collage_info:
            print("❌ Could not fetch collage info")
            return {"success": False, "error": "Could not fetch collage info"}
        
        collage_name = collage_info.get('name', f'Collage_{collage_id}')
        print(f"🎯 Collage: {collage_name}")
        print(f"   Category: {collage_info.get('collageCategoryName', 'Unknown')}")
        print(f"🎵 Encoding preferences: {' → '.join(encoding_prefs)}")
        
        # Set up output directory
        if not output_dir:
            # Cross-platform download directory
            import platform
            system = platform.system()
            if system == "Windows":
                base_dir = Path.home() / 'Documents' / 'Orpheus'
            elif system == "Darwin":  # macOS
                base_dir = Path.home() / 'Documents' / 'Orpheus'
            else:  # Linux and other Unix-like systems
                base_dir = Path.home() / 'Documents' / 'Orpheus'
            
            output_dir = base_dir / f"collage_{collage_id}_{self.sanitize_filename(collage_name)}"
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Get all torrents
        all_torrents = await self.get_all_collage_torrents(collage_id)
        
        if not all_torrents:
            print("❌ No torrents found in collage")
            return {"success": False, "error": "No torrents found"}
        
        # Group torrents by album (group_id) if one_per_album is True
        if one_per_album:
            print(f"📋 Selecting best torrent per album based on preferences...")
            albums = {}
            
            # Group by album
            for torrent in all_torrents:
                group_id = torrent['group_id']
                if group_id not in albums:
                    albums[group_id] = {
                        'artist': torrent['artist'],
                        'album': torrent['album'],
                        'year': torrent['year'],
                        'torrents': []
                    }
                albums[group_id]['torrents'].append(torrent)
            
            # Select best torrent for each album
            selected_torrents = []
            for group_id, album_data in albums.items():
                best_torrent = self.select_best_torrent(album_data['torrents'], encoding_prefs)
                if best_torrent:
                    selected_torrents.append(best_torrent)
            
            all_torrents = selected_torrents
            print(f"   Selected {len(all_torrents)} torrents from {len(albums)} albums")
        
        # Apply format filter if specified
        if format_filter:
            filtered_torrents = [t for t in all_torrents if format_filter.upper() in t.get('format', '').upper()]
            print(f"🔍 Filtered to {len(filtered_torrents)} torrents matching format '{format_filter}'")
            all_torrents = filtered_torrents
        
        # Limit downloads if specified
        if max_downloads and len(all_torrents) > max_downloads:
            all_torrents = all_torrents[:max_downloads]
            print(f"📋 Limited to first {max_downloads} torrents")
        
        # Rate limiting warning
        print(f"\n⚠️  RATE LIMIT WARNING:")
        print(f"   📋 Orpheus has strict download limits to prevent abuse")
        print(f"   🚫 Downloading many .torrents without 'snatching' can trigger limits")
        print(f"   ⏰ If you hit Error 429, wait 24 hours for limits to reset")
        print(f"   💡 Only download torrents you plan to actually download/seed")
        if len(all_torrents) > 10:
            print(f"   🔄 Using 2-second delays between downloads for {len(all_torrents)} torrents")
            print(f"   ⏱️  Estimated time: ~{len(all_torrents) * 2 / 60:.1f} minutes")
        
        # Save torrent info to JSON
        info_file = output_path / 'torrent_info.json'
        with open(info_file, 'w') as f:
            json.dump({
                'collage_id': collage_id,
                'collage_name': collage_name,
                'collage_info': collage_info,
                'torrents': all_torrents
            }, f, indent=2)
        
        print(f"💾 Saved torrent info to {info_file}")
        
        # Download torrents
        successful = 0
        failed = 0
        
        print(f"\n⬇️  Starting download of {len(all_torrents)} torrent files...")
        
        for i, torrent in enumerate(all_torrents, 1):
            # Generate filename
            artist = self.sanitize_filename(torrent.get('artist', 'Unknown'))
            album = self.sanitize_filename(torrent.get('album', 'Unknown'))
            year = torrent.get('year', '')
            format_info = torrent.get('format', '')
            encoding = torrent.get('encoding', '')
            
            filename = f"{artist} - {album}"
            if year:
                filename += f" ({year})"
            if format_info:
                filename += f" [{format_info}"
                if encoding:
                    filename += f" {encoding}"
                filename += "]"
            filename += f" - {torrent['torrent_id']}.torrent"
            
            print(f"   {i}/{len(all_torrents)}: {filename[:80]}...")
            
            success = await self.download_torrent_file(
                torrent['torrent_id'], 
                output_path, 
                filename,
                use_tokens
            )
            
            if success:
                successful += 1
            else:
                failed += 1
            
            # Small delay to be respectful to rate limits (Orpheus has strict limits!)
            await asyncio.sleep(2.0)  # 2 seconds between downloads
        
        print(f"\n✅ Download complete!")
        print(f"   📁 Output directory: {output_path}")
        print(f"   ✅ Successful: {successful}")
        print(f"   ❌ Failed: {failed}")
        print(f"   📊 Success rate: {successful/(successful+failed)*100:.1f}%")
        print(f"\n💡 Files saved to: {output_path}")
        print(f"   Load the .torrent files in your preferred torrent client")
        
        return {
            "success": True,
            "output_dir": str(output_path),
            "successful": successful,
            "failed": failed,
            "total": len(all_torrents)
        }

async def main():
    parser = argparse.ArgumentParser(description="Download all torrent files from an Orpheus collage")
    parser.add_argument('collage_id', type=int, help='Collage ID to download')
    parser.add_argument('--output-dir', help='Output directory (default: auto-generated)')
    parser.add_argument('--use-tokens', action='store_true', help='Use FL tokens for downloads')
    parser.add_argument('--format', help='Filter by format (e.g., FLAC, MP3)')
    parser.add_argument('--max', type=int, help='Maximum number of torrents to download')
    parser.add_argument('--api-key', help='API key (or use config file)')
    
    # Encoding preference options
    parser.add_argument('--prefer-320', action='store_true', 
                       help='Prefer 320 CBR MP3, fallback to FLAC (default behavior)')
    parser.add_argument('--prefer-flac', action='store_true', 
                       help='Prefer FLAC (with logs preferred), fallback to 320 MP3')
    parser.add_argument('--prefer-v0', action='store_true',
                       help='Prefer V0 VBR MP3, fallback to 320 CBR')
    parser.add_argument('--encoding-priority', nargs='+',
                       help='Custom encoding priority list (e.g., "320" "FLAC Log 100" "V0")')
    
    parser.add_argument('--delay', type=float, default=2.0,
                       help='Delay between downloads in seconds (default: 2.0, min: 1.0)')
    
    # Download behavior
    parser.add_argument('--all-versions', action='store_true',
                       help='Download all torrent versions (not just one per album)')
    parser.add_argument('--force-fast', action='store_true',
                       help='Use faster downloads (WARNING: may trigger rate limits)')
                       
    # Show available preference options
    if len(sys.argv) == 1 or '--help' in sys.argv or '-h' in sys.argv:
        print("\nAvailable encoding preferences:")
        print("  320, V0, V1, V2           - MP3 formats")  
        print("  FLAC, FLAC Lossless      - FLAC formats")
        print("  FLAC Log, FLAC Log 100   - FLAC with ripping logs")
        print("  FLAC 24bit, FLAC Vinyl   - High quality FLAC")
        print("  FLAC CD, FLAC WEB        - FLAC by media type")
        print("\nExamples:")
        print("  --prefer-320             # 320 CBR → FLAC → V0 (default)")
        print("  --prefer-flac            # FLAC Log 100 → FLAC → 320")
        print("  --encoding-priority '320' 'V0' 'FLAC'")
        print("  --all-versions           # Download all formats, not just best")
    
    args = parser.parse_args()
    
    # Build encoding preferences based on arguments
    encoding_prefs = None
    if args.encoding_priority:
        encoding_prefs = args.encoding_priority
    elif args.prefer_flac:
        encoding_prefs = ['FLAC Log 100', 'FLAC Log', 'FLAC Lossless', 'FLAC', '320', 'V0']
    elif args.prefer_v0:
        encoding_prefs = ['V0', '320', 'FLAC Lossless', 'FLAC']
    else:  # Default or --prefer-320
        encoding_prefs = ['320', 'FLAC Lossless', 'FLAC Log 100', 'FLAC Log', 'FLAC', 'V0']
    
    one_per_album = not args.all_versions
    
    async with OrpheusCollageDownloader(args.api_key) as downloader:
        result = await downloader.download_collage_torrents(
            collage_id=args.collage_id,
            output_dir=args.output_dir,
            use_tokens=args.use_tokens,
            format_filter=args.format,
            max_downloads=args.max,
            encoding_prefs=encoding_prefs,
            one_per_album=one_per_album
        )
        
        if not result["success"]:
            print(f"❌ Download failed: {result.get('error')}")
            return 1
        
        return 0

if __name__ == "__main__":
    asyncio.run(main())
