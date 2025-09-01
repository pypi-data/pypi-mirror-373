#!/bin/bash
# Orpheus Collage Tools - macOS Package Script
# This script is used when the package is installed via pip on macOS

SCRIPT_DIR=$(dirname "$0")/../../../..
LIB_DIR="$SCRIPT_DIR/lib"
CONFIG_DIR="$HOME/.orpheus"
CONFIG_FILE="$CONFIG_DIR/config.json"

# Configuration management
check_and_setup_config() {
    # Check if config directory exists, create if not
    if [ ! -d "$CONFIG_DIR" ]; then
        echo "🔧 Setting up Orpheus configuration directory..."
        mkdir -p "$CONFIG_DIR"
        if [ $? -ne 0 ]; then
            echo "❌ Failed to create config directory: $CONFIG_DIR"
            exit 1
        fi
        echo "✅ Created config directory: $CONFIG_DIR"
    fi

    # Check if config file exists
    if [ ! -f "$CONFIG_FILE" ]; then
        echo ""
        echo "🔑 Orpheus Configuration Setup"
        echo "=============================="
        echo "Configuration file not found. Please provide your Orpheus credentials."
        echo ""

        # Loop until valid username and password are entered
        while true; do
            # Prompt for username
            read -p "Enter your Orpheus username: " username
            if [ -z "$username" ]; then
                echo "❌ Username is required!"
                continue
            fi

            # Prompt for password (hidden input)
            echo -n "Enter your Orpheus password: "
            read -s password
            echo
            if [ -z "$password" ]; then
                echo "❌ Password is required!"
                continue
            fi

            # Test login credentials
            echo "🔍 Validating credentials..."

            # Use curl to test login
            login_response=$(curl -s -c /tmp/orpheus_cookies -b /tmp/orpheus_cookies \
                -d "username=$username" \
                -d "password=$password" \
                -d "keeplogged=1" \
                -d "login=Log in" \
                -w "%{http_code}" \
                -o /dev/null \
                "https://orpheus.network/login.php" 2>/dev/null)

            # Clean up temp cookies
            rm -f /tmp/orpheus_cookies 2>/dev/null

            # Check if login was successful (302/303 redirect or 200 with session)
            if [ "$login_response" = "302" ] || [ "$login_response" = "303" ]; then
                echo "✅ Login credentials validated successfully!"
                break
            else
                echo "❌ Login failed. Please check your username and password."
                echo ""
            fi
        done

        # Now prompt for API key and validate it
        echo ""
        while true; do
            read -p "Enter your Orpheus API key: " api_key
            if [ -z "$api_key" ]; then
                echo "❌ API key is required!"
                continue
            fi

            # Test API key with a simple API call
            echo "🔍 Validating API key..."

            # Use curl to test API key with collage endpoint (simple test)
            api_response=$(curl -s \
                -H "Authorization: token $api_key" \
                -H "User-Agent: Orpheus-CLI/1.0" \
                -w "%{http_code}" \
                -o /tmp/api_test_response \
                "https://orpheus.network/ajax.php?action=collage&id=1" 2>/dev/null)

            # Check response content for success/error
            if [ -f /tmp/api_test_response ]; then
                response_content=$(cat /tmp/api_test_response)
                rm -f /tmp/api_test_response 2>/dev/null

                # Check if response contains success (API key works)
                if [[ "$api_response" = "200" ]] && [[ "$response_content" == *"\"status\":\"success\""* ]] && [[ "$response_content" != *"\"error\""* ]]; then
                    echo "✅ API key validated successfully!"
                    break
                elif [[ "$response_content" == *"\"error\""* ]]; then
                    echo "❌ API key validation failed. Please check your API key."
                    echo "💡 To obtain your API key:"
                    echo "   1. Go to User Settings: https://orpheus.network/user.php?action=edit&id=8956#access"
                    echo "   2. Scroll all the way down to the 'Access' section"
                    echo "   3. Copy your API key from there"
                    echo ""
                else
                    echo "❌ API key validation failed. Please check your API key."
                    echo "💡 To obtain your API key:"
                    echo "   1. Go to User Settings: https://orpheus.network/user.php?action=edit&id=8956#access"
                    echo "   2. Scroll all the way down to the 'Access' section"
                    echo "   3. Copy your API key from there"
                    echo ""
                fi
            else
                echo "❌ Could not validate API key. Please check your API key."
                echo "💡 To obtain your API key:"
                echo "   1. Go to User Settings: https://orpheus.network/user.php?action=edit&id=8956#access"
                echo "   2. Scroll all the way down to the 'Access' section"
                echo "   3. Copy your API key from there"
                echo ""
            fi
        done

        # Create config file
        echo "📝 Saving configuration..."
        cat > "$CONFIG_FILE" << EOF
{
  "username": "$username",
  "password": "$password",
  "api_key": "$api_key"
}
EOF

        # Set secure permissions
        chmod 600 "$CONFIG_FILE"

        echo "✅ Configuration saved to: $CONFIG_FILE"
        echo "🔒 File permissions set to 600 (owner read/write only)"
        echo ""

    else
        # Config exists, verify it has required fields
        if ! command -v python3 >/dev/null 2>&1; then
            echo "❌ Python3 is required but not installed"
            exit 1
        fi

        # Basic validation using python
        python3 -c "
import json
try:
    with open('$CONFIG_FILE', 'r') as f:
        config = json.load(f)
    required_fields = ['username', 'password', 'api_key']
    missing = [field for field in required_fields if field not in config or not config[field]]
    if missing:
        print('❌ Config file missing required fields: ' + ', '.join(missing))
        exit(1)
except Exception as e:
    print('❌ Invalid config file format: ' + str(e))
    exit(1)
" 2>/dev/null || {
            echo "❌ Invalid or incomplete configuration file"
            echo "Please delete $CONFIG_FILE and run again to reconfigure"
            exit 1
        }
    fi
}

# Interactive prompts function
interactive_mode() {
    while true; do
        tput clear
        # Loading bar with modern style
        echo -e "\033[32mLoading...\033[0m"
        bar_length=30
        for i in $(seq 1 $bar_length); do
            filled=$(printf '%.0s' $(seq 1 $i))
            empty=$(printf '%.0s' $(seq 1 $(($bar_length - $i))))
            printf "\r\033[1;32m[%s%s]\033[0m %d%%" "$filled" "$empty" $(($i * 100 / $bar_length))
            sleep 0.1
        done
        echo
        echo -e "\033[1;35mReady to go! 🎨\033[0m"
    	tput clear
    	        echo -e "\033[1;34m"

echo "  ######    ######    ######  ##    ##  #######  ##    ##  ######  "
            sleep 0.1
echo " ##    ##  ##   ##   ##   ##  ##    ##  ##       ##    ## ##    ## "
            sleep 0.09
echo " ##    ##  ##   ##   ##   ##  ##    ##  ##       ##    ## ##       "
            sleep 0.08
echo " ##    ##  ######    ######   ########  ######   ##    ##  ######  "
            sleep 0.07
echo " ##    ##  ##  ##    ##       ##    ##  ##       ##    ##       ## "
            sleep 0.06
echo " ##    ##  ##   ##   ##       ##    ##  ##       ##    ## ##    ## "
            sleep 0.05
echo "  ######   ##    ##  ##       ##    ##  #######   ######   ######  "
            sleep 0.04
                    echo -e "\033[1;36m"
                    echo -e " Orpheus Collage Tools - Interactive Mode"
                                sleep 0.04
		echo -e "\033[1;32m"
        echo
        echo "==========================================="
        echo ""
        echo "What would you like to do?"
                    sleep 0.04
                                        echo -e "\033[1;31m"

        echo "1. 🎤 Find artist albums & releases (with crates)"
                    sleep 0.03
                                        echo -e "\033[1;32m"

        echo "2. 🔍 Find collages"
                    sleep 0.02
                                        echo -e "\033[1;35m"

        echo "3. ⬇️  Download torrents from a collage"
                    sleep 0.03
                                        echo -e "\033[1;37m"

        echo "4. 📦 Manage crates"
                    sleep 0.04
                                        echo -e "\033[1;38m"

        echo "5. 🎯 Load crate and browse"
                    sleep 0.05
                                        echo -e "\033[1;39m"

        echo "6. ❌ Exit"
                    sleep 0.06
        echo ""
        echo "💡 Quick tips:"
        echo "   • Use option 1 for browsing artist discographies"
        echo "   • Use option 2 for all collage search and discovery"
        echo "   • Use option 3 to download by collage ID"
        echo "   • All downloads save to ~/Documents/Orpheus/"
        echo ""
        echo ""
        read -p "Choose option (1-6): " choice

        case $choice in
            1)
                echo ""
                echo "🎤 Find Artist Albums & Releases (Enhanced with Crates)"
                echo "======================================================"
                read -p "Enter artist name: " artist

                if [ -z "$artist" ]; then
                    echo "❌ Artist name is required!"
                    echo ""
                    continue
                fi

                echo ""
                echo "🎵 Release search options:"
                echo "1. All releases (including compilations)"
                echo "2. Official releases only"
                echo "3. Search specific release"
                echo ""
                read -p "Choose option (1-3): " search_option

                case $search_option in
                    1)
                        echo ""
                        echo "🔍 Searching for all releases by $artist..."
                        python3 "$LIB_DIR/find_album_collages.py" --artist "$artist" --interactive
                        result=$?
                        ;;
                    2)
                        echo ""
                        echo "🔍 Searching for official releases by $artist..."
                        python3 "$LIB_DIR/find_album_collages.py" --artist "$artist" --official-only --interactive
                        result=$?
                        ;;
                    3)
                        echo ""
                        read -p "Enter album/release name: " album
                        if [ -z "$album" ]; then
                            echo "❌ Album name is required!"
                            echo ""
                            continue
                        fi
                        echo ""
                        echo "🔍 Searching for '$album' by $artist..."
                        python3 "$LIB_DIR/find_album_collages.py" --artist "$artist" --album "$album" --interactive
                        result=$?
                        ;;
                    *)
                        echo "❌ Invalid choice!"
                        echo ""
                        continue
                        ;;
                esac
                ;;

            2)
                collage_menu
                ;;

            3)
                echo ""
                echo "⬇️  Download Torrents from a Collage"
                echo "===================================="
                read -p "Enter collage ID: " collage_id

                if [ -z "$collage_id" ]; then
                    echo "❌ Collage ID is required!"
                    echo ""
                    continue
                fi

                echo ""
                echo "📀 Choose preferred encoding:"
                echo "1. MP3 320 CBR     (High quality, universal compatibility)"
                echo "2. MP3 V0 VBR      (Excellent quality, smaller files)"
                echo "3. FLAC Lossless   (Perfect quality, largest files)"
                echo ""
                echo "💡 Tips:"
                echo "   • 320 CBR: Best for most users, works everywhere"
                echo "   • V0 VBR: Great quality with smaller file sizes"
                echo "   • FLAC: Perfect quality for audiophiles"
                echo ""
                read -p "Choose option (1-3): " encoding_choice

                case $encoding_choice in
                    1)
                        prefer="--prefer-320"
                        format_name="MP3 320 CBR"
                        ;;
                    2)
                        prefer="--prefer-v0"
                        format_name="MP3 V0 VBR"
                        ;;
                    3)
                        prefer="--prefer-flac"
                        format_name="FLAC Lossless"
                        ;;
                    *)
                        echo "❌ Invalid choice!"
                        echo ""
                        continue
                        ;;
                esac

                echo ""
                echo "⬇️ Starting download from collage ID: $collage_id"
                echo "🎵 Preferred format: $format_name"
                echo ""
                if [ -f "$LIB_DIR/download_collage_torrents.py" ]; then
                    python3 "$LIB_DIR/download_collage_torrents.py" "$collage_id" "$prefer"
                fi
                ;;

            4)
                echo ""
                echo "📦 Crate Management"
                echo "=================="
                echo "1. 📋 List existing crates"
                echo "2. 📝 Create new crate"
                echo "3. ⬇️  Download a crate"
                echo "4. 🔙 Back to main menu"
                echo ""
                read -p "Choose option (1-4): " crate_choice

                case $crate_choice in
                    1)
                        python3 "$LIB_DIR/download_crate.py" --list-crates
                        ;;
                    2)
                        read -p "Enter crate name: " crate_name
                        if [ -n "$crate_name" ]; then
                            python3 "$LIB_DIR/download_crate.py" --create-crate "$crate_name"
                        else
                            echo "❌ Please provide a crate name"
                        fi
                        ;;
                    3)
                        echo ""
                        python3 "$LIB_DIR/download_crate.py" --list-crates
                        echo ""
                        read -p "Enter crate name to download: " download_crate
                        if [ -n "$download_crate" ]; then
                            python3 "$LIB_DIR/download_crate.py" --download-crate "$download_crate"
                        else
                            echo "❌ Please provide a crate name"
                        fi
                        ;;
                    4)
                        continue
                        ;;
                    *)
                        echo "❌ Invalid choice!"
                        ;;
                esac
                ;;

            5)
                echo ""
                echo "🎯 Load Crate and Browse"
                echo "======================="
                python3 "$LIB_DIR/download_crate.py" --list-crates
                echo ""
                read -p "Enter crate name to load: " load_crate
                if [ -n "$load_crate" ]; then
                    read -p "Enter artist to search: " artist
                    if [ -n "$artist" ]; then
                        echo "🔍 Searching with crate functionality..."
                        python3 "$LIB_DIR/find_album_collages.py" --artist "$artist" --interactive
                    else
                        echo "❌ Artist name is required for browsing"
                    fi
                else
                    echo "❌ Please provide a crate name"
                fi
                ;;

            6)
                echo "👋 Goodbye!"
                exit 0
                ;;

            *)
                echo "❌ Invalid choice!"
                echo ""
                continue
                ;;
        esac

        # Pause before showing menu again
        if [ $result -ne 2 ] 2>/dev/null; then
            echo ""
            read -p "Press Enter to return to main menu..."
        fi
        echo ""
    done
}

# Collage submenu function
collage_menu() {
    while true; do
        echo ""
        echo "🔍 COLLAGE SEARCH OPTIONS"
        echo "========================="
        echo ""
        echo "1. 🎵 Find collages featuring an artist"
        echo "2. 🔍 Find which collages contain a specific album"
        echo "3. 📝 Search & download collages by name"
        echo "4. 🔙 Back to main menu"
        echo ""
        read -p "Choose option (1-4): " collage_choice

        case $collage_choice in
            1)
                echo ""
                echo "🎵 Find Collages Featuring an Artist"
                echo "===================================="
                read -p "Enter artist name: " artist

                if [ -z "$artist" ]; then
                    echo "❌ Artist name is required!"
                    echo ""
                    continue
                fi

                echo ""
                echo "🔍 Searching for collages that contain albums by $artist..."
                echo "💡 This will find all collages featuring $artist's music"
                echo ""

                if [ -f "$LIB_DIR/search_artist_collages.py" ]; then
                    python3 "$LIB_DIR/search_artist_collages.py" "$artist"
                else
                    echo "❌ Artist collage search script not found!"
                fi
                ;;

            2)
                echo ""
                echo "🔍 Find Which Collages Contain an Album"
                echo "======================================="
                read -p "Enter artist name: " artist
                read -p "Enter album name: " album

                if [ -z "$artist" ] || [ -z "$album" ]; then
                    echo "❌ Both artist and album names are required!"
                    echo ""
                    continue
                fi

                echo ""
                echo "🔍 Searching for '$album' by $artist in collages..."
                python3 "$LIB_DIR/find_album_collages.py" --artist "$artist" --album "$album" --show-collages
                result=$?
                ;;

            3)
                echo ""
                echo "📝 Search & Download Collages by Name"
                echo "===================================="
                read -p "Enter collage name or keywords: " collage_search

                if [ -z "$collage_search" ]; then
                    echo "❌ Search term is required!"
                    echo ""
                    continue
                fi

                echo ""
                echo "🔍 Searching for collages containing: '$collage_search'"
                echo "💡 This will show matching collages with their IDs"
                echo "   You can then use option 3 to download them"
                echo ""

                if [ -f "$LIB_DIR/search_collages.py" ]; then
                    python3 "$LIB_DIR/search_collages.py" "$collage_search"
                else
                    echo "❌ Collage search script not found!"
                fi
                ;;

            4)
                return
                ;;

            *)
                echo "❌ Invalid choice! Please choose 1, 2, 3, or 4."
                echo ""
                continue
                ;;
        esac

        echo ""
        read -p "Press Enter to return to collage menu..."
        echo ""
    done
}

# Check and setup configuration before running any commands
check_and_setup_config

case $1 in
    crate)
        case $2 in
            list)
                python3 "$LIB_DIR/download_crate.py" --list-crates
                ;;
            create)
                if [ -n "$3" ]; then
                    python3 "$LIB_DIR/download_crate.py" --create-crate "$3"
                else
                    echo "Usage: orpheus crate create <crate_name>"
                fi
                ;;
            download)
                if [ -n "$3" ]; then
                    python3 "$LIB_DIR/download_crate.py" --download-crate "$3"
                else
                    echo "Usage: orpheus crate download <crate_name>"
                fi
                ;;
            *)
                echo "📦 Crate Commands:"
                echo "  orpheus crate list             # List all crates"
                echo "  orpheus crate create <n>       # Create new crate"
                echo "  orpheus crate download <n>     # Download crate"
                ;;
        esac
        ;;

    find-artist-collages)
        shift
        artist="$1"

        if [ -z "$artist" ]; then
            echo "❌ Artist name is required!"
            echo "Usage: orpheus find-artist-collages 'Artist Name'"
            exit 1
        fi

        echo ""
        echo "🎵 Finding Collages Featuring '$artist'"
        echo "======================================"
        echo "🔍 Searching for collages that contain albums by $artist..."
        echo "💡 This will find all collages featuring $artist's music"
        echo ""

        if [ -f "$LIB_DIR/search_artist_collages.py" ]; then
            python3 "$LIB_DIR/search_artist_collages.py" "$artist"
        else
            echo "❌ Artist collage search script not found!"
            exit 1
        fi
        ;;

    download)
        # Download torrent files from a collage (--prefer is MANDATORY)
        shift
        collage_id="$1"
        shift

        # Check if --prefer option is provided
        prefer_found=false
        for arg in "$@"; do
            case $arg in
                --prefer-*)
                    prefer_found=true
                    break
                    ;;
            esac
        done

        if [ "$prefer_found" = false ]; then
            echo "❌ ERROR: --prefer option is MANDATORY!"
            echo ""
            echo "Required encoding preference:"
            echo "  --prefer-320    # MP3 320 CBR"
            echo "  --prefer-v0     # MP3 V0 VBR"
            echo "  --prefer-flac   # FLAC Lossless"
            echo ""
            echo "Example: orpheus download 6936 --prefer-320"
            exit 1
        fi

        python3 "$LIB_DIR/download_collage_torrents.py" "$collage_id" "$@"
        ;;

    quick-search)
        # Quick search for an artist/album's collages
        shift
        artist=""
        album=""

        while [ $# -gt 0 ]; do
            case $1 in
                --artist)
                    artist="$2"
                    shift 2
                    ;;
                --album)
                    album="$2"
                    shift 2
                    ;;
                *)
                    shift
                    ;;
            esac
        done

        if [ -n "$artist" ] || [ -n "$album" ]; then
            echo "🔍 Quick search for collages..."
            python3 "$LIB_DIR/find_album_collages.py" --artist "$artist" --album "$album"
        else
            echo "Usage: orpheus quick-search --artist 'Name' --album 'Name'"
        fi
        ;;

    "")
        # No arguments - start interactive mode
        interactive_mode
        ;;

    *)
        echo "🎵 Orpheus Collage Tools - Cross-Platform"
        echo "=========================================="
        echo ""
        echo "🌐 Live Search Commands:"
        echo "  orpheus find-album --artist 'Name' --interactive"
        echo "  orpheus find-album --artist 'Name' --album 'Name'"
        echo ""
        echo "📦 Crate Commands:"
        echo "  orpheus crate list                    # List all crates"
        echo "  orpheus crate create <n>             # Create new crate"
        echo "  orpheus crate download <n>           # Download crate"
        echo ""
        echo "⬇️  Download Commands (--prefer is MANDATORY):"
        echo "  orpheus download [collage_id] --prefer-320  # MP3 320"
        echo "  orpheus download [collage_id] --prefer-v0   # MP3 V0"
        echo "  orpheus download [collage_id] --prefer-flac # FLAC"
        echo ""
        echo "🔍 Quick Search:"
        echo "  orpheus quick-search --artist 'Name' --album 'Name'"
        echo ""
        echo "🎯 Interactive Mode:"
        echo "  orpheus                              # Start guided prompts"
        echo ""
        echo "💡 Examples:"
        echo "  orpheus find-album --artist 'The Prodigy' --interactive"
        echo "  orpheus crate create 'My Favorites'"
        echo "  orpheus crate download 'My Favorites'"
        ;;
esac
