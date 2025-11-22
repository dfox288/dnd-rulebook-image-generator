import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)


class FileManager:
    """Manages file storage and manifest tracking for generated images"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_path = Path(config["base_path"])
        self.post_resize = config.get("post_resize")
        self.timeout = config.get("timeout", 30)
        self.manifest_path = self.base_path / ".manifest.json"

        # Ensure base directory exists
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save_image(
        self,
        image_url: str,
        entity_type: str,
        slug: str
    ) -> str:
        """
        Download and save image to entity_type/slug.png

        Args:
            image_url: URL of image to download
            entity_type: Entity type (spells, items, etc.)
            slug: Entity slug for filename

        Returns:
            Path to saved image
        """
        # Create entity type directory
        entity_dir = self.base_path / entity_type
        entity_dir.mkdir(parents=True, exist_ok=True)

        # Download image
        response = requests.get(image_url, timeout=self.timeout)
        response.raise_for_status()

        image_data = response.content

        # Resize if configured
        if self.post_resize:
            image_data = self._resize_image(image_data, self.post_resize)

        # Sanitize slug to prevent path traversal
        sanitized_slug = Path(slug).name
        if sanitized_slug != slug:
            raise ValueError(f"Invalid slug: {slug}. Slugs must not contain path components.")

        # Save to file
        output_path = entity_dir / f"{sanitized_slug}.png"
        with open(output_path, 'wb') as f:
            f.write(image_data)

        logger.info(f"Saved image to {output_path}")

        return str(output_path)

    def _resize_image(self, image_data: bytes, target_size: int) -> bytes:
        """Resize image to target_size x target_size"""
        img = Image.open(io.BytesIO(image_data))
        img = img.resize((target_size, target_size), Image.Resampling.LANCZOS)

        output = io.BytesIO()
        img.save(output, format='PNG')
        return output.getvalue()

    def update_manifest(
        self,
        entity_type: str,
        slug: str,
        path: str,
        success: bool,
        error: Optional[str] = None
    ):
        """
        Update manifest with generation result

        Args:
            entity_type: Entity type
            slug: Entity slug
            path: Path to saved image
            success: Whether generation succeeded
            error: Error message if failed
        """
        manifest = self._load_manifest()

        if entity_type not in manifest:
            manifest[entity_type] = {}

        manifest[entity_type][slug] = {
            "path": path,
            "success": success,
            "error": error
        }

        self._save_manifest(manifest)

    def is_already_generated(self, entity_type: str, slug: str) -> bool:
        """Check if image already exists in manifest"""
        manifest = self._load_manifest()
        return (
            entity_type in manifest
            and slug in manifest[entity_type]
            and manifest[entity_type][slug]["success"]
        )

    def get_generated_count(self, entity_type: Optional[str] = None) -> int:
        """
        Get count of generated images

        Args:
            entity_type: Optional entity type filter

        Returns:
            Count of successfully generated images
        """
        manifest = self._load_manifest()

        if entity_type:
            entities = manifest.get(entity_type, {})
            return sum(1 for e in entities.values() if e["success"])
        else:
            total = 0
            for entities in manifest.values():
                total += sum(1 for e in entities.values() if e["success"])
            return total

    def _load_manifest(self) -> Dict[str, Any]:
        """Load manifest from disk"""
        if self.manifest_path.exists():
            with open(self.manifest_path) as f:
                return json.load(f)
        return {}

    def _save_manifest(self, manifest: Dict[str, Any]):
        """Save manifest to disk"""
        with open(self.manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
