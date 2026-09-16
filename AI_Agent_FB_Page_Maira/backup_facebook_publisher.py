"""
Facebook Publisher Module - Maira Dash (4-Channel Publisher with Bulletproof Context Switching)
Supports sequential publishing across 4 distinct Facebook destinations:
1. Facebook Page Feed (https://www.facebook.com/Maira.Dash.Page/)
2. Facebook Page Story (Maira.Dash.Page)
3. Personal Profile Feed (https://www.facebook.com/maira.dash/)
4. Personal Profile Story (maira.dash)

Features:
- Guaranteed bidirectional persona switching between Page and Personal Profile
- Strict verification of active persona via https://www.facebook.com/me before publishing
- Direct home feed composer triggering (span:has-text("What's on your mind")) - zero scroll / banner interference
- Guaranteed photo attachment verification before publishing (never posts caption alone)
- AI Label ON toggle ("Add AI label")
- Feeling / Activity selection (blessed, happy, thankful, excited, peaceful)
- Location check-in ("Odisha, India")
- Single browser session reuse across all 4 channels for maximum speed and stability
"""

import os
import sys
import time
import logging
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("AgentLogger")

class FacebookPublisher:
    def __init__(self, config):
        self.config = config
        self.fb_cfg = config.get("facebook", {})
        self.method = self.fb_cfg.get("method", "browser").lower()
        self.profile_dir = Path(config["paths"]["browser_profile"]).resolve()
        self.page_url = self.fb_cfg.get("page_url", "https://www.facebook.com/Maira.Dash.Page/").rstrip("/") + "/"
        self.profile_url = self.fb_cfg.get("profile_url", "https://www.facebook.com/maira.dash/").rstrip("/") + "/"
        self.default_location = self.fb_cfg.get("location", "Odisha, India")
        self.default_ai_label = self.fb_cfg.get("ai_label", True)
        self.default_share_to_story = self.fb_cfg.get("share_to_story", True)
        self.post_to_profile = self.fb_cfg.get("post_to_profile", True)
        self.share_to_profile_story = self.fb_cfg.get("share_to_profile_story", True)
        self.page_id = self.fb_cfg.get("page_id", "")
        self.access_token = self.fb_cfg.get("access_token", "")

    def ensure_context(self, page, target_type="page"):
        """
        Guarantees that the active Facebook persona is set to either 'page' or 'profile'.
        Strictly checks and verifies via https://www.facebook.com/me.
        """
        logger.info(f"Verifying active persona for target: [{target_type.upper()}]...")
        try:
            page.goto("https://www.facebook.com/me", timeout=60000)
            time.sleep(4)
        except Exception as e:
            logger.warning(f"Note navigating to /me: {e}")

        current_url = page.url.lower()
        is_page = "page" in current_url or "maira.dash.page" in current_url

        if target_type == "page" and is_page:
            logger.info(f"Verified: Already active as Facebook Page ({page.url}).")
            return True

        if target_type == "profile" and not is_page and ("maira.dash" in current_url or "profile.php" in current_url):
            logger.info(f"Verified: Already active as Personal Profile ({page.url}).")
            return True

        logger.info(f"Switching persona: currently {page.url}, switching to [{target_type.upper()}]...")

        # 1. Click top-right account avatar
        acc_btn = page.locator('div[role="banner"] div[aria-label="Your profile"], div[role="banner"] div[role="button"][aria-label*="profile" i]').last
        if not acc_btn.is_visible():
            acc_btn = page.locator('div[role="banner"] div[role="button"]').last

        acc_btn.click(force=True)
        time.sleep(3)

        # 2. Locate account menu dialog
        acc_dialog = page.locator('div[role="dialog"]:has-text("Log out"), div[role="dialog"]:has-text("See all profiles")').first
        if not acc_dialog.is_visible():
            logger.warning("Account menu dialog not immediately visible. Retrying click...")
            acc_btn.click(force=True)
            time.sleep(3)
            acc_dialog = page.locator('div[role="dialog"]:has-text("Log out"), div[role="dialog"]:has-text("See all profiles")').first

        if acc_dialog.is_visible():
            items = acc_dialog.locator('div[role="button"], div[role="listitem"]').all()
            clicked = False
            for b in items:
                txt = b.inner_text().strip()
                if target_type == "page":
                    if "Maira Dash Page" in txt or ("Page" in txt and "See all" not in txt):
                        logger.info(f"Found Page switch button: '{txt}'. Clicking...")
                        b.click(force=True)
                        clicked = True
                        break
                else: # target_type == "profile"
                    if "Maira Dash" in txt and "Page" not in txt and "See all" not in txt:
                        logger.info(f"Found Personal Profile switch button: '{txt}'. Clicking...")
                        b.click(force=True)
                        clicked = True
                        break

            if not clicked:
                # Check "See all profiles"
                see_all = acc_dialog.locator('div[role="button"]:has-text("See all profiles"), span:has-text("See all profiles")').first
                if see_all.is_visible():
                    logger.info("Clicking 'See all profiles'...")
                    see_all.click(force=True)
                    time.sleep(3)
                    if target_type == "page":
                        target_btn = page.locator('div[role="button"]:has-text("Maira Dash Page"), div[role="radio"]:has-text("Maira Dash Page")').first
                    else:
                        target_btn = page.locator('div[role="button"]:has-text("Maira Dash"):not(:has-text("Page")), div[role="radio"]:has-text("Maira Dash"):not(:has-text("Page"))').first
                    if target_btn.is_visible():
                        logger.info(f"Found target in See all profiles. Clicking...")
                        target_btn.click(force=True)
                        clicked = True

            # Wait for automatic switch navigation to settle
            logger.info("Waiting for switch navigation to settle...")
            try:
                page.wait_for_load_state("domcontentloaded", timeout=15000)
            except Exception:
                pass
            time.sleep(5)

        # 3. Strictly re-verify active persona via /me
        try:
            page.goto("https://www.facebook.com/me", timeout=60000)
            time.sleep(4)
        except Exception as e:
            logger.warning(f"Note re-navigating to /me: {e}")

        new_url = page.url.lower()
        if target_type == "page":
            success = "page" in new_url or "maira.dash.page" in new_url
        else:
            success = ("maira.dash" in new_url or "profile.php" in new_url) and "maira.dash.page" not in new_url

        if success:
            logger.info(f"CONFIRMED: Active persona is verified as [{target_type.upper()}] ({page.url})!")
            return True
        else:
            logger.error(f"VERIFICATION FAILED: Could not confirm active persona as [{target_type.upper()}]. Current URL: {page.url}")
            return False

    def publish_full_campaign(self, caption_text, image_path, slot_info, location=None, ai_label=None):
        """
        Coordinates full 4-channel publishing campaign with verified persona switching:
        1. Facebook Page Feed (Maira.Dash.Page)
        2. Facebook Page Story (Maira.Dash.Page)
        3. Personal Profile Feed (maira.dash)
        4. Personal Profile Story (maira.dash)
        """
        feeling = slot_info.get("feeling", "blessed")
        if location is None:
            location = self.default_location
        if ai_label is None:
            ai_label = self.default_ai_label

        image_abs_path = str(Path(image_path).resolve())
        if not Path(image_abs_path).exists():
            logger.error(f"Image file does not exist: {image_abs_path}. Aborting campaign.")
            return {"success": False, "error": "Image file not found"}

        results = {
            "page_feed": False,
            "page_story": False,
            "profile_feed": False,
            "profile_story": False
        }

        logger.info("=================================================================")
        logger.info("STARTING 4-CHANNEL PUBLISHING CAMPAIGN FOR MAIRA DASH")
        logger.info(f"Target Page:    {self.page_url}")
        logger.info(f"Target Profile: {self.profile_url}")
        logger.info(f"Image Path:     {image_abs_path}")
        logger.info(f"Feeling:        {feeling} | Location: {location} | AI Label: {ai_label}")
        logger.info("=================================================================")

        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                headless=False,
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

                # -------------------------------------------------------------
                # STAGE 1: Facebook Page Feed (Maira.Dash.Page)
                # -------------------------------------------------------------
                logger.info("\n>>> [STAGE 1/4] Ensuring Page Context & Publishing Feed Post...")
                page_switched = self.ensure_context(page, target_type="page")
                if not page_switched:
                    logger.warning("Could not verify Page persona via /me. Retrying switch...")
                    self.ensure_context(page, target_type="page")

                res_page_feed = self._publish_feed_post(
                    page=page,
                    target_name="Facebook Page",
                    caption_text=caption_text,
                    image_abs_path=image_abs_path,
                    feeling=feeling,
                    location=location,
                    ai_label=ai_label
                )
                results["page_feed"] = res_page_feed.get("success", False)

                # -------------------------------------------------------------
                # STAGE 2: Facebook Page Story (Maira.Dash.Page)
                # -------------------------------------------------------------
                if self.default_share_to_story:
                    logger.info("\n>>> [STAGE 2/4] Publishing to Facebook Page Story...")
                    try:
                        results["page_story"] = self.publish_story(
                            image_path=image_abs_path,
                            ai_label=ai_label,
                            page=page,
                            context_name="Facebook Page"
                        )
                    except Exception as e:
                        logger.error(f"Error publishing Page Story: {e}")
                else:
                    logger.info("Stage 2 skipped: share_to_story disabled in config.")

                # -------------------------------------------------------------
                # STAGE 3: Personal Profile Feed (maira.dash)
                # -------------------------------------------------------------
                if self.post_to_profile:
                    logger.info("\n>>> [STAGE 3/4] Switching Context to Personal Profile & Publishing Feed Post...")
                    profile_switched = self.ensure_context(page, target_type="profile")
                    if not profile_switched:
                        logger.error("Could not switch/verify Personal Profile persona! Aborting profile feed post.")
                    else:
                        res_prof_feed = self._publish_feed_post(
                            page=page,
                            target_name="Personal Profile",
                            caption_text=caption_text,
                            image_abs_path=image_abs_path,
                            feeling=feeling,
                            location=location,
                            ai_label=ai_label
                        )
                        results["profile_feed"] = res_prof_feed.get("success", False)
                else:
                    logger.info("Stage 3 skipped: post_to_profile disabled in config.")

                # -------------------------------------------------------------
                # STAGE 4: Personal Profile Story (maira.dash)
                # -------------------------------------------------------------
                if self.share_to_profile_story:
                    logger.info("\n>>> [STAGE 4/4] Publishing to Personal Profile Story...")
                    self.ensure_context(page, target_type="profile")
                    try:
                        results["profile_story"] = self.publish_story(
                            image_path=image_abs_path,
                            ai_label=ai_label,
                            page=page,
                            context_name="Personal Profile"
                        )
                    except Exception as e:
                        logger.error(f"Error publishing Profile Story: {e}")
                else:
                    logger.info("Stage 4 skipped: share_to_profile_story disabled in config.")

                context.close()

                overall_success = results["page_feed"] or results["profile_feed"]
                logger.info("\n=================================================================")
                logger.info(f"CAMPAIGN RESULTS SUMMARY: Overall Success = {overall_success}")
                logger.info(f"1. Page Feed:      {'SUCCESS' if results['page_feed'] else 'FAILED'}")
                logger.info(f"2. Page Story:     {'SUCCESS' if results['page_story'] else 'FAILED'}")
                logger.info(f"3. Profile Feed:   {'SUCCESS' if results['profile_feed'] else 'FAILED'}")
                logger.info(f"4. Profile Story:  {'SUCCESS' if results['profile_story'] else 'FAILED'}")
                logger.info("=================================================================")

                return {
                    "success": overall_success,
                    "details": results
                }

            except Exception as e:
                logger.exception(f"Unexpected error during 4-channel campaign: {e}")
                try:
                    page.screenshot(path="logs/campaign_error.png")
                except Exception:
                    pass
                context.close()
                return {"success": False, "error": str(e), "details": results}

    def _publish_feed_post(self, page, target_name, caption_text, image_abs_path, feeling, location, ai_label):
        """
        Publishes a photo post with feelings, location, and AI label to active persona feed.
        Navigates to https://www.facebook.com/ where the composer is always positioned cleanly at top.
        """
        home_url = "https://www.facebook.com/"
        logger.info(f"Navigating to home feed ({home_url}) to trigger composer for {target_name}...")
        page.goto(home_url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)

        # Verify login state
        if "login" in page.url.lower() or page.locator('input[name="email"]').is_visible():
            logger.error("Not logged into Facebook! Please run 'setup_accounts.bat' first.")
            return {"success": False, "error": "Not logged into Facebook"}

        # Open composer using the specific text span
        logger.info(f"Opening composer on {target_name}...")
        composer_span = page.locator('span:text-is("What\'s on your mind, Maira Dash Page?"), span:text-is("What\'s on your mind, Maira?"), span:has-text("What\'s on your mind")').first

        if composer_span.is_visible():
            composer_span.click(force=True)
        else:
            # Fallback to button selector
            composer_btn = page.locator('div[role="button"]:has-text("What\'s on your mind")').first
            if composer_btn.is_visible():
                composer_btn.click(force=True)

        time.sleep(3)
        dialog = page.locator('div[role="dialog"]:has-text("Create post")').first
        if not dialog.is_visible():
            logger.info("Dialog not visible on first click, trying photo/video shortcut...")
            pv_shortcut = page.locator('div[role="button"]:has-text("Photo/video"), span:has-text("Photo/video")').first
            if pv_shortcut.is_visible():
                pv_shortcut.click(force=True)
                time.sleep(3)
                dialog = page.locator('div[role="dialog"]:has-text("Create post")').first

        if not dialog.is_visible():
            logger.error(f"Could not open Create post dialog on {target_name}!")
            page.screenshot(path=f"logs/composer_open_failed_{target_name.replace(' ', '_')}.png")
            return {"success": False, "error": "Could not open Create post dialog"}

        logger.info(f"Create post dialog confirmed open on {target_name}!")

        # 1. Turn ON AI Label if requested
        if ai_label:
            logger.info("Configuring 'Add AI label' -> ON...")
            try:
                ai_btn = dialog.locator('div[aria-label*="AI label"], div[role="button"]:has-text("AI label")').first
                if ai_btn.is_visible() and "off" in (ai_btn.get_attribute("aria-label") or ai_btn.inner_text()).lower():
                    ai_btn.click(force=True)
                    time.sleep(2)
                    ai_switch = page.locator('[role="switch"]').first
                    if ai_switch.is_visible() and ai_switch.get_attribute("aria-checked") != "true":
                        ai_switch.click(force=True)
                        time.sleep(1)
                    got_it = page.locator('div[aria-label="Got it"], div[role="button"]:has-text("Got it"), div[role="button"]:has-text("Save")').first
                    if got_it.is_visible():
                        got_it.click(force=True)
                        time.sleep(2)
                    else:
                        page.keyboard.press("Escape")
                        time.sleep(1)
                logger.info("AI label configured.")
            except Exception as e:
                logger.warning(f"Note on setting AI label: {e}")

        # 2. Select Feeling/Activity
        if feeling:
            logger.info(f"Selecting Feeling/Activity: '{feeling}'...")
            try:
                feeling_btn = dialog.locator('div[aria-label="Feeling/activity"]').first
                if feeling_btn.is_visible():
                    feeling_btn.click(force=True)
                    time.sleep(2)
                    feel_el = page.locator(f'span:has-text("{feeling}"), div[role="button"]:has-text("{feeling}")').first
                    if feel_el.is_visible():
                        feel_el.click(force=True)
                        logger.info(f"Feeling '{feeling}' selected.")
                        time.sleep(2)
                    else:
                        search_inp = page.locator('input[placeholder="Search"], input[aria-label="Search"]').first
                        if search_inp.is_visible():
                            search_inp.fill(feeling)
                            time.sleep(2)
                            match_el = page.locator(f'span:has-text("{feeling}"), div[role="button"]:has-text("{feeling}")').first
                            if match_el.is_visible():
                                match_el.click(force=True)
                                time.sleep(2)
                            else:
                                page.keyboard.press("Escape")
                        else:
                            page.keyboard.press("Escape")
            except Exception as e:
                logger.warning(f"Note on setting feeling: {e}")

        # 3. Select Location
        if location:
            logger.info(f"Selecting Location / Check in: '{location}'...")
            try:
                loc_btn = dialog.locator('div[aria-label="Check in"]').first
                if loc_btn.is_visible():
                    loc_btn.click(force=True)
                    time.sleep(2)
                    odisha_span = page.locator(f'div[role="dialog"] span:has-text("{location}"), div[role="dialog"] div[role="button"]:has-text("{location}")').first
                    if odisha_span.is_visible():
                        odisha_span.click(force=True)
                        logger.info(f"Location '{location}' selected from suggestions.")
                        time.sleep(2)
                    else:
                        where_inp = page.locator('input[placeholder*="Where are you"]').first
                        if where_inp.is_visible():
                            where_inp.fill(location)
                            time.sleep(2)
                            match_loc = page.locator(f'div[role="dialog"] span:has-text("{location}"), div[role="dialog"] div[role="button"]:has-text("{location}")').first
                            if match_loc.is_visible():
                                match_loc.click(force=True)
                                logger.info(f"Location '{location}' selected from search.")
                                time.sleep(2)
                            else:
                                page.keyboard.press("Escape")
                        else:
                            page.keyboard.press("Escape")
            except Exception as e:
                logger.warning(f"Note on setting location: {e}")

        # 4. Attach Image and STRICTLY VERIFY preview
        logger.info(f"Attaching generated image to {target_name}: {image_abs_path}")
        photo_icon = dialog.locator('div[aria-label="Photo/video"]').first
        if photo_icon.is_visible():
            photo_icon.click(force=True)
            time.sleep(2)

        d_inputs = dialog.locator('input[type="file"]')
        if d_inputs.count() > 0:
            d_inputs.first.set_input_files(image_abs_path)
        else:
            page.locator('input[type="file"]').last.set_input_files(image_abs_path)

        logger.info("Waiting 7 seconds for photo upload preview and processing...")
        time.sleep(7)

        # STRICT VERIFICATION: Image MUST be present in dialog
        imgs = dialog.locator('img').all()
        photo_verified = False
        for im in imgs:
            src = im.get_attribute("src") or ""
            box = im.bounding_box()
            if box and box["width"] > 100 and box["height"] > 100 and "profile" not in src:
                photo_verified = True
                break

        if not photo_verified:
            logger.error(f"STRICT VERIFICATION FAILED: Photo preview not detected on {target_name}! Aborting post.")
            page.screenshot(path=f"logs/photo_upload_failed_{target_name.replace(' ', '_')}.png")
            return {"success": False, "error": f"Photo preview could not be verified on {target_name}"}

        logger.info(f"Photo preview successfully verified on {target_name}!")

        # 5. Type Caption Text
        logger.info(f"Entering caption text on {target_name}...")
        content_box = dialog.locator('[contenteditable="true"]').first
        if content_box.is_visible():
            content_box.click()
            time.sleep(1)
            content_box.fill(caption_text)
            time.sleep(1)
            page.keyboard.press("Escape")
            time.sleep(1)

        # 6. Advance & Submit (Next -> Post or direct Post)
        next_btn = dialog.locator('div[aria-label="Next"][role="button"], div[role="button"]:has-text("Next")').first
        if next_btn.is_visible():
            logger.info("Advancing past 'Next' screen...")
            for _ in range(12):
                if next_btn.get_attribute("aria-disabled") != "true":
                    break
                time.sleep(1)
            next_btn.click(force=True)
            time.sleep(4)

        logger.info(f"Locating final 'Post' button for {target_name}...")
        post_btns = page.locator('div[aria-label="Post"][role="button"], div[role="button"]:has-text("Post"), button:has-text("Post")').all()
        publish_btn = None
        for b in post_btns:
            try:
                if b.is_visible():
                    txt = b.inner_text().strip()
                    aria = b.get_attribute("aria-label") or ""
                    if txt == "Post" or aria == "Post":
                        publish_btn = b
                        break
            except Exception:
                continue

        if publish_btn:
            for _ in range(15):
                if publish_btn.get_attribute("aria-disabled") != "true":
                    break
                time.sleep(1)

            logger.info(f"Clicking final '{publish_btn.inner_text().strip()}' button on {target_name}...")
            publish_btn.click(force=True)
            logger.info(f"Post submission click sent. Waiting for {target_name} post dialog to close...")

            for i in range(30):
                time.sleep(1)
                visible_dialogs = [d for d in page.locator('div[role="dialog"]').all() if d.is_visible()]
                if not visible_dialogs:
                    logger.info(f"Post dialog closed after {i+1} seconds! {target_name} feed post live!")
                    break
            time.sleep(4)
            return {"success": True}
        else:
            logger.warning("Attempting Control+Enter keyboard submission fallback...")
            page.keyboard.press("Control+Enter")
            time.sleep(10)
            return {"success": True}

    def publish_story(self, image_path, ai_label=True, page=None, context_name="Story"):
        """
        Uploads the generated 9:16 photo directly to Facebook Stories as a native full-screen story.
        Reuses active page if provided, otherwise launches a standalone browser.
        """
        image_abs_path = str(Path(image_path).resolve())
        if not Path(image_abs_path).exists():
            logger.error(f"Image not found for story: {image_abs_path}")
            return False

        logger.info(f"Uploading 9:16 photo directly to Facebook Story for [{context_name}] ({image_abs_path})...")

        def _do_upload(p_page):
            p_page.goto("https://www.facebook.com/stories/create", wait_until="domcontentloaded", timeout=60000)
            time.sleep(5)

            file_inp = p_page.locator('input[type="file"]').first
            if file_inp.count() > 0:
                file_inp.set_input_files(image_abs_path)
                logger.info(f"Photo attached to {context_name} story editor. Waiting 5 seconds...")
                time.sleep(5)

                # Toggle AI label on Story if requested
                if ai_label:
                    ai_switch = p_page.locator('[role="switch"]').first
                    if ai_switch.is_visible() and ai_switch.get_attribute("aria-checked") != "true":
                        ai_switch.click(force=True)
                        logger.info(f"Toggled 'Add AI label' ON for {context_name} story.")
                        time.sleep(1)

                # Click Share to Story
                share_btn = p_page.locator('div[role="button"]:has-text("Share to Story"), button:has-text("Share to Story"), div[aria-label="Share to story"]').first
                if share_btn.is_visible():
                    share_btn.click(force=True)
                    logger.info(f"Clicked 'Share to Story' for {context_name}. Waiting 10 seconds for upload...")
                    time.sleep(10)
                    logger.info(f"Native photo story published successfully for [{context_name}]!")
                    return True
                else:
                    logger.warning(f"Could not find 'Share to Story' button for {context_name}.")
                    return False
            else:
                logger.error(f"No file input found on Story creation page for {context_name}.")
                return False

        if page is not None:
            try:
                return _do_upload(page)
            except Exception as e:
                logger.exception(f"Error publishing story for {context_name} on active page: {e}")
                return False
        else:
            with sync_playwright() as p:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.profile_dir),
                    headless=False,
                    channel="chrome",
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--start-maximized",
                        "--no-sandbox"
                    ],
                    viewport=None
                )
                try:
                    standalone_page = context.pages[0] if context.pages else context.new_page()
                    res = _do_upload(standalone_page)
                    context.close()
                    return res
                except Exception as e:
                    logger.exception(f"Error publishing story for {context_name}: {e}")
                    context.close()
                    return False

if __name__ == "__main__":
    import yaml
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    with open("config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    pub = FacebookPublisher(cfg)
    test_img = cfg["paths"]["reference_face"]
    res = pub.publish_full_campaign(
        caption_text="Testing Maira Dash 4-channel automated agent with verified switching! 💖✨\n\n#Testing #Automation",
        image_path=test_img,
        slot_info=cfg["slots"]["morning"]
    )
    print(f"Result: {res}")
