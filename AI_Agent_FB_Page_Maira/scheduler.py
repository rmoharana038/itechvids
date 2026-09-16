"""
Scheduler Module - Maira Dash
Schedules and triggers the 5 daily Facebook posts according to Indian Standard Time (IST).
"""

import os
import json
import logging
import pytz
from datetime import datetime
from pathlib import Path
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger("AgentLogger")

class PostScheduler:
    def __init__(self, config, job_callback):
        self.config = config
        self.job_callback = job_callback
        self.tz_name = config.get("timezone", "Asia/Kolkata")
        self.timezone = pytz.timezone(self.tz_name)
        self.scheduler = BlockingScheduler(timezone=self.timezone)
        self.history_path = Path(config["paths"]["history_file"]).resolve()
        self.history_path.parent.mkdir(parents=True, exist_ok=True)

    def register_jobs(self):
        slots = self.config.get("slots", {})
        print("\n" + "=" * 75)
        print(f"       REGISTERING SCHEDULED POSTING SLOTS (Timezone: {self.tz_name})")
        print("=" * 75)
        print(f"{'Slot':<15} | {'Scheduled Time':<15} | {'Label':<20} | {'Status'}")
        print("-" * 75)

        for slot_key, slot_data in slots.items():
            if not slot_data.get("enabled", True):
                print(f"{slot_key:<15} | {slot_data.get('time', 'N/A'):<15} | {slot_data.get('label', ''):<20} | Disabled")
                continue

            time_str = slot_data.get("time", "00:00")
            hour, minute = [int(x) for x in time_str.split(":")]

            trigger = CronTrigger(hour=hour, minute=minute, timezone=self.timezone)
            self.scheduler.add_job(
                func=self._on_slot_trigger,
                trigger=trigger,
                args=[slot_key],
                id=f"job_{slot_key}",
                name=slot_data.get("label", slot_key),
                replace_existing=True
            )
            print(f"{slot_key:<15} | {time_str + ' IST':<15} | {slot_data.get('label', ''):<20} | Active")

        print("=" * 75)

    def _on_slot_trigger(self, slot_key):
        now_ist = datetime.now(self.timezone).strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"Triggering scheduled job for slot [{slot_key}] at {now_ist} IST")
        result = self.job_callback(slot_key)
        self._record_history(slot_key, result)

    def _record_history(self, slot_key, result):
        history = []
        if self.history_path.exists():
            try:
                with open(self.history_path, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []

        record = {
            "timestamp": datetime.now(self.timezone).isoformat(),
            "slot": slot_key,
            "result": result
        }
        history.append(record)
        try:
            with open(self.history_path, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to record history: {e}")

    def start(self):
        self.register_jobs()
        print("\n--> Scheduler is running 24/7 in Indian Standard Time (Asia/Kolkata).")
        print("--> Press Ctrl+C in this terminal to stop at any time.\n")
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print("\nScheduler stopped by user.")
