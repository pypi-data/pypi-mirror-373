#!/usr/bin/env python3
"""
Search for Orpheus collages by name or keywords
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

class OrpheusCollageSearcher:
    def __init__(self, api_key: str = None):
        # Load API key from config if not provided
        if not api_key:
            config_path = Path.home() / '.orpheus' / 'config.json'
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    api_key = config.get('api_key', 'PSTi7lCo1E4Q9IHgYJvVg3zVpBBUOpGEaer0t1l26Eg5bw1J7l88wk2ua1IGs8X8bCFMej8DFA4Kfb/lMzl3TdWIhx7d50KW6oYTcOEw8Ed7gDLcI6+C')

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

    async def search_collages(self, search_term: str, max_results: int = 20) -> List[Dict]:
        """Search for collages by name or keywords"""
        search_url = f"{self.base_url}/collages.php"
        params = {'search': search_term}

        collages = []

        async with self.session.get(search_url, params=params) as response:
            if response.status != 200:
                print(f"❌ Search failed with status: {response.status}")
                return []

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            # Find collage links in search results
            collage_links = soup.find_all('a', href=re.compile(r'collages\.php\?id=\d+'))

            for link in collage_links[:max_results]:
                href = link['href']
                collage_id = re.search(r'id=(\d+)', href)

                if collage_id:
                    cid = int(collage_id.group(1))
                    name = link.text.strip()

                    # Skip if we already have this collage
                    if any(c['id'] == cid for c in collages):
                        continue

                    collages.append({
                        'id': cid,
                        'name': name,
                        'url': f"{self.base_url}{href}"
                    })

        return collages

    async def get_collage_details(self, collage_id: int) -> Dict:
        """Get detailed information about a specific collage"""
        url = f"{self.base_url}/ajax.php"
        headers = {
            'Authorization': f'token {self.api_key}',
            'User-Agent': 'CollageSearcher/1.0'
        }

        params = {
            'action': 'collage',
            'id': collage_id,
            'page': 1
        }

        try:
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'success':
                        return data['response']
        except Exception as e:
            print(f"⚠️  Error fetching collage details: {e}")

        return None

    def display_collages(self, collages: List[Dict], show_details: bool = False):
        """Display search results"""
        if not collages:
            print("❌ No collages found matching your search.")
            return

        print(f"\n🔍 Found {len(collages)} collage(s):")
        print("=" * 60)

        for i, collage in enumerate(collages, 1):
            print(f"{i}. 📀 {collage['name']}")
            print(f"   🆔 ID: {collage['id']}")
            print(f"   🔗 URL: {collage['url']}")

            if show_details:
                # Could add more details here if needed
                pass

            print("-" * 60)

        print("\n💡 To download any of these collages:")
        print("   Use: ./collage_tools download <ID> --prefer-320")
        print("   Example: ./collage_tools download 12345 --prefer-320")

async def main():
    parser = argparse.ArgumentParser(description="Search for Orpheus collages by name")
    parser.add_argument('search_term', help='Collage name or keywords to search for')
    parser.add_argument('--max-results', type=int, default=20, help='Maximum number of results to show')
    parser.add_argument('--details', action='store_true', help='Show detailed information')
    parser.add_argument('--api-key', help='API key (or use config file)')

    args = parser.parse_args()

    async with OrpheusCollageSearcher(args.api_key) as searcher:
        print(f"🔍 Searching for collages: '{args.search_term}'")

        collages = await searcher.search_collages(args.search_term, args.max_results)

        searcher.display_collages(collages, args.details)

if __name__ == "__main__":
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("❌ BeautifulSoup4 is required. Install it with:")
        print("   pip3 install beautifulsoup4")
        sys.exit(1)

    asyncio.run(main())
