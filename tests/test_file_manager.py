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

            path = manager.save_image("https://example.com/img.png", "spells", "fireball", "test-provider")

            assert Path(path).exists()
            assert "spells/test-provider/fireball.png" in path


def test_save_image_with_conversions():
    """Test that conversions are generated when configured"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {
            "base_path": tmpdir,
            "conversions": {
                "enabled": True,
                "sizes": [512, 256],
                "path": f"{tmpdir}/conversions"
            }
        }
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

                # Mock the resized images
                mock_resized = Mock()
                mock_img.resize.return_value = mock_resized

                path = manager.save_image("https://example.com/img.png", "items", "longsword")

                # Verify resize was called for both conversion sizes
                from PIL import Image as PILImage
                assert mock_img.resize.call_count == 2

                # Verify save was called for both conversions
                assert mock_resized.save.call_count == 2


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


def test_save_image_rejects_null_slug():
    """Test that save_image raises ValueError for null/None slugs"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {"base_path": tmpdir, "post_resize": None}
        manager = FileManager(config)

        with patch('src.generator.file_manager.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.content = b"fake_image_data"
            mock_get.return_value = mock_response

            # Test None slug
            with pytest.raises(ValueError, match="invalid slug 'None'"):
                manager.save_image("https://example.com/img.png", "sizes", None)

            # Test "null" string slug
            with pytest.raises(ValueError, match="invalid slug 'null'"):
                manager.save_image("https://example.com/img.png", "sizes", "null")

            # Test empty string slug
            with pytest.raises(ValueError, match="invalid slug ''"):
                manager.save_image("https://example.com/img.png", "sizes", "")


def test_save_image_rejects_path_traversal():
    """Test that save_image prevents path traversal attacks"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {"base_path": tmpdir, "post_resize": None}
        manager = FileManager(config)

        with patch('src.generator.file_manager.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.content = b"fake_image_data"
            mock_get.return_value = mock_response

            # Test path traversal attempt
            with pytest.raises(ValueError, match="must not contain path components"):
                manager.save_image("https://example.com/img.png", "spells", "../../../etc/passwd")
