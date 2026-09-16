"""
Main Orchestration Script for Facebook Page & Profile Automated Posting Agent - Maira Dash
Coordinates ChatGPT image generation, Facebook 4-channel multi-publishing, and scheduling:
1. Facebook Page Feed (Maira.Dash.Page)
2. Facebook Page Story (Maira.Dash.Page)
3. Personal Profile Feed (maira.dash)
4. Personal Profile Story (maira.dash)
"""

import os
import sys
import argparse
import logging
from pathlib import Path
import yaml
from datetime import datetime
import pytz

from chatgpt_agent import ChatGPTAgent
from facebook_publisher import FacebookPublisher
from scheduler import PostScheduler
from prompt_engine import PromptEngine
from image_tracker import ImageTracker

def setup_logger(log_file_path):
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    log_path = Path(log_file_path).resolve()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("AgentLogger")
    logger.setLevel(logging.INFO)
    logger.handlers = []

    # File Handler
    fh = logging.FileHandler(str(log_path), encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh.setFormatter(fh_formatter)
    logger.addHandler(fh)

    # Console Handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    ch.setFormatter(ch_formatter)
    logger.addHandler(ch)

    return logger

def load_config(config_path="config.yaml"):
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def run_slot_pipeline(slot_key, config, logger):
    """
    Executes end-to-end flow for a specific slot:
    1. Generates 9:16 vertical image via ChatGPT with reference face
    2. Verifies uniqueness via SHA-256 registry
    3. Builds caption with hashtags & greetings
    4. Publishes to 4 channels: Page Feed, Page Story, Profile Feed, Profile Story
    """
    slots = config.get("slots", {})
    if slot_key not in slots:
        logger.error(f"Slot '{slot_key}' not found in configuration.")
        return {"success": False, "error": f"Invalid slot '{slot_key}'"}

    slot_info = slots[slot_key]
    label = slot_info.get("label", slot_key)
    greeting = slot_info.get("greeting", "")
    hashtags = slot_info.get("hashtags", "")

    logger.info("==================================================")
    logger.info(f"Starting execution for Maira Dash: [{label}] ({slot_key})")
    logger.info("==================================================")

    # Step 1: Generate dynamic, non-repeating 9:16 prompt
    prompt_engine = PromptEngine()
    tracker = ImageTracker()
    dynamic_prompt = prompt_engine.generate_prompt(slot_key, label)

    # Step 2: Generate unique image with ChatGPT
    chatgpt = ChatGPTAgent(config)
    ref_image = config["paths"].get("reference_face", "assets/reference_face.jpg")
    logger.info(f"Step 1: Generating custom 9:16 image via ChatGPT for {label}...")
    image_path = chatgpt.generate_greeting_image(
        slot_key=slot_key,
        prompt_text=dynamic_prompt,
        reference_image_path=ref_image
    )

    if not image_path or not Path(image_path).exists():
        logger.error("ChatGPT did not produce an image. Aborting to avoid posting without an image.")
        return {"success": False, "error": "No image generated"}

    # STRICT CHECK: Verify this image was never posted before
    if tracker.is_already_posted(image_path):
        logger.error(f"Image {image_path} was already published in a previous post! Aborting to prevent duplicate posting.")
        return {"success": False, "error": "Duplicate image detected; will not repost"}

    # Step 3: Compose Caption
    full_caption = f"{greeting}\n\n{hashtags}"
    logger.info("Step 2: Composed Facebook caption:\n" + ("-" * 40) + f"\n{full_caption}\n" + ("-" * 40))

    # Step 4: Publish to 4 Facebook channels:
    # 1. Page Feed
    # 2. Page Story
    # 3. Personal Profile Feed
    # 4. Personal Profile Story
    logger.info(f"Step 3: Launching 4-channel publishing campaign with image: {image_path}")
    publisher = FacebookPublisher(config)
    location = config.get("facebook", {}).get("location", "Odisha, India")
    ai_label = config.get("facebook", {}).get("ai_label", True)

    publish_result = publisher.publish_full_campaign(
        caption_text=full_caption,
        image_path=image_path,
        slot_info=slot_info,
        location=location,
        ai_label=ai_label
    )

    if publish_result.get("success"):
        logger.info(f"SUCCESS: Slot [{label}] campaign completed successfully!")
        # Record image in registry to ensure it is never posted again
        tracker.record_posted(image_path, slot_key, full_caption)
    else:
        logger.error(f"FAILED: Campaign encountered errors: {publish_result.get('error')}")

    return {
        "slot": slot_key,
        "label": label,
        "image": str(image_path),
        "result": publish_result
    }

def main():
    parser = argparse.ArgumentParser(description="Facebook Page & Profile 5x Daily Automated Posting Agent - Maira Dash (IST)")
    parser.add_argument("--config", default="config.yaml", help="Path to config file")
    parser.add_argument("--run-scheduler", action="store_true", help="Start the 24/7 background scheduler (IST)")
    parser.add_argument("--post-now", choices=["morning", "noon", "afternoon", "evening", "night"], help="Immediately generate and post for a specific slot")
    parser.add_argument("--test-chatgpt", choices=["morning", "noon", "afternoon", "evening", "night"], help="Test ChatGPT image generation only")
    parser.add_argument("--test-facebook", action="store_true", help="Test Facebook 4-channel publishing with a sample image")
    parser.add_argument("--install-tasks", action="store_true", help="Install the 5 daily tasks into Windows Task Scheduler")
    parser.add_argument("--uninstall-tasks", action="store_true", help="Remove all 5 daily tasks from Windows Task Scheduler")

    args = parser.parse_args()
    config = load_config(args.config)
    logger = setup_logger(config["paths"]["log_file"])

    if args.install_tasks:
        os.system("install_windows_tasks.bat")
        return

    if args.uninstall_tasks:
        os.system("uninstall_windows_tasks.bat")
        return

    if hasattr(args, "post_now") and args.post_now:
        slot = args.post_now
        run_slot_pipeline(slot, config, logger)
        return

    if args.test_chatgpt:
        slot = args.test_chatgpt
        slot_info = config["slots"][slot]
        chatgpt = ChatGPTAgent(config)
        prompt_engine = PromptEngine()
        dynamic_prompt = prompt_engine.generate_prompt(slot, slot_info["label"])
        img = chatgpt.generate_greeting_image(slot, dynamic_prompt)
        print(f"\n[Test Result] Generated image path: {img}")
        return

    if args.test_facebook:
        publisher = FacebookPublisher(config)
        gen_dir = Path(config["paths"]["generated_dir"])
        gen_imgs = list(gen_dir.glob("*.jpg"))
        test_img = str(gen_imgs[0]) if gen_imgs else config["paths"]["reference_face"]
        res = publisher.publish_full_campaign(
            caption_text="Test 4-channel post from Maira Dash automated agent! 💖✨\n\n#Testing #Automation",
            image_path=test_img,
            slot_info=config["slots"]["morning"]
        )
        print(f"\n[Test Result] Facebook campaign result: {res}")
        return

    if args.run_scheduler:
        def on_trigger(slot_key):
            return run_slot_pipeline(slot_key, config, logger)

        scheduler = PostScheduler(config, on_trigger)
        scheduler.start()
        return

    # Interactive menu if no arguments passed
    print("\n" + "=" * 65)
    print("   MAIRA DASH FACEBOOK 4-CHANNEL POSTING AGENT (IST SCHEDULE)")
    print("   Channels: Page Feed, Page Story, Profile Feed, Profile Story")
    print("=" * 65)
    print("Select an option:")
    print(" 1. Start 24/7 Python Scheduler (In this terminal)")
    print(" 2. Post 'Good Morning' now (All 4 channels)")
    print(" 3. Post 'Good Noon' now (All 4 channels)")
    print(" 4. Post 'Good Afternoon' now (All 4 channels)")
    print(" 5. Post 'Good Evening' now (All 4 channels)")
    print(" 6. Post 'Good Night' now (All 4 channels)")
    print(" 7. Test ChatGPT Image Generation only")
    print(" 8. Run Account Login Setup (ChatGPT & Facebook)")
    print(" 9. Install Windows Task Scheduler (Runs in background, no terminal needed)")
    print(" 10. Uninstall Windows Task Scheduler")
    print(" 11. Exit")
    print("=" * 65)

    choice = input("\nEnter choice [1-11]: ").strip()
    slot_map = {
        "2": "morning",
        "3": "noon",
        "4": "afternoon",
        "5": "evening",
        "6": "night"
    }

    if choice == "1":
        def on_trigger(slot_key):
            return run_slot_pipeline(slot_key, config, logger)
        scheduler = PostScheduler(config, on_trigger)
        scheduler.start()
    elif choice in slot_map:
        run_slot_pipeline(slot_map[choice], config, logger)
    elif choice == "7":
        slot = "morning"
        slot_info = config["slots"][slot]
        chatgpt = ChatGPTAgent(config)
        prompt_engine = PromptEngine()
        dynamic_prompt = prompt_engine.generate_prompt(slot, slot_info["label"])
        img = chatgpt.generate_greeting_image(slot, dynamic_prompt)
        print(f"Result: {img}")
    elif choice == "8":
        import setup_accounts
        setup_accounts.run_setup()
    elif choice == "9":
        os.system("install_windows_tasks.bat")
    elif choice == "10":
        os.system("uninstall_windows_tasks.bat")
    else:
        print("Exiting.")

if __name__ == "__main__":
    main()
