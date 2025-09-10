# YouTube Downloader V1

try:
    import os, yt_dlp as ytdl, json, sys, curses
    from typing import Literal
except ModuleNotFoundError:
    import os, sys
    print(f"You do not have all the necessary modules. Please run the \"require.{"bat" if os.name == "nt" else "sh"}\" file.")
    sys.exit(1)

try:
    from extras import *
except ModuleNotFoundError:
    print("You are missing the \"extras.py\" file. Please redownload the file from the GitHub.")
    sys.exit(1)

ScriptDir = os.path.dirname(__file__)
JSONFile = os.path.join(ScriptDir, "DownloadSettings.json")

Settings = {
    "hq": True,
    "output": "~/Downloads"
}

try:
    with open(JSONFile, "r") as f:
        Settings = json.load(f)
except PermissionError:
    print("[!!!] You do not have the necessary permissions to read \"DownloadSettings.json\". Falling back to defaults.")
except FileNotFoundError:
    try:
        with open(JSONFile, "w") as f:
            json.dump(Settings, f)
    except PermissionError:
        print("[!!!] You do not have the necessary permissions to create \"DownloadSettings.json\".")
    except Exception as e:
        print("Something went wrong.", e.__traceback__.tb_lineno, e)
        sys.exit(1)
    else:
        print("DownloadSettings.json file generated.")
except Exception as e:
    print("Something went wrong.", e.__traceback__.tb_lineno, e)
    sys.exit(1)

if not CheckInternet():
    print("You do not have good enough connection to run YouTube Downloader. Please connect to the internet and try again.")
    sys.exit(1)

OutDir = os.path.abspath(os.path.expanduser(Settings["output"]))

# ok great i need to create my own argument parser, cuz, i dont like "argparse" :P

def SplitPrm(arg: str) -> list[str]:
    prms = []
    if arg.startswith("-") and len(arg) > 2 and not arg.startswith("--"):
        for idx, char in enumerate(arg):
            if idx == 0: continue
            prms.append(f"-{char}")
    else: prms.append(arg)
    return prms

def FlattenList(lst: list[list]) -> list:
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(FlattenList(item))
        else:
            result.append(item)
    return result

def printHelp() -> None:
    print(f"""YouTube Downloader
------------------
Flags:
    --help | -h : Show this help message
    --lq | -l   : Download in Low Quality regardless of DownloadSettings
    --hq | -q   : Download in High Quality regardless of DownloadSettings

Params:
    python {os.path.basename(__file__)} [Type] [URL] [Flags]

    Type: [video, audio, both] : What kind of download you want
    URL: str                   : YouTube Video URL
    Flags: str                 : See above""")
    sys.exit(0)

def ArgsInARGV(args: list[str], argv: list[str]) -> bool: return any([item in argv for item in args])

argv = FlattenList([SplitPrm(arg) for arg in sys.argv])[1:] # python . [args] | ignore . by trimming it out

if ArgsInARGV(["-h", "--help"], argv): printHelp()

OVERWRITE = False

if ArgsInARGV(["--lq", "-l"], argv): Settings["hq"], OVERWRITE = False, True
if ArgsInARGV(["--hq", "-q"], argv): Settings["hq"], OVERWRITE = True, True

print(f"[OVERWRITE] High Quality? : {Settings["hq"]}") if OVERWRITE else 0

NOFLAG = [arg for arg in argv if not arg.startswith("-")]

# huzzah we are done with that

InteractiveMode = False

try:
    Type = NOFLAG[0] # expected
    URL = NOFLAG[1] # expected
except IndexError:
    InteractiveMode = True

def download(url: str, type: Literal["video", "audio", "both"], output_path: str = ".") -> None: # url can be split by spaces :)
    PSTP = []
    if type.lower().strip() == "video":
        FRMT = "bestvideo+bestaudio/best" if Settings["hq"] else "bestvideo[height<=720]+bestaudio/best"
    elif type.lower().strip() == "audio":
        FRMT = "bestaudio/best" if Settings["hq"] else "bestaudio[abr<=128]"
        PSTP = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }]
    elif type.lower().strip() == "both":
        download(url, "video", output_path)
        download(url, "audio", output_path)
        return
    OPTS = {
        "format": FRMT,
        "postprocessors": PSTP,
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s')
    }

    if type.lower().strip() == "video":
        OPTS["merge_output_format"] = "mp4"

    DL = ytdl.YoutubeDL(OPTS)

    DL.download(url.split())

def INTERACTIVE():
    def addstr(stdscr: curses.window, y: int, text: str, *, italic: bool = False) -> None:
        _, w = stdscr.getmaxyx()
        stdscr.addstr(y, (w//2) - (len(text)//2), text, curses.A_ITALIC if italic else 0)

    def CURSESMENU(stdscr: curses.window) -> None:
        url = ""
        opt = 0
        opts = [
            "video", "audio", "both"
        ]
        while True:
            try:
                h, w = stdscr.getmaxyx()
                stdscr.clear()

                addstr(stdscr, 1, "YouTube Downloader V1")
                addstr(stdscr, 2, "by pytmg", italic=True)

                addstr(stdscr, 4, f"Mode: {' '.join([_opt.upper() if idx == opt else _opt.lower() for idx, _opt in enumerate(opts)])} [←→]")
                addstr(stdscr, 5, f"URL(s): {url} [u]")
                
                addstr(stdscr, h-3, "Press [ENTER] to begin downloading.")
                addstr(stdscr, h-2, "Press [q] to quit YouTube Downloader")

                stdscr.box()

                k = stdscr.getch()
                if k == ord("q"): break
                if k == ord("u"):
                    stdscr.clear()
                    stdscr.addstr(0, 0, "Input your URL(s) below (split by space)")
                    curses.echo(True)
                    OUTPUTb = stdscr.getstr(1, 0)
                    url = OUTPUTb.decode("utf-8")
                if k == curses.KEY_LEFT:
                    opt -= 1
                    opt %= len(opts)
                    continue
                if k == curses.KEY_RIGHT:
                    opt += 1
                    opt %= len(opts)
                    continue
                if k in [10, curses.KEY_ENTER]:
                    stdscr.clear()
                    stdscr.addstr(0, 0, "Downloading, please wait...", curses.A_DIM)
                    stdscr.refresh()
                    download(url, opts[opt], OutDir)
                    stdscr.clear()
                    stdscr.addstr(0, 0, "Downloads done. Press any key to exit.")
                    stdscr.getch()
                    break
            except curses.error:
                stdscr.clear()
                stdscr.addstr(0, 0, "Too Small!")
                stdscr.getch()

    curses.wrapper(CURSESMENU)

if InteractiveMode:
    INTERACTIVE()
else:
    if Type not in ["video", "audio", "both"]:
        print("[ArgumentError] Type is not one of [video, audio, both]")
        sys.exit(1)
    if not URL.startswith("http"):
        URL = "http://" + URL # assume http
    download(URL, Type, OutDir)