#!/usr/bin/sh

# normalize input
input="$1"

# check if input is truthy
case "$input" in
    True|true|1|yes)
        python3 -m pip install yt-dlp --break-system-packages
        ;;
    *)
        python3 -m pip install yt-dlp
        ;;
esac