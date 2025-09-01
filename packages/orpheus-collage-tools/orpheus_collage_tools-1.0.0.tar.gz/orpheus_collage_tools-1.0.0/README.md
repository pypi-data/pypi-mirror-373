# Orpheus Collage Tools

[![PyPI version](https://badge.fury.io/py/orpheus-collage-tools.svg)](https://pypi.org/project/orpheus-collage-tools/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Interactive CLI for discovering, browsing, and downloading music releases from Orpheus.network private tracker.

## Installation

```bash
pip install orpheus-collage-tools
```

## Quick Start

### 1. First Run (Configuration Setup)

```bash
orpheus
```

This will automatically create your configuration file and prompt for your Orpheus credentials.

### 2. Interactive Mode

```bash
orpheus
```

### 3. Command Line Usage

```bash
# Search for artist releases
orpheus find-album --artist "The Prodigy" --interactive

# Download torrents from a collage
orpheus download 6936 --prefer-flac

# Manage crates
orpheus crate list
orpheus crate create "My Favorites"
orpheus crate download "My Favorites"
```

## Features

- **🎤 Artist Search** - Find all releases by artist with smart filtering
- **🔍 Collage Discovery** - See which curated collections contain specific albums
- **📦 Crate System** - Create wishlists and bulk download later
- **⬇️ Bulk Downloads** - Download entire collages with format preferences
- **🎯 Release-Based Organization** - View by actual pressings/labels
- **🎵 Interactive Browsing** - One album per page with complete metadata

## What Makes This Better Than the Main Site

- **Enhanced filtering** - Show just Beatles singles (impossible on main site)
- **Release-based organization** - See all 23 pressings of "The Fat Of The Land"
- **Collage navigation** - Discover music through curated collections
- **Wishlist system** - Add albums while browsing, download all at once later
- **Format preferences** - Bulk download with FLAC/320/V0 preferences

## Download Location

All torrent files are downloaded to:

- **macOS/Windows**: `~/Documents/Orpheus/`
- **Linux**: `~/Documents/Orpheus/`

## Security

Your Orpheus credentials are stored securely in:

- **macOS**: `~/.orpheus/config.json`
- **Windows**: `%APPDATA%/orpheus/config.json`
- **Linux**: `~/.orpheus/config.json`

Files are created with owner-only permissions and never committed to version control.

## Cross-Platform Support

- **macOS**: Native bash script with full interactive features
- **Windows**: Python-based implementation with batch file launcher
- **Linux**: Python-based implementation with full feature parity

## Development

For development and contribution information, see the [development guide](docs/development-guide.md).

## License

MIT License - see LICENSE file for details.
