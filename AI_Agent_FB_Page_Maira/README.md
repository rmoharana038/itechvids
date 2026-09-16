# Maira Dash Facebook AI Automated Posting Agent (4-Channel Multi-Publisher)

An autonomous AI agent that generates customized 9:16 vertical photorealistic portraits via a local free ChatGPT browser session using a reference face photo of **Maira Dash**, and automatically publishes them 5 times daily across **4 distinct Facebook channels**:
1. **Facebook Page Feed** ([facebook.com/Maira.Dash.Page](https://www.facebook.com/Maira.Dash.Page/))
2. **Facebook Page Story** (`Maira.Dash.Page`)
3. **Personal Profile Feed** ([facebook.com/maira.dash](https://www.facebook.com/maira.dash/))
4. **Personal Profile Story** (`maira.dash`)

---

## Persona & Characteristics

- **Name**: Maira Dash
- **Age**: 23 Years Old, Single Girl
- **Physique**: Natural curvy pear-shaped physique, radiant smile, warm expressive eyes, long hair.
- **Identity**: Social media influencer, fashion model, university student, fitness model.
- **Interests & Content Themes**:
  - **Fitness & Wellness**: Gym workouts, yoga, jogging, activewear, morning fitness, healthy smoothies.
  - **Fashion Modeling**: High-fashion studio shoots, chic modern streetwear, elegant Indian lehengas and sarees, bodycon dresses, beach resort wear.
  - **Student Life**: University campus, library study sessions, modern cafe study desks with laptop and coffee.
  - **Nightlife & Entertainment**: Clubbing, dancing, rooftop lounges, cinema and movie dates, weekend party glamour.
  - **Food & Dining**: Fast food diners (burgers, fries, momos, street food), aesthetic brunch cafes, fine dining luxury hotels, bubble tea, artisan desserts.
  - **Odisha Heritage & Tourism**: Puri Beach, Konark Sun Temple, Lingaraj Temple, Chilika Lake, Daringbadi hill station, Simlipal waterfalls, Marine Drive, Gopalpur.
  - **India Travel**: Kashmir (snow & Shikara boats), Mumbai (Marine Drive), Delhi (heritage & cafes), Jaipur (palaces), Kerala (backwaters), Hyderabad, Bangalore, Uttarakhand (Rishikesh), Northeast (Meghalaya), Nepal.
  - **International Travel**: Dubai (Burj Khalifa & desert safari), Thailand (Phuket beaches), Vietnam (Ha Long Bay & Hoi An), UK (London), US (New York & California), Canada (Banff), New Zealand (Queenstown), China, Japan (Kyoto & Tokyo).
  - **Nature & Scenic**: Misty hill stations, pine forest trails, river streams, golden hour clifftops.

---

## 4-Channel Publishing Pipeline

Every scheduled slot executes a seamless 4-stage publication sequence within a single browser session:
```
Slot Trigger (IST)
       │
       ▼
1. Dynamic 9:16 Photo Generation (ChatGPT Free Tier + Reference Face)
       │
       ▼
2. SHA-256 Anti-Duplicate Check
       │
       ├──► Stage 1: Facebook Page Feed (AI Label ON + Feeling + Location + Photo Preview Verified)
       │
       ├──► Stage 2: Facebook Page Story (Native 9:16 Photo + Story AI Label)
       │
       ├──► Context Switch to Personal Profile (maira.dash)
       │
       ├──► Stage 3: Personal Profile Feed (AI Label + Feeling + Location + Photo Preview Verified)
       │
       └──► Stage 4: Personal Profile Story (Native 9:16 Photo + Story AI Label)
```

---

## Key Features

- **5 Daily IST Schedules**: Posts automatically at `06:30 AM` (Good Morning), `11:30 AM` (Good Noon), `03:30 PM` (Good Afternoon), `06:30 PM` (Good Evening), and `09:00 PM` (Good Night) in Indian Standard Time (`Asia/Kolkata`).
- **Free ChatGPT Web Automation**: Uses a local persistent Chromium browser profile (`browser_profile/`) to generate high-resolution photorealistic images without paid API keys.
- **Dynamic Prompt Engine**: Automatically selects and builds rich non-repeating prompts reflecting Maira's persona, physique, and contextually matched outfits.
- **Strict 9:16 Aspect Ratio**: Automatically crops and verifies 9:16 vertical resolution (1024x1792 / 1080x1920) via Pillow.
- **Zero Repetition Guarantee**: Cryptographic SHA-256 hash tracking prevents ever reposting the same generated image.
- **Automated Profile Context Switching**: Intelligently switches between Facebook Page and Personal Profile within the same automated run.
- **Full Feed Metadata**:
  - Automatically enables **`+ AI label on`**.
  - Sets slot-specific **Feelings/Activities** (`blessed`, `happy`, `thankful`, `excited`, `peaceful`).
  - Tags Location as **`Odisha, India`**.
  - Verifies DOM image preview before publishing (protects against caption-only posts).
- **Native 9:16 Facebook Story Upload**:
  - Automatically uploads the full-screen 9:16 photo with native Story AI labels enabled for both Page and Profile.
- **Anti-Detection & Humanized Safety Guardrails**:
  - **Slot Timing Jitter**: Random delay (60–300s) before execution to prevent clockwork robotic schedule detection (bypassed with `--no-jitter` for manual testing).
  - **Humanized Reaction Delays**: Randomized hover pauses (`human_click`) and variable navigation intervals simulating natural human browsing behavior.
  - **Proactive Security Checkpoint Detection**: Scans page URLs and body text for identity verification or action blocks, saves diagnostic screenshots (`logs/security_checkpoint.png`), and cleanly aborts to protect account health.

---

## Project Structure

```
D:\Gemini\AI_Agent_FB_Page_Maira\
│
├── assets\
│   └── reference_face.jpg         # Master face reference photo of Maira Dash
│
├── browser_profile\               # Dedicated persistent browser session (ChatGPT & FB)
│
├── generated\                     # Saved generated images (9:16 vertical format)
│
├── logs\                          # Operational logs and history tracking
│   ├── agent.log                  # Central execution log
│   ├── windows_task.log           # Task Scheduler log
│   ├── posted_images.json         # SHA-256 duplicate protection registry
│   ├── prompt_history.json        # History of generated prompts
│   └── post_history.json          # Facebook post records
│
├── venv\                          # Python virtual environment
│
├── config.yaml                    # Master configuration (timings, greetings, feelings, URLs)
├── prompt_engine.py               # Generative prompt engine with rotating themes
├── chatgpt_agent.py               # Playwright ChatGPT automation & 9:16 cropper
├── facebook_publisher.py          # 4-Channel Feed & Story publisher (Page + Profile)
├── image_tracker.py               # SHA-256 duplicate image registry engine
├── scheduler.py                   # APScheduler background runner (IST)
├── main.py                        # Unified orchestrator & CLI
├── setup_accounts.py              # Account login helper (ChatGPT, Page & Personal Profile)
├── setup_accounts.bat             # Batch launcher for setup_accounts.py
├── install_windows_tasks.bat      # Registers 5 daily tasks in Windows Task Scheduler
├── uninstall_windows_tasks.bat    # Removes tasks from Windows Task Scheduler
├── run_slot.bat                   # Slot execution script invoked by Windows Task Scheduler
├── run_hidden.vbs                 # Silent background VBS runner
├── start_agent.bat                # Interactive Windows console launcher
├── requirements.txt               # Dependencies
├── README.md                      # Overview and setup guide
└── WORKFLOW.md                    # Technical workflow guide
```

---

## Setup & Quick Start

### 1. Account Login Setup
Double-click `setup_accounts.bat` (or run `python setup_accounts.py`):
1. A browser window will open tabs for ChatGPT, Facebook Page, and Personal Profile.
2. Log into your ChatGPT account.
3. Log into your Facebook account (ensure you have access to both **maira.dash** and **Maira.Dash.Page**).
4. Return to the terminal and press `ENTER` to save your session into `browser_profile/`.

### 2. Running Options

#### Option A: Native Windows Task Scheduler (Recommended - 100% Background)
Double-click:
```bat
install_windows_tasks.bat
```
This registers 5 daily tasks in Windows Task Scheduler under folder `AI_Agent_FB_Page_Maira`:
- **06:30 AM IST**: Good Morning (All 4 channels)
- **11:30 AM IST**: Good Noon (All 4 channels)
- **03:30 PM IST**: Good Afternoon (All 4 channels)
- **06:30 PM IST**: Good Evening (All 4 channels)
- **09:00 PM IST**: Good Night (All 4 channels)

Tasks execute silently in the background via `run_hidden.vbs` without opening any command window.

To uninstall scheduled tasks at any time, run:
```bat
uninstall_windows_tasks.bat
```

#### Option B: Interactive Launcher
Double-click `start_agent.bat` to open the control menu:
- Select **`1`** to run the 24/7 background scheduler in the terminal.
- Select **`2–6`** to test any slot on demand across all 4 channels.
- Select **`7`** to test ChatGPT image generation only.
- Select **`8`** to run Account Setup.
- Select **`9`** to install Windows Task Scheduler.
- Select **`10`** to uninstall Windows Task Scheduler.

#### Option C: Command Line (CLI)
```powershell
# Run the 24/7 background scheduler
.\venv\Scripts\python.exe main.py --run-scheduler

# Trigger a specific post immediately across all 4 channels
.\venv\Scripts\python.exe main.py --post-now morning
.\venv\Scripts\python.exe main.py --post-now noon
.\venv\Scripts\python.exe main.py --post-now afternoon
.\venv\Scripts\python.exe main.py --post-now evening
.\venv\Scripts\python.exe main.py --post-now night
```
