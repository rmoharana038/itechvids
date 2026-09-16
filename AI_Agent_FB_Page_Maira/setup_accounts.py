"""
Setup Script for Persistent Browser Profile (ChatGPT & Facebook) - Maira Dash
Run this script once to log into ChatGPT and Facebook in a persistent browser window.
Your session and cookies will be saved in 'browser_profile/' for the automated agent.
"""

import os
import sys
import yaml
from pathlib import Path
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def run_setup():
    config = load_config()
    profile_dir = Path(config["paths"]["browser_profile"]).resolve()
    profile_dir.mkdir(parents=True, exist_ok=True)
    page_url = config.get("facebook", {}).get("page_url", "https://www.facebook.com/Maira.Dash.Page/")
    profile_url = config.get("facebook", {}).get("profile_url", "https://www.facebook.com/maira.dash/")

    print("=" * 75)
    print("      MAIRA DASH FACEBOOK & CHATGPT AGENT - ONE-TIME ACCOUNT SETUP")
    print("=" * 75)
    print(f"Browser profile directory: {profile_dir}")
    print(f"Facebook Page URL:         {page_url}")
    print(f"Personal Profile URL:      {profile_url}")
    print("\nA browser window will open shortly.")
    print("Please follow these steps:")
    print(" 1. In the ChatGPT tab, log into your free ChatGPT account.")
    print("    Make sure you can see the chat input box.")
    print(" 2. In the Facebook tab, log into your personal Facebook account (maira.dash).")
    print(" 3. Verify you have access to switch into the Page (Maira.Dash.Page).")
    print(" 4. When finished, return to this terminal and press ENTER to save.")
    print("=" * 75)

    input("\nPress ENTER to launch the browser...")

    with sync_playwright() as p:
        # Launch Chromium with persistent context
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=False,
            channel="chrome",  # Uses installed Google Chrome for best compatibility
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
                "--no-sandbox"
            ],
            viewport=None
        )

        page = context.pages[0] if context.pages else context.new_page()

        print("\nOpening ChatGPT (https://chatgpt.com)...")
        try:
            page.goto("https://chatgpt.com", timeout=60000)
        except Exception as e:
            print(f"Note: {e}")

        # Also open Facebook Page in a second tab
        fb_page = context.new_page()
        print(f"Opening Facebook Page ({page_url})...")
        try:
            fb_page.goto(page_url, timeout=60000)
        except Exception as e:
            print(f"Note: {e}")

        # Also open Personal Profile in a third tab
        profile_tab = context.new_page()
        print(f"Opening Personal Profile ({profile_url})...")
        try:
            profile_tab.goto(profile_url, timeout=60000)
        except Exception as e:
            print(f"Note: {e}")

        print("\n--> The browser is now open with ChatGPT, Facebook Page, and Personal Profile.")
        print("--> Complete your logins in the browser window.")
        input("\nWhen you are completely logged into both ChatGPT and Facebook, press ENTER here to save and close...")

        print("\nSaving session and closing browser...")
        context.close()
        print("Session successfully saved! Your agent can now use these authenticated sessions for all 4 channels.")

if __name__ == "__main__":
    run_setup()
