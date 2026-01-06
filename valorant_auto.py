# ===========================
# Standard Library
# ===========================
import os
import sys
import subprocess
import time
import pickle
from pathlib import Path
from datetime import datetime

# ===========================
# Third-Party Libraries
# ===========================
import google_auth_oauthlib.flow
import googleapiclient.discovery
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request

# ===========================
# ANSI COLOR CODES
# ===========================
class Colors:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"

# ===========================
# CONFIGURATION
# ===========================
BASE_DIR = r"C:\Users\username\Videos\Overwolf\Valorant Tracker\VALORANT"
TEMP_DIR = Path(os.environ['TEMP'])
OUTPUT = TEMP_DIR / f"valorant_highlights_{datetime.now().strftime('%Y%m%d_%H%M')}.mp4"
LIST_FILE = TEMP_DIR / "list.txt"
SCRIPT_DIR = Path(__file__).resolve().parent
CLIENT_SECRET = SCRIPT_DIR / "client_secret.json"
CREDENTIALS_FILE = SCRIPT_DIR / "youtube_credentials.pkl"

# Generate list file
with open(LIST_FILE, "w", encoding="utf-8") as f:
    for folder in Path(BASE_DIR).iterdir():
        for clip in folder.glob("*.mp4"):
            f.write(f"file '{clip.as_posix()}'\n")

# ===========================
# COMPILE ALL CLIPS INTO ONE VIDEO
# ===========================
print(f"{Colors.YELLOW}Compiling video...{Colors.RESET}")

if LIST_FILE.stat().st_size == 0:
    print("No clips")
    sys.exit()

subprocess.run([
    "ffmpeg",
    "-f", "concat",
    "-safe", "0",
    "-i", str(LIST_FILE),
    "-c", "copy",
    str(OUTPUT)
], check=True)

print(f"{Colors.GREEN}Video compilation complete: {OUTPUT}{Colors.RESET}")

# ===========================
# AUTHENTICATE & UPLOAD TO YOUTUBE
# ===========================
credentials = None

# Try loading saved credentials
if CREDENTIALS_FILE.exists():
    with open(CREDENTIALS_FILE, "rb") as f:
        credentials = pickle.load(f)

# If no credentials or invalid, run OAuth flow
if not credentials or not credentials.valid:
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    else:
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRET,
            scopes=["https://www.googleapis.com/auth/youtube"]
        )
        credentials = flow.run_local_server(port=8080)
    
    # Save credentials for next time
    with open(CREDENTIALS_FILE, "wb") as f:
        pickle.dump(credentials, f)

youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
media_body = MediaFileUpload(str(OUTPUT), chunksize=1024 * 1024, resumable=True)

request = youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": f"Valorant Highlights {datetime.now().strftime('%d %b %Y')}",
            "description": "Auto-generated Valorant highlights",
            "categoryId": "20"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    },
    media_body=media_body
)

response = None

# ===========================
# PLAYLIST HELPERS
# ===========================
def get_or_create_playlist(youtube, title):
    request = youtube.playlists().list(part="snippet", mine=True, maxResults=50)
    while request:
        response = request.execute()
        for playlist in response["items"]:
            if playlist["snippet"]["title"] == title:
                return playlist["id"]
        request = youtube.playlists().list_next(request, response)

    playlist = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {"title": title, "description": "Auto-generated Valorant highlights"},
            "status": {"privacyStatus": "public"}
        }
    ).execute()

    return playlist["id"]

# ===========================
# UPLOAD LOOP
# ===========================
while response is None:
    try:
        status, response = request.next_chunk()
        if status:
            percent = int(status.progress() * 100)
            print(f"\r{Colors.BLUE}Upload progress: {percent:3d}%{Colors.RESET}", end="", flush=True)

    except HttpError as e:
        if "uploadLimitExceeded" in str(e):
            print(f"\n{Colors.RED}Daily upload limit reached. Upload aborted.{Colors.RESET}")
            exit(1)

        print(f"\n{Colors.YELLOW}Transient error. Retrying in 10 seconds...{Colors.RESET}")
        time.sleep(10)

# ===========================
# POST-UPLOAD
# ===========================
video_id = response["id"]
print(f"\r{Colors.GREEN}Upload complete. Video ID: {video_id}{' ' * 20}{Colors.RESET}")

playlist_id = get_or_create_playlist(youtube, "VALORANT")

youtube.playlistItems().insert(
    part="snippet",
    body={
        "snippet": {
            "playlistId": playlist_id,
            "resourceId": {"kind": "youtube#video", "videoId": video_id}
        }
    }
).execute()

print(f"{Colors.GREEN}Video added to VALORANT playlist.{Colors.RESET}")

media_body.stream().close()
