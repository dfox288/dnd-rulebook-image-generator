import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from src.generator.file_manager import FileManager


def test_save_image_creates_directory():
    """Test that save_image creates entity type directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {"base_path": tmpdir, "post_resize": None}
        manager = FileManager(config)

        # Mock image download
        with patch('src.generator.file_manager.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.content = b"fake_image_data"
            mock_get.return_value = mock_response

            path = manager.save_image("https://example.com/img.png", "spells", "fireball")

            assert Path(path).exists()
            assert "spells/fireball.png" in path


def test_save_image_with_resize():
    """Test that images are resized when configured"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {"base_path": tmpdir, "post_resize": 512}
        manager = FileManager(config)

        with patch('src.generator.file_manager.requests.get') as mock_get:
            mock_response = Mock()
            # Create a minimal valid PNG
            mock_response.content = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
            mock_get.return_value = mock_response

            with patch('src.generator.file_manager.Image.open') as mock_open:
                mock_img = Mock()
                mock_img.size = (1024, 1024)
                mock_open.return_value = mock_img

                path = manager.save_image("https://example.com/img.png", "items", "longsword")

                # Verify resize was called (with resampling parameter)
                from PIL import Image as PILImage
                mock_img.resize.assert_called_once_with((512, 512), PILImage.Resampling.LANCZOS)


def test_update_manifest():
    """Test manifest tracking of generated images"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {"base_path": tmpdir, "post_resize": None}
        manager = FileManager(config)

        manager.update_manifest("spells", "fireball", "output/spells/fireball.png", True)

        manifest_path = Path(tmpdir) / ".manifest.json"
        assert manifest_path.exists()

        with open(manifest_path) as f:
            manifest = json.load(f)

        assert "spells" in manifest
        assert "fireball" in manifest["spells"]
        assert manifest["spells"]["fireball"]["success"] is True


def test_is_already_generated():
    """Test checking if image already exists"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {"base_path": tmpdir, "post_resize": None}
        manager = FileManager(config)

        # Not generated yet
        assert manager.is_already_generated("spells", "fireball") is False

        # Mark as generated
        manager.update_manifest("spells", "fireball", "output/spells/fireball.png", True)

        # Should now show as generated
        assert manager.is_already_generated("spells", "fireball") is True


def test_get_generated_count():
    """Test counting generated images"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {"base_path": tmpdir, "post_resize": None}
        manager = FileManager(config)

        manager.update_manifest("spells", "fireball", "path1.png", True)
        manager.update_manifest("spells", "magic-missile", "path2.png", True)
        manager.update_manifest("items", "longsword", "path3.png", True)

        assert manager.get_generated_count("spells") == 2
        assert manager.get_generated_count("items") == 1
        assert manager.get_generated_count() == 3
