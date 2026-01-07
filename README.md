# Valorant clip automation
Fully automated (unless something breaks) Valorant highlight recording, compilation, and YouTube upload. triggered simply by turning on your PC.

This project automates your entire Valorant highlight workflow

All of this is controlled by a single startup batch file and one Python automation script.

## Flow
```text
PC boots
   ↓
startup batch file runs
   ↓
Valorant launches
   ↓
Valorant Tracker launches
   ↓
Script waits for game exit
   ↓
Clips are compiled with FFmpeg
   ↓
Video is uploaded to YouTube
   ↓
Local files are cleaned
   ↓
PC shuts down (optional)
```

## Requirements

- Windows 10/11
- Valorant
- Valorant Tracker (Overwolf)
- FFmpeg
- Python 3.10+
- Google YouTube Data API credentials

Python packages
`pip install google-api-python-client google-auth-oauthlib`

## Setup Guide
### Configure to run at Windows Startup
Press `Win + R` → type:

`shell:startup`

Place `valorant_watcher.bat` or its shortcut in this folder. 


### Edit Paths (One-time)

Update the following paths in:

- valorant_watcher.bat
- valorant_auto.py

Paths to update:

- Valorant shortcut path
- Valorant Tracker shortcut path
- Valorant clips directory
- Location of valorant_auto.py

### Setup YouTube API

- Create a project in Google Cloud Console
- Enable YouTube Data API v3
- Create OAuth credentials
- Download client_secret.json
- Place it next to valorant_auto.py
- On first run, a browser window will open for Google login authorization.

## Use Case - Why This Exists

Did you ever want to look back at your gaming skills from the past?

The insane clutches.  
The embarrassing whiffs.  
The late-night sessions that felt like they would never end.

One day you’ll load up a video and think:  
*"Damn… I was actually pretty good."*  
Or maybe: *"Wow… I really thought that was a good play."* 😅

As life moves forward, time becomes expensive, priorities change, and the grind slowly fades.  
Your mechanics soften.  
Your reflexes slow.  
Your interest drifts.

This automation exists so that **version of you never disappears.**

No more “I should’ve recorded that.”  
No more lost memories.  
No more regret.

Just press power, play the game, and let your future self thank you.
