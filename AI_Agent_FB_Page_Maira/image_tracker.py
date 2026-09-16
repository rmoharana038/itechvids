"""
Image Tracker Module - Maira Dash
Guarantees that no generated image is ever posted more than once.
Maintains a permanent registry with SHA-256 content hashes in 'logs/posted_images.json'.
"""

import hashlib
import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("AgentLogger")

class ImageTracker:
    def __init__(self, registry_file="logs/posted_images.json"):
        self.registry_file = Path(registry_file).resolve()
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)

    def _get_hash(self, image_path):
        hasher = hashlib.sha256()
        with open(image_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _load_registry(self):
        if self.registry_file.exists():
            try:
                with open(self.registry_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_registry(self, registry):
        try:
            with open(self.registry_file, "w", encoding="utf-8") as f:
                json.dump(registry, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save posted images registry: {e}")

    def is_already_posted(self, image_path):
        """
        Returns True if this exact image (by content hash) was ever published before.
        """
        path = Path(image_path)
        if not path.exists():
            return False

        img_hash = self._get_hash(path)
        registry = self._load_registry()
        for item in registry:
            if item.get("hash") == img_hash:
                logger.warning(f"Image {path.name} was already posted on {item.get('timestamp')} for slot [{item.get('slot')}].")
                return True
        return False

    def record_posted(self, image_path, slot, caption):
        """
        Records the image as published to permanently prevent reuse.
        """
        path = Path(image_path)
        if not path.exists():
            return

        img_hash = self._get_hash(path)
        registry = self._load_registry()
        record = {
            "timestamp": datetime.now().isoformat(),
            "filename": path.name,
            "path": str(path.resolve()),
            "hash": img_hash,
            "slot": slot,
            "caption": caption[:80] + "..." if len(caption) > 80 else caption
        }
        registry.append(record)
        self._save_registry(registry)
        logger.info(f"Recorded image {path.name} (hash: {img_hash[:12]}...) in posted registry.")

if __name__ == "__main__":
    tracker = ImageTracker()
    test_img = Path("assets/reference_face.jpg")
    if test_img.exists():
        print(f"Is {test_img} already posted? {tracker.is_already_posted(test_img)}")
