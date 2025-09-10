#!/usr/bin/sh

# normalize input
input="$1"

# check if input is truthy
if [ "$1" = "true" ] || [ "$1" = "1" ] || [ "$1" = "yes" ]; then
    python3 -m pip install yt-dlp requests --break-system-packages
else
    python3 -m pip install yt-dlp requests
fi