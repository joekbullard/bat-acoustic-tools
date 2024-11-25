import unittest
from wav_to_flac import create_flac_path
from unittest.mock import patch, MagicMock
from pathlib import Path


class TestCreateFlacPath(unittest.TestCase):
    @patch("pathlib.Path.mkdir")  # Mock the mkdir method to avoid creating directories
    def test_create_flac_path(self, mock_mkdir):
        # Setup test input
        wav_file = Path("/home/user/data/2023-11-01/location_123/data/file.wav")
        flac_root = Path("/home/user/flac")

        # Expected output
        expected_path = Path("/home/user/flac/2023-11-01/location_123/data/file.flac")

        # Call the function
        result = create_flac_path(wav_file, flac_root)

        # Assertions
        self.assertEqual(result, expected_path)  # Check the returned FLAC file path
        mock_mkdir.assert_called_once_with(
            parents=True, exist_ok=True
        )  # Check mkdir was called

    @patch("pathlib.Path.mkdir")
    def test_create_flac_path_directory_creation(self, mock_mkdir):
        # Setup test input
        wav_file = Path("/home/user/data/2023-11-01/location_456/data/file2.wav")
        flac_root = Path("/home/user/flac")

        # Call the function
        create_flac_path(wav_file, flac_root)

        # Check mkdir was called to create the directory structure
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_create_flac_path_invalid_path(self):
        # Test with an invalid wav_file path (not enough parts)
        wav_file = Path("invalid_path.wav")
        flac_root = Path("/home/user/flac")

        # Check that the function raises an IndexError (or other appropriate error)
        with self.assertRaises(IndexError):
            create_flac_path(wav_file, flac_root)


if __name__ == "__main__":
    unittest.main()
