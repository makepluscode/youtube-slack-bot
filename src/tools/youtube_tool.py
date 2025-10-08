"""LangChain Tool for YouTube video downloading"""

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class YouTubeDownloadInput(BaseModel):
    """Input schema for YouTube download tool"""

    url: str = Field(description="The YouTube URL to download")


class YouTubeDownloadOutput(BaseModel):
    """Output schema for YouTube download tool"""

    success: bool = Field(description="Whether the download was successful")
    message: str = Field(description="Status message or error description")
    title: Optional[str] = Field(default=None, description="Video title if successful")
    file_path: Optional[str] = Field(default=None, description="Downloaded file path if successful")


class YouTubeDownloadTool(BaseTool):
    """Tool for downloading YouTube videos using yt-dlp"""

    name: str = "youtube_downloader"
    description: str = """
    Downloads a YouTube video to the specified directory.
    Input should be a valid YouTube URL (youtube.com/watch, youtu.be, or youtube.com/shorts).
    Returns success status, video title, and file path.
    """
    args_schema: Type[BaseModel] = YouTubeDownloadInput
    download_dir: str = Field(description="Directory to save downloaded videos")

    def __init__(self, download_dir: str, **kwargs):
        """
        Initialize the YouTube download tool
        
        Args:
            download_dir: Directory path for downloads
        """
        super().__init__(download_dir=download_dir, **kwargs)
        self._check_ytdlp()

    def _check_ytdlp(self) -> None:
        """Check if yt-dlp is installed"""
        if not shutil.which("yt-dlp"):
            raise RuntimeError(
                "yt-dlp is not installed. Install it with: brew install yt-dlp"
            )

    def _get_video_info(self, url: str) -> Optional[dict]:
        """
        Get video information without downloading
        
        Args:
            url: YouTube URL
            
        Returns:
            Dictionary with video info or None if failed
        """
        try:
            result = subprocess.run(
                ["yt-dlp", "--dump-json", "--no-warnings", url],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                import json
                info = json.loads(result.stdout)
                return {
                    "title": info.get("title"),
                    "duration": info.get("duration"),
                    "uploader": info.get("uploader"),
                    "id": info.get("id"),
                }
            else:
                logger.error(f"Failed to get video info: {result.stderr}")
                return None

        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return None

    def _run(self, url: str) -> str:
        """
        Download a YouTube video (synchronous)
        
        Args:
            url: YouTube URL to download
            
        Returns:
            JSON string with download result
        """
        logger.info(f"Starting download: {url}")

        try:
            # Get video info first
            info = self._get_video_info(url)
            if not info:
                return YouTubeDownloadOutput(
                    success=False,
                    message="Failed to retrieve video information"
                ).model_dump_json()

            title = info["title"]
            logger.info(f"Video title: {title}")

            # Prepare yt-dlp command
            download_path = Path(self.download_dir)
            command = [
                "yt-dlp",
                "--format",
                "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "--merge-output-format",
                "mp4",
                "--output",
                str(download_path / "%(title)s.%(ext)s"),
                "--no-warnings",
                "--no-playlist",
                url,
            ]

            # Run download
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                timeout=600  # 10 minute timeout
            )

            if result.returncode == 0:
                # Find the downloaded file
                downloaded_files = list(download_path.glob(f"*{title[:50]}*.mp4"))
                
                if not downloaded_files:
                    # Try a more general search
                    downloaded_files = sorted(
                        download_path.glob("*.mp4"),
                        key=lambda p: p.stat().st_mtime,
                        reverse=True
                    )[:1]

                if downloaded_files:
                    file_path = str(downloaded_files[0])
                    file_size = Path(file_path).stat().st_size / (1024 * 1024)  # MB
                    logger.info(f"✅ Download successful: {file_path} ({file_size:.2f} MB)")

                    return YouTubeDownloadOutput(
                        success=True,
                        message=f"Successfully downloaded: {title}",
                        title=title,
                        file_path=file_path
                    ).model_dump_json()
                else:
                    logger.warning("Download reported success but file not found")
                    return YouTubeDownloadOutput(
                        success=False,
                        message="Downloaded file not found",
                        title=title
                    ).model_dump_json()
            else:
                error_msg = result.stderr or "Unknown error"
                logger.error(f"Download failed: {error_msg}")
                return YouTubeDownloadOutput(
                    success=False,
                    message=f"Download failed: {error_msg}",
                    title=title
                ).model_dump_json()

        except subprocess.TimeoutExpired:
            error_msg = "Download timeout (exceeded 10 minutes)"
            logger.error(error_msg)
            return YouTubeDownloadOutput(
                success=False,
                message=error_msg
            ).model_dump_json()

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return YouTubeDownloadOutput(
                success=False,
                message=error_msg
            ).model_dump_json()

    async def _arun(self, url: str) -> str:
        """Async version (not implemented, falls back to sync)"""
        return self._run(url)


def get_youtube_tools(download_dir: str) -> list[BaseTool]:
    """
    Get list of YouTube-related tools
    
    Args:
        download_dir: Directory for downloads
        
    Returns:
        List of LangChain tools
    """
    return [
        YouTubeDownloadTool(download_dir=download_dir),
    ]

