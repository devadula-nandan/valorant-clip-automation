import os
import subprocess
from pathlib import Path
from datetime import datetime
import time
import msvcrt
from send2trash import send2trash
import google_auth_oauthlib.flow
import googleapiclient.discovery
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

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
# SHUTDOWN PROMPT
# ===========================
print(f"{Colors.YELLOW}Do you want to shut down the PC after uploading? (y/n): {Colors.RESET}", end="", flush=True)

while True:
    key = msvcrt.getch().decode().lower()
    if key in ("y", "n"):
        print(key)  # Echo the choice so the user can see it
        shutdown_pc = key == "y"
        break

# ===========================
# CONFIGURATION
# ===========================
BASE_DIR = r"C:\Users\username\Videos\Overwolf\Valorant Tracker\VALORANT"
TEMP_DIR = Path(os.environ['TEMP'])
OUTPUT = TEMP_DIR / f"valorant_highlights_{datetime.now().strftime('%Y%m%d_%H%M')}.mp4"
LIST_FILE = TEMP_DIR / "list.txt"
SCRIPT_DIR = Path(__file__).resolve().parent
CLIENT_SECRET = SCRIPT_DIR / "client_secret.json" # Get this from your google cloud console

# ===========================
# COMPILE ALL CLIPS INTO ONE VIDEO
# ===========================
with open(LIST_FILE, "w", encoding="utf-8") as f:
    for folder in Path(BASE_DIR).iterdir():
        for clip in folder.glob("*.mp4"):
            f.write(f"file '{clip.as_posix()}'\n")

print(f"{Colors.YELLOW}Compiling video...{Colors.RESET}")

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
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    CLIENT_SECRET,
    scopes=["https://www.googleapis.com/auth/youtube.upload"]
)
credentials = flow.run_local_server(port=8080)

youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

media_body = MediaFileUpload(
    str(OUTPUT),
    chunksize=1024 * 1024,
    resumable=True
)

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
# UPLOAD LOOP WITH RETRY HANDLING
# ===========================
while response is None:
    try:
        status, response = request.next_chunk()

        if status:
            percent = int(status.progress() * 100)
            print(f"\r{Colors.BLUE}Upload progress: {percent:3d}%{Colors.RESET}", end="", flush=True)

    except HttpError as e:
        # Hard failure — DO NOT RETRY
        if "uploadLimitExceeded" in str(e) or "exceeded the number of videos" in str(e):
            print(f"\n{Colors.RED}Upload failed: Daily upload limit reached. No retry will be attempted.{Colors.RESET}")
            break

        # Transient failure — safe to retry
        print(f"\n{Colors.YELLOW}Transient upload error. Retrying in 10 seconds...{Colors.RESET}")
        time.sleep(10)

if response:
    print(f"\r{Colors.GREEN}Upload complete. Video ID: {response['id']}{' ' * 20}{Colors.RESET}")
else:
    print(f"{Colors.RED}Upload aborted.{Colors.RESET}")
    exit(1)

media_body.stream().close()

# ===========================
# CLEAN UP TEMP FILES
# ===========================
if LIST_FILE.exists():
    send2trash(str(LIST_FILE))
if OUTPUT.exists():
    send2trash(str(OUTPUT))

# ===========================
# EMPTY VALORANT CLIP FOLDER
# ===========================
print(f"{Colors.YELLOW}Sending all clips to the Recycle Bin...{Colors.RESET}")

for item in Path(BASE_DIR).iterdir():
    send2trash(str(item))

print(f"{Colors.GREEN}Valorant folder successfully emptied.{Colors.RESET}")

# ===========================
# OPTIONAL SYSTEM SHUTDOWN
# ===========================
if shutdown_pc:
    print(f"{Colors.YELLOW}Shutting down the PC in 10 seconds...{Colors.RESET}")
    os.system("shutdown /s /t 10")
else:
    print(f"{Colors.YELLOW}Shutdown skipped.{Colors.RESET}")
