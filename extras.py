try:
    import requests
except ModuleNotFoundError:
    import os, sys
    print(f"You do not have all the necessary modules. Please run the \"require.{"bat" if os.name == "nt" else "sh"}\" file.")
    sys.exit(1)

def CheckInternet() -> bool:
    """Check if the user has an internet connection."""
    try:
        response = requests.get("https://www.google.com", timeout=2)
        return True
    except requests.exceptions.RequestException:
        return False