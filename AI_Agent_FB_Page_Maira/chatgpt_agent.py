"""
ChatGPT Web Automation Module - Maira Dash
Automates image generation using a reference face in ChatGPT via persistent browser context.
Enforces 9:16 vertical mobile aspect ratio (1024x1792 / 1080x1920).
"""

import os
import time
import base64
import logging
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

try:
    from playwright_stealth import stealth_sync
except ImportError:
    stealth_sync = None

logger = logging.getLogger("AgentLogger")

class ChatGPTAgent:
    def __init__(self, config):
        self.config = config
        self.profile_dir = Path(config["paths"]["browser_profile"]).resolve()
        self.generated_dir = Path(config["paths"]["generated_dir"]).resolve()
        self.generated_dir.mkdir(parents=True, exist_ok=True)
        self.chatgpt_cfg = config.get("chatgpt", {})
        self.headless = self.chatgpt_cfg.get("headless", False)
        self.timeout = self.chatgpt_cfg.get("timeout_seconds", 180) * 1000

    def generate_greeting_image(self, slot_key, prompt_text, reference_image_path=None):
        """
        Navigates to ChatGPT, uploads reference face image, submits prompt,
        waits for the image to be generated, and downloads it.
        Returns: Path to downloaded image, or None if failed.
        """
        if not reference_image_path:
            reference_image_path = self.config["paths"]["reference_face"]

        ref_path = Path(reference_image_path).resolve()
        if not ref_path.exists():
            logger.warning(f"Reference image not found at {ref_path}. Will proceed with text prompt only.")
            ref_path = None

        logger.info(f"Starting ChatGPT image generation for slot: {slot_key}")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = self.generated_dir / f"{slot_key}_{timestamp}.jpg"

        with sync_playwright() as p:
            logger.info("Launching browser with persistent profile...")
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                headless=self.headless,
                channel="chrome",
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--start-maximized",
                    "--no-sandbox"
                ],
                viewport=None
            )

            try:
                page = context.pages[0] if context.pages else context.new_page()
                if stealth_sync:
                    stealth_sync(page)

                logger.info("Navigating to ChatGPT (https://chatgpt.com)...")
                page.goto("https://chatgpt.com", wait_until="domcontentloaded", timeout=60000)
                time.sleep(4)

                # Check if logged in or blocked
                content_text = page.content()
                if "Log in" in content_text and "Sign up" in content_text and "prompt-textarea" not in content_text:
                    logger.error("ChatGPT does not appear to be logged in! Please run 'setup_accounts.bat' first.")
                    context.close()
                    return None

                # Locate prompt input
                logger.info("Locating chat prompt input...")
                input_selector = '#prompt-textarea'
                try:
                    page.wait_for_selector(input_selector, state="visible", timeout=20000)
                except Exception:
                    input_selector = 'div[contenteditable="true"], textarea[placeholder*="Message"]'
                    page.wait_for_selector(input_selector, state="visible", timeout=20000)

                # Attach reference face image if available
                if ref_path and ref_path.exists():
                    logger.info(f"Attaching reference face image: {ref_path}")
                    file_input = page.locator('input[type="file"]')
                    if file_input.count() > 0:
                        file_input.first.set_input_files(str(ref_path))
                        logger.info("Reference face image uploaded. Waiting for preview chip...")
                        time.sleep(5)
                    else:
                        logger.warning("Could not find file input element. Trying to click attachment button...")
                        attach_btn = page.locator('button[aria-label*="Attach"], button[aria-label*="upload"]').first
                        if attach_btn.is_visible():
                            with page.expect_file_chooser() as fc_info:
                                attach_btn.click()
                            file_chooser = fc_info.value
                            file_chooser.set_files(str(ref_path))
                            time.sleep(5)

                # Enter prompt
                full_prompt = (
                    f"Please generate a vertical 9:16 aspect ratio (1024x1792) portrait based on the attached face reference: {prompt_text}\n"
                    "Requirements: Full color, photorealistic, 9:16 vertical portrait orientation."
                ) if ref_path else (
                    f"Please generate a vertical 9:16 aspect ratio (1024x1792) high-quality, photorealistic portrait: {prompt_text}\n"
                    "Requirements: Full color, photorealistic, 9:16 vertical portrait orientation."
                )

                logger.info("Entering prompt...")
                prompt_el = page.locator(input_selector).first
                prompt_el.click()
                time.sleep(1)
                prompt_el.fill(full_prompt)
                time.sleep(2)

                # Click Send button
                logger.info("Submitting prompt to ChatGPT...")
                send_button = page.locator('button[data-testid="send-button"], button[aria-label="Send prompt"], button[aria-label="Send message"]').first
                if send_button.is_visible() and send_button.is_enabled():
                    send_button.click()
                else:
                    prompt_el.press("Enter")

                logger.info("Prompt submitted. Waiting for image generation to complete (this may take 30-90 seconds)...")

                # Wait for generation to start and finish
                start_time = time.time()
                generated_img_locator = None

                # Sleep to let generation start
                time.sleep(10)

                # Loop until an image appears in the assistant's response
                image_found = False
                while time.time() - start_time < (self.timeout / 1000):
                    # Check for rate limit / error messages
                    body_text = page.locator('body').inner_text()
                    if "reached your limit" in body_text or "You've reached your image" in body_text:
                        logger.error("ChatGPT image generation limit reached on free account.")
                        break

                    # Look for generated image in assistant messages
                    images = page.locator('div[data-message-author-role="assistant"] img, img[alt*="Generated"], img[alt*="DALL·E"], div.group img')
                    count = images.count()

                    for idx in range(count - 1, -1, -1):
                        img = images.nth(idx)
                        src = img.get_attribute("src") or ""
                        if src and not src.startswith("data:image/svg") and ("oaiusercontent" in src or "blob:" in src or "chatgpt.com" in src or len(src) > 200):
                            box = img.bounding_box()
                            if box and box["width"] > 150 and box["height"] > 150:
                                generated_img_locator = img
                                image_found = True
                                break

                    if image_found:
                        # Ensure generation has stopped (no active stop button)
                        stop_btn = page.locator('button[data-testid="stop-button"], button[aria-label="Stop streaming"]')
                        if stop_btn.count() == 0 or not stop_btn.first.is_visible():
                            logger.info("Image generation complete and settled!")
                            break

                    time.sleep(3)

                if not image_found or not generated_img_locator:
                    logger.error("Timed out or failed to detect generated image in ChatGPT.")
                    context.close()
                    return None

                # Extract image content directly via browser evaluate (bypasses CORS/auth)
                logger.info("Downloading generated image via browser memory...")
                time.sleep(2)
                base64_data = generated_img_locator.evaluate("""
                    async (img) => {
                        const response = await fetch(img.src);
                        const blob = await response.blob();
                        return new Promise((resolve) => {
                            const reader = new FileReader();
                            reader.onloadend = () => resolve(reader.result);
                            reader.readAsDataURL(blob);
                        });
                    }
                """)

                if base64_data and "," in base64_data:
                    img_bytes = base64.b64decode(base64_data.split(",")[1])
                    with open(output_filename, "wb") as f:
                        f.write(img_bytes)
                    self.enforce_9_16_ratio(output_filename)
                    logger.info(f"Generated image (9:16 ratio) saved successfully to: {output_filename}")
                    context.close()
                    return str(output_filename)
                else:
                    logger.error("Failed to extract image base64 data.")
                    context.close()
                    return None

            except Exception as e:
                logger.exception(f"Error during ChatGPT automation: {e}")
                context.close()
                return None

    def enforce_9_16_ratio(self, file_path):
        """
        Guarantees that the saved image strictly has a 9:16 vertical aspect ratio.
        If ChatGPT returns square or another ratio, crops cleanly from center to 9:16.
        """
        try:
            from PIL import Image
            path = Path(file_path)
            if not path.exists():
                return

            with Image.open(path) as img:
                w, h = img.size
                target_ratio = 9.0 / 16.0  # 0.5625
                current_ratio = w / h

                if abs(current_ratio - target_ratio) < 0.03:
                    logger.info(f"Image already matches 9:16 vertical ratio ({w}x{h}).")
                    return

                if current_ratio > target_ratio:
                    # Too wide: crop width to 9:16
                    new_w = int(h * target_ratio)
                    left = (w - new_w) // 2
                    right = left + new_w
                    cropped = img.crop((left, 0, right, h))
                    cropped.save(path, quality=95)
                    logger.info(f"Adjusted image to exact 9:16 vertical ratio: {cropped.size}")
                else:
                    # Too tall: crop height to 9:16
                    new_h = int(w / target_ratio)
                    top = (h - new_h) // 2
                    bottom = top + new_h
                    cropped = img.crop((0, top, w, bottom))
                    cropped.save(path, quality=95)
                    logger.info(f"Adjusted image to exact 9:16 vertical ratio: {cropped.size}")
        except Exception as e:
            logger.warning(f"Note on enforcing 9:16 ratio on {file_path}: {e}")

if __name__ == "__main__":
    import yaml
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    with open("config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    agent = ChatGPTAgent(cfg)
    test_slot = "morning"
    prompt = cfg["slots"][test_slot]["prompt"]
    img_path = agent.generate_greeting_image(test_slot, prompt)
    print(f"Result image path: {img_path}")
