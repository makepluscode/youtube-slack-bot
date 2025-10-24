"""Simple unit test for YouTube download functionality"""

import subprocess
import tempfile
from pathlib import Path


def test_youtube_download():
    """Test downloading a short YouTube video"""

    # Use a short test video (YouTube's official test video, ~10 seconds)
    test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # "Me at the zoo" - first YouTube video, 19 seconds

    print("=" * 60)
    print("Testing YouTube Download")
    print("=" * 60)
    print(f"Test URL: {test_url}")
    print()

    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "test_video.mp4"

        print("Starting download with Android player client...")
        print()

        # Use Android player client to bypass 403 errors
        command = [
            "yt-dlp",
            "--extractor-args", "youtube:player_client=android",
            "--format", "18",  # Use format 18 (360p) for quick download
            "--output", str(output_path),
            test_url
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                if output_path.exists():
                    file_size = output_path.stat().st_size / (1024 * 1024)  # MB
                    print("✅ TEST PASSED")
                    print(f"   Downloaded: {output_path.name}")
                    print(f"   File size: {file_size:.2f} MB")
                    print(f"   Location: {temp_dir}")
                    return True
                else:
                    print("❌ TEST FAILED: File not found after download")
                    print(f"   stderr: {result.stderr}")
                    return False
            else:
                print("❌ TEST FAILED: Download command failed")
                print(f"   Return code: {result.returncode}")
                print(f"   stderr: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("❌ TEST FAILED: Download timeout")
            return False
        except Exception as e:
            print(f"❌ TEST FAILED: {e}")
            return False


if __name__ == "__main__":
    success = test_youtube_download()
    exit(0 if success else 1)
